# Deployment & WhatsApp Setup Guide for Sai FMSC Seva Portal

This guide provides step-by-step instructions for running the **Sai Seva FMSC Group Portal** and sharing it with your Phoenix Sai WhatsApp group so devotees can sign up for upcoming months in seconds.

---

## 🚀 1. Run Locally on Your PC (Double-Click Setup)

1. Double-click the file **`run_fmsc_hub.bat`** in the project folder.
2. The server will start and display:
   ```
   Starting local web server on port 8005...
   Open your browser to: http://localhost:8005
   ```
3. Open `http://localhost:8005` in your browser.
4. **Accessing from your phone on the same Wi-Fi:**
   - Find your PC's local IP address (e.g. `192.168.1.150`).
   - On your phone's browser, open `http://192.168.1.150:8005`.

---

## 🌐 2. Host 100% Free for WhatsApp Members (24/7 Cloud Access)

To allow devotees in your WhatsApp group to access the portal anytime from their mobile phones without needing your computer to stay on, use one of these completely free options:

### Option A: Vercel (Recommended - 60 Seconds, Zero Code)
1. Sign up for a free account at [vercel.com](https://vercel.com).
2. Install the Vercel CLI (`npm i -g vercel`) or deploy via the Vercel Web Dashboard:
   - Click **"Add New Project"** -> Import your GitHub repository or drag and drop the `fmsc_signup_hub` folder.
   - Output directory: `./` (or leave default).
3. Click **Deploy**.
4. You will get an instant, free HTTPS URL (e.g., `https://phoenix-sai-fmsc.vercel.app`).
5. Devotees can bookmark this URL on their iPhones and Androids as a Web App!

### Option B: GitHub Pages (100% Free, Permanent Hosting)
1. Create a repository on [GitHub](https://github.com) named `phoenix-sai-fmsc`.
2. Push or upload `fmsc_signup_hub/index.html` and `fmsc_signup_hub/static/` to the repo.
3. Go to **Settings** -> **Pages** in your repository.
4. Under **Build and deployment**:
   - Source: `Deploy from a branch`
   - Branch: `main` / `root`
   - Click **Save**.
5. In 1 minute, your live site will be accessible at:
   `https://<your-github-username>.github.io/phoenix-sai-fmsc/`

---

## 📱 3. The WhatsApp Group Best Practice (Save Hours of Time!)

### Tip 1: Put the Link in the WhatsApp Group Description
Add the link permanently into your WhatsApp group info:
```text
🌸 Saibaba Group Phoenix SSSGC 🌸
Feed My Starving Children (FMSC) Monthly Volunteer Signups:
👉 https://phoenix-sai-fmsc.vercel.app

Next Sessions: Nov 7, 2026 | Dec 5, 2026
```
Whenever anyone in the group asks for the link or wants to check future months, they can just tap the group title to find it!

---

## ⚡ 4. Monthly Organizer Workflow (When You Book on FMSC)

Whenever you log in to `fmsc.org` and book a new month:

1. **Copy the Join Code or Join URL** from FMSC (e.g. `1NXP4D` or `http://www.fmsc.org/join-group?joincode=1NXP4D`).
2. Open the **Sai FMSC Portal** -> Click the **"Organizer & WhatsApp"** tab at the top.
3. Click **"Add New Month Booking"**:
   - Select the Date (e.g. `2026-11-07` or `2026-12-05`).
   - Paste the Join Code or URL.
   - Click **Save Session**.
4. **Generate the WhatsApp Announcement:**
   - Under the *Instant WhatsApp Message Generator*, select the month.
   - Pick the template:
     - 📣 *Standard Monthly Seva Invite*
     - ⏳ *Spots Filling Up Fast!*
     - 👟 *Final Week Guidelines & Dress Code*
     - 📅 *Multi-Month Schedule Overview*
   - Click **"Open in WhatsApp & Send"**! It automatically opens WhatsApp with the formatted invite and clickable links ready to send to your group.
5. **Populating Attendee Names on FMSC:**
   - In the app, click **"Copy for FMSC Site"**.
   - Go to your FMSC reservation page under *"If you know who is attending, please provide their names below"*.
   - Paste or enter names in seconds without hunting through WhatsApp messages!
