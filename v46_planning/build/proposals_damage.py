"""v46 proposal patches: impacts entered by hand, damage markers for the report's picture only.

Change IDs are the sign-off letters in notes/v46-notes.md §6.

Operator answers of 3 November 2026 (notes/discussion-log.md):
  the fourth box is a free-text note; rows are added as needed; a marker keeps its position
  only. Round 2: Clear is an x; the Incident narrative follows the impacts; with no impact
  the Nature of Incident is skipped; there is no Type box.

No new sentence is drawn on the page. The words are the live CaseWorkspaceLabels.Damage
strings ("Severity", "Note", "No damage recorded."), the operator's example ("Impact",
"Clear") and the captions item D asks about ("Location", "Add impact").
"""
from __future__ import annotations

import copy
import html
import pathlib

from bs4 import BeautifulSoup

from proposals_v46 import Ctx, patch

SEVERITIES = [
    ("light", "Light"), ("light_to_moderate", "Light to moderate"), ("moderate", "Moderate"),
    ("moderate_to_heavy", "Moderate to heavy"), ("heavy", "Heavy"),
]
# AssessmentVocabulary.DamageAreas, in the record's order, without Multiple (item B).
LOCATIONS = [
    ("front", "Front"), ("left_front", "LH Front"), ("right_front", "RH Front"),
    ("left_side", "LH Side"), ("right_side", "RH Side"), ("rear", "Rear"),
    ("left_rear", "LH Rear"), ("right_rear", "RH Rear"),
    ("underside", "Underside"), ("interior", "Interior"), ("mechanical", "Mechanical"),
]
SEVERITY_WORDS = dict(SEVERITIES)
LOCATION_WORDS = dict(LOCATIONS)

# The proposed impacts on each capture (severity, location, note).
FIXTURES: dict[str, list[tuple[str, str, str]]] = {
    "v46-two-read": [
        ("moderate", "right_rear", "Crease and paint damage to the rear quarter panel."),
        ("light", "rear", "Bumper cover scuffed and cracked."),
    ],
    "v46-apart-read": [
        ("light", "front", "Front bumper scuffed."),
        ("moderate", "right_side", "Driver's door dented."),
        ("moderate_to_heavy", "rear", "Boot lid and rear bumper pushed in."),
    ],
    "v46-none-read": [],
}
FIXTURES["v46-two-edit"] = FIXTURES["v46-two-read"]
FIXTURES["v46-apart-edit"] = FIXTURES["v46-apart-read"]
FIXTURES["v46-none-edit"] = FIXTURES["v46-none-read"]

DAMAGE_STATES = ("damage-two-read", "damage-two-edit", "damage-apart-read", "damage-apart-edit",
                 "damage-apart-edit-under", "damage-none-read", "damage-none-edit",
                 "wording-apart", "wording-none")

E = html.escape


def options(pairs: list[tuple[str, str]], chosen: str | None) -> str:
    blank = '<option value=""></option>'
    return blank + "".join(
        f'<option value="{code}"{" selected" if code == chosen else ""}>{E(text)}</option>' for code, text in pairs)


def cell(caption: str, text: str, control: str) -> str:
    empty = "" if text else " empty"
    return f'<span class="fc" data-caption="{caption}"><div class="fv{empty}">{E(text)}</div>{control}</span>'


def row(index: int, severity: str = "", location: str = "", note: str = "") -> str:
    return (
        f'<div class="impact-entry-row" data-v46-impact-row="{index}">'
        f'<span class="impact-entry-label">Impact</span>'
        + cell("Severity", SEVERITY_WORDS.get(severity, ""),
               f'<select class="fi" aria-label="Severity" data-v46-impact-severity>{options(SEVERITIES, severity)}</select>')
        + cell("Location", LOCATION_WORDS.get(location, ""),
               f'<select class="fi" aria-label="Location" data-v46-impact-location>{options(LOCATIONS, location)}</select>')
        + cell("Note", note, f'<input class="fi" maxlength="200" aria-label="Note" value="{E(note, quote=True)}" data-v46-impact-note />')
        + '<button type="button" class="icon-button impact-entry-clear" aria-label="Clear" title="Clear" data-v46-impact-clear>'
        '<svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button>'
        + '</div>'
    )


