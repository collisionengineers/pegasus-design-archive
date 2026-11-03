# v47: an impact, or a deliberate Skip impacts

**Stage 1, awaiting sign-off.**

- Created at the operator's request on 3 November 2026, as a follow-up to v46, PR #1869
  (https://github.com/collisionengineers/pegasus/pull/1869).
- It is built over live captures of Pegasus `origin/dev` (`7231a4b37`, 3 November 2026), which
  includes PR 1869.
- It is not application code, not design authority and not implementation evidence. The
  self-check and screenshots test the mockup against itself, not the application.
- Behaviour is owned by the FRDs (FRD-24 Damage record, FRD-11 readiness and report wording,
  FRD-16 Damage). Presentation is owned by the
  [design authority](https://github.com/collisionengineers/pegasus/blob/dev/docs/design/README.md).
- The sign-off list in [notes/v47-notes.md §6](notes/v47-notes.md#6-sign-off) decides what
  Stage 2 changes.

Open [pegasus_v47.html](pegasus_v47.html) in a browser. It is one self-contained file with 8
states of the Case record's Damage section and the aside's readiness.

- **Today** is the page as captured from the running application. A Case with no impact is
  ready to send, nothing offers a skip, and the Incident narrative's sentences sit on
  consecutive lines.
- **Proposal** is the same page with the changes applied:
  - Readiness names **Impacts** until a complete impact is entered or **Skip impacts** is
    ticked. In the blocked states this is the application's own rendering, captured with the
    proposed rule switched on.
  - **Skip impacts** stands beside Add impact while no impact row exists. Ticking it greys out
    Add impact, and while reading it is a static tick.
  - With no row, the empty state sits on the facts' own left edge.
  - The Incident narrative puts a line's space between its sentences.

The floating strip at the bottom left (`Mockup controls`) is a demo control, not product UI. It
switches states, Today / Proposal and **Diff badges**, and lists the changes on the current
state. Hide it with `?strip=0`.

Query string: `?state=<key>&mode=today|proposal&diff=1&strip=0`. The state keys are
`none-read`, `none-edit`, `skipped-read`, `skipped-edit`, `partial-read`, `partial-edit`,
`two-read` and `two-edit`.

## Layout

| Path | What it is |
| --- | --- |
| `pegasus_v47.html` | The interactive mockup: 8 states, Today and Proposal. It is built, so do not edit it by hand |
| `notes/v47-notes.md` | Change table, live rules mirrored, frame numbers, coverage audit and departures, sign-off items A–G, self-check record, known limits |
| `notes/discussion-log.md` | The operator's brief and answers, rounds 1 and 2, 3 November 2026 |
| `notes/stage-2-plan.md` | The Stage 2 implementation plan, written during Stage 1. Not started |
| `notes/capture-run-2026-11-03.log` | Results of the `ZzMockupCaptureCase.CaptureV47*` runs against `7231a4b37` |
| `pages/` | The Case page folder: how it works today, how it should work, states and panels |
| `captured-live/case/` | The server-rendered pages the mockup is built over, including the `v47-rule-*` captures |
| `captured-live/_source/` | The live `wwwroot` the captures reference, and `source.txt` naming the commit |
| `build/` | `build-v47.py` (assemble), `proposals_skip.py` (the patches), `check-v47.py` (self-check and shots), `preview_patch.py` |
| `shots/` | Screenshots at 1580×1000, 1440×900 and 760×1000, with section crops and `verification.json` |

## Rebuild

```powershell
python -X utf8 build/build-v47.py
python -X utf8 build/check-v47.py            # add --no-shots to skip screenshots
```

To recapture, run the `ZzMockupCaptureCase.CaptureV47*` facts in a capture worktree with
`MOCKUP_CAPTURE=1` and `MOCKUP_CAPTURE_DIR` set to this folder's `captured-live`. Run the
`CaptureV47Rule*` facts with `MOCKUP_V47_RULE=1` as well, with the scratch readiness rule in
`AssessmentPolicy.Evaluate`. Neither the facts nor the rule are ever committed.

## Status

- Round 1 settled the place, the exclusivity, the label "Skip impacts" and no backfill.
- Round 2 settled the empty state's alignment and the greyed Add impact.
- Items A–G are open.
