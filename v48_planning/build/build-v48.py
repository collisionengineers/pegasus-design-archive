#!/usr/bin/env python3
"""Build pegasus_v48.html: the v48 Send report dialog and Original report card round, drawn over the live application.

Every state's Today view is a page captured from the running application on the
current checkout (captured-live/<lane>/<name>.html, written by the excluded
ZzMockupCapture* scratch tests). It is not redrawn. The Proposal view is the same
capture with the registered patches from proposals_v48.py applied, each marked
with data-v48-change so the Diff badges show what changed. A state may name a
"proposal" capture instead: the same Case captured with the proposed readiness
item (the scratch MOCKUP_V48_RULE switch in the capture worktree), so the blocked
page is the application's own rendering; the patches then apply to that capture.

One self-contained file: the live stylesheets, scripts, icon sprite and images
are inlined once, and each state is composed into a frame at runtime with the
live site.js running inside it. Requests are stubbed and links between captured
pages switch state.
"""
from __future__ import annotations

import base64
import copy
import gzip
import json
import pathlib
import re
import sys

from bs4 import BeautifulSoup, Tag

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent  # v48_planning/: the mockup, captured-live/, shots/ and pages/ sit beside build/
CAPTURED = ROOT / "captured-live"
# The live assets copied beside the captures, so styles and scripts match the captured markup.
SOURCE = CAPTURED / "_source"
WWWROOT = SOURCE / "wwwroot"
OUT = ROOT / "pegasus_v48.html"

sys.path.insert(0, str(HERE))
import proposals_v48 as proposals  # noqa: E402
from states_v48 import ROUTES, STATES  # noqa: E402


FINGERPRINT = re.compile(r"\.[a-z0-9]{10}(?=\.[a-z0-9]+$)")


def unfingerprint(url: str) -> str:
    """/css/site.dzrw21ap95.css -> /css/site.css (static assets are served fingerprinted)."""
    return FINGERPRINT.sub("", url.split("?")[0])


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def parse(text: str) -> BeautifulSoup:
    return BeautifulSoup(text, "lxml")


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

def data_uri(path: pathlib.Path) -> str:
    mime = {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml", ".woff2": "font/woff2", ".ico": "image/x-icon",
    }.get(path.suffix.lower(), "application/octet-stream")
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def css_asset(name: str) -> str:
    css = read(WWWROOT / "css" / name)

    def repl(match: re.Match[str]) -> str:
        raw = match.group(1).strip().strip("'\"")
        if raw.startswith("data:"):
            return match.group(0)
        rel = raw.split("?")[0].lstrip("/")
        while rel.startswith("../"):
            rel = rel[3:]
        candidate = WWWROOT / rel
        if not candidate.exists():
            stem = candidate.name.split(".")[0]
            matches = sorted(candidate.parent.glob(f"{stem}*{candidate.suffix}")) if candidate.parent.exists() else []
            candidate = matches[0] if matches else candidate
        return f'url("{data_uri(candidate)}")' if candidate.exists() else match.group(0)

    return re.sub(r"url\(([^)]+)\)", repl, css)


# Proposal-only behaviour, inert on Today markup (which never opens the viewer from a
# dialog). Each correction must match exactly once (origin/dev 8da7957ce).
#  F: the Case viewer opens over the Send report dialog. The dialog's document-level
#     keydown (site.js) yields while the viewer is open, so Escape and Tab reach the
#     viewer's own handler first; the viewer lifts the inert the dialog put on its host
#     (site.js inertOutside spares only [data-dialog] siblings) and restores it on close.
JS_CORRECTIONS = {
    "site.js": [
        (
            "                if (openDialogStack[openDialogStack.length - 1] !== dialog) {\n",
            "                if (document.body.classList.contains('has-viewer')) { return; }\n"
            "                if (openDialogStack[openDialogStack.length - 1] !== dialog) {\n",
        ),
    ],
    "case-workspace.js": [
        (
            "            document.body.classList.add('has-viewer');\n",
            "            document.body.classList.add('has-viewer');\n"
            "            var v48Wrap = host.closest('[data-case-viewer-host]');\n"
            "            if (v48Wrap && v48Wrap.hasAttribute('inert')) { v48Wrap.removeAttribute('inert'); state.v48Reinert = v48Wrap; }\n",
        ),
        (
            "            document.body.classList.remove('has-viewer');\n",
            "            document.body.classList.remove('has-viewer');\n"
            "            if (state.v48Reinert) { state.v48Reinert.setAttribute('inert', ''); state.v48Reinert = null; }\n",
        ),
    ],
}


def js_asset(name: str) -> str:
    source = read(WWWROOT / "js" / name)
    for old, new in JS_CORRECTIONS.get(name, []):
        count = source.count(old)
        if count != 1:
            raise SystemExit(f"{name}: correction matched {count} times, expected 1: {old[:60]!r}")
        source = source.replace(old, new)
    return re.sub(r"</(script)", r"<\\/\1", source, flags=re.IGNORECASE)


