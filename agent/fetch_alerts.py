# agent/fetch_alerts.py

import feedparser
import os
import json
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from datetime import datetime

# --- SETUP INTELLIGENCE BRAIN ---
# Download the lexicon (dictionary) for sentiment analysis if not present
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

sia = SentimentIntensityAnalyzer()

# --- CONFIGURATION ---
FEED_FILE = "config/feeds.txt"
OUTPUT_DIR = "outputs"

# Output Files
BRIEF_FILE = os.path.join(OUTPUT_DIR, "EXECUTIVE_BRIEF.md")
CONTENT_FILE = os.path.join(OUTPUT_DIR, "CONTENT_STUDIO.md")
DASHBOARD_DATA = os.path.join(OUTPUT_DIR, "dashboard_data.json")

# --- INTELLIGENCE LEXICONS ---

# 1. Topic Classifiers
CATEGORIES = {
    "GEOPOLITICS": ["war", "military", "border", "diplomat", "treaty", "sanction", "sovereignty", "empire", "strategic", "nuclear", "hostage"],
    "CYBER & TECH": ["cyber", "hack", "ransomware", "data breach", "ai", "surveillance", "semiconductor", "digital", "crypto", "spyware"],
    "GLOBAL ECONOMY": ["trade", "tariff", "supply chain", "inflation", "currency", "market", "imf", "oil", "energy", "debt", "recession"],
    "LEADERSHIP": ["election", "parliament", "ceo", "resignation", "scandal", "protest", "policy", "regime", "coup"]
}

# 2. Industry Mapping
INDUSTRIES = {
    "ENERGY": ["oil", "gas", "pipeline", "nuclear", "grid", "power", "renewables", "lithium", "coal", "barrel", "lng"],
    "FINANCE": ["bank", "currency", "inflation", "stock", "crypto", "debt", "imf", "rate", "equity", "bond"],
    "DEFENSE": ["military", "weapon", "missile", "army", "navy", "defense", "drone", "aerospace", "fighter"],
    "TECH": ["cyber", "ai", "chip", "semiconductor", "data", "software", "cloud", "platform", "server"],
    "LOGISTICS": ["supply chain", "cargo", "port", "tariff", "shipping", "container", "freight", "vessel", "transit"]
}

# 3. GLOBAL CHOKEPOINTS (Replaced Countries)
# Mapping specific names to broad keywords to catch all relevant news
CHOKEPOINTS = {
    "Strait of Hormuz": ["hormuz", "persian gulf", "oil tanker", "iran coast", "oman gulf"],
    "Bab el-Mandeb (Red Sea)": ["bab el-mandeb", "red sea", "houthi", "suez", "yemen coast", "aden"],
    "Malacca Strait": ["malacca", "singapore strait", "south china sea passage"],
    "Panama Canal": ["panama canal", "gatun", "panama drought"],
    "Taiwan Strait": ["taiwan strait", "taipei water", "china sea"],
    "Turkish Straits": ["bosphorus", "dardanelles", "black sea access"],
    "Cape of Good Hope": ["good hope", "cape route", "africa tip"]
}

# 4. Severity Keywords
HIGH_RISK_TERMS = ["war", "attack", "crisis", "crash", "sanction", "nuclear", "invasion", "collapse", "conflict", "dead", "kill", "blocked", "closed"]
MED_RISK_TERMS = ["tariff", "protest", "inflation", "hack", "breach", "tension", "dispute", "warning", "ban", "restriction", "delay", "reroute"]

# 5. Marketing Hooks
HOOKS = [
    "Supply chain alert: Critical chokepoint activity detected...",
    "Why logistics leaders are watching this waterway today...",
    "The hidden risk in global trade corridors...",
    "Strategic analysis: Disruption signals in key passage..."
]

# --- CONTEXTUAL ENGINE ---

def analyze_risk_context(text):
    """
    Calculates a risk score based on both KEYWORDS and SENTIMENT.
    """
    text_lower = text.lower()
    
    # A. Get Base Keyword Score
    base_score = 1
    if any(term in text_lower for term in HIGH_RISK_TERMS): base_score = 3
    elif any(term in text_lower for term in MED_RISK_TERMS): base_score = 2

    # B. Get Sentiment Score (-1.0 to +1.0)
    sentiment = sia.polarity_scores(text)['compound']

    # C. Apply Contextual Weighting
    final_score = base_score

    if sentiment < -0.3: 
        final_score += 1.5 # Amplify Risk
    elif sentiment > 0.3:
        final_score -= 1.5 # Dampen Risk
    
    return max(1, min(5, round(final_score, 1)))

def extract_entities(text):
    text_lower = text.lower()
    
    # Find Chokepoints (Check values in dictionary)
    found_chokepoints = []
    for name, keywords in CHOKEPOINTS.items():
        if any(k in text_lower for k in keywords):
            found_chokepoints.append(name)

    # Find Industries
    found_industries = [ind for ind, kw in INDUSTRIES.items() if any(k in text_lower for k in kw)]
    
    return found_chokepoints, found_industries

def categorize_item(text):
    text = text.lower()
    for category, keywords in CATEGORIES.items():
        if any(word in text for word in keywords):
            return category
    return "GENERAL UPDATES"

# --- MAIN LOOP ---

