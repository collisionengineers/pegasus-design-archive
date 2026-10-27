"""Work Centre Proposal patches: 5 simplified Work Centre designs (WC1..WC5, sign-off AC).

Replaces the overloaded Needs attention ledger (10 kind-filter chips, Office/Mine scope toggle,
priority group rows) with five switchable workspace designs (work-centre-a .. work-centre-e)
built around three focused operational streams plus Office Queue & Activity stats:

1. New Cases (default first view): newly arrived Cases across Principal API, E-mail, Manual
   and Automation intake channels (since /Inbox only shows emails).
2. System Actions: automated actions Pegasus has taken on Cases (auto-matched emails via thread,
   claim ref or VRM+date; early vehicle images paired to a Case; deterministic PAV-dispute query
   creation; cancellation matching & flagging).
3. AI Actions: AI deliverables and active jobs on a Case (Estimate done / Draft ready, Draft to a
   query, Estimate taken, active generation, and failed estimate job).
4. Stats: preserves the 5 Office queue totals (Not ready, Review, Held, Unidentified, Triages)
   and the Activity throughput figures (Today and This week across New cases, Sent to Engineer,
   Reports sent, E-mails received).
"""
from __future__ import annotations

from proposals_v42 import Ctx, patch

AC_SUMMARY = (
    "Work Centre simplification (/): choose Design A, B, C, D or E to replace Needs attention "
    "with New Cases (first view across API, E-mail, Manual & Automation), System Actions, "
    "AI Actions, and preserved Queue + Activity stats."
)

DESIGN_META: dict[str, tuple[str, str, str]] = {
    "a": (
        "WC1",
        "Design A · Streamlined ledger",
        "Design A (Streamlined ledger): side-by-side Office queues and Activity stat cards above "
        "a unified 3-tab ledger (New Cases, System Actions, AI Actions) with channel/kind sub-filters.",
    ),
    "b": (
        "WC2",
        "Design B · KPI ribbon & split inspector",
        "Design B (KPI ribbon & split inspector): ultra-compact single-row Queue + Activity ribbon "
        "above a 2-pane workbench with selectable stream rows on the left and a live Case / AI output "
        "inspector pane on the right.",
    ),
    "c": (
        "WC3",
        "Design C · Three-column live board",
        "Design C (Three-column live board): 9-cell unified metric bar above a 3-column simultaneous "
        "operations board showing New Cases, System Actions, and AI Actions side by side (or single-stream focus).",
    ),
    "d": (
        "WC4",
        "Design D · Telemetry sidebar & priority stream",
        "Design D (Telemetry sidebar & priority stream): 280px left telemetry rail for Office queues "
        "and Today/Week Activity beside a full-height time-grouped stream starting at the top of the viewport.",
    ),
    "e": (
        "WC5",
        "Design E · Command deck & action cards",
        "Design E (Command deck & action cards): dark charcoal .record-head command deck with Queue "
        "and Activity tiles above 3 view selector cards and structured 4-zone Case action cards.",
    ),
}

QUEUE_STATS: list[dict[str, str]] = [
    {"key": "not_ready", "label": "Not ready", "count": "6", "href": "/Cases?tab=not_ready", "tone": "amber"},
    {"key": "review", "label": "Review", "count": "3", "href": "/Cases?tab=review", "tone": "navy"},
    {"key": "held", "label": "Held", "count": "2", "href": "/Cases?tab=held", "tone": "neutral"},
    {"key": "unidentified", "label": "Unidentified", "count": "1", "href": "/Cases?tab=unassigned&show=unidentified", "tone": "red"},
    {"key": "triage", "label": "Triages", "count": "1", "href": "/Cases?tab=triage", "tone": "blue"},
]

ACTIVITY_STATS: list[dict[str, str]] = [
    {"key": "new-cases", "label": "New cases", "short": "New cases", "today": "3", "week": "5"},
    {"key": "sent", "label": "Sent to Engineer", "short": "Sent to Eng", "today": "6", "week": "17"},
    {"key": "reports", "label": "Reports sent", "short": "Reports sent", "today": "3", "week": "11"},
    {"key": "emails", "label": "E-mails received", "short": "E-mails", "today": "18", "week": "64"},
]

NEW_CASES: list[dict] = [
    {
        "id": "nc-26221",
        "ref": "QDOS26221",
        "href": "/Cases/2f93f288-ffe3-4301-8ffa-ef7964432f9c",
        "vehicle": "FD70NJK · Ford Puma",
        "claimant": "T. Nowak",
        "principal": "QDOS",
        "work_type": "Inspection",
        "channel_key": "api",
        "channel_label": "Principal API",
        "channel_cls": "status--navy",
        "stage_label": "Unassigned",
        "stage_cls": "status--amber",
        "owner": "Unassigned",
        "received": "Today 18:29",
        "bucket": "today",
        "cta_label": "Assign Engineer",
        "cta_href": "/Cases/2f93f288-ffe3-4301-8ffa-ef7964432f9c",
        "can_take": True,
        "summary": "API instruction ingested with policy schedule & 12 paired vehicle photos (FD70NJK-01). Ready for Engineer assignment.",
        "facts": [("Principal", "QDOS"), ("Work type", "Inspection"), ("Channel", "Principal API (webhook)"), ("Evidence", "12 photos paired · Instruction PDF")],
    },
    {
        "id": "nc-26217",
        "ref": "QDOS26217",
        "href": "/Cases/8a63804e-c66d-4725-a5db-312d9870311e",
        "vehicle": "AB12CDE · Vauxhall Corsa",
        "claimant": "S. Whitfield",
        "principal": "QDOS",
        "work_type": "Inspection",
        "channel_key": "email",
        "channel_label": "E-mail",
        "channel_cls": "status--neutral",
        "stage_label": "Unassigned",
        "stage_cls": "status--amber",
        "owner": "Unassigned",
        "received": "Today 16:29",
        "bucket": "today",
        "cta_label": "Assign Engineer",
        "cta_href": "/Cases/8a63804e-c66d-4725-a5db-312d9870311e",
        "can_take": True,
        "summary": "Created from instruction e-mail 'Instruction — AB12CDE — S. Whitfield' with bodyshop estimate attached.",
        "facts": [("Principal", "QDOS"), ("Work type", "Inspection"), ("Channel", "E-mail intake"), ("Evidence", "Instruction form + Audatex PDF")],
    },
    {
        "id": "nc-26214",
        "ref": "QDOS26214",
        "href": "/Cases/85de4c48-ed02-445f-a2ce-d97a087c19dd",
        "vehicle": "MA59BDY · Ford Focus",
        "claimant": "R. Whitfield",
        "principal": "QDOS",
        "work_type": "Inspection & Audit",
        "channel_key": "email",
        "channel_label": "E-mail",
        "channel_cls": "status--neutral",
        "stage_label": "With Engineer · e.mawdsley",
        "stage_cls": "status--blue",
        "owner": "e.mawdsley",
        "received": "25 Oct 19:29",
        "bucket": "earlier",
        "cta_label": "Open Case",
        "cta_href": "/Cases/85de4c48-ed02-445f-a2ce-d97a087c19dd",
        "can_take": False,
        "summary": "Combined Inspection & Audit case assigned to e.mawdsley. Supplementary bodyshop figures auto-linked today.",
        "facts": [("Principal", "QDOS"), ("Work type", "Inspection & Audit"), ("Channel", "E-mail intake"), ("Engineer", "e.mawdsley")],
    },
    {
        "id": "nc-26102",
        "ref": "PCH26102",
        "href": "/Cases/8a63804e-c66d-4725-a5db-312d9870311e",
        "vehicle": "EF56GHJ · BMW 320d",
        "claimant": "P. Marsh",
        "principal": "PCH",
        "work_type": "Inspection",
        "channel_key": "manual",
        "channel_label": "Manual",
        "channel_cls": "status--neutral",
        "stage_label": "Not ready · Awaiting images",
        "stage_cls": "status--amber",
        "owner": "Unassigned",
        "received": "24 Oct 20:29",
        "bucket": "earlier",
        "cta_label": "Open Case",
        "cta_href": "/Cases/8a63804e-c66d-4725-a5db-312d9870311e",
        "can_take": False,
        "summary": "Manually created PCH instruction via /Cases/Create. Supplementary workshop photos arrived via e-mail today.",
        "facts": [("Principal", "PCH"), ("Work type", "Inspection"), ("Channel", "Manual (/Cases/Create)"), ("Readiness", "Not ready · Awaiting images")],
    },
    {
        "id": "nc-26208",
        "ref": "QDOS26208",
        "href": "/Cases/e794a46c-8393-492e-b996-06f4cb217df9",
        "vehicle": "KP68LHT · Audi A3",
        "claimant": "M. Brennan",
        "principal": "QDOS",
        "work_type": "Audit",
        "channel_key": "automation",
        "channel_label": "Automation",
        "channel_cls": "status--blue",
        "stage_label": "Review · e.mawdsley",
        "stage_cls": "status--navy",
        "owner": "e.mawdsley",
        "received": "23 Oct 20:29",
        "bucket": "earlier",
        "cta_label": "Open Case",
        "cta_href": "/Cases/e794a46c-8393-492e-b996-06f4cb217df9",
        "can_take": False,
        "summary": "Ingested via Automation pipeline. AI desktop audit estimate (14 lines · £1,842.50) is complete and ready for review.",
        "facts": [("Principal", "QDOS"), ("Work type", "Audit"), ("Channel", "Automation MCP"), ("AI status", "Estimate draft ready (£1,842.50)")],
    },
    {
        "id": "nc-26219",
        "ref": "t.QDOS26219",
        "href": "/Cases/2ca7c99a-ccc9-4ab5-99ba-6848bc88f965",
        "vehicle": "BK21XYZ · VW Golf",
        "claimant": "H. Vance",
        "principal": "QDOS",
        "work_type": "Triage",
        "channel_key": "email",
        "channel_label": "E-mail",
        "channel_cls": "status--neutral",
        "stage_label": "Triage · Unassigned",
        "stage_cls": "status--amber",
        "owner": "Unassigned",
        "received": "23 Oct 14:15",
        "bucket": "earlier",
        "cta_label": "Open Triage",
        "cta_href": "/Cases/2ca7c99a-ccc9-4ab5-99ba-6848bc88f965",
        "can_take": True,
        "summary": "Total-loss / repairability triage request created from QDOS triage e-mail with 8 damaged vehicle photographs.",
        "facts": [("Principal", "QDOS"), ("Work type", "Triage"), ("Channel", "E-mail intake"), ("Stage", "Triage · Unassigned")],
    },
]

