"""Conformance check and screenshots for conformance/pegasus_v47_routed.html.

The Stage 1 self-check (../build/check-v47.py) run against the implementation: every state is
the routed Case page Pegasus renders, with the implementation's own CSS and JS and no mockup
patches or script corrections. The Today-only checks (live before v47) are dropped, and the
Skip impacts hook is the implementation's class, which the editing tick and the reading tick
share. Shots take the number of the Stage 1 Proposal shot they compare with.

Run: python -X utf8 conformance/check-conformance.py [--no-shots]
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
ROOT = HERE  # v47_planning/conformance/
SHOTS = ROOT / "shots"
MOCK = (ROOT / "pegasus_v47_routed.html").resolve().as_uri()
CHROME = next(iter(sorted(glob.glob(os.path.expandvars(
    r"%LOCALAPPDATA%\ms-playwright\chromium-*\chrome-win64\chrome.exe")), reverse=True)), None)
VIEWPORTS = [(1580, 1000), (1440, 900), (760, 1000)]
DS = "#section-damage"
WP = "#section-report [data-report-wording]"
SKIP = "#section-damage .impact-entry-skip"
ROW = "#section-damage [data-impacts-rows] [data-impact-row]"
NARR = "#section-damage [data-damage-narrative]"
TWO = ["The vehicle has suffered moderate collision/impact damage to the left side.",
       "The vehicle has suffered moderate collision/impact damage to the rear."]


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


def next_label(page: Page) -> str:
    return text_in(page, "[data-next-step] [data-next-label]").strip()


def impacts_listed(page: Page) -> bool:
    return frame_eval(page, "[...d.querySelectorAll('li.blocker')].some(li => "
                            "(li.querySelector('.blocker-name, a, span') || li).innerText.trim() === 'Impacts')")


def skip_checked(page: Page) -> bool:
    return frame_eval(page, f"!!(d.querySelector({json.dumps(SKIP + ' input[type=checkbox]')}) || {{}}).checked")


def lines(page: Page) -> list[str]:
    return frame_eval(page, f"[...d.querySelectorAll({json.dumps(NARR + ' .fv-line')})].map(e => e.innerText.trim())")


def line_gap(page: Page) -> float:
    """The space between the narrative's first two lines, in line heights."""
    return frame_eval(page, f"(() => {{ const l = d.querySelectorAll({json.dumps(NARR + ' .fv-line')}); "
                            "if (l.length < 2) return 0; const a = l[0].getBoundingClientRect(); "
                            "const b = l[1].getBoundingClientRect(); "
                            "return (b.top - a.bottom) / parseFloat(w.getComputedStyle(l[0]).lineHeight); })()")


def choose(page: Page, selector: str, value: str, index: int = 0) -> None:
    frame_eval(page, f"(() => {{ const e = d.querySelectorAll({json.dumps(selector)})[{index}]; e.value = {json.dumps(value)}; "
                     "e.dispatchEvent(new Event('change', {bubbles: true})); })()")
    page.wait_for_timeout(60)


def left(page: Page, selector: str) -> float:
    return frame_eval(page, f"(d.querySelector({json.dumps(selector)}) || {{getBoundingClientRect: () => ({{x: -1}})}})"
                            ".getBoundingClientRect().x")


