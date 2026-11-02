"""Self-check and screenshots for pegasus_v44.html.

Run from v44_planning/:  python -X utf8 build/check-v44.py
Prints one line: RESULT {"fail":[...],"okCount":N}. Writes shots/ and shots/verification.json.
Uses Python Playwright with the installed full Chromium (chromium-1223).
"""
import glob
import itertools
import json
import os
import pathlib
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = ROOT.joinpath("pegasus_v44.html").as_uri()
SHOTS = ROOT / "shots"
EXE = glob.glob(os.path.join(os.environ["LOCALAPPDATA"], "ms-playwright", "chromium-1223", "*", "chrome.exe"))[0]

STATES = ["unlinked", "linked", "query", "triage"]
PICKER = ["dialog", "inline"]
CHANGE = ["Change linked Case", "Change"]
ACTIONS = ["buttons", "links"]

# Every visible string a control may carry: live OperatorLabels / CaseWorkspaceLabels values.
LIVE_LABELS = {
    "Change linked Case", "Change", "Unlink", "Link to Case", "Place on Hold", "Close case",
    "Mark query done", "Cancel", "Confirm Action",
}

# (number, slug, query) — the states the notes cite.
SHOT_PRESETS = [
    ("001", "today-linked", "mode=today&state=linked"),
    ("002", "proposal-linked", "mode=proposal&state=linked"),
    ("003", "today-unlinked", "mode=today&state=unlinked"),
    ("004", "proposal-unlinked", "mode=proposal&state=unlinked"),
    ("005", "today-query", "mode=today&state=query"),
    ("006", "proposal-query", "mode=proposal&state=query"),
    ("007", "today-triage", "mode=today&state=triage"),
    ("008", "proposal-triage", "mode=proposal&state=triage"),
    ("009", "proposal-change-dialog", "mode=proposal&state=linked&menu=0&dialog=changeLinkedCaseDialog"),
    ("010", "proposal-link-dialog", "mode=proposal&state=unlinked&menu=0&dialog=linkCaseDialog"),
    ("011", "proposal-unlink-dialog", "mode=proposal&state=linked&menu=0&dialog=unlinkCaseDialog"),
    ("012", "today-change-dialog", "mode=today&state=linked&menu=0&dialog=changeLinkedCaseDialog"),
    ("013", "variant-inline-picker-open", "mode=proposal&state=linked&opt=picker:inline&inline=1"),
    ("014", "variant-short-label", "mode=proposal&state=linked&opt=changelabel:Change"),
    ("015", "variant-change-case-links", "mode=proposal&state=linked&opt=caseactions:links"),
    ("016", "proposal-linked-diff", "mode=proposal&state=linked&diff=1"),
]
SIZES = [(1580, 1000), (1440, 900), (760, 1000)]

fails, ok = [], 0


def check(name, cond):
    global ok
    if cond:
        ok += 1
    else:
        fails.append(name)


def opt(picker, change, actions):
    return "opt=" + ",".join([f"picker:{picker}", f"changelabel:{change}", f"caseactions:{actions}"])


