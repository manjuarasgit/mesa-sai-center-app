@echo off
echo ========================================
echo   Cricket Match Notifier
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM No config file needed - just scraping and displaying results

echo Checking for India cricket matches...
echo.
python cricket_notifier.py
echo.
echo Script completed.
pause

