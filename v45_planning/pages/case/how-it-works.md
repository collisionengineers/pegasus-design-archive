# Case record: report content choices and Report wording, how it works

Read from the live source on 2 November 2026 (Pegasus `origin/dev` `f6de68d1a`).

## What the page does not show

- Six things decide what the report says, but they sit in four places with no connection
  between them:

  | What | Where |
  | --- | --- |
  | The five content switches | Valuation section |
  | The wording blocks and their `On report` ticks | Report section, Report wording panel |
  | The Valuation commentary text | Report section, its own field |
  | The Statement of truth | Report section, a folded read-only sub-panel |

- Two blocks have two on/off controls each, and nothing on the page says so.
  - **PAV commentary** and **Unrelated damage** are gated by a Valuation switch
    (`report.valuation_commentary`, `report.include_unrelated_damage`).
  - They also carry the panel's own `On report` tick.
  - With the switch off, the block is not offered at all, so the panel gives no sign that
    the block exists.
- Disclose guide source changes the Statement of truth, not a wording block. Its sentence
  prints only when the guide used was Glass's.
- FAO The Court changes the address block on page 1 (Report For), not the narrative. It
  prints on the assessment report only, not on the image pack or fee note (R610).
- With Include statement of truth off, the report still prints paragraphs 3–4 (the
  parts-price caveat and the fee-note paragraph) and the sign-off (R609).

## Governing documentation

| Document | What it settles for this page |
| --- | --- |
| FRD-11, "Assessment-report outcomes" | The statement of truth, the guide sentence and the include switch (R609) |
| FRD-11, "Report wording blocks" | The nine blocks and their order. Wording equal to the composed text is no change. Wording is held per Case per work and written by the one Case save. R572 |
| FRD-11, "Report For" | The FAO line (R610, R611) |
| FRD-11, readiness | Commentary on with no text, and unrelated damage on with none recorded, block the report |
| FRD-16, "Valuation" | On the report as one line |
| FRD-16, "Report" | The switches, the read-mode line (R611, R616), the statement sub-panel (folded, read-only, R609) and the Report wording panel |
| rulings R609, R610, R611, R616 | See above. R611 places both new ticks "in the On the report group on Valuation, as one home for every report content choice" |

## Source by layer

| Layer | File | What it owns |
| --- | --- | --- |
| Web | `Pages/Cases/Shared/_CaseValuation.cshtml` (lines 258–285) | The On the report row: the five checkboxes in edit mode, `ReportContentSummary` in read mode |
| Web | `Pages/Cases/Details.Report.cs` `ReportContentSummary` | The read-mode line (R616) |
| Web | `Pages/Cases/Shared/_CaseReport.cshtml` (lines 643–735, `WordingRow`) | The commentary text field, the Statement of truth sub-panel, the Report wording panel |
| Web | `wwwroot/js/case-workspace.js` (lines 4560–4650, 4985–5010) | Wording move, recompose and new paragraph; the `On report` dimming; the summary-line rewrite |
| Web | `Presentation/CaseWorkspaceLabels.cs` (`Report`, `ReportWording`) | The labels |
| Web | `Presentation/ReportWordingEdits.cs` | `Offered` / `ToRecord`. A block equal to the composed text stores null |
| Core | `Reports/ReportWording.cs` `ReportWordingComposition` | The nine keys and titles, composition, and the switch gating of `commentary` and `unrelated` |
| Core | `Reports/AssessmentReportRendering.cs` | The statement paragraphs, `StatementOfTruthGuide` and `PrintsGuideDisclosure` |
| Core | `Reports/CaseReportGeneration.cs` `CaseReportContentSwitches.IsOn` | The defaults: the first three are off until recorded `true`; FAO and the statement are on until recorded `false` |
| Core | `Reports/CaseReportFreshness.cs` | All five switches and the wording mark a confirmed report stale |
| Infrastructure | `CaseReportWordingEntity` / `CaseReportWordings` | One row per changed block per work: `Title`, `Text`, `Order`, `Included`, `Manual` |
| Web (MCP) | `Mcp/ReportPreparationMcpTools.cs` | `pegasus_report_wording_get` / `_save`. The switches are written through `pegasus_assessment_update` |

## Behaviours

### On the report (Valuation)

- **Edit mode.** The row shows five ticks in one line: Disclose guide source, Valuation
  commentary, Include unrelated damage, FAO The Court and Include statement of truth.
  - Each tick posts `true`, followed by a hidden `false`, so an unticked switch records
    No.
  - Origin: v28 P38, and R611 for the last two.
- **Read mode.** The row shows one line, for example "Guide source disclosed · valuation
  commentary · unrelated damage".
  - "No FAO The Court" and "No statement of truth" appear only when those switches are off
    (R616).
- **Defaults.**
  - Disclose guide source, Valuation commentary and Include unrelated damage are off until
    recorded on.
  - FAO The Court and Include statement of truth are on until recorded off (R611).

### Valuation commentary text

- The commentary text is a full-width field under Engineer's comments on the Report pane.
- It is frozen into the report only while the Valuation commentary switch is on.
- If no text is recorded, the projection falls back to the applied valuation's reason.

### Statement of truth sub-panel

- It is folded until this browser opens it (v36 item P).
- It shows `Model.StatementOfTruth` read-only, in print order:
  1. paragraphs 1 and 2, only when the statement is included;
  2. the guide sentence, only when Disclose guide source is on and the guide is Glass's;
  3. paragraph 3;
  4. paragraph 4.

### Report wording panel

- The panel is drawn only when the report can be projected (`Model.ReportWording.Count > 0`).
- Each block is a row with:
  - its heading input;
  - a chip: tracks fields, edited, manual, from Estimate or pass-through;
  - Recompose (standard blocks only);
  - Move up and Move down;
  - `On report`;
  - a textarea.
- An unticked block is dimmed (`is-off`), and in read mode it is dimmed as well.
- New paragraph adds a manual block.
- Everything joins the one Save form (`wordingEdits[i].*`).
- A standard block whose composed text is empty and that has no saved change is not offered.
  That is why a switched-off commentary or unrelated damage block is missing.

## Things the FRD does not settle

- Whether a content choice that changes the statement of truth or the address belongs with the
  narrative blocks at all. R611 put all five on Valuation as "one home".
- What the panel shows when the report cannot be projected, while the content choices are
  still editable.
