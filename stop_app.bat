@echo off
title Stopping AORL Servers
echo ===================================================
echo   Stopping Advanced OCR with Layout Understanding
echo ===================================================
echo.

echo Stopping processes on port 8000 (Backend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>&1

echo Stopping processes on port 3000 (Frontend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>&1

echo.
echo All AORL services have been stopped.
echo.
pause
