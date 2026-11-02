"""Report wording Proposal patches (v45, notes/v45-notes.md).

The operator's brief and answers of 2 November 2026 (settled; change ids R1-R6):

  R1  Valuation's On the report row leaves the Valuation section;
  R2  the Report wording panel opens with one settings checklist: every offered block,
      manual paragraphs, then Disclose guide source, FAO The Court and Include statement
      of truth, each defaulting as it does today;
  R3  the per-block On report tick goes; an unticked item has no block in the panel;
  R4  ticking Valuation commentary or Unrelated damage shows its own block, and the
      commentary is written in its block (the separate field goes);
  R5  the Statement of truth is a read-only block in the panel; its folded sub-panel goes;
  R6  Disclose guide source shows its sentence as a read-only box; FAO The Court is a
      tick with no box.

Open sign-off items marked where they show: A (one owner per tick), B (report cannot be
projected), C (read mode as static ticks), D (read-only blocks pinned last, guide box in
print position), E (commentary text owner), G (settings layout), H (the commentary tick's
label), I (statement block with the statement off).

Every label is a live string: CaseWorkspaceLabels.ReportWording / .Report, the block
titles from ReportWordingComposition, EngineerLabels.StatementOfTruth. The statement
paragraphs are AssessmentReportRendering's constants, verbatim.
"""
from __future__ import annotations

import copy
import re

from bs4 import Tag

from proposals_v45 import Ctx, patch, presets

# AssessmentReportRendering (origin/dev f6de68d1a), verbatim.
SOT1 = ("I declare that I understand my duty in providing this report to the court and I confirm that I have "
        "complied with that duty. I understand that this duty overrides any other obligation. The report is based "
        "upon instructions received.")
SOT2 = ("I confirm that I have made clear which facts and matters referred to in this report are within my own "
        "knowledge and which are not. Those that are within my own knowledge I confirm to be true. The opinions I "
        "have expressed represent my true and complete professional opinion on the matters to which they refer.")
GUIDE = ("We have used Glass's Evaluator to assist with the valuation of the vehicle and Thatcham and/or "
         "manufacturer's data to compile the repair specification.")
SOT3 = ("Parts prices are subject to fluctuation and further damage may be found upon dismantling the vehicle. Our "
        "valuation is based on the mileage information provided and assuming that the vehicle has a valid MOT "
        "certificate (where applicable) to support such.")
SOT4 = ("We appreciate your instructions and enclose our fee note for your kind attention, which we confirm remains "
        "payable irrespective of the outcome of this case. Please ensure this is passed to your accounts department.")

# Live labels.
STATEMENT = "Statement of truth"            # EngineerLabels.StatementOfTruth
PAV = "PAV commentary"                      # ReportWordingComposition standard title
UNRELATED = "Unrelated damage"              # standard title and CaseWorkspaceLabels.Report.UnrelatedDamage
TRACKS = "tracks fields"                    # CaseWorkspaceLabels.ReportWording.TracksFields
SWITCHES = [
    # (path, settings key, live label)
    ("report.disclose_guide_source", "guide", "Disclose guide source"),
    ("report.fao_the_court", "fao", "FAO The Court"),
    ("report.include_statement_of_truth", "statement", "Include statement of truth"),
]
COMMENTARY_SWITCH = "report.valuation_commentary"
UNRELATED_SWITCH = "report.include_unrelated_damage"
COMMENTARY_TEXT = "report.valuation_commentary_text"

COMMENTARY_FIXTURE = "The guide value reflects the vehicle's recorded mileage and condition; no adjustment was needed."

REPORT_STATES = (
    "case-read", "case-edit", "case-switches-read", "case-switches-edit", "case-court-off-read",
    "case-court-off-edit", "case-edit-unprojected", "case-edit-columns", "valuation-read", "valuation-edit",
)
SWITCHES_ON = ("case-switches-read", "case-switches-edit", "case-edit-columns")

