"""The v42 mockup's states: one per captured live page the mail simplification changes.

lane/capture name the file captured-live/<lane>/<capture>.html, captured from the
application (captured-live/_source/source.txt names the exact source). Every state's
Today is that capture; its Proposal is the capture with the patches from
proposals_inbox.py, proposals_case.py and proposals_work.py applied.
"""
from __future__ import annotations

INBOX, CASE, WORK = "Inbox", "Case", "Work Centre"


def s(key: str, label: str, group: str, lane: str, capture: str | None = None, **extra) -> dict:
    return {"key": key, "label": label, "group": group, "lane": lane, "capture": capture or key, **extra}


STATES: list[dict] = [
    s("inbox", "Inbox · All incoming", INBOX, "inbox"),
    s("inbox-no-case-found", "Inbox · No Case Found", INBOX, "inbox"),
    s("inbox-rows-ticked", "Inbox · two rows ticked", INBOX, "inbox", "inbox"),
    s("message-m1", "Message · New instruction, no Case", INBOX, "inbox"),
    s("message-m2", "Message · Case update on a Report sent Case", INBOX, "inbox"),
    s("message-m4", "Message · Query on a Report sent Case", INBOX, "inbox"),
    s("message-m4-ai-reply", "Message · Query, composer on the AI draft", INBOX, "inbox"),
    s("message-m3", "Message · photographs, no Case", INBOX, "inbox"),
    s("message-m7", "Message · Billing, no Case", INBOX, "inbox"),
    s("message-m11", "Message · Cancellation on a Case in Report preparation", INBOX, "inbox"),
    s("message-m12", "Message · thank-you on a Report sent Case", INBOX, "inbox"),
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
    ("/Cases", "cases-query"),
    ("/Inbox?queue=no_case_found", "inbox-no-case-found"),
    ("/Cases/", "case"),
]
