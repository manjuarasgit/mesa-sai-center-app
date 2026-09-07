# PowerShell script to run Cricket Match Notifier
Write-Host "Running Cricket Match Notifier..." -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# No config file needed - just scraping and displaying results

# Run the script
Write-Host "Checking for India cricket matches..." -ForegroundColor Cyan
Write-Host ""
python cricket_notifier.py

Write-Host ""
Write-Host "Script completed." -ForegroundColor Green
Read-Host "Press Enter to exit"
