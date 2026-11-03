"""Self-check and screenshots for pegasus_v46.html.

1. Every state loads in Today and in Proposal with no page or console error.
2. Every Proposal marks its changes (Diff badges).
3. Today is live (the derived cells, the marker list, the chips); the Proposal holds items
   A-K (notes/v46-notes.md §6): impact rows, their vocabularies, read/edit geometry, Add and
   Clear, a marker dragged off the vehicle removed, and the Nature of Incident composition.
4. Screenshots of every state at 1580x1000, 1440x900 and 760x1000, a crop of the Damage
   section (or the Report wording panel) at each width, and a 1580 whole page, in Today and
   Proposal, into ../shots/ with verification.json.

Prints RESULT {"fail":[...],"okCount":N}. Run: python -X utf8 build/check-v46.py [--no-shots]
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
ROOT = HERE.parent  # v46_planning/
SHOTS = ROOT / "shots"
MOCK = (ROOT / "pegasus_v46.html").resolve().as_uri()
CHROME = next(iter(sorted(glob.glob(os.path.expandvars(
    r"%LOCALAPPDATA%\ms-playwright\chromium-*\chrome-win64\chrome.exe")), reverse=True)), None)
VIEWPORTS = [(1580, 1000), (1440, 900), (760, 1000)]
DS = "#section-damage"
WP = "#section-report [data-report-wording]"
ROW = "[data-v46-impact-row]"
APART = ("The vehicle has suffered light collision/impact damage to the front.\n"
         "The vehicle has suffered moderate collision/impact damage to the right side.\n"
         "The vehicle has suffered moderate to heavy collision/impact damage to the rear.")

ok: list[str] = []
fail: list[str] = []


def check(name: str, condition: bool) -> None:
    (ok if condition else fail).append(name)


def go(page: Page, key: str, mode: str, **options) -> None:
    page.evaluate("([k, m, o]) => window.__mock.go(k, m, o)", [key, mode, options])
    page.wait_for_timeout(150)


def frame_eval(page: Page, script: str):
    return page.evaluate(f"() => {{ const d = window.__mock.doc(); const w = window.__mock.win(); return ({script}); }}")


def q(page: Page, selector: str) -> bool:
    return frame_eval(page, f"!!d.querySelector({json.dumps(selector)})")


def n(page: Page, selector: str) -> int:
    return frame_eval(page, f"d.querySelectorAll({json.dumps(selector)}).length")


def text_in(page: Page, selector: str) -> str:
    return frame_eval(page, f"(d.querySelector({json.dumps(selector)}) || {{innerText: ''}}).innerText")


def shown(page: Page, selector: str) -> bool:
    """The first match takes space and is visible."""
    return frame_eval(page, f"(() => {{ const e = d.querySelector({json.dumps(selector)}); if (!e) return false; "
                            "const s = w.getComputedStyle(e); const r = e.getBoundingClientRect(); "
                            "return s.display !== 'none' && s.visibility !== 'hidden' && !e.hidden && r.width > 0; })()")


def click(page: Page, selector: str, index: int = 0) -> None:
    frame_eval(page, f"d.querySelectorAll({json.dumps(selector)})[{index}].click()")
    page.wait_for_timeout(60)


def nature_text(page: Page) -> str:
    return frame_eval(page, "(() => { const b = d.querySelector('[data-wording-block=\"nature\"]'); if (!b) return ''; "
                            "const t = b.querySelector('textarea[data-wording-text]'); "
                            "return t ? t.value : b.innerText; })()")


def drag_mark_off(page: Page) -> tuple[int, int]:
    """Drags the first burst far off the vehicle; returns the mark count before and after."""
    before = n(page, f"{DS} [data-mark]")
    box = frame_eval(page, "(() => { const g = d.querySelector('#section-damage [data-mark] circle.area'); "
                           "g.scrollIntoView({block: 'center'}); const r = g.getBoundingClientRect(); "
                           "const f = window.frameElement; return [r.x + r.width / 2, r.y + r.height / 2]; })()")
    origin = page.evaluate("(() => { const r = document.getElementById('mock-frame').getBoundingClientRect(); return [r.x, r.y]; })()")
    x, y = origin[0] + box[0], origin[1] + box[1]
    page.mouse.move(x, y)
    page.mouse.down()
    for step in range(1, 13):
        page.mouse.move(x - 40 * step, y - 40 * step)
    page.mouse.up()
    page.wait_for_timeout(100)
    return before, n(page, f"{DS} [data-mark]")


def damage_checks(page: Page) -> None:
    # Today is live: PR 1862's derived cells, the marker list, the chips.
    go(page, "damage-apart-read", "today")
    check("today apart: derived location reads Multiple", text_in(page, "[data-damage-location]").strip() == "Multiple")
    check("today apart: derived severity reads Moderate to heavy",
          text_in(page, "[data-damage-severity]").strip() == "Moderate to heavy")
    check("today apart: three marker rows", n(page, "[data-damage-row]") == 3)
    check("today apart: three bursts", n(page, f"{DS} [data-mark]") == 3)
    check("today apart: the three other-area chips", n(page, "[data-damage-area]") == 3)
    check("today: no impact rows", n(page, ROW) == 0)
    go(page, "damage-two-read", "today")
    check("today two: live derives Multiple for two damages apart",
          text_in(page, "[data-damage-location]").strip() == "Multiple")
    go(page, "damage-none-read", "today")
    check("today none: location Not recorded", text_in(page, "[data-damage-location]").strip() == "Not recorded")

    expected = {"two": 2, "apart": 3, "none": 0}  # damage-apart-edit-under is checked below
    for fixture, count in expected.items():
        for mode_name in ("read", "edit"):
            key = f"damage-{fixture}-{mode_name}"
            go(page, key, "proposal")
            check(f"{key}: {count} impact rows", n(page, ROW) == count)
            check(f"{key}: no derived cells", not q(page, "[data-damage-location]") and not q(page, "[data-damage-severity]"))
            check(f"{key}: no marker list", not q(page, "[data-damage-impact-list]"))
            check(f"{key}: no other-area chips", not q(page, "[data-damage-area]"))
            check(f"{key}: no readout", not q(page, "[data-damage-readout]"))
            check(f"{key}: the plan stays", q(page, f"{DS} svg.damage-diagram"))
            check(f"{key}: captions only when an impact is recorded",
                  shown(page, "[data-v46-impact-head]") == (count > 0))
            if count:
                widths = frame_eval(page, f"[...d.querySelector('{ROW}').children].map(c => Math.round(c.getBoundingClientRect().width)).join()")
                check(f"{key}: one value per line for Location", frame_eval(
                    page, f"d.querySelectorAll('{ROW} .fc')[1].getBoundingClientRect().height") < 60)
            check(f"{key}: empty state only when nothing is recorded",
                  shown(page, "[data-v46-impact-empty]") == (count == 0))
            if count:
                check(f"{key}: row label Impact", text_in(page, f"{ROW} .impact-entry-label").strip() == "Impact")
                locations = frame_eval(page, f"[...d.querySelectorAll('{ROW} [data-v46-impact-location] option')]"
                                             ".filter(o => o.value).slice(0, 11).map(o => o.textContent)")
                check(f"{key}: Location is the 11 recorded areas", locations == [
                    "Front", "LH Front", "RH Front", "LH Side", "RH Side", "Rear", "LH Rear", "RH Rear",
                    "Underside", "Interior", "Mechanical"])
                check(f"{key}: no Multiple location", "Multiple" not in text_in(page, "[data-v46-impacts]"))
                check(f"{key}: no Type box (round 2)", not q(page, "[data-v46-impact-type]")
                      and "Type" not in text_in(page, ".impact-entry-head"))
                severities = frame_eval(page, f"[...d.querySelector('{ROW} [data-v46-impact-severity]').options]"
                                              ".filter(o => o.value).map(o => o.textContent)")
                check(f"{key}: five severities", severities == [
                    "Light", "Light to moderate", "Moderate", "Moderate to heavy", "Heavy"])
                note = frame_eval(page, f"d.querySelector('{ROW} [data-v46-impact-note]').maxLength")
                check(f"{key}: note holds 200 characters", note == 200)
            editing = mode_name == "edit"
            if count:
                check(f"{key}: values shown {'never' if editing else 'always'}",
                      shown(page, f"{ROW} .fc .fv") != editing)
                check(f"{key}: controls shown only while editing", shown(page, f"{ROW} select.fi") == editing)
                check(f"{key}: Clear shown only while editing", shown(page, "[data-v46-impact-clear]") == editing)
                geometry = frame_eval(page, f"(() => {{ const c = d.querySelector('{ROW} [data-v46-impact-clear]'); "
                                            "return c.getBoundingClientRect().width > 0; })()")
                check(f"{key}: the Clear column keeps its place in both modes", geometry)
            check(f"{key}: Add impact only while editing", shown(page, "[data-v46-impact-add]") == editing)

    # Flows: add, fill, clear.
    go(page, "damage-apart-edit", "proposal")
    click(page, "[data-v46-impact-add]")
    check("add: a fourth row", n(page, ROW) == 4)
    check("add: the new row's severity and location are blank",
          frame_eval(page, f"(() => {{ const r = d.querySelectorAll('{ROW}')[3]; return r.querySelector('[data-v46-impact-severity]').value === '' "
                           "&& r.querySelector('[data-v46-impact-location]').value === ''; })()"))
    frame_eval(page, f"(() => {{ const s = d.querySelectorAll('{ROW}')[3].querySelector('[data-v46-impact-location]'); "
                     "s.value = 'underside'; s.dispatchEvent(new Event('change', {bubbles: true})); })()")
    check("fill: the row's value follows its control",
          frame_eval(page, f"d.querySelectorAll('{ROW}')[3].querySelectorAll('.fv')[1].textContent") == "Underside")
    check("narrative: a row without a severity adds no sentence",
          text_in(page, "[data-damage-narrative]").strip() == APART)
    frame_eval(page, f"(() => {{ const s = d.querySelectorAll('{ROW}')[3].querySelector('[data-v46-impact-severity]'); "
                     "s.value = 'heavy'; s.dispatchEvent(new Event('change', {bubbles: true})); })()")
    check("narrative: completing the row adds its own sentence", text_in(page, "[data-damage-narrative]").strip() ==
          APART + "\nThe vehicle has suffered heavy collision/impact damage to the underside.")
    check("nature: the report block follows",
          nature_text(page) == APART + "\nThe vehicle has suffered heavy collision/impact damage to the underside.")
    check("clear: the × is labelled Clear", frame_eval(
        page, "(() => { const b = d.querySelector('[data-v46-impact-clear]'); return b.textContent.trim() === '×' && b.getAttribute('aria-label') === 'Clear'; })()"))
    click(page, "[data-v46-impact-clear]", 0)
    check("narrative: clearing the first impact drops its sentence", text_in(page, "[data-damage-narrative]").startswith(
        "The vehicle has suffered moderate collision/impact damage to the right side.\n"))
    check("clear: removes the row", n(page, ROW) == 3)
    check("clear: rows renumber", frame_eval(page, f"[...d.querySelectorAll('{ROW}')].map(r => r.getAttribute('data-v46-impact-row')).join()") == "0,1,2")
    go(page, "damage-two-edit", "proposal")
    click(page, "[data-v46-impact-clear]", 0)
    click(page, "[data-v46-impact-clear]", 0)
    check("clear all: no rows", n(page, ROW) == 0)
    check("clear all: the empty state shows", shown(page, "[data-v46-impact-empty]"))
    check("clear all: the captions hide", not shown(page, "[data-v46-impact-head]"))
    check("narrative: nothing recorded reads Not recorded", text_in(page, "[data-damage-narrative]").strip() == "Not recorded")
    go(page, "damage-none-edit", "proposal")
    click(page, "[data-v46-impact-add]")
    check("none: Add impact gives the first row", n(page, ROW) == 1 and not shown(page, "[data-v46-impact-empty]"))

    # J: a marker dragged off the vehicle. Today puts it back; Proposal removes it.
    go(page, "damage-apart-edit", "today")
    before, after = drag_mark_off(page)
    check(f"J today: a burst dragged off the vehicle returns ({before}->{after})", before == 3 and after == 3)
    go(page, "damage-apart-edit", "proposal")
    before, after = drag_mark_off(page)
    check(f"J proposal: a burst dragged off the vehicle is removed ({before}->{after})", before == 3 and after == 2)
    check("J proposal: removing a burst leaves the impacts alone", n(page, ROW) == 3)
    check("J: Clear markers is drawn while editing", shown(page, "[data-v46-clear-markers]")
          and text_in(page, "[data-v46-clear-markers]").strip() == "Clear markers")
    click(page, "[data-v46-clear-markers]")
    check("J: Clear markers removes every burst", n(page, f"{DS} [data-mark]") == 0)
    check("J: Clear markers leaves the impacts alone", n(page, ROW) == 3)
    click(page, "[data-damage-reset]")
    check("J: Reset brings the markers back", n(page, f"{DS} [data-mark]") == 3)
    go(page, "damage-apart-read", "proposal")
    check("J: no Clear markers while reading", not q(page, "[data-v46-clear-markers]"))
    go(page, "damage-apart-edit", "today")
    check("J today: live has no Clear markers", not q(page, "[data-v46-clear-markers]"))

    # A: the Nature of Incident composition.
    go(page, "wording-apart", "today")
    check("A today: live lists the following areas", "following areas" in nature_text(page))
    go(page, "wording-apart", "proposal")
    check("A: a separate sentence for each impact, in order", nature_text(page) == APART)
    # G (ruled 3 November 2026): no impact, no Nature of Incident, no impact blockers.
    go(page, "wording-none", "today")
    check("G today: live blocks the report on Impact location and severity",
          n(page, '.blocker[data-report-blocker="damage"]') == 2)
    for key in ("wording-none", "damage-none-read", "damage-none-edit"):
        go(page, key, "proposal")
        check(f"G {key}: no impact blocker", n(page, '[data-report-blocker="damage"]') == 0)
        check(f"G {key}: no Nature of Incident block", not q(page, '[data-wording-block="nature"]'))
        check(f"G {key}: no Nature of Incident tick", not q(page, '[data-wording-toggle="nature"]'))
        check(f"G {key}: the other blocks are drawn", n(page, "[data-wording-block]") >= 4)
    go(page, "wording-none", "proposal")
    click(page, "[data-v46-impact-add]")
    check("G: an empty new row skips Nature of Incident still", not q(page, '[data-wording-block="nature"]'))
    go(page, "wording-apart", "proposal")
    for _ in range(3):
        click(page, "[data-v46-impact-clear]", 0)
    check("G: clearing every impact hides the Nature of Incident block",
          not shown(page, '[data-wording-block="nature"]') and not shown(page, '[data-wording-toggle="nature"]'))
    go(page, "damage-two-read", "proposal")
    check("A read: the block reads a sentence for each impact",
          "right rear.\nThe vehicle has suffered light collision/impact damage to the rear."
          in text_in(page, '[data-wording-block="nature"]'))

    # A: the Damage section's Incident narrative reads the same composition.
    go(page, "damage-apart-read", "proposal")
    check("A: the Incident narrative reads a sentence for each impact, one to a line",
          text_in(page, "[data-damage-narrative]").strip() == APART)
    go(page, "damage-apart-read", "today")
    check("A today: the Incident narrative lists the following areas", "following areas" in text_in(page, "[data-damage-narrative]"))

    # K variant: the impacts under the plan, full width.
    go(page, "damage-apart-edit-under", "proposal")
    check("K variant: the impacts follow the workbench", frame_eval(
        page, "(() => { const w = d.querySelector('#section-damage .damage-workbench'); "
              "return !!w && w.nextElementSibling === d.querySelector('[data-v46-impacts]'); })()"))
    check("K variant: three rows", n(page, ROW) == 3)
    go(page, "damage-apart-edit", "proposal")
    check("K: the impacts stand in the facts column", q(page, ".damage-facts > [data-v46-impacts]"))

    # 760: a row folds to two columns.
    page.set_viewport_size({"width": 760, "height": 1000})
    go(page, "damage-apart-edit", "proposal")
    columns = frame_eval(page, f"w.getComputedStyle(d.querySelector('{ROW}')).gridTemplateColumns.split(' ').length")
    check("760: an impact row folds to two columns", columns == 2)
    page.set_viewport_size({"width": 1580, "height": 1000})
    go(page, "damage-apart-edit", "proposal")
    columns = frame_eval(page, f"w.getComputedStyle(d.querySelector('{ROW}')).gridTemplateColumns.split(' ').length")
    check("1580: an impact row is one line of five columns", columns == 5)
    overflow = frame_eval(page, f"(() => {{ const r = d.querySelector('{ROW}'); return r.scrollWidth <= r.clientWidth + 1; }})()")
    check("1580: the row does not overflow", overflow)


def main() -> None:
    shots_wanted = "--no-shots" not in sys.argv
    shots: list[dict] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--allow-file-access-from-files"], executable_path=CHROME)
        page = browser.new_page(viewport={"width": 1580, "height": 1000}, reduced_motion="reduce")
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto(MOCK + "?strip=0")
        page.wait_for_function("window.__mockReady === true", timeout=120000)
        keys = page.evaluate("window.__mock.states")

        for key in keys:
            meta = page.evaluate("k => window.__mock.meta(k)", key)
            for mode in ("today", "proposal"):
                errors.clear()
                go(page, key, mode)
                check(f"{key} ({mode}): no page error {errors[:2]}", not errors)
                check(f"{key} ({mode}): renders the Damage section", q(page, DS))
            if meta["hasProposal"] and meta["changes"]:
                go(page, key, "proposal", diff=True)
                check(f"{key}: proposal marks its changes", n(page, "[data-v46-change]") > 0)

        errors.clear()
        damage_checks(page)
        check(f"checks: no page or console error {errors[:2]}", not errors)

        if shots_wanted:
            SHOTS.mkdir(exist_ok=True)
            for old in SHOTS.glob("*.png"):
                old.unlink()
            number = 0
            plan = [(key, mode) for key in keys for mode in ("today", "proposal")
                    if mode == "today" or page.evaluate("k => window.__mock.meta(k).hasProposal", key)]
            for key, mode in plan:
                number += 1
                for width, height in VIEWPORTS:
                    errors.clear()
                    page.set_viewport_size({"width": width, "height": height})
                    go(page, key, mode)
                    page.wait_for_timeout(250)
                    name = f"{number:03d}-{key}-{mode}-{width}.png"
                    page.screenshot(path=str(SHOTS / name))
                    shots.append({"shot": name, "state": key, "mode": mode, "viewport": f"{width}x{height}"})
                    page.evaluate("window.__mock.expand(true)")
                    sel = WP if key.startswith("wording") else DS
                    box = frame_eval(page, f"(() => {{ const r = d.querySelector({json.dumps(sel)}).getBoundingClientRect(); "
                                           "return [r.x, r.y + d.documentElement.scrollTop, r.width, r.height]; })()")
                    crop = f"{number:03d}-{key}-{mode}-{width}-panel.png"
                    page.screenshot(path=str(SHOTS / crop), full_page=True,
                                    clip={"x": box[0], "y": box[1], "width": box[2], "height": box[3]})
                    shots.append({"shot": crop, "state": key, "mode": mode, "viewport": f"{width} panel crop"})
                    if width == 1580:
                        full = f"{number:03d}-{key}-{mode}-full.png"
                        page.screenshot(path=str(SHOTS / full), full_page=True)
                        shots.append({"shot": full, "state": key, "mode": mode, "viewport": "1580 whole page"})
                    page.evaluate("window.__mock.expand(false)")
                    check(f"shot {name}: no console error {errors[:2]}", not errors)
        browser.close()

    result = {"fail": fail, "okCount": len(ok)}
    if shots_wanted:
        (SHOTS / "verification.json").write_text(json.dumps({
            "checkedAtUtc": datetime.now(timezone.utc).isoformat(), "result": result, "shots": shots}, indent=2),
            encoding="utf-8")
    print("RESULT " + json.dumps(result))
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
