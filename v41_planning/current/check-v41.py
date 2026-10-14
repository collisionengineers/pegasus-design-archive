"""Self-check run and screenshots for the v41 full-application UX/UI mockup round.

1. Opens v41-selfcheck.html in headless Chromium (file access allowed) and reads
   its RESULT line: every state, dialog, variable, and Proposal vs Today assertion
   across pegasus_shell_v41.html (18 states) and pegasus_case_workspace_v41.html (9 states).
2. Takes the design authority's three captures (1580x1000, 1440x900, 760x1000)
   of every page and state cited in the v41 notes and pages/ folders, plus a
   whole-page capture at 1580, recording console errors on every load.
Writes v41-shots/verification.json and prints RESULT {"fail":[],"okCount":N}.
"""
from __future__ import annotations

import glob
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SHOTS = HERE / "v41-shots"
SHELL_MOCK = (HERE / "pegasus_shell_v41.html").resolve().as_uri()
CASE_MOCK = (HERE / "pegasus_case_workspace_v41.html").resolve().as_uri()
CHROME = next(
    iter(
        sorted(
            glob.glob(
                os.path.expandvars(
                    r"%LOCALAPPDATA%\ms-playwright\chromium-*\chrome-win64\chrome.exe"
                )
            ),
            reverse=True,
        )
    ),
    None,
)
VIEWPORTS = [(1580, 1000), (1440, 900), (760, 1000)]

# (name, mock_uri, query, focus_selector)
SHOTLIST = [
    ("auth-signin", SHELL_MOCK, "state=auth-signin&design=proposal", None),
    ("auth-consent", SHELL_MOCK, "state=auth-consent&design=proposal", None),
    ("auth-consent-today", SHELL_MOCK, "state=auth-consent&design=today", None),
    ("auth-errors", SHELL_MOCK, "state=auth-errors&design=proposal", None),
    ("shell-dialogs", SHELL_MOCK, "state=shell-dialogs&design=proposal", None),
    ("work-centre", SHELL_MOCK, "state=work-centre&design=proposal", None),
    ("work-centre-tabs", SHELL_MOCK, "state=work-centre-tabs&design=proposal", None),
    ("search", SHELL_MOCK, "state=search&design=proposal", None),
    ("search-today", SHELL_MOCK, "state=search&design=today", None),
    ("inbox", SHELL_MOCK, "state=inbox&design=proposal", None),
    ("inbox-today", SHELL_MOCK, "state=inbox&design=today", None),
    ("mail-message", SHELL_MOCK, "state=mail-message&design=proposal", None),
    ("upload-review", SHELL_MOCK, "state=upload-review&design=proposal", None),
    ("cases-queue", SHELL_MOCK, "state=cases-queue&design=proposal", None),
    ("create-case", SHELL_MOCK, "state=create-case&design=proposal", None),
    ("triage-case", SHELL_MOCK, "state=triage-case&design=proposal", None),
    ("unidentified-images", SHELL_MOCK, "state=unidentified-images&design=proposal", None),
    ("admin-accounts", SHELL_MOCK, "state=admin-accounts&design=proposal", None),
    ("admin-contacts", SHELL_MOCK, "state=admin-contacts&design=proposal", None),
    ("admin-config-mail", SHELL_MOCK, "state=admin-config-mail&design=proposal", None),
    ("admin-logs-ops", SHELL_MOCK, "state=admin-logs-ops&design=proposal", None),
    ("case-overview", CASE_MOCK, "state=v41-overview&design=proposal", None),
    ("case-delivery-rules", CASE_MOCK, "state=delivery-rules&design=proposal", "#section-report"),
    ("case-delivery-plain", CASE_MOCK, "state=delivery-plain&design=proposal", "#section-report"),
    ("case-delivery-stop", CASE_MOCK, "state=delivery-stop&design=proposal", "#section-report"),
    ("case-delivery-missing", CASE_MOCK, "state=delivery-missing&design=proposal", "#section-report"),
    ("case-next-action-tasks", CASE_MOCK, "state=next-action-tasks&design=proposal", None),
    ("case-tasks-dialog", CASE_MOCK, "state=tasks-dialog&design=proposal", "#section-tasks"),
    ("case-engineer-read", CASE_MOCK, "state=engineer-read&design=proposal", None),
    ("case-engineer-edit", CASE_MOCK, "state=engineer-edit&design=proposal", None),
]


