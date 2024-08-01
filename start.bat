@echo off
start "" "python" "server.py"
timeout /t 3 >nul
start "" ngrok http 8000
pause
