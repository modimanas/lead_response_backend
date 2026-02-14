# 📦 What to Share with Intern

## Share These 2 Files (Chat App Only):

```
chat_app/
├── index.html          ⭐ (Main chat interface - all-in-one)
└── README.md          (Instructions for using the app)
```

## The intern needs to:

1. **Get the HTML file**: `index.html`
2. **Open it in a browser**: Double-click or open with their browser
3. **Make sure backend is running**: On `http://localhost:8000`

That's it! No installation, no dependencies, no login.

---

## Backend Code (KEEP ON YOUR SERVER):

✋ Do NOT share with intern. Keep separately:

```
lead_response_backend/
├── llm_engine.py       (LLM logic)
├── main.py            (FastAPI server)
├── models.py          (Data models)
├── session_manager.py (Session management)
├── requirements.txt   (Dependencies)
└── .env              (API keys - NEVER share!)
```

---

## For Intern - Quick Start:

### Option 1: Simple (Recommended)
1. Copy `index.html` to their computer
2. Double-click it
3. Make sure backend is running on localhost:8000

### Option 2: With Local Server (More Professional)
1. Copy entire `chat_app/` folder
2. Open terminal in that folder
3. Run: `python -m http.server 8080`
4. Open: `http://localhost:8080`

---

## Customizing for Intern's Server

If the backend will be on a different server, the intern needs to:

1. Open `index.html` in a text editor
2. Find line ~263: `const API_BASE = 'http://localhost:8000';`
3. Change to: `const API_BASE = 'http://their-server-url:port';`
4. Save and reload in browser

---

## Share This Files:
- ✅ `chat_app/index.html`
- ✅ `chat_app/README.md`
- ✅ `chat_app/SHARE_WITH_INTERN.md` (this file)

## Don't Share:
- ❌ `lead_response_backend/` (backend code)
- ❌ `.env` file (contains API keys)
- ❌ Any Python files
- ❌ `venv/` folder
