"""Build Gmail search query strings from UI options."""

from __future__ import annotations


def build_query(
    *,
    older_than_value: int | None,
    older_than_unit: str,
    larger_than_mb: float | None,
    has_attachment: bool,
    categories: list[str],
    exclude_starred: bool,
    exclude_important: bool,
    only_unread: bool,
    custom_query: str,
) -> str:
    parts: list[str] = []

    if older_than_value is not None and older_than_value > 0:
        u = older_than_unit.strip().lower()
        if u == "days":
            parts.append(f"older_than:{int(older_than_value)}d")
        elif u == "months":
            parts.append(f"older_than:{int(older_than_value)}m")
        elif u == "years":
            parts.append(f"older_than:{int(older_than_value)}y")

    if larger_than_mb is not None and larger_than_mb > 0:
        # Gmail accepts e.g. larger:5M
        parts.append(f"larger:{int(round(larger_than_mb * 1_000_000))}")

    if has_attachment:
        parts.append("has:attachment")

    if categories:
        if len(categories) == 1:
            parts.append(f"category:{categories[0]}")
        else:
            inner = " OR ".join(f"category:{c}" for c in categories)
            parts.append(f"({inner})")

    if exclude_starred:
        parts.append("-is:starred")

    if exclude_important:
        parts.append("-is:important")

    if only_unread:
        parts.append("is:unread")

    extra = (custom_query or "").strip()
    if extra:
        parts.append(extra)

    return " ".join(parts).strip()
