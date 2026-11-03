# v46: impacts entered by hand, damage markers for the picture only

**Historical reference.** Stage 2 is delivered on Pegasus branch `task/v46-impact-entry`
(PR #1869, https://github.com/collisionengineers/pegasus/pull/1869). Current behaviour is owned by the PRDs, FRDs and ADRs (FRD-24 Damage record, FRD-11
report wording blocks, FRD-16 Damage, FRD-10 MCP) and by rulings R642–R646 in
[docs/rulings.md](https://github.com/collisionengineers/pegasus/blob/dev/docs/rulings.md), not by
this folder.

- Created at the operator's request on 3 November 2026. It is built over live captures of
  Pegasus `origin/dev` (`fb4c5e741`, 3 November 2026), which includes PR 1862.
- It is not application code, not design authority and not implementation evidence. The
  self-check and screenshots test the mockup against itself, not the application.
- Behaviour is owned by the FRDs (FRD-24 Damage record, FRD-11 report wording). Presentation is
  owned by the [design authority](https://github.com/collisionengineers/pegasus/blob/dev/docs/design/README.md).
- The sign-off list in [notes/v46-notes.md §6](notes/v46-notes.md#6-sign-off) decides what
  Stage 2 changes.
- Once Stage 2 lands and FRD-24 and FRD-11 carry the settled behaviour, this folder is
  historical provenance only.

Open [pegasus_v46.html](pegasus_v46.html) in a browser. It is one self-contained file with 9
states of the Case record's Damage section and the Report wording's Nature of Incident block.

- **Today** is the page as captured from the running application. Impact location and severity
  are derived from the markers (PR 1862), and each marker has its own list row.
- **Proposal** is the same page with the changes applied:
  - Staff type the impacts as rows: Impact · Severity · Location · Note · ×, and add more rows
    with Add impact.
  - The Incident narrative and Nature of Incident are a sentence for each impact and follow the rows. With no impact, Nature of
    Incident is skipped and the report is not blocked.
  - The markers are bursts on the plan and nothing else. Clear markers removes them all.
  - The derived cells, the per-marker list, the Underside/Interior/Mechanical chips and the area
    readout are gone.

The floating strip at the bottom left (`Mockup controls`) is a demo control, not product UI. It
switches states, Today / Proposal and **Diff badges**, and lists the changes on the current
state. Hide it with `?strip=0`.

Query string: `?state=<key>&mode=today|proposal&diff=1&strip=0`. The state keys are
`damage-two-read`, `damage-two-edit`, `damage-apart-read`, `damage-apart-edit`,
`damage-apart-edit-under`, `damage-none-read`, `damage-none-edit`, `wording-apart` and
`wording-none`.

## Layout

| Path | What it is |
| --- | --- |
| `pegasus_v46.html` | The interactive mockup: 9 states, Today and Proposal. It is built, so do not edit it by hand |
| `notes/v46-notes.md` | Change table, live rules mirrored, frame numbers, coverage audit and departures, sign-off items A–L, self-check record, known limits |
| `notes/discussion-log.md` | The operator's brief and answers of 3 November 2026 |
| `notes/stage-2-plan.md` | The Stage 2 implementation plan, written during Stage 1. Not started |
| `notes/capture-run-2026-11-03.log` | Output of the `ZzMockupCaptureCase` v46 lane against `fb4c5e741` |
| `pages/` | The Case page folder: how it works today, how it should work, states and panels |
| `captured-live/case/` | The server-rendered pages the mockup is built over |
| `captured-live/_source/` | The live `wwwroot` the captures reference, and `source.txt` naming the commit |
| `build/` | `build-v46.py` (assemble), `proposals_damage.py` (the patches), `check-v46.py` (self-check and shots), `preview_patch.py` |
| `shots/` | Screenshots at 1580×1000, 1440×900 and 760×1000 with section crops and `verification.json` |
| `conformance/` | Stage 2 evidence: the implemented page captured from the same fixtures, built with its own CSS and JS, its check (`RESULT {"fail": [], "okCount": 65}`) and its shots. See [conformance/README.md](conformance/README.md) |

## Rebuild

```powershell
python -X utf8 build/build-v46.py
python -X utf8 build/check-v46.py            # add --no-shots to skip screenshots
```

To recapture, run the `ZzMockupCaptureCase.CaptureV46*` facts in a capture worktree with
`MOCKUP_CAPTURE=1` and `MOCKUP_CAPTURE_DIR` set to this folder's `captured-live`.

## Status

Every item is settled. G was settled in round 2, A and J in rounds 3 and 4, and B–F, G2, H,
I, K and L on 3 November 2026: "Based on the mockup, assume the outstanding points are
approved" (R646). Stage 2 is delivered (PR #1869, https://github.com/collisionengineers/pegasus/pull/1869); the conformance evidence is in
[conformance/](conformance/README.md).