SYSTEM_ACTIONS: list[dict] = [
    {
        "id": "sa-26214-match",
        "ref": "QDOS26214",
        "href": "/Cases/85de4c48-ed02-445f-a2ce-d97a087c19dd",
        "vehicle": "MA59BDY · Ford Focus",
        "kind_key": "auto-match",
        "action_label": "Auto-matched e-mail to Case",
        "action_cls": "status--green",
        "detail": '“RE: QDOS26214 — Revised bodyshop figures” linked automatically to Case correspondence',
        "signal": "Thread & Claim ref",
        "when": "Today 19:12",
        "bucket": "today",
        "cta_label": "Open Case",
        "cta_href": "/Cases/85de4c48-ed02-445f-a2ce-d97a087c19dd",
        "can_take": False,
        "owner": "e.mawdsley",
        "summary": "SelectTarget v2 matched conversation thread and subject token QDOS26214 with 100% agreement across signals.",
        "facts": [("Rule", "AutomaticMailCaseAssociation v2"), ("Signals", "Conversation thread + Claim ref"), ("Mailbox", "claims@collisionengineers.co.uk"), ("Result", "Filed under Correspondence")],
    },
    {
        "id": "sa-26221-images",
        "ref": "QDOS26221",
        "href": "/Cases/2f93f288-ffe3-4301-8ffa-ef7964432f9c",
        "vehicle": "FD70NJK · Ford Puma",
        "kind_key": "images",
        "action_label": "Vehicle images paired",
        "action_cls": "status--blue",
        "detail": "Early image intake FD70NJK-01 (12 photos) automatically merged into Case upon arrival",
        "signal": "Exact VRM match",
        "when": "Today 18:30",
        "bucket": "today",
        "cta_label": "Open Images",
        "cta_href": "/Cases/2f93f288-ffe3-4301-8ffa-ef7964432f9c",
        "can_take": False,
        "owner": "Unassigned",
        "summary": "12 pre-arrival photographs held under Unidentified batch FD70NJK-01 were paired automatically when QDOS26221 arrived.",
        "facts": [("Rule", "Early image VRM pairing"), ("Batch", "FD70NJK-01 (12 JPEGs)"), ("Signal", "Exact VRM (FD70NJK)"), ("Result", "Unidentified item closed & merged")],
    },
    {
        "id": "sa-26190-query",
        "ref": "QDOS26190",
        "href": "/Cases/2dc71cf4-debc-403d-be99-241d73c16bd2",
        "vehicle": "PO16DDF · Mercedes A180",
        "kind_key": "rules",
        "action_label": "Query opened automatically",
        "action_cls": "status--purple",
        "detail": '“Storage charges dispute — PO16DDF” opened an Unassigned query on Report sent Case',
        "signal": "PAV & storage dispute rule",
        "when": "Today 17:45",
        "bucket": "today",
        "cta_label": "Open query",
        "cta_href": "/Cases/2dc71cf4-debc-403d-be99-241d73c16bd2?section=queries",
        "can_take": True,
        "owner": "Unassigned",
        "summary": "Deterministic query criterion matched the QDOS dispute phrase on a Report sent Case and opened an Unassigned CaseQuery.",
        "facts": [("Rule", "Deterministic query criterion"), ("Stage overlay", "Purple Query chip active"), ("Assignee", "Unassigned (ready to Take)"), ("AI follow-up", "Draft reply generated at 17:46")],
    },
    {
        "id": "sa-26102-vrm",
        "ref": "PCH26102",
        "href": "/Cases/8a63804e-c66d-4725-a5db-312d9870311e",
        "vehicle": "EF56GHJ · BMW 320d",
        "kind_key": "auto-match",
        "action_label": "Auto-matched e-mail to Case",
        "action_cls": "status--green",
        "detail": '“Supplementary workshop photos EF56GHJ” narrowed across 2 VRM candidates by accident date',
        "signal": "VRM + Accident date (14 Oct)",
        "when": "Today 15:20",
        "bucket": "today",
        "cta_label": "Open Case",
        "cta_href": "/Cases/8a63804e-c66d-4725-a5db-312d9870311e",
        "can_take": False,
        "owner": "Unassigned",
        "summary": "Two Cases shared VRM EF56GHJ; candidate with non-matching accident date was dropped, leaving PCH26102 (14 Oct).",
        "facts": [("Rule", "VRM + Accident date intersection"), ("VRM", "EF56GHJ (2 candidates → 1)"), ("Accident date", "14 October 2026"), ("Result", "Linked + 6 photos extracted")],
    },
    {
        "id": "sa-26220-cancel",
        "ref": "QDOS26220",
        "href": "/Cases/bee37ce3-c710-4a5b-8e2c-67e8ed6ad8cb",
        "vehicle": "LK21ABC · Vauxhall Corsa",
        "kind_key": "rules",
        "action_label": "Cancellation matched & flagged",
        "action_cls": "status--amber",
        "detail": '“Instruction cancellation — LK21ABC” linked and Cancellation received notice raised on Case',
        "signal": "Claim ref + Cancellation rule",
        "when": "Yesterday 16:05",
        "bucket": "earlier",
        "cta_label": "Open Case",
        "cta_href": "/Cases/bee37ce3-c710-4a5b-8e2c-67e8ed6ad8cb",
        "can_take": False,
        "owner": "e.mawdsley",
        "summary": "Cancellation e-mail matched QDOS26220 in Report preparation, set the Case aside notice, and enabled Place on Hold / Close case.",
        "facts": [("Rule", "Cancellation intake rule"), ("Case state", "Report preparation"), ("Aside notice", "Cancellation received"), ("Quick actions", "Place on Hold · Close case")],
    },
]

