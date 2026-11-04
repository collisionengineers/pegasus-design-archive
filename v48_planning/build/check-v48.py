"""Self-check and screenshots for pegasus_v48.html.

1. Every state loads in Today and in Proposal with no page or console error.
2. Every Proposal marks its changes (Diff badges).
3. Today is live (the inline send form, no dialog, no card); the Proposal holds items A–N
   (notes/v48-notes.md §6): the head and Next action openers, the dialog with every live
   field carried over, Subject, the Files rows and ticks, the viewer over the dialog, Rename
   and Reset, the rules' blocks, Cancel and close, the posted fields, the Original report
   card on the Audit view only with its rows and the money and placement variables, and the
   layout at 1580, 1440 and 760.
4. Screenshots of every state at 1580x1000, 1440x900 and 760x1000 with a crop of the
   Report section, the dialog or the card, a 1580 whole page for the page states, and the
   variable shots, into ../shots/ with verification.json.

Prints RESULT {"fail":[...],"okCount":N}. Run: python -X utf8 build/check-v48.py [--no-shots]
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # v48_planning/
SHOTS = ROOT / "shots"
MOCK = (ROOT / "pegasus_v48.html").resolve().as_uri()


def chromium() -> str | None:
    found = glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\ms-playwright\chromium-*\chrome-win64\chrome.exe"))
    def number(path: str) -> int:
        match = re.search(r"chromium-(\d+)", path)
        return int(match.group(1)) if match else 0
    return max(found, key=number) if found else None


CHROME = chromium()
VIEWPORTS = [(1580, 1000), (1440, 900), (760, 1000)]
RS = "#section-report"
DIALOG = '[data-dialog="case-send-report-dialog"]'
DLG = DIALOG + " section.dialog"
FORM = "form[data-send-report]"
OPENER = "[data-v48-send-open]"
CARD = "[data-v48-original-report]"
FIGURES = "[data-case-aside] [data-figures]"
VIEWER = "[data-case-viewer]"
ROW = "[data-v48-file]"
OPEN = "[data-v48-file-open]"

ok: list[str] = []
fail: list[str] = []


def check(name: str, condition: bool) -> None:
    (ok if condition else fail).append(name)


def go(page: Page, key: str, mode: str, **options) -> None:
    page.evaluate("([k, m, o]) => window.__mock.go(k, m, o)", [key, mode, options])
    page.wait_for_timeout(200)


def frame_eval(page: Page, script: str):
    return page.evaluate(f"() => {{ const d = window.__mock.doc(); const w = window.__mock.win(); return ({script}); }}")


def q(page: Page, selector: str) -> bool:
    return frame_eval(page, f"!!d.querySelector({json.dumps(selector)})")


def n(page: Page, selector: str) -> int:
    return frame_eval(page, f"d.querySelectorAll({json.dumps(selector)}).length")


def text_in(page: Page, selector: str) -> str:
    return frame_eval(page, f"(d.querySelector({json.dumps(selector)}) || {{innerText: ''}}).innerText")


def texts(page: Page, selector: str) -> list[str]:
    return frame_eval(page, f"[...d.querySelectorAll({json.dumps(selector)})].map(e => e.innerText.trim())")


def contents(page: Page, selector: str) -> list[str]:
    """textContent, untouched by text-transform (eyebrows and legends draw uppercase)."""
    return frame_eval(page, f"[...d.querySelectorAll({json.dumps(selector)})].map(e => e.textContent.trim())")


def attr(page: Page, selector: str, name: str):
    return frame_eval(page, f"(d.querySelector({json.dumps(selector)}) || {{getAttribute(){{return null}}}}).getAttribute({json.dumps(name)})")


def value(page: Page, selector: str):
    return frame_eval(page, f"(d.querySelector({json.dumps(selector)}) || {{}}).value")


def values(page: Page, selector: str) -> list:
    return frame_eval(page, f"[...d.querySelectorAll({json.dumps(selector)})].map(e => e.value)")


def shown(page: Page, selector: str) -> bool:
    return frame_eval(page, f"(() => {{ const e = d.querySelector({json.dumps(selector)}); if (!e) return false; "
                            "const s = w.getComputedStyle(e); const r = e.getBoundingClientRect(); "
                            "return s.display !== 'none' && s.visibility !== 'hidden' && !e.hidden && r.width > 0; })()")


def click(page: Page, selector: str, index: int = 0) -> None:
    frame_eval(page, f"d.querySelectorAll({json.dumps(selector)})[{index}].click()")
    page.wait_for_timeout(80)


def key(page: Page, name: str) -> None:
    frame_eval(page, f"d.activeElement.dispatchEvent(new KeyboardEvent('keydown', {{key: {json.dumps(name)}, bubbles: true, cancelable: true}}))")
    page.wait_for_timeout(80)


def rect(page: Page, selector: str) -> dict:
    return frame_eval(page, f"(() => {{ const e = d.querySelector({json.dumps(selector)}); if (!e) return null; "
                            "const r = e.getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height, right: r.right, bottom: r.bottom}; })()")


def dialog_open(page: Page) -> bool:
    return frame_eval(page, f"(() => {{ const b = d.querySelector({json.dumps(DIALOG)}); return !!b && !b.hidden; }})()")


def viewer_open(page: Page) -> bool:
    return frame_eval(page, f"(() => {{ const v = d.querySelector({json.dumps(VIEWER)}); return !!v && !v.hidden; }})()")


def set_value(page: Page, selector: str, text: str) -> None:
    frame_eval(page, f"(() => {{ const e = d.querySelector({json.dumps(selector)}); e.value = {json.dumps(text)}; "
                     "e.dispatchEvent(new Event('input', {bubbles: true})); })()")


def today_checks(page: Page) -> dict:
    """Today is live; the facts carried over are read from Today for the comparison."""
    today: dict = {}
    for key_ in ("plain-edit", "rules-edit", "stop-edit", "missing-edit", "resend-edit", "audit-edit"):
        state_key = key_.replace("-edit", "-dialog") if key_ not in ("plain-edit", "audit-edit") else key_
        go(page, state_key, "today")
        check(f"today {state_key}: the inline send form in the Report section", q(page, RS + " " + FORM))
        check(f"today {state_key}: no dialog", not q(page, DIALOG))
        check(f"today {state_key}: no head opener", not q(page, OPENER))
        check(f"today {state_key}: no card", not q(page, CARD))
        today[state_key] = {
            "hidden": frame_eval(page, f"[...d.querySelectorAll({json.dumps(FORM + ' input[type=hidden]')})].map(e => [e.name, e.value])"),
            "from": values(page, FORM + " [data-report-from] option"),
            "fromSelected": value(page, FORM + " [data-report-from]"),
            "to": values(page, FORM + " input[name=toRecipients]"),
            "cc": values(page, FORM + " input[name=ccRecipients]"),
            "message": value(page, FORM + " #report-message"),
            "messageRequired": attr(page, FORM + " #report-message", "required") is not None,
            "messageMax": attr(page, FORM + " #report-message", "maxlength"),
            "fileName": text_in(page, FORM + " [data-report-file-name]").strip(),
            "attach": frame_eval(page, f"[...d.querySelectorAll({json.dumps(FORM + ' [data-report-attach-choice]')})].map(e => e.getAttribute('data-report-attach-choice'))"),
            "questions": n(page, FORM + " [data-report-question]"),
            "holds": n(page, FORM + " [data-report-hold]"),
            "stop": q(page, FORM + " [data-report-stop]"),
            "missing": n(page, FORM + " [data-report-missing-companion]"),
            "submit": q(page, FORM + " button[type=submit]"),
            "alreadySent": text_in(page, FORM + " [data-report-already-sent]").strip(),
            "nextSend": "Send report" in texts(page, "[data-next-step] [data-next-label]"),
        }
    go(page, "plain-read", "today")
    check("today plain-read: the greyed read cells", q(page, RS + " [data-send-report-read]"))
    go(page, "audit-read", "today")
    check("today audit-read: Views card, Figures, no Original report card", q(page, "[data-case-views]") and q(page, FIGURES) and not q(page, CARD))
    return today


def dialog_checks(page: Page, today: dict, facts: dict) -> None:
    # A: the openers.
    go(page, "plain-edit", "proposal")
    check("plain-edit: Send report is the Report head's primary", text_in(page, RS + " .panel-actions " + OPENER).strip() == "Send report")
    check("plain-edit: the only primary in the head", n(page, RS + " .panel-head .btn--primary") == 1)
    check("plain-edit: the section holds no form", not q(page, RS + " " + FORM))
    check("plain-edit: the dialog holds the one form", n(page, DIALOG + " " + FORM) == 1 and n(page, FORM) == 1)
    check("plain-edit: the dialog is closed until opened", not dialog_open(page))
    check("plain-edit: the Next action step opens the dialog",
          q(page, "[data-next-step] button[data-dialog-open=case-send-report-dialog]") == today["plain-edit"]["nextSend"])
    click(page, OPENER)
    check("plain-edit: the head opener opens the dialog", dialog_open(page))
    check("plain-edit: the shell is inert behind it", frame_eval(page, "!!d.querySelector('.app-shell [inert], .app-shell[inert]') || d.querySelector('#case-main').closest('[inert]') !== null"))
    click(page, DIALOG + " .dialog-close")
    check("plain-edit: × closes it", not dialog_open(page))
    click(page, "[data-next-step] button[data-dialog-open=case-send-report-dialog]")
    check("plain-edit: the Next action opener opens the dialog", dialog_open(page))
    click(page, DIALOG + " footer [data-dialog-close]")
    check("plain-edit: Cancel closes it", not dialog_open(page))
    go(page, "plain-read", "proposal")
    check("plain-read: no head opener while reading", not q(page, OPENER))
    check("plain-read: no dialog while reading", not q(page, DIALOG))
    check("plain-read: the greyed read cells are gone (G)", not q(page, RS + " [data-send-report-read]"))
    check("plain-read: the preview card stays", q(page, RS + " [data-report-preview-card]"))

    # B–D: carried over, Subject, Files.
    for state_key in ("plain-dialog", "rules-dialog", "stop-dialog", "missing-dialog", "resend-dialog", "audit-dialog"):
        live = today[state_key if state_key in today else state_key.replace("-dialog", "-edit")]
        f = facts[state_key]
        go(page, state_key, "proposal")
        check(f"{state_key}: opens on the dialog preset", dialog_open(page))
        check(f"{state_key}: the composer shape", q(page, DLG + ".mail-compose-dialog.dialog--send"))
        check(f"{state_key}: the dialog is titled Send report", text_in(page, DLG + " .dialog-head h2").strip() == "Send report")
        check(f"{state_key}: eyebrow names the report", contents(page, DLG + " .dialog-head .eyebrow") == [f"Report · {f['reference']}"])
        hidden = frame_eval(page, f"[...d.querySelectorAll({json.dumps(FORM + ' input[type=hidden]')})].filter(e => !/^(fileName-|secondFileName-)/.test(e.name)).map(e => [e.name, e.value])")
        check(f"{state_key}: every hidden field carried over", sorted(map(tuple, hidden)) == sorted(map(tuple, live["hidden"])))
        check(f"{state_key}: From options as Today", values(page, FORM + " #report-from option") == live["from"])
        check(f"{state_key}: From starts on Today's default", value(page, FORM + " #report-from") == live["fromSelected"])
        check(f"{state_key}: To as Today", values(page, FORM + " input[name=toRecipients]") == live["to"])
        check(f"{state_key}: Cc as Today", values(page, FORM + " input[name=ccRecipients]") == live["cc"])
        check(f"{state_key}: Message as Today, required, 5000", value(page, FORM + " #report-message") == live["message"]
              and attr(page, FORM + " #report-message", "required") is not None and attr(page, FORM + " #report-message", "maxlength") == live["messageMax"])
        check(f"{state_key}: Subject prefilled with the derived subject (C)", value(page, FORM + " input[name=subject]") == f["subject"])
        check(f"{state_key}: Subject is editable", attr(page, FORM + " input[name=subject]", "readonly") is None and attr(page, FORM + " input[name=subject]", "disabled") is None)
        check(f"{state_key}: field order From, To, Cc, Subject, Message, Files",
              contents(page, FORM + " .mail-compose-addresses > .field > label, " + FORM + " .mail-compose-subject > label, " + FORM + " .mail-compose-message > label, " + FORM + " .mail-compose-attachments > legend")[:6]
              == ["From", "To", "Cc", "Subject", "Message", "Files"])
        rows = frame_eval(page, f"[...d.querySelectorAll({json.dumps(ROW)})].map(e => [e.getAttribute('data-v48-file'), e.querySelector('[data-v48-file-open]').getAttribute('data-file-name'), e.querySelector('.choice').classList.contains('is-static'), !!e.querySelector('.choice input[type=checkbox]:checked'), e.querySelector('small').innerText])")
        kinds = [row[0] for row in rows]
        check(f"{state_key}: a row per live Attach choice", [k for k in kinds if not k.startswith(("other-", "estimate-"))] == live["attach"])
        check(f"{state_key}: the report row is named as the send names it", rows[0][1] == live["fileName"] and rows[0][0] == "AssessmentReport")
        check(f"{state_key}: the report tick is static, on", rows[0][2])
        fee = next((row for row in rows if row[0] == "FeeNote"), None)
        check(f"{state_key}: the fee note row is a tick, on", fee is not None and not fee[2] and fee[3])
        for row in rows:
            if row[0] in ("RepairSpecification", "ImagePack"):
                check(f"{state_key}: {row[0]} unticked unless required", row[2] or not row[3])
        check(f"{state_key}: every row has a name button, kind and size", all(row[1].endswith(".pdf") and " · " in row[4] for row in rows))
        check(f"{state_key}: no File name cell, no Attach legend", not q(page, FORM + " [data-report-file-name]") and "Attach" not in texts(page, FORM + " .lbl"))
        check(f"{state_key}: Rename on every row (E)", n(page, ROW + " [data-v48-rename]") == len(rows))
        check(f"{state_key}: questions carried", n(page, FORM + " [data-report-question]") == live["questions"])
        check(f"{state_key}: holds carried", n(page, FORM + " [data-report-hold]") == live["holds"])
        check(f"{state_key}: stop carried", q(page, FORM + " [data-report-stop]") == live["stop"])
        check(f"{state_key}: missing companion carried", n(page, FORM + " [data-report-missing-companion]") == live["missing"])
        check(f"{state_key}: Send report in the foot as Today, or Cancel only", q(page, FORM + " footer button[type=submit]") == live["submit"] and q(page, FORM + " footer [data-dialog-close]"))
        check(f"{state_key}: no leftover form text outside the fields", frame_eval(page, f"[...d.querySelector({json.dumps(FORM)}).children].every(c => c.classList.contains('mail-compose-form-fields') || c.tagName === 'FOOTER' || (c.tagName === 'INPUT' && c.type === 'hidden'))"))
        if live["alreadySent"]:
            check(f"{state_key}: Already sent in the dialog", text_in(page, FORM + " [data-report-already-sent]").strip() == live["alreadySent"])
            check(f"{state_key}: Already sent under the preview card (N)", text_in(page, RS + " [data-v48-already-sent]").strip() == live["alreadySent"])

    go(page, "stop-dialog", "proposal")
    check("stop-dialog: the filed estimate is a static row", any(row for row in texts(page, ROW + " small") if row.startswith("Filed estimate")))
    check("stop-dialog: Override reason required", attr(page, FORM + " #report-stop-override", "required") is not None)
    check("stop-dialog: subject is the registration's", value(page, FORM + " input[name=subject]") == "AB12CDE Report")
    go(page, "rules-dialog", "proposal")
    check("rules-dialog: Answer before sending with Yes/No", n(page, FORM + " [data-report-question] input[type=radio]") >= 2)
    check("rules-dialog: the Cc hint", q(page, FORM + " [data-report-cc-hint]"))
    check("rules-dialog: After sending", q(page, FORM + " [data-report-after-sending]"))
    check("rules-dialog: a hold with Done", q(page, FORM + " [data-report-hold-row] [data-report-hold]"))
    go(page, "missing-dialog", "proposal")
    check("missing-dialog: no Send report", not q(page, FORM + " button[type=submit]"))
    check("missing-dialog: Cancel only in the foot", n(page, FORM + " footer button") == 1)
    go(page, "audit-dialog", "proposal")
    other = frame_eval(page, f"[...d.querySelectorAll({json.dumps(ROW)})].filter(e => e.getAttribute('data-v48-file').startsWith('other-')).map(e => [e.getAttribute('data-v48-file'), e.querySelector('[data-v48-file-open]').getAttribute('data-file-name'), e.querySelector('small').innerText, !!e.querySelector('input[type=checkbox]:checked')])")
    check("audit-dialog: the Inspection report and its three documents are rows", [row[0] for row in other] == ["other-AssessmentReport", "other-FeeNote", "other-RepairSpecification", "other-ImagePack"])
    check("audit-dialog: the Inspection report row keeps its delivery name", other and other[0][1].endswith("Total loss report.pdf"))
    check("audit-dialog: the other rows are unticked and named Inspection", all(not row[3] and row[2].startswith("Inspection · ") for row in other))
    check("audit-dialog: secondGenerationId rides the report row", q(page, ROW + "[data-v48-file=other-AssessmentReport] input[name=secondGenerationId]") and q(page, ROW + "[data-v48-file=other-AssessmentReport] input[name=secondExpectedGenerationVersion]"))

    # O: removable To / Cc boxes.
    go(page, "plain-dialog", "proposal")
    TO, CC = FORM + " #report-recipient-to", FORM + " #report-recipient-cc"
    check("recipients: each To box has its ×, hidden on the only one", n(page, TO + " [data-v48-recipient]") == 1 and not shown(page, TO + " [data-v48-remove-recipient]"))
    click(page, FORM + ' [data-add-report-recipient="report-recipient-to"]')
    check("recipients: Add To adds a box with its ×", n(page, TO + " [data-v48-recipient]") == 2 and n(page, TO + " [data-v48-remove-recipient]:not([hidden])") == 2)
    click(page, TO + " [data-v48-remove-recipient]", 1)
    check("recipients: × removes the box", n(page, TO + " [data-v48-recipient]") == 1 and n(page, TO + " input[name=toRecipients]") == 1)
    check("recipients: the last To box keeps no ×", not shown(page, TO + " [data-v48-remove-recipient]"))
    click(page, FORM + ' [data-add-report-recipient="report-recipient-cc"]')
    check("recipients: Add Cc adds a removable box", n(page, CC + " [data-v48-recipient]") == 2)
    click(page, CC + " [data-v48-remove-recipient]", 0)
    click(page, CC + " [data-v48-remove-recipient]", 0)
    check("recipients: every Cc box can go", n(page, CC + " input[name=ccRecipients]") == 0)

    # F: the viewer over the dialog.
    go(page, "plain-dialog", "proposal")
    name0 = attr(page, OPEN, "data-file-name")
    click(page, OPEN)
    check("plain-dialog: a name opens the Case viewer", viewer_open(page))
    check("plain-dialog: the viewer names the file", text_in(page, "[data-viewer-name]").strip() == name0)
    check("plain-dialog: the dialog stays open under it", dialog_open(page))
    check("plain-dialog: the viewer host is not inert", not frame_eval(page, "d.querySelector('[data-case-viewer-host]').hasAttribute('inert')"))
    top = frame_eval(page, "(() => { const e = d.elementFromPoint(d.documentElement.clientWidth / 2, d.documentElement.clientHeight / 2); return !!(e && e.closest('[data-case-viewer]')); })()")
    check("plain-dialog: the viewer is on top", top)
    key(page, "Escape")
    check("plain-dialog: Escape closes the viewer first", not viewer_open(page) and dialog_open(page))
    check("plain-dialog: focus returns to the name", frame_eval(page, "d.activeElement && d.activeElement.hasAttribute('data-v48-file-open')"))
    check("plain-dialog: the host is inert again", frame_eval(page, "d.querySelector('[data-case-viewer-host]').hasAttribute('inert')"))
    key(page, "Escape")
    check("plain-dialog: a second Escape closes the dialog", not dialog_open(page))
    go(page, "plain-viewer", "proposal")
    check("plain-viewer: the preset opens the viewer over the dialog", viewer_open(page) and dialog_open(page))

    # E: Rename and Reset.
    go(page, "plain-dialog", "proposal")
    report_row = ROW + "[data-v48-file=AssessmentReport]"
    default = attr(page, report_row, "data-v48-default")
    click(page, report_row + " [data-v48-rename]")
    check("rename: the name becomes an input of its stem", shown(page, report_row + " [data-v48-rename-row]") and value(page, report_row + " [data-v48-rename-row] input") == default[:-4])
    check("rename: .pdf stays beside it", text_in(page, report_row + " [data-v48-rename-row] .mono").strip() == ".pdf")
    check("rename: Reset offered", shown(page, report_row + " [data-v48-rename-reset]"))
    set_value(page, report_row + " [data-v48-rename-row] input", "QDOS3100042 report for Northline")
    key(page, "Enter")
    check("rename: Enter keeps the new name with .pdf", attr(page, report_row + " " + OPEN, "data-file-name") == "QDOS3100042 report for Northline.pdf"
          and text_in(page, report_row + " " + OPEN).strip() == "QDOS3100042 report for Northline.pdf")
    check("rename: the posted name is filled", value(page, report_row + " [data-v48-file-name]") == "QDOS3100042 report for Northline.pdf")
    click(page, report_row + " [data-v48-rename]")
    click(page, report_row + " [data-v48-rename-reset]")
    check("rename: Reset restores the policy name", attr(page, report_row + " " + OPEN, "data-file-name") == default)
    check("rename: Reset clears the posted name", value(page, report_row + " [data-v48-file-name]") == "")
    go(page, "resend-dialog", "proposal")
    click(page, report_row + " [data-v48-rename]")
    check("resend rename: the resend dot stays in the stem", value(page, report_row + " [data-v48-rename-row] input").endswith("report."))
    key(page, "Escape")
    check("resend rename: Escape cancels", not shown(page, report_row + " [data-v48-rename-row]") and dialog_open(page))
    go(page, "plain-rename", "proposal")
    check("plain-rename: the preset starts the rename", shown(page, report_row + " [data-v48-rename-row]"))

    # The post: what Send report would send.
    go(page, "rules-dialog", "proposal")
    click(page, FORM + " footer button[type=submit]")
    check("rules-dialog: Send with questions unanswered posts nothing", page.evaluate("window.__mock.lastPost") is None and dialog_open(page))
    frame_eval(page, f"[...d.querySelectorAll({json.dumps(FORM + ' [data-report-question]')})].forEach(qn => qn.querySelector('input[value=true]').checked = true)")
    frame_eval(page, f"[...d.querySelectorAll({json.dumps(FORM + ' [data-report-hold]')})].forEach(h => h.checked = true)")
    click(page, FORM + " footer button[type=submit]")
    posted = page.evaluate("window.__mock.lastPost") or []
    names = [pair[0] for pair in posted]
    check("rules-dialog: Send posts the live fields and Subject", all(name in names for name in ("operationKey", "fromMailboxId", "toRecipients", "coveringMessage", "attach", "holdsDone", "subject"))
          and any(name.startswith("decision-") for name in names))
    check("rules-dialog: the dialog closes after Send", not dialog_open(page))
    go(page, "stop-dialog", "proposal")
    click(page, FORM + " footer button[type=submit]")
    check("stop-dialog: Send without an override reason posts nothing", page.evaluate("window.__mock.lastPost") is None and dialog_open(page))


def card_checks(page: Page, facts: dict) -> None:
    for state_key in ("audit-edit", "audit-read"):
        go(page, state_key, "proposal")
        check(f"{state_key}: the card after Figures (I)", frame_eval(page, f"(d.querySelector({json.dumps(CARD)}) || {{}}).previousElementSibling === d.querySelector({json.dumps(FIGURES)})"))
        check(f"{state_key}: titled Original report (J)", text_in(page, CARD + " h2").strip() == "Original report")
        check(f"{state_key}: the rows (L)", texts(page, CARD + " dt") == ["Repair cost inc VAT", "Salvage value", "Engineer's Value"])
        check(f"{state_key}: the figures as the aside draws money", texts(page, CARD + " dd") == ["£7,850.00", "£1,250.00", "£5,000.00 (Cazana)"])
        check(f"{state_key}: the Figures card is unchanged", texts(page, FIGURES + " dt") == ["Repair cost inc VAT", "Engineer's Value", "Repair cost of value"])
        check(f"{state_key}: the card is in the aside", frame_eval(page, f"!!d.querySelector({json.dumps(CARD)}).closest('[data-case-aside]')"))
    go(page, "audit-repairable", "proposal")
    check("audit-repairable: no Salvage value row", texts(page, CARD + " dt") == ["Repair cost inc VAT", "Engineer's Value"])
    check("audit-repairable: the guide is Glass's", texts(page, CARD + " dd")[-1] == "£5,000.00 (Glass's)")
    go(page, "audit-inspection", "proposal")
    check("audit-inspection: no card on the Inspection view", not q(page, CARD) and q(page, '[data-case-view-row="inspection"] [aria-current="page"]'))
    for state_key in ("plain-edit", "plain-read"):
        go(page, state_key, "proposal")
        check(f"{state_key}: no card on an Inspection Case", not q(page, CARD))
    go(page, "audit-read", "proposal", opt="card:before-figures")
    check("variable card:before-figures", frame_eval(page, f"(d.querySelector({json.dumps(CARD)}) || {{}}).nextElementSibling === d.querySelector({json.dumps(FIGURES)})"))
    go(page, "audit-read", "proposal", opt="money:pounds")
    check("variable money:pounds", texts(page, CARD + " dd") == ["£7,850", "£1,250", "£5,000 (Cazana)"])


def layout_checks(page: Page) -> None:
    for width, height in VIEWPORTS:
        page.set_viewport_size({"width": width, "height": height})
        go(page, "plain-dialog", "proposal")
        box = rect(page, DLG)
        if width >= 1440:
            check(f"{width}: the dialog is 880 wide ({box['w']:.0f})", abs(box["w"] - 880) <= 2)
        else:
            check(f"{width}: the dialog fits the viewport ({box['w']:.0f})", box["w"] <= width - 20)
        check(f"{width}: the foot is inside the viewport", rect(page, FORM + " footer")["bottom"] <= height + 1)
        check(f"{width}: Files under the message", rect(page, FORM + " .mail-compose-attachments")["y"] >= rect(page, FORM + " .mail-compose-message")["y"])
        go(page, "plain-dialog", "proposal", opt="width:1100")
        box = rect(page, DLG)
        check(f"{width}: variable width:1100 ({box['w']:.0f})", abs(box["w"] - 1100) <= 2 if width >= 1440 else box["w"] <= width - 20)
        go(page, "plain-dialog", "proposal", opt="files:beside")
        files, message = rect(page, FORM + " .mail-compose-attachments"), rect(page, FORM + " .mail-compose-message")
        if width >= 900:
            check(f"{width}: variable files:beside puts Files right of the message", files["x"] >= message["right"] - 1)
        else:
            check(f"{width}: variable files:beside stacks at this width", files["y"] >= message["y"])
        go(page, "audit-read", "proposal")
        card, aside = rect(page, CARD), rect(page, "[data-case-aside]")
        if width >= 1441:
            check(f"{width}: the card in the 285px aside ({card['w']:.0f})", abs(card["w"] - 285) <= 2 and card["x"] >= aside["x"] - 1)
        elif width >= 761:
            check(f"{width}: the card in the folded two-up strip (M)", card["y"] < rect(page, "#case-main")["y"] and card["w"] < aside["w"] * 0.6)
        else:
            check(f"{width}: the card in the single column above the sections (M)", card["y"] < rect(page, "#case-main")["y"] and card["right"] <= width + 1)
    page.set_viewport_size({"width": 1580, "height": 1000})


def main() -> None:
    shots_wanted = "--no-shots" not in sys.argv
    shots: list[dict] = []
    facts = {}
    import importlib.util
    spec = importlib.util.spec_from_file_location("states_v48", HERE / "states_v48.py")
    states = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(states)  # type: ignore[union-attr]
    for state in states.STATES:
        path = ROOT / "captured-live" / state["lane"] / f'{state["capture"]}.facts.json'
        facts[state["key"]] = json.loads(path.read_text(encoding="utf-8"))

    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--allow-file-access-from-files"], executable_path=CHROME)
        page = browser.new_page(viewport={"width": 1580, "height": 1000}, reduced_motion="reduce")
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto(MOCK + "?strip=0")
        page.wait_for_function("window.__mockReady === true", timeout=120000)
        keys = page.evaluate("window.__mock.states")

        for key_ in keys:
            meta = page.evaluate("k => window.__mock.meta(k)", key_)
            for mode in ("today", "proposal"):
                errors.clear()
                go(page, key_, mode)
                check(f"{key_} ({mode}): no page error {errors[:2]}", not errors)
                check(f"{key_} ({mode}): renders the Report section", q(page, RS))
            if meta["hasProposal"] and meta["changes"]:
                go(page, key_, "proposal", diff=True)
                check(f"{key_}: proposal marks its changes", n(page, "[data-v48-change]") > 0)

        errors.clear()
        today = today_checks(page)
        dialog_checks(page, today, facts)
        card_checks(page, facts)
        layout_checks(page)
        check(f"checks: no page or console error {errors[:2]}", not errors)

        if shots_wanted:
            SHOTS.mkdir(exist_ok=True)
            for old in SHOTS.glob("*.png"):
                old.unlink()
            number = 0
            plan = [(key_, mode) for key_ in keys for mode in ("today", "proposal")
                    if mode == "today" or page.evaluate("k => window.__mock.meta(k).hasProposal", key_)]
            for key_, mode in plan:
                meta = page.evaluate("k => window.__mock.meta(k)", key_)
                state = next(s for s in states.STATES if s["key"] == key_)
                if mode == "today" and state.get("dialog") and key_ != "plain-dialog":
                    continue  # Today of a dialog state is the inline form, shot once on plain-dialog
                number += 1
                for width, height in VIEWPORTS:
                    errors.clear()
                    page.set_viewport_size({"width": width, "height": height})
                    go(page, key_, mode)
                    page.wait_for_timeout(300)
                    name = f"{number:03d}-{key_}-{mode}-{width}.png"
                    page.screenshot(path=str(SHOTS / name))
                    shots.append({"shot": name, "state": key_, "mode": mode, "viewport": f"{width}x{height}"})
                    if state.get("dialog") and mode == "proposal":
                        box = rect(page, DLG)
                        crop = f"{number:03d}-{key_}-{mode}-{width}-dialog.png"
                        page.screenshot(path=str(SHOTS / crop), clip={"x": box["x"], "y": box["y"], "width": box["w"], "height": box["h"]})
                        shots.append({"shot": crop, "state": key_, "mode": mode, "viewport": f"{width} dialog crop"})
                        if width == 1580 and not state.get("viewer"):
                            # The whole Files list and every block, however tall.
                            frame_eval(page, f"(() => {{ const s = d.querySelector({json.dumps(DLG)}); s.style.height = 'auto'; s.style.maxHeight = 'none'; "
                                             "const f = d.querySelector('.mail-compose-form-fields'); f.style.overflow = 'visible'; return 1; })()")
                            page.evaluate("window.__mock.expand(true)")
                            box = frame_eval(page, f"(() => {{ const r = d.querySelector({json.dumps(DLG)}).getBoundingClientRect(); "
                                                   "return [r.x, r.y + d.documentElement.scrollTop, r.width, r.height]; })()")
                            full = f"{number:03d}-{key_}-{mode}-{width}-dialog-full.png"
                            page.screenshot(path=str(SHOTS / full), full_page=True, clip={"x": box[0], "y": box[1], "width": box[2], "height": box[3]})
                            shots.append({"shot": full, "state": key_, "mode": mode, "viewport": "1580 whole dialog"})
                            page.evaluate("window.__mock.expand(false)")
                    else:
                        sel = state.get("panel") or RS
                        if mode == "today" and sel == CARD:
                            sel = FIGURES
                        page.evaluate("window.__mock.expand(true)")
                        box = frame_eval(page, f"(() => {{ const e = d.querySelector({json.dumps(sel)}); if (!e) return null; const r = e.getBoundingClientRect(); "
                                               "return [r.x, r.y + d.documentElement.scrollTop, r.width, r.height]; })()")
                        if box:
                            crop = f"{number:03d}-{key_}-{mode}-{width}-{'card' if sel in (CARD, FIGURES) else 'panel'}.png"
                            page.screenshot(path=str(SHOTS / crop), full_page=True, clip={"x": box[0], "y": box[1], "width": box[2], "height": box[3]})
                            shots.append({"shot": crop, "state": key_, "mode": mode, "viewport": f"{width} crop of {sel}"})
                        if width == 1580:
                            full = f"{number:03d}-{key_}-{mode}-full.png"
                            page.screenshot(path=str(SHOTS / full), full_page=True)
                            shots.append({"shot": full, "state": key_, "mode": mode, "viewport": "1580 whole page"})
                        page.evaluate("window.__mock.expand(false)")
                    check(f"shot {name}: no console error {errors[:2]}", not errors)
            # The variables, at 1580.
            page.set_viewport_size({"width": 1580, "height": 1000})
            for key_, opt, label in (("plain-dialog", "width:1100", "width-1100"), ("plain-dialog", "files:beside", "files-beside"),
                                     ("plain-dialog", "width:1100,files:beside", "width-1100-files-beside"),
                                     ("audit-read", "card:before-figures", "card-before-figures"), ("audit-read", "money:pounds", "money-pounds")):
                number += 1
                go(page, key_, "proposal", opt=opt)
                page.wait_for_timeout(300)
                name = f"{number:03d}-{key_}-proposal-1580-opt-{label}.png"
                page.screenshot(path=str(SHOTS / name))
                shots.append({"shot": name, "state": key_, "mode": "proposal", "viewport": f"1580x1000, opt={opt}"})
                sel = DLG if key_ == "plain-dialog" else "[data-case-aside]"
                box = rect(page, sel)
                crop = f"{number:03d}-{key_}-proposal-1580-opt-{label}-crop.png"
                page.screenshot(path=str(SHOTS / crop), clip={"x": box["x"], "y": box["y"], "width": box["w"], "height": min(box["h"], 1000 - box["y"])})
                shots.append({"shot": crop, "state": key_, "mode": "proposal", "viewport": f"1580 crop, opt={opt}"})
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
