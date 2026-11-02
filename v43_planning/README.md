# v43: Case details — Claim source card, Principal panel, Case contact and Notes from client removed

**Temporary design review artifact**, created at the operator's request on 2 November 2026
and built over live captures of `origin/dev` (`826c2aed7`, 2 November 2026). It is not
application code, not design authority and not implementation evidence. Behaviour is
owned by the FRDs, and presentation by the
[design authority](https://github.com/collisionengineers/pegasus/blob/dev/docs/design/README.md).
Once the Stage 2 implementation lands and FRD-16 and FRD-23 carry the settled behaviour,
this folder is historical provenance only. The sign-off list in
[notes/v43-notes.md §6](notes/v43-notes.md#6-sign-off) decides what Stage 2 changes.

Open [pegasus_v43.html](pegasus_v43.html) in a browser. It is one self-contained file with
7 states of the Case record's **Case details** section. **Today** is the page captured from
the running application, and **Proposal** is the same page with the proposed changes
applied. The floating strip at the bottom left (`Mockup controls`) is a demo control for
switching states, toggling Today / Proposal and **Diff badges**, and reading the changes on
the current state. It is not product UI and is hidden with `?strip=0`. Query string:
`?state=<key>&mode=today|proposal&diff=1&strip=0`.

## Layout

| Path | What it is |
| --- | --- |
| `pegasus_v43.html` | The interactive mockup (7 states, Today and Proposal) |
| `notes/v43-notes.md` | Change table, live rules mirrored, frame numbers, settled items A–E, departures, open items F–H, self-check record, known limits |
| `notes/discussion-log.md` | The operator's 2 November 2026 brief and answers, and what was explored |
| `notes/stage-2-plan.md` | The Stage 2 implementation plan, written during Stage 1; not started |
| `notes/capture-run-2026-11-02.log` | Output of the `ZzMockupCaptureCase` lane against `origin/dev` `826c2aed7` |
| `build/states_v43.py` | The 7 states and their captures |
| `build/proposals_v43.py`, `build/proposals_case.py` | The patch API, presets and the Case details patches |
| `build/build-v43.py` | Builds `pegasus_v43.html` and `build/v43-changes.json` from `captured-live/` |
| `build/check-v43.py` | Playwright self-check and screenshots into `shots/` |
| `build/preview_patch.py` | Inspects one state's changes and Today→Proposal diff without building |
| `build/runtime-v43.js`, `bridge-v43.js`, `strip-v43.html`, `shell-v43.css`, `frame-v43.css` | Mockup runtime: frame, request stubs, control strip |
| `captured-live/` | Captured Case pages and lazy sections, and the live assets (`_source/`, with `source.txt`) |
| `shots/` | 98 screenshots (`001`–`014` at 1580×1000, 1440×900, 760×1000, a Case details crop at each width, and a 1580 whole page) and `verification.json` |
| `pages/` | `pages/case/`: `README.md`, `dialogs/`, `states/`, `panels/`, `how-it-works.md`, `how-it-should-work.md` |

## Building

Run from `v43_planning/`:

```powershell
python -X utf8 build/build-v43.py; python -X utf8 build/check-v43.py
```

The self-check and screenshots test the mockup against itself; they are not application
evidence.

## Status

**Signed off and implemented (2 November 2026).** Items **A**–**H** are settled
([notes/v43-notes.md §6](notes/v43-notes.md#6-sign-off)). Stage 2 is `task/case-details-claim-source`
in the application repository; its conformance evidence is in [conformance/](conformance/README.md).
Once that PR merges, this folder is historical reference: current behaviour is owned by the FRDs
(FRD-16 §Case details, FRD-23, FRD-04), the rulings R594–R599 and the ADRs, not by this mockup.
