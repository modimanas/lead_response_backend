#!/bin/bash
# Quick setup and run script for the Diagnostic Assistant

echo "🚀 Starting Diagnostic Assistant..."
echo ""

# Check if backend is already running
if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "📦 Starting backend server on http://localhost:8000..."
    cd /home/manas-modi/lead_response_backend
    python -m uvicorn main:app --reload &
    sleep 3
else
    echo "✓ Backend already running on port 8000"
fi

echo ""
echo "🌐 Chat app is ready at:"
echo "   file:///home/manas-modi/chat_app/index.html"
echo ""
echo "📱 Or serve with Python:"
echo "   cd /home/manas-modi/chat_app"
echo "   python -m http.server 8080"
echo "   Then open: http://localhost:8080"
echo ""
echo "✅ Everything is set up!"