AI_ACTIONS: list[dict] = [
    {
        "id": "ai-26208-est",
        "ref": "QDOS26208",
        "href": "/Cases/e794a46c-8393-492e-b996-06f4cb217df9",
        "vehicle": "KP68LHT · Audi A3",
        "kind_key": "estimate",
        "action_label": "Estimate done",
        "state_label": "Draft ready",
        "state_cls": "status--green",
        "detail": "Front bumper and offside wing — 14 lines · £1,842.50 drafted from bodyshop estimate & 10 photos",
        "actor_when": "e.mawdsley · Today 18:10",
        "when": "Today 18:10",
        "bucket": "today",
        "cta_label": "Review estimate",
        "cta_href": "/Cases/e794a46c-8393-492e-b996-06f4cb217df9?section=estimate",
        "switch_state": "",
        "summary": "AI desktop audit extracted 14 repair/paint lines (£1,842.50 net vs £2,190.00 claimed, saving £347.50 on strip/refit overlap).",
        "facts": [("Deliverable", "AI Estimate (14 lines)"), ("Assessed total", "£1,842.50 (claimed £2,190.00)"), ("Variance", "-£347.50 (overlap removed)"), ("Status", "Draft ready for Engineer sign-off")],
    },
    {
        "id": "ai-26190-qdraft",
        "ref": "QDOS26190",
        "href": "/Cases/2dc71cf4-debc-403d-be99-241d73c16bd2",
        "vehicle": "PO16DDF · Mercedes A180",
        "kind_key": "query-draft",
        "action_label": "Draft to a query",
        "state_label": "Draft ready",
        "state_cls": "status--purple",
        "detail": 'Reply drafted for “Storage charges dispute” — cites inspection timeline & 5-day protocol cap',
        "actor_when": "Auto-drafted · Today 17:46",
        "when": "Today 17:46",
        "bucket": "today",
        "cta_label": "Open draft reply",
        "cta_href": "/Cases/2dc71cf4-debc-403d-be99-241d73c16bd2?section=queries",
        "switch_state": "message-m4-ai-reply",
        "summary": "AI drafted a structured reply citing the 19 Oct inspection date, 21 Oct report dispatch, and the QDOS 5-day storage cap.",
        "facts": [("Deliverable", "Query reply draft"), ("Target query", "Storage charges dispute"), ("Citations", "Inspection log + Report sent timestamp"), ("Composer", "Ready in #mailMessageDialog")],
    },
    {
        "id": "ai-26214-taken",
        "ref": "QDOS26214",
        "href": "/Cases/85de4c48-ed02-445f-a2ce-d97a087c19dd",
        "vehicle": "MA59BDY · Ford Focus",
        "kind_key": "estimate",
        "action_label": "Estimate done · Taken",
        "state_label": "Taken",
        "state_cls": "status--navy",
        "detail": "Rear bumper replacement — 9 lines · £1,120.00 · Taken by e.mawdsley (lease until 19:59)",
        "actor_when": "e.mawdsley · Today 13:29",
        "when": "Today 13:29",
        "bucket": "today",
        "cta_label": "Open Estimate",
        "cta_href": "/Cases/85de4c48-ed02-445f-a2ce-d97a087c19dd?section=estimate",
        "switch_state": "",
        "summary": "9-line rear bumper & parking sensor estimate drafted by AI and currently checked out by e.mawdsley.",
        "facts": [("Deliverable", "AI Estimate (9 lines)"), ("Assessed total", "£1,120.00"), ("Checked out by", "e.mawdsley (until 19:59)"), ("Status", "Taken · In Engineer review")],
    },
    {
        "id": "ai-26214-gen",
        "ref": "QDOS26214",
        "href": "/Cases/85de4c48-ed02-445f-a2ce-d97a087c19dd",
        "vehicle": "MA59BDY · Ford Focus",
        "kind_key": "query-draft",
        "action_label": "Draft to a query",
        "state_label": "Generating",
        "state_cls": "status--blue",
        "detail": "Drafting reply to PAV valuation query — comparing Glass’s mileage adjustment against 3 adverts",
        "actor_when": "e.mawdsley · Today 19:25",
        "when": "Today 19:25",
        "bucket": "today",
        "cta_label": "Open Queries",
        "cta_href": "/Cases/85de4c48-ed02-445f-a2ce-d97a087c19dd?section=queries",
        "switch_state": "case-queries",
        "summary": "Active AI job synthesising a PAV valuation rebuttal using the 3 comparable Ford Focus adverts attached to QDOS26214.",
        "facts": [("Deliverable", "Query reply draft (in progress)"), ("Target query", "PAV valuation dispute (m4)"), ("Evidence used", "Glass's guide + 3 market comparables"), ("Status", "Generating (started 19:25)")],
    },
    {
        "id": "ai-26203-fail",
        "ref": "QDOS26203",
        "href": "/Cases/b3d58471-7bc2-404b-8b15-81740a82d0f2",
        "vehicle": "QDOS · Instruction form",
        "kind_key": "failed",
        "action_label": "Estimate failed",
        "state_label": "Failed",
        "state_cls": "status--red",
        "detail": "Offside door and sill — could not extract estimate lines from low-contrast PDF scan",
        "actor_when": "e.mawdsley · Today 13:29",
        "when": "Today 13:29",
        "bucket": "earlier",
        "cta_label": "Open Case",
        "cta_href": "/Cases/b3d58471-7bc2-404b-8b15-81740a82d0f2",
        "switch_state": "",
        "summary": "OCR confidence fell below threshold on page 2 of the faxed bodyshop scan; requires manual estimate entry or clearer PDF.",
        "facts": [("Job type", "AI Estimate extraction"), ("Failure reason", "Low-contrast PDF scan (page 2)"), ("Requested by", "e.mawdsley"), ("Next step", "Upload clearer PDF or enter manually")],
    },
]


def _wc_design_switcher_bar(design: str) -> str:
    pills = []
    labels = [
        ("a", "A · Streamlined ledger"),
        ("b", "B · KPI ribbon & inspector"),
        ("c", "C · Three-column live board"),
        ("d", "D · Telemetry sidebar"),
        ("e", "E · Command deck & cards"),
    ]
    for d_key, d_label in labels:
        target = f"work-centre-{d_key}"
        pressed = "true" if d_key == design else "false"
        pills.append(
            f'<button type="button" class="up-design-pill" '
            f'data-wc-switch-state="{target}" aria-pressed="{pressed}">{d_label}</button>'
        )
    return (
        '<nav class="up-design-bar wc-design-bar" aria-label="Work Centre design options" data-wc-design-bar data-v42-demo>'
        '<div class="up-design-group">'
        '<span class="up-design-label">v42 Work Centre layout</span>'
        f'<div class="up-design-pills" role="group" aria-label="Choose Work Centre design">{"".join(pills)}</div>'
        "</div>"
        '<div class="up-design-right">'
        '<div class="up-design-group">'
        '<span class="up-design-label">Active view</span>'
        '<div class="up-design-pills" role="group" aria-label="Switch Work Centre view">'
        '<button type="button" class="up-design-pill" data-wc-view-switch="new-cases" aria-pressed="true">New Cases (6)</button>'
        '<button type="button" class="up-design-pill" data-wc-view-switch="system-actions" aria-pressed="false">System Actions (5)</button>'
        '<button type="button" class="up-design-pill" data-wc-view-switch="ai-actions" aria-pressed="false">AI Actions (5)</button>'
        "</div>"
        "</div>"
        "</div>"
        "</nav>"
    )


def _refresh_cluster() -> str:
    return (
        '<div class="wc-refresh">'
        '<span class="meta wc-refresh-outcome" data-wc-refresh-outcome-label>Updated 19:29</span>'
        '<div class="refresh-button" data-refresh-region role="status" aria-live="polite">'
        '<form method="get" data-refresh-form>'
        '<input type="hidden" name="refresh" value="true" />'
        '<button type="submit" class="btn btn--small" title="Refresh">'
        '<svg class="icon icon--spin" aria-hidden="true"><use href="#icon-refresh-cw"></use></svg>'
        "<span data-refresh-label>Refresh</span>"
        "</button>"
        "</form>"
        "</div>"
        "</div>"
    )


def _take_form(item_id: str) -> str:
    return (
        f'<form action="/?handler=TakeItem" data-wc-take="{item_id}" method="post">'
        f'<input type="hidden" name="itemId" value="{item_id}" />'
        '<button type="submit" class="btn btn--primary btn--small" data-busy-label="Taking…">Take</button>'
        "</form>"
    )


