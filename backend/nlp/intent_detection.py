# backend/nlp/intent_detection.py

from typing import Literal

IntentType = Literal[
    "greeting",
    "smalltalk",
    "stress",
    "anxiety",
    "sadness",
    "tiredness",
    "loneliness",
    "self_esteem",
    "work_study",
    "relationship",
    "exams",
    "motivation",
    "gratitude",
    "goodbye",
    "affirmation",
    "negation",
    "uncertainty",
    "coping_request",
    "crisis",
    "unknown",
]


def detect_intent(text: str) -> IntentType:
    """
    Simplified but powerful rule-based intent detection.
    Returns a single intent string (used by the LLM + templates).
    """
    t = text.lower().strip()

    if not t:
        return "unknown"

    # --- Exams / academic stress (check early - high priority) ---
    if any(k in t for k in ["exam", "test", "college", "study", "fail", "result", "marks", "grades"]):
        return "exams"

    # --- Anxiety ---
    if any(k in t for k in ["anxious", "anxiety", "panic", "fear", "nervous", "scared", "terrified", "overthinking"]):
        return "anxiety"

    # --- Tiredness / exhaustion ---
    if any(k in t for k in ["tired", "exhausted", "burnt out", "burnout", "sleepy", "no energy", "drained", "fatigued"]):
        return "tiredness"

    # --- Sadness ---
    if any(k in t for k in ["sad", "hopeless", "lonely", "worthless", "depressed", "depression", "crying", "empty"]):
        return "sadness"

    # --- Stress ---
    if any(k in t for k in ["stressed", "stress", "pressure", "overwhelmed"]):
        return "stress"

    # --- Goodbye ---
    if any(k in t for k in ["bye", "goodbye", "see you", "good night", "goodnight", "gn", "got to go"]):
        return "goodbye"

    # --- Gratitude ---
    if any(k in t for k in ["thanks", "thank you", "thx", "tysm", "ty", "appreciate"]):
        return "gratitude"

    # --- Greetings ---
    if any(k in t for k in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
        return "greeting"

    # --- Small talk ---
    if any(k in t for k in ["how are you", "what's up", "whats up"]):
        return "smalltalk"

    # --- Crisis (also handled separately in crisis_detection.py) ---
    if any(k in t for k in ["suicide", "kill myself", "end my life", "self-harm", "hurt myself", "don't want to live"]):
        return "crisis"

    # fallback
    return "unknown"
