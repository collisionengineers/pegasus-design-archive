# v48 notes: the Send report dialog and the Original report card

The round opened on 4 November 2026. The live source was read from Pegasus `origin/dev`
`8da7957ce` (`captured-live/_source/source.txt`), which includes PR 1883 (R655, From is a
default on every send). The brief, the three planning questions, the operator's answers and
the note on removable recipients are in [discussion-log.md](discussion-log.md).

## 1. What changes

| # | Today (problem) | Proposal | Shots |
| --- | --- | --- | --- |
| 1 | The delivery form sits inline in the Report section while editing: a long block of From, To, Cc, Attach ticks, a read-only File name, a nine-row Message and Send report, under the preview card | **Send report** is the Report head's primary while editing with the report stored (Generate report is the primary until then), and the aside's Next action step. Both open the **Send report** dialog (A) | 001/002, 003/004 |
| 2 | The form is a bespoke block (`recip-form`); the Inbox, Triage and Chaser composers are a different shape | The dialog is the Triage composer's shape (`.dialog.mail-compose-dialog`), 880px wide (the Inbox message dialog's width): From, To, Cc, Subject, Message, Files, the rules' blocks, Cancel and Send report pinned in the foot (B) | 004, 021–023 |
| 3 | There is no Subject; the send derives it ("Re: " + the instruction's subject, or "{REG} Report") and staff never see it | **Subject**, prefilled with the derived subject, editable (C; operator, 4 November 2026) | 004, 010 |
| 4 | Attach is a row of ticks with labels; one "File name" cell names the report; the companions' and estimates' names are never shown; nothing opens a file | **Files**: one row per attachment with its include tick (the live tick: the report and a required companion static and on, the fee note on, Repair Spec and Images off, the other work's report and its documents off, filed estimates on), the file glyph, its name, its kind and size, and Rename. The name opens the file in the Case viewer over the dialog (D, F) | 004, 005, 010, 015 |
| 5 | Only the report can carry a different name, and only through the Principal's pattern; companions keep their custody names | **Rename** on every row: the stem is edited, `.pdf` stays, Reset restores the policy name; a changed name is posted (E) | 006, 012 |
| 6 | Add To recipient and Add Cc recipient grow the stacks with no way back | Each To or Cc box has its ×; the one remaining To box keeps none (O; operator, 4 November 2026) | 004 |
| 7 | The Principal's rules draw questions, holds, a Stop and its reason, a missing companion, the Cc hint, After sending, in the same block | Unchanged, moved into the dialog with their words (D): the notices first, the questions, warnings, After sending and holds after Files; Send withheld with Cancel only while a companion is missing | 009, 010, 011 |
| 8 | Reading draws the form's cells greyed (From, To, Cc, Attach, File name, Message) | The Report section keeps the preview card; the greyed cells go, so read and edit share one geometry (G). A report already sent says so under the preview card as well as in the dialog (N) | 007/008, 012 |
| 9 | The Audit view of an Inspection + Audit Case shows nothing of the Inspection report's figures; Figures is the Audit's own | **Original report**, a card after Figures in the Audit view: Repair cost inc VAT, Salvage value on a Total loss, Engineer's Value with the guide in brackets, from the Inspection report as generated (I–M; operator, 4 November 2026) | 013/014, 016/017, 018/019, 020, 024, 025 |

Shot numbers are the `NNN-` prefixes in [../shots](../shots): each comes at 1580, 1440 and
760 with a `-dialog`, `-panel` or `-card` crop, a 1580 `-dialog-full` (the whole dialog) or
`-full` (the whole page), and the five variable shots 021–025.

## 2. Live rules the mockup mirrors

| Rule | Source |
| --- | --- |
| The send form exists while editing with a Confirmed generation and a Confirmed report; reading draws greyed cells | `_CaseReport.cshtml` `canSendReport`, `reportSendable` |
| Generate report is the head's primary until the report and its fee note are stored; the fixtures confirm every companion so the head is free | `_CaseReport.cshtml` `canGenerate`, `feeNoteOutstanding` |
| From starts on the default and may be any send-ready Outgoing mailbox (R655) | `CaseMailSenderOptions`, `StaffMailAnswer` |
| The subject the send derives | `ReportDispatchPolicy.Subject`, `StaffMailReplySubject.For` |
| The delivered name: the Principal's pattern, else "{Case/PO} {REG} {Outcome} report" with one dot per earlier send | `CaseReportDeliveryNaming.ReportName` (R580) |
| The companions' custody names | `CaseReportGeneration.FileNameOf` (`{SLUG}_report\|fee_note\|repair_specification\|images.pdf`) |
| Which attachments a send offers and which are required | `CaseReportDeliveryPolicy.Attachments`, `ReportDispatchPolicy.Plan` (`RequiredCompanions`, `MissingCompanions`, `FiledEstimates`) |
| The other work's report in the same send once the Audit exists, off until ticked | `DetailsModel.OtherReportSendable`, `OtherReportDeliveryFileName` (operator, 12 October 2026) |
| Questions, Holds with Done, a Stop with its reason, the Cc hint, After sending | `ReportDispatchPolicy.Plan`, `CaseWorkspaceLabels.ReportDelivery` |
| The dialog contract: `[data-dialog-open]`, focus trap, Escape on the topmost dialog, inert outside | `site.js` `bindBackdropDialogs`, `inertOutside` |
| A document preview opens the Case viewer; Escape closes it and focus returns to the invoker | `case-workspace.js` `openDocument`, `show`, `close` |
| The aside: Views, Linked cases, Figures, Next action, Report not ready; a two-up strip below 1441px | `_CaseAside.cshtml`, `site.css` 946–967 |
| The Audit view and the Inspection view | `Details.Views.cs` (`IsInspectionView`, `?view=inspection`) |
| Figures' money and the absent mark | `_CaseAside.cshtml` `FormatMoney`, `.figures dd.absent` |
| The Inspection report's snapshot | `CaseReportGenerationSnapshot` (`Costs`, `EngineerValue`, `AppliedValuationId`, `Guides`, `Report.Outcome/SalvageValue`) |
| The guide's word | `AppliedValuation.GuideValuationId` → `CaseValuation.Details.Source` → `CaseWorkspaceLabels.Valuation.SourceLabel` |

## 3. Frame numbers

- **Dialog.** `.dialog.mail-compose-dialog.dialog--send`: 880px wide (1100 as a variable),
  at most 760px tall, the Triage composer's grid: head 10px 16px, fields scroll, foot pinned
  with Cancel and Send report. Below 540px it fills the viewport. The dialog backdrop is
  z-index 1000; the viewer 1200.
- **Addresses.** Two columns (the Triage composer's): From then Cc on the left, To on the
  right; each stack's Add button under it, 4px below; each box with its × (28px, `btn--icon`).
- **Files.** One row per attachment, 6px apart: a 4-column grid (tick · 20px glyph · name and
  "{kind} · {size}" · Rename), 6px 9px padding, 1px `--line` border, 12px text; the name 650
  weight, one line, ellipsed. Renaming: the input at the control height, ".pdf" in mono,
  Reset. Beside the message (a variable, 900px and up): a second column of 36%, at least 300px.
- **Card.** The Figures card's shape: `panel-head` 51px minimum, `dl.figures` 6px apart, 12.5px
  rows, the repair cost 17px (`figure--big`), values 650 weight tabular. 285px in the aside
  at 1441px and above; one cell of the two-up strip below; full width at 760px.
- **Head.** Send report is `btn btn--small btn--primary` with the send glyph, first in the
  Report head's actions, before More and the section tools.

## 4. Decisions and authority

| Decision | Authority |
| --- | --- |
| Send report moves into a dialog with a composer; files are clickable to preview and renameable | Operator brief, 4 November 2026 |
| An Original report card on an Inspection + Audit Case, in the Audit view only, with the repair cost, the salvage value on a total loss, and the Engineer's Value with the guide in brackets | Operator brief, 4 November 2026 |
| The card reads the Inspection report as generated, not the live Inspection values | Operator, 4 November 2026 ("Inspection report as generated (Recommended)") |
| Subject is editable, prefilled with the derived subject | Operator, 4 November 2026 ("Editable, prefilled (Recommended)") |
| Send report opens only while editing, as today | Operator, 4 November 2026 ("Only while editing, as today (Recommended)") |
| Every To or Cc box is removable | Operator, 4 November 2026 ("extra recepients/cc box isn't removable - adjust") |
| The composer's shape, width and labels | The Triage composer (`_TriageCase.cshtml`), the Inbox message dialog's width (`inbox.css`) |
| The card's labels and money | `CaseWorkspaceLabels.Frame.OriginalReport`, `RepairCostIncVat`, `EngineersValue`, `Settlement.SalvageValue`; the aside's `FormatMoney` |
| The aside order with the card after Figures | Proposal, item I; the guardrail's aside order is kept and extended |
| "Engineer's Value" and "£5,000.00" rather than the brief's "Engineers Value" and "£5000" | Live vocabulary and format; items L and the money variable |

## 5. Coverage audit and departures from live

Every control and fact of the live Report section (`v48-plain-edit.html`,
`v48-rules-edit.html`, `v48-stop-edit.html`, `v48-missing-edit.html`, `v48-resend-edit.html`,
`v48-audit-edit.html`, `v48-plain-read.html`) and the aside (`v48-audit-*.html`):

| Live item | Proposal |
| --- | --- |
| Head: Generate report / "Report not ready", More (Preview draft, Preview Repair Spec, Preview images, Generate Repair Spec, Generate images), Edit, fold | Unchanged; Send report added first while editing with the report stored |
| Report / Fee tabs, the preview card (title, Generated, filing chip, Open report, Open fee note), Report date, Engineer's comments, Report wording, the Fee tab | Unchanged |
| Hidden fields (operation key, lease token, versions, generation, view, fingerprint) | Carried whole into the dialog's form |
| "Already sent on … to …" | In the dialog, and under the preview card (N) |
| Stop notice, Override reason | In the dialog, first |
| Missing companion notice; no Send | In the dialog; Cancel only |
| "Answer before sending", Yes / No per question | In the dialog after Files |
| "Reviewed recipients", From select, To and Cc stacks, Add To recipient, Add Cc recipient, the address book | In the dialog; each box with its × (O) |
| Cc hint | Under the addresses |
| Attach: Report (static), Fee note, Repair Spec, Images, "(required for this Principal)" | The ticks of the Files rows, the same elements |
| The other work's report by its delivery name, its documents | Files rows, "Inspection · Report" and so on |
| Filed estimate names | Files rows, "Filed estimate", on, posting nothing |
| Warnings | After Files |
| File name | The report row's name (the same `ReportDeliveryFileName`) |
| Message | The dialog's Message |
| After sending | After Files |
| Holds with Done | After Files |
| Send report | The dialog's foot |
| Read mode: From, To, Cc, Attach, File name, Message greyed | Removed (G) |
| Aside: Views, Linked cases, Figures, Next action (the Send report step), Report not ready | Unchanged; the step opens the dialog while editing; Original report added after Figures in the Audit view |

**Departures from live, deliberate:**
- The greyed read-mode cells are removed (G): reading no longer repeats the delivery cells.
- The "File name" cell becomes the report row's name; the "Attach" and "Filed estimate"
  legends become rows (D).
- Subject is added (C); each extra To / Cc box gets a × (O); Cancel is added to the foot.
- The Next action step is a button while editing (A); the jump stays while reading.

**Not shown:**
- The Report section with no stored report (Generate report as the primary, Report not ready):
  unchanged by the round.
- A refused send reopening the dialog on its notice (N): the mockup's Send closes the dialog
  and posts to the strip.

## 6. Sign-off

Each item reads "Confirm, or …". The three planning answers (C, H, K) and the operator's
note (O) are built in and listed for the record.

- **A. The openers.** Send report is the Report head's primary while editing with the report
  stored, and the aside's Send report step opens the same dialog while editing (the jump
  while reading). **Confirm, or** keep Send report inside the section body as well.
- **B. The dialog.** The Triage composer's shape at 880px (the Inbox message dialog's width),
  Files below the recipients. The strip draws 1100px and Files beside the message for
  comparison. **Confirm, or** choose 1100 / beside.
- **C. Subject.** Editable, prefilled with the derived subject (operator, 4 November 2026).
  FRD-11 "From and subject" changes. **Confirm.**
- **D. Files rows.** One row per attachment with the live include tick, the name, the kind
  and size, and Rename; filed estimates listed as rows, on; the other work's report and its
  documents as rows, off. **Confirm, or** leave the filed estimates out of the list.
- **E. Rename.** Every attachment: the stem is edited, `.pdf` stays, Reset restores the
  policy name; Core accepts a staff name on every attachment (today the lead report only).
  **Confirm, or** rename the report only.
- **F. Preview.** A file's name opens the Case viewer over the dialog; Escape closes the
  viewer first, then the dialog. Stage 2 exempts the viewer's host from the dialog's inert
  and keeps the viewer's z-index when focused (the live `[tabindex]:focus-visible` rule
  lowers it to 2). **Confirm.**
