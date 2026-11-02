"""The v45 conformance states: the implemented Case page, captured from task/report-wording-settings.

Each state is the capture of the same name in ../captured-live/case/ with no patch: its
Today view is the implementation, compared with the mockup's Proposal of the same state.
The mockup's derived states (case-edit-unprojected, case-edit-columns) have no capture of
their own: B is covered by CaseReportWordingWebTests and G's variant was not chosen.
"""
from __future__ import annotations

GROUP = "Case · Report wording (implemented)"
SCROLL = "#section-report [data-report-wording]"


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
    s("valuation-read", "Valuation section · read", "case-read", scroll="#section-valuation"),
    s("valuation-edit", "Valuation section · editing", "case-edit", scroll="#section-valuation"),
]

ROUTES: list[tuple[str, str]] = []