CSS = """
#section-report .wording-settings{display:flex;flex-wrap:wrap;align-items:center;gap:6px 20px;margin:0 0 8px;padding:8px;border:1px solid var(--line);border-radius:4px;background:var(--surface-2)}
#section-report .wording-settings .choice{display:inline-flex;align-items:center;gap:6px;font-size:12px;white-space:nowrap}
#section-report .wording-settings--columns{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}
#section-report .wb-fixed{background:var(--surface-2)}
#section-report .wb-fixed .fc+.fc,#section-report .wb-fixed .wb-fixed{margin-top:8px}
#section-report .wb-fixed .wb-fixed{background:var(--surface)}
@media (max-width:900px){#section-report .wording-settings--columns{grid-template-columns:repeat(2,minmax(0,1fr))}}
"""

SCRIPT = r"""
(function () {
  'use strict';
  function bind() {
    var panel = document.querySelector('#section-report [data-report-wording]');
    if (!panel || panel.dataset.v45Bound) { return; }
    panel.dataset.v45Bound = 'true';
    var settings = panel.querySelector('[data-wording-settings]');
    var list = panel.querySelector('[data-wording-list]');
    if (!settings) { return; }
    function target(key) {
      if (key === 'statement') { return panel.querySelector('[data-sot-court]'); }
      return panel.querySelector('[data-wording-block="' + key + '"]');
    }
    function sync(box) {
      var shown = target(box.getAttribute('data-wording-toggle'));
      if (shown) { shown.hidden = !box.checked; }
    }
    settings.addEventListener('change', function (event) {
      var box = event.target.closest('[data-wording-toggle]');
      if (box) { sync(box); }
    });
    function follow(row) {
      var title = row.querySelector('input.wbt');
      var key = row.getAttribute('data-wording-block');
      var label = settings.querySelector('[data-wording-toggle="' + key + '"] ~ span');
      if (title && label) { title.addEventListener('input', function () { label.textContent = title.value; }); }
    }
    function add(row) {
      var key = row.getAttribute('data-wording-block');
      var name = row.querySelector('[data-wording-key]').name.replace(/\.Key$/, '.Included');
      var label = document.createElement('label');
      label.className = 'choice';
      label.innerHTML = '<input type="checkbox" value="true" checked form="case-edit-form" data-wording-included>'
        + '<input type="hidden" value="false" form="case-edit-form"><span></span>';
      var inputs = label.querySelectorAll('input');
      inputs[0].name = name; inputs[1].name = name;
      inputs[0].setAttribute('data-wording-toggle', key);
      label.querySelector('span').textContent = (row.querySelector('input.wbt') || {}).value || '';
      settings.insertBefore(label, settings.querySelector('[data-wording-toggle="guide"]').closest('label'));
      follow(row);
    }
    if (list) {
      Array.prototype.forEach.call(list.querySelectorAll('[data-wording-row]'), follow);
      new MutationObserver(function (records) {
        records.forEach(function (record) {
          Array.prototype.forEach.call(record.addedNodes, function (node) {
            if (node.nodeType === 1 && node.matches('[data-wording-row]')
                && !settings.querySelector('[data-wording-toggle="' + node.getAttribute('data-wording-block') + '"]')) {
              add(node);
            }
          });
        });
      }).observe(list, { childList: true });
    }
  }
  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', bind); } else { bind(); }
})();
"""


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _switch_states(ctx_body: Tag) -> dict[str, bool]:
    """The five switches as live records them: inputs while editing, the summary line while reading."""
    row = ctx_body.select_one('[data-field="report-content"]')
    states: dict[str, bool] = {}
    if row is None:
        return states
    boxes = row.select("input[type=checkbox][data-report-switch]")
    if boxes:
        for box in boxes:
            states[box["data-report-switch"]] = box.has_attr("checked")
        return states
    summary = row.select_one("[data-report-content]").get_text(" ", strip=True)
    states["report.disclose_guide_source"] = "Guide source disclosed" in summary
    states[COMMENTARY_SWITCH] = "valuation commentary" in summary
    states[UNRELATED_SWITCH] = "unrelated damage" in summary
    states["report.fao_the_court"] = "No FAO The Court" not in summary
    states["report.include_statement_of_truth"] = "No statement of truth" not in summary
    return states


