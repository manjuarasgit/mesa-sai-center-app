# Windows Quick Setup Guide

## Step-by-Step Setup for Windows Users

### Step 1: Install Python (if not already installed)

1. Download Python from https://www.python.org/downloads/
2. During installation, **check "Add Python to PATH"**
3. Verify installation: Open Command Prompt and type `python --version`

### Step 2: Install Required Packages

Open Command Prompt or PowerShell in the project folder and run:
```cmd
pip install -r requirements.txt
```

### Step 3: Configure Notifications

**For Email (Gmail):**
1. Enable 2-Factor Authentication on your Gmail account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an App Password for "Mail"
4. Copy the 16-character password

**For SMS (Twilio):**
1. Sign up at https://www.twilio.com/try-twilio (free trial available)
2. Get your Account SID and Auth Token from the Twilio Console
3. Get a phone number from Twilio (or use trial number)
4. Note your recipient phone number (format: +1234567890)

### Step 4: Create Config File

1. Copy the example config:
   ```cmd
   copy config.json.example config.json
   ```

2. Open `config.json` in Notepad or any text editor

3. Fill in your details:
   - For email: Set `"enabled": true` and add your Gmail and app password
   - For SMS: Set `"enabled": true` and add your Twilio credentials
   - Add recipient email/phone number

### Step 5: Test the Script

**Option A: Double-click `run_notifier.bat`**

**Option B: Run in PowerShell:**
```powershell
.\run_notifier.ps1
```

**Option C: Run in Command Prompt:**
```cmd
python cricket_notifier.py
```

### Step 6: Schedule Automatic Checks (Optional)

**Easy Method:**
1. Right-click `setup_scheduler.ps1`
2. Select "Run with PowerShell"
3. If you see an execution policy error, open PowerShell as Administrator and run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
4. Then run `setup_scheduler.ps1` again
5. Choose how often you want to check (1, 3, 6, 12 hours, or daily)

**Verify it's scheduled:**
- Press `Win + R`, type `taskschd.msc`, press Enter
- Look for "CricketMatchNotifier" in the task list

## Troubleshooting

### "Python is not recognized"
- Python is not in your PATH
- Reinstall Python and check "Add Python to PATH"
- Or add Python manually to System Environment Variables

### "Execution policy" error when running .ps1 files
Run this in PowerShell (as Administrator):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Email not sending
- Make sure you're using an App Password, not your regular Gmail password
- Check that 2FA is enabled on your Gmail account
- Verify SMTP settings in config.json

### SMS not sending
- Verify Twilio credentials are correct
- Check phone numbers are in E.164 format (+country code + number)
- Ensure your Twilio account has credits

### No matches found
- Check your internet connection
- ESPN Cricinfo website structure may have changed
- Try running the script manually to see error messages

## Quick Reference

- **Run once**: Double-click `run_notifier.bat`
- **Schedule**: Run `setup_scheduler.ps1`
- **View scheduled tasks**: `Win + R` → `taskschd.msc`
- **Edit config**: Open `config.json` in Notepad
