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


def _contains_any(text: str, phrases: list[str]) -> bool:
    return any(p in text for p in phrases)


def detect_intent(text: str) -> IntentType:
    """
    Rule-based intent detection for more natural conversation.
    Returns a single intent string (used by the LLM + templates).
    """
    t = text.lower().strip()

    if not t:
        return "unknown"

    # --- Very short replies handled first ---
    if len(t.split()) <= 3:
        if _contains_any(t, ["yes", "yeah", "yep", "sure", "ok", "okay", "ofc", "of course"]):
            return "affirmation"
        if _contains_any(t, ["no", "nope", "nah", "never"]):
            return "negation"
        if _contains_any(t, ["idk", "i dont know", "i don't know", "not sure", "maybe", "kinda"]):
            return "uncertainty"
        if _contains_any(t, ["thanks", "thank you", "thx", "tysm", "ty"]):
            return "gratitude"
        if _contains_any(t, ["bye", "goodbye", "see you", "good night", "goodnight", "gn"]):
            return "goodbye"

    # --- Greetings & small talk ---
    if _contains_any(t, ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
        return "greeting"

    if _contains_any(t, ["how are you", "what's up", "whats up", "how is it going"]):
        return "smalltalk"

    # --- Direct emotional states ---
    if _contains_any(
        t,
        [
            "stressed",
            "stress",
            "pressure",
            "under pressure",
            "overwhelmed with work",
            "burnout",
            "burned out",
        ],
    ):
        return "stress"

    if _contains_any(
        t,
        [
            "anxious",
            "anxiety",
            "panic",
            "panic attack",
            "nervous",
            "scared",
            "terrified",
            "overthinking",
        ],
    ):
        return "anxiety"

    if _contains_any(
        t,
        [
            "sad",
            "depressed",
            "depression",
            "lonely",
            "alone",
            "crying",
            "upset",
            "empty",
            "hurt emotionally",
        ],
    ):
        return "sadness"

    if _contains_any(
        t,
        ["tired", "exhausted", "no energy", "drained", "fatigued", "worn out"],
    ):
        return "tiredness"

    if _contains_any(
        t,
        [
            "no friends",
            "ignored",
            "left out",
            "no one cares",
            "no one understands",
            "i feel alone",
            "i feel lonely",
        ],
    ):
        return "loneliness"

    # --- Self-esteem / self-worth ---
    if _contains_any(
        t,
        [
            "useless",
            "failure",
            "i am a failure",
            "i'm a failure",
            "not good enough",
            "worthless",
            "i hate myself",
            "hate myself",
            "disappointment",
        ],
    ):
        return "self_esteem"

    # --- Work / study / exams ---
    if _contains_any(
        t,
        [
            "exam",
            "exams",
            "test",
            "marks",
            "grades",
            "result",
            "results",
            "semester",
            "internals",
        ],
    ):
        return "exams"

    if _contains_any(
        t,
        [
            "assignment",
            "project",
            "deadline",
            "workload",
            "too much work",
            "studies",
            "study",
            "college",
            "job",
            "office",
            "placement",
            "interview",
        ],
    ):
        return "work_study"

    # --- Relationships / family ---
    if _contains_any(
        t,
        [
            "friend",
            "friends",
            "friendship",
            "relationship",
            "breakup",
            "broke up",
            "ex",
            "partner",
            "girlfriend",
            "boyfriend",
            "family issues",
            "my parents",
            "mom",
            "dad",
            "siblings",
        ],
    ):
        return "relationship"

    # --- Motivation / feeling stuck / guidance ---
    if _contains_any(
        t,
        [
            "no motivation",
            "lost motivation",
            "i'm not motivated",
            "i am not motivated",
            "feel stuck",
            "stuck in life",
            "dont know what to do",
            "don't know what to do",
            "direction in life",
        ],
    ):
        return "motivation"

    # --- Asking directly for help / coping ideas ---
    if _contains_any(
        t,
        [
            "what should i do",
            "how do i handle",
            "how to deal with",
            "how do i deal with",
            "any advice",
            "any suggestion",
            "how can i cope",
            "help me",
        ],
    ):
        return "coping_request"

    # --- Crisis / self-harm (also handled in crisis_detection) ---
    if _contains_any(
        t,
        [
            "suicide",
            "kill myself",
            "end my life",
            "self-harm",
            "self harm",
            "hurt myself",
            "dont want to live",
            "don't want to live",
            "no reason to live",
        ],
    ):
        return "crisis"

    # --- Gratitude / goodbye (longer sentences) ---
    if _contains_any(
        t,
        [
            "thank you so much",
            "thanks a lot",
            "you really helped",
            "this helped",
            "i appreciate",
        ],
    ):
        return "gratitude"

    if _contains_any(
        t,
        [
            "i have to go",
            "got to go",
            "need to sleep",
            "going to sleep",
            "talk to you later",
            "see you later",
        ],
    ):
        return "goodbye"

    # fallback
    return "unknown"
