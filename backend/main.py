# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

import os
import random

from dotenv import load_dotenv
from openai import OpenAI

# Gemini (may not be installed; handled gracefully)
try:
    import google.generativeai as genai
except Exception:
    genai = None

from nlp.emotional_model import EmotionAnalyzer  # make sure filename matches
from nlp.intent_detection import detect_intent
from nlp.crisis_detection import is_crisis

# -----------------------------------------------------------------------------
# FastAPI app + CORS
# -----------------------------------------------------------------------------

app = FastAPI(title="NeuroCare Mental Health Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in dev, allow all; in prod, restrict to frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Environment + LLM clients
# -----------------------------------------------------------------------------

load_dotenv(dotenv_path=".env")

# Emotion model
emotion_analyzer = EmotionAnalyzer()

# OpenAI client
_OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if _OPENAI_KEY and not _OPENAI_KEY.startswith("sk-REPLACE"):
    try:
        client = OpenAI(api_key=_OPENAI_KEY)
        print("OpenAI client initialised.")
    except Exception as e:
        print("OpenAI client init error:", e)
        client = None
else:
    client = None
    print("OpenAI API key not found or placeholder — OpenAI client disabled.")

# Gemini client
_GEMINI_KEY = os.getenv("GEMINI_API_KEY")
print(f"DEBUG: GEMINI_API_KEY from env: {_GEMINI_KEY[:20] if _GEMINI_KEY else 'NOT FOUND'}...")
if genai is not None and _GEMINI_KEY and _GEMINI_KEY.strip() != "":
    try:
        genai.configure(api_key=_GEMINI_KEY)
        
        # Try different Gemini models in order of preference
        gemini_models_to_try = [
            "gemini-1.5-flash",  # Fast and widely available
            "gemini-1.5-pro",    # More capable but may not be available
            "gemini-pro",        # Fallback to standard model
        ]
        
        gemini_model = None
        for model_name in gemini_models_to_try:
            try:
                gemini_model = genai.GenerativeModel(model_name)
                print(f"Gemini client initialised with model: {model_name}")
                break
            except Exception as e:
                print(f"Model {model_name} not available: {e}")
                continue
        
        if gemini_model is None:
            print("Gemini: No suitable model found. Using template responses.")
    except Exception as e:
        print("Gemini client init error:", e)
        gemini_model = None
else:
    gemini_model = None
    print("Gemini SDK not installed or GEMINI_API_KEY missing — Gemini disabled.")

# -----------------------------------------------------------------------------
# Pydantic models
# -----------------------------------------------------------------------------

class HistoryMessage(BaseModel):
    sender: str  # "user" or "bot"
    text: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[HistoryMessage]] = None
    user_id: Optional[str] = None
    mode: Optional[str] = "gemini"  # "gemini" | "openai"


class ChatResponse(BaseModel):
    reply: str
    emotion_label: str
    emotion_score: float
    intent: str
    is_crisis: bool
    llm_mode: str  # "gemini" | "openai" | "template"

# -----------------------------------------------------------------------------
# Template responses (fallback / simple intents / crisis)
# -----------------------------------------------------------------------------

