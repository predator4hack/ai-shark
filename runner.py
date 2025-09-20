from scraper_module import StartupScraper
from analyzer_module import read_scraped_content, analyze_startup_comprehensive, save_markdown_table
import json

def productAndServicesAnalyser(domainName):
    # Step 1: Scrape website
    scraper = StartupScraper(domainName)
    scraped_data = scraper.scrape_from_sitemap()
    scraper.save_to_markdown(scraped_data, "startup_report.md")

    # Step 2: Analyze content
    content = read_scraped_content("startup_report.md")
    analysis_report = analyze_startup_comprehensive(domainName, content)

    # Step 3: Save outputs
    json_file = f"{domainName.lower().replace('https://','').replace('http://','').replace('/','')}_analysis_data.json"
    md_file = f"{domainName.lower().replace('https://','').replace('http://','').replace('/','')}_analysis_data.md"

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(analysis_report, f, indent=2, ensure_ascii=False)

    save_markdown_table(analysis_report, md_file)

    return analysis_report

# Example usage:
# report = productAndServicesAnalyser("https://rupeek.com/")