def main():
    SHOTS.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=EXE)
        page = browser.new_page(viewport={"width": 1580, "height": 1000})
        errors = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))

        def go(q):
            page.goto(f"{URL}?strip=0&{q}")
            page.wait_for_timeout(60)

        # Font loads (fidelity with the app's Inter).
        go("mode=proposal&state=linked")
        page.wait_for_timeout(300)
        check("Inter font loaded", page.evaluate("document.fonts.check('13px Inter')"))

        # Today mirrors live: the markup the operator screenshotted.
        go("mode=today&state=linked")
        check("today linked: Unlink is .mail-settings-link", page.locator(".mail-settings-popover .mail-settings-link", has_text="Unlink").count() == 1)
        check("today linked: inline Case / PO input", page.locator(".mail-settings-popover #mailLinkCaseReference").is_visible())
        check("today linked: Change linked Case is button.mail-settings-item", page.locator(".mail-settings-popover button.mail-settings-item", has_text="Change linked Case").count() == 1)
        check("today linked: Case / PO label is bold (the defect)", page.evaluate("getComputedStyle(document.querySelector('label[for=mailLinkCaseReference]')).fontWeight") == "780")
        go("mode=today&state=unlinked")
        check("today unlinked: Link to Case item", page.locator("button.mail-settings-item", has_text="Link to Case").count() == 1)
        check("today unlinked: no Change case", page.locator("[data-mail-change-case]").count() == 0)

        # Proposal across every state x variable combination.
        for state, picker, change, actions in itertools.product(STATES, PICKER, CHANGE, ACTIONS):
            tag = f"{state}/{picker}/{change}/{actions}"
            go(f"mode=proposal&state={state}&{opt(picker, change, actions)}")
            pop = page.locator(".mail-settings-popover")
            check(f"{tag}: popover visible", pop.is_visible())
            check(f"{tag}: no visible input in popover when closed", page.locator(".mail-settings-popover input:visible").count() == 0)
            labels = page.evaluate("""() => [...document.querySelectorAll('.mail-settings-popover .mail-decision-label')]
                .map(e => { const s = getComputedStyle(e); return s.fontSize + '/' + s.fontWeight; })""")
            check(f"{tag}: one label style", len(set(labels)) == 1 and labels[0] == "10px/400")
            texts = page.evaluate("() => [...document.querySelectorAll('.mail-settings-popover button:not(.command-result), .mail-settings-popover a.btn, .mail-settings-links a')].map(e => e.textContent.trim())")
            check(f"{tag}: control strings are live labels", all(t in LIVE_LABELS for t in texts))
            linked = state != "unlinked"
            check(f"{tag}: Unlink only when linked", (page.locator(".mail-settings-popover button", has_text="Unlink").count() == 1) == linked)
            check(f"{tag}: Change label", (page.locator("[data-v44-change]").inner_text().strip() == (change if linked else "Link to Case")))
            has_query = state == "query"
            check(f"{tag}: Query section iff open query", (page.locator("[data-v44-section=query]").count() == 1) == has_query)
            has_cc = state in ("linked", "query")
            check(f"{tag}: Change case iff the Case allows", (page.locator("[data-v44-section=change-case]").count() == 1) == has_cc)
            if has_cc:
                want = "a.btn" if actions == "buttons" else ".mail-settings-links a"
                check(f"{tag}: Change case drawn as {actions}", page.locator(f"[data-v44-section=change-case] {want}").count() == 2)
            check(f"{tag}: Decided foot", page.locator("[data-v44-section=decided]").count() == 1)
            borders = page.evaluate("""() => [...document.querySelectorAll('.mail-settings-popover > .mail-settings-section')].slice(1)
                .map(e => getComputedStyle(e).borderTopWidth)""")
            check(f"{tag}: every section after the first is divided", all(b == "1px" for b in borders))
            # Flow: Change / Link to Case
            page.locator("[data-v44-change]").click()
            page.wait_for_timeout(40)
            if picker == "dialog":
                dlg = "#changeLinkedCaseDialog" if linked else "#linkCaseDialog"
                check(f"{tag}: dialog opens", page.locator(dlg).is_visible())
                check(f"{tag}: dialog holds Case / PO then Reason", page.evaluate(f"""() => {{
                    const d = document.querySelector('{dlg}');
                    const labels = [...d.querySelectorAll('.dialog-body label')].map(l => l.textContent.trim());
                    return labels.join('|') === 'Case / PO|Reason for action'; }}"""))
                inp = page.locator(f"{dlg} [data-v44-picker] input")
                check(f"{tag}: picker focused first", inp.evaluate("e => e === document.activeElement"))
                inp.fill("QDOS2616")
                check(f"{tag}: options appear", page.locator(f"{dlg} [data-case-picker-options]").is_visible())
                page.locator(f"{dlg} [data-case-picker-choice]").first.click()
                check(f"{tag}: choice fills", page.locator(f"{dlg} [data-v44-picker] input").input_value() == "QDOS26162")
                page.locator(f"{dlg} [data-dialog-close]").first.click()
                check(f"{tag}: dialog closes", page.locator(f"{dlg}").is_hidden())
            else:
                check(f"{tag}: inline picker revealed", page.locator("#v44InlinePicker input").is_visible())
                check(f"{tag}: aria-expanded true", page.locator("[data-v44-change]").get_attribute("aria-expanded") == "true")
                page.locator("[data-v44-inline-cancel]").click()
                check(f"{tag}: Cancel hides inline picker", page.locator("#v44InlinePicker").is_hidden())

        # Unlink dialog: the approved consequence sentence only where unlinking cancels the Case.
        for state, expect in (("linked", True), ("query", False), ("triage", False)):
            go(f"mode=proposal&state={state}&menu=0&dialog=unlinkCaseDialog")
            check(f"unlink {state}: dialog visible", page.locator("#unlinkCaseDialog").is_visible())
            check(f"unlink {state}: consequence {expect}", (page.locator("#unlinkCaseDialog .notice").count() == 1) == expect)
            check(f"unlink {state}: no picker", page.locator("#unlinkCaseDialog [data-v44-picker]").count() == 0)

        # Diff badges
        go("mode=proposal&state=linked&diff=1")
        check("diff marks changed blocks", page.locator(".v44-changed").count() >= 3)

        # Narrow viewport: the popover stays on screen.
        page.set_viewport_size({"width": 760, "height": 1000})
        for state in STATES:
            for mode in ("today", "proposal"):
                go(f"mode={mode}&state={state}")
                box = page.locator(".mail-settings-popover").bounding_box()
                check(f"760 {mode}/{state}: popover inside viewport", box and box["x"] >= 0 and box["x"] + box["width"] <= 760)
                check(f"760 {mode}/{state}: no page spill", page.evaluate("document.documentElement.scrollWidth <= innerWidth"))

        # Strip: switching state through the strip re-renders without error.
        page.set_viewport_size({"width": 1580, "height": 1000})
        page.goto(URL + "?mode=proposal&state=linked")
        page.locator("[data-strip='State'][data-value='unlinked']").click()
        check("strip switches state", page.locator("[data-v44-change]").inner_text().strip() == "Link to Case")
        page.locator("[data-strip='Mode'][data-value='today']").click()
        check("strip switches mode", page.locator("#mailLinkCaseReference").count() == 1)
        page.locator("[data-strip-reset]").click()
        page.evaluate("localStorage.clear()")

        check("no console errors", not errors)
        if errors:
            fails.extend(f"console: {e}" for e in errors[:5])

        # Screenshots
        shots = []
        for w, h in SIZES:
            page.set_viewport_size({"width": w, "height": h})
            for num, slug, q in SHOT_PRESETS:
                go(q)
                page.wait_for_timeout(120)
                name = f"{num}-{slug}-{w}.png"
                page.screenshot(path=str(SHOTS / name))
                shots.append(name)
        browser.close()

    result = {"fail": fails, "okCount": ok}
    (SHOTS / "verification.json").write_text(json.dumps({"result": result, "shots": shots}, indent=2), encoding="utf-8")
    print("RESULT " + json.dumps(result))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
