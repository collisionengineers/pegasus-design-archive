# v48 Stage 2 plan (built 4 November 2026)

Written during Stage 1, 4 November 2026, against Pegasus `origin/dev` `8da7957ce`. It waits
for items A–O and the operator's approval. Re-derive it if it is older than a week when
built.

The branch is `task/v48-send-dialog-original-report`, from `origin/dev`, in
`../pegasus-worktrees/v48-send-dialog-original-report`. Delivery follows
`razor-html-mockup-conversion`.

## Core

- `Reports/CaseReportDelivery.cs` `SendCaseReportRequest` / `SendCaseReport`: a posted
  `Subject` (trimmed, bounded as `StaffMailSendCommand` bounds it) replaces the derived one
  when given, else the derived one stands (C). Per-attachment names: `AttachmentNames`
  keyed by kind, and for the second report; `CaseReportDeliveryNaming.Named` applies a staff
  name to any attachment, non-blank and `.pdf`; `StaffReportSend.AttachmentsMatch`
  (`Operations/StaffMailSendEngine.cs`) accepts a differing name on every attachment under
  the same bound (E). Custody names and the Principal pattern stay the defaults.
- `ReportDispatchPolicy.Subject` unchanged; the form prefills from it.
- No Core change for the card: the Web reads the other work's generation and resolves the
  basis card through the existing `IListAppliedValuations` / `IListCaseValuations` with the
  primary work selector (K, L).
- MCP (`Mcp/SendMcpTools.cs` `pegasus_report_send`): `subject` and `attachmentNames`
  accepted the same way (FRD-10).

## Web

- `_CaseReport.cshtml`: the inline form and the greyed read cells go; the head gains the
  Send report primary while `canSendReport` (`data-dialog-open="case-send-report-dialog"`);
  the Already sent line under the preview card when `ReportSendHistory.LastSentAtUtc` (G, N).
- New `Pages/Cases/Shared/_CaseSendReportDialog.cshtml`, rendered inside `[data-case-dialogs]`
  while `canSendReport`: the composer (`.dialog.mail-compose-dialog.dialog--send`), the same
  hidden fields and names, `subject`, the Files rows with `fileName-{kind}` /
  `secondFileName-{kind}`, each To / Cc box with its × (O). Labels in
  `CaseWorkspaceLabels.ReportDelivery` (Subject, Files, Rename, Reset, Cancel, Remove
  recipient).
- `_CaseAside.cshtml`: the Send report step is a `data-dialog-open` button while editing and
  the jump while reading (A); the Original report card after Figures when
  `!IsInspectionView && Works.HasAudit`, from `OtherReportGeneration` plus the primary work's
  applied valuation and card (I–M); labels `Frame.OriginalReport`, `Frame.RepairCostIncVat`,
  `Settlement.SalvageValue`, `Frame.EngineersValue`.
- `Details.cshtml.cs`: `OnPostSendReportAsync` binds `subject` and the names; a refused send
  returns with `?dialog=send-report` so the dialog reopens on its notice (N);
  `LoadCommitResultAsync` loads what the card reads so the aside swap keeps it.
- `case-workspace.js`: `bindReportRecipients` adds the × and removes a box; the Files row
  name opens `openInViewer`; rename and Reset; `submitInPlace` keeps the dialog open on a
  refusal (N).
- `site.js`: the dialog's `onKeydown` yields while `body.has-viewer`; `inertOutside` spares
  `[data-case-viewer-host]` (F).
- `case-workspace.css`: `.dialog--send` width 880px, the `.recip-form` rules re-scoped to
  the dialog, the Files rows, `.v48-recipient` (named `.recip-box`), and
  `.case-viewer[tabindex]:focus-visible{z-index:1200}` or the viewer excluded from the
  shared focus-visible z-index (F). No new breakpoint (M).
- Follow `pegasus-ui-guardrails` and `references/case-workspace.md` (aside order, no second
  breakpoint).

## Documentation

- FRD-11: "What a delivery is called" (staff names on every attachment, Reset), "From and
  subject" (Subject editable, prefilled), "Report sending rules" (the dialog).
- FRD-16: "Report" (the head's Send report, no inline form, no greyed cells; the "awaits its
  design sign-off" sentence retired), "Case workspace" (aside order), "Inspection and Audit
  views" (the card), "Decisions" (Figures and Original report).
- FRD-21: "Outbound correspondence" (where the controls are; what the composer carries).
- FRD-10: the send tool's `subject` and names.
- Design authority: the Case record frame (dialog, viewer over a dialog, aside order), the
  component catalogue (`dialog--send`, the Files row, `recip-box`).
- Rulings: rows for the brief, the three planning answers, the removable boxes (O) and the
  sign-off, numbered at combine.
- The guardrail reference `case-workspace.md`.

## Tests

- Core: `CaseReportDeliveryTests` — a posted subject replaces the derived one; a blank or
  over-long subject refused; names on every attachment accepted and applied; a non-`.pdf`
  name refused; `AttachmentsMatch` with renamed companions.
- Web: `CaseReportDeliveryWebTests` — the dialog's fields and hidden inputs; the head opener
  while editing with a stored report, absent while reading or before storage; Subject
  prefilled; Files rows per fixture; rename round-trip posts `fileName-*`; a refused send
  reopens the dialog; the × removes a box and the sole To keeps none.
- Web: `CaseViewsWebTests` — the card on the Audit view with the three rows and the guide
  word; no Salvage row on a Repairable; absent on the Inspection view, on a standalone
  Audit and before an Inspection generation exists; present after a commit swap.
- A no-growth query-count pair for the Case page open (R458, 500 ms budget).

## Conformance

v47's `conformance/build-conformance.py` / `check-conformance.py` pattern: capture the task
worktree with the same fixtures, build with no patches, run the Stage 1 checks minus the
Today-only ones.
