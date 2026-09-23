#!/bin/bash
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║         ALIAS v0.1.0                     ║"
echo "║  AI-assisted Login Anomaly Investigation ║"
echo "║              System                      ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "[*] Starting ALIAS Backend..."
cd backend/app && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

echo "[*] Starting ALIAS Frontend..."
cd ../../frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "[OK] ALIAS is running."
echo "[*] Backend: http://localhost:8000"
echo "[*] Frontend: http://localhost:5173"
echo "[*] API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop."

wait $BACKEND_PID $FRONTEND_PID
