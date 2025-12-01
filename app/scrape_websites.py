# Tavily Web Scraper for Writing Tips from Blogs and Forums
import json
import time
import os
from tavily import TavilyClient
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

DATA_PATH = "data/guides.json"
SITES = [
    "writersdigest.com",
    "writingforward.com",
    "nybookeditors.com",
    "thewritepractice.com",
    "scribophile.com",
    "writershelpingwriters.net"
]
SEARCH_QUERIES = ["writing tips", "how to write", "writing advice", "story structure", "character development"]
MAX_RESULTS = 100  # per site/query
RATE_LIMIT_SLEEP = 2  # seconds between requests

def scrape_web_writing_tips():
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY not set in environment.")
    client = TavilyClient(api_key=api_key)
    all_tips = []
    for site in SITES:
        for query in SEARCH_QUERIES:
            print(f"Scraping {site} for '{query}'...")
            try:
                results = client.search(
                    query=f"{query} site:{site}",
                    max_results=MAX_RESULTS,
                    timeout=30
                )
                # Save raw results for inspection
                raw_path = f"data/raw_scraped_dataraw_web_{site.replace('.', '_')}_{query.replace(' ', '_')}.json"
                with open(raw_path, "w") as rawf:
                    json.dump(results, rawf, indent=2)
                # Filter and sanitize results
                for post in results:
                    if isinstance(post, dict):
                        title = post.get("title", "Untitled")
                        content = post.get("snippet", "")
                        if content and content.lower() not in ["query", "answer", "results", "images", "response_time", "request_id", "follow_up_questions"]:
                            tip = {"title": title, "content": content}
                            all_tips.append(tip)
                    elif isinstance(post, str):
                        if post and post.lower() not in ["query", "answer", "results", "images", "response_time", "request_id", "follow_up_questions"]:
                            tip = {"title": "Untitled", "content": post}
                            all_tips.append(tip)
                time.sleep(RATE_LIMIT_SLEEP)
            except Exception as e:
                print(f"Error scraping {site} for '{query}': {e}")
                time.sleep(RATE_LIMIT_SLEEP * 2)
    print(f"Total tips scraped: {len(all_tips)}")
    # Load existing tips
    try:
        with open(DATA_PATH, "r") as f:
            existing = json.load(f)
    except Exception:
        existing = []
    # Merge and deduplicate
    titles = set(tip["title"] for tip in existing)
    new_tips = [tip for tip in all_tips if tip["title"] not in titles]
    merged = existing + new_tips
    with open(DATA_PATH, "w") as f:
        json.dump(merged, f, indent=2)
    print(f"Saved {len(merged)} total tips to {DATA_PATH}")

if __name__ == "__main__":
    scrape_web_writing_tips()
