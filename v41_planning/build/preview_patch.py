"""Try the proposal patches on captured states without writing the mockup.

    python preview_patch.py <state-key> [<state-key> ...]     changes and the changed markup
    python preview_patch.py --all                              changes for every state
    python preview_patch.py --html <state-key>                 write preview-<key>.html (Proposal body) for inspection
"""
from __future__ import annotations

import copy
import difflib
import sys

import importlib.util
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("build_v41", HERE / "build-v41.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)  # type: ignore[union-attr]

states = {s["key"]: s for s in build.STATES}
args = sys.argv[1:]
write_html = "--html" in args
args = [a for a in args if a != "--html"]
keys = list(states) if args == ["--all"] else args
for key in keys:
    state = states[key]
    capture = build.Capture(state["lane"], state["capture"])
    today = capture.html()
    body = copy.copy(capture.body)
    changes = build.proposals.apply(key, body, state)
    proposal = body.decode_contents()
    print(f"== {key}: {len(changes)} change(s)")
    for change in changes:
        print(f"   {change['id']}: {change['summary']}")
    if args != ["--all"]:
        diff = difflib.unified_diff(today.splitlines(), proposal.splitlines(), lineterm="", n=1)
        lines = list(diff)
        print("\n".join(lines[:200]) + ("\n   ... diff truncated" if len(lines) > 200 else ""))
    if write_html:
        (HERE / f"preview-{key}.html").write_text(proposal, encoding="utf-8")
