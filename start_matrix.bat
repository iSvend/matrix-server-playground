@echo off
cd /d %~dp0

echo === CONNECTING TO THE MATRIX ===
echo.

python\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000

start http://localhost:8000
pause
