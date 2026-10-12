@echo off
title Sai Seva FMSC Hub - Phoenix SSSGC
cd /d "%~dp0"

echo =========================================================
echo    Sai Seva - FMSC Group Sign-Up Hub (Phoenix SSSGC)
echo =========================================================
echo Starting local web server on port 8005...
echo Open your browser to: http://localhost:8005
echo.

python -m uvicorn fmsc_signup_hub.app:app --host 0.0.0.0 --port 8005 --reload

pause