RESPONSES = {
    "greeting": [
        "Hi! I'm NeuroCare. I'm really glad you reached out. What's going on in your world today?",
        "Hello! It's good to see you. I'm here to listen whenever you need to talk. How are you feeling right now?",
        "Hey there! Thanks for opening up to me. I'm genuinely here to support you. What's on your mind?",
    ],
    "smalltalk": [
        "I appreciate you checking in with me! But I'm really here to understand what's happening with YOU. Is there something weighing on your heart today?",
        "That's kind of you to ask, but I'm mainly interested in you. Tell me—how are you really doing? What's been on your mind lately?",
        "I exist to listen to you. So let's focus on you for a moment—what's something you've been wanting to talk about?",
    ],
    "stress": [
        "It sounds like there's a lot of pressure on your shoulders right now. That's a heavy load to carry. Let's break it down together—what feels like the biggest stressor?",
        "Stress can feel so overwhelming when everything piles up. I'm here with you. What's the main thing that's been stressing you out?",
        "You're dealing with a lot right now. That takes courage to even acknowledge. Can you tell me more about what's causing the most stress?",
    ],
    "anxiety": [
        "Anxiety can be so exhausting and paralyzing. I'm sorry you're experiencing that. What does the anxiety feel like for you? When does it hit the hardest?",
        "Anxious thoughts can spiral so quickly. You're not alone in this. Would you like to talk about what's triggering your anxiety right now?",
        "Anxiety is tough to deal with. I'm here to listen and help you work through it. What's your anxiety telling you that worries you?",
    ],
    "sadness": [
        "I'm really sorry you're feeling this way. Sadness can feel so lonely. I want you to know I'm here. What's been making you feel down?",
        "Your sadness matters, and I'm grateful you're sharing it with me. Something clearly hurt or disappointed you. Can you tell me what happened?",
        "Sadness is a heavy emotion to carry alone. You don't have to. I'm listening. What's at the heart of how you're feeling?",
    ],
    "motivation": [
        "It's completely normal to feel unmotivated sometimes—you're human. Let's think about this together. What's draining your motivation right now?",
        "Losing motivation can feel like you're stuck. But reaching out is already a positive step! Tell me, what would help reignite your spark?",
        "Motivation ebbs and flows. It's okay to not feel it right now. But let's explore together—what's one small thing that might help you move forward?",
    ],
    "goodbye": [
        "I'm so glad we got to talk today. Remember, you're stronger than you know. Take care of yourself, and come back whenever you need to. You've got this! 💚",
        "Thank you for opening up to me. You're doing better than you think. Be gentle with yourself, and know I'm always here. See you soon!",
        "It was really meaningful talking with you. You matter more than you realize. Rest well, and remember—reaching out takes courage. I'm proud of you. 💚",
    ],
    "gratitude": [
        "You're so welcome! I'm here for you, and I genuinely care about your wellbeing. Don't hesitate to come back if you need support.",
        "I'm truly honored I could help. You deserve all the support in the world. Remember, seeking help is a sign of strength, not weakness.",
        "That means so much to me. Taking care of yourself is what matters most. I'll always be here to listen and support you. 💚",
    ],
    "unknown": [
        "I'm here and I'm listening. Can you tell me more about what you're experiencing? What's going on?",
        "That sounds important to you. I'd love to understand better—can you share a bit more about how it's affecting you?",
        "Help me understand what you're going through. I'm genuinely interested in supporting you. What's really on your mind?",
    ],
    "crisis": [
        (
            "I'm genuinely concerned about your safety right now. I'm an AI and not a professional, "
            "but your life is incredibly important. PLEASE reach out immediately to someone who can help:\n"
            "• Call 988 (Suicide & Crisis Lifeline in the US) or text HOME to 741741\n"
            "• Call emergency services (911 in the US)\n"
            "• Tell a trusted friend, family member, or counselor\n"
            "You don't have to go through this alone. Please reach out for help right now. You deserve support. 💚"
        )
    ],
}


def choose_response(intent: str, crisis_flag: bool) -> str:
    if crisis_flag:
        return RESPONSES["crisis"][0]
    if intent in RESPONSES:
        return random.choice(RESPONSES[intent])
    return random.choice(RESPONSES["unknown"])

# -----------------------------------------------------------------------------
# OpenAI-based reply (more human-like)
# -----------------------------------------------------------------------------

def generate_llm_reply(
    user_message: str,
    emotion: str,
    intent: str,
    crisis_flag: bool,
    history: Optional[List[Dict[str, Any]]] = None,
) -> str:
    if crisis_flag:
        return RESPONSES["crisis"][0]

    if client is None:
        print("DEBUG: OpenAI client None; using template fallback.")
        return choose_response(intent, crisis_flag)

    # Strong system prompt forcing specificity and referencing the user's text/intent
    system_msg = (
        "You are NeuroCare — a warm, deeply empathetic mental health support assistant. "
        "Your role is to listen, validate, and gently guide. "
        "You are NOT a medical professional, but you ARE genuinely compassionate. "
        "\n\n"
        "CRITICAL RESPONSE RULES:\n"
        "1. FIRST SENTENCE: Directly acknowledge what the user shared. Reference specific words or emotions they mentioned. "
        "Examples: 'I hear that you\'re feeling overwhelmed by your exams...' or 'It sounds like the pressure at work is really weighing on you...'\n"
        "2. VALIDATION: Show you understand the weight of their feelings. Use phrases like 'That makes total sense,' 'It\'s completely understandable,' 'Your feelings are valid.'\n"
        "3. REFRAME: Help them see their situation with gentle perspective. Maybe there's a strength they\'re not noticing, or a small step forward they\'ve already taken.\n"
        "4. PRACTICAL HELP: Offer 1-3 specific, actionable suggestions. Not generic advice—match the suggestion to THEIR situation.\n"
        "5. CONTINUE DIALOGUE: Ask ONE warm follow-up question that shows genuine curiosity about their experience.\n"
        "6. LENGTH: 4-7 sentences. Be thorough but conversational.\n"
        "7. TONE: Warm, natural, human. Like talking to a caring friend who truly gets it.\n"
        "\n"
        "Never repeat earlier responses. Never be generic. Every response is personalized to THIS user, THIS moment."
    )

    messages = [{"role": "system", "content": system_msg}]

    # add recent history (both user and assistant)
    if history:
        for msg in history[-8:]:
            role = "user" if msg.get("sender") == "user" else "assistant"
            # include messages as-is to preserve context
            messages.append({"role": role, "content": msg.get("text","")})

    # Add explicit instruction / user turn
    user_context = (
        f"(Detected emotion: {emotion}; detected intent: {intent})\n"
        f"USER: \"{user_message}\"\n\n"
        "Remember: mention the user's exact situation in the first sentence, validate feelings, "
        "give 1-3 relevant, realistic coping steps, and ask one gentle follow-up question. "
        "End with 'I am not a professional' disclaimer in one sentence."
    )
    messages.append({"role": "user", "content": user_context})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.9,
            max_tokens=420,
        )
        assistant_text = response.choices[0].message.content.strip()
        return assistant_text
    except Exception as e:
        print("OpenAI LLM error, falling back to template:", repr(e))
        return choose_response(intent, crisis_flag)

