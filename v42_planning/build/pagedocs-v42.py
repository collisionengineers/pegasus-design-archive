"""Write v42_planning/pages/<area>/states/README.md and pages/README.md from v42-changes.json.

Today is the captured live page, so the state tables list each state's key, label and
the sign-off items its Proposal changes (v42-notes.md §4 settled, §6 sign-off). Hand-
written page docs (README.md, dialogs/README.md, panels/README.md, how-it-works.md
and how-it-should-work.md) sit beside states/README.md and are not overwritten. Run
after build-v42.py.
"""
from __future__ import annotations

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
PAGES = HERE.parent / "pages"
SLUGS = {
    "Inbox": "inbox",
    "Case": "case",
    "Work Centre": "work-centre",
    "Upload": "upload",
}


def main() -> None:
    states = json.loads((HERE / "v42-changes.json").read_text(encoding="utf-8"))
    PAGES.mkdir(exist_ok=True)
    index = [
        "# v42 pages",
        "",
        "One folder per area the mail simplification changes. Each area carries its "
        "[How it works](inbox/how-it-works.md) (read from the live source on 26 October 2026), "
        "[How it should work](inbox/how-it-should-work.md) (rules D1…), and its generated "
        "`states/README.md` table for [pegasus_v42.html](../pegasus_v42.html) "
        "(`?state=<key>&mode=today|proposal`). Sign-off letters refer to "
        "[notes/v42-notes.md §6](../notes/v42-notes.md#6-sign-off).",
        "",
    ]
    for group, slug in SLUGS.items():
        rows = [s for s in states if s["group"] == group]
        if not rows:
            continue
        ids: dict[str, str] = {}
        for state in rows:
            for change in state["changes"]:
                ids.setdefault(change["id"], change["summary"])
        lines = [
            f"# {group} — states",
            "",
            "Today is the page captured from the application; it is not redrawn. "
            "The Proposal is the same page with the changes below.",
            "",
            "| State | Page | Changes |",
            "| --- | --- | --- |",
        ]
        for state in rows:
            changed = ", ".join(sorted({c["id"] for c in state["changes"]}, key=sort_key)) or "none"
            lines.append(f"| `{state['key']}` | {state['label']} | {changed} |")
        lines += ["", "## Changes", ""]
        for change_id in sorted(ids, key=sort_key):
            lines.append(f"- **{change_id}**: {ids[change_id]}")
        states_dir = PAGES / slug / "states"
        states_dir.mkdir(parents=True, exist_ok=True)
        (states_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        index.append(
            f"- [**{group}**]({slug}/README.md) — "
            f"[How it works]({slug}/how-it-works.md) · "
            f"[How it should work]({slug}/how-it-should-work.md) · "
            f"[Dialogs]({slug}/dialogs/README.md) · "
            f"[Panels]({slug}/panels/README.md) · "
            f"[States ({len(rows)})]({slug}/states/README.md)"
        )
    (PAGES / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    print(f"Wrote {PAGES}")


def sort_key(change_id: str) -> tuple[int, str]:
    return len(change_id), change_id


if __name__ == "__main__":
    main()
