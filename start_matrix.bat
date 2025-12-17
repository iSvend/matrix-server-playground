@echo off
cd /d %~dp0

set PORT=67

echo === CONNECTING TO THE MATRIX ON PORT %PORT% ===
echo.

REM --- Kill any process already using the port ---
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT%') do (
    echo Found existing process on port %PORT%, killing PID %%a
    taskkill /PID %%a /F > nul 2>&1
)

REM --- Open browser ---
start http://localhost:%PORT%

REM --- Start server (blocks, as intended) ---
python\python.exe -m uvicorn app:app --host 127.0.0.1 --port %PORT%
