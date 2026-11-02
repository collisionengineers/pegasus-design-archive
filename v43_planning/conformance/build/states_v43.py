"""The v43 mockup's states: the Case record's Case details section, captured from origin/dev.

Captures (captured-live/case/, ZzMockupCaptureCase.cs on 826c2aed7, 2 November 2026):
  case-read        a filled Case in Report preparation, read mode, with a Claim source,
                   the Principal's and Claim source's record notes and this Case's notes
  case-edit        the same Case in the edit session
  case-read-bare   no Claim source, no record notes, no Case notes (read mode)
  case-edit-bare   the same in the edit session
"""
from __future__ import annotations

CASE = "Case · Case details"


def s(key: str, label: str, capture: str | None = None, **extra) -> dict:
    return {"key": key, "label": label, "group": CASE, "lane": "case", "capture": capture or key, **extra}


STATES: list[dict] = [
    s("case-read", "Read · filled"),
    s("case-edit", "Editing · filled"),
    s("case-read-bare", "Read · no Claim source, no notes"),
    s("case-edit-bare", "Editing · no Claim source, no notes"),
    s("case-edit-claim-source-changed", "Editing · Claim source chosen (notes follow the select)", "case-edit-bare"),
    s("case-read-f-half", "Read · item F variant: Accident circumstances half width", "case-read"),
    s("case-read-bare-g-span", "Read · item G variant: this Case's Principal notes span the panel", "case-read-bare"),
]

# Live routes with no captured path of their own, mapped to the nearest state.
ROUTES: list[tuple[str, str]] = []
