"""Self-check and screenshots for pegasus_v43.html.

1. Every state loads in Today and in Proposal with no page or console error.
2. Every Proposal marks its changes (Diff badges).
3. The Case details items A-G (notes/v43-notes.md section 6) hold in read, edit, bare,
   the Claim-source-changed and the F/G variant states; Today is the live order.
4. Screenshots of every state at 1580x1000, 1440x900 and 760x1000, a crop of the Case
   details section at each width, and a 1580 whole page, in Today and Proposal, into
   ../shots/ with verification.json.

Prints RESULT {"fail":[...],"okCount":N}. Run: python -X utf8 build/check-v43.py [--no-shots]
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
ROOT = HERE.parent  # v43_planning/
SHOTS = ROOT / "shots"
MOCK = (ROOT / "pegasus_v43_conformance.html").resolve().as_uri()
CHROME = next(iter(sorted(glob.glob(os.path.expandvars(
    r"%LOCALAPPDATA%\ms-playwright\chromium-*\chrome-win64\chrome.exe")), reverse=True)), None)
VIEWPORTS = [(1580, 1000), (1440, 900), (760, 1000)]
OV = "#section-overview"
CARD = f'{OV} [data-collapse="case.overview.claim-source"]'
PRINCIPAL = f'{OV} [data-collapse="case.overview.principal-notes"]'
DOT = "·"

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


def heads(page: Page) -> list[str]:
    return frame_eval(page, f"[...d.querySelectorAll({json.dumps(OV + ' .sub-panel > h3')})].map(h => h.firstChild.textContent.trim())")


def labels(page: Page, selector: str) -> list[str]:
    return frame_eval(page, f"[...d.querySelectorAll({json.dumps(selector + ' .fc')})]"
                            ".map(f => ((f.querySelector('label, .lbl') || {}).textContent || '').trim())")


def case_checks(page: Page) -> None:
    go(page, "case-read", "today")
    check("today: live sub-panels Case, Principal, Case contact, Notes",
          heads(page) == ["Case", "Principal", "Case contact", "Notes"])
    check("today: Notes from client beside Accident circumstances", q(page, f"{OV} [data-client-notes]"))

    for key in ("case-read", "case-edit"):
        go(page, key, "proposal")
        check(f"{key}: sub-panels Case, Claim source, Principal", heads(page) == ["Case", "Claim source", "Principal"])
        check(f"{key} A: the Claim source card holds the select cell and three contact cells",
              n(page, f"{CARD} [data-claim-source-cell]") == 1 and n(page, f"{CARD} [data-claim-source-contact]") == 3)
        card_labels = labels(page, CARD)
        check(f"{key} B: the record's notes then this Case's notes close the Claim source card",
              card_labels[-2:] == ["Claim source notes", f"Claim source notes {DOT} this Case"])
        check(f"{key} C: the Principal panel holds only the two Principal cells",
              labels(page, PRINCIPAL) == ["Principal notes", f"Principal notes {DOT} this Case"])
        check(f"{key} C: the Principal panel sits below the card grid, full width",
              frame_eval(page, f"!d.querySelector({json.dumps(PRINCIPAL)}).closest('.overview-grid')"))
        check(f"{key} D: no Case contact anywhere",
              n(page, f'{OV} [data-collapse="case.overview.contact"]') == 0
              and n(page, f"{OV} [name=contactName], {OV} [name=contactEmailAddress], {OV} [name=contactPhoneNumber]") == 0
              and "Case contact" not in text_in(page, OV))
        check(f"{key} E: no Notes from client",
              n(page, f"{OV} [data-client-notes], {OV} [name=clientNotes]") == 0
              and "Notes from client" not in text_in(page, OV))
        check(f"{key} F: Accident circumstances alone at full width",
              n(page, f"{OV} [data-accident-band] .fc") == 1 and n(page, f"{OV} [data-accident-band] .fg.g2") == 0)
        check(f"{key}: no Notes band left", n(page, f"{OV} [data-notes-band]") == 0)

    go(page, "case-edit", "proposal")
    check("edit: Claim source notes · this Case is a textarea in the card", q(page, f"{CARD} textarea[name=claimSourceNotes]"))
    check("edit: Principal notes · this Case is a textarea in the Principal panel",
          q(page, f"{PRINCIPAL} textarea[name=principalNotes]"))
    check("edit: both textareas still post with the Save form",
          n(page, f"{OV} textarea[form=case-edit-form][name=claimSourceNotes], {OV} textarea[form=case-edit-form][name=principalNotes]") == 2)

    go(page, "case-read-bare", "proposal")
    check("bare read: no record-notes cells (absent when the record has none)", n(page, f"{OV} [data-record-notes]") == 0)
    check("bare read: both this-Case cells read Not recorded",
          "Not recorded" in text_in(page, CARD) and "Not recorded" in text_in(page, PRINCIPAL))

    go(page, "case-edit-bare", "proposal")
    check("bare edit: the hidden record-notes slot sits in the Claim source card",
          q(page, f'{CARD} [data-record-notes-slot="claim-source"][hidden]'))

    slot = f'{OV} [data-record-notes-slot="claim-source"]'
    for mode in ("today", "proposal"):
        go(page, "case-edit-claim-source-changed", mode)
        page.wait_for_timeout(300)
        check(f"claim source changed ({mode}): the slot shows the chosen record's notes",
              frame_eval(page, f"(() => {{ const s = d.querySelector({json.dumps(slot)}); "
                               "return !!s && !s.hidden && s.innerText.includes('Photos with every report'); })()"))
        check(f"claim source changed ({mode}): the contact inputs follow the select",
              frame_eval(page, "d.querySelector('#f-claim-source-contact-name').value") == "Lee Turner")
    check("claim source changed (proposal): the notes that follow are in the Claim source card",
          q(page, f'{CARD} [data-record-notes-slot="claim-source"]:not([hidden])'))

    go(page, "case-read-f-half", "proposal")
    check("F variant: Accident circumstances keeps its half-width cell",
          n(page, f"{OV} [data-accident-band] .fg.g2") == 1 and n(page, f"{OV} [data-accident-band] .fc") == 1)

    go(page, "case-read-bare", "proposal")
    check("G proposed: with no Principal record notes, this Case's cell keeps its half-width place",
          n(page, f"{PRINCIPAL} .fc.span2") == 0 and n(page, f"{PRINCIPAL} .fc") == 1)
    go(page, "case-read-bare-g-span", "proposal")
    check("G variant: this Case's Principal notes span the panel",
          n(page, f"{PRINCIPAL} .fc.span2") == 1
          and frame_eval(page, f"d.querySelector({json.dumps(PRINCIPAL + ' .fc')}).getBoundingClientRect().width "
                               f"> d.querySelector({json.dumps(PRINCIPAL)}).getBoundingClientRect().width * 0.8"))


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
                check(f"{key} ({mode}): renders the Case details section", q(page, OV))
            if meta["hasProposal"] and meta["changes"]:
                go(page, key, "proposal", diff=True)
                check(f"{key}: proposal marks its changes", n(page, "[data-v43-change]") > 0)

        errors.clear()
        case_checks(page)
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
                    box = frame_eval(page, f"(() => {{ const r = d.querySelector({json.dumps(OV)}).getBoundingClientRect(); "
                                           "return [r.x, r.y + d.documentElement.scrollTop, r.width, r.height]; })()")
                    crop = f"{number:03d}-{key}-{mode}-{width}-case-details.png"
                    page.screenshot(path=str(SHOTS / crop), full_page=True,
                                    clip={"x": box[0], "y": box[1], "width": box[2], "height": box[3]})
                    shots.append({"shot": crop, "state": key, "mode": mode, "viewport": f"{width} Case details section"})
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
