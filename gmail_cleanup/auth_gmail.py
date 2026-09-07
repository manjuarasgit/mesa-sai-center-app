"""OAuth2 + Gmail API service builder with multi-account support.

Tokens are stored in tokens/<email>.json so each account is independent.
A legacy token.json (single-account era) is migrated automatically on first run.
"""

from __future__ import annotations

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ("https://www.googleapis.com/auth/gmail.modify",)

_DIR = Path(__file__).resolve().parent
CREDENTIALS_PATH = _DIR / "credentials.json"
TOKENS_DIR = _DIR / "tokens"
_LEGACY_TOKEN = _DIR / "token.json"


def _tokens_dir() -> Path:
    TOKENS_DIR.mkdir(exist_ok=True)
    return TOKENS_DIR


def _refresh_if_needed(creds: Credentials, token_path: Path) -> Credentials:
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def list_accounts() -> dict[str, Path]:
    """Return {email: token_path} for all saved accounts, sorted alphabetically."""
    folder = _tokens_dir()
    return {p.stem: p for p in sorted(folder.glob("*.json"))}


def get_service_for_account(email: str):
    """Return a Gmail service for a saved account, refreshing the token if needed."""
    token_path = _tokens_dir() / f"{email}.json"
    if not token_path.exists():
        raise ValueError(f"No saved token for {email}. Use 'Add account' to sign in.")
    creds = Credentials.from_authorized_user_file(str(token_path), list(SCOPES))
    creds = _refresh_if_needed(creds, token_path)
    if not creds.valid:
        raise ValueError(
            f"Token for {email} has expired or been revoked. "
            "Use 'Add account' to re-authenticate."
        )
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def sign_in_new_account() -> tuple[str, object]:
    """Open browser OAuth flow for a new (or re-authenticated) account.

    Returns (email, service). Token is saved to tokens/<email>.json.
    """
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"Missing {CREDENTIALS_PATH.name}. Download the OAuth Desktop-app client "
            "JSON from Google Cloud Console and save it as credentials.json here."
        )
    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), list(SCOPES))
    creds = flow.run_local_server(port=0)

    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    profile = service.users().getProfile(userId="me").execute()
    email = profile.get("emailAddress", "unknown")

    token_path = _tokens_dir() / f"{email}.json"
    token_path.write_text(creds.to_json(), encoding="utf-8")
    return email, service


def remove_account(email: str) -> bool:
    """Delete the saved token for an account. Returns True if it existed."""
    p = _tokens_dir() / f"{email}.json"
    if p.exists():
        p.unlink()
        return True
    return False


def migrate_legacy_token() -> str | None:
    """One-time migration: if token.json exists and tokens/ is empty, move it over.

    Makes one API call to discover the email address. Returns the email on success.
    """
    if not _LEGACY_TOKEN.exists() or list_accounts():
        return None
    try:
        creds = Credentials.from_authorized_user_file(str(_LEGACY_TOKEN), list(SCOPES))
        _refresh_if_needed(creds, _LEGACY_TOKEN)
        if not creds.valid:
            return None
        service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        profile = service.users().getProfile(userId="me").execute()
        email = profile.get("emailAddress", "unknown")
        token_path = _tokens_dir() / f"{email}.json"
        token_path.write_text(creds.to_json(), encoding="utf-8")
        return email
    except Exception:
        return None
