import time
import random
import os
import google.generativeai as genai
from dotenv import load_dotenv
import glob
import argparse
import re
load_dotenv()

from src.utils.prompt_manager import PromptManager
prompt_manager = PromptManager()

# Configure the Google Generative AI SDK
# Ensure you have your GEMINI_API_KEY set as an environment variable
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

class GeminiResponse:
    """A wrapper for Gemini API response to ensure consistent attribute access."""
    def __init__(self, text):
        self.text = text

def call_llm_api(prompt: str):
    """
    Calls the Gemini LLM API to generate content.

    Args:
        prompt: The prompt to send to the LLM.

    Returns:
        A GeminiResponse object containing the generated text.

    Raises:
        Exception: If the Gemini API call fails or returns an empty response.
    """
    try:
        model = genai.GenerativeModel(GEMINI_MODEL) # You can choose other models like 'gemini-ultra' if available
        print("Calling Gemini API...")
        response = model.generate_content(prompt)
        
        if response and response.text:
            print("Gemini API call successful.")
            return GeminiResponse(response.text)
        else:
            raise Exception("Gemini API call succeeded but returned an empty response.")
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        raise # Re-raise the exception to be caught by the retry mechanism


def load_analysis_reports(company_name: str, reports_dir: str = "outputs") -> dict:
    """
    Load multiple analysis reports for a given company.
    
    Args:
        company_name: The company name to search for in report filenames
        reports_dir: Directory containing the analysis reports
        
    Returns:
        Dictionary with report types as keys and content as values
        
    Raises:
        Exception: If no reports are found or directory doesn't exist
    """
    reports = {}
    
    # Validate inputs
    if not company_name or not company_name.strip():
        raise ValueError("Company name cannot be empty")
    
    # Clean company name for filename matching (remove special characters)
    clean_company_name = re.sub(r'[^\w\-]', '', company_name.strip().lower())
    
    # Check if reports directory exists
    if not os.path.exists(reports_dir):
        raise FileNotFoundError(f"Reports directory '{reports_dir}' does not exist")
    
    # Search for files matching pattern: {company_name}-*.md
    pattern = os.path.join(reports_dir, f"{clean_company_name}-*.md")
    matching_files = glob.glob(pattern)
    
    if not matching_files:
        raise FileNotFoundError(f"No analysis reports found for company '{company_name}' in '{reports_dir}' directory")
    
    # Load content from matching files
    for file_path in matching_files:
        filename = os.path.basename(file_path)
        # Extract report type from filename (e.g., "sia-business-analysis.md" -> "business_analysis")
        report_type = filename.replace(f"{clean_company_name}-", "").replace(".md", "").replace("-", "_")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():  # Only add non-empty files
                    reports[report_type] = content
                    print(f"Loaded {report_type} report from {filename}")
                else:
                    print(f"Warning: {filename} is empty, skipping")
        except Exception as e:
            print(f"Warning: Could not read {filename}: {e}")
    
    if not reports:
        raise Exception(f"No valid report content found for company '{company_name}'")
    
    print(f"Successfully loaded {len(reports)} reports: {list(reports.keys())}")
    return reports


def generate_questions_with_retry(company_name: str, reports: dict, max_retries: int = 3):
    """
    Generates questions for multiple analysis reports using an LLM, with a retry mechanism.

    Args:
        company_name: The name of the company being analyzed
        reports: Dictionary containing analysis reports with report types as keys
        max_retries: The maximum number of times to retry the API call.

    Returns:
        The generated questions as a string, or raises an exception if all retries fail.
    """
    prompt = prompt_manager.format_prompt(
        "questionaire_agent",
        version="v4",
        **reports  # Unpack the reports dictionary
    )

    for attempt in range(max_retries):
        try:
            print(f"Attempting to generate questions (Attempt {attempt + 1}/{max_retries})...")
            
            # Replace `call_llm_api` with your actual LLM API call function
            response = call_llm_api(prompt)
            
            # The response check might need to be adapted based on your LLM client library
            if response and hasattr(response, 'text') and response.text:
                print("Successfully generated questions.")
                return response.text
            else:
                print("API call succeeded but returned an empty or invalid response.")

        except Exception as e:
            print(f"API call failed on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                # Exponential backoff with jitter
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            else:
                print("All retries have failed.")
                raise

# --- Example Usage ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate founder questionnaire from analysis reports')
    parser.add_argument('--company-name', required=True, help='Company name for report discovery')
    parser.add_argument('--reports-dir', default='outputs', help='Directory containing analysis reports')
    
    args = parser.parse_args()
    
    print("--- Running Questionnaire Agent ---")
    try:
        # Load analysis reports
        print(f"Loading analysis reports for company: {args.company_name}")
        reports = load_analysis_reports(args.company_name, args.reports_dir)
        
        # Generate questionnaire
        print("Generating founder questionnaire...")
        generated_questions = generate_questions_with_retry(args.company_name, reports)
        
        # Ensure outputs directory exists
        os.makedirs(args.reports_dir, exist_ok=True)
        
        # Save output
        output_file = f"{args.reports_dir}/{args.company_name}-founders-checklist.md"
        with open(output_file, "w", encoding='utf-8') as f:
            # Add metadata header
            f.write(f"# Founder Questionnaire for {args.company_name.title()}\n\n")
            f.write(f"**Generated on:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Reports analyzed:** {', '.join(reports.keys())}\n\n")
            f.write("---\n\n")
            f.write(generated_questions or "")
        
        print(f"\n--- Questionnaire Generation Complete ---")
        print(f"Founder questionnaire saved to: {output_file}")
        print(f"Reports analyzed: {list(reports.keys())}")
            
    except Exception as e:
        print(f"\nFailed to generate questionnaire: {e}")