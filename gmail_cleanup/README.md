# Gmail cleanup (local UI)

Small [Streamlit](https://streamlit.io) app that talks to your Gmail over the official API. You pick filters (age, size, attachments, categories, extra search text), preview a sample, then **trash** or **archive** up to a capped number of messages per run.

**Trash** still counts toward storage until you empty Trash in the Gmail web UI (or delete forever).

## One-time Google Cloud setup

1. Open [Google Cloud Console](https://console.cloud.google.com/) → create or pick a project.
2. **APIs & Services → Library** → enable **Gmail API**.
3. **APIs & Services → Credentials → Create credentials → OAuth client ID**.
4. Set **who may sign in** (Google still documents this as “user type”):
   - Open **[Manage app audience](https://console.cloud.google.com/auth/audience)** (same project selected in the top bar). In the left nav this often appears under **Google Auth Platform → Audience**.
   - Choose **External** if you use a personal **@gmail.com** (or anyone outside one Workspace). **Internal** only allows accounts in *that* Cloud organization.
   - While publishing status is **Testing**, add **Test users** (your exact Gmail address) on that Audience / consent flow—otherwise only listed test users can proceed.
   - The page **APIs & Services → OAuth consent screen** may show mostly **Branding** and **Data access**; if you don’t see Internal/External there, use **Audience** above.
5. Application type: **Desktop app**. Download the JSON.
6. Save the file as `credentials.json` in this folder (`gmail_cleanup/credentials.json`).

### Error `403: org_internal`

That means the consent screen is **Internal** (Workspace-only), but you’re signing in with an account that isn’t in that organization (e.g. personal Gmail). Fix:

1. Go to **[Manage app audience](https://console.cloud.google.com/auth/audience)** and set the app to **External** if you need @gmail.com. (See [Google: Manage app audience](https://support.google.com/cloud/answer/15549945).)
2. If **External** isn’t offered or you can’t switch from Internal, your project may sit under a **Workspace Cloud organization** with restrictive policy—create a **new project** while signed into a **personal** Google account and use that project’s Desktop OAuth client instead.
3. If still in **Testing**, add your Gmail under **Test users**, wait a minute, then try **Sign in with Google** again.

If your employer **requires** Internal apps, you must use your **work Google account** that belongs to that Workspace—not @gmail.com.

## Install and run

```powershell
cd gmail_cleanup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Your browser opens to the app. First **Sign in with Google** completes OAuth and creates `token.json` (kept local; do not commit).

## Using it regularly

- Adjust filters each time (e.g. promotions older than 2 years, then large attachments).
- Click **Build query**, **Preview**, then type **YES** and **Apply**.
- Use a **low max messages** first to verify behavior, then raise the cap.

Optional: pin a shortcut or Task Scheduler job that runs:

`streamlit run "C:\path\to\per\gmail_cleanup\app.py"`

from an activated venv, or use `run_gmail_cleanup.bat` after editing paths inside.

## Permissions

The app requests **Gmail modify** scope so it can list messages and move them (trash/archive). It does not send mail.
