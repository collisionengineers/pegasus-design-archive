"""The v41 mockup's states: one per captured live page.

lane/capture name the file captured-live/<lane>/<capture>.html, captured from the
application (see captured-live/_source/source.txt for the exact source). ibx marks
the Inbox states, whose Proposal is drawn by inbox-designs-v41.js: its preset is the
sub-state the Inbox opens on (scope, dialog, selected, ticked, dismissed).
"""
from __future__ import annotations

SHELL, WORK, INBOX, INTAKE, CASE, ADMIN = (
    "Shell and sign-in", "Work Centre and Search", "Inbox", "Upload and Cases", "Case", "Administration",
)


def s(key: str, label: str, group: str, lane: str, capture: str | None = None, **extra) -> dict:
    return {"key": key, "label": label, "group": group, "lane": lane, "capture": capture or key, **extra}


STATES: list[dict] = [
    # Work Centre and Search
    s("work-centre", "Work Centre · Needs attention", WORK, "shell"),
    s("work-centre-selected", "Work Centre · row open", WORK, "shell"),
    s("work-centre-assign", "Work Centre · Assign Engineer", WORK, "shell"),
    s("work-centre-mine", "Work Centre · Mine", WORK, "shell"),
    s("work-centre-new-cases", "Work Centre · New cases", WORK, "shell"),
    s("work-centre-ai-jobs", "Work Centre · AI jobs", WORK, "shell"),
    s("search", "Search", WORK, "shell"),
    s("search-filters", "Search · more filters", WORK, "shell"),

    # Inbox (PR 1331's AI-drafted query reply included)
    s("inbox", "Inbox", INBOX, "inbox", ibx={"preset": {}}),
    s("inbox-no-case-found", "Inbox · No Case Found", INBOX, "inbox",
      ibx={"preset": {"scope": "nocase"}}),
    s("inbox-sent", "Inbox · Sent Items", INBOX, "inbox", ibx={"preset": {"scope": "sent"}}),
    s("inbox-dismissed", "Inbox · Dismissed", INBOX, "inbox", ibx={"preset": {"scope": "dismissed"}}),
    s("inbox-deleted", "Inbox · Deleted Items", INBOX, "inbox", ibx={"preset": {"scope": "deleted"}}),
    # I18 (R140 a): row ticks and the one bulk form. The live Dismissed capture is empty, so the last state seeds two
    # dismissed messages to show bulk Restore.
    s("inbox-rows-ticked", "Inbox · rows ticked", INBOX, "inbox", "inbox",
      ibx={"preset": {"ticked": "m1,m5"}}),
    s("inbox-rows-ticked-classify", "Inbox · Correct classification for the ticked rows", INBOX, "inbox", "inbox",
      ibx={"preset": {"ticked": "m1,m5", "dialog": "bulk-classify"}}),
    # I18 busy state (finding-mail-bulk-actions criterion 13): the pressed bulk Dismiss says its busy word.
    s("inbox-rows-ticked-busy", "Inbox · bulk Dismiss pressed", INBOX, "inbox", "inbox",
      ibx={"preset": {"ticked": "m1,m5", "busy": "dismiss"}}),
    s("inbox-dismissed-rows-ticked", "Inbox · Dismissed, bulk Restore", INBOX, "inbox", "inbox-dismissed",
      ibx={"preset": {"scope": "dismissed", "dismissed": "m2,m4", "ticked": "m2"}}),
    s("mail-message", "Message · Case update, linked", INBOX, "inbox", "message-m2",
      ibx={"preset": {"dialog": "message", "selected": "m2"}}),
    s("mail-message-new-instruction", "Message · New instruction", INBOX, "inbox", "message-m1",
      ibx={"preset": {"dialog": "message", "selected": "m1"}}),
    s("mail-message-no-case", "Message · No Case Found", INBOX, "inbox", "message-m3",
      ibx={"preset": {"dialog": "message", "selected": "m3", "scope": "nocase"}}),
    s("mail-message-reply", "Message · Reply", INBOX, "inbox", "message-m2-reply",
      ibx={"preset": {"dialog": "compose", "selected": "m2"}}),
    s("mail-message-query", "Message · Query, Draft reply with AI", INBOX, "inbox", "message-m4",
      ibx={"preset": {"dialog": "message", "selected": "m4", "ai": "start"}}),
    s("mail-message-query-queued", "Message · Query, AI draft queued", INBOX, "inbox", "message-m4-ai-queued",
      ibx={"preset": {"dialog": "message", "selected": "m4", "ai": "queued"}}),
    s("mail-message-query-ready", "Message · Query, Reply with AI draft", INBOX, "inbox", "message-m4-ai-ready",
      ibx={"preset": {"dialog": "message", "selected": "m4", "ai": "ready"}}),
    s("mail-message-query-ai-reply", "Message · Query, composer on the AI draft", INBOX, "inbox", "message-m4-ai-reply",
      ibx={"preset": {"dialog": "compose", "selected": "m4", "ai": "ready"}}),
    s("case-correspondence", "Case · Correspondence and Queries", INBOX, "inbox", "case-ai-ready", scroll="#section-files"),

    # Upload and Cases
    s("upload", "Upload", INTAKE, "intake"),
    s("upload-review", "Upload · review", INTAKE, "intake"),
    s("upload-review-new-case", "Upload · review, new Case", INTAKE, "intake"),
    s("cases-not-ready", "Cases · Not ready", INTAKE, "intake", "cases-not_ready"),
    s("cases-unassigned", "Cases · Unassigned", INTAKE, "intake"),
    s("cases-unassigned-unidentified", "Cases · Unassigned, Unidentified", INTAKE, "intake"),
    s("cases-review", "Cases · Review", INTAKE, "intake"),
    s("cases-with-engineer", "Cases · With Engineer", INTAKE, "intake", "cases-with_engineer"),
    s("cases-query", "Cases · Queries", INTAKE, "intake"),
    s("cases-triage", "Cases · Triage", INTAKE, "intake"),
    s("cases-held", "Cases · Held", INTAKE, "intake"),
    s("cases-selected", "Cases · Quick detail", INTAKE, "intake"),
    s("create-manual", "Create case · manual", INTAKE, "intake"),
    s("create-seeded", "Create case · from an instruction", INTAKE, "intake"),
    s("triage", "Triage", INTAKE, "intake"),
    s("triage-finding", "Triage · finding recorded", INTAKE, "intake"),
    s("unidentified", "Unidentified", INTAKE, "intake"),
    s("vehicle-images", "Vehicle images", INTAKE, "intake"),
    s("chaser", "Chaser", INTAKE, "intake"),

    # Case
    s("case-read", "Case · With Engineer", CASE, "case"),
    s("case-edit", "Case · editing", CASE, "case"),
    s("case-not-ready", "Case · report not ready", CASE, "case"),
    s("case-delivery-rules", "Case · Report, rules to answer", CASE, "case", scroll="#section-report"),
    s("case-delivery-plain", "Case · Report, ready to send", CASE, "case", scroll="#section-report"),
    s("case-delivery-stop", "Case · Report, a rule stops sending", CASE, "case", scroll="#section-report"),
    s("case-delivery-missing", "Case · Report, missing attachment", CASE, "case", scroll="#section-report"),
    s("case-report-sent", "Case · Report sent, open query", CASE, "case", scroll="#section-queries"),
    s("case-audit", "Case · Inspection and Audit", CASE, "case"),
    s("case-tasks", "Case · Tasks dialog", CASE, "case", "case-tasks-open"),
    s("case-with-engineer-unassigned", "Case · With Engineer, no Engineer", CASE, "case", "case-read"),
    s("case-closed", "Case · Closed, Return to work", CASE, "case"),

    # Administration
    s("admin-hub", "Administration", ADMIN, "admin"),
    s("accounts", "Staff accounts", ADMIN, "admin"),
    s("accounts-settings", "Staff accounts · settings", ADMIN, "admin"),
    s("accounts-glass", "Staff accounts · Glass's login", ADMIN, "admin"),
    s("accounts-glass-empty", "Staff accounts · Glass's login, not set", ADMIN, "admin"),
    s("accounts-temp-password", "Staff accounts · temporary password", ADMIN, "admin"),
    s("contacts", "Contacts", ADMIN, "admin"),
    s("contacts-create", "Contacts · Add Repairer", ADMIN, "admin"),
    s("contacts-principal-contact", "Contacts · Principal", ADMIN, "admin"),
    s("contacts-principal-report-generation", "Contacts · Principal, Report generation", ADMIN, "admin"),
    s("contacts-principal-report-sending", "Contacts · Principal, Report sending", ADMIN, "admin"),
    s("contacts-principal-salvage-matrix", "Contacts · Principal, Salvage matrix", ADMIN, "admin"),
    s("contacts-principal-default-inspection-location", "Contacts · Principal, Inspection location", ADMIN, "admin"),
    s("contacts-principal-principal-api", "Contacts · Principal, Principal API", ADMIN, "admin"),
    s("contacts-other", "Contacts · Repairer", ADMIN, "admin"),
    s("configuration", "Workflow configuration", ADMIN, "admin"),
    s("mailboxes", "Mail settings", ADMIN, "admin"),
    s("mailboxes-settings", "Mail settings · mailbox", ADMIN, "admin"),
    s("mailboxes-new", "Mail settings · Add mailbox", ADMIN, "admin"),
    s("email-templates", "E-mail templates", ADMIN, "admin"),
    s("valuation-presets", "Valuation presets", ADMIN, "admin"),
    s("health", "Service health", ADMIN, "admin"),
    s("logs", "Logs", ADMIN, "admin"),
    s("logs-intake", "Logs · intake", ADMIN, "admin"),
    s("logs-intake-drawer", "Logs · intake, drawer open", ADMIN, "admin"),
    # A26: one capture, four tab states (the Proposal draws the tab, the capture holds every panel).
    s("reports", "Management reports · Engineers tab", ADMIN, "admin"),
    s("reports-principals", "Management reports · Principals tab", ADMIN, "admin", "reports"),
    s("reports-queues", "Management reports · Queues tab", ADMIN, "admin", "reports"),
    s("reports-case-list", "Management reports · Case list tab", ADMIN, "admin", "reports"),
    s("admin-release-notes", "Release notes (Administration)", ADMIN, "admin", "release-notes"),
    s("release-note-edit", "Release note · edit", ADMIN, "admin"),
    s("release-note-new", "Release note · new", ADMIN, "admin"),
    s("release-note-published", "Release note · published", ADMIN, "admin"),
    s("problem-reports", "Problem reports", ADMIN, "admin"),
    s("ai-jobs", "AI jobs", ADMIN, "admin"),
    s("automation", "Automation & AI", ADMIN, "admin"),

    # Shell and sign-in
    s("auth-signin", "Sign in", SHELL, "shell"),
    s("auth-signin-failed", "Sign in · refused", SHELL, "shell"),
    s("auth-signed-out", "Signed out", SHELL, "shell"),
    s("auth-password-forced", "Password change · required", SHELL, "shell"),
    s("auth-password-voluntary", "Password change", SHELL, "shell"),
    s("auth-access-denied", "Access denied", SHELL, "shell"),
    s("consent", "Connector consent", SHELL, "shell"),
    s("error", "Error", SHELL, "shell"),
    s("status-404", "Not found", SHELL, "shell"),
    s("release-notes", "Release notes", SHELL, "shell"),
    s("whats-new", "What's new", SHELL, "shell"),
]

