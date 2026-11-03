"""The v47 mockup's states: the Case record's Damage section and its readiness item.

Captures (captured-live/case/, ZzMockupCaptureCase.cs on origin/dev 7231a4b37, 3 November 2026):
  v47-two-read / v47-two-edit          two impacts: Moderate LH Side, Moderate Rear (the
                                       operator's screenshot)
  v47-none-read / v47-none-edit        no impact recorded; live is ready to send
  v47-partial-read / v47-partial-edit  one row with a severity and no location
  v47-rule-*                           the none and partial Cases again, captured with the
                                       scratch readiness item A switched on (MOCKUP_V47_RULE=1)

A state with "proposal" builds its Proposal over that capture; the others patch the Today
capture. "skipped" builds the Case as saved with Skip impacts ticked: the readiness is the
live none capture's (no item), with the tick drawn on.
"""
from __future__ import annotations

DAMAGE = "Case · Damage"
DAMAGE_SCROLL = "#section-damage"


def s(key: str, label: str, capture: str, group: str = DAMAGE, scroll: str = DAMAGE_SCROLL, **extra) -> dict:
    return {"key": key, "label": label, "group": group, "lane": "case", "capture": capture,
            "scroll": scroll, **extra}


STATES: list[dict] = [
    s("none-read", "Read · no impact: Impacts outstanding (A)", "v47-none-read",
      proposal="v47-rule-none-read"),
    s("none-edit", "Editing · no impact: Skip impacts offered (A, B)", "v47-none-edit",
      proposal="v47-rule-none-edit"),
    s("skipped-read", "Read · Skip impacts ticked and saved (C)", "v47-none-read", skipped=True),
    s("skipped-edit", "Editing · Skip impacts ticked and saved (B)", "v47-none-edit", skipped=True),
    s("partial-read", "Read · a row with no location: still outstanding (B)", "v47-partial-read",
      proposal="v47-rule-partial-read"),
    s("partial-edit", "Editing · a row with no location: no Skip impacts (B)", "v47-partial-edit",
      proposal="v47-rule-partial-edit"),
    s("two-read", "Read · two impacts: a space between the sentences (G)", "v47-two-read"),
    s("two-edit", "Editing · two impacts: no Skip impacts, the narrative spaced (B, G)", "v47-two-edit"),
]

# Live routes with no captured path of their own, mapped to the nearest state.
ROUTES: list[tuple[str, str]] = []
