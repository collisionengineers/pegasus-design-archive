"""Side-by-side conformance for v45: the mockup's Proposal crop beside the implemented page's.

For each state and width, the implemented page (pegasus_v45_conformance.html, built from
captures of task/report-wording-settings) is shot the way check-v45.py shot the mockup, and
the panel crop is pasted beside the mockup's crop of the same state, mode proposal, width:
  ../shots/NNN-<state>-<width>-side-by-side.png   (left: mockup, right: implemented)
It also asserts the behaviours the notes promised on the implemented page.

Prints RESULT {"fail":[...],"okCount":N}. Run from v45_planning/conformance/:
  python -X utf8 build/build-v45.py; python -X utf8 build/conformance-v45.py
"""
from __future__ import annotations

import glob
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MOCK_SHOTS = ROOT.parent / "shots"
SHOTS = ROOT / "shots"
PAGE = (ROOT / "pegasus_v45_conformance.html").resolve().as_uri()
CHROME = next(iter(sorted(glob.glob(os.path.expandvars(
    r"%LOCALAPPDATA%\ms-playwright\chromium-*\chrome-win64\chrome.exe")), reverse=True)), None)
VIEWPORTS = [(1580, 1000), (1440, 900), (760, 1000)]
# The mockup's shot numbers per state (proposal), from ../shots/verification.json.
MOCK_NUMBER = {
    "case-read": "002", "case-edit": "004", "case-switches-read": "006", "case-switches-edit": "008",
    "case-court-off-read": "010", "case-court-off-edit": "012", "valuation-read": "018", "valuation-edit": "020",
}
RS = "#section-report"
WP = f"{RS} [data-report-wording]"
SET = f"{WP} [data-wording-settings]"

ok: list[str] = []
fail: list[str] = []


def check(name: str, condition: bool) -> None:
    (ok if condition else fail).append(name)


