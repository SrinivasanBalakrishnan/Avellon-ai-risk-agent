# agent/topic_generator.py

def generate_topics(alerts):
    high = []
    medium = []

    for alert in alerts:
        title = alert["title"]
        priority = alert["priority"]

        if priority == "HIGH":
            high.append(f"- {title}")
        elif priority == "MEDIUM":
            medium.append(f"- {title}")

    output = ""

    if high:
        output += "🔥 HIGH PRIORITY GLOBAL RISKS\n"
        output += "\n".join(high) + "\n\n"

    if medium:
        output += "🟡 MEDIUM PRIORITY WATCHLIST\n"
        output += "\n".join(medium) + "\n\n"

    return output if output else "No major global risks detected today."