def block(rows: list[tuple[str, str, str]], compose: str = "all") -> str:
    body = "".join(row(i, *r) for i, r in enumerate(rows))
    hidden = "" if rows else " hidden"
    shown = " hidden" if rows else ""
    return (
        f'<div class="impact-entry" data-v46-impacts data-v46-compose="{compose}">'
        f'<div class="impact-entry-head" aria-hidden="true" data-v46-impact-head{hidden}><span></span>'
        '<span class="lbl">Severity</span>'
        '<span class="lbl">Location</span><span class="lbl">Note</span><span></span></div>'
        f'<div class="impact-entry-rows" data-v46-impact-rows>{body}</div>'
        f'<p class="muted impact-entry-empty" data-v46-impact-empty{shown}>No damage recorded.</p>'
        '<div class="impact-entry-foot"><span></span>'
        '<button type="button" class="btn impact-entry-add" data-v46-impact-add>'
        '<svg class="icon" aria-hidden="true"><use href="#icon-plus" /></svg><span>Add impact</span></button></div>'
        f'<template data-v46-impact-template>{row(0)}</template>'
        '</div>'
    )


CSS = """
#section-damage .impact-entry{display:grid;gap:6px}
#section-damage .damage-workbench + .impact-entry{margin-top:12px}
#section-damage .impact-entry-head[hidden]{display:none}
#section-damage .impact-entry-head,#section-damage .impact-entry-row{display:grid;grid-template-columns:52px minmax(162px,1fr) minmax(110px,.9fr) minmax(0,2fr) 36px;gap:6px;align-items:center}
#section-damage .impact-entry-foot{display:none;grid-template-columns:52px minmax(162px,1fr) minmax(110px,.9fr) minmax(0,2fr) 36px;gap:6px;margin-top:2px}
#section-damage .impact-entry-foot .impact-entry-add{grid-column:2/4;justify-self:start}
#section-damage .impact-entry-head .lbl{font-size:10.5px;color:var(--quiet);font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-left:9px;white-space:nowrap}
#section-damage .impact-entry-rows{display:grid;gap:6px}
#section-damage .impact-entry-label{font-weight:700;font-size:13px;color:var(--ink)}
#section-damage .impact-entry-row .fc{margin:0;min-width:0}
#section-damage .impact-entry-row .fc:not([data-caption="Note"]) .fv{flex-wrap:nowrap;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block}
#section-damage .impact-entry-row .fi{min-width:0;width:100%}
.is-editing #section-damage .impact-entry-row .fc:not(.ro) .fv{display:none}
#section-damage .impact-entry-clear{min-width:var(--control);min-height:var(--control);visibility:hidden;justify-self:center}
#section-damage .impact-entry-clear:hover{color:var(--danger);background:var(--danger-bg)}
#section-damage .impact-entry-empty{margin:0 0 0 58px;font-size:12.5px}
#section-damage .damage-extra{justify-content:center}
#section-damage .damage-extra [data-v46-clear-markers]{margin:0}
.case-record.is-editing #section-damage[data-damage-editable="true"] .impact-entry-row [data-v46-impact-clear]{visibility:visible}
.case-record.is-editing #section-damage[data-damage-editable="true"] .impact-entry-foot{display:grid}
@media(max-width:1100px){#section-damage .impact-entry-head{display:none}#section-damage .impact-entry-row{grid-template-columns:repeat(2,minmax(0,1fr));padding:8px;border:1px solid var(--line);border-radius:var(--radius)}#section-damage .impact-entry-label{grid-row:1;grid-column:1}#section-damage .impact-entry-row [data-v46-impact-clear]{grid-row:1;grid-column:2;justify-self:end}#section-damage .impact-entry-row .fc[data-caption="Note"]{grid-column:1/-1}#section-damage .impact-entry-empty{margin-left:0}.case-record.is-editing #section-damage[data-damage-editable="true"] .impact-entry-foot{display:block}#section-damage .impact-entry-row .fc::before{content:attr(data-caption);display:block;font-size:10.5px;color:var(--quiet);font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin:0 0 3px 9px}}
"""