- **G. The section.** The preview card stays; the inline form and the greyed read cells go.
  **Confirm, or** keep a read summary (From, To, Cc) under the card.
- **H. While editing only**, as today (operator, 4 November 2026). **Confirm.**
- **I. The card.** On an Inspection + Audit Case, in the Audit view only, after Figures.
  **Confirm, or** before Figures (drawn by the strip).
- **J. The heading.** "Original report", the existing label. **Confirm, or** give the words.
- **K. The source.** The Inspection report as generated; "—" until one exists (operator,
  4 November 2026). **Confirm.**
- **L. The rows.** Repair cost inc VAT; Salvage value only on a Total loss; Engineer's Value
  with the basis guide's word in brackets, none for a typed value; money as the aside draws
  it ("£5,000.00 (Cazana)", not "£5000"; the strip draws whole pounds). **Confirm, or**
  whole pounds.
- **M. Below 1441px** the card is one more cell of the two-up strip; no new breakpoint.
  **Confirm.**
- **N. After Send** the page swaps and the dialog closes, as every in-place post does today;
  a refused send reopens the dialog with its notice; a report already sent says so under the
  preview card too. **Confirm, or** keep the notice on the page only.
- **O. Recipients.** Every To or Cc box after the first To has its ×; Add To recipient and
  Add Cc recipient add a removable box (operator, 4 November 2026). **Confirm, or** let the
  last To box go too.

