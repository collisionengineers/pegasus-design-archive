# Case record: Report delivery and the aside, how it works

Read from the live source on 4 November 2026 (`origin/dev` `8da7957ce`, after PR 1883).

## What the page does not show

- **There is no Subject field.** The e-mail's subject is derived when the send runs
  (`ReportDispatchPolicy.Subject`: "Re: " + the instruction's subject through
  `StaffMailReplySubject.For`, else "{REG} Report") and staff never see or edit it.
- **The companion documents' names are invisible.** The form shows one "File name" cell, the
  report's delivery name (`CaseReportDeliveryNaming.ReportName`, the Principal's pattern or
  "{Case/PO} {REG} {Outcome} report" with one dot per earlier send, then `.pdf`). The fee
  note, Repair Spec and Images go under their custody names
  (`{SLUG}_fee_note.pdf`, `_repair_specification.pdf`, `_images.pdf`), which the form never
  states, and filed estimates under their own.
- **Nothing on the form opens a file.** Open report and Open fee note are on the preview card
  above it; the Attach ticks are labels only.
- **Reading shows the form greyed** (From, To, Cc, Attach, File name, Message), with To and
  Cc reading the last send's addresses or "Not recorded" (v41 K5). The Attach ticks there are
  fixed (Report and Fee note on), not what was last sent.
- **Added recipient boxes cannot be removed.** Add To recipient and Add Cc recipient append an
  `<input>` (`case-workspace.js` `bindReportRecipients`); nothing removes one. An empty box
  is dropped by the send.
- **The Audit view shows nothing of the Inspection report's figures.** Figures is the Audit
  work's own (its Current spec's gross, its Engineer's Value, the ratio). The Inspection
  report's generation is loaded (`OtherReportGeneration`) but only its tick in the send form
  reads it.

## Governing documentation

| Document | What it settles for this page |
| --- | --- |
| FRD-11 "Companion documents and what a delivery attaches", "What a delivery is called", "From and subject", "Report sending rules" | What the send attaches and in what order, the delivered name, the derived subject, the rules' Questions, Holds, Stop and override, Attach overrides, required companions, the fingerprint |
| FRD-16 "Report", "Assessment" (the delivery form paragraph, which says the form "awaits its design sign-off"), "Case workspace" (the aside's cards), "Inspection and Audit views", "Decisions" | The preview card, Open report, the form's cells, read mode, the Views card, the aside order, Figures as the home of the repair cost and the Engineer's Value |
| FRD-21 "Outbound correspondence" | Where the send controls are, who may send, which mailbox (R651–R655), the 35 MB limit, what the composer carries |
| FRD-24 "Valuation sources", "Settlement" | The guide cards, the Engineer's Value and its basis, salvage on a total loss |
| Design authority "Case record frame", "Keyboard and dialog contract", "Source tags" | The aside (Views, Linked cases, Figures, Next action, Report not ready; the two-up strip below 1441px), the dialog contract, the `src-tag` word for a value's source |
| Rulings R178, R580, R651–R655 | The three Attach words; the registration once in the default name; which mailbox a send starts on and that From is a free choice |

## Sources by layer

| Layer | File | Owns |
| --- | --- | --- |
| Web | `Pages/Cases/Shared/_CaseReport.cshtml` | The Report section: head (Generate report or "Report not ready", the More menu), the preview card, the delivery form (edit) and its greyed cells (read), the report fields, Report wording, the Fee tab |
| Web | `Pages/Cases/Details.cshtml.cs` `OnPostSendReportAsync`, `LoadEngineerSectionsAsync` | The handler's parameters and guards; the reads behind the form (dispatch facts, the plan, senders, history, the other work's generation) |
| Web | `Pages/Cases/Details.Report.cs` | `ReportDeliveryFileName`, `OtherReportGeneration`, `OtherReportSendable`, `OtherReportDeliveryFileName`, `ReportDeliveryMessage` |
| Web | `Pages/Cases/Details.Views.cs` | `?view=inspection`, `IsInspectionView`, the work selector |
| Web | `Pages/Cases/Shared/_CaseAside.cshtml` | Views, Linked cases, Figures (`dl.figures`, "—" for an absent figure, money "£" + N2), Next action (the Send report step with its section jump), Report not ready |
| Web | `Pages/Cases/Shared/_CaseDialogs.cshtml`, `Details.cshtml:185` | The Case dialogs in `[data-case-dialogs]`, swapped in place |
| Web | `Pages/Cases/Shared/_CaseViewer.cshtml`, `[data-case-viewer-host]` | The full-screen viewer; `openDocument` for a PDF |
| Web | `wwwroot/js/site.js` | Dialogs: `bindBackdropDialogs`, `inertOutside` (spares `[data-dialog]` siblings only), the focus trap and Escape (`onKeydown`, topmost dialog only) |
| Web | `wwwroot/js/case-workspace.js` | `bindReportRecipients` (Add To / Add Cc), the document previews (`openInViewer`), the viewer (`buildViewer`, `show` adds `has-viewer`), in-place posts (`submitInPlace`, which closes any open Case dialog on a non-commit swap) |
| Web | `wwwroot/css/site.css`, `case-workspace.css`, `inbox.css` | `.dialog` 590px, `.dialog--wide` 820px, `.dialog--mail` 880px (Inbox only), `.mail-compose-dialog` 660×700 grid with a pinned footer; `#section-report .recip-form` rules; `.case-viewer` z-index 1200; `[tabindex]:focus-visible` z-index 2 |
| Core | `Reports/CaseReportDelivery.cs` | `SendCaseReport`, `CaseReportDeliveryPolicy.Attachments`, `CaseReportDeliveryNaming`, `CaseReportSendHistory` |
| Core | `Reports/ReportDispatchPolicy.cs` | The plan (Questions, Holds, Stop, Cc, filed estimates), `Subject` |
| Core | `Operations/StaffMailSendEngine.cs` `StaffReportSend.AttachmentsMatch` | Only the lead report of each block may carry a different name, non-blank and `.pdf` |
| Core | `Operations/CaseMailSender.cs` | `StaffMailAnswer` (R655): From starts on the default, any send-ready Outgoing mailbox may be chosen |
| Core | `Reports/CaseReportGeneration.cs` `CaseReportGenerationSnapshot` | `Costs`, `EngineerValue`, `AppliedValuationId`, `Guides`, `Report` (outcome, salvage category and value) |
| Core | `Assessment/Valuations.cs`, `ValuationCalculations.cs` | `ValuationSource`, `ValuationPolicy.SourceName`, `AppliedValuation.GuideValuationId` |

