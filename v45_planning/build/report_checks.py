"""v45 report checks, imported by check-v45.py (the settled changes R1-R6 and items A-I)."""
from __future__ import annotations

import json

RS = "#section-report"
WP = f"{RS} [data-report-wording]"
SET = f"{WP} [data-wording-settings]"
VAL = "#section-valuation"
TAIL = ["Disclose guide source", "FAO The Court", "Include statement of truth"]


def run(page, go, check, q, n, text_in, frame_eval) -> None:
    def settings_labels() -> list[str]:
        return frame_eval(page, f"[...d.querySelectorAll({json.dumps(SET + ' .choice')})]"
                                ".map(c => c.lastElementChild.textContent.trim())")

    def shown(selector: str) -> bool:
        return frame_eval(page, f"(() => {{ const e = d.querySelector({json.dumps(selector)}); "
                                "return !!e && !e.closest('[hidden]') && e.getClientRects().length > 0; })()")

    def click(selector: str) -> None:
        frame_eval(page, f"d.querySelector({json.dumps(selector)}).click()")
        page.wait_for_timeout(60)

    def ticked(key: str) -> bool:
        return frame_eval(page, f"d.querySelector({json.dumps(SET + ' [data-wording-toggle=' + chr(34) + key + chr(34) + ']')}).checked")

    go(page, "case-edit", "today")
    check("today edit: On the report row on Valuation", q(page, f'{VAL} [data-field="report-content"]'))
    check("today edit: per-block On report ticks", n(page, f"{WP} [data-wording-row] [data-wording-included]") >= 5)
    check("today edit: Statement of truth sub-panel", q(page, f"{RS} [data-report-statement]"))
    check("today edit: Valuation commentary field", q(page, f'{RS} [data-field="report.valuation_commentary_text"]'))

    for key in ("case-read", "case-edit", "case-switches-read", "case-switches-edit",
                "case-court-off-read", "case-court-off-edit", "valuation-read", "valuation-edit"):
        go(page, key, "proposal")
        check(f"{key} R1: no On the report row anywhere", n(page, '[data-field="report-content"]') == 0)
        check(f"{key} R5: no Statement of truth sub-panel", n(page, "[data-report-statement]") == 0)
        check(f"{key} E: no separate commentary field", n(page, '[data-field="report.valuation_commentary_text"]') == 0)
        labels = settings_labels()
        check(f"{key} R2: settings open the panel, blocks first, the three switches last {labels}",
              q(page, f"{WP} > h3 + [data-wording-settings]") and labels[-3:] == TAIL
              and labels[:2] == ["Nature of Incident", "Engineer's Comments"]
              and "PAV commentary" in labels and "Unrelated damage" in labels)
        check(f"{key} R3: no On report tick on any block",
              n(page, f"{WP} .wb .wb-tools .choice") == 0 and n(page, f"{WP} .wb [data-wording-included]") == 0)
        check(f"{key} R6: FAO The Court has no block", n(page, f'{WP} [data-wording-block="fao"]') == 0)
        check(f"{key} R5: one read-only statement block with no inputs",
              n(page, f'{WP} [data-wording-block="statement-of-truth"]') == 1
              and n(page, f"{WP} [data-wording-fixed] input, {WP} [data-wording-fixed] textarea") == 0)
        court = "court-off" not in key
        check(f"{key} I: paragraphs 1-2 shown only with the statement on", shown(f"{WP} [data-sot-court]") == court)
        check(f"{key}: paragraphs 3-4 always shown", "Parts prices are subject" in text_in(page, f"{WP} [data-wording-fixed]"))
        on = "switches" in key
        check(f"{key} R6: guide sentence shown only with Disclose guide source on",
              shown(f'{WP} [data-wording-block="guide"]') == on)
        check(f"{key} R4: commentary block shown only with its tick on", shown(f'{WP} [data-wording-block="commentary"]') == on)
        check(f"{key} R4: unrelated damage block shown only with its tick on",
              shown(f'{WP} [data-wording-block="unrelated"]') == on)

    for key in ("case-read", "case-switches-read", "case-court-off-read"):
        go(page, key, "proposal")
        check(f"{key} C: settings are static ticks",
              n(page, f"{SET} .choice.is-static") >= 8 and n(page, f"{SET} input") == 0)
        check(f"{key} C: the FAO tick matches the record",
              frame_eval(page, f"d.querySelector({json.dumps(SET + ' [data-wording-toggle=fao]')}).dataset.on")
              == ("false" if "court-off" in key else "true"))

    go(page, "case-edit", "proposal")
    check("edit: defaults as today (guide, commentary, unrelated off; FAO, statement on)",
          [ticked(k) for k in ("guide", "commentary", "unrelated", "fao", "statement")]
          == [False, False, False, True, True])
    check("edit: the switches post under their live assessment names",
          n(page, f'{SET} input[type=checkbox][name="assessmentFields[report.fao_the_court]"]') == 1
          and n(page, f'{SET} input[type=hidden][name="assessmentFields[report.fao_the_court]"][value=false]') == 1)
    check("edit: block ticks post the live Included names", n(page, f'{SET} input[type=checkbox][name$=".Included"]') >= 5)
    check("edit E: the commentary text box writes the commentary field",
          q(page, f'{WP} [data-wording-block="commentary"] textarea[name="assessmentFields[report.valuation_commentary_text]"]'))
    click(f"{SET} [data-wording-toggle=commentary]")
    check("edit: ticking PAV commentary shows its block", shown(f'{WP} [data-wording-block="commentary"]'))
    click(f"{SET} [data-wording-toggle=unrelated]")
    check("edit: ticking Unrelated damage shows its block", shown(f'{WP} [data-wording-block="unrelated"]'))
    click(f"{SET} [data-wording-toggle=guide]")
    check("edit: ticking Disclose guide source shows its sentence", shown(f'{WP} [data-wording-block="guide"]'))
    click(f"{SET} [data-wording-toggle=statement]")
    check("edit: unticking the statement hides paragraphs 1-2 only",
          not shown(f"{WP} [data-sot-court]") and "Parts prices" in text_in(page, f"{WP} [data-wording-fixed]"))
    blocks = n(page, f"{WP} .wb:not([hidden])")
    click(f"{SET} [data-wording-toggle=fao]")
    check("edit: unticking FAO The Court shows or hides no block", n(page, f"{WP} .wb:not([hidden])") == blocks)
    click(f"{SET} [data-wording-toggle=nature]")
    check("edit: unticking Nature of Incident hides its block", not shown(f'{WP} [data-wording-block="nature"]'))
    click(f"{SET} [data-wording-toggle=nature]")
    check("edit: ticking it again shows it", shown(f'{WP} [data-wording-block="nature"]'))
    before = len(settings_labels())
    click(f"{WP} [data-wording-new]")
    labels = settings_labels()
    check(f"edit: New paragraph adds its tick before the three switches {labels[-4:]}",
          len(labels) == before + 1 and labels[-4] == "New paragraph" and labels[-3:] == TAIL)
    check("edit: the new paragraph's tick posts its Included",
          frame_eval(page, f"[...d.querySelectorAll({json.dumps(SET + ' input[type=checkbox]')})]"
                           ".some(i => /^wordingEdits\\[\\d+\\]\\.Included$/.test(i.name)"
                           " && (i.getAttribute('data-wording-toggle') || '').startsWith('manual:'))"))
    frame_eval(page, f"(() => {{ const t = [...d.querySelectorAll({json.dumps(WP + ' input.wbt')})].pop(); "
                     "t.value = 'Storage'; t.dispatchEvent(new Event('input', {bubbles: true})); })()")
    check("edit: the tick follows the paragraph's heading", "Storage" in settings_labels())
    click(f"{WP} [data-wording-list] > [data-wording-row]:nth-child(2) [data-wording-up]")
    check("edit: Move up still works",
          frame_eval(page, f"d.querySelector({json.dumps(WP + ' [data-wording-row]')}).dataset.wordingBlock") == "comments")

    go(page, "case-switches-edit", "proposal")
    check("switches edit: the commentary text is in its block",
          "guide value reflects" in frame_eval(page, f"d.querySelector({json.dumps(WP + ' [data-wording-block=commentary] textarea')}).value"))
    check("switches edit: commentary, unrelated and guide ticked",
          all(ticked(k) for k in ("commentary", "unrelated", "guide")))

    go(page, "case-edit-unprojected", "today")
    check("unprojected today: no Report wording panel", n(page, WP) == 0)
    go(page, "case-edit-unprojected", "proposal")
    check(f"unprojected B: the five switches only, no blocks {settings_labels()}",
          settings_labels() == ["PAV commentary", "Unrelated damage"] + TAIL and n(page, f"{WP} .wb") == 0)

    go(page, "case-edit-columns", "proposal")
    check("G variant: settings in columns",
          frame_eval(page, f"getComputedStyle(d.querySelector({json.dumps(SET)})).display") == "grid")
    go(page, "case-edit", "proposal")
    check("G proposed: settings in one wrapping line",
          frame_eval(page, f"getComputedStyle(d.querySelector({json.dumps(SET)})).display") == "flex")