# A grey placeholder for photographs served by handlers that a capture cannot inline.
PLACEHOLDER_IMAGE = (
    "data:image/svg+xml;base64,"
    + base64.b64encode(
        b'<svg xmlns="http://www.w3.org/2000/svg" width="320" height="240">'
        b'<rect width="320" height="240" fill="#d9dde1"/>'
        b'<path d="M40 190l70-80 50 55 40-35 80 60z" fill="#b9c0c6"/>'
        b'<circle cx="230" cy="80" r="22" fill="#c6ccd1"/></svg>'
    ).decode("ascii")
)


# ---------------------------------------------------------------------------
# Captured pages
# ---------------------------------------------------------------------------

class Capture:
    def __init__(self, lane: str, name: str):
        self.lane, self.name = lane, name
        path = CAPTURED / lane / f"{name}.html"
        if not path.exists():
            raise FileNotFoundError(path)
        doc = parse(read(path))
        self.css: list[str] = []
        for link in doc.select('link[rel~="stylesheet"][href]'):
            file = unfingerprint(link["href"]).rsplit("/", 1)[-1]
            if file.endswith(".css") and (WWWROOT / "css" / file).exists() and file not in self.css:
                self.css.append(file)
        self.js: list[str] = []
        for script in doc.select("script[src]"):
            file = unfingerprint(script["src"]).rsplit("/", 1)[-1]
            if (WWWROOT / "js" / file).exists() and file not in self.js:
                self.js.append(file)
        for node in doc.select("script, link"):
            node.decompose()
        self.html_attrs = dict(doc.html.attrs) if doc.html else {}
        self.body_attrs = dict(doc.body.attrs) if doc.body else {}
        self.body = doc.body
        self._fill_lazy_sections()
        self._inline_images()
        self._drop_sprite()

    def _fill_lazy_sections(self) -> None:
        for placeholder in self.body.select("[data-lazy]"):
            key = placeholder.get("data-lazy")
            fragment = CAPTURED / self.lane / f"{self.name}.section-{key}.html"
            if not fragment.exists():
                continue
            frag = parse(read(fragment))
            for script in frag.select("script"):
                script.decompose()
            nodes = [node for node in (frag.body.contents if frag.body else []) if getattr(node, "name", None)]
            if not nodes:
                continue
            for node in nodes:
                placeholder.insert_before(copy.copy(node))
            placeholder.decompose()

    def _inline_images(self) -> None:
        for img in self.body.select("img[src]"):
            src = img["src"]
            if src.startswith("data:"):
                continue
            local = WWWROOT / unfingerprint(src).lstrip("/")
            ok = src.startswith("/") and local.is_file()
            img["src"] = data_uri(local) if ok else PLACEHOLDER_IMAGE
            img.attrs.pop("srcset", None)

    def _drop_sprite(self) -> None:
        # The Lucide sprite is inlined once and added to every composed frame.
        for svg in self.body.find_all("svg"):
            if svg.find("symbol") and not svg.find("use"):
                svg.decompose()
        # Since PR 1449 (finding-inline-sprite) the live pages reference a static
        # fingerprinted sprite file (/images/lucide-sprite.<hash>.svg#icon-x) and
        # publish its address on <html data-icon-sprite> for site.js. The mockup
        # inlines the sprite once, so every reference becomes a fragment and the
        # attribute is emptied (site.js then draws '#' + name).
        for use in self.body.select("use[href]"):
            href = use["href"]
            if "lucide-sprite" in href and "#" in href:
                use["href"] = "#" + href.split("#", 1)[1]
        if "data-icon-sprite" in self.html_attrs:
            self.html_attrs["data-icon-sprite"] = ""

    def html(self) -> str:
        return self.body.decode_contents()


def pack(markup: str) -> str:
    """A page body, gzip-compressed and base64-encoded; the runtime unpacks it."""
    return base64.b64encode(gzip.compress(markup.encode("utf-8"), 9)).decode("ascii")


def sprite_html() -> str:
    # Captures up to 16 October 2026 carried the Razor partial; from PR 1449 the
    # sprite is the static file wwwroot/images/lucide-sprite.svg (copied into
    # _source/wwwroot with the other assets). Either shape is inlined hidden.
    partial = SOURCE / "_LucideSprite.cshtml"
    if partial.exists():
        raw = read(partial)
        return re.sub(r"@\*[\s\S]*?\*@", "", raw).strip()
    raw = read(WWWROOT / "images" / "lucide-sprite.svg").strip()
    raw = re.sub(r"^<\?xml[^>]*\?>\s*", "", raw)
    if re.match(r"<svg\b", raw) and "sprite-sheet" not in raw.split(">", 1)[0]:
        # The partial hid itself with the sprite-sheet class (the production CSP
        # discards inline styles); the mockup has no CSP, so both are set.
        raw = re.sub(r"^<svg\b", '<svg class="sprite-sheet" style="display:none" aria-hidden="true"', raw, count=1)
    return raw


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def prepare_capture(state: dict) -> Capture:
    capture = Capture(state["lane"], state["capture"])
    proposals.preset(state["key"], capture.body, state)
    return capture


