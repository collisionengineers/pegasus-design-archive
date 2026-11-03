"""Stage 2 conformance check and shots for pegasus_v46_routed.html (the implementation).

1. Every state loads with no page or console error.
2. The behaviours the notes promised, proven on the implemented page with its own script:
   the impact rows as captured, one geometry in read and edit, Add impact, filling a row,
   the x (Clear) removing its row, an incomplete row kept but left out of the narrative, the
   Incident narrative following the rows, Clear markers, a marker drawn and moved but never
   removed by dragging, no Reset, chips, readout or plan-area controls, the 1580 single line and
   the 760 fold, and the report with no impact: no Nature of Incident and no impact blockers.
3. Shots of every state at 1580x1000, 1440x900 and 760x1000, a crop of the Damage section (or
   the Report wording panel) at each width, and a 1580 whole page, into shots/ with
   verification.json. Compare each with ../shots/NNN-<state>-proposal-*.png.

Prints RESULT {"fail":[...],"okCount":N}. Run: python -X utf8 conformance/check-conformance.py
"""
from __future__ import annotations

import glob
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

HERE = Path(__file__).resolve().parent
SHOTS = HERE / "shots"
PAGE = (HERE / "pegasus_v46_routed.html").resolve().as_uri()
CHROME = next(iter(sorted(glob.glob(os.path.expandvars(
    r"%LOCALAPPDATA%\ms-playwright\chromium-*\chrome-win64\chrome.exe")), reverse=True)), None)
VIEWPORTS = [(1580, 1000), (1440, 900), (760, 1000)]
DS = "#section-damage"
WP = "#section-report [data-report-wording]"
ROW = "[data-impacts-rows] [data-impact-row]"
APART = ("The vehicle has suffered light collision/impact damage to the front.\n"
         "The vehicle has suffered moderate collision/impact damage to the right side.\n"
         "The vehicle has suffered moderate to heavy collision/impact damage to the rear.")

ok: list[str] = []
fail: list[str] = []


def check(name: str, condition: bool) -> None:
    (ok if condition else fail).append(name)


def go(page: Page, key: str) -> None:
    page.evaluate("([k, m, o]) => window.__mock.go(k, m, o)", [key, "today", {}])
    page.wait_for_timeout(200)


def frame_eval(page: Page, script: str):
    return page.evaluate(f"() => {{ const d = window.__mock.doc(); const w = window.__mock.win(); return ({script}); }}")


def n(page: Page, selector: str) -> int:
    return frame_eval(page, f"d.querySelectorAll({json.dumps(selector)}).length")


def q(page: Page, selector: str) -> bool:
    return n(page, selector) > 0


def shown(page: Page, selector: str) -> bool:
    return frame_eval(page, f"(() => {{ const e = d.querySelector({json.dumps(selector)}); if (!e) return false; "
                            "const s = w.getComputedStyle(e); const r = e.getBoundingClientRect(); "
                            "return s.display !== 'none' && s.visibility !== 'hidden' && !e.hidden && r.width > 0; })()")


def click(page: Page, selector: str, index: int = 0) -> None:
    frame_eval(page, f"d.querySelectorAll({json.dumps(selector)})[{index}].click()")
    page.wait_for_timeout(60)


def choose(page: Page, row: int, selector: str, value: str) -> None:
    frame_eval(page, f"(() => {{ const c = d.querySelectorAll({json.dumps(ROW)})[{row}].querySelector({json.dumps(selector)}); "
                     f"c.value = {json.dumps(value)}; c.dispatchEvent(new w.Event('change', {{bubbles: true}})); }})()")
    page.wait_for_timeout(40)


def narrative(page: Page) -> str:
    return frame_eval(page, "d.querySelector('[data-damage-narrative]').textContent")


def impacts_value(page: Page) -> list:
    return json.loads(frame_eval(page, "d.querySelector('[data-impacts-input]').value"))


def markers_value(page: Page) -> list:
    return json.loads(frame_eval(page, "d.querySelector('[data-damage-input]').value"))


def cell_lefts(page: Page) -> list:
    return frame_eval(page, f"[...d.querySelectorAll({json.dumps(ROW)})].map(r => [...r.children].map(c => Math.round(c.getBoundingClientRect().left)))")


def mouse_at(page: Page, selector: str) -> tuple[float, float]:
    box = frame_eval(page, f"(() => {{ const g = d.querySelector({json.dumps(selector)}); g.scrollIntoView({{block: 'center'}}); "
                           "const r = g.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; })()")
    origin = page.evaluate("(() => { const r = document.getElementById('mock-frame').getBoundingClientRect(); return [r.x, r.y]; })()")
    return origin[0] + box[0], origin[1] + box[1]


