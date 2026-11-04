"""v48 Proposal patch: the Original report card on the Audit view of an Inspection + Audit Case.

The letters are the sign-off items in notes/v48-notes.md §6.
  I  the card exists on an Inspection + Audit Case in the Audit view only, after Figures
  J  its heading is "Original report" (CaseWorkspaceLabels.Frame.OriginalReport)
  K  it reads the Inspection report as generated (OtherReportGeneration's snapshot)
  L  rows: Repair cost inc VAT; Salvage value only on a Total loss; Engineer's Value with the
     basis guide's word in brackets, none for a typed value; money as the aside draws it
  M  below 1441px the card is one more cell of the two-up strip

The rows reuse the Figures card's own markup (dl.figures, .figure, .mono, .absent) and the
live labels Frame.RepairCostIncVat, Settlement.SalvageValue and Frame.EngineersValue. The
figures are the capture's fixture facts ({name}.facts.json, "other"); the runtime formats
them (the money variable) and moves the card (the placement variable).
"""
from __future__ import annotations

from proposals_v48 import Anchor, Ctx, patch
from states_v48 import AUDIT_VIEW_STATES, STATES

HEADING = "Original report"
REPAIR_COST = "Repair cost inc VAT"
SALVAGE = "Salvage value"
ENGINEERS_VALUE = "Engineer's Value"


def money(value: float | int | None) -> str:
    return "—" if value is None else f"£{value:,.2f}"


def figure(label: str, value: float | None, big: bool = False, guide: str | None = None) -> str:
    absent = value is None
    text = money(value) + (f" ({guide})" if guide and not absent else "")
    attrs = "" if absent else f' data-v48-money="{value}"' + (f' data-v48-guide="{guide}"' if guide else "")
    return (f'<div class="figure{" figure--big" if big else ""}"><dt>{label}</dt>'
            f'<dd class="mono{" absent" if absent else ""}"{attrs}>{text}</dd></div>')


@patch(*AUDIT_VIEW_STATES)
def original_report_card(ctx: Ctx) -> None:
    if ctx.one('[data-case-view-row="audit"] [aria-current="page"]') is None:
        raise Anchor(f"{ctx.key}: not the Audit view of an Inspection + Audit Case")
    figures = ctx.need("[data-case-aside] [data-figures]")
    other = ctx.facts.get("other")
    if not other:
        raise Anchor(f"{ctx.key}: the capture's facts carry no Inspection report")
    total_loss = other.get("outcome") == "TotalLoss"
    rows = figure(REPAIR_COST, other.get("gross"), big=True)
    if total_loss:
        rows += figure(SALVAGE, other.get("salvageValue"))
    rows += figure(ENGINEERS_VALUE, other.get("engineerValue"), guide=other.get("guide"))
    card = ctx.html(
        '<section class="panel context-card" data-v48-original-report>'
        f'<div class="panel-head"><h2>{HEADING}</h2></div>'
        f'<div class="panel-body"><dl class="figures">{rows}</dl></div>'
        '</section>')
    figures.insert_after(card)
    ctx.mark(card, "I", "Original report: the Inspection report's figures, after Figures, in the Audit view only")
    ctx.record("K", "The card reads the Inspection report as generated; every figure is — until one exists")
    ctx.record("L", "Repair cost inc VAT, Salvage value on a Total loss, Engineer's Value with the guide's word in brackets")


@patch("audit-inspection")
def inspection_view_has_no_card(ctx: Ctx) -> None:
    """I: the Inspection view draws no card; the patch only proves the capture is that view."""
    if ctx.one('[data-case-view-row="inspection"] [aria-current="page"]') is None:
        raise Anchor(f"{ctx.key}: not the Inspection view")
    ctx.record("I", "Original report: the Inspection report's figures, after Figures, in the Audit view only")
