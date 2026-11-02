"""Case details Proposal patches (v43 items, notes/v43-notes.md §6).

The operator's brief of 2 November 2026, applied to the captured #section-overview:

  A  the card headed "Principal" holds the Claim source and its contact, so it is
     headed "Claim source";
  B  the Claim source record's notes on every Case and this Case's Claim source notes
     sit in the Claim source card, under its contact cells;
  C  the Principal's notes (the record's, read-only, and this Case's) are their own
     full-width sub-panel headed "Principal", where the Notes band was;
  D  the Case contact sub-panel goes;
  E  Notes from client goes.

A–E are the operator's brief and answers (settled). F and G are open sign-off items:

  F  Accident circumstances, now alone in the accident band: full width (proposed)
     or its live half-width cell (variant state case-read-f-half);
  G  a Case whose Principal record has no notes: this Case's Principal notes cell
     keeps its live half-width place (proposed) or spans the panel (variant state
     case-read-bare-g-span).

Every label is a live CaseWorkspaceLabels.Frame string; the two new headings are the
live "Claim source" label and the operator's answer "Principal" (2 November 2026).
"""
from __future__ import annotations

from bs4 import Tag

from proposals_v43 import Ctx, patch, presets

CASE_STATES = (
    "case-read", "case-edit", "case-read-bare", "case-edit-bare",
    "case-edit-claim-source-changed", "case-read-f-half", "case-read-bare-g-span",
)


def _heading_text(h3: Tag, text: str) -> None:
    """Replace the heading's words, keeping its collapse toggle."""
    for node in list(h3.contents):
        if isinstance(node, str):
            node.extract()
    h3.insert(0, text + " ")


@patch(*CASE_STATES)
def claim_source_card(ctx: Ctx) -> None:
    card = ctx.one('#section-overview [data-collapse="case.overview.principal"]')
    if card is None:
        return
    card["data-collapse"] = "case.overview.claim-source"
    _heading_text(card.find("h3"), "Claim source")
    ctx.mark(card.find("h3"), "A", "The card holding the Claim source and its contact is headed Claim source, not Principal.")

    band = ctx.one("#section-overview [data-notes-band]")
    grid = card.select_one(".fg")
    if band is None or grid is None:
        return
    # B: the Claim source notes cells (the record's, its edit slot, this Case's) move
    # under the contact cells, each spanning the card.
    moved = []
    record = band.select_one('[data-record-notes="claim-source"], [data-record-notes-slot="claim-source"]')
    if record is not None:
        moved.append(record.extract())
    own = band.select_one("#f-claim-source-notes")
    own_cell = own.find_parent(class_="fc") if own is not None else None
    if own_cell is None:
        own_cell = next((fc for fc in band.select(".fc")
                         if fc.get_text(" ", strip=True).startswith("Claim source notes · this Case")), None)
    if own_cell is not None:
        moved.append(own_cell.extract())
    for cell in moved:
        grid.append(cell)
        ctx.mark(cell, "B", "The Claim source notes (the record's on every Case, then this Case's) sit in the Claim source card under its contact.")


@patch(*CASE_STATES)
def principal_panel(ctx: Ctx) -> None:
    band = ctx.one("#section-overview [data-notes-band]")
    if band is None:
        return
    # C: what is left of the Notes band is the Principal's notes: its own full-width sub-panel.
    del band["data-notes-band"]
    band["class"] = [c for c in band.get("class", []) if c != "notes-band"]
    band["data-collapse"] = "case.overview.principal-notes"
    _heading_text(band.find("h3"), "Principal")
    ctx.mark(band, "C", "The Principal's notes (the record's, read-only, and this Case's) are their own full-width sub-panel headed Principal, where the Notes band was.")


@patch(*CASE_STATES)
def case_contact_removed(ctx: Ctx) -> None:
    panel = ctx.one('#section-overview [data-collapse="case.overview.contact"]')
    ctx.remove(panel, "D", "The Case contact sub-panel and its three cells are removed.")


@patch(*CASE_STATES)
def client_notes_removed(ctx: Ctx) -> None:
    cell = ctx.one("#section-overview [data-client-notes]")
    if cell is None:
        return
    band = cell.find_parent(attrs={"data-accident-band": True})
    ctx.remove(cell, "E", "Notes from client is removed.")
    grid = band.select_one(".fg") if band is not None else None
    if grid is None:
        return
    if ctx.key == "case-read-f-half":
        ctx.mark(grid, "F", "Variant: Accident circumstances keeps its live half-width cell.")
    else:
        grid["class"] = [c for c in grid.get("class", []) if c != "g2"]
        ctx.mark(grid, "F", "Accident circumstances, now alone, spans the full width.")


@patch("case-read-bare-g-span")
def principal_case_notes_span(ctx: Ctx) -> None:
    panel = ctx.one('#section-overview [data-collapse="case.overview.principal-notes"]')
    if panel is None or panel.select_one('[data-record-notes="principal"]') is not None:
        return
    cell = panel.select_one(".fc")
    if cell is not None:
        cell["class"] = cell.get("class", []) + ["span2"]
        ctx.mark(cell, "G", "Variant: with no Principal record notes, this Case's Principal notes span the panel.")


# ---------------------------------------------------------------------------
# Presets (Today and Proposal alike)
# ---------------------------------------------------------------------------

@presets(*CASE_STATES)
def open_on_case_details(body: Tag, state: dict) -> None:
    """Every state opens on the Case details section (the first section; nothing to scroll)."""


@presets("case-edit-claim-source-changed")
def choose_another_claim_source(body: Tag, state: dict) -> None:
    """While editing a Case with no Claim source, choose Car 2 Go from the select.

    The capture's directory options carry no notes or contact, so this preset gives the
    Car 2 Go option synthetic ones (a fixture, like every value in the mockup) and fires
    the live change handler, so the notes cell is seen following the select.
    """
    select = body.select_one("[data-claim-source-select]")
    if select is None:
        return
    option = next((o for o in select.find_all("option") if o.get_text(strip=True) == "Car 2 Go"), None)
    if option is None:
        return
    option["data-notes"] = "Photos with every report, please."
    option["data-contact-name"] = "Lee Turner"
    option["data-contact-phone"] = "0161 555 0144"
    option["data-contact-email"] = "lee.turner@car2go.example"
    for other in select.find_all("option"):
        if other.has_attr("selected"):
            del other["selected"]
    option["selected"] = ""
    body.append(Ctx.html(
        "<script>window.addEventListener('load',function(){"
        "var s=document.querySelector('[data-claim-source-select]');"
        "if(s){s.dispatchEvent(new Event('change',{bubbles:true}));}});</script>"))

