# Cricket Match Notifier

A Python script that scrapes ESPN Cricinfo for upcoming India cricket matches and sends email/SMS notifications if a match is scheduled within 24 hours.

## Features

- 🔍 Scrapes ESPN Cricinfo for India cricket matches
- ⏰ Checks if matches are within 24 hours
- 📧 Sends email notifications
- 📱 Sends SMS notifications (via Twilio)
- 🔄 Can be scheduled to run periodically

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Email (Optional)

For Gmail:
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the app password in the config file

### 3. Configure SMS (Optional)

1. Sign up for a Twilio account: https://www.twilio.com/
2. Get your Account SID and Auth Token from the Twilio console
3. Get a Twilio phone number
4. Add your recipient phone number

### 4. Create Configuration File

**On Windows:**

1. Copy `config.json.example` to `config.json`:
   ```powershell
   copy config.json.example config.json
   ```
   Or in Command Prompt:
   ```cmd
   copy config.json.example config.json
   ```

2. Edit `config.json` with your credentials:
   - Set `enabled: true` for email or SMS (or both)
   - Fill in your email/SMS credentials
   - Add recipient email/phone number

## Usage

### Run Once

**Option 1: Double-click the batch file**
- Simply double-click `run_notifier.bat`

**Option 2: Use PowerShell**
- Right-click `run_notifier.ps1` → "Run with PowerShell"
- Or open PowerShell and run: `.\run_notifier.ps1`

**Option 3: Command line**
```cmd
python cricket_notifier.py
```

### Schedule to Run Periodically (Windows)

**Easy Method - Use the Setup Script:**

1. Right-click `setup_scheduler.ps1` → "Run with PowerShell"
2. If prompted about execution policy, run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. Follow the prompts to choose how often to check (every 1, 3, 6, 12 hours, or daily)
4. The script will automatically create a Windows Task Scheduler entry

**Manual Method - Task Scheduler:**

1. Press `Win + R`, type `taskschd.msc`, press Enter
2. Click "Create Basic Task" in the right panel
3. Name it "Cricket Match Notifier"
4. Choose trigger (e.g., "Daily" or "When I log on")
5. Set the time/interval
6. Action: "Start a program"
7. Program: `python` (or full path like `C:\Python39\python.exe`)
8. Arguments: `"C:\full\path\to\cricket_notifier.py"`
9. Start in: `C:\full\path\to\project\directory`
10. Check "Open the Properties dialog" and click Finish
11. In Properties, check "Run whether user is logged on or not" if you want it to run in background
12. Click OK (may need to enter your password)

**View/Manage Scheduled Task:**
- Press `Win + R`, type `taskschd.msc`, press Enter
- Look for "CricketMatchNotifier" in the task list

## Configuration Options

### Email Configuration
- `enabled`: Set to `true` to enable email notifications
- `smtp_server`: SMTP server (default: smtp.gmail.com)
- `smtp_port`: SMTP port (default: 587)
- `sender_email`: Your email address
- `sender_password`: Your email password or app password
- `recipient_email`: Where to send notifications

### SMS Configuration
- `enabled`: Set to `true` to enable SMS notifications
- `twilio_account_sid`: Your Twilio Account SID
- `twilio_auth_token`: Your Twilio Auth Token
- `twilio_phone_number`: Your Twilio phone number (format: +1234567890)
- `recipient_phone_number`: Recipient phone number (format: +1234567890)

## Windows-Specific Notes

- **PowerShell Execution Policy**: If you get an error running `.ps1` files, run this in PowerShell (as Administrator):
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- **Python Path**: Make sure Python is added to your system PATH. You can check by running `python --version` in Command Prompt or PowerShell.
- **Running in Background**: When setting up Task Scheduler, you can configure it to run even when you're not logged in.

## Notes

- The script checks for matches involving India within the next 24 hours
- If both email and SMS are enabled, both will be sent
- The script uses web scraping, so it may need updates if ESPN Cricinfo changes their website structure
- Make sure your internet connection is active when running the script
- The script will automatically retry different URLs if one doesn't work

## Troubleshooting

### Email not sending
- Check if 2FA is enabled and you're using an app password (for Gmail)
- Verify SMTP server and port settings
- Check firewall settings

### SMS not sending
- Verify Twilio credentials are correct
- Ensure phone numbers are in E.164 format (+country code + number)
- Check Twilio account balance

### No matches found
- ESPN Cricinfo website structure may have changed
- Check your internet connection
- Verify India has upcoming matches on the website

## License

This project is provided as-is for personal use.

