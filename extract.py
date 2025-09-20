import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
import re
import xml.etree.ElementTree as ET


class StartupScraper:
    def __init__(self, base_url):
        if not base_url.startswith("http"):
            base_url = "https://" + base_url
        self.base_url = base_url.rstrip("/")
        self.domain = urlparse(self.base_url).netloc
        self.session = requests.Session()

    def can_scrape(self, path="/"):
        """Check robots.txt for scraping permission"""
        robots_url = urljoin(self.base_url, "/robots.txt")
        rp = RobotFileParser()
        try:
            rp.set_url(robots_url)
            rp.read()
            return rp.can_fetch("*", urljoin(self.base_url, path))
        except Exception:
            return True  # If robots.txt not found, assume allowed

    def get_metadata(self):
        """Extract meta tags like title, description, keywords"""
        if not self.can_scrape("/"):
            print("Scraping disallowed by robots.txt")
            return {}

        resp = self.session.get(self.base_url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        metadata = {
            "title": soup.title.string.strip() if soup.title else None,
            "description": None,
            "keywords": None
        }

        for meta in soup.find_all("meta"):
            if meta.get("name") == "description":
                metadata["description"] = meta.get("content")
            if meta.get("name") == "keywords":
                metadata["keywords"] = meta.get("content")

        return metadata

    def parse_sitemap(self, sitemap_url=None):
        """Parse sitemap.xml (or sitemap index) and return URLs"""
        candidate_paths = [
            "/sitemap.xml",
            "/sitemap_index.xml",
            "/sitemap/sitemap.xml",
            "/sitemap/sitemap-index.xml"
        ]

        urls = []

        # Auto-discovery of sitemap
        if sitemap_url is None:
            for path in candidate_paths:
                test_url = urljoin(self.base_url, path)
                try:
                    resp = self.session.get(test_url, timeout=10)
                    if resp.status_code == 200 and "<urlset" in resp.text or "<sitemapindex" in resp.text:
                        sitemap_url = test_url
                        break
                except Exception:
                    continue

        if not sitemap_url:
            return []

        try:
            resp = self.session.get(sitemap_url, timeout=10)
            if resp.status_code != 200:
                return []

            root = ET.fromstring(resp.text)
            namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

            # Case 1: Sitemap Index
            for sitemap in root.findall("sm:sitemap", namespace):
                loc = sitemap.find("sm:loc", namespace)
                if loc is not None:
                    urls.extend(self.parse_sitemap(loc.text))

            # Case 2: URL set
            for url in root.findall("sm:url", namespace):
                loc = url.find("sm:loc", namespace)
                if loc is not None:
                    urls.append(loc.text)

        except Exception as e:
            print(f"⚠️ Error parsing sitemap: {e}")

        return list(set(urls))

    def scrape_page_text(self, url):
        """Scrape clean text content from a page"""
        if not self.can_scrape(urlparse(url).path):
            return "Disallowed by robots.txt"

        try:
            resp = self.session.get(url, timeout=10)
        except Exception:
            return "Failed to fetch page"

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove noise
        for tag in soup(["script", "style", "noscript", "header", "footer", "svg"]):
            tag.extract()

        text = re.sub(r"\s+", " ", soup.get_text(separator=" ").strip())
        return text

    def scrape_from_sitemap(self):
        """Main pipeline using sitemap if available"""
        results = {
            "metadata": self.get_metadata(),
            "pages": {}
        }

        urls = self.parse_sitemap()
        if not urls:  # fallback
            print("⚠️ No sitemap found, fallback to homepage")
            urls = [self.base_url]

        for url in urls[:50]:  # limit to first 50 pages to avoid overload
            print(f"Scraping: {url}")
            results["pages"][url] = self.scrape_page_text(url)

        return results

    def save_to_markdown(self, data, filename="startup_report.md"):
        """Save scraped data into Markdown file"""
        md_lines = []
        md_lines.append(f"# Startup Report for {self.base_url}\n")

        # Metadata
        md_lines.append("## Metadata\n")
        for key, value in data["metadata"].items():
            md_lines.append(f"- **{key.capitalize()}**: {value}\n")

        # Pages
        md_lines.append("\n## Pages Scraped\n")
        for url, content in data["pages"].items():
            md_lines.append(f"### {url}\n")
            if content:
                md_lines.append(content[:2000] + "...\n")
            else:
                md_lines.append("No content found.\n")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        print(f"✅ Report saved as {filename}")


if __name__ == "__main__":
    scraper = StartupScraper("https://rupeek.com/")
    data = scraper.scrape_from_sitemap()
    scraper.save_to_markdown(data)
