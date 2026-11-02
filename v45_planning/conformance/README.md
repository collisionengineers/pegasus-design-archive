# v45 conformance

This folder holds the Stage 2 evidence for the v45 round. The implemented Case page is captured
from `task/report-wording-settings`, which was built on Pegasus `origin/dev` `f6de68d1a`, by the
excluded `ZzMockupCaptureCase` lane (`capture-run.log`). Each panel crop is shown beside the
mockup's Proposal crop of the same state and width.

| Path | What it is |
| --- | --- |
| `pegasus_v45_conformance.html` | The implemented captures, drawn by the round's runtime with no patch |
| `build/` | The round's build, over these captures; `conformance-v45.py` writes the side-by-sides |
| `captured-live/` | The implemented pages and their live assets (`_source/source.txt`) |
| `shots/NNN-<state>-<width>-side-by-side.png` | The mockup on the left, the implementation on the right, numbered as `../shots/` |
| `shots/conformance.json` | The pairs and the check result |

Run from this folder:

```powershell
python -X utf8 build/build-v45.py; python -X utf8 build/conformance-v45.py
```

## Result, 2 November 2026

- **Result:** `RESULT {"fail":[],"okCount":35}`.
- **Coverage:** 8 states × 3 widths. No page or console error.
- **Behaviours checked on the implemented page:**
  - the settings order;
  - no On the report row, statement sub-panel, separate commentary field or per-block tick;
  - ticking draws a block, and unticking the statement hides only paragraphs 1–2;
  - New paragraph adds its tick;
  - static ticks while reading;
  - the court-off state.

## Expected differences

- **The commentary tick reads "Valuation commentary"**, where the mockup drew "PAV commentary". This
  is item H as settled (R625).
- **No guide-sentence box** in the `case-switches-*` states. The capture's fake projection has no
  Glass's guide, so `ReportStatementParts.Guide` is null and the box is not drawn, as on a live
  Case without a Glass's guide. The mockup added it with a preset.
- **The PAV commentary block's text in read mode** is empty in the `case-switches-read` capture. The
  same fake projection carries no `ValuationCommentary`. In edit mode the box shows the recorded
  field.
- **No `case-edit-unprojected` side-by-side.** Item B is proven by
  `CaseReportWordingWebTests.ACaseWhoseReportCannotBeProjectedHasTheFiveSwitchesAndNoBlocks`, and
  it keeps the statement block, which live shows in every state.
