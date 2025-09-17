import time
import random
import os
import google.generativeai as genai
from dotenv import load_dotenv
import uuid
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


def generate_questions_with_retry(investment_memo: str, max_retries: int = 3):
    """
    Generates questions for an investment memo using an LLM, with a retry mechanism.

    Args:
        investment_memo: The text of the investment memo.
        max_retries: The maximum number of times to retry the API call.

    Returns:
        The generated questions as a string, or raises an exception if all retries fail.
    """
    prompt = prompt_manager.format_prompt(
        "questionaire_agent",
        investment_memo=investment_memo,
        version="v3"
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
    # This is a sample investment memo. You can replace it with actual memo text.
    # sample_memo = """
    # **Company:** InnovateAI
    # **Problem:** Businesses in the creative industry struggle to generate novel ideas consistently.
    # **Solution:** We provide a SaaS platform that uses a proprietary generative AI model to brainstorm and develop creative concepts for marketing campaigns, product design, and content creation.
    # **Market:** The global market for creative tools is estimated at $30B. Our initial target is mid-sized marketing agencies in North America, a $2B segment.
    # **Team:** Two co-founders: a CEO with 10 years of experience in marketing and a CTO who is a PhD in machine learning.
    # **Traction:** 15 pilot customers and a growing waitlist of 200+ companies.
    # """
    
    with open("results/analysis_results.md", "r") as f:
        sample_memo = f.read()

    print("--- Running Questionnaire Agent ---")
    try:
        generated_questions = generate_questions_with_retry(sample_memo)
        print("\n--- Generated Questions ---")
        print(generated_questions)
        with open(f"results/generated_question-{uuid.uuid4()}.md", "w") as f:
            f.write(generated_questions)
            
    except Exception as e:
        print(f"\nFailed to generate questions after multiple retries: {e}")