# Add and Clear (item C: the × removes the row; rows are added as needed). Every change
# recomposes the Incident narrative and the Nature of Incident block (item A), as live
# recomposes a block that tracks fields.
SCRIPT = """
document.addEventListener('DOMContentLoaded', function () {
  var root = document.querySelector('[data-v46-impacts]');
  if (!root) return;
  var rows = root.querySelector('[data-v46-impact-rows]');
  var empty = root.querySelector('[data-v46-impact-empty]');
  var template = root.querySelector('[data-v46-impact-template]');
  var section = root.closest('#section-damage');
  var absent = (section && section.getAttribute('data-damage-absent')) || 'Not recorded';
  function word(select) {
    var option = select.options[select.selectedIndex];
    return option && option.value ? option.text.toLowerCase().replace(/^lh /, 'left ').replace(/^rh /, 'right ') : '';
  }
  function compose() {
    var parts = [];
    rows.querySelectorAll('[data-v46-impact-row]').forEach(function (r) {
      var severity = word(r.querySelector('[data-v46-impact-severity]'));
      var location = word(r.querySelector('[data-v46-impact-location]'));
      if (severity && location) parts.push(severity + ' collision/impact damage to the ' + location);
    });
    return parts.map(function (part) { return 'The vehicle has suffered ' + part + '.'; }).join('\\n');
  }
  function recompose() {
    var sentence = compose();
    var narrative = document.querySelector('[data-damage-narrative]');
    if (narrative) {
      narrative.textContent = sentence || absent;
      narrative.classList.toggle('empty', !sentence);
      narrative.classList.toggle('multi', sentence.indexOf('\\n') >= 0);
    }
    var nature = document.querySelector('[data-wording-block="nature"]');
    if (nature) {
      if (nature.hasAttribute('data-wording-composed')) nature.setAttribute('data-wording-composed', sentence);
      var text = nature.querySelector('textarea[data-wording-text]');
      if (text) text.value = sentence;
      // G (operator, 3 November 2026): with no impact, Nature of Incident is skipped.
      nature.hidden = !sentence;
      var tick = document.querySelector('[data-wording-toggle="nature"]');
      if (tick) (tick.closest('label') || tick).hidden = !sentence;
      nature.querySelectorAll('.fv').forEach(function (v) {
        if (/collision\\/impact|^$/.test(v.textContent.trim()) && !v.closest('.wbh')) v.textContent = sentence;
      });
    }
  }
  function sync() {
    recompose();
    var all = rows.querySelectorAll('[data-v46-impact-row]');
    all.forEach(function (r, i) { r.setAttribute('data-v46-impact-row', String(i)); });
    empty.hidden = all.length > 0;
    root.querySelector('[data-v46-impact-head]').hidden = all.length === 0;
  }
  root.querySelector('[data-v46-impact-add]').addEventListener('click', function () {
    rows.appendChild(template.content.firstElementChild.cloneNode(true));
    sync();
    var added = rows.lastElementChild.querySelector('select');
    if (added) added.focus();
  });
  rows.addEventListener('click', function (event) {
    var clear = event.target.closest('[data-v46-impact-clear]');
    if (!clear) return;
    clear.closest('[data-v46-impact-row]').remove();
    sync();
  });
  rows.addEventListener('change', function (event) {
    var control = event.target.closest('select, input');
    if (!control) return;
    var value = control.previousElementSibling;
    if (!value || !value.classList.contains('fv')) return;
    value.textContent = control.tagName === 'SELECT' ? control.options[control.selectedIndex].text : control.value;
    value.classList.toggle('empty', !value.textContent);
    recompose();
  });
});
"""


