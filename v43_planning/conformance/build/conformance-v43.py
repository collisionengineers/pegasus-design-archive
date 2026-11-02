"""Stage 2 conformance: the implemented Case details beside the signed-off Proposal.

Renders pegasus_v43_conformance.html (captures of task/case-details-claim-source) at the
mockup's three widths, crops the Case details section, and writes, for each state,
cNNN-<state>-<width>.png and a side-by-side sNNN-<state>-<width>.png (Proposal shot left,
implemented right) into ../shots/. NNN is the mockup's Proposal shot number.

Run from conformance/: python -X utf8 build/conformance-v43.py
"""
from __future__ import annotations

import glob
import json
import os
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SHOTS = ROOT / "shots"
MOCK_SHOTS = ROOT.parent / "shots"
PAGE = (ROOT / "pegasus_v43_conformance.html").resolve().as_uri()
CHROME = next(iter(sorted(glob.glob(os.path.expandvars(
    r"%LOCALAPPDATA%\ms-playwright\chromium-*\chrome-win64\chrome.exe")), reverse=True)), None)
VIEWPORTS = [(1580, 1000), (1440, 900), (760, 1000)]
STATES = [("002", "case-read"), ("004", "case-edit"), ("006", "case-read-bare"),
          ("008", "case-edit-bare"), ("010", "case-edit-claim-source-changed")]


def main() -> None:
    SHOTS.mkdir(exist_ok=True)
    for old in SHOTS.glob("*.png"):
        old.unlink()
    written = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--allow-file-access-from-files"], executable_path=CHROME)
        page = browser.new_page(viewport={"width": 1580, "height": 1000}, reduced_motion="reduce")
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto(PAGE + "?strip=0")
        page.wait_for_function("window.__mockReady === true", timeout=120000)
        for number, key in STATES:
            for width, height in VIEWPORTS:
                page.set_viewport_size({"width": width, "height": height})
                page.evaluate("([k]) => window.__mock.go(k, 'today', {})", [key])
                page.wait_for_timeout(400)
                page.evaluate("window.__mock.expand(true)")
                box = page.evaluate(
                    "() => { const d = window.__mock.doc(); const r = d.querySelector('#section-overview').getBoundingClientRect();"
                    " return [r.x, r.y + d.documentElement.scrollTop, r.width, r.height]; }")
                built = SHOTS / f"c{number}-{key}-{width}.png"
                page.screenshot(path=str(built), full_page=True,
                                clip={"x": box[0], "y": box[1], "width": box[2], "height": box[3]})
                page.evaluate("window.__mock.expand(false)")
                mock = MOCK_SHOTS / f"{number}-{key}-proposal-{width}-case-details.png"
                left, right = Image.open(mock), Image.open(built)
                pair = Image.new("RGB", (left.width + right.width + 24, max(left.height, right.height)), "white")
                pair.paste(left, (0, 0))
                pair.paste(right, (left.width + 24, 0))
                side = SHOTS / f"s{number}-{key}-{width}.png"
                pair.save(side)
                written.append({"state": key, "width": width, "mockup": mock.name, "built": built.name,
                                "sideBySide": side.name, "heightMockup": left.height, "heightBuilt": right.height})
        browser.close()
    (SHOTS / "conformance.json").write_text(json.dumps({"errors": errors, "shots": written}, indent=2), encoding="utf-8")
    print(json.dumps({"errors": errors, "count": len(written)}))


if __name__ == "__main__":
    main()
