"""List and modify messages via Gmail API."""

from __future__ import annotations

from typing import Literal

# Gmail batchModify allows at most 1000 IDs per request.
BATCH_SIZE = 1000

Action = Literal["trash", "archive"]


def fmt_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def list_all_message_ids(service, query: str, max_messages: int) -> list[str]:
    ids: list[str] = []
    page_token: str | None = None

    while len(ids) < max_messages:
        remaining = max_messages - len(ids)
        req = (
            service.users()
            .messages()
            .list(
                userId="me",
                q=query or None,
                pageToken=page_token,
                maxResults=min(500, remaining),
            )
        )
        resp = req.execute()
        for m in resp.get("messages") or []:
            ids.append(m["id"])
            if len(ids) >= max_messages:
                break
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return ids


def preview_list(
    service, query: str, max_preview: int
) -> tuple[list[dict], int | None, int]:
    """Return sample rows, approximate message count, and total sample size in bytes.

    The third return value is the sum of sizeEstimate for the sample — use it
    with the message count to project total storage impact.
    """
    req = (
        service.users()
        .messages()
        .list(userId="me", q=query or None, maxResults=min(20, max_preview))
    )
    resp = req.execute()
    estimate = resp.get("resultSizeEstimate")
    mids = [m["id"] for m in (resp.get("messages") or [])]

    rows: list[dict] = []
    total_bytes = 0
    for mid in mids[:max_preview]:
        full = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=mid,
                format="metadata",
                metadataHeaders=["Subject", "From", "Date"],
            )
            .execute()
        )
        headers = {
            h["name"].lower(): h["value"]
            for h in full.get("payload", {}).get("headers", [])
        }
        size_bytes = full.get("sizeEstimate", 0)
        total_bytes += size_bytes
        rows.append(
            {
                "from": headers.get("from", "")[:80],
                "subject": headers.get("subject", "(no subject)")[:120],
                "date": headers.get("date", "")[:25],
                "size": fmt_bytes(size_bytes),
                "snippet": (full.get("snippet") or "")[:120],
            }
        )
    return rows, estimate, total_bytes


def apply_action(service, message_ids: list[str], action: Action) -> int:
    """Trash or archive in batches. Returns number of messages processed."""
    n = 0
    for i in range(0, len(message_ids), BATCH_SIZE):
        chunk = message_ids[i : i + BATCH_SIZE]
        if action == "trash":
            body = {"ids": chunk, "addLabelIds": ["TRASH"], "removeLabelIds": ["INBOX"]}
        else:
            body = {"ids": chunk, "removeLabelIds": ["INBOX"]}
        service.users().messages().batchModify(userId="me", body=body).execute()
        n += len(chunk)
    return n


def empty_trash(service) -> None:
    """Permanently delete all messages currently in Trash."""
    service.users().messages().emptyTrash(userId="me").execute()