## 7. Self-check

`python -X utf8 build/check-v48.py` on 4 November 2026: `RESULT {"fail": [], "okCount": 416}`,
with no page or console error on any state in Today or Proposal (`shots/verification.json`,
151 shots). The check proves: Today is live (the inline form, no dialog, no
card); the openers and the one form in the dialog; every hidden field, From, To, Cc and
Message equal to Today's; Subject per fixture; the Files rows, names and ticks per fixture;
the × on every added box and none on the sole To; the viewer over the dialog with the host
not inert and Escape order; Rename, Enter, Escape and Reset; the rules' blocks; Send with
questions unanswered or a Stop without a reason posts nothing, and a decided send posts the
live fields with Subject; Cancel, × and the backdrop close; the card after (or before)
Figures with its rows and money, absent on the Inspection view and on an Inspection Case;
the widths at 1580, 1440 and 760.

## 8. Known limits

- There are no files behind a mockup: the viewer opens a drawn page bearing the file name,
  and the sizes in the Files rows are synthetic (1.2 MB, under 0.1 MB, 0.3 MB, 4.8 MB,
  0.2 MB).
- Send posts to the strip (`window.__mock.lastPost`) and closes the dialog; the live swap,
  the status notice and a refusal are not drawn.
- The Audit work's own Figures stay the fixture's (£270.00 / £5,000.00 / 5%); the Inspection
  report's figures (£7,850.00, £1,250.00, £5,000.00 on Cazana) are the frozen snapshot the
  capture fixture sets.
- Font fallback where Inter Variable is not installed is the live page's.
- The dialog's eyebrow is the Case/PO; the Audit view's send could name the Audit reference
  instead (Stage 2 detail).