def _dismiss_form(item_id: str, ref: str) -> str:
    return (
        f'<form action="/?handler=DismissItem" data-wc-dismiss="{item_id}" method="post">'
        f'<input type="hidden" name="itemId" value="{item_id}" />'
        f'<button type="submit" class="icon-button wc-dismiss" title="Dismiss {ref}" aria-label="Dismiss {ref}">'
        '<svg class="icon" aria-hidden="true"><use href="#icon-x"></use></svg>'
        "</button>"
        "</form>"
    )


def _cta_button(label: str, href: str, switch_state: str = "", primary: bool = False) -> str:
    cls = "btn btn--primary btn--small" if primary else "btn btn--small"
    state_attr = f' data-wc-switch-state="{switch_state}"' if switch_state else ""
    return (
        f'<a class="{cls}" href="{href}"{state_attr}>'
        '<svg class="icon" aria-hidden="true"><use href="#icon-arrow-right"></use></svg>'
        f"<span>{label}</span></a>"
    )


def _view_tabs_nav() -> str:
    return (
        '<div class="tabs wc-v42-tabs" role="tablist" aria-label="Work Centre views">'
        '<button type="button" role="tab" class="tab" id="wc-tab-new-cases" '
        'data-wc-view-tab="new-cases" aria-selected="true" aria-controls="wc-panel-new-cases">'
        '<span>New Cases</span> <span class="tab-count" data-wc-tab-count="new-cases">6</span>'
        "</button>"
        '<button type="button" role="tab" class="tab" id="wc-tab-system-actions" '
        'data-wc-view-tab="system-actions" aria-selected="false" aria-controls="wc-panel-system-actions">'
        '<span>System Actions</span> <span class="tab-count" data-wc-tab-count="system-actions">5</span>'
        "</button>"
        '<button type="button" role="tab" class="tab" id="wc-tab-ai-actions" '
        'data-wc-view-tab="ai-actions" aria-selected="false" aria-controls="wc-panel-ai-actions">'
        '<span>AI Actions</span> <span class="tab-count" data-wc-tab-count="ai-actions">5</span>'
        "</button>"
        "</div>"
    )


def _search_box(placeholder: str = "Filter by Case, VRM, claimant or action…") -> str:
    return (
        '<div class="wc-v42-search">'
        '<svg class="icon" aria-hidden="true"><use href="#icon-search"></use></svg>'
        f'<input type="search" data-wc-live-search placeholder="{placeholder}" '
        'aria-label="Filter Work Centre items" autocomplete="off" />'
        "</div>"
    )


def _subfilters_new_cases() -> str:
    return (
        '<div class="wc-v42-subbar" role="toolbar" aria-label="New Cases channel filters">'
        '<div class="wc-v42-chips" role="group" aria-label="Arrival channel">'
        '<button type="button" class="chip" data-wc-subfilter="all" data-wc-target-panel="new-cases" aria-pressed="true">'
        'All channels <span class="n">6</span></button>'
        '<button type="button" class="chip" data-wc-subfilter="api" data-wc-target-panel="new-cases" aria-pressed="false">'
        'Principal API <span class="n">1</span></button>'
        '<button type="button" class="chip" data-wc-subfilter="email" data-wc-target-panel="new-cases" aria-pressed="false">'
        'E-mail <span class="n">3</span></button>'
        '<button type="button" class="chip" data-wc-subfilter="manual" data-wc-target-panel="new-cases" aria-pressed="false">'
        'Manual <span class="n">1</span></button>'
        '<button type="button" class="chip" data-wc-subfilter="automation" data-wc-target-panel="new-cases" aria-pressed="false">'
        'Automation <span class="n">1</span></button>'
        "</div>"
        '<span class="meta" data-wc-visible-count="new-cases">6 cases across all intake channels</span>'
        "</div>"
    )


def _subfilters_system_actions() -> str:
    return (
        '<div class="wc-v42-subbar" role="toolbar" aria-label="System Actions kind filters">'
        '<div class="wc-v42-chips" role="group" aria-label="System action type">'
        '<button type="button" class="chip" data-wc-subfilter="all" data-wc-target-panel="system-actions" aria-pressed="true">'
        'All system actions <span class="n">5</span></button>'
        '<button type="button" class="chip" data-wc-subfilter="auto-match" data-wc-target-panel="system-actions" aria-pressed="false">'
        'Auto-matched e-mail <span class="n">2</span></button>'
        '<button type="button" class="chip" data-wc-subfilter="images" data-wc-target-panel="system-actions" aria-pressed="false">'
        'Vehicle images paired <span class="n">1</span></button>'
        '<button type="button" class="chip" data-wc-subfilter="rules" data-wc-target-panel="system-actions" aria-pressed="false">'
        'Queries &amp; rules <span class="n">2</span></button>'
        "</div>"
        '<span class="meta" data-wc-visible-count="system-actions">5 automated actions</span>'
        "</div>"
    )


def _subfilters_ai_actions() -> str:
    return (
        '<div class="wc-v42-subbar" role="toolbar" aria-label="AI Actions kind filters">'
        '<div class="wc-v42-chips" role="group" aria-label="AI action type">'
        '<button type="button" class="chip" data-wc-subfilter="all" data-wc-target-panel="ai-actions" aria-pressed="true">'
        'All AI actions <span class="n">5</span></button>'
        '<button type="button" class="chip" data-wc-subfilter="estimate" data-wc-target-panel="ai-actions" aria-pressed="false">'
        'Estimate done <span class="n">2</span></button>'
        '<button type="button" class="chip" data-wc-subfilter="query-draft" data-wc-target-panel="ai-actions" aria-pressed="false">'
        'Draft to a query <span class="n">2</span></button>'
        '<button type="button" class="chip" data-wc-subfilter="failed" data-wc-target-panel="ai-actions" aria-pressed="false">'
        'Failed <span class="n">1</span></button>'
        "</div>"
        '<span class="meta" data-wc-visible-count="ai-actions">5 AI deliverables &amp; jobs</span>'
        "</div>"
    )


def _ledger_table_new_cases(selectable: bool = False, show_dividers: bool = True) -> str:
    rows: list[str] = []
    inserted_divider = False
    for idx, item in enumerate(NEW_CASES):
        if show_dividers and item["bucket"] == "earlier" and not inserted_divider:
            inserted_divider = True
            rows.append(
                '<tr class="wc-group-row" data-wc-group-divider>'
                '<td colspan="6">Earlier · Since you last looked</td>'
                "</tr>"
            )
        sel_attr = ""
        if selectable:
            is_sel = "true" if idx == 0 else "false"
            sel_attr = f' data-wc-inspect-row="{item["id"]}" aria-selected="{is_sel}" tabindex="0"'
        take_html = _take_form(item["id"]) if item["can_take"] else ""
        rows.append(
            f'<tr data-wc-item="{item["id"]}" data-wc-panel-item="new-cases" '
            f'data-wc-filter-cat="{item["channel_key"]}" data-wc-channel="{item["channel_key"]}"{sel_attr}>'
            '<td class="wc-cell-case">'
            f'<a class="mono wc-case-link" href="{item["href"]}">{item["ref"]}</a>'
            f'<small class="wc-cell-sub">{item["principal"]} · {item["work_type"]}</small>'
            "</td>"
            '<td class="wc-cell-vehicle">'
            f'<strong>{item["vehicle"]}</strong>'
            f'<small class="wc-cell-sub">Claimant: {item["claimant"]}</small>'
            "</td>"
            '<td class="wc-cell-channel">'
            f'<span class="status {item["channel_cls"]}">{item["channel_label"]}</span>'
            "</td>"
            '<td class="wc-cell-stage" data-wc-owner-cell>'
            f'<span class="status {item["stage_cls"]}" data-wc-stage-pill>{item["stage_label"]}</span>'
            "</td>"
            f'<td class="wc-cell-when tabular">{item["received"]}</td>'
            '<td class="wc-cell-actions">'
            '<div class="wc-row-actions">'
            f'{_cta_button(item["cta_label"], item["cta_href"])}'
            f"{take_html}"
            f'{_dismiss_form(item["id"], item["ref"])}'
            "</div>"
            "</td>"
            "</tr>"
        )
    return (
        '<div class="table-wrap">'
        '<table class="table wc-ledger-table" aria-label="New Cases">'
        "<thead><tr>"
        '<th scope="col">Case</th>'
        '<th scope="col">Vehicle &amp; claimant</th>'
        '<th scope="col">Arrival channel</th>'
        '<th scope="col">Stage / owner</th>'
        '<th scope="col">Received</th>'
        '<th scope="col"><span class="sr-only">Actions</span></th>'
        "</tr></thead>"
        f'<tbody>{"".join(rows)}</tbody>'
        "</table>"
        "</div>"
    )


