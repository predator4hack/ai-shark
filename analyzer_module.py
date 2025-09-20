import os
import json
import requests
import re
from time import sleep
from dotenv import load_dotenv


REPORT_FOLDER = "startup_analysed_report"
os.makedirs(REPORT_FOLDER, exist_ok=True)
# Load GEMINI API key from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
MIN_CHUNK_SIZE = 500  # minimum characters per chunk

# -----------------------------
# UTILITIES
# -----------------------------
def read_scraped_content(filepath="startup_report.md"):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def clean_text(text):
    """Remove images, links, extra spaces"""
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def calculate_dynamic_chunk_size(text, max_chunks=20):
    """Determine chunk size dynamically based on total text length"""
    total_length = len(text)
    chunk_size = max(total_length // max_chunks, MIN_CHUNK_SIZE)
    return chunk_size

def chunk_text(text, size):
    return [text[i:i+size] for i in range(0, len(text), size)]

# -----------------------------
# GEMINI ANALYSIS
# -----------------------------
def analyze_with_gemini(company_name, chunk):
    prompt = f"""
You are a professional venture analyst. Analyze the following content about {company_name}. 

Focus on these areas: Value Proposition, Competitive Advantage, Product Maturity, Feature Set, Tech Stack, Business Model, Traction, Scalability, Market Opportunity, Legal & Risk, Cost Structure, Roadmap & Innovation.

Content:
{chunk}

Return ONLY valid JSON in this format:
{{
  "value_proposition": {{
    "unique_value_proposition": "string",
    "problem_solved": "string",
    "target_customers": "string"
  }},
  "competitive_advantage": {{
    "moat_type": "string",
    "differentiators": [],
    "defensibility": "high|medium|low|unknown"
  }},
  "product_maturity": {{
    "stage": "idea|MVP|beta|launched|scaling|enterprise-ready",
    "features": [],
    "user_feedback_signals": []
  }},
  "overall_assessment": {{
    "strengths": [],
    "weaknesses": [],
    "investment_thesis": "string",
    "risk_level": "low|medium|high|very-high"
  }}
}}
Be precise and concise.
"""

    headers = {"Content-Type": "application/json", "X-goog-api-key": GEMINI_API_KEY}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text")
            if not content:
                raise ValueError("No content returned")
            # Clean ```json fences
            content = re.sub(r"^```json\s*|```$", "", content.strip(), flags=re.MULTILINE)
            return json.loads(content)
        except Exception as e:
            print(f"⚠️ Chunk analysis failed (attempt {attempt}/{MAX_RETRIES}): {e}")
            print(f"   Raw response snippet: {getattr(resp, 'text', '')[:300]}")
            sleep(RETRY_DELAY)
    return {"error": "Failed after retries", "raw_chunk": chunk[:200] + "..."}

# -----------------------------
# MERGE RESULTS
# -----------------------------
def merge_chunk_results(results):
    merged = {
        "value_proposition": {"unique_value_proposition": [], "problem_solved": [], "target_customers": []},
        "competitive_advantage": {"moat_type": set(), "differentiators": [], "defensibility": []},
        "product_maturity": {"stage": set(), "features": [], "user_feedback_signals": []},
        "overall_assessment": {"strengths": [], "weaknesses": [], "investment_thesis": [], "risk_level": set()}
    }

    for res in results:
        if "error" in res:
            continue
        for category, values in res.items():
            for key, value in values.items():
                if isinstance(merged[category][key], set):
                    if isinstance(value, str) and value not in ["unknown", ""]:
                        merged[category][key].add(value)
                elif isinstance(merged[category][key], list):
                    if isinstance(value, list):
                        merged[category][key].extend(value)
                    elif isinstance(value, str) and value not in ["unknown", ""]:
                        merged[category][key].append(value)

    # Final cleanup
    for cat, vals in merged.items():
        for k, v in vals.items():
            if isinstance(v, set):
                merged[cat][k] = ", ".join(filter(None, v)) or "unknown"
            elif isinstance(v, list):
                merged[cat][k] = list(set(filter(None, v)))

    return merged

# -----------------------------
# SAVE MARKDOWN TABLE
# -----------------------------
def save_markdown_table(data, filename):
    """
    Save the analysis report as a Markdown table in startup_analysed_report folder.
    """
    def list_to_md(lst):
        return "<br>".join(lst) if isinstance(lst, list) else str(lst)

    md = "# Startup Analysis\n\n"
    for section, values in data.items():
        md += f"## {section.replace('_',' ').title()}\n\n| Key | Value |\n| --- | --- |\n"
        for k, v in values.items():
            md += f"| {k} | {list_to_md(v)} |\n"
        md += "\n"

    filepath = os.path.join(REPORT_FOLDER, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"✅ Markdown table saved: {filepath}")
# -----------------------------
# MAIN ANALYSIS FUNCTION
# -----------------------------
def analyze_startup_comprehensive(company_name, content, max_chunks=20):
    cleaned = clean_text(content)
    chunk_size = calculate_dynamic_chunk_size(cleaned, max_chunks)
    chunks = chunk_text(cleaned, size=chunk_size)

    results = []
    print(f"🔍 Analyzing {company_name} across {len(chunks)} chunks (chunk size: {chunk_size})...")
    for idx, chunk in enumerate(chunks, start=1):
        print(f"  Processing chunk {idx}/{len(chunks)}...")
        res = analyze_with_gemini(company_name, chunk)
        results.append(res)
        sleep(1)

    return merge_chunk_results(results)