def damage_checks(page: Page) -> None:
    page.set_viewport_size({"width": 1580, "height": 1000})

    # Read: the impacts as captured, values only, the x's column kept but hidden.
    go(page, "damage-apart-read")
    check("read: three impact rows", n(page, ROW) == 3)
    check("read: no control shows", not shown(page, f"{ROW} select"))
    check("read: the x keeps its column, hidden", n(page, f"{ROW} [data-impact-clear]") == 3
          and not shown(page, f"{ROW} [data-impact-clear]"))
    check("read: no Add impact, no Clear markers", not q(page, "[data-impacts-add]") and not q(page, "[data-damage-clear-markers]"))
    check("read: the narrative is a sentence for each impact", narrative(page) == APART)
    read_lefts = cell_lefts(page)
    read_heights = frame_eval(page, f"[...d.querySelectorAll({json.dumps(ROW)})].map(r => Math.round(r.getBoundingClientRect().height))")
    check(f"1580: each impact on one line {read_heights}", all(h <= 40 for h in read_heights))
    for removed in ("[data-damage-reset]", "[data-damage-area]", "[data-damage-plan-area]", "[data-damage-readout]",
                    "[data-damage-location]", "[data-damage-severity]", "[data-damage-impact-list]"):
        check(f"I: {removed} is gone", not q(page, removed))
    check("Multiple is gone", "Multiple" not in frame_eval(page, f"d.querySelector({json.dumps(DS)}).innerText"))

    # Edit: one geometry, then every behaviour.
    go(page, "damage-apart-edit")
    check("edit: three impact rows and selects showing", n(page, ROW) == 3 and shown(page, f"{ROW} select"))
    check(f"one geometry: read and edit cells stand alike {read_lefts} / {cell_lefts(page)}", read_lefts == cell_lefts(page))
    check("edit: the x shows", shown(page, f"{ROW} [data-impact-clear]"))
    edit_heights = frame_eval(page, f"[...d.querySelectorAll({json.dumps(ROW)})].map(r => Math.round(r.getBoundingClientRect().height))")
    check(f"one geometry: read and edit rows are the same height {read_heights} / {edit_heights}", read_heights == edit_heights)
    check("edit: no value reads beside its control", not shown(page, f"{ROW} .fc .fv"))
    check("edit: Clear markers stands under the plan", shown(page, "[data-damage-clear-markers]"))
    check("edit: Add impact shows", shown(page, "[data-impacts-add]"))
    check("edit: no Reset", not q(page, "[data-damage-reset]"))
    check("edit: the template row is not drawn", n(page, f"{DS} [data-impact-row]") == 3 + 0
          or not shown(page, "template [data-impact-row]"))
    lefts = frame_eval(page, "(() => { const a = d.querySelector('[data-impacts-add]').getBoundingClientRect(); "
                             f"const s = d.querySelector({json.dumps(ROW)} + ' .fc').getBoundingClientRect(); return [a.left, s.left, a.height]; }})()")
    check(f"Add impact stands under Severity, full height {lefts}", abs(lefts[0] - lefts[1]) < 2 and lefts[2] >= 35)

    click(page, "[data-impacts-add]")
    check("Add impact adds a blank row", n(page, ROW) == 4
          and frame_eval(page, f"[...d.querySelectorAll({json.dumps(ROW)})][3].querySelector('[data-impact-severity]').value") == "")
    check("a blank row is not written", len(impacts_value(page)) == 3)
    choose(page, 3, "[data-impact-severity]", "heavy")
    check("an incomplete row is written as entered", impacts_value(page)[3] == {"severity": "heavy", "location": "", "note": ""})
    check("an incomplete row is left out of the narrative", narrative(page) == APART)
    choose(page, 3, "[data-impact-location]", "interior")
    check("a complete row joins the narrative on its own line",
          narrative(page) == APART + "\nThe vehicle has suffered heavy collision/impact damage to the interior.")
    check("the value reads where the control edits",
          frame_eval(page, f"[...d.querySelectorAll({json.dumps(ROW)})][3].querySelector('.fv').textContent") == "Heavy")

    click(page, f"{ROW} [data-impact-clear]", 1)
    check("the x removes its row", n(page, ROW) == 3)
    check("the x's row leaves the JSON", [i["location"] for i in impacts_value(page)] == ["front", "rear", "interior"])
    check("the x's row leaves the narrative", "right side" not in narrative(page))

    # Markers: drawn, moved, never removed by dragging; Clear markers removes them all.
    before = n(page, f"{DS} [data-mark]")
    x, y = mouse_at(page, f"{DS} [data-mark] circle.area")
    page.mouse.move(x, y)
    page.mouse.down()
    for step in range(1, 13):
        page.mouse.move(x - 40 * step, y - 40 * step)
    page.mouse.up()
    page.wait_for_timeout(100)
    check(f"J2: a burst dragged off the vehicle is not removed ({before}->{n(page, f'{DS} [data-mark]')})",
          n(page, f"{DS} [data-mark]") == before and len(markers_value(page)) == before)
    check("a marker records a position only", all(set(m) == {"x", "y", "r"} for m in markers_value(page)))
    x, y = mouse_at(page, f"{DS} .dv-hit path")
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + 20, y + 10)
    page.mouse.up()
    page.wait_for_timeout(100)
    check("a press on the vehicle draws a new marker", n(page, f"{DS} [data-mark]") == before + 1
          and len(markers_value(page)) == before + 1)
    kept = impacts_value(page)
    click(page, "[data-damage-clear-markers]")
    check("Clear markers removes every marker", n(page, f"{DS} [data-mark]") == 0 and markers_value(page) == [])
    check("Clear markers leaves the impacts", impacts_value(page) == kept and n(page, ROW) == 3)

    # The 760 fold: a captioned card, the Note across it, the x on the Impact line.
    page.set_viewport_size({"width": 760, "height": 1000})
    go(page, "damage-apart-edit")
    fold = frame_eval(page, f"(() => {{ const r = d.querySelector({json.dumps(ROW)}); const c = [...r.children].map(e => e.getBoundingClientRect()); "
                            "const note = r.querySelector('[data-caption=\"Note\"]').getBoundingClientRect(); "
                            "return {caption: w.getComputedStyle(r.querySelector('.fc'), '::before').content, noteWide: note.width > r.getBoundingClientRect().width * 0.8, "
                            "clearTop: Math.abs(c[4].top - c[0].top) < 12}; })()")
    check(f"760: a row folds into a captioned card {fold}", fold["caption"] == '"Severity"' and fold["noteWide"] and fold["clearTop"])
    page.set_viewport_size({"width": 1580, "height": 1000})

    # No impact: the section says so; the report skips Nature of Incident and is not blocked.
    go(page, "damage-none-read")
    check("none: No damage recorded.", shown(page, "[data-impacts-empty]")
          and frame_eval(page, "d.querySelector('[data-impacts-empty]').textContent") == "No damage recorded.")
    check("none: the captions are hidden", not shown(page, "[data-impacts-head]"))
    check("none: the narrative reads Not recorded", narrative(page) == "Not recorded")
    go(page, "wording-none")
    check("G: no Nature of Incident block", not q(page, '[data-wording-block="nature"]'))
    check("G: no Nature of Incident tick", not q(page, '[data-wording-toggle="nature"]'))
    check("G: no impact blocker", not q(page, '[data-report-blocker="damage"]'))
    go(page, "wording-apart")
    nature = frame_eval(page, "(() => { const b = d.querySelector('[data-wording-block=\"nature\"]'); "
                              "const t = b && b.querySelector('textarea[data-wording-text]'); return t ? t.value : (b ? b.innerText : ''); })()")
    check(f"A: Nature of Incident is a sentence for each impact, one to a line {nature[:60]!r}", APART in nature)