def _ledger_table_system_actions(selectable: bool = False) -> str:
    rows: list[str] = []
    for idx, item in enumerate(SYSTEM_ACTIONS):
        sel_attr = ""
        if selectable:
            is_sel = "true" if idx == 0 else "false"
            sel_attr = f' data-wc-inspect-row="{item["id"]}" aria-selected="{is_sel}" tabindex="0"'
        take_html = _take_form(item["id"]) if item["can_take"] else ""
        rows.append(
            f'<tr data-wc-item="{item["id"]}" data-wc-panel-item="system-actions" '
            f'data-wc-filter-cat="{item["kind_key"]}" data-wc-sys-kind="{item["kind_key"]}"{sel_attr}>'
            '<td class="wc-cell-sys-kind">'
            f'<span class="status {item["action_cls"]}">{item["action_label"]}</span>'
            "</td>"
            '<td class="wc-cell-case">'
            f'<a class="mono wc-case-link" href="{item["href"]}">{item["ref"]}</a>'
            f'<small class="wc-cell-sub">{item["vehicle"]}</small>'
            "</td>"
            '<td class="wc-cell-detail">'
            f'<span class="wc-detail-main">{item["detail"]}</span>'
            f'<small class="wc-cell-sub">Signal: <strong>{item["signal"]}</strong></small>'
            "</td>"
            f'<td class="wc-cell-when tabular">{item["when"]}</td>'
            '<td class="wc-cell-actions">'
            '<div class="wc-row-actions">'
            f'{_cta_button(item["cta_label"], item["cta_href"])}'
            f"{take_html}"
            f'{_dismiss_form(item["id"], item["ref"])}'
            "</div>"
            "</td>"
            "</tr>"
        )
    return (
        '<div class="table-wrap">'
        '<table class="table wc-ledger-table" aria-label="System Actions">'
        "<thead><tr>"
        '<th scope="col">System action</th>'
        '<th scope="col">Case</th>'
        '<th scope="col">Matched detail &amp; rule signal</th>'
        '<th scope="col">When</th>'
        '<th scope="col"><span class="sr-only">Actions</span></th>'
        "</tr></thead>"
        f'<tbody>{"".join(rows)}</tbody>'
        "</table>"
        "</div>"
    )


def _ledger_table_ai_actions(selectable: bool = False) -> str:
    rows: list[str] = []
    for idx, item in enumerate(AI_ACTIONS):
        sel_attr = ""
        if selectable:
            is_sel = "true" if idx == 0 else "false"
            sel_attr = f' data-wc-inspect-row="{item["id"]}" aria-selected="{is_sel}" tabindex="0"'
        rows.append(
            f'<tr data-wc-item="{item["id"]}" data-wc-panel-item="ai-actions" '
            f'data-wc-filter-cat="{item["kind_key"]}" data-wc-ai-kind="{item["kind_key"]}"{sel_attr}>'
            '<td class="wc-cell-ai-kind">'
            f'<strong>{item["action_label"]}</strong>'
            "</td>"
            '<td class="wc-cell-case">'
            f'<a class="mono wc-case-link" href="{item["href"]}">{item["ref"]}</a>'
            f'<small class="wc-cell-sub">{item["vehicle"]}</small>'
            "</td>"
            '<td class="wc-cell-state">'
            f'<span class="status {item["state_cls"]}">{item["state_label"]}</span>'
            "</td>"
            '<td class="wc-cell-detail">'
            f'<span class="wc-detail-main">{item["detail"]}</span>'
            f'<small class="wc-cell-sub">{item["actor_when"]}</small>'
            "</td>"
            f'<td class="wc-cell-when tabular">{item["when"]}</td>'
            '<td class="wc-cell-actions">'
            '<div class="wc-row-actions">'
            f'{_cta_button(item["cta_label"], item["cta_href"], item["switch_state"])}'
            f'{_dismiss_form(item["id"], item["ref"])}'
            "</div>"
            "</td>"
            "</tr>"
        )
    return (
        '<div class="table-wrap">'
        '<table class="table wc-ledger-table" aria-label="AI Actions">'
        "<thead><tr>"
        '<th scope="col">AI action</th>'
        '<th scope="col">Case</th>'
        '<th scope="col">State</th>'
        '<th scope="col">Deliverable &amp; summary</th>'
        '<th scope="col">When</th>'
        '<th scope="col"><span class="sr-only">Actions</span></th>'
        "</tr></thead>"
        f'<tbody>{"".join(rows)}</tbody>'
        "</table>"
        "</div>"
    )


def _three_view_panels(selectable: bool = False) -> str:
    return (
        '<section id="wc-panel-new-cases" role="tabpanel" aria-labelledby="wc-tab-new-cases" '
        'data-wc-view-panel="new-cases">'
        f"{_subfilters_new_cases()}"
        f"{_ledger_table_new_cases(selectable=selectable)}"
        "</section>"
        '<section id="wc-panel-system-actions" role="tabpanel" aria-labelledby="wc-tab-system-actions" '
        'data-wc-view-panel="system-actions" hidden>'
        f"{_subfilters_system_actions()}"
        f"{_ledger_table_system_actions(selectable=selectable)}"
        "</section>"
        '<section id="wc-panel-ai-actions" role="tabpanel" aria-labelledby="wc-tab-ai-actions" '
        'data-wc-view-panel="ai-actions" hidden>'
        f"{_subfilters_ai_actions()}"
        f"{_ledger_table_ai_actions(selectable=selectable)}"
        "</section>"
    )


# ==============================================================================
# Design A: Streamlined Ledger (WC1)
# ==============================================================================
def _build_design_a() -> str:
    queue_cells = "".join(
        f'<a class="wc-a-queue-cell wc-tone--{q["tone"]}" data-value="{q["key"]}" href="{q["href"]}">'
        f'<span class="wc-a-queue-label">{q["label"]}</span>'
        f'<strong class="wc-a-queue-val tabular">{q["count"]}</strong>'
        "</a>"
        for q in QUEUE_STATS
    )
    act_cells = "".join(
        f'<div class="wc-a-act-cell" data-figure="{a["key"]}">'
        f'<span class="wc-a-act-label">{a["label"]}</span>'
        '<div class="wc-a-act-nums">'
        f'<strong class="wc-a-act-today tabular" data-figure="{a["key"]}-today">{a["today"]}</strong>'
        '<span class="wc-a-act-tag">today</span>'
        "</div>"
        f'<small class="wc-a-act-week tabular" data-figure="{a["key"]}-week">This week: {a["week"]}</small>'
        "</div>"
        for a in ACTIVITY_STATS
    )
    return (
        '<div class="work-centre wc-v42-root wc-v42--a" data-work-centre data-wc-design="a">'
        '<header class="page-header">'
        '<div class="page-title">'
        '<p class="eyebrow">Operations overview</p>'
        "<h1>Work Centre</h1>"
        "</div>"
        f'<div class="page-actions">{_refresh_cluster()}</div>'
        "</header>"
        '<div class="wc-a-stats-grid" aria-label="Operational statistics">'
        '<section class="panel wc-a-stat-card" aria-label="Office queue totals">'
        '<div class="wc-a-stat-head">'
        "<h2>Office queues</h2>"
        '<a class="wc-stat-link" href="/Cases">All Cases →</a>'
        "</div>"
        f'<nav class="wc-a-queues" aria-label="Office queue totals">{queue_cells}</nav>'
        "</section>"
        '<section class="panel wc-a-stat-card" aria-label="Activity throughput" data-wc-activity>'
        '<div class="wc-a-stat-head">'
        "<h2>Activity</h2>"
        '<span class="meta">Today vs This week</span>'
        "</div>"
        f'<div class="wc-a-activity-grid">{act_cells}</div>'
        "</section>"
        "</div>"
        '<section class="panel wc-a-panel" aria-label="Work Centre streams">'
        '<div class="wc-a-panel-head">'
        f"{_view_tabs_nav()}"
        f"{_search_box()}"
        "</div>"
        f"{_three_view_panels(selectable=False)}"
        "</section>"
        "</div>"
    )