# -----------------------------------------------------------------------------
# Gemini-based reply (more human-like)
# -----------------------------------------------------------------------------

def generate_gemini_reply(
    user_message: str,
    emotion: str,
    intent: str,
    crisis_flag: bool,
    history: Optional[List[Dict[str, Any]]] = None,
) -> str:
    if crisis_flag:
        return RESPONSES["crisis"][0]

    if intent in ("goodbye", "gratitude"):
        return random.choice(RESPONSES.get(intent, RESPONSES["unknown"]))

    if gemini_model is None:
        print("DEBUG: Gemini model None; using template fallback.")
        return choose_response(intent, crisis_flag)

    system_msg = (
        "You are NeuroCare — a warm, deeply empathetic mental health companion. "
        "Listen carefully, validate emotions, and offer gentle guidance. "
        "You are NOT a doctor, but you ARE genuinely caring.\n\n"
        "RESPONSE STRUCTURE:\n"
        "1. ACKNOWLEDGE: First sentence directly references what they shared. Use their words.\n"
        "2. VALIDATE: Show their feelings are understandable and okay.\n"
        "3. REFRAME: Help them see a different angle—their strength, progress, or hope.\n"
        "4. SUGGEST: Give 1-3 practical, specific coping strategies for THEIR situation.\n"
        "5. ENGAGE: Ask one genuine follow-up question.\n"
        "6. LENGTH: 4-7 natural sentences.\n"
        "7. TONE: Like a caring, understanding friend. Warm, real, genuine.\n\n"
        "Make every response personal. Never generic. Include name acknowledgment if they shared it. "
        "Show you actually listened by reflecting details back."
    )

    # Build conversation text for Gemini (text prompt)
    history_text = ""
    if history:
        for msg in history[-8:]:
            role = "User" if msg.get("sender") == "user" else "NeuroCare"
            history_text += f"{role}: {msg.get('text','')}\n"

    user_prompt = (
        f"{system_msg}\n\n"
        f"Conversation so far:\n{history_text}\n\n"
        f"Detected emotion: {emotion}\nDetected intent: {intent}\n"
        f"User: \"{user_message}\"\n\n"
        "Respond now as NeuroCare (obey the constraints above)."
    )

    try:
        # some genai SDKs provide .generate or .generate_text; we use generate_content as before
        response = gemini_model.generate_content(user_prompt)
        # read .text or fallback to str
        if hasattr(response, "text"):
            reply_text = response.text.strip()
        else:
            reply_text = str(response).strip()
        return reply_text
    except Exception as e:
        print("Gemini error, falling back to template:", repr(e))
        return choose_response(intent, crisis_flag)

# -----------------------------------------------------------------------------
# API routes
# -----------------------------------------------------------------------------

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    user_message = payload.message
    history = payload.history or []
    history_list: Optional[List[Dict[str, Any]]] = [m.model_dump() for m in history] if history else None

    # 1. Emotion
    emo = emotion_analyzer.analyze(user_message)
    emotion_label = emo["label"]
    emotion_score = emo["score"]

    # 2. Intent
    intent = detect_intent(user_message)

    # 3. Crisis detection
    crisis_flag = is_crisis(user_message) or (intent == "crisis")

    requested_mode = (payload.mode or "gemini").lower()

    if crisis_flag:
        reply = RESPONSES["crisis"][0]
        llm_mode = "template"
    else:
        if requested_mode == "gemini" and gemini_model is not None:
            reply = generate_gemini_reply(
                user_message=user_message,
                emotion=emotion_label,
                intent=intent,
                crisis_flag=crisis_flag,
                history=history_list,
            )
            llm_mode = "gemini"
        elif requested_mode == "openai" and client is not None:
            reply = generate_llm_reply(
                user_message=user_message,
                emotion=emotion_label,
                intent=intent,
                crisis_flag=crisis_flag,
                history=history_list,
            )
            llm_mode = "openai"
        else:
            reply = choose_response(intent, crisis_flag)
            llm_mode = "template"

    return ChatResponse(
        reply=reply,
        emotion_label=emotion_label,
        emotion_score=emotion_score,
        intent=intent,
        is_crisis=crisis_flag,
        llm_mode=llm_mode,
    )


@app.get("/")
def root():
    return {
        "message": "NeuroCare API is running. Go to /docs to test the chat endpoint.",
        "endpoints": {
            "chat": "/api/chat",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": "NeuroCare Mental Health API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