def main() -> None:
    SHOTS.mkdir(exist_ok=True)
    for old in SHOTS.glob("*.png"):
        old.unlink()
    fails: list[str] = []
    ok = 0
    shots: list[dict[str, str]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            args=["--allow-file-access-from-files"], executable_path=CHROME
        )
        page = browser.new_page(viewport={"width": 1700, "height": 1100})
        page.goto((HERE / "v41-selfcheck.html").resolve().as_uri())
        page.wait_for_function(
            "document.getElementById('out').textContent.startsWith('RESULT')",
            timeout=120000,
        )
        selfcheck = json.loads(
            page.locator("#out").text_content().removeprefix("RESULT ")
        )
        page.close()
        fails += [f"selfcheck: {f}" for f in selfcheck["fail"]]
        ok += selfcheck["okCount"]
        shot_page = browser.new_page(
            viewport={"width": 1580, "height": 1000}, device_scale_factor=1
        )
        errors: list[str] = []
        shot_page.on(
            "console",
            lambda m: errors.append(m.text) if m.type == "error" else None,
        )
        shot_page.on("pageerror", lambda e: errors.append(str(e)))
        shot_page.goto(f"{(HERE / 'pegasus_v41.html').resolve().as_uri()}?state=work-centre&design=proposal&strip=0")
        shot_page.wait_for_function("window.__mockReady === true")
        for number, (name, mock_uri, query, focus) in enumerate(SHOTLIST, start=1):
            qparts = dict(part.split("=", 1) for part in query.split("&") if "=" in part)
            st = qparts.get("state", "work-centre")
            ds = qparts.get("design", "proposal")
            for width, height in VIEWPORTS:
                errors.clear()
                shot_page.set_viewport_size({"width": width, "height": height})
                shot_page.evaluate(
                    "([s, d]) => { window.__mock.setDesign(d); window.__mock.go(s); window.scrollTo(0, 0); }",
                    [st, ds],
                )
                shot_page.wait_for_timeout(60)
                if errors:
                    fails.append(f"{name} {width}: console {errors[:2]}")
                else:
                    ok += 1
                if focus:
                    shot_page.evaluate(
                        "s => { const el = document.querySelector(s); if (el) window.scrollTo(0, el.getBoundingClientRect().top + scrollY - 64); }",
                        focus,
                    )
                    shot_page.wait_for_timeout(40)
                shot = SHOTS / f"{number:02d}-{name}-{width}.png"
                shot_page.screenshot(path=str(shot))
                shots.append(
                    {
                        "shot": shot.name,
                        "mock": Path(mock_uri).name,
                        "query": query,
                        "viewport": f"{width}x{height}",
                    }
                )
                if width == 1580:
                    full = SHOTS / f"{number:02d}-{name}-full.png"
                    shot_page.screenshot(path=str(full), full_page=True)
                    shots.append(
                        {
                            "shot": full.name,
                            "mock": Path(mock_uri).name,
                            "query": query,
                            "viewport": "1580 whole page",
                        }
                    )
        shot_page.close()
        browser.close()
    result = {"fail": fails, "okCount": ok}
    (SHOTS / "verification.json").write_text(
        json.dumps(
            {
                "checkedAtUtc": datetime.now(timezone.utc).isoformat(),
                "selfcheck": selfcheck,
                "result": result,
                "shots": shots,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("RESULT " + json.dumps(result))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
