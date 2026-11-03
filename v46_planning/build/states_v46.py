"""The v46 mockup's states: the Case record's Damage section and the Nature of Incident block.

Captures (captured-live/case/, ZzMockupCaptureCase.cs on origin/dev fb4c5e741, 3 November 2026):
  v46-two-read / v46-two-edit      two damages recorded by area (RH Rear moderate, Rear light);
                                   live derives RH Rear, Moderate
  v46-apart-read / v46-apart-edit  three damages drawn apart (Front, RH Side, Rear);
                                   live derives Multiple, Moderate to heavy
  v46-none-read / v46-none-edit    no damage recorded

Derived states (a preset on a capture, in Today and Proposal alike):
  damage-apart-edit-under  item K variant: the impacts full width under the plan
"""
from __future__ import annotations

DAMAGE = "Case · Damage"
REPORT = "Case · Report wording"
DAMAGE_SCROLL = "#section-damage"
REPORT_SCROLL = "#section-report [data-report-wording]"


def s(key: str, label: str, capture: str, group: str = DAMAGE, scroll: str = DAMAGE_SCROLL, **extra) -> dict:
    return {"key": key, "label": label, "group": group, "lane": "case", "capture": capture,
            "scroll": scroll, **extra}


STATES: list[dict] = [
    s("damage-two-read", "Read · two impacts", "v46-two-read"),
    s("damage-two-edit", "Editing · two impacts", "v46-two-edit"),
    s("damage-apart-read", "Read · three impacts apart", "v46-apart-read"),
    s("damage-apart-edit", "Editing · three impacts apart", "v46-apart-edit"),
    s("damage-apart-edit-under", "Editing · item K variant: impacts under the plan", "v46-apart-edit"),
    s("damage-none-read", "Read · nothing recorded", "v46-none-read"),
    s("damage-none-edit", "Editing · nothing recorded", "v46-none-edit"),
    s("wording-apart", "Nature of Incident · a sentence for each impact (item A)", "v46-apart-edit",
      group=REPORT, scroll=REPORT_SCROLL),
    s("wording-none", "Report wording · no impact recorded: Nature of Incident skipped (G)", "v46-none-edit",
      group=REPORT, scroll=REPORT_SCROLL),
]

# Live routes with no captured path of their own, mapped to the nearest state.
ROUTES: list[tuple[str, str]] = []