def main() -> None:
    SHOTS.mkdir(exist_ok=True)
    for old in SHOTS.glob("*.png"):
        old.unlink()
    pairs: list[dict] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--allow-file-access-from-files"], executable_path=CHROME)
        page = browser.new_page(viewport={"width": 1580, "height": 1000}, reduced_motion="reduce")
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto(PAGE + "?strip=0")
        page.wait_for_function("window.__mockReady === true", timeout=120000)

        def go(key: str) -> None:
            page.evaluate("k => window.__mock.go(k, 'today')", key)
            page.wait_for_timeout(250)

        def ev(script: str):
            return page.evaluate(f"() => {{ const d = window.__mock.doc(); return ({script}); }}")

        def shown(selector: str) -> bool:
            return ev(f"(() => {{ const e = d.querySelector({json.dumps(selector)}); "
                      "return !!e && !e.closest('[hidden]') && e.getClientRects().length > 0; })()")

        # Behaviours on the implemented page.
        go("case-edit")
        labels = ev(f"[...d.querySelectorAll({json.dumps(SET + ' .choice')})].map(c => c.lastElementChild.textContent.trim())")
        check(f"edit: settings, blocks first and the three switches last {labels}",
              labels[-3:] == ["Disclose guide source", "FAO The Court", "Include statement of truth"]
              and "Valuation commentary" in labels and "Unrelated damage" in labels)
        check("edit: no On the report row on Valuation", ev("!d.querySelector('[data-field=\"report-content\"]')"))
        check("edit: no statement sub-panel, no separate commentary field",
              ev("!d.querySelector('[data-report-statement]') && !d.querySelector('[data-field=\"report.valuation_commentary_text\"].fc')"))
        check("edit: no On report tick on a block", ev(f"!d.querySelector({json.dumps(WP + ' .wb .wb-tools .choice')})"))
        check("edit: commentary and unrelated hidden while off",
              not shown(f'{WP} [data-wording-block="commentary"]') and not shown(f'{WP} [data-wording-block="unrelated"]'))
        ev(f"d.querySelector({json.dumps(SET + ' [data-wording-toggle=commentary]')}).click()")
        page.wait_for_timeout(60)
        check("edit: ticking Valuation commentary draws its block", shown(f'{WP} [data-wording-block="commentary"]'))
        ev(f"d.querySelector({json.dumps(SET + ' [data-wording-toggle=statement]')}).click()")
        page.wait_for_timeout(60)
        check("edit: unticking the statement hides paragraphs 1-2 only",
              not shown(f"{WP} [data-sot-court]") and "Parts prices" in ev(f"d.querySelector({json.dumps(WP + ' [data-wording-fixed]')}).innerText"))
        before = len(labels)
        ev(f"d.querySelector({json.dumps(WP + ' [data-wording-new]')}).click()")
        page.wait_for_timeout(80)
        after = ev(f"[...d.querySelectorAll({json.dumps(SET + ' .choice')})].map(c => c.lastElementChild.textContent.trim())")
        check(f"edit: New paragraph adds its tick before the three switches {after[-4:]}",
              len(after) == before + 1 and after[-4] == "New paragraph")
        go("case-read")
        check("read: settings are static ticks", ev(f"d.querySelectorAll({json.dumps(SET + ' .choice.is-static')}).length >= 8"))
        go("case-court-off-read")
        check("court off read: FAO tick off, paragraphs 1-2 hidden",
              ev(f"d.querySelector({json.dumps(SET + ' [data-wording-toggle=fao]')}).dataset.on") == "false"
              and not shown(f"{WP} [data-sot-court]"))
        check(f"behaviours: no page or console error {errors[:2]}", not errors)

        # Side by side.
        for key, number in MOCK_NUMBER.items():
            target = "#section-valuation" if key.startswith("valuation") else WP
            for width, height in VIEWPORTS:
                errors.clear()
                page.set_viewport_size({"width": width, "height": height})
                go(key)
                page.evaluate("window.__mock.expand(true)")
                box = ev(f"(() => {{ const r = d.querySelector({json.dumps(target)}).getBoundingClientRect(); "
                         "return [r.x, r.y + d.documentElement.scrollTop, r.width, r.height]; })()")
                built = SHOTS / f"{number}-{key}-{width}-implemented.png"
                page.screenshot(path=str(built), full_page=True,
                                clip={"x": box[0], "y": box[1], "width": box[2], "height": box[3]})
                page.evaluate("window.__mock.expand(false)")
                check(f"{key} {width}: no console error {errors[:2]}", not errors)
                mock = MOCK_SHOTS / f"{number}-{key}-proposal-{width}-panel.png"
                if not mock.exists():
                    check(f"{key} {width}: mockup shot {mock.name} exists", False)
                    continue
                left, right = Image.open(mock), Image.open(built)
                gap, head = 24, 28
                sheet = Image.new("RGB", (left.width + right.width + gap, max(left.height, right.height) + head), "white")
                draw = ImageDraw.Draw(sheet)
                draw.text((4, 6), f"Mockup {mock.name}", fill="black")
                draw.text((left.width + gap + 4, 6), f"Implemented {built.name}", fill="black")
                sheet.paste(left, (0, head))
                sheet.paste(right, (left.width + gap, head))
                out = SHOTS / f"{number}-{key}-{width}-side-by-side.png"
                sheet.save(out)
                pairs.append({"state": key, "width": width, "mockup": mock.name, "implemented": built.name,
                              "sideBySide": out.name, "mockupSize": list(left.size), "implementedSize": list(right.size)})
        browser.close()

    result = {"fail": fail, "okCount": len(ok)}
    (SHOTS / "conformance.json").write_text(json.dumps({
        "checkedAtUtc": datetime.now(timezone.utc).isoformat(), "result": result, "pairs": pairs}, indent=2),
        encoding="utf-8")
    print("RESULT " + json.dumps(result))
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
