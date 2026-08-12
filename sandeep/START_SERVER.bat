@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM SANDEEP - Jarvis AI Voice Assistant
REM Server Startup Script for Windows
REM ═══════════════════════════════════════════════════════════════════════════

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  🤖  SANDEEP - Jarvis AI Voice Assistant                      ║
echo ║  Starting FastAPI Server...                                    ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Navigate to script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Install requirements if not already installed
echo Checking dependencies...
pip install -q -r requirements.txt 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Warning: Could not install/verify dependencies
    echo Please run: pip install -r requirements.txt
    echo.
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  Starting FastAPI Server...                                    ║
echo ║                                                                ║
echo ║  🌐 http://127.0.0.1:8000/                                    ║
echo ║  📖 Press Ctrl+C to stop                                       ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Start the server
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload

echo.
echo Server stopped.
pause