def damage_checks(page: Page) -> None:
    # A: the readiness item where there is no complete impact and no skip.
    for key in ("none-read", "none-edit", "partial-read", "partial-edit"):
        go(page, key, "today")
        check(f"{key}: the next step is Impacts", next_label(page) == "Impacts")
        check(f"{key}: the step goes to Damage",
              frame_eval(page, "(d.querySelector('[data-next-step] a') || {}).getAttribute?.('data-section-jump')") == "damage")
        check(f"{key}: Impacts is in the outstanding list", impacts_listed(page))
        check(f"{key}: the impacts block is the cell the jump outlines",
              q(page, '#section-damage [data-impacts][data-field="assessment.impacts"]'))
    for key in ("skipped-read", "skipped-edit", "two-read", "two-edit"):
        go(page, key, "today")
        check(f"{key}: no Impacts step", next_label(page) != "Impacts")
        check(f"{key}: no Impacts blocker", not impacts_listed(page))

    # C: reading, the static tick in place.
    go(page, "none-read", "today")
    check("none-read: a static Skip impacts, off",
          frame_eval(page, f"(d.querySelector({json.dumps(SKIP)}) || {{}}).dataset?.on") == "false")
    check("none-read: no checkbox while reading", not q(page, SKIP + " input"))
    check("none-read: the tick reads Skip impacts", text_in(page, SKIP).strip() == "Skip impacts")
    read_x = left(page, SKIP)
    go(page, "skipped-read", "today")
    check("skipped-read: a static Skip impacts, on, with its check",
          frame_eval(page, f"d.querySelector({json.dumps(SKIP)}).dataset.on") == "true" and q(page, SKIP + " .tick .icon"))
    check("skipped-read: no Impacts row", n(page, ROW) == 0)
    go(page, "partial-read", "today")
    check("partial-read: no Skip impacts beside a row", not q(page, SKIP))
    go(page, "two-read", "today")
    check("two-read: no Skip impacts beside rows", not q(page, SKIP))

    # B: editing, offered only while no row exists.
    go(page, "none-edit", "today")
    check("none-edit: Skip impacts shown, off", shown(page, SKIP) and not skip_checked(page))
    check("none-edit: the tick posts the skip field",
          q(page, SKIP + ' input[type=checkbox][name="assessmentFields[assessment.impacts_skipped]"][value="true"]'))
    edge = left(page, "#section-damage [data-field='damage.unrelated']")
    check("none-edit: Add impact on the facts' left edge", abs(left(page, "#section-damage [data-impacts-add]") - edge) < 2)
    check("none-edit: No damage recorded. on the same edge", abs(left(page, "#section-damage [data-impacts-empty]") - edge) < 2)
    check("none-read: the reading tick on the same edge", abs(read_x - edge) < 2)
    ADD = "#section-damage [data-impacts-add]"
    check("none-edit: Add impact enabled while unticked", not frame_eval(page, f"d.querySelector({json.dumps(ADD)}).disabled"))
    click(page, SKIP + " input")
    check("none-edit: ticking it", skip_checked(page))
    check("none-edit: ticking it greys out Add impact", frame_eval(page, f"d.querySelector({json.dumps(ADD)}).disabled"))
    click(page, ADD)
    check("none-edit: a greyed Add impact adds no row", n(page, ROW) == 0)
    click(page, SKIP + " input")
    check("none-edit: unticking enables Add impact", not frame_eval(page, f"d.querySelector({json.dumps(ADD)}).disabled"))
    click(page, ADD)
    check("none-edit: Add impact adds a row", n(page, ROW) == 1)
    check("none-edit: Add impact hides Skip impacts", not shown(page, SKIP))
    click(page, ROW + " [data-impact-clear]")
    check("none-edit: clearing the last row offers Skip impacts again", shown(page, SKIP))
    check("none-edit: and the empty state is back on the left edge",
          abs(left(page, "#section-damage [data-impacts-add]") - edge) < 2)
    check("none-edit: offered again unticked", not skip_checked(page))
    go(page, "skipped-edit", "today")
    check("skipped-edit: Skip impacts shown, ticked", shown(page, SKIP) and skip_checked(page))
    check("skipped-edit: Add impact greyed out",
          frame_eval(page, "d.querySelector('#section-damage [data-impacts-add]').disabled"))
    click(page, SKIP + " input")
    check("skipped-edit: unticking enables Add impact",
          not frame_eval(page, "d.querySelector('#section-damage [data-impacts-add]').disabled"))
    go(page, "partial-edit", "today")
    check("partial-edit: Skip impacts not offered beside a row", q(page, SKIP) and not shown(page, SKIP))
    click(page, ROW + " [data-impact-clear]")
    check("partial-edit: clearing the row offers Skip impacts", shown(page, SKIP))
    go(page, "two-edit", "today")
    check("two-edit: Skip impacts not offered beside rows", q(page, SKIP) and not shown(page, SKIP))

    # G: a line's space between the narrative's sentences, read and as it recomposes.
    go(page, "two-read", "today")
    check("two-read: one block per sentence", lines(page) == TWO)
    gap = line_gap(page)
    check(f"two-read: a line's space between them ({gap:.2f} line heights)", 0.9 <= gap <= 1.2)
    go(page, "two-edit", "today")
    check("two-edit: one block per sentence", lines(page) == TWO)
    choose(page, ROW + " [data-impact-location]", "front")
    check("two-edit: recomposed as blocks", lines(page) == [TWO[0].replace("left side", "front"), TWO[1]])
    check("two-edit: still spaced", 0.9 <= line_gap(page) <= 1.2)
    click(page, ROW + " [data-impact-clear]")
    check("two-edit: one sentence, one block", len(lines(page)) == 1)
    click(page, ROW + " [data-impact-clear]")
    check("two-edit: no impact reads the absent mark", text_in(page, NARR).strip() == "Not recorded"
          or text_in(page, NARR).strip() == "—")
    check("two-edit: clearing the last row offers Skip impacts", shown(page, SKIP))


