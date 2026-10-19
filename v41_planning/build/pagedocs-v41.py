"""Write v41-redesign/pages/: one README per area, generated from v41-changes.json.

Today is the captured live page, so the docs do not describe it in prose: each
state lists its capture and the proposed changes (ID and summary), which are the
open items of v41-notes.md section 5 and the settled items of section 4. Run after
build-v41.py.
"""
from __future__ import annotations

import json
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
PAGES = HERE.parent / "pages"
SLUGS = {
    "Work Centre and Search": "work-centre-and-search",
    "Inbox": "inbox",
    "Upload and Cases": "upload-and-cases",
    "Case": "case",
    "Administration": "administration",
    "Shell and sign-in": "shell-and-sign-in",
}


def main() -> None:
    states = json.loads((HERE / "v41-changes.json").read_text(encoding="utf-8"))
    if PAGES.exists():
        shutil.rmtree(PAGES)
    PAGES.mkdir()
    index = ["# v41 pages", "",
             "One folder per area. Each page lists its states, opened in "
             "[pegasus_v41.html](../pegasus_v41.html) with `?state=<key>&mode=today|proposal`, "
             "and the changes its Proposal makes. The IDs are the items in "
             "[v41-notes.md](../notes/v41-notes.md): §5 lists the open ones and "
             "[§4](../notes/v41-notes.md#4-already-settled) what is settled.", ""]
    for group, slug in SLUGS.items():
        rows = [s for s in states if s["group"] == group]
        if not rows:
            continue
        ids: dict[str, str] = {}
        for state in rows:
            for change in state["changes"]:
                ids.setdefault(change["id"], change["summary"])
        lines = [f"# {group}", "",
                 "Today is the page captured from the application; it is not redrawn. "
                 "The Proposal is the same page with the changes below.", "",
                 "| State | Page | Changes |", "| --- | --- | --- |"]
        for state in rows:
            changed = ", ".join(sorted({c["id"] for c in state["changes"]}, key=sort_key)) or "none"
            lines.append(f"| `{state['key']}` | {state['label']} | {changed} |")
        lines += ["", "## Changes", ""]
        for change_id in sorted(ids, key=sort_key):
            lines.append(f"- **{change_id}**: {ids[change_id]}")
        folder = PAGES / slug
        folder.mkdir()
        (folder / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        index.append(f"- [{group}]({slug}/README.md): {len(rows)} states, {len(ids)} changes")
    (PAGES / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    print(f"Wrote {PAGES}")


def sort_key(change_id: str) -> tuple[str, int]:
    head = change_id.rstrip("0123456789")
    tail = change_id[len(head):]
    return head, int(tail) if tail else 0


if __name__ == "__main__":
    main()
