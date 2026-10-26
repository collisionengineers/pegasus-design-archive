"""The v42 mockup's states: one per captured live page the mail simplification changes.

In the live application (v41 Stage 2), clicking an e-mail on /Inbox opens #mailMessageDialog
(_MessageDialog.cshtml) inside [data-mail-dialog-root] over /Inbox. Every message-m* state
mounts that dialog over its Inbox scope (All or No Case Found) in both Today and Proposal.
In Today the dialog carries the 380px right-hand Decision column with twelve Classification
chips; in Proposal the Decision column is replaced by the streamlined cog settings menu
(#icon-settings) in the dialog header.
"""
from __future__ import annotations

INBOX, CASE, WORK = "Inbox", "Case", "Work Centre"


def s(key: str, label: str, group: str, lane: str, capture: str | None = None, **extra) -> dict:
    return {"key": key, "label": label, "group": group, "lane": lane, "capture": capture or key, **extra}


STATES: list[dict] = [
    s("inbox", "Inbox · All", INBOX, "inbox"),
    s("inbox-no-case-found", "Inbox · No Case Found", INBOX, "inbox"),
    s("inbox-dismissed", "Inbox · Dismissed", INBOX, "inbox"),
    s("inbox-rows-ticked", "Inbox · two rows ticked", INBOX, "inbox", "inbox"),
    s("message-m1", "Message dialog · New instruction, no Case (settings open)", INBOX, "inbox", "inbox",
      dialog="m1", settings_open=True),
    s("message-m2", "Message dialog · Case update on a Report sent Case (settings open)", INBOX, "inbox", "inbox",
      dialog="m2", settings_open=True),
    s("message-m4", "Message dialog · Query on a Report sent Case (settings open)", INBOX, "inbox", "inbox",
      dialog="m4", settings_open=True),
    s("message-m4-ai-reply", "Message dialog · Query, composer on the AI draft", INBOX, "inbox", "inbox",
      dialog="m4-ai-reply", settings_open=False),
    s("message-m3", "Message dialog · photographs, no Case", INBOX, "inbox", "inbox-no-case-found",
      dialog="m3", settings_open=False),
    s("message-m7", "Message dialog · Billing, no Case (settings open)", INBOX, "inbox", "inbox-no-case-found",
      dialog="m7", settings_open=True),
    s("message-m11", "Message dialog · Cancellation on a Case in Report preparation (settings open)", INBOX, "inbox", "inbox",
      dialog="m11", settings_open=True),
    s("message-m12", "Message dialog · thank-you on a Report sent Case (settings open)", INBOX, "inbox", "inbox",
      dialog="m12", settings_open=True),
    s("case", "Case · Correspondence", CASE, "inbox", "case", scroll="#section-files"),
    s("case-queries", "Case · Queries", CASE, "inbox", "case", scroll="#section-queries"),
    s("case-queries-assign", "Case · Assign query dialog", CASE, "inbox", "case", scroll="#section-queries"),
    s("case-aside-query", "Case · Next action and Actions menu with an open query", CASE, "inbox", "case"),
    s("case-qdos26220", "Case · Cancellation received", CASE, "inbox", "case-qdos26220"),
    s("work-centre", "Work Centre · Needs attention", WORK, "shell"),
    s("work-centre-mine", "Work Centre · Mine", WORK, "shell"),
    s("cases-query", "Cases · Queries", WORK, "intake"),
]

# Live routes with no captured path of their own, mapped to the nearest state.
ROUTES: list[tuple[str, str]] = [
    ("/", "work-centre"),
    ("/Index", "work-centre"),
    ("/Inbox", "inbox"),
    ("/Inbox?queue=no_case_found", "inbox-no-case-found"),
    ("/Inbox?folder=dismissed", "inbox-dismissed"),
    ("/Cases", "cases-query"),
    ("/Cases/bee37ce3-c710-4a5b-8e2c-67e8ed6ad8cb", "case-qdos26220"),
    ("/Cases/85de4c48-ed02-445f-a2ce-d97a087c19dd", "case"),
    ("/Cases/", "case"),
]