def _static_tick(label: str, on: bool, key: str) -> str:
    tick = '<svg aria-hidden="true" class="icon"><use href="#icon-check"></use></svg>' if on else ""
    return (f'<span class="choice is-static" data-on="{"true" if on else "false"}" data-wording-toggle="{key}">'
            f'<span class="tick">{tick}</span><span>{_esc(label)}</span></span>')


def _switch_tick(path: str, key: str, label: str, on: bool) -> str:
    name = f"assessmentFields[{path}]"
    checked = ' checked="checked"' if on else ""
    return (f'<label class="choice"><input type="checkbox" value="true" form="case-edit-form" name="{name}"'
            f' data-report-switch="{path}" data-wording-switch="" data-wording-toggle="{key}"{checked}/>'
            f'<input type="hidden" value="false" form="case-edit-form" name="{name}"/>'
            f'<span>{_esc(label)}</span></label>')


def _fixed_block(states: dict[str, bool]) -> str:
    """The Statement of truth as it prints (D, I), the guide sentence in its print place (R6)."""
    court = states.get("report.include_statement_of_truth", True)
    guide = states.get("report.disclose_guide_source", False)
    return (
        '<div class="stack" data-wording-fixed="">'
        '<div class="wb wb-fixed" data-wording-block="statement-of-truth">'
        f'<div class="wbh"><div class="fc ro wbt"><div class="fv">{STATEMENT}</div></div></div>'
        f'<div class="fc ro" data-sot-court=""{"" if court else " hidden"}><div class="fv derived multi">{_esc(SOT1)}\n\n{_esc(SOT2)}</div></div>'
        f'<div class="wb wb-fixed" data-wording-block="guide"{"" if guide else " hidden"}>'
        '<div class="wbh"><div class="fc ro wbt"><div class="fv">Disclose guide source</div></div></div>'
        f'<div class="fc ro"><div class="fv derived multi">{_esc(GUIDE)}</div></div></div>'
        f'<div class="fc ro"><div class="fv derived multi">{_esc(SOT3)}\n\n{_esc(SOT4)}</div></div>'
        '</div></div>'
    )


def _strip_included(row: Tag) -> None:
    for node in row.select('[name$=".Included"]'):
        parent = node.parent
        node.decompose()
        if parent is not None and parent.name == "label" and not parent.select("input"):
            parent.decompose()


def _edit_row(ctx: Ctx, source: Tag, key: str, title: str, text: str, slot: int) -> Tag:
    """A wording row for a block live does not offer while its switch is off, in the live row's shape."""
    row = copy.copy(source)
    row["data-wording-block"] = key
    row["data-wording-composed"] = text
    markup = str(row)
    markup = re.sub(r"wordingEdits\[\d+\]", f"wordingEdits[{slot}]", markup)
    markup = re.sub(r"f-wording-\d+-", f"f-wording-{slot}-", markup)
    fresh = ctx.html(markup)
    fresh.select_one("[data-wording-key]")["value"] = key
    fresh.select_one("input.wbt")["value"] = title
    fresh.select_one("[data-wording-chip]").string = TRACKS
    fresh.select_one("[data-wording-chip]")["class"] = ["src-tag"]
    fresh.select_one("textarea").string = text
    return fresh


def _read_block(source: Tag, key: str, title: str, text: str) -> Tag:
    block = copy.copy(source)
    block["data-wording-block"] = key
    block.select_one(".wbt .fv").string = title
    block.select_one(".src-tag").string = TRACKS
    block.select_one(".src-tag")["class"] = ["src-tag"]
    block.select_one(".wbh ~ .fc .fv").string = text
    return block


# ---------------------------------------------------------------------------
# presets: what live draws that the capture's fake projection does not
# ---------------------------------------------------------------------------

