@echo off
title SANDEEP — Personal AI Assistant
echo ============================================
echo   SANDEEP — Starting All Systems...
echo ============================================
cd /d "%~dp0"
call venv\Scripts\activate.bat
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
pause
