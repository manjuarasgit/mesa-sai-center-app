# PowerShell script to set up Windows Task Scheduler for Cricket Notifier
# Run this script as Administrator for best results

Write-Host "Cricket Match Notifier - Task Scheduler Setup" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Warning: Not running as Administrator. Some operations may fail." -ForegroundColor Yellow
    Write-Host "For best results, right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
}

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$notifierScript = Join-Path $scriptDir "cricket_notifier.py"
$pythonExe = (Get-Command python).Source

if (-not (Test-Path $notifierScript)) {
    Write-Host "Error: cricket_notifier.py not found in current directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Script location: $notifierScript" -ForegroundColor Cyan
Write-Host "Python location: $pythonExe" -ForegroundColor Cyan
Write-Host ""

# Get schedule frequency
Write-Host "How often would you like to check for matches?" -ForegroundColor Yellow
Write-Host "1. Every 1 hour"
Write-Host "2. Every 3 hours"
Write-Host "3. Every 6 hours"
Write-Host "4. Every 12 hours"
Write-Host "5. Once per day (at 9 AM)"
Write-Host ""
$choice = Read-Host "Enter your choice (1-5)"

$taskName = "CricketMatchNotifier"
$taskDescription = "Checks ESPN Cricinfo for upcoming India cricket matches and sends notifications"

# Remove existing task if it exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create action
$action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$notifierScript`"" -WorkingDirectory $scriptDir

# Create trigger based on choice
switch ($choice) {
    "1" {
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)
        Write-Host "Setting up task to run every 1 hour..." -ForegroundColor Green
    }
    "2" {
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 3) -RepetitionDuration (New-TimeSpan -Days 365)
        Write-Host "Setting up task to run every 3 hours..." -ForegroundColor Green
    }
    "3" {
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration (New-TimeSpan -Days 365)
        Write-Host "Setting up task to run every 6 hours..." -ForegroundColor Green
    }
    "4" {
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 12) -RepetitionDuration (New-TimeSpan -Days 365)
        Write-Host "Setting up task to run every 12 hours..." -ForegroundColor Green
    }
    "5" {
        $trigger = New-ScheduledTaskTrigger -Daily -At "9:00AM"
        Write-Host "Setting up task to run daily at 9:00 AM..." -ForegroundColor Green
    }
    default {
        Write-Host "Invalid choice. Using default: Every 6 hours" -ForegroundColor Yellow
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration (New-TimeSpan -Days 365)
    }
}

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Create principal (run as current user)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# Register the task
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $taskDescription | Out-Null
    Write-Host ""
    Write-Host "Task scheduled successfully!" -ForegroundColor Green
    Write-Host "Task Name: $taskName" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can view/manage this task in Task Scheduler:" -ForegroundColor Yellow
    Write-Host "  - Press Win+R, type 'taskschd.msc', and press Enter" -ForegroundColor Yellow
    Write-Host "  - Look for task: $taskName" -ForegroundColor Yellow
    Write-Host ""
} catch {
    Write-Host "Error creating scheduled task: $_" -ForegroundColor Red
    Write-Host "You may need to run this script as Administrator" -ForegroundColor Yellow
}

Read-Host "Press Enter to exit"
