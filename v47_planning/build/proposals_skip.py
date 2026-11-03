"""v47 Proposal patches: impacts or a deliberate Skip impacts, and the spaced Incident narrative.

The letters are the sign-off items in notes/v47-notes.md §6.
  A  the readiness item "Impacts" (drawn by the application itself in the rule captures;
     here it is only marked, and the impacts block takes the data-field its jump outlines)
  B  Skip impacts while editing: offered only while no row exists, beside Add impact
  C  Skip impacts while reading: a static tick in the same place
  G  the Incident narrative: one block per sentence, a line's space between them

The label "Skip impacts" is the operator's (round 1). The readiness wording is item A's
proposal and comes from the application's own rule capture, not from this file.
"""
from __future__ import annotations

from proposals_v47 import Ctx, patch

ALL = ("none-read", "none-edit", "skipped-read", "skipped-edit",
       "partial-read", "partial-edit", "two-read", "two-edit")
SKIP_PATH = "assessment.impacts_skipped"
SKIP_NAME = f"assessmentFields[{SKIP_PATH}]"
SKIP_LABEL = "Skip impacts"
CHECK = '<svg class="icon" aria-hidden="true"><use href="#icon-check"></use></svg>'

# With no row there is no column to align to, so the empty state sits on the facts' own left
# edge, the edge the Unrelated damage and Incident narrative cells use (operator, round 2:
# "it does look odd with things kinda floating rather than being organized"). Once a row
# exists the live row grid is unchanged, and the tick is hidden.
EMPTY = "#section-damage .impact-entry:not(:has([data-impacts-rows] [data-impact-row]))"
CSS = f"""
{EMPTY} .impact-entry-empty{{margin-left:0}}
.case-record.is-editing #section-damage[data-damage-editable="true"] .impact-entry:not(:has([data-impacts-rows] [data-impact-row])) .impact-entry-foot{{display:flex;align-items:center;gap:16px;margin-top:0}}
{EMPTY} .impact-entry-foot > span:first-child{{display:none}}
#section-damage .impact-entry-skip[hidden]{{display:none}}
#section-damage .impact-entry-skip.choice{{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;font-weight:500;min-height:var(--control)}}
#section-damage .impact-entry-skip input{{width:15px;height:15px;min-height:0;margin:0;accent-color:var(--red)}}
#section-damage .choice.is-static{{cursor:default;color:var(--muted)}}
#section-damage .choice.is-static[data-on="true"]{{color:var(--ink)}}
#section-damage .choice.is-static .tick{{display:inline-grid;place-items:center;width:15px;height:15px;flex:none;border:1px solid var(--line-strong);border-radius:2px;background:var(--surface-2)}}
#section-damage .choice.is-static .tick .icon{{width:11px;height:11px}}
#section-damage .impact-entry-foot.impact-entry-foot--read{{display:block;margin-top:0}}
"""

LINES_CSS = """
#section-damage [data-damage-narrative][data-v47-lines]{display:block}
#section-damage [data-damage-narrative] .fv-line{display:block}
#section-damage [data-damage-narrative] .fv-line+.fv-line{margin-top:1lh}
"""


def sheet(ctx: Ctx, css: str, change_id: str) -> None:
    """The proposal's stylesheet rules; a change is recorded only where markup changes."""
    ctx.body.append(ctx.html(f'<style data-v47-css="{change_id}">{css}</style>'))


def rows(ctx: Ctx) -> int:
    return len(ctx.all("#section-damage [data-impacts-rows] [data-impact-row]"))


@patch(*ALL)
def skip_tick(ctx: Ctx) -> None:
    entry = ctx.one("#section-damage [data-impacts]")
    if entry is None:
        return
    # A: the blocker's jump outlines the impacts block, as it does any field cell.
    entry["data-field"] = "assessment.impacts"
    skipped = bool(ctx.state.get("skipped"))
    count = rows(ctx)
    foot = entry.select_one(".impact-entry-foot")
    if foot is not None:
        checked = " checked" if skipped else ""
        hidden = " hidden" if count > 0 else ""
        tick = ctx.html(
            f'<label class="choice impact-entry-skip" data-v47-skip data-field="{SKIP_PATH}"{hidden}>'
            f'<input type="checkbox" name="{SKIP_NAME}" value="true" form="case-edit-form"{checked} />'
            f'<input type="hidden" name="{SKIP_NAME}" value="false" form="case-edit-form" />'
            f"<span>{SKIP_LABEL}</span></label>")
        foot.append(tick)
        add = foot.select_one("[data-impacts-add]")
        if skipped and add is not None:
            add["disabled"] = ""
        ctx.mark(tick, "B", "Skip impacts beside Add impact, offered only while no impact row exists; "
                            "ticking it greys out Add impact, a row hides it, and clearing the last row offers it again")
    elif count == 0:
        on = "true" if skipped else "false"
        read = ctx.html(
            '<div class="impact-entry-foot impact-entry-foot--read"><span></span>'
            f'<span class="choice is-static impact-entry-skip" data-on="{on}" data-v47-skip>'
            f'<span class="tick">{CHECK if skipped else ""}</span><span>{SKIP_LABEL}</span></span></div>')
        empty = entry.select_one("[data-impacts-empty]")
        (empty.insert_after(read) if empty is not None else entry.append(read))
        ctx.mark(read.select_one("[data-v47-skip]"), "C",
                 "While reading, Skip impacts is a static tick in the place the editable tick stands")
    sheet(ctx, CSS, "B")


@patch(*ALL)
def narrative_lines(ctx: Ctx) -> None:
    cell = ctx.one("#section-damage [data-damage-narrative]")
    if cell is None:
        return
    cell["data-v47-lines"] = ""
    text = cell.get_text().strip()
    if "\n" in text:
        cell.clear()
        for line in text.split("\n"):
            span = ctx.html('<span class="fv-line"></span>')
            span.string = line.strip()
            cell.append(span)
        ctx.mark(cell, "G", "The Incident narrative puts a line's space between its sentences")
    sheet(ctx, LINES_CSS, "G")


@patch("none-read", "none-edit", "partial-read", "partial-edit")
def mark_blocker(ctx: Ctx) -> None:
    summary = ("Readiness names Impacts until an impact is entered or Skip impacts is ticked "
               "(drawn by the application with the proposed rule)")
    step = ctx.one("[data-next-step]")
    label = step.select_one("[data-next-label]") if step is not None else None
    if label is not None and label.get_text(strip=True) == "Impacts":
        ctx.mark(step, "A", summary)
    for item in ctx.all("li.blocker"):
        if "Impacts" in item.get_text(" ", strip=True).split(" · ")[0]:
            ctx.mark(item, "A", summary)
