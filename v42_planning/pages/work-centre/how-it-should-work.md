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

## Decided 27 October 2026

Signed off by the operator ("I sign off on this design"): rule **D1** and item **P** are settled as drawn in `pegasus_v42.html` (`9fd9869`).

## Work Centre Simplification — 5 Candidate Designs (`WC1`–`WC5`, item **AC**)

The live Work Centre (`/`) stacks two stat blocks above a `Needs attention` ledger with an `Office` / `Mine` scope toggle, ten separate kind-filter chips (`Case`, `Held`, `Review`, `Unassigned`, `With Engineer`, `Vehicle images paired`, `Unidentified`, `Triage`, `Tasks`, `AI draft`), and priority group rows.

In v42 (`work-centre-a` .. `work-centre-e`), `Needs attention` is replaced by five candidate workspace layouts built around three focused views while preserving the operational statistics:

1. **New Cases (first / default view):** Shows newly arrived Cases across every intake channel (`Principal API`, `E-mail`, `Manual`, `Automation`), since `/Inbox` only lists emails.
2. **System Actions:** Shows automated actions Pegasus has taken on Cases (automatic email-to-Case matching via conversation thread, claim reference, or VRM + accident date; early vehicle images paired to a Case; deterministic PAV-dispute query creation; cancellation matching & flagging).
3. **AI Actions:** Shows AI deliverables and jobs on Cases (`Estimate done` / `Draft ready`, `Draft to a query`, `Estimate done · Taken`, active generation, and failed estimate extraction).
4. **Stats:** Preserves the 5 Office queue totals (`Not ready`, `Review`, `Held`, `Unidentified`, `Triages`) and the `Activity` throughput figures (`Today` and `This week` across `New cases`, `Sent to Engineer`, `Reports sent`, `E-mails received`).

| State | Code | Design |
| --- | --- | --- |
| `work-centre-a` | **WC1** | **Design A — Streamlined ledger:** Side-by-side `Office queues` and `Activity` stat cards above a unified 3-tab ledger (`New Cases`, `System Actions`, `AI Actions`) with contextual channel/kind sub-filters. |
| `work-centre-b` | **WC2** | **Design B — KPI ribbon & split inspector:** Ultra-compact single-row Queue + Activity ribbon above a 2-pane `.pane-layout` workbench with selectable rows on the left and a live Case / AI output inspector pane on the right. |
| `work-centre-c` | **WC3** | **Design C — Three-column live board:** 9-cell unified metric bar above a 3-column simultaneous operations board showing `New Cases`, `System Actions`, and `AI Actions` side by side (with 1-click single-stream focus). |
| `work-centre-d` | **WC4** | **Design D — Telemetry sidebar & priority stream:** `276px` left telemetry rail for `Office queues` and `Today` / `Week` `Activity` beside a full-height stream starting at the top of the viewport. |
| `work-centre-e` | **WC5** | **Design E — Command deck & action cards:** Dark charcoal `.record-head` command deck with Queue and Activity tiles above 3 view selector cards and structured 4-zone Case action cards. |
