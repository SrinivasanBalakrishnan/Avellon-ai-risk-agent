# agent/topic_generator.py

from openai import OpenAI
from agent.prompts import SYSTEM_PROMPT

client = OpenAI()

def generate_topics(prioritized_alerts):
    """
    Sends prioritized alerts to the AI and generates
    executive-level LinkedIn topic ideas.
    """

    input_text = "\n".join([
        f"[{a['priority']}] {a['title']} - {a['summary']}"
        for a in prioritized_alerts
        if a["priority"] in ["HIGH", "MEDIUM"]
    ])

    if not input_text.strip():
        return "No significant risks detected today."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": input_text}
        ]
    )

    return response.choices[0].message.content

