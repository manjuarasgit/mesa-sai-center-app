@echo off
REM Edit VENV and folder paths if needed.
set "ROOT=%~dp0"
cd /d "%ROOT%"

if exist "%ROOT%.venv\Scripts\activate.bat" (
  call "%ROOT%.venv\Scripts\activate.bat"
) else (
  echo Create a venv first: python -m venv .venv
  pause
  exit /b 1
)

streamlit run "%ROOT%app.py"