@presets(*SWITCHES_ON)
def commentary_and_guide_as_live(body: Tag, state: dict) -> None:
    """The fake projection behind the capture carries no ValuationCommentary and no Glass's guide, so
    live's PAV commentary block and guide sentence are added here, in Today and Proposal alike."""
    panel = body.select_one("#section-report [data-report-wording]")
    if panel is not None and panel.select_one('[data-wording-block="commentary"]') is None:
        comments = panel.select_one('[data-wording-block="comments"]')
        if comments is not None and comments.has_attr("data-wording-row"):
            slot = len(panel.select("[data-wording-list] > [data-wording-row]"))
            row = copy.copy(comments)
            markup = re.sub(r"wordingEdits\[\d+\]", f"wordingEdits[{slot}]", str(row))
            markup = re.sub(r"f-wording-\d+-", f"f-wording-{slot}-", markup)
            fresh = Ctx.html(markup)
            fresh["data-wording-block"] = "commentary"
            fresh["data-wording-composed"] = COMMENTARY_FIXTURE
            fresh.select_one("[data-wording-key]")["value"] = "commentary"
            fresh.select_one("input.wbt")["value"] = PAV
            fresh.select_one("textarea").string = COMMENTARY_FIXTURE
            comments.insert_after(fresh)
        elif comments is not None:
            comments.insert_after(_read_block(comments, "commentary", PAV, COMMENTARY_FIXTURE))
    statement = body.select_one("[data-report-statement] .fv")
    if statement is not None and GUIDE not in statement.get_text():
        statement.string = statement.get_text().replace(SOT2 + "\n\n", SOT2 + "\n\n" + GUIDE + "\n\n")


@presets("case-edit-unprojected")
def report_cannot_be_projected(body: Tag, state: dict) -> None:
    """Live draws no Report wording panel when the report cannot be projected (Model.ReportWording empty)."""
    panel = body.select_one("#section-report [data-report-wording]")
    if panel is not None:
        panel.decompose()


# ---------------------------------------------------------------------------
# patches
# ---------------------------------------------------------------------------

@patch(*REPORT_STATES)
def valuation_row_leaves(ctx: Ctx) -> None:
    row = ctx.one('#section-valuation [data-field="report-content"]')
    states = _switch_states(ctx.body)
    ctx.state["_switches"] = states
    if row is not None:
        # Keep the inputs (edit) for the settings checklist; the row itself goes.
        ctx.state["_switch_inputs"] = {box["data-report-switch"]: box.has_attr("checked")
                                       for box in row.select("input[type=checkbox][data-report-switch]")}
        ctx.remove(row, "R1", "On the report leaves the Valuation section; its five ticks move to Report wording.")


@patch(*REPORT_STATES)
def statement_and_commentary_move(ctx: Ctx) -> None:
    sub = ctx.one("#section-report [data-report-statement]")
    ctx.remove(sub, "R5", "The Statement of truth sub-panel goes; the statement is a read-only block in Report wording.")
    field = ctx.one(f'#section-report [data-field="{COMMENTARY_TEXT}"]')
    if field is not None:
        textarea = field.select_one("textarea")
        ctx.state["_commentary_text"] = (textarea.get_text() if textarea is not None
                                         else field.select_one(".fv").get_text(strip=True))
        if field.select_one(".fv.empty") is not None and textarea is None:
            ctx.state["_commentary_text"] = ""
        ctx.remove(field, "E", "The Valuation commentary field goes; the commentary is written in its block.")


