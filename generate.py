import os
import json
import requests
import re
from time import sleep

# --- CONFIG ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
if GEMINI_API_KEY:
    print(f"Gemini key loaded: {GEMINI_API_KEY[:5]}...")
else:
    print("❌ GEMINI_API_KEY not found in environment variables.")

CHUNK_SIZE = 1000
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# --- UTILITIES ---
def read_scraped_content(filepath="startup_report.md"):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def clean_text(text):
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # remove images
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # remove links
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text, size=CHUNK_SIZE):
    return [text[i:i+size] for i in range(0, len(text), size)]

# --- GEMINI CALL ---
def analyze_with_gemini(company_name, chunk):
    prompt = f"""
You are a professional venture analyst. Analyze the following content about {company_name}. 

Focus on these areas: Value Proposition, Competitive Advantage, Product Maturity, Feature Set, Tech Stack, Business Model, Traction, Scalability, Market Opportunity, Legal & Risk, Cost Structure, Roadmap & Innovation.

For each, consider:
- What Good Looks Like (Green Signals)
- What Bad Looks Like (Red Signals)
- Possible Public Sources / Proxies

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
Be precise, concise, and avoid commentary.
"""

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            text = resp.text.strip()

            if not text:
                raise ValueError("Empty response from Gemini")

            # Safely get JSON content
            data = resp.json()
            content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text")
            if not content:
                raise ValueError(f"No content returned. Raw response: {text[:200]}...")

            # Strip ```json or ``` fences
            content = re.sub(r"^```json\s*|```$", "", content.strip(), flags=re.MULTILINE)

            return json.loads(content)
        except (requests.RequestException, json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"⚠️ Chunk analysis failed (attempt {attempt}/{MAX_RETRIES}): {e}")
            print(f"   Raw response snippet: {resp.text[:300]}")
            if attempt < MAX_RETRIES:
                sleep(RETRY_DELAY)
            else:
                return {"error": str(e), "raw_chunk": chunk[:200] + "..."}

# --- MERGE RESULTS ---
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
            if category in merged:
                for key, value in values.items():
                    if isinstance(merged[category][key], set):
                        if isinstance(value, str) and value not in ["unknown", ""]:
                            merged[category][key].add(value)
                    elif isinstance(merged[category][key], list):
                        if isinstance(value, list):
                            merged[category][key].extend(value)
                        elif isinstance(value, str) and value not in ["unknown", ""]:
                            merged[category][key].append(value)

    # Final clean-up
    for cat, vals in merged.items():
        for k, v in vals.items():
            if isinstance(v, set):
                merged[cat][k] = ", ".join(filter(None, v)) or "unknown"
            elif isinstance(v, list):
                merged[cat][k] = list(set(filter(None, v)))
    return merged

# --- SAVE MD TABLE ---
def save_markdown_table(data, filepath):
    def list_to_md(lst):
        if isinstance(lst, list):
            return "<br>".join(lst)
        return str(lst)

    md = f"# Startup Analysis\n\n"
    for section, values in data.items():
        md += f"## {section.replace('_', ' ').title()}\n\n"
        md += "| Key | Value |\n| --- | --- |\n"
        for k, v in values.items():
            md += f"| {k} | {list_to_md(v)} |\n"
        md += "\n"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"✅ Markdown table saved: {filepath}")

# --- MAIN WORKFLOW ---
def analyze_startup_comprehensive(company_name, content):
    cleaned = clean_text(content)
    chunks = chunk_text(cleaned)
    results = []
    print(f"🔍 Analyzing {company_name} across {len(chunks)} content chunks...")

    for idx, chunk in enumerate(chunks, start=1):
        print(f"  Processing chunk {idx}/{len(chunks)}...")
        res = analyze_with_gemini(company_name, chunk)
        results.append(res)
        sleep(1)
    return merge_chunk_results(results)

# --- RUN ---
if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("❌ Please set GEMINI_API_KEY environment variable")
        exit(1)

    company_name = input("Enter company name: ").strip() or "Rupeek"
    content = read_scraped_content("startup_report.md")

    print(f"📊 Starting comprehensive evaluation of {company_name}...")
    report = analyze_startup_comprehensive(company_name, content)

    # Save JSON output
    output_json = f"{company_name.lower()}_analysis_data.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON analysis saved: {output_json}")

    # Save Markdown table output
    output_md = f"{company_name.lower()}_analysis_data.md"
    save_markdown_table(report, output_md)
