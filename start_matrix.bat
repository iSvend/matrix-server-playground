@echo off
cd /d %~dp0

set PORT=8000

echo === CONNECTING TO THE MATRIX ON PORT %PORT% ===
echo.

REM --- Kill any process already using the port ---
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT%') do (
    echo Found existing process on port %PORT%, killing PID %%a
    taskkill /PID %%a /F > nul 2>&1
)

REM --- Open browser ---
start http://localhost:%PORT%
echo Starting server...
echo.

REM --- Start server (BLOCKING) ---
python\python.exe -m uvicorn app:app --host 127.0.0.1 --port %PORT%

REM --- If we ever get here, server exited ---
echo.
echo === SERVER STOPPED ===
pause