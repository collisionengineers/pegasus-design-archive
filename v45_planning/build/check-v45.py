"""Self-check and screenshots for pegasus_v45.html.

1. Every state loads in Today and in Proposal with no page or console error.
2. Every Proposal marks its changes (Diff badges).
3. The settled changes R1-R6 and items A-I (notes/v45-notes.md) hold; Today is live.
4. Screenshots of every state at 1580x1000, 1440x900 and 760x1000, a crop of the Report
   wording panel (or Valuation) at each width, and a 1580 whole page, in Today and Proposal, into
   ../shots/ with verification.json.

Prints RESULT {"fail":[...],"okCount":N}. Run: python -X utf8 build/check-v45.py [--no-shots]
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
sys.path.insert(0, str(HERE))
ROOT = HERE.parent  # v45_planning/
SHOTS = ROOT / "shots"
MOCK = (ROOT / "pegasus_v45.html").resolve().as_uri()
CHROME = next(iter(sorted(glob.glob(os.path.expandvars(
    r"%LOCALAPPDATA%\ms-playwright\chromium-*\chrome-win64\chrome.exe")), reverse=True)), None)
VIEWPORTS = [(1580, 1000), (1440, 900), (760, 1000)]
import report_checks  # noqa: E402
RS, WP, VAL = report_checks.RS, report_checks.WP, report_checks.VAL

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
                check(f"{key} ({mode}): renders the Report section", q(page, RS))
            if meta["hasProposal"] and meta["changes"]:
                go(page, key, "proposal", diff=True)
                check(f"{key}: proposal marks its changes", n(page, "[data-v45-change]") > 0)

        errors.clear()
        report_checks.run(page, go, check, q, n, text_in, frame_eval)
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
                    sel = VAL if key.startswith("valuation") else (WP if q(page, WP) else RS)
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
