# Mesa Sathya Sai Center - One-Stop Hub App (PWA)

A dedicated, modern **Progressive Web App (PWA)** created for the **Mesa Sathya Sai Center, Arizona (AZ)** to keep all center members, parents, gurus, and youth connected in one place.

---

## Key Features

1. **Center Schedule & "Missed a Session?" Recaps**
   - Live Sunday timeline (Balvikas, Bhajans, Study Circle).
   - "Missed a session?" digest feed featuring weekly lesson summaries, Study Circle key takeaways, Bhajan songs, and embedded interactive lesson slides (e.g. `Lesson21_Slides.html`).

2. **Balvikas / SSE (Spiritual Education for Kids)**
   - Group 1 to Group 4 lesson outlines, value of the week, and weekly homework assignments.
   - Direct interactive slide deck viewer for gurus and students.

3. **Study Circle Hub**
   - Upcoming study topic, facilitator details, reflection discussion prompts, and direct link to Swami's literature (Vahinis, Sathya Sai Speaks).

4. **Sai Bhajans & Songbook**
   - Sunday lead singer schedule, pitch assignments (e.g., 4 White / G#), and instrument allocations.
   - Searchable center songbook with lyrics in English/Transliteration and spiritual meanings.

5. **Feed My Starving Children (FMSC.org) Monthly Seva**
   - FMSC Mesa site location & event details.
   - Age guidelines (kids 5+ with adult supervision ratios).
   - Direct link to `fmsc.org` group registration with group code `MESA-SAI-2026`.
   - Real-time center headcount tracker (kids count + adults count).
   - One-click **"Share to WhatsApp"** button for easy coordination.

6. **Bi-Weekly Homeless Hot Breakfast Seva**
   - Item checklist signup (Oatmeal, Boiled Eggs, Bananas, Coffee, Juice, Utensils) with real-time volunteer pledge tracking.
   - On-site serving & distribution team signup.

7. **Progressive Web App (PWA) & Mobile Installation**
   - Can be added directly to the home screen of any **iPhone (iOS Safari)** or **Android (Chrome)** device without App Store fees or approval delays.

---

## How to Run Locally

Double-click `run_mesa_sai_app.bat` or run the following command in terminal:

```bash
python mesa_sai_app/app.py
```

Then open your browser to [http://localhost:8000](http://localhost:8000).

---

## Free Hosting & Deployment Options

To make this app accessible 24/7 on the internet for all Mesa Sai Center members:

1. **Option A: Deploy to Render / Railway / PythonAnywhere (Free Python Backend)**
   - Push this repository to GitHub.
   - Connect repository to [Render.com](https://render.com) (Free Web Service tier).
   - Set Build Command: `pip install -r requirements.txt` (or install fastapi uvicorn)
   - Set Start Command: `uvicorn mesa_sai_app.app:app --host 0.0.0.0 --port $PORT`

2. **Option B: Deploy to Vercel / Netlify (Free Serverless Static PWA)**
   - Convert API endpoints to Vercel Serverless Python Functions or deploy static `index.html` + Supabase/Firebase backend.

---

## How Members Install on Their Phones

- **iPhone (iOS Safari):** Tap the **Share** button at the bottom of Safari -> Select **"Add to Home Screen"**.
- **Android (Chrome):** Tap the **Install App** banner at the top or Chrome Menu -> **"Add to Home Screen"**.
