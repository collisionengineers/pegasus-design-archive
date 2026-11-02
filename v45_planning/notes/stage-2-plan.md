# v45 Stage 2 plan (written during Stage 1, not started)

Stage 2 starts only after items A–I in [v45-notes §6](v45-notes.md#6-sign-off) are settled and
the operator approves. It follows `razor-html-mockup-conversion` and is built on branch
`task/report-wording-settings`, made from `origin/dev`.

## Web

- **`Pages/Cases/Shared/_CaseValuation.cshtml`**: remove the `valuation-report` row.
- **`Pages/Cases/Shared/_CaseReport.cshtml`**:
  - Add the settings checklist at the top of the wording sub-panel. In edit mode it uses the
    live `label.choice` pairs; in read mode, static ticks.
  - The block ticks post `wordingEdits[i].Included`. The switches post
    `assessmentFields[report.*]`.
  - `WordingRow` loses its `On report` tick. An unticked block renders with `hidden`.
  - Add the read-only Statement of truth block, with the guide sentence in its print place.
  - Remove the statement sub-panel and the separate commentary field.
- **`Pages/Cases/Details.Report.cs`**: remove `ReportContentSummary`.
- **`Pages/Cases/Details.cshtml.cs`**:
  - The commentary and unrelated blocks are always offered (`ReportWordingEdits.Offered`).
  - The statement block reads the parts of `AssessmentReportContract.StatementOfTruth`.
  - Apply item B: what the panel draws while the report cannot be projected.
- **`wwwroot/js/case-workspace.js`**:
  - Replace the summary-line script (lines 4985–5010) with the checklist show/hide.
  - New paragraph adds its tick.
  - A heading edit relabels its tick.
- **`Presentation/CaseWorkspaceLabels.cs`**:
  - `SectionOf` maps the five switch paths to "report".
  - Remove `Frame.OnTheReport` if it is no longer used.
- **`wwwroot/css/case-workspace.css`**:
  - Remove the `#section-valuation .valuation-report` rules.
  - Add `.wording-settings` and `.wb-fixed`. The proposal's `CSS` constant in
    `build/proposals_report.py` is the starting point.

## Core

- **`Reports/ReportWording.cs`**: the offering rule for `commentary` and `unrelated` (item A).
- **`Reports/CaseReportGeneration.cs`** (lines 794–813) and **`AssessmentReportRendering`**: the
  blocker words from item F.

## MCP

- No tool change is needed. The switches stay `pegasus_assessment_update` paths, and the
  wording keys are unchanged.
- Check the descriptions in `ReportPreparationMcpTools.cs:36` and FRD-10.

## Docs

- FRD-16 "Valuation" and "Report" sections, dated and citing the new ruling.
- FRD-11 "Report wording blocks", "Report For" and readiness.
- The new ruling row in `docs/rulings.md`, superseding R611's placement and R616.

## Tests

CI runs these:

- `CaseRecordFieldsWebTests` (FAO and statement default on, lines ~310–381);
- `CaseReportWordingWebTests`;
- `CaseEditModeWebTests`;
- `ReportWordingTests`;
- the Valuation section render tests.

## Conformance

Copy the excluded `ZzMockupCapture*` files into the task worktree. Capture into
`conformance/captured-live`, and reuse this round's build for side-by-side shots, as v43 did.
