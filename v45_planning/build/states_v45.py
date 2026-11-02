"""The v45 mockup's states: the Case record's report content choices and Report wording.

Captures (captured-live/case/, ZzMockupCaptureCase.cs on f6de68d1a, 2 November 2026):
  case-read / case-edit                    default switches (guide source, commentary and
                                           unrelated damage off; FAO and statement on)
  case-switches-read / case-switches-edit  guide source, commentary and unrelated damage on,
                                           with commentary text and unrelated damage recorded
  case-court-off-read / case-court-off-edit  FAO The Court and statement of truth recorded off

Derived states (a preset on the capture, in Today and Proposal alike):
  case-edit-unprojected  the report cannot be projected, so live draws no Report wording
                         panel (item B)
  case-edit-columns      item G variant: the settings laid out in columns
"""
from __future__ import annotations

GROUP = "Case · Report wording"
SCROLL = "#section-report [data-report-wording], #section-report [data-report-statement]"


def s(key: str, label: str, capture: str | None = None, **extra) -> dict:
    return {"key": key, "label": label, "group": GROUP, "lane": "case", "capture": capture or key,
            "scroll": SCROLL, **extra}


STATES: list[dict] = [
    s("case-read", "Read · default inclusions"),
    s("case-edit", "Editing · default inclusions"),
    s("case-switches-read", "Read · guide source, commentary, unrelated damage on"),
    s("case-switches-edit", "Editing · guide source, commentary, unrelated damage on"),
    s("case-court-off-read", "Read · FAO The Court and statement of truth off"),
    s("case-court-off-edit", "Editing · FAO The Court and statement of truth off"),
    s("case-edit-unprojected", "Editing · report cannot be projected (item B)", "case-edit"),
    s("case-edit-columns", "Editing · item G variant: settings in columns", "case-switches-edit"),
    s("valuation-read", "Valuation section · read", "case-read", scroll="#section-valuation"),
    s("valuation-edit", "Valuation section · editing", "case-edit", scroll="#section-valuation"),
]

# Live routes with no captured path of their own, mapped to the nearest state.
ROUTES: list[tuple[str, str]] = []