def layout_checks(page: Page) -> None:
    page.set_viewport_size({"width": 760, "height": 1000})
    go(page, "none-edit", "today")
    check("760: Skip impacts shown", shown(page, SKIP))
    inside = frame_eval(page, f"(() => {{ const r = d.querySelector({json.dumps(SKIP)}).getBoundingClientRect(); "
                              "return r.right <= d.documentElement.clientWidth; })()")
    check("760: Skip impacts inside the page", inside)
    go(page, "none-read", "today")
    check("760: the static tick shown", shown(page, SKIP))
    page.set_viewport_size({"width": 1580, "height": 1000})
    go(page, "none-edit", "today")
    same_line = frame_eval(page, f"(() => {{ const a = d.querySelector('#section-damage [data-impacts-add]').getBoundingClientRect(); "
                                 f"const t = d.querySelector({json.dumps(SKIP)}).getBoundingClientRect(); "
                                 "return Math.abs((a.top + a.bottom) / 2 - (t.top + t.bottom) / 2) < 3; })()")
    check("1580: Skip impacts on Add impact's line", same_line)
    go(page, "two-edit", "today")
    add_x = left(page, "#section-damage [data-impacts-add]")
    sev_x = left(page, ROW + " [data-caption='Severity']")
    check("1580: with rows, Add impact stays under Severity as live", abs(add_x - sev_x) < 2)


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
            for mode in ("today",):
                errors.clear()
                go(page, key, mode)
                check(f"{key} ({mode}): no page error {errors[:2]}", not errors)
                check(f"{key} ({mode}): renders the Damage section", q(page, DS))
        errors.clear()
        damage_checks(page)
        layout_checks(page)
        check(f"checks: no page or console error {errors[:2]}", not errors)

        if shots_wanted:
            SHOTS.mkdir(exist_ok=True)
            for old in SHOTS.glob("*.png"):
                old.unlink()
            number = 0
            plan = [(key, "today") for key in keys]
            for key, mode in plan:
                # The Stage 1 Proposal shot of the same state: 002, 004 …
                number = 2 * (keys.index(key) + 1)
                for width, height in VIEWPORTS:
                    errors.clear()
                    page.set_viewport_size({"width": width, "height": height})
                    go(page, key, mode)
                    page.wait_for_timeout(250)
                    name = f"{number:03d}-{key}-routed-{width}.png"
                    page.screenshot(path=str(SHOTS / name))
                    shots.append({"shot": name, "state": key, "mode": mode, "viewport": f"{width}x{height}"})
                    page.evaluate("window.__mock.expand(true)")
                    sel = DS
                    box = frame_eval(page, f"(() => {{ const r = d.querySelector({json.dumps(sel)}).getBoundingClientRect(); "
                                           "return [r.x, r.y + d.documentElement.scrollTop, r.width, r.height]; })()")
                    crop = f"{number:03d}-{key}-routed-{width}-panel.png"
                    page.screenshot(path=str(SHOTS / crop), full_page=True,
                                    clip={"x": box[0], "y": box[1], "width": box[2], "height": box[3]})
                    shots.append({"shot": crop, "state": key, "mode": mode, "viewport": f"{width} panel crop"})
                    if width == 1580:
                        full = f"{number:03d}-{key}-routed-full.png"
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
