# agent/fetch_alerts.py

import feedparser
from agent.risk_prioritizer import classify_risk
from agent.topic_generator import generate_topics
from datetime import datetime

FEED_FILE = "config/feeds.txt"
OUTPUT_FILE = "outputs/daily_topics.md"

def fetch_alerts():
    alerts = []
    with open(FEED_FILE, "r") as f:
        feeds = f.readlines()

    for url in feeds:
        feed = feedparser.parse(url.strip())
        for entry in feed.entries:
            alerts.append({
                "title": entry.title,
                "summary": entry.summary if "summary" in entry else "",
            })
    return alerts

def run_agent():
    raw_alerts = fetch_alerts()

    prioritized_alerts = []
    for alert in raw_alerts:
        priority = classify_risk(alert)
        alert["priority"] = priority
        prioritized_alerts.append(alert)

    topics = generate_topics(prioritized_alerts)

    today = datetime.utcnow().strftime("%Y-%m-%d")

    with open(OUTPUT_FILE, "w") as f:
        f.write(f"# Daily Global Risk Topics – Avellon Intelligence ({today})\n\n")
        f.write(topics)

    print("Daily topics generated successfully.")

if __name__ == "__main__":
    run_agent()

