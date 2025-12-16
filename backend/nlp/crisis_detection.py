# backend/nlp/crisis_detection.py

CRISIS_KEYWORDS = [
    "suicide",
    "kill myself",
    "end my life",
    "self-harm",
    "hurt myself",
    "no reason to live",
    "die",
]

def is_crisis(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in CRISIS_KEYWORDS)
