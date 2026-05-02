@echo off
setlocal
cd /d "%~dp0"
echo Starting Jarvis Web on http://127.0.0.1:8000 (hidden)
powershell -NoProfile -WindowStyle Hidden -Command "Start-Process py -ArgumentList '-3.14 run_web.py' -WindowStyle Hidden"
timeout /t 2 >nul
start "" http://127.0.0.1:8000
endlocal

