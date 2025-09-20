# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()


def generate():
    client = genai.Client(
        api_key=os.environ.get("GOOGLE_API_KEY"),
    )

    model = "gemini-2.5-pro"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""You are a company analyst, gather and present all available information from the web about the products and services offered by the company: 'SIA Analytics', Website URL: 'https://www.sianalytics.in/'."""),
            ],
        ),
    ]
    tools = [
        types.Tool(url_context=types.UrlContext()),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=-1,
        ),
        tools=tools,
    )

    # Dump the content in a .md file named as public_data.md in results directory of the project
    with open("results/public_data.md", "w") as f:
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.text is not None:
                f.write(chunk.text)
        

if __name__ == "__main__":
    generate()