# Live routes with no captured path of their own, mapped to the nearest state.
ROUTES: list[tuple[str, str]] = [
    ("/", "work-centre"),
    ("/Index", "work-centre"),
    ("/Inbox", "inbox"),
    ("/Upload", "upload"),
    ("/Cases", "cases-with-engineer"),
    ("/Cases/Create", "create-manual"),
    ("/Cases/QDOS26214", "case-correspondence"),
    ("/Cases/", "case-read"),
    ("/Search", "search"),
    ("/Administration", "admin-hub"),
    ("/Administration/Accounts", "accounts"),
    ("/Administration/Contacts", "contacts"),
    ("/Administration/Configuration", "configuration"),
    ("/Administration/Mailboxes", "mailboxes"),
    ("/Administration/EmailTemplates", "email-templates"),
    ("/Administration/ValuationPresets", "valuation-presets"),
    ("/Administration/Health", "health"),
    ("/Administration/Logs", "logs"),
    # The query decides the state (build-v41.py strips queries from the captured routes): A24 and A26 tab links.
    ("/Administration/Logs?tab=intake", "logs-intake"),
    ("/Administration/Logs?tab=intake&Receipt=00000000-0000-4000-8000-0000000c0de1", "logs-intake-drawer"),
    ("/Administration/Reports", "reports"),
    ("/Administration/Reports?tab=engineers", "reports"),
    ("/Administration/Reports?tab=principals", "reports-principals"),
    ("/Administration/Reports?tab=queues", "reports-queues"),
    ("/Administration/Reports?tab=case-list", "reports-case-list"),
    ("/Administration/ReleaseNotes", "admin-release-notes"),
    ("/Administration/ProblemReports", "problem-reports"),
    ("/Administration/AiJobs", "ai-jobs"),
    ("/Administration/Automation", "automation"),
    ("/ReleaseNotes", "release-notes"),
    ("/Account/SignIn", "auth-signin"),
    ("/Account/SignOut", "auth-signed-out"),
    ("/Account/PasswordChange", "auth-password-voluntary"),
    ("/VehicleImages/", "vehicle-images"),
    ("/Unidentified/", "unidentified"),
]
