# Case (Correspondence and Queries) — how it works

Read from the live source on 26 October 2026 (`origin/dev` `373dcc81a`).

## What the page does not show

- `CaseQueryLedger` (`src/Pegasus.Infrastructure/Persistence/CaseQueryLedger.cs`) is the sole writer of `CaseQueries` and `CaseWorkflows.HasOpenQuery`, but mail queries and staff-logged queries enter through two different code paths: `RaiseForMailAsync` (triggered as a side-effect of `MailCategory.Query` on link or classification correction) and `IRaiseCaseQuery` (`Closure.cshtml.cs` `OnPostLogQueryAsync` and MCP `pegasus_case_action` `log_query`).
- `ResolveCaseQueries` (`CaseQueryLedger.ResolveAllAsync`) closes **every** open query on the Case in one transaction (`ClosedAs = Resolved`) and clears `HasOpenQuery`. There is no way to mark one query done while leaving another open, and no way to reopen a resolved query.
- Both `RaiseCaseQuery` and `ResolveCaseQueries` inherit `CaseMutationRequest`, requiring a live Case edit lease token and `ExpectedVersion`. If a colleague is editing the Case, staff cannot log or resolve a query.
- `CaseQueryEntity` has no `AssigneeStaffId` column; queries cannot be assigned or taken independently of the Case's Engineer.
- The Engineer activity report (`EfEngineerActivityQueries.GetAsync`) and the Case list activity query count (`EfCaseListQueries.ActivityAsync`) count retained messages classified as `MailCategory.Query` rather than `CaseQueries` rows, so staff-logged queries are omitted from those counts.

## Governing documentation

| Document | What it settles for this page |
| --- | --- |
| `docs/adr/0067-case-query-records-and-open-query-mark.md` | `CaseQueries` table, `CaseWorkflows.HasOpenQuery` mark, `CaseQueryLedger` as sole writer, all-at-once resolution and no per-query assignee. |
| `docs/frd/frd-10-automation-api-and-mcp-surface.md` | `pegasus_case_action` (`log_query`, `resolve_query`) and `pegasus_mail_send` (`resolveQuery`). |
| `docs/frd/frd-12-identity-authorisation-and-staff-notifications.md` | `QueryReceived` notification to the Case's assigned Engineer. |
| `docs/frd/frd-13-case-lifecycle-and-workflow.md` | `ReportSent` stage, the `Query` stage overlay (`CaseQueryRules.IsQueryStage`), and query eligibility (`CaseQueryRules.CanLog`). |
| `docs/frd/frd-16-case-record-workspace.md` | `Files › Correspondence` table, `Queries` section, ribbon `Actions` menu (`Log query`, `Resolve query`) and `Next action` aside. |
| `docs/frd/frd-17-operational-reporting-and-audit-views.md` | Engineer activity report `Queries` count and action history labels. |

## Source by layer

| Layer | File | What it owns |
| --- | --- | --- |
| Web | `src/Pegasus.Web/Pages/Cases/Closure.cshtml.cs`, `Details.Queries.cs`, `Details.Frame.cs` | `OnPostLogQueryAsync`, `OnPostResolveQueryAsync`, `OnPostDraftQueryReplyAsync`, ribbon action predicates. |
| Web | `src/Pegasus.Web/Pages/Cases/Shared/_CaseCorrespondence.cshtml`, `_CaseQueries.cshtml`, `_CaseAside.cshtml`, `_CaseRibbon.cshtml`, `_CaseDialogs.cshtml`, `_ResolveQueryForm.cshtml` | Correspondence table (`Classification`, `Tag as query`), Queries table (`State`, `Raised`, `Raised by`, `Channel`, `Message`, `Resolved`), Next action (`Resolve query` / `Reply`), ribbon `Actions` menu, `Log query` dialog. |
| Web | `src/Pegasus.Web/Presentation/CaseNextAction.cs`, `CaseWorkspaceLabels.cs`, `OperatorLabels.cs` | Next-action step selection, section and column labels, status chip tones and action history labels. |
| Web (MCP) | `src/Pegasus.Web/Mcp/CaseLifecycleMcpTools.cs` | `pegasus_case_action` (`log_query`, `resolve_query`). |
| Core | `src/Pegasus.Core/Lifecycle/CaseQueryLifecycle.cs`, `src/Pegasus.Core/Workflow/CaseWorkflowContracts.cs`, `src/Pegasus.Core/Cases/CaseQueries.cs` | `CaseQueryRules`, `RaiseCaseQuery`, `ResolveCaseQueries`, `CaseQueryItem`, `CaseOpenQueryRoute`. |
| Infrastructure | `src/Pegasus.Infrastructure/Persistence/CaseQueryLedger.cs`, `EfCaseWorkflowStore.cs`, `EfCaseQueryStore.cs`, `EfCaseListQueries.cs`, `EfEngineerActivityQueries.cs` | `CaseQueries` persistence, `HasOpenQuery` recomputation, `ActionHistory` events, query section read model, activity counts. |

## Behaviours

### Correspondence table and `Tag as query`

`_CaseCorrespondence.cshtml` lists linked messages with columns `Received`, `Sender`, `Subject`, `Classification` and `Action`. For a received message not already classified as `Query`, it renders a `Tag as query` form posting `/Inbox/{messageId}?handler=CorrectClassification` with `ClassificationKey=query` and `ReturnCaseId`.

### Queries section

`_CaseQueries.cshtml` lists open queries followed by closed (`Resolved`) queries, with columns `State` (`Query` purple / `Resolved` green), `Raised`, `Raised by`, `Channel`, `Message`, `Resolved` and `Action`. Open mail queries show `Open message`, `Reply` (or `Reply with AI draft`) and `Draft reply with AI`. Logged queries and resolved queries have no row actions.

### Next action and Actions menu

When `HasOpenQuery` is true, `CaseNextAction` returns a `ResolvesQuery` step. If `OldestOpenQuery` came by e-mail, `_CaseAside.cshtml` renders `Resolve query` as the label and a `Reply` link (`/Inbox/{id}?compose=reply&correspondenceCaseReference=…&resolveQuery=true`); otherwise it renders `_ResolveQueryForm.cshtml` (`Resolve query` submit button). The ribbon `Actions` menu renders both `Log query` and `Resolve query` when `!Model.ColleagueIsEditing`.

## Things the FRD does not settle

- How one Core route opens a query whether triggered from the Inbox, deterministic criteria, the AI classifier, Automation MCP or the Case page.
- How individual queries are assigned, taken, marked done one at a time and reopened without a Case edit lease.