def build() -> None:
    entries, missing = [], []
    bodies: dict[str, str] = {}
    css_names, js_names = {"site.css"}, {"site.js"}
    routes: list[list[str]] = []

    for state in STATES:
        try:
            capture = prepare_capture(state)
            state["facts"] = proposals.facts_for(state)
        except FileNotFoundError as error:
            missing.append(f'{state["key"]}: {error}')
            continue
        if "case-workspace.css" not in capture.css:
            raise SystemExit(f'{state["key"]}: case-workspace.css is not linked by the capture')
        today_html = capture.html()
        if state.get("proposal"):
            proposal_capture = Capture(state["lane"], state["proposal"])
            proposals.preset(state["key"], proposal_capture.body, state)
            css_names.update(proposal_capture.css)
            js_names.update(proposal_capture.js)
            proposal_doc = proposal_capture.body
        else:
            proposal_doc = copy.copy(capture.body)
        changes = proposals.apply(state["key"], proposal_doc, state)
        proposal_html = proposal_doc.decode_contents()
        has_proposal = proposal_html != today_html
        css_names.update(capture.css)
        js_names.update(capture.js)
        bodies[f'{state["key"]}-today'] = pack(today_html)
        if has_proposal:
            bodies[f'{state["key"]}-proposal'] = pack(proposal_html)
        if True:
            index = CAPTURED / state["lane"] / "index.tsv"
            if index.exists():
                for line in read(index).splitlines():
                    parts = line.split("\t")
                    if len(parts) >= 3 and parts[0] == state["capture"] and parts[1] == "200":
                        bare = parts[2].split("?")[0]
                        # The two views of one Case are two states; the view rides on the key.
                        routes.append([bare + "?view=inspection" if "view=inspection" in parts[2] else bare, state["key"]])
        entries.append({
            "key": state["key"],
            "label": state["label"],
            "group": state["group"],
            "css": capture.css or ["site.css"],
            "js": capture.js or ["site.js"],
            "htmlAttrs": capture.html_attrs,
            "bodyAttrs": capture.body_attrs,
            "hasProposal": has_proposal,
            "changes": changes,
            "scroll": state.get("scroll"),
            # The presets a state opens on (the runtime and the check read them).
            "dialog": bool(state.get("dialog")),
            "viewer": state.get("viewer"),
            "rename": bool(state.get("rename")),
            "panel": state.get("panel"),
        })

    routes.extend([list(item) for item in ROUTES])
    # Captured fragments (message previews and content) answer the live scripts' requests.
    fragments: dict[str, str] = {}
    for index in sorted(CAPTURED.glob("*/index.tsv")):
        for line in read(index).splitlines():
            parts = line.split("\t")
            if len(parts) >= 3 and parts[0].startswith("fragment-") and parts[1] == "200":
                fragments[parts[2]] = read(index.parent / f"{parts[0]}.html")
    assets = [f'<template id="a-css-{name}"><style data-sheet="{name}">{css_asset(name)}</style></template>'
              for name in sorted(css_names)]
    assets += [f'<template id="a-js-{name}"><script>{js_asset(name)}</script></template>'
               for name in sorted(js_names)]
    assets += [
        f'<template id="a-sprite">{sprite_html()}</template>',
        f'<template id="a-css-frame"><style>{read(HERE / "frame-v48.css")}</style></template>',
        f'<template id="a-js-bridge"><script>{read(HERE / "bridge-v48.js")}</script></template>',
        f'<template id="a-js-proposal"><script>{read(HERE / "proposal-v48.js")}</script></template>',
    ]
    runtime = (read(HERE / "runtime-v48.js")
               .replace("__STATES__", json.dumps(entries).replace("</", "<\\/"))
               .replace("__ROUTES__", json.dumps(routes))
               .replace("__FRAGMENTS__", json.dumps(fragments).replace("</", "<\\/")))
    doc = (
        "<!DOCTYPE html>\n<html lang=\"en-GB\">\n<head>\n<meta charset=\"utf-8\" />\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n"
        "<title>Pegasus v48 Send report dialog and Original report card</title>\n"
        f"<style>{read(HERE / 'shell-v48.css')}</style>\n</head>\n<body>\n"
        "<iframe id=\"mock-frame\" title=\"Pegasus\"></iframe>\n"
        f"{read(HERE / 'strip-v48.html')}\n"
        + "\n".join(assets) + "\n"
        f'<script type="application/json" id="mock-bodies">{json.dumps(bodies)}</script>\n'
        "<script>window.mockupErrors=[];window.addEventListener('error',function(e){window.mockupErrors.push(e.message);});</script>\n"
        f"<script>{runtime}</script>\n</body>\n</html>\n"
    )
    OUT.write_text(doc, encoding="utf-8")
    (HERE / "v48-changes.json").write_text(json.dumps(
        [{"key": e["key"], "label": e["label"], "group": e["group"], "changes": e["changes"]}
         for e in entries], indent=2), encoding="utf-8")
    print(f"Wrote {OUT.name}: {len(entries)} states, "
          f"{sum(1 for e in entries if e['hasProposal'])} with proposals, {len(doc) // 1024} KB")
    for item in missing:
        print("missing capture:", item)


if __name__ == "__main__":
    build()
