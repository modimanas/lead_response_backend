# Diagnostic Chat App

A simple, clean chat interface for the Diagnostic Assistant backend.

## Features

✨ **No Login Required** - Just open and use
✨ **Simple Chat Interface** - Type your issue or select options
✨ **Multi-Step Diagnosis** - Asks 4-8 questions to narrow down the issue
✨ **Clean UI** - Modern, responsive design that works on all devices

## How to Use

### 1. Start the Backend

Make sure the backend is running:

```bash
cd /home/manas-modi/lead_response_backend
python -m uvicorn main:app --reload
```

The backend will run on `http://localhost:8000`

### 2. Open the Chat App

Simply open `index.html` in your browser:
- Double-click the `index.html` file, OR
- Right-click → Open with → Your Browser, OR
- Use a local server: `python -m http.server 8080`

### 3. Use the App

1. **First message**: Describe your issue (e.g., "My WiFi keeps disconnecting")
2. **Select options**: Click on the options provided or type your own answer
3. **Answer questions**: Keep answering until you get the diagnosis
4. **Get result**: See a concise diagnosis in the final response

## Customizing the Backend URL

If your backend is running on a different URL, edit line 263 in `index.html`:

```javascript
const API_BASE = 'http://localhost:8000';  // Change this URL
```

Change it to:
```javascript
const API_BASE = 'http://your-backend-url:port';
```

## File Structure

```
chat_app/
├── index.html          # Complete chat interface (all-in-one file)
└── README.md          # This file
```

## Browser Support

Works on all modern browsers:
- Chrome/Chromium
- Firefox
- Safari
- Edge

## Notes

- No backend installation needed on the client side
- No cookies or local storage required
- Each conversation is independent
- Responsive design works on mobile and desktop
