"""
Gmail cleanup UI: pick filters, preview, then trash or archive in batches.
Run: streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from auth_gmail import (
    get_service_for_account,
    list_accounts,
    migrate_legacy_token,
    remove_account,
    sign_in_new_account,
)
from gmail_ops import (
    Action,
    apply_action,
    empty_trash,
    fmt_bytes,
    list_all_message_ids,
    preview_list,
)
from query_builder import build_query

# One-click preset queries — loads straight into the query box.
QUICK_PRESETS: list[tuple[str, str]] = [
    ("Promotions > 1 yr",         "category:promotions older_than:1y -is:starred"),
    ("Social > 6 mo",             "category:social older_than:6m -is:starred"),
    ("Updates > 1 yr",            "category:updates older_than:1y -is:starred"),
    ("Large attachments > 10 MB", "has:attachment larger:10M -is:starred"),
    ("Newsletters > 6 mo",        "unsubscribe older_than:6m -is:starred -is:important"),
    ("Old sent > 3 yr",           "in:sent older_than:3y"),
]

st.set_page_config(page_title="Gmail Cleanup", layout="wide")

st.title("Gmail cleanup")
st.caption(
    "Connect once with Google OAuth, build a search query from filters, preview matches, "
    "then move messages to Trash or remove Inbox (archive). Empty Trash in Gmail to free storage."
)

if "service" not in st.session_state:
    st.session_state.service = None
if "active_account" not in st.session_state:
    st.session_state.active_account = None
if "built_query" not in st.session_state:
    st.session_state.built_query = ""
if "resolved_ids" not in st.session_state:
    st.session_state.resolved_ids: list[str] = []

# One-time silent migration of legacy token.json → tokens/<email>.json
if "migration_done" not in st.session_state:
    st.session_state.migration_done = True
    migrated = migrate_legacy_token()
    if migrated:
        st.session_state._migration_msg = f"Existing account migrated: {migrated}"

with st.sidebar:
    st.header("Account")

    # Show migration notice once
    if st.session_state.get("_migration_msg"):
        st.info(st.session_state.pop("_migration_msg"))

    accounts = list_accounts()

    if accounts:
        email_options = list(accounts.keys())
        selected = st.selectbox(
            "Saved accounts",
            options=email_options,
            index=email_options.index(st.session_state.active_account)
            if st.session_state.active_account in email_options
            else 0,
            key="sidebar_selected_account",
        )

        col_connect, col_remove = st.columns([3, 2])
        if col_connect.button("Connect", type="primary", use_container_width=True):
            try:
                st.session_state.service = get_service_for_account(selected)
                st.session_state.active_account = selected
                st.rerun()
            except Exception as e:
                st.error(str(e))

        if col_remove.button("Remove", use_container_width=True):
            remove_account(selected)
            if st.session_state.active_account == selected:
                st.session_state.service = None
                st.session_state.active_account = None
            st.rerun()

        st.divider()

    if st.button("Add / switch account", use_container_width=True):
        try:
            email, service = sign_in_new_account()
            st.session_state.service = service
            st.session_state.active_account = email
            st.rerun()
        except FileNotFoundError as e:
            st.error(str(e))
        except Exception as e:
            st.exception(e)

    st.divider()
    if st.session_state.active_account:
        st.success(f"Connected: {st.session_state.active_account}")
    else:
        st.info(
            "Select a saved account and click **Connect**, "
            "or click **Add / switch account** to sign in via browser."
        )

st.divider()

with st.expander("Quick presets — click to load a ready-made query", expanded=True):
    st.caption("Sets the query in the 'Current query' box below. Then Preview and Apply.")
    cols = st.columns(3)
    for i, (label, query) in enumerate(QUICK_PRESETS):
        if cols[i % 3].button(label, use_container_width=True):
            st.session_state.built_query = query
            st.rerun()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Filters")
    use_age = st.checkbox("Older than…", value=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        age_n = st.number_input("Amount", min_value=1, value=365, disabled=not use_age)
    with c2:
        age_unit = st.selectbox(
            "Unit",
            options=["days", "months", "years"],
            index=0,
            disabled=not use_age,
        )

    use_size = st.checkbox("Larger than (MB)", value=False)
    larger_mb = st.number_input(
        "Megabytes",
        min_value=0.0,
        value=5.0,
        step=0.5,
        disabled=not use_size,
    )

    has_attachment = st.checkbox("Has attachment", value=False)

    categories = st.multiselect(
        "Categories (optional)",
        options=["promotions", "social", "updates", "forums"],
        default=[],
        help="Maps to Gmail category: search. Leave empty to not filter by tab.",
    )

    exclude_starred = st.checkbox("Exclude starred", value=True)
    exclude_important = st.checkbox("Exclude important", value=False)
    only_unread = st.checkbox("Only unread", value=False)

    custom = st.text_area(
        "Extra search text (optional)",
        placeholder='e.g. from:linkedin.com -label:"keep"',
        help="Appended to the built query. Uses Gmail’s search syntax.",
    )

with col_b:
    st.subheader("Run")
    max_messages = st.number_input(
        "Max messages per run",
        min_value=1,
        max_value=50_000,
        value=500,
        step=100,
        help="Safety cap: only this many matching messages are loaded and processed.",
    )
    action = st.radio("Action", options=["trash", "archive"], horizontal=True)
    if action == "trash":
        st.warning("Moves to **Trash**. Storage is freed only after you empty Trash in Gmail.")
    else:
        st.info("Removes **Inbox** label (archive). Does not delete or free storage by itself.")

    if st.button("Build query", type="secondary"):
        older_val = int(age_n) if use_age else None
        larger = float(larger_mb) if use_size else None
        q = build_query(
            older_than_value=older_val,
            older_than_unit=age_unit,
            larger_than_mb=larger,
            has_attachment=has_attachment,
            categories=list(categories),
            exclude_starred=exclude_starred,
            exclude_important=exclude_important,
            only_unread=only_unread,
            custom_query=custom,
        )
        st.session_state.built_query = q

    st.text_area("Current query", value=st.session_state.built_query, height=80, disabled=True)

    if st.button("Preview (sample + estimate)", type="secondary"):
        if not st.session_state.service:
            st.error("Sign in first.")
        elif not st.session_state.built_query.strip():
            st.error("Build a query first.")
        else:
            with st.spinner("Loading preview…"):
                try:
                    rows, est, sample_bytes = preview_list(
                        st.session_state.service, st.session_state.built_query, 20
                    )
                    st.session_state.preview_rows = rows
                    st.session_state.preview_estimate = est
                    if est and len(rows) > 0:
                        projected = int((sample_bytes / len(rows)) * est)
                        st.session_state.preview_size_str = fmt_bytes(projected)
                    else:
                        st.session_state.preview_size_str = "—"
                except Exception as e:
                    st.exception(e)

    if "preview_rows" in st.session_state:
        m1, m2 = st.columns(2)
        m1.metric("Matched messages (approx.)", st.session_state.get("preview_estimate", "—"))
        m2.metric("Est. size to free (approx.)", st.session_state.get("preview_size_str", "—"))
        st.dataframe(st.session_state.preview_rows, use_container_width=True, hide_index=True)

    confirm = st.text_input('Type YES to allow apply (matches "Max messages per run")')

    if st.button(f"Apply: {action}", type="primary"):
        if not st.session_state.service:
            st.error("Sign in first.")
        elif not st.session_state.built_query.strip():
            st.error("Build a query first.")
        elif confirm.strip().upper() != "YES":
            st.error('Type YES in the confirmation box.')
        else:
            with st.spinner("Resolving message IDs…"):
                try:
                    ids = list_all_message_ids(
                        st.session_state.service,
                        st.session_state.built_query,
                        int(max_messages),
                    )
                    st.session_state.resolved_ids = ids
                except Exception as e:
                    st.exception(e)
                    st.stop()

            if not st.session_state.resolved_ids:
                st.warning("No messages matched.")
            else:
                with st.spinner(f"Applying {action} to {len(st.session_state.resolved_ids)}…"):
                    try:
                        chosen: Action = "archive" if action == "archive" else "trash"
                        n = apply_action(
                            st.session_state.service,
                            st.session_state.resolved_ids,
                            chosen,
                        )
                        st.success(f"Done. Processed {n} message(s).")
                    except Exception as e:
                        st.exception(e)

st.divider()
st.markdown(
    "**Regular use:** create a desktop shortcut or Task Scheduler entry that runs "
    "`streamlit run app.py` from this folder (after `pip install -r requirements.txt`)."
)

st.divider()
with st.expander("Danger zone: empty Trash"):
    st.warning(
        "Permanently deletes **all** messages in Trash. Cannot be undone. "
        "Only do this after reviewing what you trashed above."
    )
    confirm_empty = st.text_input('Type YES to confirm', key="confirm_empty_trash")
    if st.button("Empty Trash now", type="primary", key="btn_empty_trash"):
        if not st.session_state.service:
            st.error("Sign in first.")
        elif confirm_empty.strip().upper() != "YES":
            st.error('Type YES in the box above to confirm.')
        else:
            with st.spinner("Emptying Trash\u2026"):
                try:
                    empty_trash(st.session_state.service)
                    st.success("Trash emptied. Your Google storage will update within a few minutes.")
                except Exception as e:
                    st.exception(e)