@patch(*REPORT_STATES)
def wording_panel(ctx: Ctx) -> None:
    states = ctx.state.get("_switches", {})
    editing = ctx.one("#section-report [data-wording-list]") is not None or ctx.key == "case-edit-unprojected"
    panel = ctx.one("#section-report [data-report-wording]")
    commentary_on = states.get(COMMENTARY_SWITCH, False)
    unrelated_on = states.get(UNRELATED_SWITCH, False)
    commentary_text = ctx.state.get("_commentary_text") or ""

    if panel is None:
        # B: the report cannot be projected. The settings still show, with no blocks.
        anchor = ctx.one("#section-report .fg.g4")
        if anchor is None:
            return
        items = [_switch_tick(COMMENTARY_SWITCH, "commentary", PAV, commentary_on),
                 _switch_tick(UNRELATED_SWITCH, "unrelated", UNRELATED, unrelated_on)]
        items += [_switch_tick(path, key, label, states.get(path, key in ("fao", "statement")))
                  for path, key, label in SWITCHES]
        fresh = ctx.html('<div class="sub-panel wording" data-report-wording="">'
                         '<h3>Report wording<span class="rt">in print order</span></h3>'
                         f'<div class="wording-settings" data-wording-settings="">{"".join(items)}</div></div>')
        anchor.insert_after(fresh)
        ctx.mark(fresh.select_one("[data-wording-settings]"), "B",
                 "The report cannot be projected: the settings still show, with no blocks.")
        ctx.style(CSS, "R2", "Settings checklist styling.")
        return

    if editing:
        _edit_panel(ctx, panel, states, commentary_on, unrelated_on, commentary_text)
    else:
        _read_panel(ctx, panel, states, commentary_on, unrelated_on)
    ctx.style(CSS, "R2", "Settings checklist and read-only block styling.")


def _edit_panel(ctx: Ctx, panel: Tag, states: dict[str, bool], commentary_on: bool, unrelated_on: bool,
                commentary_text: str) -> None:
    wlist = panel.select_one("[data-wording-list]")
    rows = wlist.select(":scope > [data-wording-row]")
    comments = next((r for r in rows if r["data-wording-block"] == "comments"), rows[0])
    slot = len(rows)

    # R4: the commentary and unrelated damage blocks are offered whatever their switch says.
    commentary = wlist.select_one('[data-wording-block="commentary"]')
    if commentary is None:
        commentary = _edit_row(ctx, comments, "commentary", PAV, commentary_text, slot)
        slot += 1
        comments.insert_after(commentary)
    # E: the block's text box is the commentary field itself.
    area = commentary.select_one("textarea")
    area["name"] = f"assessmentFields[{COMMENTARY_TEXT}]"
    area.string = commentary_text
    recompose = commentary.select_one("[data-wording-recompose]")
    if recompose is not None:
        recompose.decompose()
    ctx.mark(commentary, "R4", "PAV commentary has its own block, shown while its tick is on; its text box writes the commentary (E).")

    unrelated = wlist.select_one('[data-wording-block="unrelated"]')
    if unrelated is None:
        unrelated = _edit_row(ctx, comments, "unrelated", UNRELATED, "", slot)
        slot += 1
        commentary.insert_after(unrelated)
    ctx.mark(unrelated, "R4", "Unrelated damage has its own block, shown while its tick is on.")

    # R2 / R3: one settings checklist; each row's own On report tick moves into it.
    items: list[str] = []
    for row in wlist.select(":scope > [data-wording-row]"):
        key = row["data-wording-block"]
        title = row.select_one("input.wbt")["value"]
        if key == "commentary":
            _strip_included(row)
            items.append(_switch_tick(COMMENTARY_SWITCH, "commentary", title, commentary_on))
            if not commentary_on:
                row["hidden"] = ""
            continue
        if key == "unrelated":
            _strip_included(row)
            items.append(_switch_tick(UNRELATED_SWITCH, "unrelated", title, unrelated_on))
            if not unrelated_on:
                row["hidden"] = ""
            continue
        box = row.select_one("input[type=checkbox][data-wording-included]")
        on = box is not None and box.has_attr("checked")
        name = box["name"] if box is not None else ""
        _strip_included(row)
        checked = ' checked="checked"' if on else ""
        items.append(f'<label class="choice"><input type="checkbox" value="true" form="case-edit-form" name="{name}"'
                     f' data-wording-included="" data-wording-toggle="{key}"{checked}/>'
                     f'<input type="hidden" value="false" form="case-edit-form" name="{name}"/>'
                     f'<span>{_esc(title)}</span></label>')
        if not on:
            row["hidden"] = ""
        row.attrs.pop("class", None)
        row["class"] = ["wb"]
    for path, key, label in SWITCHES:
        items.append(_switch_tick(path, key, label, states.get(path, key in ("fao", "statement"))))
    template = panel.select_one("[data-wording-template]")
    if template is not None:
        for row in template.select("[data-wording-row]"):
            _strip_included(row)

    columns = " wording-settings--columns" if ctx.key == "case-edit-columns" else ""
    settings = ctx.html(f'<div class="wording-settings{columns}" data-wording-settings="">{"".join(items)}</div>')
    panel.select_one("h3").insert_after(settings)
    ctx.mark(settings, "R2", "One settings checklist opens Report wording: every block, then Disclose guide source, "
                             "FAO The Court and Include statement of truth, defaulting as today.")
    if columns:
        ctx.mark(settings, "G", "Item G variant: the settings in columns.")
    ctx.record("R3", "Each block's own On report tick goes; an unticked item has no block.")
    ctx.record("A", "Commentary and unrelated damage: the one tick writes the switch; the block's own flag is not offered.")
    ctx.record("H", "The commentary tick reads as its block's heading (PAV commentary), not Valuation commentary.")

    fixed = ctx.html(_fixed_block(states))
    panel.select_one(".button-row").insert_after(fixed)
    ctx.mark(fixed.select_one(".wb-fixed"), "R5", "The Statement of truth is a read-only block, pinned last (D).")
    ctx.mark(fixed.select_one('[data-wording-block="guide"]'), "R6",
             "Disclose guide source shows its sentence in its print place; FAO The Court has no block.")
    ctx.record("D", "The read-only blocks are pinned last, with the guide sentence where it prints.")
    ctx.record("I", "With the statement off, its block keeps the paragraphs that still print (R609).")
    panel.append(ctx.html(f"<script>{SCRIPT}</script>"))


