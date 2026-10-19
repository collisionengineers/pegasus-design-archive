"""Self-check and screenshots for pegasus_v41.html.

1. Every state loads in Today and in Proposal with no page error, and the Today
   frame is the capture (it has the live page's main landmark or auth panel).
2. Every Proposal with changes shows them (Diff badges mark at least one element,
   or the change is a stylesheet rule).
3. The Inbox Proposal: one dialog (no tags, no design choice), the eleven
   Classification chips with one pressed, the Case picker, I9's buttons, and the
   row ticks with one bulk form (I18).
4. The Work Centre, Case and Administration items whose hooks the plan names:
   W8, K5, K9, K10, A21 to A24, A26, A28, A30.
5. Screenshots of every state at 1580x1000, 1440x900 and 760x1000, plus a 1580
   whole-page capture, in Today and Proposal, into ../shots/ with verification.json.

Prints RESULT {"fail":[...],"okCount":N}. Run: python build/check-v41.py [--no-shots]
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
ROOT = HERE.parent  # v41-redesign/
SHOTS = ROOT / "shots"
MOCK = (ROOT / "pegasus_v41.html").resolve().as_uri()
CHROME = next(iter(sorted(glob.glob(os.path.expandvars(
    r"%LOCALAPPDATA%\ms-playwright\chromium-*\chrome-win64\chrome.exe")), reverse=True)), None)
VIEWPORTS = [(1580, 1000), (1440, 900), (760, 1000)]

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


def frame_set(page: Page, script: str) -> None:
    """Run a statement in the frame (set a field, dispatch an event)."""
    page.evaluate(f"() => {{ const d = window.__mock.doc(); const w = window.__mock.win(); {script} }}")
    page.wait_for_timeout(80)


def click_to_state(page: Page, key: str, selector: str, expected: str) -> bool:
    """Click a link in the Proposal of one state and report whether the mockup moved to the expected state."""
    go(page, key, "proposal")
    frame_click(page, selector)
    page.wait_for_timeout(500)
    return page.evaluate("window.__mock.state") == expected


def inbox_checks(page: Page) -> None:
    q = lambda s: frame_eval(page, f"!!d.querySelector({json.dumps(s)})")
    n = lambda s: frame_eval(page, f"d.querySelectorAll({json.dumps(s)}).length")
    text = lambda: frame_eval(page, "d.body.innerText")
    ibx = lambda expr: frame_eval(page, f"w.InboxDesigns.state().{expr}")

    go(page, "inbox", "today")
    check("inbox today: live preview pane", q("#mail-quick-preview"))
    check("inbox today: live Folder select", q("#folder-filter"))

    # The one dialog (15 October ruling): no tag model, no design choice, no preview.
    go(page, "inbox", "proposal")
    check("inbox: mount rendered", q("[data-ibx] .inbox-layout"))
    check("inbox: five scopes on the rail", all(s in text() for s in
          ["All incoming", "No Case Found", "Sent Items", "Dismissed", "Deleted Items"]))
    check("inbox: no Folder select and no Tag filter", not q("[data-ibx] #folder-filter") and not q("#ibx-tag"))
    check("inbox: Category lists All categories and the eleven categories", n("#ibx-category option") == 12)
    check("inbox: no email called Unidentified", "Unidentified" not in text())
    check("inbox: no quick preview (the dialog is the reader)", not q("#mail-quick-preview"))
    check("inbox: no tag chips, tag column or New tag",
          not q(".tag-chip") and not q("[data-tag-column]") and not q("[data-toggle-tag]")
          and not frame_eval(page, "/\\btags?\\b/i.test(d.querySelector('[data-ibx]').innerText)"))
    check("inbox: the strip has no design row", not page.evaluate("!!document.querySelector('[data-design-row]')"))

    go(page, "inbox", "proposal", dialog="message", selected="m2")
    dialog = "[data-ibx-dialog] [data-dialog=message]"
    check("inbox: message dialog opens", q(dialog))
    check("inbox: no tag picker in the dialog", not q("[data-ibx-dialog] [data-tag-picker]") and not q("[data-ibx-dialog] #ibx-tag"))
    check("inbox: no Open full message", "Open full message" not in text())
    check("inbox: foot buttons plain as live (no dark or red outside composing)",
          n(f"{dialog} .dialog-foot .btn--dark, {dialog} .dialog-foot .btn--primary") == 0)
    check("inbox: Dismiss stands apart on the left", q(f"{dialog} .dialog-foot .left [data-dismiss]"))
    check("inbox: dialog at most 1080px",
          frame_eval(page, "d.querySelector('.dialog--mail').getBoundingClientRect().width") <= 1080)
    check("inbox: Previous/Next message", q(f"{dialog} [aria-label='Next message']"))
    check("inbox: tabs Message, Attachments, Thread (Case folded into Decision)",
          frame_eval(page, f"[...d.querySelectorAll('{dialog} .tabs .tab')].map(t => t.textContent.trim().split(/\\s/)[0]).join(',')") == "Message,Attachments,Thread")
    check("inbox: one Case row with its own actions, no Destination/Filed to",
          "Filed to" not in text() and "Destination" not in text() and q(f"{dialog} [data-open-link]") and q(f"{dialog} [data-open-unlink]"))
    check("inbox: Decided plain text with actor", "13 Oct 2026 08:04 · Automatic" in text())
    check("inbox: subject not repeated in the body",
          frame_eval(page, f"d.querySelector('{dialog} .dialog-body').innerText.includes('Update — QDOS26214 — repair authority')") is False)
    check("inbox: Correct classification is no button of the message dialog (the chips replace it)",
          frame_eval(page, f"[...d.querySelectorAll('{dialog} button')].every(b => !b.textContent.includes('Correct classification'))"))

    # Classification: the eleven categories as chips, one pressed, applied at once.
    go(page, "inbox", "proposal", dialog="message", selected="m1")
    chips = "[data-ibx-dialog] [data-set-classification]"
    pressed = lambda: frame_eval(page, f"[...d.querySelectorAll('{chips}')].filter(b => b.getAttribute('aria-pressed') === 'true').map(b => b.dataset.setClassification).join('|')")
    check("inbox: eleven Classification chips", n(chips) == 11)
    check("inbox: exactly one chip pressed, the message's classification", pressed() == "New instruction")
    frame_click(page, f"{chips}[data-set-classification='Billing']")
    check("inbox: a chip press applies at once", pressed() == "Billing" and n(chips) == 11)
    frame_click(page, f"{chips}[data-set-classification='Billing']")
    check("inbox: pressing the pressed chip does nothing", pressed() == "Billing")

    # The Case picker sits beside the chips, with I9's buttons beneath it.
    picker = "[data-ibx-dialog] [data-case-picker] input#ibx-case-query"
    check("inbox: Case picker (Case / PO combobox) in the dialog", q(picker) and "Case / PO" in text())
    check("inbox: chips, then the Case picker, then the Link / Unlink buttons", frame_eval(page, """(() => {
        const chips = d.querySelector('[data-ibx-dialog] .ibx-chipset');
        const picker = d.querySelector('[data-ibx-dialog] [data-case-picker]');
        const link = d.querySelector('[data-ibx-dialog] [data-open-link]');
        const before = (a, b) => !!(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING);
        return !!(chips && picker && link) && before(chips, picker) && before(picker, link);
    })()"""))
    check("inbox: an unlinked message offers Link to Case, no Unlink",
          q("[data-ibx-dialog] [data-open-link]") and not q("[data-ibx-dialog] [data-open-unlink]"))
    frame_set(page, "const i = d.querySelector('#ibx-case-query'); i.value = 'QDOS262'; i.dispatchEvent(new Event('input', {bubbles: true}));")
    check("inbox: typing in the Case picker lists Cases", n("[data-case-option]") == 4)
    frame_click(page, "[data-case-option='QDOS26216']")
    check("inbox: choosing a Case fills the picker", frame_eval(page, "d.querySelector('#ibx-case-query').value") == "QDOS26216")
    frame_click(page, "[aria-label='Next message']")
    check("inbox: Next message moves the dialog on", ibx("selected") == "m2")
    check("inbox: a linked message offers Change linked Case and Unlink", q("[data-ibx-dialog] [data-open-unlink]"))
    frame_click(page, "[data-ibx-dialog] [data-dismiss]")
    check("inbox: Dismiss in the dialog moves to the next message",
          ibx("selected") != "m2" and frame_eval(page, "!!w.InboxDesigns.state().dismissed.m2"))
    go(page, "inbox", "proposal", dialog="compose", selected="m2")
    check("inbox: composer has Cancel and Send", frame_eval(page, "d.querySelector('[data-ibx-dialog] .dialog-foot').innerText.includes('Cancel') && d.querySelector('[data-ibx-dialog] .dialog-foot').innerText.includes('Send')"))
    go(page, "inbox", "proposal", dialog="unlink", selected="m2")
    check("inbox: Unlink opens its reason dialog in one step", "Reason for action" in text() and "Unlink from QDOS26214" in text())
    go(page, "inbox", "proposal", scope="deleted")
    check("inbox: Deleted Items shows the live empty copy", "Deleted items messages are not kept" in text())

    # The Received sort toggle is the live link (words, direction and aria-label); no icon the sprite lacks.
    go(page, "inbox", "proposal")
    check("inbox: the Received sort toggle reads Received ↓ with the live aria-label and no icon",
          frame_eval(page, "(() => { const a = d.querySelector('.sort-toggle'); return !!a && a.tagName === 'A' && a.textContent.trim() === 'Received ↓' && a.getAttribute('aria-label') === 'Received order: newest first; activate for oldest first' && !a.querySelector('svg'); })()"))
    # The No Case Found scope lists the same three messages the capture does (m1, m3, m5), and the rail counts them.
    go(page, "inbox-no-case-found", "proposal")
    check("inbox: No Case Found lists the capture's three messages and the rail counts three",
          n("[data-mail-row]") == 3 and "3 messages" in text()
          and frame_eval(page, "[...d.querySelectorAll('.scope-button')].find(b => b.textContent.includes('No Case Found')).querySelector('.tabular').textContent.trim()") == "3")

    # I18 (R140): a tick on each row and one bulk form.
    go(page, "inbox", "proposal")
    check("I18: a tick on every incoming row, bound to the one bulk form",
          n("[data-mail-row]") == 5 and n("[data-tick][form='ibx-bulk']") == 5)
    check("I18: one bulk form, outside the rows", n("#ibx-bulk") == 1 and not q("[data-mail-row] #ibx-bulk"))
    check("I18: Dismiss and Correct classification stay enabled while nothing is ticked (a bare post writes nothing, no script needed)",
          frame_eval(page, "[...d.querySelectorAll('#ibx-bulk [data-bulk]')].map(b => b.dataset.bulk + ':' + b.disabled).join()") == "dismiss:false,classify:false")
    frame_click(page, "#ibx-bulk [data-bulk=dismiss]")
    frame_click(page, "#ibx-bulk [data-bulk=classify]")
    check("I18: Dismiss and Correct classification with nothing ticked write and open nothing",
          frame_eval(page, "Object.keys(w.InboxDesigns.state().dismissed).length") == 0 and n("[data-mail-row]") == 5
          and ibx("dialog") == "")
    check("I18: bulk Dismiss carries the existing busy word Dismissing…",
          frame_eval(page, "d.querySelector('#ibx-bulk [data-bulk=dismiss]').getAttribute('data-busy-label')") == "Dismissing…")
    frame_click(page, "[data-tick='m1']")
    check("I18: ticking a row counts it and enables the bulk buttons",
          ibx("ticked.m1") is True and frame_eval(page, "d.querySelector('[data-bulk-count]').textContent") == "1"
          and frame_eval(page, "[...d.querySelectorAll('#ibx-bulk [data-bulk]')].every(b => !b.disabled)"))
    frame_click(page, "[data-mail-row=m5] .ibx-row-tick")
    check("I18: ticking neither opens nor pins a row", ibx("ticked.m5") is True and ibx("selected") == "m1" and ibx("dialog") == "")
    frame_click(page, "#ibx-bulk [data-bulk=classify]")
    check("I18: bulk Correct classification opens the existing dialog once",
          ibx("dialog") == "bulk-classify" and n("[data-ibx-dialog] [data-dialog=classify]") == 1
          and all(s in text() for s in ["Classification", "Reason for correction", "Save correction"]))
    frame_click(page, "[data-ibx-dialog] [data-dialog-close]")
    frame_click(page, "#ibx-bulk [data-bulk=dismiss]")
    check("I18: bulk Dismiss dismisses every ticked row and clears the ticks",
          sorted(frame_eval(page, "Object.keys(w.InboxDesigns.state().dismissed)")) == ["m1", "m5"]
          and frame_eval(page, "Object.keys(w.InboxDesigns.state().ticked).length") == 0 and n("[data-mail-row]") == 3)
    frame_click(page, "[data-scope=dismissed]")
    check("I18: Dismissed offers bulk Restore, not Dismiss or Correct classification",
          q("#ibx-bulk [data-bulk=restore]") and not q("#ibx-bulk [data-bulk=dismiss]") and not q("#ibx-bulk [data-bulk=classify]"))
    check("I18: bulk Restore carries the existing busy word Restoring…",
          frame_eval(page, "d.querySelector('#ibx-bulk [data-bulk=restore]').getAttribute('data-busy-label')") == "Restoring…")
    frame_click(page, "[data-tick='m1']")
    frame_click(page, "#ibx-bulk [data-bulk=restore]")
    check("I18: bulk Restore returns the ticked rows",
          sorted(frame_eval(page, "Object.keys(w.InboxDesigns.state().dismissed)")) == ["m5"])
    for scope in ("sent", "deleted"):
        go(page, "inbox", "proposal", scope=scope)
        check(f"I18: {scope} scope has no ticks and no bulk form", not q("#ibx-bulk") and not q("[data-tick]"))

    go(page, "inbox-rows-ticked", "proposal")
    check("I18: inbox-rows-ticked opens with two rows ticked",
          n("[data-tick]:checked") == 2 and frame_eval(page, "d.querySelector('[data-bulk-count]').textContent") == "2")
    go(page, "inbox-rows-ticked-classify", "proposal")
    check("I18: inbox-rows-ticked-classify opens the Correct classification dialog",
          n("[data-ibx-dialog] [data-dialog=classify]") == 1 and n("#ibx-classification option") == 13)
    check("I18: Save correction carries the busy word Saving…",
          frame_eval(page, "d.querySelector('[data-ibx-dialog] [data-ibx-reason] button[type=submit]').getAttribute('data-busy-label')") == "Saving…")
    frame_set(page, "const s = d.querySelector('#ibx-classification'); s.value = 'New instruction'; s.dispatchEvent(new Event('change', {bubbles: true}));")
    check("I18: New instruction asks for a Case type", frame_eval(page, "!d.querySelector('[data-work-type-field]').hidden"))
    frame_set(page, """const s = d.querySelector('#ibx-classification'); s.value = 'Billing'; s.dispatchEvent(new Event('change', {bubbles: true}));
        d.querySelector('#ibx-correction-reason').value = 'Checked'; d.querySelector('[data-ibx-reason]').requestSubmit();""")
    check("I18: saving applies one classification to every ticked row and clears the ticks",
          ibx("dialog") == "" and frame_eval(page, "Object.keys(w.InboxDesigns.state().ticked).length") == 0
          and all("Billing" in frame_eval(page, f"d.querySelector('[data-mail-row={m}]').innerText") for m in ("m1", "m5")))
    go(page, "inbox-rows-ticked-busy", "proposal")
    check("I18: inbox-rows-ticked-busy draws the pressed bulk Dismiss busy, with its glyph and word",
          frame_eval(page, "(() => { const b = d.querySelector('#ibx-bulk [data-bulk=dismiss]'); return !!b && b.hasAttribute('data-busy') && b.textContent.trim() === 'Dismissing…' && !!b.querySelector('.busy-spin'); })()")
          and q("#ibx-bulk[data-busy-form]") and n("[data-tick]:checked") == 2)
    go(page, "inbox-dismissed-rows-ticked", "proposal")
    check("I18: inbox-dismissed-rows-ticked lists two dismissed rows, one ticked, Restore enabled",
          n("[data-mail-row]") == 2 and n("[data-tick]:checked") == 1
          and frame_eval(page, "!d.querySelector('#ibx-bulk [data-bulk=restore]').disabled"))

    # I14 is dropped: Case correspondence opens no Inbox dialog.
    go(page, "case-correspondence", "proposal")
    check("case-correspondence: no Inbox dialog, mount or openers", not q("[data-ibx-open]") and not q("[data-ibx]"))


def lane_checks(page: Page) -> None:
    """W8, K5, K9, K10 and the Administration items whose hooks plan-2026-10-15.md 2.4 names."""
    q = lambda s: frame_eval(page, f"!!d.querySelector({json.dumps(s)})")
    n = lambda s: frame_eval(page, f"d.querySelectorAll({json.dumps(s)}).length")
    texts = lambda s: frame_eval(page, f"[...d.querySelectorAll({json.dumps(s)})].map(e => e.textContent.trim().replace(/\\s+/g, ' '))")

    # W8: the Unassigned option, Take on an Unassigned row, a With Engineer row in Mine, Unassigned in Cases.
    go(page, "work-centre-assign", "proposal")
    named = frame_eval(page, "[...d.querySelectorAll('#wc-assign-engineer option')].filter(o => o.value).map(o => o.textContent.trim())")
    check("W8: Assign Engineer lists the signed-in person first as Name (you)", bool(named) and named[0].endswith("(you)"))
    check("W8: Assign Engineer gains an Unassigned option", named[-1:] == ["Unassigned"])
    check("W8: the Assign Engineer dialog has no Reason box", not q("#wc-assign-dialog textarea, #wc-assign-dialog [name=reason]"))
    viewer_id = frame_eval(page, "([...d.querySelectorAll('#wc-assign-engineer option')].find(o => o.textContent.trim().endsWith('(you)')) || {}).value || ''")
    check("W8: the (you) option carries the signed-in person's staff id", bool(viewer_id) and viewer_id != "unassigned")
    for key in ("work-centre", "work-centre-assign", "work-centre-mine"):
        go(page, key, "proposal")
        check(f"W8 {key}: Take beside Assign Engineer on an Unassigned row",
              q("tr[data-wc-row-kind=unassigned] form[data-wc-take] button.btn--primary")
              and texts("tr[data-wc-row-kind=unassigned] form[data-wc-take] button")[0] == "Take"
              and q("tr[data-wc-row-kind=unassigned] .wc-row-actions a.btn"))
        ids = frame_eval(page, "[...d.querySelectorAll('form[data-wc-take] input[name=engineerId]')].map(i => i.value)")
        check(f"W8 {key}: every Take posts the signed-in person's staff id as engineerId", bool(ids) and set(ids) == {viewer_id})
    go(page, "work-centre-mine", "proposal")
    check("W8: Mine gains a With Engineer row", texts("tr[data-wc-row-kind=with-engineer] a.wc-task-link") == ["With Engineer"])
    check("W8: the Mine With Engineer row is undated (No due date), last in Later, with no Due borrowed from another Case",
          texts("tr[data-wc-row-kind=with-engineer] .wc-col-due") == ["No due date"]
          and frame_eval(page, "(() => { const rows = [...d.querySelectorAll('#wc-panel-attention table.wc-ledger-table tbody tr')]; const at = rows.findIndex(r => r.dataset.wcRowKind === 'with-engineer'); return at > 0 && rows.slice(0, at).some(r => r.dataset.wcGroup === 'later') && at === rows.length - 1; })()")
          and "Later (2)" in texts("tr.wc-group-row[data-wc-group=later] h3"))
    go(page, "cases-with-engineer", "proposal")
    check("W8: Cases · With Engineer reads Unassigned where there is no Engineer",
          "Unassigned" in texts(".cases-table tbody tr[data-cases-row] td"))

    # K5: the Report sent Case reads its To from the capture's sent evidence.
    go(page, "case-report-sent", "proposal")
    recipients = frame_eval(page, "[...d.querySelectorAll('.recip-form[data-send-report-read] > .fc.ro')].map(c => c.innerText.replace(/\\s+/g, ' ').trim())")
    check("K5: read-mode To shows an address taken from the capture, Cc stays Not recorded",
          any(c.upper().startswith("TO ") and "@" in c for c in recipients) and any(c.upper().startswith("CC ") and "Not recorded" in c for c in recipients))

    # K9: a With Engineer Case with no Engineer.
    go(page, "case-with-engineer-unassigned", "proposal")
    ribbon = frame_eval(page, "[...d.querySelectorAll('.ribbon-item')].filter(i => i.querySelector('.ribbon-label') && i.querySelector('.ribbon-label').textContent.trim() === 'Engineer').map(i => i.querySelector('.ribbon-value').textContent.trim())")
    check("K9: the ribbon Engineer reads Unassigned", ribbon == ["Unassigned"])
    check("K9: Next action opens with Assign Engineer and Take beside it",
          texts("[data-next-assign] .btn")[:2] == ["Assign Engineer", "Take"] and q("[data-next-assign] form[data-case-take] button.btn--primary"))
    take_engineer = frame_eval(page, "(d.querySelector('[data-next-assign] form[data-case-take] input[name=engineerId]') || {}).value || ''")
    you_engineer = frame_eval(page, "([...d.querySelectorAll('#case-handoff-dialog select option')].find(o => o.textContent.trim().endsWith('(you)')) || {}).value || ''")
    check("K9: Take posts the engineerId the dialog's (you) option posts", bool(take_engineer) and take_engineer == you_engineer)
    menu = texts("[data-case-actions] .menu-body .btn")
    check("K9: the Actions menu lists Assign Engineer first", bool(menu) and menu[0] == "Assign Engineer")
    handoff = texts("#case-handoff-dialog select option")
    check("K9: the Assign Engineer dialog lists (you) first, then Unassigned, with no Reason box",
          len(handoff) >= 3 and handoff[1].endswith("(you)") and handoff[-1] == "Unassigned"
          and not q("#case-handoff-dialog textarea, #case-handoff-dialog [name=reason]"))
    check("K6-K8: the case-query-view-* states are gone", not any(k.startswith("case-query-view") for k in page.evaluate("window.__mock.states")))

    # K10 (R157): Return to work on a closed Case.
    go(page, "case-closed", "proposal")
    menu = texts("[data-case-actions] .menu-body .btn")
    check("K10: the Actions menu offers Return to work before Archive case",
          "Return to work" in menu and "Archive case" in menu and menu.index("Return to work") < menu.index("Archive case"))
    check("K10: the Return to work dialog posts the Reopen handler with a stage and a reason",
          q("#case-return-to-work-dialog form[action*='handler=Reopen']")
          and texts("#case-return-to-work-dialog select[name=destination] option")[1:] == ["Not ready", "Review", "With Engineer", "Report sent"]
          and q("#case-return-to-work-dialog textarea"))

    # A21, A22, A23, A24, A26, A28, A30.
    go(page, "valuation-presets", "proposal")
    check("A21: amount inputs sit inside the .input-money wrapper",
          n("table.preset-table .input-money > input") > 0 and n("table.preset-table input.input-money") == 0)
    heads = texts("table.preset-table thead th")
    check("A21: the State column reads Enabled and the head reads Presets",
          "Enabled" in heads and "State" not in heads and "Presets" in texts("main h2"))
    go(page, "health", "proposal")
    check("A22: Working chips take the green tone", n(".service-health-table td .status--green") > 0)
    go(page, "automation", "proposal")
    body = frame_eval(page, "d.body.innerText")
    check("A23: Received files and Send to AI", "Received files" in body and "Send to AI" in body and "Reviewed AI proposals enabled" not in body)
    go(page, "logs", "proposal")
    check("A24: no <details> on Logs", n("main details") == 0)
    go(page, "logs-intake", "proposal")
    check("A24: the Intake log tiles use .metric",
          n(".metric-strip .metric") >= 2 and texts(".metric-strip .metric-label") == ["Failed files", "Oldest file waiting"])
    go(page, "logs-intake-drawer", "proposal")
    check("A24: the drawer takes the shared dialog frame with one close",
          q("[data-dialog=intake-drawer] .dialog") and not q("aside.logs-drawer") and n("[data-dialog=intake-drawer] .dialog-close") == 1
          and not q("[data-dialog=intake-drawer] .dialog-foot a"))
    check("A24: the Logs intake tab link lands on the intake state",
          click_to_state(page, "logs", "a[href='/Administration/Logs?tab=intake']", "logs-intake"))
    for key, active in (("reports", "Engineers"), ("reports-principals", "Principals"),
                        ("reports-queues", "Queues"), ("reports-case-list", "Case list")):
        go(page, key, "proposal")
        check(f"A26 {key}: four tabs under the period bar, {active} current",
              texts("nav.tabs a") == ["Engineers", "Principals", "Queues", "Case list"]
              and frame_eval(page, "d.querySelector('nav.tabs a[aria-current=page]').textContent.trim()") == active)
    check("A26: the Principals tab link lands on the Principals state",
          click_to_state(page, "reports", "nav.tabs a[href$='tab=principals']", "reports-principals"))
    go(page, "reports-case-list", "proposal")
    check("A26: the Case list has its fieldsets", n("section[data-case-list] form fieldset") > 0)
    go(page, "ai-jobs", "proposal")
    check("A28: no .row-confirm, details or reason box on AI jobs",
          n(".row-confirm") == 0 and n("table[data-admin-ai-jobs] td.row-actions details") == 0 and n("table[data-admin-ai-jobs] input[name=reason]") == 0)
    check("A28: Stop is one small danger button",
          n("table[data-admin-ai-jobs] td.row-actions form button.btn--danger.btn--small") > 0
          and "Stop" in texts("table[data-admin-ai-jobs] td.row-actions form button"))
    go(page, "contacts", "proposal")
    check("A30: Apply renders only without script", q("form.contact-toolbar noscript") and not q("form.contact-toolbar > button[type=submit]"))


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
            if meta["hasProposal"] and meta["changes"] and not meta.get("ibx"):
                go(page, key, "proposal", diff=True)
                marked = frame_eval(page, "d.querySelectorAll('[data-v41-change], style[data-v41-css]').length")
                check(f"{key}: proposal marks its changes", marked > 0)

        errors.clear()
        inbox_checks(page)
        lane_checks(page)
        check(f"checks: no page or console error {errors[:2]}", not errors)

        if shots_wanted:
            SHOTS.mkdir(exist_ok=True)
            for old in SHOTS.glob("*.png"):
                old.unlink()
            number = 0
            plan = [(key, mode, {}) for key in keys for mode in ("today", "proposal")
                    if mode == "today" or page.evaluate("k => window.__mock.meta(k).hasProposal", key)]
            for key, mode, options in plan:
                number += 1
                for width, height in VIEWPORTS:
                    errors.clear()
                    page.set_viewport_size({"width": width, "height": height})
                    go(page, key, mode, **options)
                    name = f"{number:03d}-{key}-{mode}-{width}.png"
                    page.screenshot(path=str(SHOTS / name))
                    shots.append({"shot": name, "state": key, "mode": mode, "viewport": f"{width}x{height}", **options})
                    check(f"shot {name}: no console error {errors[:2]}", not errors)
                    if width == 1580:
                        page.evaluate("window.__mock.expand(true)")
                        full = f"{number:03d}-{key}-{mode}-full.png"
                        page.screenshot(path=str(SHOTS / full), full_page=True)
                        page.evaluate("window.__mock.expand(false)")
                        shots.append({"shot": full, "state": key, "mode": mode, "viewport": "1580 whole page", **options})
        browser.close()

    result = {"fail": fail, "okCount": len(ok)}
    if shots_wanted:
        (SHOTS / "verification.json").write_text(json.dumps({
            "checkedAtUtc": datetime.now(timezone.utc).isoformat(), "result": result, "shots": shots}, indent=2), encoding="utf-8")
    print("RESULT " + json.dumps(result))
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
