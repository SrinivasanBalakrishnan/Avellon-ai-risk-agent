# agent/risk_prioritizer.py

HIGH_IMPACT_KEYWORDS = [
    "sanctions", "export ban", "trade restriction", "blockade",
    "war", "conflict", "military escalation",
    "shipping disruption", "chokepoint", "port closure",
    "energy shortage", "oil supply", "gas supply",
    "critical minerals", "rare earth", "semiconductor",
    "currency crisis", "sovereign debt",
    "cyber attack", "infrastructure attack"
]

MEDIUM_IMPACT_KEYWORDS = [
    "tensions", "diplomatic standoff", "policy shift",
    "regulatory risk", "tariffs",
    "investment screening", "national security review",
    "supply risk", "resource nationalism"
]

def classify_risk(alert):
    """
    Classifies a Google Alert entry into HIGH, MEDIUM, or WATCH
    based on business-relevant geopolitical exposure.
    """

    text = (alert["title"] + " " + alert["summary"]).lower()

    high_score = sum(1 for k in HIGH_IMPACT_KEYWORDS if k in text)
    medium_score = sum(1 for k in MEDIUM_IMPACT_KEYWORDS if k in text)

    if high_score >= 2:
        return "HIGH"
    elif high_score == 1 or medium_score >= 2:
        return "MEDIUM"
    else:
        return "WATCH"
