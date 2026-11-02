# v45: Report wording absorbs On the report

**Temporary design review artifact.**

- Created at the operator's request on 2 November 2026, and built over live captures of Pegasus
  `origin/dev` (`f6de68d1a`, 2 November 2026).
- It is not application code, not design authority and not implementation evidence.
- Behaviour is owned by the FRDs, and presentation by the
  [design authority](https://github.com/collisionengineers/pegasus/blob/dev/docs/design/README.md).
- The sign-off list in [notes/v45-notes.md §6](notes/v45-notes.md#6-sign-off) decides what
  Stage 2 changes.
- Once Stage 2 lands and FRD-11 and FRD-16 carry the settled behaviour, this folder is
  historical provenance only.

Open [pegasus_v45.html](pegasus_v45.html) in a browser. It is one self-contained file with 10
states of the Case record's Report wording panel and Valuation section.

- **Today** is the page as captured from the running application.
- **Proposal** is the same page with the changes applied:
  - On the report leaves Valuation.
  - A settings checklist opens Report wording.
  - Only ticked items have a block.
  - The Statement of truth and the guide sentence are read-only blocks.
  - FAO The Court is a tick only.

The floating strip at the bottom left (`Mockup controls`) is a demo control, not product UI. It
switches states, Today / Proposal and **Diff badges**, and lists the changes on the current
state. Hide it with `?strip=0`.

Query string: `?state=<key>&mode=today|proposal&diff=1&strip=0`.

## Layout

| Path | What it is |
| --- | --- |
| `pegasus_v45.html` | The interactive mockup: 10 states, Today and Proposal. It is built, so do not edit it by hand |
| `notes/v45-notes.md` | Change table, live rules mirrored, frame numbers, coverage audit and departures, sign-off items A–I, self-check record, known limits |
| `notes/discussion-log.md` | The operator's brief and answers of 2 November 2026 |
| `notes/stage-2-plan.md` | The Stage 2 implementation plan, written during Stage 1. Not started |
| `notes/capture-run-2026-11-02.log` | Output of the `ZzMockupCaptureCase` lane against `f6de68d1a` |
| `build/states_v45.py` | The states and their captures |
| `build/proposals_v45.py`, `build/proposals_report.py` | The patch API, the presets and the Report wording patches |
| `build/build-v45.py` | Builds `pegasus_v45.html` and `build/v45-changes.json` from `captured-live/` |
| `build/check-v45.py`, `build/report_checks.py` | Playwright self-check and screenshots into `shots/` |
| `build/preview_patch.py` | Inspects one state's changes without building |
| `build/runtime-v45.js`, `bridge-v45.js`, `strip-v45.html`, `shell-v45.css`, `frame-v45.css` | Mockup runtime: frame, request stubs and control strip |
| `captured-live/` | Captured Case pages and lazy sections, plus the live assets (`_source/`, with `source.txt`) |
| `shots/` | Screenshots and `verification.json` |
| `pages/` | `pages/case/`: `README.md`, `dialogs/`, `states/`, `panels/`, `how-it-works.md`, `how-it-should-work.md` |

## Building

Run from `v45_planning/`:

```powershell
python -X utf8 build/build-v45.py; python -X utf8 build/check-v45.py
```

## Status

**Signed off and implemented (2 November 2026).** Items A–I are settled
([notes/v45-notes.md §6](notes/v45-notes.md#6-sign-off); rulings R624 and R625).

- **Stage 2** is `task/report-wording-settings` in the application repository. Its conformance
  evidence is in [conformance/](conformance/README.md).
- **Once that PR merges,** this folder is historical reference only. Current behaviour is then
  owned by the FRDs (FRD-11 Report wording blocks, FRD-16 Report), by rulings R609–R611 and
  R624–R625, and by the design authority, not by this mockup.