@patch(*DAMAGE_STATES)
def damage_section(ctx: Ctx) -> None:
    section = ctx.one("#section-damage")
    if section is None:
        return
    capture = ctx.state["capture"]

    # I: the derived Impact location and Impact severity cells and the per-marker list go.
    facts = section.select_one(".damage-facts")
    derived = facts.select_one(".fg.g2") if facts else None
    marker_list = facts.select_one("[data-damage-impact-list]") if facts else None
    # K: the impacts take the place of the derived cells and the list, beside the plan.
    entry = ctx.html(block(FIXTURES.get(capture, [])))
    if derived is not None:
        derived.insert_before(entry)
    elif facts is not None:
        facts.insert(0, entry)
    ctx.mark(entry, "B C D K", "Impacts are rows typed in by staff: Impact · Severity · Location · Note · × (Clear), "
             "with Add impact. They stand where the derived cells and the "
             "marker list stood. Location is one of the 11 recorded areas, with no Multiple.")
    ctx.remove(derived, "I", "Removed: the derived Impact location and Impact severity cells, the "
               "per-marker list (areas, severity, note, ×), the Underside, Interior and Mechanical chips "
               "(now Location values) and the area readout. A marker is a burst on the plan and nothing else.")
    ctx.remove(marker_list, "I", "The per-marker list (areas, severity, note, ×) is removed: a marker "
               "is a burst on the plan and nothing else.")

    # I: Underside, Interior and Mechanical are Location values now, not chips; the readout goes.
    for chip in section.select(".damage-extra [data-damage-area]"):
        ctx.remove(chip, "I", "The Underside, Interior and Mechanical chips are removed; they are "
                   "Location values on an impact row.")
    ctx.remove(section.select_one("[data-damage-readout]"), "I",
               "The area readout under the pointer is removed: a marker names no area.")
    extra = section.select_one(".damage-extra")
    if extra is not None and not extra.find(True):
        extra.decompose()
    reset = section.select_one("[data-damage-reset]")
    if reset is not None:
        clear_markers = ctx.html('<button type="button" class="btn" data-v46-clear-markers>'
                                 '<svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg>'
                                 '<span>Clear markers</span></button>')
        reset.insert_before(clear_markers)
        reset.decompose()
        ctx.mark(clear_markers, "J", "Clear markers (round 3) removes every marker and stands where Reset "
                 "stood; Reset is removed (round 4). The impacts are untouched.")
    # The hidden plan-area keyboard controls named an area for a new damage.
    for control in section.select("[data-damage-plan-area]"):
        control.decompose()
    plan = section.select_one("svg.damage-diagram")
    ctx.mark(plan, "J", "A marker is pressed, sized and moved as today; it is not removed by dragging (J2, round 4).")

    if ctx.key == "damage-apart-edit-under":
        workbench = section.select_one(".damage-workbench")
        entry.extract()
        workbench.insert_after(entry)
        ctx.mark(entry, "K", "Item K variant: the impacts run the full width of the section, under the plan.")
    ctx.style(CSS, "K", "Impact rows laid out in one line per impact; two columns below 1100px.")
    script = ctx.html(f"<script data-v46-js>{SCRIPT}</script>")
    section.append(script)


def words(code: str) -> str:
    return (SEVERITY_WORDS.get(code) or LOCATION_WORDS.get(code) or code).lower() \
        .replace("lh ", "left ").replace("rh ", "right ")


def nature(rows: list[tuple[str, str, str]]) -> str:
    """Round 3 (A): a separate sentence for each impact, one to a line, in row order."""
    return "\n".join(f"The vehicle has suffered {words(severity)} collision/impact damage to the {words(location)}."
                     for severity, location, _note in rows)


