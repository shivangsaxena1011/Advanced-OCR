@echo off
title Launching AORL - Advanced OCR with Layout Understanding
echo ===================================================
echo   Starting Advanced OCR with Layout Understanding
echo ===================================================
echo.

set ROOT_DIR=%~dp0

:: 1. Launch Backend Server in a new window
echo [1/3] Starting Backend (FastAPI + PaddleOCR) on port 8000...
start "AORL Backend (FastAPI)" cmd /k "cd /d "%ROOT_DIR%backend" && "%ROOT_DIR%backend\.venv\Scripts\uvicorn.exe" app.main:app --reload --port 8000"

:: 2. Launch Frontend Server in a new window
echo [2/3] Starting Frontend (Next.js) on port 3000...
start "AORL Frontend (Next.js)" cmd /k "cd /d "%ROOT_DIR%frontend" && npm run dev"

:: 3. Wait for servers to initialize
echo [3/3] Waiting for servers to initialize...
timeout /t 5 /nobreak >nul

:: 4. Automatically open browser
echo.
echo Opening http://localhost:3000 in your browser...
start http://localhost:3000

echo.
echo ===================================================
echo   AORL is running!
echo   - Frontend: http://localhost:3000
echo   - Backend:  http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo ===================================================
echo.
echo You can close this launch window now. Keep the Backend and Frontend windows open while using the app.
pause