# ==============================================================================
# Design B: KPI Ribbon & Split Inspector (WC2)
# ==============================================================================
def _inspector_cards() -> str:
    cards: list[str] = []
    all_items: list[tuple[str, dict]] = (
        [("new-cases", x) for x in NEW_CASES]
        + [("system-actions", x) for x in SYSTEM_ACTIONS]
        + [("ai-actions", x) for x in AI_ACTIONS]
    )
    for idx, (stream, item) in enumerate(all_items):
        hidden_attr = "" if idx == 0 else " hidden"
        if stream == "new-cases":
            badge = f'<span class="status {item["channel_cls"]}">{item["channel_label"]}</span>'
            subtitle = f'{item["vehicle"]} · Claimant: {item["claimant"]}'
            box_title = "Arrival & intake summary"
            when_str = item["received"]
            extra_btn = _take_form(item["id"]) if item["can_take"] else ""
            sw = ""
        elif stream == "system-actions":
            badge = f'<span class="status {item["action_cls"]}">{item["action_label"]}</span>'
            subtitle = f'{item["vehicle"]} · Signal: {item["signal"]}'
            box_title = "Automated rule & match evidence"
            when_str = item["when"]
            extra_btn = _take_form(item["id"]) if item["can_take"] else ""
            sw = ""
        else:
            badge = f'<span class="status {item["state_cls"]}">{item["action_label"]} · {item["state_label"]}</span>'
            subtitle = f'{item["vehicle"]} · {item["actor_when"]}'
            box_title = "AI deliverable & output preview"
            when_str = item["when"]
            extra_btn = ""
            sw = item["switch_state"]

        facts_html = "".join(
            f'<div class="wc-b-fact"><dt>{k}</dt><dd>{v}</dd></div>'
            for k, v in item["facts"]
        )
        cards.append(
            f'<article class="wc-b-inspect-card" data-wc-inspector-card="{item["id"]}" '
            f'data-wc-inspector-stream="{stream}"{hidden_attr}>'
            '<header class="wc-b-inspect-head">'
            '<div class="wc-b-inspect-title">'
            '<span class="eyebrow">Selected item</span>'
            f'<h3><a class="mono" href="{item["href"]}">{item["ref"]}</a></h3>'
            f"<p>{subtitle}</p>"
            "</div>"
            f"{badge}"
            "</header>"
            f'<dl class="wc-b-facts">{facts_html}</dl>'
            '<div class="wc-b-preview-box">'
            f'<span class="wc-b-preview-label">{box_title}</span>'
            f'<p>{item["summary"]}</p>'
            f'<small class="meta">Recorded {when_str}</small>'
            "</div>"
            '<footer class="wc-b-inspect-foot">'
            f'{_cta_button(item["cta_label"], item["cta_href"], sw, primary=True)}'
            f"{extra_btn}"
            f'<a class="btn btn--small" href="{item["href"]}">Open Case</a>'
            "</footer>"
            "</article>"
        )
    return "".join(cards)


def _build_design_b() -> str:
    q_badges = "".join(
        f'<a class="wc-b-qpill" data-value="{q["key"]}" href="{q["href"]}">'
        f'<span>{q["label"]}</span><strong class="tabular">{q["count"]}</strong></a>'
        for q in QUEUE_STATS
    )
    a_badges = "".join(
        f'<div class="wc-b-apill" data-figure="{a["key"]}">'
        f'<span>{a["short"]}</span>'
        f'<strong class="tabular" data-figure="{a["key"]}-today">{a["today"]}</strong>'
        f'<small class="tabular" data-figure="{a["key"]}-week">/ {a["week"]} wk</small>'
        "</div>"
        for a in ACTIVITY_STATS
    )
    return (
        '<div class="work-centre wc-v42-root wc-v42--b" data-work-centre data-wc-design="b">'
        '<header class="page-header wc-b-header">'
        '<div class="page-title">'
        '<p class="eyebrow">Workbench &amp; live inspector</p>'
        "<h1>Work Centre</h1>"
        "</div>"
        f'<div class="page-actions">{_refresh_cluster()}</div>'
        "</header>"
        '<section class="panel wc-b-ribbon" aria-label="Queues and Activity KPI ribbon" data-wc-activity>'
        '<div class="wc-b-ribbon-group">'
        '<span class="wc-b-ribbon-label">Queues</span>'
        f'<nav class="wc-b-ribbon-items" aria-label="Office queue totals">{q_badges}</nav>'
        "</div>"
        '<div class="wc-b-ribbon-group wc-b-ribbon-group--act">'
        '<span class="wc-b-ribbon-label">Activity (Today / Week)</span>'
        f'<div class="wc-b-ribbon-items">{a_badges}</div>'
        "</div>"
        "</section>"
        '<div class="pane-layout wc-b-workbench">'
        '<div class="pane wc-b-list-pane">'
        '<div class="wc-a-panel-head">'
        f"{_view_tabs_nav()}"
        f"{_search_box('Search active view…')}"
        "</div>"
        f"{_three_view_panels(selectable=True)}"
        "</div>"
        '<aside class="pane wc-b-inspector" aria-label="Selected item inspector">'
        f"{_inspector_cards()}"
        "</aside>"
        "</div>"
        "</div>"
    )


