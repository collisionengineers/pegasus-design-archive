"""Self-check and screenshots for pegasus_v42.html.

1. Every state loads in Today and in Proposal with no page error, and the Today
   frame is the capture (it has the live page's main landmark).
2. Every Proposal with changes shows them (Diff badges mark at least one element).
3. The Inbox Proposal: no Category select and no bulk Correct classification;
   four Type chips with exactly one pressed on every message state; the Query row
   on m2, m4 and m12 and not on m1, m3 or m7; Change case links on m11.
4. The Case and Work Centre Proposals: Correspondence header Type and no Tag as
   query; the Queries section's Assigned to column and a Reopen on the Done row;
   the Assign query dialog; a Query kind chip and row in the Work Centre.
5. Screenshots of every state at 1580x1000, 1440x900 and 760x1000, plus a 1580
   whole-page capture, in Today and Proposal, into ../shots/ with verification.json.

Prints RESULT {"fail":[...],"okCount":N}. Run: python build/check-v42.py [--no-shots]
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
ROOT = HERE.parent  # v42_planning/
SHOTS = ROOT / "shots"
MOCK = (ROOT / "pegasus_v42.html").resolve().as_uri()
CHROME = next(iter(sorted(glob.glob(os.path.expandvars(
    r"%LOCALAPPDATA%\ms-playwright\chromium-*\chrome-win64\chrome.exe")), reverse=True)), None)
VIEWPORTS = [(1580, 1000), (1440, 900), (760, 1000)]
KEPT = ["New instruction", "Triage request", "Cancellation"]
REMOVED_SUBJECTS = ["Remittance advice — October", "Your October product update",
                    "FW: QDOS26214 — engineer note", "Possible instruction — LK21 ABC"]
MESSAGES = ("message-m1", "message-m2", "message-m3", "message-m4", "message-m4-ai-reply",
            "message-m7", "message-m11", "message-m12")
WITH_QUERY_ROW = ("message-m2", "message-m4", "message-m4-ai-reply", "message-m12")

ok: list[str] = []
fail: list[str] = []


def check(name: str, condition: bool) -> None:
    (ok if condition else fail).append(name)


def go(page: Page, key: str, mode: str, **options) -> None:
    page.evaluate("([k, m, o]) => window.__mock.go(k, m, o)", [key, mode, options])
    page.wait_for_timeout(120)


def frame_eval(page: Page, script: str):
    return page.evaluate(f"() => {{ const d = window.__mock.doc(); const w = window.__mock.win(); return ({script}); }}")


def frame_click(page: Page, selector: str) -> None:
    page.evaluate("s => { const el = window.__mock.doc().querySelector(s); if (el) el.click(); }", selector)
    page.wait_for_timeout(80)


def click_to_state(page: Page, key: str, selector: str, expected: str) -> bool:
    """Click a link in the Proposal of one state and report whether the mockup moved to the expected state."""
    go(page, key, "proposal")
    frame_click(page, selector)
    page.wait_for_timeout(500)
    return page.evaluate("window.__mock.state") == expected


def v42_checks(page: Page) -> None:
    q = lambda s: frame_eval(page, f"!!d.querySelector({json.dumps(s)})")
    n = lambda s: frame_eval(page, f"d.querySelectorAll({json.dumps(s)}).length")
    text = lambda s: frame_eval(page, f"(d.querySelector({json.dumps(s)}) || {{innerText: ''}}).innerText.trim()")
    rows = lambda: frame_eval(page, "Array.from(d.querySelectorAll('div.inbox-row a.row-title')).map(a => a.innerText.trim())")
    stray_category = lambda: frame_eval(
        page, "Array.from(d.querySelectorAll('.cluster > .row-meta')).some(e => "
              f"!{json.dumps(KEPT)}.includes(e.innerText.trim()))")

    # Inbox list (A, B, I)
    go(page, "inbox", "today")
    check("inbox today: live Category select", q("select#queue-filter"))
    check("inbox today: live bulk Correct classification", q("[data-bulk-classify]"))
    check("inbox today: All incoming lists m7 to m10", all(s in rows() for s in REMOVED_SUBJECTS))
    go(page, "inbox", "proposal")
    check("I: inbox has no Category select", not q("select#queue-filter"))
    check("I: inbox has no bulk Correct classification or its dialog",
          not q("[data-bulk-classify]") and not q("#bulkClassifyDialog"))
    listed = rows()
    check("B: All incoming omits m7 to m10", not any(s in listed for s in REMOVED_SUBJECTS))
    check("B: All incoming keeps m1, m2, m4, m11 and m12 only", len(listed) == 5)
    check("B: All incoming count reads 5",
          frame_eval(page, "Array.from(d.querySelectorAll('.scope-list form')).find(f => f.innerText.trim().startsWith('All incoming')).innerText.replace(/\\s+/g, ' ').trim()") == "All incoming 5")
    check("A: no removed category text on an All incoming row", not stray_category())
    go(page, "inbox-no-case-found", "proposal")
    listed = rows()
    check("B: No Case Found lists m7 to m10", all(s in listed for s in REMOVED_SUBJECTS))
    check("A: No Case Found rows carry no removed category text", not stray_category())
    check("I: No Case Found has no Category select", not q("select#queue-filter"))
    go(page, "inbox-rows-ticked", "today")
    check("inbox-rows-ticked today: two ticks, count 2", text("[data-bulk-count]") == "2")
    go(page, "inbox-rows-ticked", "proposal")
    check("I: ticked rows keep the count 2", text("[data-bulk-count]") == "2")
    check("I: bulk bar keeps Dismiss only", n("form#mail-bulk button") == 1 and "Dismiss" in text("form#mail-bulk"))

    # Message dialog (G, H, K, L, N, R)
    for key in MESSAGES:
        go(page, key, "today")
        check(f"{key} today: twelve live Classification chips", n("#mailClassificationForm .mail-chips .chip") == 12)
        go(page, key, "proposal")
        check(f"H: {key} has four Type chips", n("#mailClassificationForm .mail-chips .chip") == 4)
        check(f"H: {key} has exactly one pressed chip", n('#mailClassificationForm .chip[aria-pressed="true"]') == 1)
        check(f"H: {key} row label is Type", text("#mailClassificationForm .mail-decision-label") == "Type")
        check(f"G: {key} Case row comes first", frame_eval(
            page, "(() => { const f = d.querySelector('.decision-facts'); const first = f && f.firstElementChild;"
                  " return !!first && first.classList.contains('decision-row') && first.innerText.trim().startsWith('Case'); })()"))
        has_query = q("[data-mail-query]")
        if key in WITH_QUERY_ROW:
            check(f"N/K: {key} has the Query row after Type", has_query and frame_eval(
                page, "d.querySelector('#mailClassificationForm').nextElementSibling.hasAttribute('data-mail-query')"))
        else:
            check(f"N: {key} has no Query row", not has_query)
        check(f"G: {key} Change case only on m11", q("[data-mail-change-case]") == (key == "message-m11"))
    go(page, "message-m1", "proposal")
    check("H: m1 New instruction pressed", text('.chip[aria-pressed="true"]') == "New instruction")
    check("H: m1 Case type select in the Type row", q("#mailClassificationForm [data-work-type-field] select#mailWorkType"))
    for key in ("message-m2", "message-m3", "message-m7", "message-m12"):
        go(page, key, "proposal")
        check(f"A/H: {key} pressed Correspondence", text('.chip[aria-pressed="true"]') == "Correspondence")
    go(page, "message-m4", "proposal")
    query_row = text("[data-mail-query]")
    check("K: m4 Query row has the Query chip, Unassigned and Mark done",
          all(word in query_row for word in ("Query", "Unassigned", "Mark done")))
    for key in ("message-m2", "message-m12"):
        go(page, key, "proposal")
        check(f"N: {key} Query row offers Open query", "Open query" in text("[data-mail-query]"))
    go(page, "message-m11", "proposal")
    check("E: m11 Cancellation pressed", text('.chip[aria-pressed="true"]') == "Cancellation")
    check("G: m11 Change case links to the hold and close dialogs",
          q('[data-mail-change-case] a[href$="?dialog=case-hold-dialog"]')
          and q('[data-mail-change-case] a[href$="?dialog=case-close-dialog"]'))
    check("G: m11 Place on Hold opens the Case",
          click_to_state(page, "message-m11", '[data-mail-change-case] a[href$="?dialog=case-hold-dialog"]', "case-qdos26220"))
    go(page, "message-m3", "today")
    check("message-m3 today: no Register images", not q('[data-offered-action="RegisterImages"]'))
    go(page, "message-m3", "proposal")
    check("R: m3 offers Register images with its dialog",
          q('[data-offered-action="RegisterImages"]') and q("#messageRegisterImagesDialog"))
    go(page, "message-m4-ai-reply", "proposal")
    check("L: composer tick reads Mark query done", frame_eval(
        page, "(d.querySelector('input[data-resolve-query]').closest('label').innerText || '').trim()") == "Mark query done")

    # Case (D, J, K, M, N, O, X, AA)
    go(page, "case", "today")
    check("case today: live Tag as query", q("form[data-tag-as-query]"))
    go(page, "case", "proposal")
    check("X: Correspondence header Type", frame_eval(
        page, "Array.from(d.querySelectorAll('#section-files th')).some(t => t.textContent.trim() === 'Type')"))
    check("X: no Classification header in Correspondence", not frame_eval(
        page, "Array.from(d.querySelectorAll('#section-files th')).some(t => t.textContent.trim() === 'Classification')"))
    check("X: the query e-mail carries the Query chip", q("#section-files td .status--purple"))
    check("N: no Tag as query; Open query on m2 and m12", not q("form[data-tag-as-query]") and n("form[data-open-query]") == 2)
    go(page, "case-queries", "proposal")
    check("D: Queries has the Assigned to column", frame_eval(
        page, "Array.from(d.querySelectorAll('[data-queries-table] th')).some(t => t.textContent.trim() === 'Assigned to')"))
    check("K: Queries column Done replaces Resolved", frame_eval(
        page, "(() => { const h = Array.from(d.querySelectorAll('[data-queries-table] th')).map(t => t.textContent.trim());"
              " return h.includes('Done') && !h.includes('Resolved'); })()"))
    check("M: Done row offers Reopen", q('tr[data-case-query-open="false"] [data-reopen-query]'))
    check("K/O: open rows offer Mark done, Assign and Take",
          n("[data-mark-query-done]") == 2 and n("[data-assign-query]") == 2 and n("[data-take-query]") == 2)
    go(page, "case-queries-assign", "today")
    check("case-queries-assign today: no Assign query dialog", not q("#case-assign-query-dialog"))
    go(page, "case-queries-assign", "proposal")
    check("O: Assign query dialog opens with Assigned to", frame_eval(
        page, "(() => { const g = d.getElementById('case-assign-query-dialog'); return !!g && !g.hidden; })()")
          and q("#case-assign-query-assignee"))
    check("O: Assigned to lists the viewer first and Unassigned last", frame_eval(
        page, "(() => { const o = Array.from(d.querySelectorAll('#case-assign-query-assignee option')).map(x => x.innerText.trim());"
              " return o[0].endsWith('(you)') && o[o.length - 1] === 'Unassigned'; })()"))
    go(page, "case-aside-query", "today")
    check("case-aside-query today: live Resolve query in the menu", q(".menu-body [data-resolve-query-form]"))
    go(page, "case-aside-query", "proposal")
    check("K: Next action reads Answer query with Reply",
          text("[data-next-resolve-query] [data-next-label]") == "Answer query" and q("[data-next-reply-query]"))
    check("K: Actions menu has no Resolve query", not q(".menu-body [data-resolve-query-form]"))
    check("K: Actions menu keeps Log query", q(".menu-body [data-log-query]"))
    check("AA: the purple Query stage chip stays", text(".ribbon-chips .status--purple") == "Query")
    go(page, "case-qdos26220", "proposal")
    check("AA: no Open query before the report is sent", not q("form[data-open-query]") and not q("form[data-tag-as-query]"))
    check("E: Cancellation received stays in the aside", "Cancellation received" in text("main"))

    # Work Centre (P)
    go(page, "work-centre", "proposal")
    check("P: Work Centre has the Query kind chip", q('nav.wc-filters a[data-wc-kind="query"]'))
    check("P: Work Centre Query row is Unassigned with Take",
          q('tr[data-wc-row-kind="query"] [data-wc-take]') and text('tr[data-wc-row-kind="query"] .wc-col-owner') == "Unassigned")
    check("P: Needs attention count reads 10", text("#wc-tab-attention .tab-count") == "10")
    go(page, "work-centre-mine", "proposal")
    check("P: Mine Query row assigned to the viewer, no Take",
          q('tr[data-wc-row-kind="query"]') and not q('tr[data-wc-row-kind="query"] [data-wc-take]')
          and text('tr[data-wc-row-kind="query"] .wc-col-owner') == "e.mawdsley")
    go(page, "cases-query", "proposal")
    check("P: Cases › Queries unchanged", not page.evaluate("window.__mock.meta('cases-query').hasProposal"))


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
                check(f"{key} ({mode}): renders the page",
                      frame_eval(page, "!!d.querySelector('main, .auth-panel, .external-shell, .app-shell')"))
            if meta["hasProposal"] and meta["changes"]:
                go(page, key, "proposal", diff=True)
                marked = frame_eval(page, "d.querySelectorAll('[data-v42-change], style[data-v42-css]').length")
                check(f"{key}: proposal marks its changes", marked > 0)

        errors.clear()
        v42_checks(page)
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
                    name = f"{number:03d}-{key}-{mode}-{width}.png"
                    page.screenshot(path=str(SHOTS / name))
                    shots.append({"shot": name, "state": key, "mode": mode, "viewport": f"{width}x{height}"})
                    check(f"shot {name}: no console error {errors[:2]}", not errors)
                    if width == 1580:
                        page.evaluate("window.__mock.expand(true)")
                        full = f"{number:03d}-{key}-{mode}-full.png"
                        page.screenshot(path=str(SHOTS / full), full_page=True)
                        page.evaluate("window.__mock.expand(false)")
                        shots.append({"shot": full, "state": key, "mode": mode, "viewport": "1580 whole page"})
        browser.close()

    result = {"fail": fail, "okCount": len(ok)}
    if shots_wanted:
        (SHOTS / "verification.json").write_text(json.dumps({
            "checkedAtUtc": datetime.now(timezone.utc).isoformat(), "result": result, "shots": shots}, indent=2), encoding="utf-8")
    print("RESULT " + json.dumps(result))
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