@patch("wording-apart", "damage-two-read", "damage-two-edit", "damage-apart-read",
       "damage-apart-edit", "damage-apart-edit-under")
def nature_of_incident(ctx: Ctx) -> None:
    block_el = ctx.one('[data-wording-block="nature"]')
    if block_el is None:
        return
    sentence = nature(FIXTURES.get(ctx.state["capture"], []))
    if not sentence:
        return
    if block_el.has_attr("data-wording-composed"):
        block_el["data-wording-composed"] = sentence
    text = block_el.select_one("textarea[data-wording-text]")
    if text is not None:
        text.string = sentence
    for value in block_el.select(".fv"):
        if "collision/impact" in value.get_text():
            value.string = sentence
    narrative = ctx.one("[data-damage-narrative]")
    if narrative is not None:
        narrative.string = sentence
        classes = [c for c in narrative.get("class", []) if c != "multi"]
        narrative["class"] = classes + (["multi"] if "\n" in sentence else [])
        ctx.mark(narrative, "A", "")
    summary = ("Nature of Incident is a separate sentence for each impact, one to a line, in row "
               "order (round 3); the report's Impact Magnitude prints the first impact.")
    ctx.mark(block_el, "A", summary)


CAPTURED = pathlib.Path(__file__).resolve().parent.parent / "captured-live" / "case"
# The same Case fixture with damage recorded, whose report could be projected.
DONOR = {"v46-none-read": "v46-apart-read", "v46-none-edit": "v46-apart-edit"}


def case_id(body) -> str | None:
    section = body.select_one("[data-case-id]") or body.select_one('input[name="id"]')
    return section.get("data-case-id") or section.get("value") if section else None


@patch("damage-none-read", "damage-none-edit", "wording-none")
def no_impact_report(ctx: Ctx) -> None:
    """G, ruled 3 November 2026: with no impact recorded, Nature of Incident is skipped.

    Live refuses to project the report without the derived pair, so Report not ready lists
    Impact location and Impact severity and Report wording shows its settings alone. The
    proposal takes the Report section and Next action from the same fixture's capture with
    damage recorded (the only difference between the two Cases), with Nature of Incident
    removed.
    """
    donor_name = DONOR[ctx.state["capture"]]
    donor = BeautifulSoup((CAPTURED / f"{donor_name}.html").read_text(encoding="utf-8"), "lxml").body
    own_id, donor_id = case_id(ctx.body), case_id(donor)
    for selector in ("#section-report", "[data-next-action]"):
        mine, theirs = ctx.one(selector), donor.select_one(selector)
        if mine is None or theirs is None:
            continue
        markup = str(theirs)
        if own_id and donor_id:
            markup = markup.replace(donor_id, own_id)
        graft = BeautifulSoup(markup, "lxml").body.find(True)
        # As the build does for every capture: the sprite is inlined once, scripts do not travel.
        for use in graft.select("use[href]"):
            if "lucide-sprite" in use["href"] and "#" in use["href"]:
                use["href"] = "#" + use["href"].split("#", 1)[1]
        for script in graft.select("script"):
            script.decompose()
        mine.replace_with(graft)
        if selector == "#section-report":
            report = graft
    nature = report.select_one('[data-wording-block="nature"]')
    if nature is not None:
        nature.decompose()
    tick = report.select_one('[data-wording-toggle="nature"]')
    if tick is not None:
        (tick.find_parent("label") or tick).decompose()
    # The aside's Report not ready card listed only Impact location and Impact severity.
    card = ctx.one("section.report-not-ready")
    if card is not None and all(b.get("data-report-blocker") == "damage" for b in card.select("li.blocker")):
        ctx.remove(card, "G", "")
    ctx.mark(report, "G", "Ruled 3 November 2026: impacts are optional. With none recorded the report "
             "is not blocked and Nature of Incident is skipped: no block and no tick.")