# ==============================================================================
# Design C: Three-Column Live Operations Board (WC3)
# ==============================================================================
def _build_design_c() -> str:
    q_cells = "".join(
        f'<a class="wc-c-stat-cell" data-value="{q["key"]}" href="{q["href"]}">'
        f'<span class="wc-c-stat-label">{q["label"]}</span>'
        f'<strong class="wc-c-stat-val tabular">{q["count"]}</strong>'
        '<small class="wc-c-stat-sub">Queue</small>'
        "</a>"
        for q in QUEUE_STATS
    )
    a_cells = "".join(
        f'<div class="wc-c-stat-cell wc-c-stat-cell--act" data-figure="{a["key"]}">'
        f'<span class="wc-c-stat-label">{a["short"]}</span>'
        f'<strong class="wc-c-stat-val tabular" data-figure="{a["key"]}-today">{a["today"]}</strong>'
        f'<small class="wc-c-stat-sub tabular" data-figure="{a["key"]}-week">{a["week"]} this wk</small>'
        "</div>"
        for a in ACTIVITY_STATS
    )

    nc_cards = "".join(
        f'<article class="wc-c-card" data-wc-item="{item["id"]}" data-wc-panel-item="new-cases" '
        f'data-wc-filter-cat="{item["channel_key"]}" data-wc-channel="{item["channel_key"]}">'
        '<div class="wc-c-card-top">'
        f'<a class="mono wc-case-link" href="{item["href"]}">{item["ref"]}</a>'
        f'<span class="status {item["channel_cls"]}">{item["channel_label"]}</span>'
        f'<span class="wc-c-time tabular">{item["received"]}</span>'
        "</div>"
        f'<div class="wc-c-card-Title"><strong>{item["vehicle"]}</strong> · {item["claimant"]}</div>'
        '<div class="wc-c-card-meta">'
        f'<span class="status {item["stage_cls"]}" data-wc-stage-pill>{item["stage_label"]}</span>'
        f'<small>{item["principal"]} · {item["work_type"]}</small>'
        "</div>"
        '<div class="wc-c-card-foot">'
        f'{_cta_button(item["cta_label"], item["cta_href"])}'
        f'{_take_form(item["id"]) if item["can_take"] else ""}'
        f'{_dismiss_form(item["id"], item["ref"])}'
        "</div>"
        "</article>"
        for item in NEW_CASES
    )

    sa_cards = "".join(
        f'<article class="wc-c-card" data-wc-item="{item["id"]}" data-wc-panel-item="system-actions" '
        f'data-wc-filter-cat="{item["kind_key"]}" data-wc-sys-kind="{item["kind_key"]}">'
        '<div class="wc-c-card-top">'
        f'<a class="mono wc-case-link" href="{item["href"]}">{item["ref"]}</a>'
        f'<span class="status {item["action_cls"]}">{item["action_label"]}</span>'
        f'<span class="wc-c-time tabular">{item["when"]}</span>'
        "</div>"
        f'<div class="wc-c-card-Title">{item["detail"]}</div>'
        f'<div class="wc-c-card-meta"><small>Vehicle: {item["vehicle"]} · Rule: <strong>{item["signal"]}</strong></small></div>'
        '<div class="wc-c-card-foot">'
        f'{_cta_button(item["cta_label"], item["cta_href"])}'
        f'{_take_form(item["id"]) if item["can_take"] else ""}'
        f'{_dismiss_form(item["id"], item["ref"])}'
        "</div>"
        "</article>"
        for item in SYSTEM_ACTIONS
    )

    ai_cards = "".join(
        f'<article class="wc-c-card" data-wc-item="{item["id"]}" data-wc-panel-item="ai-actions" '
        f'data-wc-filter-cat="{item["kind_key"]}" data-wc-ai-kind="{item["kind_key"]}">'
        '<div class="wc-c-card-top">'
        f'<a class="mono wc-case-link" href="{item["href"]}">{item["ref"]}</a>'
        f'<span class="status {item["state_cls"]}">{item["action_label"]} · {item["state_label"]}</span>'
        f'<span class="wc-c-time tabular">{item["when"]}</span>'
        "</div>"
        f'<div class="wc-c-card-Title">{item["detail"]}</div>'
        f'<div class="wc-c-card-meta"><small>{item["vehicle"]} · {item["actor_when"]}</small></div>'
        '<div class="wc-c-card-foot">'
        f'{_cta_button(item["cta_label"], item["cta_href"], item["switch_state"])}'
        f'{_dismiss_form(item["id"], item["ref"])}'
        "</div>"
        "</article>"
        for item in AI_ACTIONS
    )

    return (
        '<div class="work-centre wc-v42-root wc-v42--c" data-work-centre data-wc-design="c">'
        '<header class="page-header">'
        '<div class="page-title">'
        '<p class="eyebrow">Simultaneous three-stream board</p>'
        "<h1>Work Centre</h1>"
        "</div>"
        f'<div class="page-actions">{_refresh_cluster()}</div>'
        "</header>"
        '<section class="panel wc-c-stats" aria-label="Unified Queues and Activity metrics" data-wc-activity>'
        f"{q_cells}{a_cells}"
        "</section>"
        '<div class="panel wc-c-toolbar">'
        '<div class="wc-c-focus-bar">'
        f"{_view_tabs_nav()}"
        '<button type="button" class="chip" data-wc-board-all aria-pressed="true">Show all 3 columns</button>'
        "</div>"
        f"{_search_box('Filter across all 3 columns…')}"
        "</div>"
        '<div class="wc-c-board" data-wc-board-focus="all">'
        '<section class="panel wc-c-col wc-c-col--new" id="wc-panel-new-cases" '
        'data-wc-view-panel="new-cases" aria-label="New Cases stream">'
        '<header class="wc-c-col-head">'
        '<div><h2>New Cases</h2><small>API, E-mail, Manual &amp; Automation arrivals</small></div>'
        '<span class="tab-count" data-wc-tab-count="new-cases">6</span>'
        "</header>"
        f'<div class="wc-c-col-body">{nc_cards}</div>'
        "</section>"
        '<section class="panel wc-c-col wc-c-col--sys" id="wc-panel-system-actions" '
        'data-wc-view-panel="system-actions" aria-label="System Actions stream">'
        '<header class="wc-c-col-head">'
        '<div><h2>System Actions</h2><small>Auto-matched e-mails, paired images &amp; rules</small></div>'
        '<span class="tab-count" data-wc-tab-count="system-actions">5</span>'
        "</header>"
        f'<div class="wc-c-col-body">{sa_cards}</div>'
        "</section>"
        '<section class="panel wc-c-col wc-c-col--ai" id="wc-panel-ai-actions" '
        'data-wc-view-panel="ai-actions" aria-label="AI Actions stream">'
        '<header class="wc-c-col-head">'
        '<div><h2>AI Actions</h2><small>Completed estimates &amp; query reply drafts</small></div>'
        '<span class="tab-count" data-wc-tab-count="ai-actions">5</span>'
        "</header>"
        f'<div class="wc-c-col-body">{ai_cards}</div>'
        "</section>"
        "</div>"
        "</div>"
    )


# ==============================================================================
# Design D: Telemetry Sidebar & Priority Stream (WC4)
# ==============================================================================
def _build_design_d() -> str:
    q_list = "".join(
        f'<a class="wc-d-queue-row wc-tone--{q["tone"]}" data-value="{q["key"]}" href="{q["href"]}">'
        f'<span>{q["label"]}</span>'
        f'<strong class="tabular">{q["count"]}</strong>'
        "</a>"
        for q in QUEUE_STATS
    )
    a_rows = "".join(
        f'<tr data-figure="{a["key"]}">'
        f'<th scope="row">{a["label"]}</th>'
        f'<td class="tabular" data-figure="{a["key"]}-today"><strong>{a["today"]}</strong></td>'
        f'<td class="tabular quiet" data-figure="{a["key"]}-week">{a["week"]}</td>'
        "</tr>"
        for a in ACTIVITY_STATS
    )
    return (
        '<div class="work-centre wc-v42-root wc-v42--d" data-work-centre data-wc-design="d">'
        '<div class="wc-d-layout">'
        '<aside class="wc-d-sidebar" aria-label="Office queues and Activity telemetry">'
        '<div class="wc-d-brand">'
        '<p class="eyebrow">Operations</p>'
        "<h1>Work Centre</h1>"
        f"{_refresh_cluster()}"
        "</div>"
        '<section class="panel wc-d-card" aria-label="Office queue totals">'
        '<div class="wc-d-card-head"><h2>Office queues</h2><a href="/Cases">View all</a></div>'
        f'<nav class="wc-d-queue-list" aria-label="Office queue totals">{q_list}</nav>'
        "</section>"
        '<section class="panel wc-d-card" aria-label="Activity throughput" data-wc-activity>'
        '<div class="wc-d-card-head"><h2>Activity</h2><span class="meta">Throughput</span></div>'
        '<table class="wc-d-act-table">'
        '<thead><tr><th scope="col">Metric</th><th scope="col">Today</th><th scope="col">Week</th></tr></thead>'
        f"<tbody>{a_rows}</tbody>"
        "</table>"
        "</section>"
        "</aside>"
        '<div class="panel wc-d-main">'
        '<div class="wc-a-panel-head">'
        f"{_view_tabs_nav()}"
        f"{_search_box()}"
        "</div>"
        f"{_three_view_panels(selectable=False)}"
        "</div>"
        "</div>"
        "</div>"
    )


