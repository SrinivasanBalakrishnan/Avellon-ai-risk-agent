# agent/fetch_alerts.py

import feedparser
import os
from datetime import datetime

# Configuration
FEED_FILE = "config/feeds.txt"
OUTPUT_DIR = "outputs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "daily_topics.md")

def fetch_alerts():
    alerts = []
    
    # 1. Check if feed file exists
    if not os.path.exists(FEED_FILE):
        print(f"Warning: {FEED_FILE} not found. Using default feeds.")
        # fallback feeds if file is missing
        feeds = ["http://feeds.bbci.co.uk/news/world/rss.xml"] 
    else:
        with open(FEED_FILE, "r") as f:
            feeds = [line.strip() for line in f.readlines() if line.strip()]

    print(f"Scanning {len(feeds)} feeds...")

    # 2. Parse feeds
    for url in feeds:
        try:
            print(f"Fetching: {url}")
            feed = feedparser.parse(url)
            # Get top 5 entries from each feed to avoid clutter
            for entry in feed.entries[:5]:
                alerts.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.summary if "summary" in entry else "No summary available."
                })
        except Exception as e:
            print(f"Failed to parse {url}: {e}")

    return alerts

def run_agent():
    print("Agent started...")
    raw_alerts = fetch_alerts()
    print(f"Total alerts found: {len(raw_alerts)}")

    # 3. Format the Output (The non-AI way)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    markdown_content = f"# Daily Global Risk Topics – Avellon Intelligence ({today})\n\n"
    
    if not raw_alerts:
        markdown_content += "No significant risk updates found today.\n"
    else:
        for alert in raw_alerts:
            markdown_content += f"### [{alert['title']}]({alert['link']})\n"
            markdown_content += f"{alert['summary'][:200]}...\n\n" # Limit summary length
            markdown_content += "---\n\n"

    # 4. Save the file (Auto-create folder if missing)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Success! Output saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_agent()
