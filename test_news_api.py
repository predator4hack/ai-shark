import requests
import os 
from dotenv import load_dotenv
load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def fetch_news(company, page_size=20):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": company,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": NEWSAPI_KEY
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json().get("articles", [])


ans = fetch_news("ZINIOSA")
ans = fetch_news("Timbuckdo")
import json
print(json.dumps(ans, indent=2))

