"""U11-U12: the Vehicle images and Unidentified record pages.

Each patch edits the captured live page only where the capture holds the element it
changes. A capture without the element is left as it is.
"""
from __future__ import annotations

from proposals_v41 import Ctx, patch

U11 = ("U11", "Add to an existing case is the one strong action and its eligible Cases sit right under it; Edit record is a plain button.")
U12 = ("U12", "Resolve lists its actions as one even column, Link to Case first, with Close with reason set apart at the bottom.")


# -- U11 --------------------------------------------------------------------

@patch("vehicle-images")
def u11_vehicle_images_one_primary(ctx: Ctx) -> None:
    bar = ctx.one(".image-record .image-record-bar")
    if bar is None:
        return
    edit = bar.select_one(".image-record-bar-end .btn--primary")
    if edit is not None:
        classes = [name for name in edit.get("class", []) if name != "btn--primary"]
        edit["class"] = classes
        ctx.mark(edit, *U11)

    add = bar.select_one('[data-image-action="add-to-case"]')
    candidates = ctx.one('.image-record-body section[aria-labelledby="image-intake-candidates-title"]')
    body = ctx.one(".image-record .image-record-body")
    if add is not None and candidates is not None and body is not None:
        body.insert(0, candidates.extract())
        ctx.mark(candidates, *U11)
        ctx.mark(add, *U11)


# -- U12 --------------------------------------------------------------------

@patch("unidentified")
def u12_unidentified_resolve_column(ctx: Ctx) -> None:
    row = ctx.one("[data-unidentified-resolve] .panel-section > .button-row")
    if row is None:
        return
    close = row.select_one('[data-unidentified-action="close"]')
    if close is None:
        return
    end = ctx.html('<div class="v41-resolve-end"></div>')
    close.insert_before(end)
    end.append(close.extract())
    row["class"] = row.get("class", []) + ["v41-resolve"]
    ctx.mark(row, *U12)
    ctx.style(
        "[data-unidentified-resolve] .button-row.v41-resolve{display:grid;gap:8px;align-items:stretch}"
        "[data-unidentified-resolve] .v41-resolve form{margin:0}"
        "[data-unidentified-resolve] .v41-resolve .btn{width:100%;justify-content:flex-start}"
        "[data-unidentified-resolve] .v41-resolve-end{margin-top:12px;padding-top:12px;border-top:1px solid var(--line)}",
        *U12)
