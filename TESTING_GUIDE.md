# Frontend Setup & Testing Guide

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Frontend Dev Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` (Vite default)

### 3. Ensure Backend is Running

Backend must be running on `http://127.0.0.1:8001`

```powershell
cd backend
python main.py
```

---

## Testing the Full Stack

### Test Checklist

1. **Root Endpoint Check**

   - Open browser: `http://127.0.0.1:8001/`
   - Should see endpoint listing

2. **Health Check**

   - Open browser: `http://127.0.0.1:8001/health`
   - Should see: `{"status": "healthy", "service": "NeuroCare Mental Health API"}`

3. **Swagger API Docs**

   - Open browser: `http://127.0.0.1:8001/docs`
   - Interactive API documentation

4. **Frontend Chat**

   - Open: `http://localhost:5173`
   - Try sending messages about:
     - Stress: "I'm feeling really stressed about work"
     - Anxiety: "I'm having anxiety attacks"
     - Sadness: "I've been feeling really down lately"
     - Motivation: "I've lost all motivation"

5. **Mode Switching**

   - Click "Use: gemini" button to switch between Gemini and OpenAI
   - Observe different response styles

6. **Emotion Detection**
   - Check emotion labels in responses
   - Verify emotional accuracy

---

## Expected Behavior

### Good Response Examples

**Input:** "I've been stressed about my exams coming up"

**Output (Gemini Mode):**

- Reply acknowledges exams specifically
- Validates exam stress
- Offers practical study/coping suggestions
- Asks follow-up question
- Shows: Emotion: FEAR/SADNESS, Intent: stress/exams

**Input:** "I just can't see the point anymore"

**Critical Response:**

- Immediate crisis detection
- Shows resources: 988, text HOME to 741741
- Encourages immediate help-seeking
- Shows: is_crisis: true

---

## Common Issues & Solutions

### Issue: 404 on API Call

**Solution:**

- Verify backend is running: `python main.py`
- Check endpoint URL in App.jsx: `http://127.0.0.1:8001/api/chat`
- Ensure CORS middleware is enabled (it is by default)

### Issue: No Gemini Responses

**Solution:**

- Verify GEMINI_API_KEY is in `.env`
- Check console for Gemini initialization error
- Falls back to template responses automatically

### Issue: No OpenAI Responses

**Solution:**

- Verify OPENAI_API_KEY is in `.env`
- Check console for OpenAI initialization error
- Falls back to template responses automatically

### Issue: Dry Responses Still Showing

**Solution:**

- Clear browser cache (Ctrl+Shift+Delete)
- Restart backend server
- Check `llm_mode` in response - should show "gemini" or "openai", not "template"

---

## Response Quality Checklist

When testing responses, verify:

✅ **Acknowledgment**

- Does it mention the user's specific situation?
- Does it use their words/topic?

✅ **Validation**

- Does it validate their feelings?
- Does it use empathetic language?

✅ **Personalization**

- Is it specific to their input or generic?
- Would it apply to many different inputs?

✅ **Actionability**

- Does it suggest practical coping strategies?
- Are suggestions relevant to their situation?

✅ **Engagement**

- Does it ask a genuine follow-up question?
- Would you want to answer the question?

✅ **Tone**

- Does it sound like a caring friend?
- Or does it sound robotic/clinical?

---

## Environment Variables

### .env file required for backend:

```
OPENAI_API_KEY=sk-your-key-here
GEMINI_API_KEY=your-gemini-key-here
```

Without these keys:

- Responses fall back to templates (still good quality)
- But LLM mode responses won't be available
- Feature still fully functional

---

## Performance Notes

- **Emotion Analysis:** ~500ms (transformers pipeline)
- **Intent Detection:** ~10ms (regex-based)
- **Crisis Detection:** ~5ms (keyword matching)
- **LLM Response:** 2-5 seconds (depends on API latency)
- **Total Request:** 3-6 seconds typical

---

## Architecture Overview

```
Frontend (React + Vite)
    ↓
    [Sends ChatRequest to]
    ↓
Backend (FastAPI)
    ├─ Emotion Analyzer (Transformers)
    ├─ Intent Detector (Rule-based)
    ├─ Crisis Detector (Keyword matching)
    └─ LLM Response Generator
       ├─ Gemini API (if available)
       ├─ OpenAI API (if available)
       └─ Template Fallback (always available)
    ↓
    [Returns ChatResponse]
    ↓
Frontend (Display in Chat)
```

---

## Contact & Support

For issues with:

- **API/Backend:** Check [BACKEND_FIXES_SUMMARY.md](BACKEND_FIXES_SUMMARY.md)
- **Frontend:** Check App.jsx configuration
- **Responses:** Review prompt engineering in main.py

All endpoints are documented at: `http://127.0.0.1:8001/docs`
