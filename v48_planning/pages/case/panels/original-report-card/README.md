# Original report card

## Condition

An Inspection + Audit Case, in the Audit view (`!IsInspectionView && Works.HasAudit`), in read
and edit alike. Absent on the Inspection view, on a standalone Audit, on a Triage Case and
before the Audit exists.

## The card

`section.panel.context-card[data-v48-original-report]` after Figures in `[data-case-aside]`,
heading "Original report" (`CaseWorkspaceLabels.Frame.OriginalReport`, today the standalone
Audit's section heading; the card never reuses that section's id). `dl.figures` in the
Figures card's own shape:

| Row | Label (live) | Source |
| --- | --- | --- |
| 1, `figure--big` | Repair cost inc VAT (`Frame.RepairCostIncVat`) | `OtherReportGeneration.Snapshot.Costs.Totals.Printed.Gross` |
| 2, only on a Total loss | Salvage value (`Settlement.SalvageValue`) | `Snapshot.Report.SalvageValue` when `Snapshot.Report.Outcome == TotalLoss` |
| 3 | Engineer's Value (`Frame.EngineersValue`) | `Snapshot.EngineerValue`, then " ({guide})" where `Snapshot.AppliedValuationId` → the applied valuation's `GuideValuationId` → that card's `ValuationSource` → `CaseWorkspaceLabels.Valuation.SourceLabel`; no bracket for a typed value |

Money as the aside draws it, "£" + N2 en-GB; "—" in `.absent` until an Inspection report
generation exists.

## Variables

`opt=card:before-figures` moves the card above Figures; `opt=money:pounds` draws "£5,000
(Cazana)". Both are drawn for comparison; the proposal is after Figures and "£5,000.00".

## Fixture

The Inspection report frozen as a Total loss, repair cost £7,850.00, salvage £1,250.00
(category S), Engineer's Value £5,000.00 on a Cazana guide (`v48-audit-*`); and as Repairable
on a Glass's guide (`v48-audit-repairable-read`). The Audit work's own Figures stay the
fixture's £270.00 / £5,000.00 / 5%.

## Shots

`audit-edit`, `audit-read`, `audit-repairable`, `audit-inspection` at the three widths with a
card crop; the two variable shots. See
[../../../../notes/v48-notes.md §1](../../../../notes/v48-notes.md#1-what-changes).
