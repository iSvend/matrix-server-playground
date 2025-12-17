@echo off
cd /d %~dp0

set PORT=8000

echo === CONNECTING TO THE MATRIX ON PORT %PORT% ===
echo.

REM Open browser first (non-blocking)
start http://localhost:%PORT%

REM Give browser a moment (optional)
timeout /t 1 > nul

REM Start the server (this blocks, as intended)
python\python.exe -m uvicorn app:app --host 127.0.0.1 --port %PORT%