def main() -> None:
    shots_wanted = "--no-shots" not in sys.argv
    shots: list[dict] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--allow-file-access-from-files"], executable_path=CHROME)
        page = browser.new_page(viewport={"width": 1580, "height": 1000}, reduced_motion="reduce")
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto(PAGE + "?strip=0")
        page.wait_for_function("window.__mockReady === true", timeout=120000)
        keys = page.evaluate("window.__mock.states")
        for key in keys:
            errors.clear()
            go(page, key)
            check(f"{key}: no page error {errors[:2]}", not errors)
            check(f"{key}: renders the Damage section", q(page, DS))
        errors.clear()
        damage_checks(page)
        check(f"checks: no page or console error {errors[:2]}", not errors)

        if shots_wanted:
            SHOTS.mkdir(exist_ok=True)
            for old in SHOTS.glob("*.png"):
                old.unlink()
            for key in keys:
                for width, height in VIEWPORTS:
                    page.set_viewport_size({"width": width, "height": height})
                    go(page, key)
                    page.wait_for_timeout(250)
                    name = f"{key}-routed-{width}.png"
                    page.screenshot(path=str(SHOTS / name))
                    shots.append({"shot": name, "state": key, "viewport": f"{width}x{height}"})
                    page.evaluate("window.__mock.expand(true)")
                    sel = WP if key.startswith("wording") else DS
                    box = frame_eval(page, f"(() => {{ const r = d.querySelector({json.dumps(sel)}).getBoundingClientRect(); "
                                           "return [r.x, r.y + d.documentElement.scrollTop, r.width, r.height]; })()")
                    crop = f"{key}-routed-{width}-panel.png"
                    page.screenshot(path=str(SHOTS / crop), full_page=True,
                                    clip={"x": box[0], "y": box[1], "width": box[2], "height": box[3]})
                    shots.append({"shot": crop, "state": key, "viewport": f"{width} panel crop"})
                    if width == 1580:
                        full = f"{key}-routed-full.png"
                        page.screenshot(path=str(SHOTS / full), full_page=True)
                        shots.append({"shot": full, "state": key, "viewport": "1580 whole page"})
                    page.evaluate("window.__mock.expand(false)")
        browser.close()

    result = {"fail": fail, "okCount": len(ok)}
    if shots_wanted:
        (SHOTS / "verification.json").write_text(json.dumps(
            {"checkedAtUtc": datetime.now(timezone.utc).isoformat(), "result": result, "shots": shots}, indent=2),
            encoding="utf-8")
    print("RESULT " + json.dumps(result))
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
