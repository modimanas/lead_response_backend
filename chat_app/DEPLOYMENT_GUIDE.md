# 🚀 Diagnostic Assistant - Deployment Guide

## Quick Start (2 Minutes)

### 1. Start Backend (if not running)
```bash
cd /home/manas-modi/lead_response_backend
/home/manas-modi/lead_response_backend/venv/bin/python -m uvicorn main:app --reload
```

### 2. Open Chat App
Open this in your browser:
```
file:///home/manas-modi/chat_app/index.html
```

---

## 📦 What's Included

### Backend (`/lead_response_backend/`)
- **llm_engine.py** - Smart question generation & diagnosis logic
- **main.py** - FastAPI endpoints
- **session_manager.py** - Session tracking
- **models.py** - Data schemas

### Frontend (`/chat_app/`)
- **index.html** - Complete chat interface (all-in-one file)
- **README.md** - User instructions
- **SHARE_WITH_INTERN.md** - What to share/hide

---

## ✨ Features (Updated)

✅ **Smart Question Generation** - Like ChatGPT, never asks same question twice  
✅ **Conversational Flow** - Natural dialogue with adaptive questioning  
✅ **No Repeated Questions** - Each question targets new information  
✅ **Multi-Domain** - Health, tech, home, finance, automotive, etc.  
✅ **Health-Aware** - Stricter thresholds & disclaimers for medical issues  
✅ **Minimum 4 Questions** - Gets sufficient context before diagnosis  
✅ **Quick Diagnosis** - Stops after 8 questions max  
✅ **Clean UI** - No login, no complexity, just chat  

---

## 🎯 How It Works

1. **User describes issue** - "My WiFi keeps disconnecting"
2. **System generates hypotheses** - 3-4 possible causes
3. **Asks smart questions** - Each targets the gap between top 2
4. **Analyzes answers** - Updates probabilities with Bayesian reasoning
5. **Adapts dynamically** - Never repeats, always asks next logical question
6. **Delivers diagnosis** - After 4-8 questions, gives concise recommendation

---

## 🔧 Backend API Endpoints

### POST /start
Start a new diagnostic session
```
{
  "message": "My WiFi keeps disconnecting"
}
```

### POST /answer
Answer a question
```
{
  "session_id": "abc-123",
  "selected_option": "Multiple times per day"
}
```

### GET /health
Health check
```
Returns: {"status": "Backend running"}
```

---

## 📱 Browser Compatibility

✅ Chrome/Chromium  
✅ Firefox  
✅ Safari  
✅ Edge  
✅ Mobile browsers

---

## ⚙️ Configuration

### Change Backend URL (if hosted elsewhere)
Edit line ~263 in `index.html`:
```javascript
const API_BASE = 'http://localhost:8000';  // Change this
```

To:
```javascript
const API_BASE = 'http://your-server.com:8000';
```

---

## 🚀 Deployment Options

### Option 1: Local File (Simplest)
1. Copy `index.html` to intern's computer
2. Double-click it
3. Backend must run on localhost:8000

### Option 2: Local Web Server
```bash
cd /home/manas-modi/chat_app
python -m http.server 8080
# Open: http://localhost:8080
```

### Option 3: Remote Server
1. Deploy backend to server (e.g., AWS, Heroku, VPS)
2. Update API_BASE URL in index.html
3. Host index.html on any web server
4. Share the link with interns

---

## 📊 Conversation Flow Example

```
User: "My WiFi keeps disconnecting"

Bot: How often does this happen?
↓
User: "Multiple times per day"

Bot: Does it affect all devices or just one?
↓
User: "Only my laptop"

Bot: Have you updated anything recently - software, drivers, router?
↓
User: "Updated browser yesterday"

Bot: When the connection drops, does it come back automatically or need manual reconnect?
↓
User: "Needs manual reconnect"

Bot: [After analysis]
Yeah, probably interference from other devices or a software issue on your laptop. 
Try moving your router to a central location or updating your network drivers. 
If it persists, contact your internet provider.
```

---

## ✅ Checklist Before Sharing

- ✅ Backend running on http://localhost:8000
- ✅ index.html opens without errors
- ✅ Chat flows smoothly
- ✅ No repeated questions
- ✅ Final diagnosis is clear & concise
- ✅ API_BASE URL is correct

---

## 📝 Notes

- Each conversation is independent (no user data saved)
- No login or authentication required
- No cookies or local storage
- All logic runs on backend (frontend is just UI)
- API key (.env) is secure on backend server

---

## 🎉 Ready to Deploy!

The system is now ready for interns to use. 

**Share with them:**
- `index.html` - Main app
- `README.md` - Instructions
- `SHARE_WITH_INTERN.md` - Setup guide

**Keep private:**
- Backend code (llm_engine.py, main.py, etc.)
- .env file (contains API keys)
- All Python files

Enjoy! 🚀
