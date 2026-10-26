# Work Centre — how it should work

Decided with the operator on 26 October 2026 (item **D**: a new query is Unassigned until
taken or assigned) and proposed for sign-off (rule **D1**, open item **P**).

## Rules

- **D1 (P):** `NeedsAttentionKind` gains `Query` (chip label `Query`, slug `query`, `HasPersonSlot = true`):
  - On the `Office` view, each **Unassigned** open query on a non-archived Case appears as a `Needs attention` row (`Owner = Unassigned`, `Due = No due date`, task title = the query e-mail's subject or logged details, record = Case reference and vehicle) with row action **Open query** (`/Cases/{id}?section=queries`) and **Take** (`/?handler=TakeQuery` posting `queryId` to `IAssignCaseQuery` with the viewer).
  - On the `Mine` view, each open query assigned to the signed-in staff member (`AssigneeStaffId == viewerStaffId`) appears with **Open query** and no `Take` button.
  - `Cases › Queries` (`/Cases?stage=query`) continues to list one row per Case in the `Query` stage.
  - Open: **P** — confirm Work Centre `Needs attention` rows for Unassigned (`Office`, with `Take`) and viewer-assigned (`Mine`) open queries, and keeping `Cases › Queries` at one row per Case.

## The action

- **Take (`/?handler=TakeQuery`):** `IndexModel.OnPostTakeQueryAsync(Guid queryId, string operationKey, string? returnUrl)` calls `IAssignCaseQuery.ExecuteAsync` with the signed-in staff member's `StaffId` and redirects back to `returnUrl` (mirroring `OnPostAssignEngineerAsync`).

## Where this lands

| Page / component | Entry |
| --- | --- |
| `src/Pegasus.Core/Operations/DashboardCounts.cs`, `OperationsSnapshot.cs` | Add `NeedsAttentionKind.Query`, `ListOpenQueriesForAttentionAsync` on the Core query read port, and `NeedsAttentionPolicy` arms for `Query` (`IsMine`, `CanTake`, `HasPersonSlot`). |
| `src/Pegasus.Infrastructure/Persistence/EfCaseQueryStore.cs` | Implement `ListOpenQueriesForAttentionAsync`. |
| `src/Pegasus.Web/Presentation/NeedsAttentionPresentation.cs`, `OperatorLabels.cs` | Add `Query => "Query"` chip label, `query` slug and `Open query` action label. |
| `src/Pegasus.Web/Pages/Index.cshtml.cs`, `Pages/Shared/_WorkCentreBody.cshtml` | Add `OnPostTakeQueryAsync` and bind `data-wc-take` on `Query` rows to `?handler=TakeQuery`. |

## Documentation impact when the FRD is written

- Update `FRD-15` (`Needs attention` kinds, `Office`/`Mine` rules and `Take` on open queries).