def fetch_and_process():
    print("Avellon Intelligence: Scanning Global Chokepoints...")
    
    if not os.path.exists(FEED_FILE):
        print(f"Warning: {FEED_FILE} not found. Using default feeds.")
        feeds = ["http://feeds.bbci.co.uk/news/world/rss.xml"] 
    else:
        with open(FEED_FILE, "r") as f:
            feeds = [line.strip() for line in f.readlines() if line.strip()]

    processed_data = {cat: [] for cat in CATEGORIES.keys()}
    processed_data["GENERAL UPDATES"] = []
    
    # Counters
    chokepoint_risk_map = {c: 0 for c in CHOKEPOINTS.keys()}
    industry_risk_map = {i: 0 for i in INDUSTRIES.keys()}

    seen_titles = set()
    total_scanned = 0

    for url in feeds:
        try:
            print(f"Fetching: {url}")
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:10]:
                if entry.title in seen_titles: continue
                seen_titles.add(entry.title)
                total_scanned += 1

                full_text = f"{entry.title} {entry.get('summary', '')}"
                category = categorize_item(full_text)
                
                # --- SCORING ---
                risk_score = analyze_risk_context(full_text)
                chokepoints, industries = extract_entities(full_text)
                
                # Update Counters
                for cp in chokepoints: chokepoint_risk_map[cp] += risk_score
                for i in industries: industry_risk_map[i] += risk_score

                # Determine Color
                risk_color = "red" if risk_score >= 3.5 else "yellow" if risk_score >= 2.5 else "green"

                item = {
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.summary[:200] + "..." if "summary" in entry else "No detail available.",
                    "source": feed.feed.get("title", "Global Wire"),
                    "published": entry.get("published", datetime.utcnow().strftime("%Y-%m-%d")),
                    "risk_score": risk_score,
                    "risk_color": risk_color
                }
                processed_data[category].append(item)
                
        except Exception as e:
            print(f"Failed to parse {url}: {e}")

    # Sort & Rank
    top_chokepoints = sorted(chokepoint_risk_map.items(), key=lambda x: x[1], reverse=True)[:5]
    top_industries = sorted(industry_risk_map.items(), key=lambda x: x[1], reverse=True)

    print(f"Scan complete. {total_scanned} items processed.")
    return processed_data, top_chokepoints, top_industries

def generate_reports(data, top_chokepoints, top_industries):
    today = datetime.utcnow().strftime("%d %B %Y")

    # 1. DASHBOARD DATA
    dashboard_json = {
        "generated_at": today,
        "stats": {k: len(v) for k, v in data.items()},
        # Send Chokepoints instead of Countries
        "top_chokepoints": [{"name": c[0], "score": round(c[1], 1)} for c in top_chokepoints],
        "industry_risks": [{"name": i[0], "score": round(i[1], 1)} for i in top_industries],
        "items": data
    }
    
    with open(DASHBOARD_DATA, "w", encoding="utf-8") as f:
        json.dump(dashboard_json, f, indent=4)
    
    # 2. EXECUTIVE BRIEF
    brief_content = f"""# AVELLON INTELLIGENCE: DAILY EXECUTIVE BRIEF
**Date:** {today}
**Classification:** INTERNAL USE ONLY
**Focus:** Global Risk & Strategic Opportunity

---
## ⚓ CRITICAL CHOKEPOINTS (Daily Scan)
"""
    for cp in top_chokepoints:
        if cp[1] > 0: brief_content += f"- **{cp[0]}** (Risk Score: {round(cp[1], 1)})\n"
    
    brief_content += "\n---\n"

    has_news = False
    for category, items in data.items():
        if not items: continue
        has_news = True
        brief_content += f"\n## 🏛 {category}\n"
        for item in items[:5]:
            icon = "🔴" if item['risk_color'] == "red" else "🟡" if item['risk_color'] == "yellow" else "🟢"
            brief_content += f"**{icon} {item['title']}**\n"
            brief_content += f"> *{item['summary']}* ([Source]({item['link']}))\n\n"

    if not has_news:
        brief_content += "\nNo significant risk updates found in today's scan.\n"

    brief_content += "---\n*Generated by Avellon Risk Engine v2.0*"

    # 3. CONTENT STUDIO
    content_output = f"""# AVELLON MARKETING STUDIO
**Date:** {today}
**Goal:** Thought Leadership & Lead Gen
**Strategy:** Translate risk into business value.

---
"""
    for category, items in data.items():
        if not items or category == "GENERAL UPDATES": continue
        top_story = items[0]
        content_output += f"## 📝 DRAFT POST: {category.title()} Angle\n"
        content_output += f"**Source News:** {top_story['title']}\n\n"
        content_output += "**LinkedIn Hook Options:**\n"
        content_output += f"1. 🛑 {HOOKS[0]}\n"
        content_output += f"2. 💡 {HOOKS[1]}\n\n"
        content_output += "**Draft Body Structure:**\n"
        content_output += f"- **The News:** {top_story['title']}\n"
        content_output += "- **The Insight:** This isn't just political; it's a warning signal for market stability.\n"
        content_output += "- **The Avellon View:** Resilience is the new currency. How is your organization preparing?\n\n"
        content_output += f"**Tags:** #AvellonIntelligence #RiskManagement #{category.replace(' & ', '')} #Strategy\n"
        content_output += "---\n\n"

    # Save Files
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(BRIEF_FILE, "w", encoding="utf-8") as f:
        f.write(brief_content)
    
    with open(CONTENT_FILE, "w", encoding="utf-8") as f:
        f.write(content_output)

    print(f"Success! Reports generated:\n1. {DASHBOARD_DATA} (Dashboard)\n2. {BRIEF_FILE} (Internal)\n3. {CONTENT_FILE} (Marketing)")

def run_agent():
    data, top_chokepoints, top_industries = fetch_and_process()
    generate_reports(data, top_chokepoints, top_industries)

if __name__ == "__main__":
    run_agent()