# ==============================================================================
# Design E: Command Deck & Case Action Cards (WC5)
# ==============================================================================
def _build_design_e() -> str:
    q_tiles = "".join(
        f'<a class="wc-e-qtile" data-value="{q["key"]}" href="{q["href"]}">'
        f'<span class="wc-e-qlabel">{q["label"]}</span>'
        f'<strong class="wc-e-qval tabular">{q["count"]}</strong>'
        "</a>"
        for q in QUEUE_STATS
    )
    a_tiles = "".join(
        f'<div class="wc-e-atile" data-figure="{a["key"]}">'
        f'<span class="wc-e-alabel">{a["label"]}</span>'
        '<div class="wc-e-avals">'
        f'<strong class="tabular" data-figure="{a["key"]}-today">{a["today"]} today</strong>'
        f'<small class="tabular" data-figure="{a["key"]}-week">{a["week"]} this week</small>'
        "</div>"
        "</div>"
        for a in ACTIVITY_STATS
    )

    nc_cards = "".join(
        f'<article class="wc-e-item wc-e-item--new" data-wc-item="{item["id"]}" data-wc-panel-item="new-cases" '
        f'data-wc-filter-cat="{item["channel_key"]}" data-wc-channel="{item["channel_key"]}">'
        '<div class="wc-e-zone-case">'
        f'<a class="mono wc-case-link" href="{item["href"]}">{item["ref"]}</a>'
        f'<strong>{item["vehicle"]}</strong>'
        f'<small>{item["principal"]} · Claimant: {item["claimant"]}</small>'
        "</div>"
        '<div class="wc-e-zone-badges">'
        f'<span class="status {item["channel_cls"]}">{item["channel_label"]}</span>'
        f'<span class="status {item["stage_cls"]}" data-wc-stage-pill>{item["stage_label"]}</span>'
        f'<small class="tabular">{item["work_type"]} · {item["received"]}</small>'
        "</div>"
        '<div class="wc-e-zone-detail">'
        f'<p>{item["summary"]}</p>'
        "</div>"
        '<div class="wc-e-zone-actions">'
        f'{_cta_button(item["cta_label"], item["cta_href"], primary=True)}'
        f'{_take_form(item["id"]) if item["can_take"] else ""}'
        f'{_dismiss_form(item["id"], item["ref"])}'
        "</div>"
        "</article>"
        for item in NEW_CASES
    )

    sa_cards = "".join(
        f'<article class="wc-e-item wc-e-item--sys" data-wc-item="{item["id"]}" data-wc-panel-item="system-actions" '
        f'data-wc-filter-cat="{item["kind_key"]}" data-wc-sys-kind="{item["kind_key"]}">'
        '<div class="wc-e-zone-case">'
        f'<a class="mono wc-case-link" href="{item["href"]}">{item["ref"]}</a>'
        f'<strong>{item["vehicle"]}</strong>'
        f'<small>Rule signal: {item["signal"]}</small>'
        "</div>"
        '<div class="wc-e-zone-badges">'
        f'<span class="status {item["action_cls"]}">{item["action_label"]}</span>'
        f'<small class="tabular">{item["when"]}</small>'
        "</div>"
        '<div class="wc-e-zone-detail">'
        f'<p>{item["detail"]}</p>'
        f'<small class="quiet">{item["summary"]}</small>'
        "</div>"
        '<div class="wc-e-zone-actions">'
        f'{_cta_button(item["cta_label"], item["cta_href"], primary=True)}'
        f'{_take_form(item["id"]) if item["can_take"] else ""}'
        f'{_dismiss_form(item["id"], item["ref"])}'
        "</div>"
        "</article>"
        for item in SYSTEM_ACTIONS
    )

    ai_cards = "".join(
        f'<article class="wc-e-item wc-e-item--ai" data-wc-item="{item["id"]}" data-wc-panel-item="ai-actions" '
        f'data-wc-filter-cat="{item["kind_key"]}" data-wc-ai-kind="{item["kind_key"]}">'
        '<div class="wc-e-zone-case">'
        f'<a class="mono wc-case-link" href="{item["href"]}">{item["ref"]}</a>'
        f'<strong>{item["vehicle"]}</strong>'
        f'<small>{item["actor_when"]}</small>'
        "</div>"
        '<div class="wc-e-zone-badges">'
        f'<span class="status {item["state_cls"]}">{item["action_label"]} · {item["state_label"]}</span>'
        f'<small class="tabular">{item["when"]}</small>'
        "</div>"
        '<div class="wc-e-zone-detail">'
        f'<p>{item["detail"]}</p>'
        f'<small class="quiet">{item["summary"]}</small>'
        "</div>"
        '<div class="wc-e-zone-actions">'
        f'{_cta_button(item["cta_label"], item["cta_href"], item["switch_state"], primary=True)}'
        f'{_dismiss_form(item["id"], item["ref"])}'
        "</div>"
        "</article>"
        for item in AI_ACTIONS
    )

    return (
        '<div class="work-centre wc-v42-root wc-v42--e" data-work-centre data-wc-design="e">'
        '<section class="record wc-e-deck" aria-label="Work Centre command deck" data-wc-activity>'
        '<div class="record-head wc-e-deck-head">'
        '<div class="wc-e-deck-top">'
        "<div>"
        '<p class="wc-e-eyebrow">Collision Engineers · Operations Command Deck</p>'
        "<h1>Work Centre</h1>"
        "</div>"
        f'<div class="wc-e-deck-refresh">{_refresh_cluster()}</div>'
        "</div>"
        '<div class="wc-e-deck-metrics">'
        '<div class="wc-e-deck-block">'
        '<span class="wc-e-block-label">Office queues</span>'
        f'<nav class="wc-e-qtiles" aria-label="Office queue totals">{q_tiles}</nav>'
        "</div>"
        '<div class="wc-e-deck-block">'
        '<span class="wc-e-block-label">Activity throughput</span>'
        f'<div class="wc-e-atiles">{a_tiles}</div>'
        "</div>"
        "</div>"
        "</div>"
        '<div class="record-accent"></div>'
        "</section>"
        '<div class="wc-e-nav-bar" role="tablist" aria-label="Work Centre views">'
        '<button type="button" role="tab" class="wc-e-nav-card" id="wc-tab-new-cases" '
        'data-wc-view-tab="new-cases" aria-selected="true" aria-controls="wc-panel-new-cases">'
        '<div class="wc-e-nav-top"><strong>New Cases</strong><span class="tab-count" data-wc-tab-count="new-cases">6</span></div>'
        "<small>Principal API, E-mail, Manual &amp; Automation arrivals</small>"
        "</button>"
        '<button type="button" role="tab" class="wc-e-nav-card" id="wc-tab-system-actions" '
        'data-wc-view-tab="system-actions" aria-selected="false" aria-controls="wc-panel-system-actions">'
        '<div class="wc-e-nav-top"><strong>System Actions</strong><span class="tab-count" data-wc-tab-count="system-actions">5</span></div>'
        "<small>Auto-matched e-mails, paired images &amp; rule triggers</small>"
        "</button>"
        '<button type="button" role="tab" class="wc-e-nav-card" id="wc-tab-ai-actions" '
        'data-wc-view-tab="ai-actions" aria-selected="false" aria-controls="wc-panel-ai-actions">'
        '<div class="wc-e-nav-top"><strong>AI Actions</strong><span class="tab-count" data-wc-tab-count="ai-actions">5</span></div>'
        "<small>Completed estimates &amp; drafted query replies</small>"
        "</button>"
        "</div>"
        '<section class="panel wc-e-stream-panel">'
        '<div class="wc-e-filter-row">'
        f"{_search_box('Filter action cards by Case, VRM, channel or deliverable…')}"
        "</div>"
        '<section id="wc-panel-new-cases" role="tabpanel" aria-labelledby="wc-tab-new-cases" data-wc-view-panel="new-cases">'
        f"{_subfilters_new_cases()}"
        f'<div class="wc-e-list">{nc_cards}</div>'
        "</section>"
        '<section id="wc-panel-system-actions" role="tabpanel" aria-labelledby="wc-tab-system-actions" data-wc-view-panel="system-actions" hidden>'
        f"{_subfilters_system_actions()}"
        f'<div class="wc-e-list">{sa_cards}</div>'
        "</section>"
        '<section id="wc-panel-ai-actions" role="tabpanel" aria-labelledby="wc-tab-ai-actions" data-wc-view-panel="ai-actions" hidden>'
        f"{_subfilters_ai_actions()}"
        f'<div class="wc-e-list">{ai_cards}</div>'
        "</section>"
        "</section>"
        "</div>"
    )


BUILDERS = {
    "a": _build_design_a,
    "b": _build_design_b,
    "c": _build_design_c,
    "d": _build_design_d,
    "e": _build_design_e,
}


@patch("work-centre-a", "work-centre-b", "work-centre-c", "work-centre-d", "work-centre-e")
def apply_work_centre_design(ctx: Ctx) -> None:
    design = str(ctx.state.get("wc_design", "a")).lower()
    change_id, _, summary = DESIGN_META[design]
    old_wc = ctx.one("div.work-centre")
    if old_wc is None:
        return
    switcher = Ctx.html(_wc_design_switcher_bar(design))
    new_wc = Ctx.html(BUILDERS[design]())
    old_wc.insert_before(switcher)
    old_wc.replace_with(new_wc)
    ctx.mark(new_wc, change_id, summary)
    ctx.mark(new_wc, "AC", AC_SUMMARY)
