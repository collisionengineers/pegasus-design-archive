# v41 redesign: the Pegasus redesign mockup

**Temporary design review artifact**, created at the operator's request on 14 October
2026 and rebuilt over live captures on 15 October 2026. It is not application code, not
design authority and not implementation evidence. Behaviour is owned by the FRDs, and
presentation by the [design authority](../../../docs/design/README.md). The sign-off list
in [notes/v41-notes.md §5](notes/v41-notes.md#5-sign-off) decides what Stage 2 changes.

Open [pegasus_v41.html](pegasus_v41.html) in a browser. It is one self-contained file
with 104 states. **Today** is each page captured from the application (`dev` `365d83064`,
19 October 2026), and **Proposal** is the same page with the proposed changes.
The controls at the bottom left pick the page, Today or Proposal and the Diff badges, and
list what the proposal changes on that page. Query string:
`?state=<key>&mode=today|proposal&diff=1&strip=0`.

The Inbox Proposal is one message dialog (tags and the six designs were dropped on 15
October): the message on the left, and Decision on the right with the eleven
Classification chips and the Case picker. The list carries a checkbox on each row and one
bulk form (I18).

## Layout

| Path | What it is |
| --- | --- |
| `pegasus_v41.html` | The mockup |
| `notes/v41-notes.md` | Source, method, what the 15 October review changed, what is settled, the sign-off list, the self-check record |
| `notes/plan-2026-10-15.md` | The 15 October rulings on the sign-off questions, the #1213 and PERF-WEB-08 incorporations (PERF-WEB-09 is not withdrawn: R42 builds it in its own PR and it draws no page change), the Administration pass (A14–A30) and the work they imply |
| `notes/discussion-log.md` | How the round came to be |
| `build/states_v41.py` | The states and their captures |
| `build/proposals_v41.py`, `build/proposals_{shell,work,inbox,intake,case,admin,records}.py` | The proposal patches: the patch API and one module per area |
| `build/inbox-designs-v41.js`, `build/inbox-designs-v41.css` | The Inbox Proposal: list, row ticks and bulk form, the one message dialog, Classification chips, Case picker |
| `build/build-v41.py` | Builds `pegasus_v41.html` and `build/v41-changes.json` from `captured-live/` |
| `build/pagedocs-v41.py` | Writes `pages/` from `v41-changes.json` |
| `build/check-v41.py` | The self-check and the screenshots into `shots/` |
| `build/preview_patch.py` | One state's changes and Today→Proposal diff, without building |
| `build/runtime-v41.js`, `bridge-v41.js`, `strip-v41.html`, `shell-v41.css`, `frame-v41.css` | The mockup runtime: frame, request stubs, controls |
| `captured-live/` | The captured pages, fragments and the live assets (`_source/`, with `source.txt`) |
| `shots/` | The screenshots and `verification.json` from the last check |
| `pages/` | Generated: one page per area, listing its states and the changes each Proposal makes |

## Building

Run from this folder. To refresh the captures, run the excluded `ZzMockupCapture*` tests
(see [notes/v41-notes.md §2](notes/v41-notes.md#2-how-it-is-made)) with `MOCKUP_CAPTURE` set; they write
under the capture worktree's `artifacts/` and the lanes are copied into `captured-live/`. Then:

```powershell
python build/build-v41.py && python build/pagedocs-v41.py && python build/check-v41.py
```

## Status

Stage 1. [notes/plan-2026-10-15.md](notes/plan-2026-10-15.md) §2 was applied on 19 October
2026 (104 states). Next: operator sign-off on the items in
[notes/v41-notes.md §5](notes/v41-notes.md#5-sign-off), then one Stage 2 delivery. Nothing
under `src/` or `tests/` is changed.
