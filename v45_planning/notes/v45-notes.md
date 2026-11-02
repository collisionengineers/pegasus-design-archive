# v45 notes: Report wording absorbs On the report

The round opened on 2 November 2026. The live source was read from Pegasus `origin/dev`
`f6de68d1a` (`captured-live/_source/source.txt`). The brief, the questions and the operator's
answers are in [discussion-log.md](discussion-log.md).

The brief calls the row's home "the Vehicle section". On the live page, On the report is in the
Valuation section, directly under Vehicle, and it is the only On the report on the Case page.

## 1. What changes

| # | Today (problem) | Proposal | Shots |
| --- | --- | --- | --- |
| R1 | What the report includes is decided in two sections. The five ticks are on Valuation; the block ticks are on Report | The On the report row leaves Valuation | 017–020 |
| R2 | No single place answers "what will the report say" | One settings checklist opens Report wording. It lists every offered block in print order, then Disclose guide source, FAO The Court and Include statement of truth, with today's defaults | 002, 004, 006, 008, 010, 012 |
| R3 | Each block has its own `On report` tick, and an unticked block is drawn dimmed | No per-block tick. An unticked item has no block, and ticking it shows the block | 004, 008 |
| R4 | PAV commentary and Unrelated damage are not offered while their Valuation switch is off. The commentary text is a separate field away from its block | Both are always offered and are shown while ticked. The commentary is written in its block | 004, 008 |
| R5 | The Statement of truth is a folded sub-panel apart from the wording | It is a read-only block, pinned last in Report wording | 002, 004, 010, 012 |
| R6 | Disclose guide source changes the statement, but nothing on the page shows that | Its sentence is a read-only box in its print place within the statement. FAO The Court is a tick with no box | 006, 008 |

## 2. Live rules the mockup mirrors

- **Defaults** (`CaseReportContentSwitches.IsOn`):
  - Disclose guide source, Valuation commentary and Unrelated damage are off until recorded
    `true`.
  - FAO The Court and Include statement of truth are on until recorded `false` (R611).
- **Statement paragraphs** (`AssessmentReportContract.StatementOfTruth`):
  - Paragraphs 1–2 print only with the statement included.
  - The guide sentence (`StatementOfTruthGuide`) prints only with Disclose guide source on
    and a Glass's guide used (`PrintsGuideDisclosure`).
  - Paragraphs 3–4 always print (R609).
- **FAO The Court** prints above the addressee on the assessment report only (R610). It is no
  wording block.
- **Block chips, Recompose, Move up/down and New paragraph** are unchanged (`WordingRow`,
  `case-workspace.js`).
- **Form names** stay live.
  - Block ticks post `wordingEdits[i].Included` with a hidden `false`.
  - The switches post `assessmentFields[report.*]` with a hidden `false`.
- **Offering** (`ReportWordingEdits.Offered`): a standard block with empty composed text and
  no saved change is not offered (Supplementary damage and Salvage on this Case). That stays
  the same.

## 3. Frame numbers

- **Settings box.** 8px padding, 1px `--line` border, 4px radius, `--surface-2` background.
  Ticks are 12px, with 6px vertical and 20px horizontal gaps, as the live On the report row.
- **Settings layout.** Flex-wrap in one line (proposed). The item G variant is a 3-column grid,
  2 columns under 900px.
- **Read-only blocks.** They use the live `.wb` box on `--surface-2`. The guide box is nested
  on `--surface`, and its paragraphs are 8px apart.
- **Tokens.** No new token, colour, icon or label.

## 4. Decisions and authority

- **R1–R6** come from the operator's brief and three answers of 2 November 2026
  ([discussion log](discussion-log.md)).
- **Labels** are live strings:
  - `CaseWorkspaceLabels.ReportWording` (Report wording, in print order, New paragraph);
  - `CaseWorkspaceLabels.Report` (Disclose guide source, FAO The Court, Include statement of
    truth, Unrelated damage);
  - the `ReportWordingComposition` titles;
  - `EngineerLabels.StatementOfTruth`.
- **Statement wording** is `AssessmentReportRendering`'s constants, verbatim.

## 5. Coverage audit and departures from live