## Behaviours

### The delivery form exists only while editing with a stored report

`canSendReport = editing && generation Confirmed && report artifact Confirmed`
(`_CaseReport.cshtml`). Reading draws the same cells greyed (v36 item Z) and no Send.

### The form's fields, top to bottom

Already sent line; Stop notice and "Override reason" (required once a Stop is decided);
missing-companion notices; "Answer before sending" Yes/No radios per undecided rule;
"Reviewed recipients": From (a select, R655), To and Cc stacks with Add To recipient / Add
Cc recipient and the Case's address book as a datalist; the Cc hint; "Attach": Report (a
static tick), Fee note (on), Repair Spec, Images, "(required for this Principal)" where a
rule requires one; once the Audit exists, the other work's report by its delivery name with
its own documents; "Filed estimate" names; warnings; "File name"; "Message" (9 rows, 5000);
"After sending"; Holds with "Done"; "Send report", omitted while a required companion is
missing.

### The send

`OnPostSendReportAsync` → `SendCaseReport.ExecuteAsync`: the lease and versions, the
message bounds, the plan decided (fingerprint, questions, stop reason, holds), recipients
reviewed (at least one To, valid, deduped), attachments built and the lead report renamed,
the second report added, the sender resolved, the subject derived, then
`IStaffReportSend.SendAsync`, which re-verifies every attachment by identity and hash. Every
outcome redirects to `?section=report&view=…`, and in the browser the record is swapped in
place; a non-commit post closes any open Case dialog.

### The aside

Views (once the Audit exists), Linked cases (while any Triage is linked), Figures (always),
Next action (while there is a step, an AI draft, a stale generation or an open task), Report
not ready (while anything is outstanding). Below 1441px the aside is a two-up strip above
the sections, single column at 760px. The Send report step is a link that jumps to the
Report section.

### The Audit view

`!IsInspectionView && Works.HasAudit`. Every section is the Audit work's; the Inspection view
(`?view=inspection`) edits the primary work's own values. `OtherReportGeneration` is read on
the full page whenever the Audit exists (not on the commit-answer path).

### The viewer and a dialog

A document preview opens the viewer (`openDocument`), z-index 1200 above the dialog backdrop's
1000, but `site.js` `inertOutside` puts `inert` on the viewer's host while a dialog is open,
and the live `[tabindex]:focus-visible` rule gives the focused viewer z-index 2 on
specificity. Nothing live opens the viewer from a dialog today.

## Things the FRD does not settle

- A staff-edited subject (today derived and never edited).
- A staff name for a companion document or a filed estimate (today custody and own names
  only), and whether a chosen name persists for the next send.
- The viewer over a dialog: the `inert` and the `focus-visible` z-index above.
- The Audit view reading the Inspection report's figures.
- Removing a To or Cc box once added.
- What the Next action step does while reading, once Send report opens a dialog while editing
  (the mockup keeps the jump while reading).