def _read_panel(ctx: Ctx, panel: Tag, states: dict[str, bool], commentary_on: bool, unrelated_on: bool) -> None:
    stack = panel.select_one(":scope > .stack")
    blocks = stack.select(":scope > .wb")
    comments = next((b for b in blocks if b["data-wording-block"] == "comments"), blocks[0])
    if stack.select_one('[data-wording-block="unrelated"]') is None:
        anchor = stack.select_one('[data-wording-block="commentary"]') or comments
        anchor.insert_after(_read_block(comments, "unrelated", UNRELATED, ""))
    if stack.select_one('[data-wording-block="commentary"]') is None:
        comments.insert_after(_read_block(comments, "commentary", PAV, ""))

    items: list[str] = []
    for block in stack.select(":scope > .wb"):
        key = block["data-wording-block"]
        title = block.select_one(".wbt .fv").get_text(strip=True)
        if key == "commentary":
            on = commentary_on
        elif key == "unrelated":
            on = unrelated_on
        else:
            on = "is-off" not in block.get("class", [])
        items.append(_static_tick(title, on, key))
        tools = block.select_one(".wb-tools")
        if tools is not None:
            tools.decompose()
        if not on:
            block.decompose()
    for path, key, label in SWITCHES:
        items.append(_static_tick(label, states.get(path, key in ("fao", "statement")), key))
    settings = ctx.html(f'<div class="wording-settings" data-wording-settings="">{"".join(items)}</div>')
    panel.select_one("h3").insert_after(settings)
    ctx.mark(settings, "C", "Read mode: the settings as static ticks, replacing the On the report summary line.")
    ctx.record("R3", "Only the ticked items have a block.")
    fixed = ctx.html(_fixed_block(states))
    stack.insert_after(fixed)
    ctx.mark(fixed.select_one(".wb-fixed"), "R5", "The Statement of truth is a read-only block, pinned last (D).")
