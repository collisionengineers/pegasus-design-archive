# Case record: Damage impacts and the report's readiness, how it works

Read from the live source on 3 November 2026 (Pegasus `origin/dev` `7231a4b37`, after PR 1869).

## What the page does not show

- A Case with no impact row is ready for its report as far as Damage goes. No readiness item,
  aside step or Damage cell says that the impacts were never considered.
- With no complete impact (a row naming both a severity and a location), the Incident narrative
  reads `—` and Report wording does not offer the Nature of Incident block. The report prints
  no Nature of Incident, and Impact Magnitude reads `—`.
- A partial row (a severity with no location, or the reverse) is kept as entered but prints
  nothing. Nothing on the page says that it will not print.
- The PR 1869 migration (`ImpactsEnteredByHand`) left every existing Case with no impacts.
  Each of them can be generated with no Nature of Incident, and nothing prompts staff.
- With two or more impacts, the Incident narrative shows the sentences on consecutive lines
  with no space between them. The cell is `pre-wrap` text joined with `\n`.

## Governing documentation

| Document | What it settles here |
| --- | --- |
| FRD-24 Damage record | Staff enter impacts by hand. "Impacts are optional: none blocks the report" (R642–R646) |
| FRD-11 Report wording blocks | One Nature of Incident sentence per impact, one to a line. With none, the block is not offered or printed (R644–R646) |
| FRD-11 readiness table | Damage: "Unrelated damage when its switch is on; impacts are optional" |
| FRD-16 Damage | The rows, Add impact, the × and the read-only Incident narrative |
| R645 A2 | "One to a line. Where several impacts exist, it should be one to a line." |

## Source by layer

| Layer | File | Owns |
| --- | --- | --- |
| Core | `Assessment/AssessmentContracts.cs` | `AssessmentImpact` and `IsComplete`, and `assessment.impacts` with its format |
| Core | `Assessment/AssessmentPolicy.cs` `Evaluate` | The readiness items: `RequireField` and `RequireCaseFact`. There is none for impacts |
| Core | `Reports/AssessmentReportProjection.cs` | `Prepare`, which adds sign-off and spec items, and `ReportImpacts`, the complete rows |
| Core | `Reports/ReportWording.cs` | `NatureOfIncidentText` (sentences joined `\n`), and `Offered`, which skips a block composing nothing |
| Web | `Pages/Cases/Shared/_CaseDamage.cshtml` | The rows, Add impact, the empty line "No damage recorded.", Unrelated damage and the Incident narrative cell (`.fv.derived.multi`) |
| Web | `wwwroot/js/case-workspace.js` `bindImpacts` | Adding and clearing rows, writing the JSON back, and recomposing the narrative with `join('\n')` |
| Web | `Pages/Cases/Shared/_CaseAside.cshtml` | The Next action step (the first blocker) and the outstanding blocker list |
| Web | `Presentation/CaseWorkspaceLabels.cs` `Report.BlockerSection` | Routes a blocker to the section that owns its `Field` |

## Precedents the proposal reuses

- **Tick while editing.** `label.choice` holding a checkbox, with a hidden `false` posted after
  it (`_CaseEstimate.cshtml`'s Explain on report, and Report wording's settings).
- **Static tick while reading.** `span.choice.is-static` with a `.tick` that holds
  `icon-check` when on (`_CaseReport.cshtml` `StaticTick`, v45).
- **Blocker routed by field.** An `AssessmentReadinessItem` whose `Field` is a Damage path
  jumps to the Damage section and outlines its `data-field` cell.
