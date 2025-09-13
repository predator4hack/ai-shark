import os
import io
import json
from pathlib import Path
import fitz  # PyMuPDF
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import time
import functools

# Load environment variables from .env file
load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL")

def configure_gemini():
    """Configures the Gemini API with the key from environment variables."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Please set it in a .env file.")
    genai.configure(api_key=api_key)

def retry_with_backoff(retries=5, backoff_in_seconds=5):
    """
    Decorator for retrying a function with exponential backoff.
    """
    def rwb(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        raise e
                    else:
                        sleep = backoff_in_seconds * 2 ** x
                        print(f"Error in {f.__name__}: {e}. Retrying in {sleep} seconds.")
                        time.sleep(sleep)
                        x += 1
        return wrapper
    return rwb

def pdf_to_images(pdf_path: str):
    """Converts each page of a PDF into a list of PIL Images."""
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=150)
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        images.append(image)
    doc.close()
    return images

@retry_with_backoff()
def generate_table_of_contents(page_images: list):
    """Stage 1: Use Gemini to generate a table of contents for the document."""
    print("\nStage 1: Generating Table of Contents...")
    model = genai.GenerativeModel(GEMINI_MODEL)

    prompt = """
    You are a document analysis expert. Your task is to create a table of contents for this pitch deck.
    Analyze all the pages provided and identify the main sections.
    Return a JSON object where keys are the main topics (e.g., "Problem", "Solution", "Team", "Market_Size", "Financials", "Competition", "Traction", "Ask") and values are a list of page numbers where that topic is discussed.
    Page numbers should be 1-based.
    Example response: {"Problem": [2], "Solution": [3, 4], "Team": [5]}
    """

    # Prepare the content list [prompt, image1, image2, ...]
    content = [prompt] + page_images
    
    try:
        response = model.generate_content(content)
        # Clean up the response to extract only the JSON part
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
        toc = json.loads(cleaned_response)
        print("Successfully generated Table of Contents:")
        print(json.dumps(toc, indent=2))
        with open('results/TOC.json', 'w') as f:
            json.dump(toc, f, indent=2)
        return toc
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error generating or parsing Table of Contents: {e}")
        print(f"Model response was: {response.text if 'response' in locals() else 'No response'}")
        return None

@retry_with_backoff()
def extract_topic_data(topic: str, page_images: list):
    """Stage 2: Extract detailed information for a specific topic from its relevant pages."""
    model = genai.GenerativeModel(GEMINI_MODEL)

    prompt = f"""
    You are a startup analyst. Analyze the following pages which are known to be about the topic: '{topic}'.
    Synthesize all information from these pages to provide a complete and detailed summary for this section.
    Present the information in a clear, well-structured format. If it's a list (like team members or competitors), use bullet points.
    Be very specific when generating the response, dont include texts like 'Here is the breakdown' or 'being an AI agent'. Always refer
    to the {topic} and provide the accureate responses. 
    """

    content = [prompt] + page_images
    response = model.generate_content(content)
    return response.text

@retry_with_backoff()
def generate_embeddings(text: str, task_type: str = "RETRIEVAL_DOCUMENT"):
    """Generates embeddings for the given text."""
    model = GEMINI_EMBEDDING_MODEL
    embedding = genai.embed_content(model=model, content=text, task_type=task_type)
    return embedding['embedding']

def json_to_markdown(data: dict) -> str:
    """Converts a dictionary to a Markdown string."""
    markdown_string = ""
    for key, value in data.items():
        markdown_string += f"## {key.replace('_', ' ').title()}\n\n"
        markdown_string += f"{value}\n\n"
    return markdown_string

def process_pitch_deck(pdf_path: str):
    """Main function to orchestrate the new two-stage pitch deck processing pipeline."""
    print(f"Processing pitch deck: {pdf_path}")

    # Create results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)

    # 1. Convert PDF to a list of images
    all_page_images = pdf_to_images(pdf_path)
    print(f"Successfully converted PDF to {len(all_page_images)} images.")

    # 2. Stage 1: Generate Table of Contents
    toc = generate_table_of_contents(all_page_images)
    if not toc:
        print("Could not generate a table of contents. Aborting pipeline.")
        return

    # 3. Stage 2: Targeted, topic-by-topic extraction
    print("\nStage 2: Performing targeted extraction based on Table of Contents...")
    final_structured_data = {}
    for topic, page_nums in toc.items():
        print(f"  - Extracting topic: '{topic}' from pages {page_nums}...")
        # Get the specific images for this topic (adjusting for 0-based index)
        topic_images = [all_page_images[p - 1] for p in page_nums if 0 < p <= len(all_page_images)]
        if not topic_images:
            print(f"    - Warning: Page numbers {page_nums} for topic '{topic}' are out of range.")
            continue
        
        try:
            extracted_data = extract_topic_data(topic, topic_images)
            final_structured_data[topic] = extracted_data
            print(f"    - Successfully extracted data for '{topic}'.")
        except Exception as e:
            print(f"    - Could not process topic '{topic}'. Error: {e}")

    if not final_structured_data:
        print("No data was extracted from the document. Exiting.")
        return

    # 4. Consolidate and prepare for embedding
    print("\nConsolidating all extracted data into a single document...")
    consolidated_document = json.dumps(final_structured_data, indent=2)
    print(consolidated_document)

    with open('results/Consolidated_result.json', 'w') as f:
        json.dump(final_structured_data, f, indent=2)

    # 5. Convert to Markdown and save
    print("\nConverting to Markdown and saving...")
    markdown_content = json_to_markdown(final_structured_data)
    with open('results/analysis_results.md', 'w') as f:
        f.write(markdown_content)
    print("Successfully saved Markdown analysis to results/analysis_results.md")

    # 6. Generate embeddings for the final consolidated document
    # print("\nGenerating embeddings for the consolidated document...")
    # try:
    #     embeddings = generate_embeddings(consolidated_document)
    #     print(f"Successfully generated embeddings. Vector dimension: {len(embeddings)}")

    #     # 7. Downstream: Store in a Vector Database (Placeholder)
    #     # This consolidated_document and its embeddings vector are now ready for storage.
    #     print("\nPipeline complete. Data is ready to be stored in a vector database.")

    # except Exception as e:
    #     print(f"Could not generate embeddings. Error: {e}")

if __name__ == '__main__':
    try:
        configure_gemini()
        # pitch_deck_pdf_path = '/Users/ritikrajak/Desktop/Hackathon/pitch_decks_data/airbnb-pitch-deck.pdf'
        pitch_deck_pdf_path = "./assets/Company Data/14. Ziniosa/Ziniosa Pitch Deck.pdf"

        if not Path(pitch_deck_pdf_path).exists():
            print(f"Error: The file was not found at: {pitch_deck_pdf_path}")
        else:
            process_pitch_deck(pitch_deck_pdf_path)

    except ValueError as e:
        print(f"Configuration Error: {e}")