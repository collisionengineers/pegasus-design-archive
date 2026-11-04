"""The v48 mockup's states: the Send report dialog and the Original report aside card.

Captures (captured-live/case/, ZzMockupCaptureCase.CaptureV48* on origin/dev 8da7957ce,
4 November 2026). Every companion document is Confirmed so Generate report has left the
Report head and the send form stands:
  v48-plain-edit / v48-plain-read   a Principal with no rules; the report replies to the
                                    instruction e-mail; two Outgoing mailboxes (R655)
  v48-rules-edit                    a Principal whose rules ask questions, Cc, a hold, a
                                    reminder, an Audatex estimate
  v48-stop-edit                     a rule's Stop the Case already meets, a filed estimate,
                                    no instruction e-mail (the subject is "{REG} Report")
  v48-missing-edit                  a companion the Principal requires is not generated
  v48-resend-edit                   the report was sent once (the Already sent line, the
                                    resend name with its dot)
  v48-audit-edit / v48-audit-read   Inspection + Audit, the Audit view; the Inspection report
                                    was generated as a Total loss, salvage £1,250, on a Cazana
                                    guide, Engineer's Value £5,000
  v48-audit-repairable-read         the same Case; the Inspection report was Repairable
  v48-audit-inspection              the same Case in the Inspection view (no card)

A state with "dialog" opens the Send report dialog after the page loads (Proposal); Today
scrolls to the inline form instead. "viewer" opens the Nth Files row in the Case viewer over
the dialog; "rename" starts renaming the report.
"""
from __future__ import annotations

REPORT = "Case · Report send"
AUDIT = "Case · Inspection + Audit"
REPORT_SCROLL = "#section-report"
ASIDE_SCROLL = "[data-case-aside]"


def s(key: str, label: str, capture: str, group: str = REPORT, scroll: str | None = REPORT_SCROLL, **extra) -> dict:
    return {"key": key, "label": label, "group": group, "lane": "case", "capture": capture,
            "scroll": scroll, **extra}


STATES: list[dict] = [
    s("plain-edit", "Editing · Send report in the Report head; the form leaves the section (A, G)", "v48-plain-edit",
      panel="#section-report"),
    s("plain-dialog", "Send report dialog: From, To, Cc, Subject, Message, Files (B, C, D)", "v48-plain-edit",
      dialog=True),
    s("plain-viewer", "A file opened in the Case viewer over the dialog (F)", "v48-plain-edit",
      dialog=True, viewer=0),
    s("plain-rename", "Renaming the report: the stem, .pdf fixed, Reset (E)", "v48-plain-edit",
      dialog=True, rename=True),
    s("plain-read", "Reading · no Send report control, no greyed cells (G, H)", "v48-plain-read",
      panel="#section-report"),
    s("rules-dialog", "Principal rules: Questions, Cc hint, After sending, Holds (D)", "v48-rules-edit",
      dialog=True),
    s("stop-dialog", "A Stop with its Override reason; the filed estimate in Files (D)", "v48-stop-edit",
      dialog=True),
    s("missing-dialog", "Missing companion: the notice, Cancel only (D)", "v48-missing-edit",
      dialog=True),
    s("resend-dialog", "Already sent: the line and the resend name (E, G)", "v48-resend-edit",
      dialog=True),
    s("audit-edit", "Audit view · editing: the Original report card after Figures (I–M)", "v48-audit-edit",
      group=AUDIT, scroll=ASIDE_SCROLL, panel="[data-v48-original-report]"),
    s("audit-dialog", "Audit send: the Inspection report and its documents in Files (D)", "v48-audit-edit",
      group=AUDIT, dialog=True),
    s("audit-read", "Audit view · reading: the card (I–M)", "v48-audit-read",
      group=AUDIT, scroll=ASIDE_SCROLL, panel="[data-v48-original-report]"),
    s("audit-repairable", "Audit view · the Inspection was Repairable: no Salvage value row (L)", "v48-audit-repairable-read",
      group=AUDIT, scroll=ASIDE_SCROLL, panel="[data-v48-original-report]"),
    s("audit-inspection", "Inspection view · no card (I)", "v48-audit-inspection",
      group=AUDIT, scroll=ASIDE_SCROLL, panel="[data-figures]"),
]

EDIT_STATES = tuple(state["key"] for state in STATES
                    if state["capture"].endswith("-edit") and state["key"] != "audit-inspection")
DIALOG_STATES = tuple(state["key"] for state in STATES if state.get("dialog"))
READ_STATES = tuple(state["key"] for state in STATES if state["capture"].endswith("-read"))
AUDIT_VIEW_STATES = ("audit-edit", "audit-dialog", "audit-read", "audit-repairable")

# Live routes with no captured path of their own, mapped to the nearest state.
ROUTES: list[tuple[str, str]] = []
