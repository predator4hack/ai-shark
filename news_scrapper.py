import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

# Configure the Gemini API key from environment variables
try:
    api_key = os.environ["GEMINI_API_KEY"]
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment.")
    genai.configure(api_key=api_key)
except (KeyError, ValueError) as e:
    print(f"Error: {e}")
    print("Please make sure you have a .env file with your GEMINI_API_KEY or set it as an environment variable.")
    exit(1)


class Inc42ScraperAgent:
    """
    An agent that scrapes a company's page on Inc42.com and uses
    the Gemini API to extract and format the information.
    """
    def __init__(self):
        """
        Initializes the agent and the Gemini model.
        """
        self.model = genai.GenerativeModel(GEMINI_MODEL)

    def scrape_and_summarize(self, url: str) -> str:
        """
        Scrapes a given URL, extracts relevant information using the Gemini API,
        and returns it in a formatted Markdown string.

        Args:
            url: The URL of the company page on Inc42.com.

        Returns:
            A Markdown formatted string with the extracted information,
            or an error message if the process fails.
        """
        print(f"Scraping and summarizing URL: {url}")
        try:
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            return f"Error: Could not fetch the URL: {e}"

        soup = BeautifulSoup(resp.text, "html.parser")
        # Extract text from the body to focus the AI on the main content
        page_text = soup.body.get_text(" ", strip=True)

        # Reduce the text size to fit within model context limits if necessary
        if len(page_text) > 15000:
            page_text = page_text[:15000]

        prompt = f"""
        Based on the following text from an Inc42 page, please extract key information about the company.
        Present the output in Markdown format.

        Include the following sections if the information is available:
        - ## About the Company
        - ## Funding and Financials
        - ## Founders and Key People
        - ## Industry and Sector
        - ## Key Developments or News

        If specific information (like funding) is not found, simply state "Information not available".

        Here is the text:
        ---
        {page_text}
        ---
        """

        print("Extracting information with the Gemini API...")
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: Failed to generate content using the Gemini API: {e}"

    def run(self, company_name: str):
        """
        Main method to run the agent.

        Note: This agent no longer includes a search function due to unreliability.
        Instead, we construct a plausible URL. For best results, you may need to
        implement a more robust search mechanism or provide a direct URL.
        """
        # Construct a plausible URL. This is an educated guess and might not work for all companies.
        url = f"https://inc42.com/datalabs/startup-directory/{company_name.lower().replace(' ', '-')}/"
        print(f"Constructed URL: {url}")
        return self.scrape_and_summarize(url)


# Example Run
if __name__ == "__main__":
    # The original script used "Zepto", but finding a reliable URL proved difficult.
    # We are using "Paytm" as an example of a company with a page on Inc42's startup directory.
    # You can replace "paytm" with another company name.
    company_to_search = "ziniosa"
    agent = Inc42ScraperAgent()
    markdown_output = agent.run(company_to_search)
    print("\n--- Generated Report ---")
    print(markdown_output)