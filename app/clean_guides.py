import os
import json
import re
from glob import glob

data_dir = "data"
guides_path = os.path.join(data_dir, "guides.json")
raw_dir = os.path.join(data_dir, "raw_scraped_data")
raw_files = glob(os.path.join(raw_dir, "*.json"))

# Generic field names to ignore
GENERIC = {"query", "answer", "results", "images", "response_time", "request_id", "follow_up_questions", "untitled"}

def clean_text(text):
    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)
    # Remove non-ASCII
    text = text.encode("ascii", errors="ignore").decode()
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


# Phrases that indicate generic intros or non-actionable content
GENERIC_PHRASES = [
    "here are", "in this article", "offers tips", "shares advice", "read more", "for more information",
    "visit our website", "this post covers", "in this guide", "author of", "award-winning", "novel",
    "learn more", "click to read", "see full list", "this is the place to learn"
]
# Actionable verbs (not strict, just a hint)
ACTION_VERBS = [
    "write", "edit", "avoid", "use", "try", "practice", "read", "show", "develop", "cut", "improve", "keep", "make", "start", "stop", "find", "focus", "commit", "draft", "revise", "remove", "replace", "combine", "vary", "mix", "describe", "choose", "ask", "tell"
]

def is_valid_tip(tip):
    title = tip.get("title", "").strip().lower()
    content = tip.get("content", "").strip().lower()
    if not content or content in GENERIC or len(content) < 15:
        return False
    if title in GENERIC and len(content) < 30:
        return False
    # Filter out generic intros
    for phrase in GENERIC_PHRASES:
        if phrase in content:
            return False
    # Prefer tips with actionable verbs (not too strict)
    if not any(verb in content for verb in ACTION_VERBS):
        if len(content) < 40:
            return False
    return True

def load_existing_guides():
    try:
        with open(guides_path, "r") as f:
            return json.load(f)
    except Exception:
        return []

def main():
    all_tips = []
    for raw_file in raw_files:
        with open(raw_file, "r") as f:
            data = json.load(f)
            # If the file has a 'results' array, use it
            entries = data.get("results") if isinstance(data, dict) and "results" in data else data
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if isinstance(entry, dict):
                    title = clean_text(entry.get("title", "Untitled"))
                    # Prefer 'content', fallback to 'snippet' if present
                    content = clean_text(entry.get("content", entry.get("snippet", "")))
                else:
                    title = "Untitled"
                    content = clean_text(str(entry))
                tip = {"title": title, "content": content}
                if is_valid_tip(tip):
                    all_tips.append(tip)
    # Deduplicate by content
    seen = set()
    unique_tips = []
    for tip in all_tips:
        if tip["content"] not in seen:
            unique_tips.append(tip)
            seen.add(tip["content"])
    # Merge with existing guides
    existing = load_existing_guides()
    existing_contents = set(t["content"] for t in existing)
    merged = existing + [tip for tip in unique_tips if tip["content"] not in existing_contents]
    with open(guides_path, "w") as f:
        json.dump(merged, f, indent=2)
    print(f"Saved {len(merged)} total tips to {guides_path}")

if __name__ == "__main__":
    main()
