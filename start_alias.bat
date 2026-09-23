@echo off
title ALIAS — AI-assisted Login Anomaly Investigation System
echo.
echo  ╔══════════════════════════════════════════╗
echo  ║         ALIAS v0.1.0                     ║
echo  ║  AI-assisted Login Anomaly Investigation ║
echo  ║              System                      ║
echo  ╚══════════════════════════════════════════╝
echo.
echo [*] Initializing ALIAS...

:: Launch Backend (FastAPI)
echo [1/2] Starting ALIAS Backend...
start "ALIAS Backend" cmd /k "cd backend\app && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

:: Launch Frontend (Vite)
echo [2/2] Starting ALIAS Frontend...
start "ALIAS Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo [OK] ALIAS is starting up.
echo [*] Backend: http://localhost:8000
echo [*] Frontend: http://localhost:5173
echo [*] API Docs: http://localhost:8000/docs
echo.
pause
