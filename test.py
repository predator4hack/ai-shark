import google.generativeai as genai
import os
from PIL import Image
import sys

# load the env variables
from dotenv import load_dotenv
load_dotenv()

def setup_gemini():
    """
    Set up the Gemini API client.
    Make sure to set your GOOGLE_API_KEY environment variable.
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("Please set the GOOGLE_API_KEY environment variable")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

def analyze_image(image_path, custom_prompt=None):
    """
    Analyze an image using Gemini 2.5 Flash model.
    
    Args:
        image_path (str): Path to the image file
        custom_prompt (str, optional): Custom prompt for analysis
    
    Returns:
        str: Analysis results from Gemini
    """
    try:
        # Set up the model
        model = setup_gemini()
        
        # Open and prepare the image
        image = Image.open(image_path)
        
        # Default prompt if none provided
        if not custom_prompt:
            prompt = """
            Analyze this pitch deck slide and provide structured information in the following format:

HEADING: [Extract the main title, heading, or key topic of this slide]

IMAGE_DESCRIPTIONS: [Describe any images, logos, charts, graphs, or visual elements you see. If there are multiple visual elements, list each one separately]

CHART_TABLE_DATA: [If there are any charts, graphs, tables, or data visualizations, extract and explain the key data points, trends, or insights in plain text format]

INTERPRETATION: [Explain what this slide is trying to convey, its purpose in the pitch deck, and why it's important for understanding the business or investment opportunity]

Please be thorough and specific in your analysis. If any section doesn't apply to this slide, write "None" for that section.
            """
        else:
            prompt = custom_prompt
        
        # Generate content
        response = model.generate_content([prompt, image])
        
        return response.text
        
    except FileNotFoundError:
        return f"Error: Image file '{image_path}' not found."
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def main():
    """
    Main function to run the image analyzer.
    """
    # Check if image path is provided
    if len(sys.argv) < 2:
        print("Usage: python gemini_analyzer.py <image_path> [custom_prompt]")
        print("Example: python gemini_analyzer.py photo.jpg")
        print("Example with custom prompt: python gemini_analyzer.py photo.jpg 'What animals do you see?'")
        return
    
    image_path = sys.argv[1]
    custom_prompt = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Analyzing image: {image_path}")
    print("=" * 50)
    
    # Analyze the image
    result = analyze_image(image_path, custom_prompt)
    
    print(result)

if __name__ == "__main__":
    main()