| Live element | Proposal |
| --- | --- |
| Valuation: On the report label and summary line | Gone. Read mode shows the static ticks instead (item C) |
| Valuation: five switch inputs | Moved into the settings under the same names |
| Report: Valuation commentary field | Gone. Its textarea is the PAV commentary block's text box, under the same name (item E) |
| Report: Statement of truth sub-panel and its fold | Gone. The read-only block has no fold, so the fold cookie `case.report.statement` is no longer used |
| Report wording: heading, "in print order", chips, Recompose, Move up/down, New paragraph, template | Kept. The commentary block has no Recompose because its text box is the field itself |
| Report wording: per-block `On report` tick and read-mode `On report` mark | Gone. They are in the settings (R3) |
| Report wording: dimmed `is-off` blocks | Gone. An unticked block is hidden (R3) |
| Report date, Engineer's comments, send form, Fee tab | Unchanged |

## 6. Sign-off

Each item reads "Confirm, or …".

- **A. One owner per tick.**
  - The commentary and unrelated damage ticks write the existing switches
    (`report.valuation_commentary`, `report.include_unrelated_damage`). The block's own
    `Included` flag is no longer offered for those two keys.
  - Every other block tick writes `Included`. Guide, FAO and statement keep their switches.
  - No migration.
  - Confirm, or make the block flag the owner and retire the two switches, which needs a
    data migration.
- **B. Report cannot be projected** (state `case-edit-unprojected`, shots 013–014).
  - The proposal is that the settings show the five former switches, with no blocks.
  - Today the whole panel is absent, while the switches stay editable on Valuation.
  - Confirm, or hide the settings too.
- **C. Read mode.** The settings are shown as static ticks, which replace R616's summary line
  ("Guide source disclosed · … · No FAO The Court"). Confirm, or keep the line.
- **D. Read-only blocks.**
  - The Statement of truth block is pinned after New paragraph, with no move controls.
  - The guide sentence sits inside it, between paragraphs 2 and 3, where it prints.
  - Confirm, or show the guide sentence as its own block before the statement.
- **E. Commentary text.**
  - The PAV commentary block's text box writes `report.valuation_commentary_text`, so the
    block has one owner, and the separate field goes.
  - Confirm, or keep the field and let the block hand-edit as other blocks do.
- **F. Blocker wording.**
  - The readiness and render blockers for commentary and unrelated damage say "turn off …
    under On the report on the Valuation section" (`CaseReportGeneration.cs:794–813`).
  - The operator supplies the replacement words. The mockup does not draw them.
- **G. Settings layout.**
  - The proposal is one wrapping line, as the live On the report row is (shot 008).
  - Confirm, or use columns (`case-edit-columns`, shot 016).
- **H. Commentary tick label.**
  - The tick reads the block's heading, "PAV commentary", so each item has one name.
  - Confirm, or use the live switch label "Valuation commentary".
- **I. Statement off** (shots 010, 012).
  - With Include statement of truth off, the block keeps the paragraphs that still print
    (3–4, R609) and hides paragraphs 1–2.
  - Confirm, or hide the whole block.

## 7. Self-check

`build/check-v45.py`, run on 2 November 2026 at 18:15 UTC:

- **Result:** `RESULT {"fail":[],"okCount":238}`, with no page or console error in any of the 10
  states, in Today or Proposal.
- **Shots:** 140, at 1580×1000, 1440×900 and 760×1000, each with a panel crop, plus a 1580
  whole page. They are listed in `shots/verification.json`.
- **Settled changes.** Each of R1–R6 is asserted in every state.
- **Today.** The live row, the per-block ticks, the statement sub-panel and the commentary
  field are asserted present.
- **Edit flows.** These are asserted:
  - the tick-driven show and hide, including Nature of Incident off and on;
  - FAO changing no block;
  - statement off hiding only paragraphs 1–2;
  - New paragraph adding its tick before the three switches;
  - the tick following a heading edit;
  - Move up;
  - the live form names.
- **Variants.** Items B and G are asserted on their own states.

## 8. Known limits

- **Commentary block and guide sentence.** The capture's fake projection
  (`AssessmentReportDraftWebTests.FakeProjectionSource`) carries no `ValuationCommentary` and no
  Glass's guide.
  - In the `case-switches-*` and `case-edit-columns` states, a preset therefore adds both to
    Today and Proposal.
  - The preset adds live's PAV commentary block (shaped like its Engineer's Comments row) and
    the guide sentence in the statement.
- **Unprojectable state.** `case-edit-unprojected` is `case-edit` with the panel removed, not a
  separate capture.
- **The mockup's script.**
  - The show/hide and the new-paragraph tick are the mockup's own script (`SCRIPT` in
    `build/proposals_report.py`), not live code.
  - Save posts nowhere; there is no server behind the mockup.
- **Not drawn.** The blocker words (item F) and the Audit view's wording.
- **Not evidence.** The self-check and shots test the mockup against itself. They are not
  application evidence.
