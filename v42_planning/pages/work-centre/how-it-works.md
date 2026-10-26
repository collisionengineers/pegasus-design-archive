# Work Centre — how it works

Read from the live source on 26 October 2026 (`origin/dev` `373dcc81a`).

## What the page does not show

- `GetOperationsSnapshot.FetchAttentionInputsAsync` (`src/Pegasus.Core/Operations/OperationsSnapshot.cs:360`) builds `Needs attention` rows for `CaseChase`, `HeldDecision`, `ReviewCase`, `UnassignedEngineer`, `WithEngineer`, `VehicleImagesPaired`, `Unidentified`, `Triage`, `OverdueTask` and `AiDraft`, plus a `QueryResponse` row under `AI jobs` when an AI query draft job exists, but has no `NeedsAttentionKind` for an open `CaseQueries` record itself.
- Unless staff check `Cases › Queries` (`/Cases?stage=query`) or receive a `QueryReceived` notification, an open query has no row in `Needs attention`.

## Governing documentation

| Document | What it settles for this page |
| --- | --- |
| `docs/frd/frd-15-work-centre-and-operational-queues.md` | Work Centre `Needs attention` kinds, `Office` vs `Mine` scoping (`NeedsAttentionPolicy.IsMine`), kind chips, row actions and `Take` (`data-wc-take`). |
| `docs/frd/frd-16-case-record-workspace.md` | `/Cases?stage=query` (`Cases › Queries`) listing Cases with `HasOpenQuery = true`. |

## Source by layer

| Layer | File | What it owns |
| --- | --- | --- |
| Web | `src/Pegasus.Web/Pages/Index.cshtml`, `Index.cshtml.cs`, `Pages/Shared/_WorkCentreBody.cshtml` | Work Centre page, `Office`/`Mine` scope switch, kind filter chips, `Needs attention` table and `OnPostAssignEngineerAsync` (`Take`). |
| Web | `src/Pegasus.Web/Presentation/NeedsAttentionPresentation.cs`, `OperatorLabels.cs` | Kind slugs, kind chip labels (`OperatorLabels.WorkCentre.KindChip`), row titles and action labels. |
| Core | `src/Pegasus.Core/Operations/DashboardCounts.cs`, `OperationsSnapshot.cs` | `NeedsAttentionKind`, `NeedsAttentionPolicy` (`IsMine`, `CanTake`, `HasPersonSlot`), `GetOperationsSnapshot.FetchAttentionInputsAsync`. |
| Infrastructure | `src/Pegasus.Infrastructure/Persistence/EfCaseQueryStore.cs` | Reads `CaseQueries` rows. |

## Behaviours

### `Office` vs `Mine` scoping and `Take`

In `_WorkCentreBody.cshtml`, `Office` lists team-wide items requiring action (such as `UnassignedEngineer`, `Triage`, `Unidentified`), while `Mine` lists items whose owner is the signed-in staff member (`NeedsAttentionPolicy.IsMine`). Rows for which `NeedsAttentionPolicy.CanTake` is true render a `Take` form (`data-wc-take`) beside the primary row link.

## Things the FRD does not settle

- How open queries (`CaseQueries` rows) surface in `Needs attention` across `Office` and `Mine` once queries have their own `AssigneeStaffId`.
