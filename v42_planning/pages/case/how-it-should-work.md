# Case (Correspondence and Queries) — how it should work

Decided with the operator on 26 October 2026 (rules **D1**–**D2**, settled items **D**–**E**)
and proposed for sign-off (rules **D3**–**D12**, open items **J**, **K**, **M**–**O**, **Q**, **X**–**AA**).

## Rules

- **D1 (D, settled 26 October 2026):** Every newly opened query starts with `AssigneeStaffId = null` (**Unassigned**) until a staff member takes it or assigns it.
- **D2 (E, settled 26 October 2026):** When a linked e-mail has `Type = Cancellation`, the Case aside continues to show the `Cancellation received` row with `Open message`.
- **D3 (J):** Query mutations (`OpenCaseQuery`, `MarkCaseQueryDone`, `ReopenCaseQuery`, `AssignCaseQuery`) require no Case edit lease, no `ExpectedVersion` and no reason; a colleague editing the Case does not block any query act.
  - Open: **J** — confirm no edit lease, expected version or reason on query acts.
- **D4 (K):** Each open query is marked done individually (`IMarkCaseQueryDone`, setting `ClosedAs = Resolved` and recomputing `HasOpenQuery` from remaining open queries); the closed chip and column header read **Done** (green tone, replacing `Resolved`); `Resolve query` is removed from the ribbon `Actions` menu; the `Next action` step when a query is open reads **Answer query** with **Reply** (when the oldest open query is an e-mail) or **Mark done** (when logged).
  - Open: **K** — confirm per-query **Mark done**, the **Done** chip/column, removing `Resolve query` from the `Actions` menu, and **Answer query** in `Next action`.
- **D5 (M):** Any staff role (`Administrator`, `Engineer`, `User`) and the `Automation` actor may **Reopen** a `Done` (`Resolved`, not `Withdrawn`) query with no reason while the Case is not archived or closed (`CaseQueryRules.CanReopen`), clearing its closure columns and setting `HasOpenQuery = true`.
  - Open: **M** — confirm `Reopen` eligibility across all staff roles and `Automation`.
- **D6 (N):** At most one non-withdrawn query exists per e-mail: **Open query** is offered in Case `Correspondence` (and in the Inbox Decision panel) when the row is a received e-mail, `CaseQueryRules.CanOpen` holds and the e-mail holds no non-withdrawn query; if the e-mail's query is `Done`, staff reopen it from `Queries` instead.
  - Open: **N** — confirm one query per e-mail and `Open query` replacing `Tag as query`.
- **D7 (O):** Each open query in `Queries` offers **Assign** (opening `#case-assign-query-dialog`, whose `Assigned to` select lists the signed-in person first as `Name (you)`, then enabled casework staff, then `Unassigned`) and, when not already assigned to the viewer, **Take** (assigning the viewer immediately); assigning a query to someone other than the actor sends a `Query assigned` notification linking to `/Cases/{id}?section=queries`.
  - Open: **O** — confirm the `Assign query` dialog, `Take` button and `Query assigned` notification.
- **D8 (Q):** Opening a query from an e-mail continues to notify the Case's assigned Engineer with `Query received`.
  - Open: **Q** — confirm keeping `Query received` for the Case's Engineer.
- **D9 (X):** In `Files › Correspondence`, the `Classification` column header becomes **Type**, displaying `Correspondence` (or `New instruction`, `Triage request`, `Cancellation`) followed by the e-mail's query chip (`Query` when open, `Done` when resolved).
  - Open: **X** — confirm the **Type** column and inline query chip in `Correspondence`.
- **D10 (Y):** Unlinking an e-mail from a Case withdraws its open query (`ClosedAs = Withdrawn`) and recomputes `HasOpenQuery`; there is no separate withdraw button.
  - Open: **Y** — confirm unlink as the sole query withdrawal path.
- **D11 (Z):** The Engineer activity report's `Queries` column (`EfEngineerActivityQueries`) and the Case list's query activity count (`EfCaseListQueries`) count `CaseQueries` rows with `ClosedAs` null or `Resolved` (excluding `Withdrawn`) rather than messages classified as `Query`.
  - Open: **Z** — confirm counting `CaseQueries` records in activity reports and the Case list.
- **D12 (AA):** `Query` remains the purple stage chip over the Case's stored state whenever `HasOpenQuery` is true (returning to the stored state, normally `Report sent`, when the last open query is marked done), and queries can be opened only once the report is sent (`CaseLifecycleRules.ReportIsSent`).
  - Open: **AA** — confirm keeping the purple `Query` stage overlay and the `ReportIsSent` gate.

## The actions and dialogs

- **Open query (`Details?handler=OpenQuery`):** takes `id`, `retainedMessageId`, `operationKey`, `section`; calls `IOpenCaseQuery` and redirects back to `/Cases/{id}?section=files|queries`.
- **Log query (`Details?handler=LogQuery`):** takes `id`, `operationKey`, `channel`, `details`; calls `IOpenCaseQuery` with no lease or expected version.
- **Mark done (`Details?handler=MarkQueryDone`):** takes `id`, `queryId`, `operationKey`; calls `IMarkCaseQueryDone`.
- **Reopen (`Details?handler=ReopenQuery`):** takes `id`, `queryId`, `operationKey`; calls `IReopenCaseQuery`.
- **Assign / Take (`Details?handler=AssignQuery`):** takes `id`, `queryId`, `operationKey`, `assignee` (`Guid` or `"unassigned"`); calls `IAssignCaseQuery`.

## Where this lands

| Page / component | Entry |
| --- | --- |
| `src/Pegasus.Core/Lifecycle/CaseQueryLifecycle.cs`, `CaseWorkflowContracts.cs` | `IOpenCaseQuery`, `IMarkCaseQueryDone`, `IReopenCaseQuery`, `IAssignCaseQuery`, `CaseQueryRules.CanOpen`/`CanMarkDone`/`CanReopen`. |
| `src/Pegasus.Infrastructure/Persistence/CaseQueryLedger.cs`, `EfCaseWorkflowStore.cs`, `EfCaseQueryStore.cs` | `AssigneeStaffId`, `AssignedAtUtc`, migration `_AssignableCaseQueries`, single writer methods `OpenForMessageAsync`, `OpenLogged`, `MarkDoneAsync`, `ReopenAsync`, `AssignAsync`. |
| `src/Pegasus.Web/Pages/Cases/Details.Queries.cs`, `Closure.cshtml.cs` | Move query handlers to `Details.Queries.cs` (no lease); delete `Closure.cshtml.cs` query handlers and `_ResolveQueryForm.cshtml`. |
| `src/Pegasus.Web/Pages/Cases/Shared/_CaseQueries.cshtml`, `_CaseCorrespondence.cshtml`, `_CaseAside.cshtml`, `_CaseRibbon.cshtml`, `_CaseDialogs.cshtml` | Assigned to and Done columns, row actions, Assign query dialog, Type column and Open query button, Answer query Next action. |
| `src/Pegasus.Web/Mcp/CaseQueryMcpTools.cs`, `CaseLifecycleMcpTools.cs` | New `pegasus_case_query` (`open`, `mark_done`, `reopen`, `assign`); remove `log_query`/`resolve_query` from `pegasus_case_action`. |

## Documentation impact when the FRD is written

- `ADR-0085` amends `ADR-0067` (all-at-once resolution and no-assignee consequences).
- Update `FRD-10`, `FRD-12`, `FRD-13`, `FRD-16`, `FRD-17` and `CONTEXT.md`.
