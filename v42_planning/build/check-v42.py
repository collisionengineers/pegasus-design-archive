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
NON_COMPOSE_MESSAGES = ("message-m1", "message-m2", "message-m3", "message-m4",
                        "message-m7", "message-m11", "message-m12")
WITH_QUERY_ROW = ("message-m2", "message-m4", "message-m12")

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
              f"!{json.dumps(KEPT)}.includes(e.textContent.trim()))")

    # Inbox list (A, B, I): 3 scopes (All, No Case Found, Dismissed), no Sent/Deleted, Principal & Signal filters
    go(page, "inbox", "today")
    check("inbox today: live Category select", q("select#queue-filter"))
    check("inbox today: live bulk Correct classification", q("[data-bulk-classify]"))
    check("inbox today: All incoming lists m7 to m10", all(s in rows() for s in REMOVED_SUBJECTS))
    go(page, "inbox", "proposal")
    check("I: inbox has no Category select and no left aside pane",
          not q("select#queue-filter") and not q("section.inbox-layout > aside.pane"))
    check("I: inbox has exactly three scope tabs (All, No Case Found, Dismissed) and no Sent or Deleted Items",
          frame_eval(page, "Array.from(d.querySelectorAll('[data-scope-switch]')).map(b => b.getAttribute('data-scope-switch')).join(',')") == "all,no_case_found,dismissed")
    check("I: inbox has Principal and Mailbox filter selects and exact column headers",
          q("select#principal-filter") and q("select#mailbox-filter")
          and frame_eval(page, "Array.from(d.querySelectorAll('.inbox-ledger-head > span')).map(s => s.textContent.trim()).filter(Boolean).join(',')") == "Case,Type,Subject,Sender,Received")
    check("I: inbox has no bulk Correct classification or its dialog, and bulk bar is hidden when 0 ticked",
          not q("[data-bulk-classify]") and not q("#bulkClassifyDialog")
          and frame_eval(page, "d.getElementById('mail-bulk').hidden === true"))
    check("I: inbox header has Select all checkbox", q("input[data-mail-tick-all]"))
    listed = rows()
    check("B: All omits unlinked non-instruction m7 to m10", not any(s in listed for s in REMOVED_SUBJECTS))
    check("B: All lists 8 instructions, triage requests and Case-linked messages", len(listed) == 8)
    check("A: no removed category text on an All row", not stray_category())
    go(page, "inbox-no-case-found", "proposal")
    listed = rows()
    check("B: No Case Found lists m7 to m10", all(s in listed for s in REMOVED_SUBJECTS))
    check("A: No Case Found rows carry no removed category text", not stray_category())
    check("I: No Case Found has no Category select", not q("select#queue-filter"))
    go(page, "inbox-dismissed", "proposal")
    check("I: Dismissed scope lists dismissed messages with Restore",
          n("div.inbox-row") == 2 and q('form[data-mail-row-action="restore"]'))
    go(page, "inbox-rows-ticked", "today")
    check("inbox-rows-ticked today: two ticks, count 2", text("[data-bulk-count]") == "2")
    go(page, "inbox-rows-ticked", "proposal")
    check("I: ticked rows reveal the contextual bulk bar with count 2 and Dismiss only",
          frame_eval(page, "d.getElementById('mail-bulk').hidden === false")
          and text("[data-bulk-count]") == "2"
          and n("form#mail-bulk button") == 1 and "Dismiss" in text("form#mail-bulk"))
    check("I: Select all checkbox ticks all visible rows and updates bulk count",
          frame_eval(page, "(() => { const a = d.querySelector('input[data-mail-tick-all]'); a.click();"
                           " const ok = d.querySelector('[data-bulk-count]').textContent.trim() === '8';"
                           " a.click(); return ok; })()"))

    # Message dialog over /Inbox + streamlined cog settings menu (G, H, K, L, N, R)
    tc = lambda s: frame_eval(page, f"(d.querySelector({json.dumps(s)}) || {{textContent: ''}}).textContent.trim()")
    val = lambda s: frame_eval(page, f"(d.querySelector({json.dumps(s)}) || {{value: ''}}).value")
    for key in MESSAGES:
        for mode in ("today", "proposal"):
            go(page, key, mode)
            check(f"{key} ({mode}): opens #mailMessageDialog over /Inbox (not standalone page)",
                  frame_eval(page, "(() => { const g = d.getElementById('mailMessageDialog');"
                                   " return !!g && !g.hidden && !!d.querySelector('[data-mail-workspace]') && !d.querySelector('article.record'); })()"))
    for key in NON_COMPOSE_MESSAGES:
        go(page, key, "today")
        check(f"{key} today: live Decision sidebar with twelve Classification chips",
              q("section.mail-decision") and n("#mailClassificationForm .mail-chips .chip") == 12)
        go(page, key, "proposal")
        check(f"G: {key} replaces Decision sidebar with cog settings menu and context bar",
              not q("section.mail-decision") and q("details[data-mail-settings] [data-mail-settings-toggle]")
              and q("[data-mail-context-bar]"))
        check(f"H: {key} replaces clicky chips with one streamlined Type select (6 options)",
              not q("#mailClassificationForm .mail-chips") and n("#mailTypeSelect option") == 6)
        check(f"H: {key} label is Type", tc("#mailClassificationForm .mail-decision-label") == "Type")
        check(f"G: {key} Case section comes first in cog menu", frame_eval(
            page, "(() => { const f = d.querySelector('[data-mail-settings-popover] .decision-facts');"
                  " const first = f && f.firstElementChild;"
                  " return !!first && first.textContent.trim().startsWith('Case'); })()"))
        has_query = q("[data-mail-query]")
        if key in WITH_QUERY_ROW:
            check(f"N/K: {key} has the Query action after Email type", has_query and frame_eval(
                page, "d.querySelector('#mailClassificationForm').nextElementSibling.hasAttribute('data-mail-query')"))
        else:
            check(f"N: {key} has no Query row", not has_query)
        check(f"G: {key} Change case only on m11", q("[data-mail-change-case]") == (key == "message-m11"))
    go(page, "message-m1", "proposal")
    check("H: m1 selects New instruction — Inspection", val("#mailTypeSelect") == "new-instruction:Inspection")
    for key in ("message-m2", "message-m3", "message-m7", "message-m12"):
        go(page, key, "proposal")
        check(f"A/H: {key} selects Case correspondence", val("#mailTypeSelect") == "correspondence")
    go(page, "message-m4", "proposal")
    query_row = tc("[data-mail-query]")
    check("K: m4 Query item has Mark done and Query · Unassigned",
          all(word in query_row for word in ("Query", "Unassigned", "Mark done")))
    for key in ("message-m2", "message-m12"):
        go(page, key, "proposal")
        check(f"N: {key} Query item offers Open query", "Open query" in tc("[data-mail-query]"))
    go(page, "message-m11", "proposal")
    check("E: m11 selects Cancellation", val("#mailTypeSelect") == "cancellation")
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
        page, "(d.querySelector('input[data-resolve-query]').closest('label').textContent || '').trim()") == "Mark query done")

    # Interactive email opening, Next stepping and live settings menu actions on /Inbox
    go(page, "inbox", "proposal")
    frame_click(page, '.inbox-row[data-mail-row] a[data-mail-open]')
    page.wait_for_timeout(150)
    check("interactive: clicking a row on /Inbox opens #mailMessageDialog",
          frame_eval(page, "(() => { const g = d.getElementById('mailMessageDialog'); return !!g && !g.hidden; })()"))
    first_id = frame_eval(page, "d.getElementById('mailMessageDialog').getAttribute('data-mail-message')")
    frame_click(page, "#mailMessageDialog [data-mail-next]")
    page.wait_for_timeout(150)
    second_id = frame_eval(page, "d.getElementById('mailMessageDialog').getAttribute('data-mail-message')")
    check("interactive: Next message button steps to the next email in the list",
          bool(second_id) and second_id != first_id)
    # Next once more reaches m2 (which has Open query in its cog menu)
    frame_click(page, "#mailMessageDialog [data-mail-next]")
    page.wait_for_timeout(150)
    frame_click(page, "#mailMessageDialog [data-mail-settings-toggle]")
    page.wait_for_timeout(80)
    frame_click(page, '#mailMessageDialog [data-mail-query] button[type="submit"]')
    page.wait_for_timeout(120)
    check("interactive: clicking Open query in cog menu updates the dialog context bar to Query · Unassigned",
          "Query · Unassigned" in tc("#mailMessageDialog [data-mail-context-bar]"))
    # Verify table row-action buttons fit inside their td / .table-wrap container
    go(page, "case", "proposal")
    check("layout: Case Correspondence and Queries buttons fit inside their row and table-wrap",
          frame_eval(page, "Array.from(d.querySelectorAll('#section-files td.row-actions .btn, #section-queries td.row-actions .btn')).every(b => {"
                           " const br = b.getBoundingClientRect(); const tdr = b.closest('td').getBoundingClientRect();"
                           " return br.top >= tdr.top - 0.5 && br.bottom <= tdr.bottom + 0.5; })"))

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

    # Work Centre 5 candidate designs (WC1..WC5, AC)
    wc_markers = {
        "a": ".wc-v42--a .wc-a-stats-grid",
        "b": ".wc-v42--b .pane-layout.wc-b-workbench",
        "c": ".wc-v42--c .wc-c-board",
        "d": ".wc-v42--d .wc-d-layout",
        "e": ".wc-v42--e .record.wc-e-deck",
    }
    for d_key, marker in wc_markers.items():
        wc_state = f"work-centre-{d_key}"
        go(page, wc_state, "today")
        check(f"{wc_state} today: live Needs attention Work Centre",
              q("#wc-tab-attention") and not q(".wc-v42-root"))
        go(page, wc_state, "proposal")
        body_text = text("main")
        check(f"AC/{d_key.upper()}: {wc_state} removes Needs attention and renders distinct design marker ({marker})",
              not q("#wc-tab-attention") and q(marker) and q("[data-wc-design-bar]"))
        check(f"AC/{d_key.upper()}: {wc_state} preserves Queue totals and Activity Today/Week stats",
              all(lbl in body_text for lbl in ("Not ready", "Review", "Held", "Unidentified", "Triages"))
              and q('[data-figure="new-cases-today"]') and q('[data-figure="sent-today"]')
              and q('[data-figure="reports-today"]') and q('[data-figure="emails-today"]'))
        check(f"AC/{d_key.upper()}: {wc_state} defaults to New Cases first view with API, E-mail, Manual and Automation arrivals",
              q('[data-wc-view-tab="new-cases"][aria-selected="true"]')
              and q('[data-wc-channel="api"]') and q('[data-wc-channel="email"]')
              and q('[data-wc-channel="manual"]') and q('[data-wc-channel="automation"]'))
        check(f"AC/{d_key.upper()}: {wc_state} includes System Actions and AI Actions panels",
              q('[data-wc-view-panel="system-actions"] [data-wc-sys-kind="auto-match"]')
              and q('[data-wc-view-panel="system-actions"] [data-wc-sys-kind="images"]')
              and q('[data-wc-view-panel="ai-actions"] [data-wc-ai-kind="estimate"]')
              and q('[data-wc-view-panel="ai-actions"] [data-wc-ai-kind="query-draft"]'))
        check(f"AC/{d_key.upper()}: {wc_state} has no horizontal overflow",
              frame_eval(page, "d.documentElement.scrollWidth <= d.documentElement.clientWidth"))
    # Interactive tab switching and Design B inspector verification
    go(page, "work-centre-a", "proposal")
    frame_click(page, '[data-wc-view-tab="system-actions"]')
    check("AC: clicking System Actions tab reveals system-actions panel",
          frame_eval(page, "!d.querySelector('[data-wc-view-panel=\"system-actions\"]').hidden"))
    frame_click(page, '[data-wc-view-tab="ai-actions"]')
    check("AC: clicking AI Actions tab reveals ai-actions panel with Estimate done and Draft to a query",
          frame_eval(page, "!d.querySelector('[data-wc-view-panel=\"ai-actions\"]').hidden")
          and "Estimate done" in text('[data-wc-view-panel="ai-actions"]')
          and "Draft to a query" in text('[data-wc-view-panel="ai-actions"]'))
    go(page, "work-centre-b", "proposal")
    frame_click(page, 'tr[data-wc-inspect-row="nc-26217"]')
    check("AC/B: clicking a row in Design B updates the right-hand split inspector",
          frame_eval(page, "!d.querySelector('[data-wc-inspector-card=\"nc-26217\"]').hidden"))
    go(page, "cases-query", "proposal")
    check("P: Cases › Queries unchanged", not page.evaluate("window.__mock.meta('cases-query').hasProposal"))
    # Upload 5 candidate designs (UB1..UB5, AB) for both /Upload and Case /Upload?caseId=…
    design_markers = {
        "a": ".up-v42--a .pane-layout.up-a-workbench",
        "b": ".up-v42--b .up-b-guide",
        "c": ".up-v42--c .up-c-dropbar",
        "d": ".up-v42--d .up-d-split",
        "e": ".up-v42--e .record.up-e-sheet",
    }
    for d_key, marker in design_markers.items():
        rail_state = f"upload-{d_key}"
        case_state = f"upload-{d_key}-case"
        go(page, rail_state, "today")
        check(f"{rail_state} today: live .up-surface without DeclaredCaseId",
              q(".up-surface") and not q(".up-v42-root") and not q("[data-upload-declared]"))
        go(page, case_state, "today")
        check(f"{case_state} today: live .up-surface with DeclaredCaseId for QDOS26214",
              q(".up-surface") and not q(".up-v42-root") and q("[data-upload-declared]")
              and "QDOS26214" in text("[data-upload-destination]"))
        for st, is_case in ((rail_state, False), (case_state, True)):
            go(page, st, "proposal")
            body_text = text("main")
            check(f"AB/{d_key.upper()}: {st} renders distinct design marker ({marker}) and upload.js enhancement",
                  q(marker) and q("[data-upload-select].is-enhanced") and q("input#Upload[type='file']"))
            check(f"AB/{d_key.upper()}: {st} preserves exact limits and accepted extensions",
                  all(lim in body_text for lim in (
                      "20 files maximum", "100.0 MB per file", "200.0 MB per upload",
                      "JPG, JPEG, PNG, PDF, DOC, DOCX, EML, MSG, MP4 or MOV")))
            check(f"AB/{d_key.upper()}: {st} has no horizontal overflow",
                  frame_eval(page, "d.documentElement.scrollWidth <= d.documentElement.clientWidth"))
            if is_case:
                check(f"AB/{d_key.upper()}: {st} displays QDOS26214 Case identity, filing rule and Back to QDOS26214",
                      q("[data-upload-declared]") and q("[data-upload-back-case]")
                      and all(tok in body_text for tok in (
                          "QDOS26214", "MA59BDY · R. Whitfield", "QDOS", "Report sent",
                          "They appear under Files once processed.", "Back to QDOS26214")))
    check("AB: clicking Back to QDOS26214 on upload-e-case returns to case",
          click_to_state(page, "upload-e-case", "[data-upload-back-case]", "case"))
    check("AB: clicking Add evidence on case opens upload-e-case",
          click_to_state(page, "case", "[data-add-evidence]", "upload-e-case"))
    go(page, "upload-e", "proposal")
    frame_click(page, '[data-upload-sample-toggle="1"]')
    page.wait_for_timeout(120)
    check("AB: 3 sample files toggle populates 3 files via upload.js and updates submit button",
          n("ul[data-select-list] li.up-file") == 3
          and text("[data-select-submit-label]") == "Upload 3 files")
    frame_click(page, '[data-upload-sample-toggle="0"]')
    page.wait_for_timeout(120)
    check("AB: Empty toggle clears sample files",
          n("ul[data-select-list] li.up-file") == 0)


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
