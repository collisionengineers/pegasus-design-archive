# v48 discussion log

How the round came to be. This log is not design authority.

## Round 1: brief and planning questions, 4 November 2026

**Brief (operator):**

> Plan a mockup incorporating the following:
>
> 1. Send report moves to a dialogue box with a composer
>
> - Files clickable to preview
> - Files renameable
>
> 2. Additional box on the right hand rail for Inspection+Audit cases (only for the audit case).
> Must show:
>
> - Original report repair cost
> - Salvage value (if total loss)
> - Engineers Value (with guide chosen for original report in brackets. E.g. £5000 (Cazana)

**Explored.**
- The live delivery form (`_CaseReport.cshtml` at `origin/dev` `8da7957ce`, after PR 1883's
  From select, R655): its fields, notices, questions, holds, the Attach ticks, the read-only
  File name and the greyed read-mode cells; `OnPostSendReportAsync` and `SendCaseReport`.
- How the subject is derived (`ReportDispatchPolicy.Subject`, never staff-edited) and how
  attachments are named (`CaseReportDeliveryNaming`; only the lead report may differ from
  its custody name, `StaffReportSend.AttachmentsMatch`).
- The three composers (Inbox, Triage, Chaser) and the dialog contract (`site.js`), the Case
  viewer (`openDocument`) and the dialog's `inert` rule, which inerts the viewer's host.
- The aside (`_CaseAside.cshtml`): Views, Linked cases, Figures, Next action, Report not
  ready; the Audit view (`Details.Views.cs`); `OtherReportGeneration` and its snapshot; the
  valuation sources and the basis card (`AppliedValuation.GuideValuationId`).
- The live vocabulary: "Engineer's Value", "Salvage value", "Original report", "Repair cost
  inc VAT"; money as the aside draws it ("£5,000.00").

**Questions and answers.**

| Question | Operator's answer |
| --- | --- |
| The card's source: the Inspection report as generated (the frozen snapshot), or the Inspection work's live values, which the Inspection view can still edit after the report was sent? | "Inspection report as generated (Recommended)" |
| Subject: today derived ("Re: " + the instruction's subject, or "{REG} Report") and never staff-edited; the Triage and Inbox composers show an editable Subject. Editable, prefilled? | "Editable, prefilled (Recommended)" |
| Send report today exists only in the page-wide edit session; should the dialog open from read mode too? | "Only while editing, as today (Recommended)" |

**Made.**
- Ten fresh captures of `origin/dev` `8da7957ce` behind the recording store: the delivery form
  under a plain Principal, a Principal with rules, a Stop, a missing companion, a resend, and
  an Inspection + Audit Case in both views with the Inspection report frozen as a Total loss
  on a Cazana guide and as Repairable on Glass's.
- The mockup over them: the Send report dialog and the Original report card.

**Raised.** Items A–N in [v48-notes.md §6](v48-notes.md#6-sign-off).

## Round 1, addition during the build, 4 November 2026

**Operator** (on the To / Cc boxes, which Add To recipient and Add Cc recipient grow today
with no way back):

> extra recepients/cc box isn't removable - adjust

**Changed.** Every To or Cc box in the dialog carries its ×. Add To recipient and Add Cc
recipient add a box with its ×; the one remaining To box keeps none, since a send needs a To.

**Raised.** Item O.

## Round 2: Stage 2 questions, 4 November 2026

**Operator:** "Plan out full integration of this".

**Questions and answers** (the recommended option first in each).

| Question | Operator's answer |
| --- | --- |
| Stage 2 begins only once items A–O are settled. Do the mockup's defaults stand as the settlement of A–O (Send report from the head and the Next action step while editing; the 880px composer with Files below the recipients; Subject editable and prefilled; Files rows with the filed estimates listed; every generation document renameable; the viewer over the dialog; the inline form and the greyed read cells removed; the Original report card after Figures headed "Original report", pence and the guide word in brackets, no new breakpoint; a refused send reopens the dialog and the Already sent line sits under the preview card; every To/Cc box after the first To removable)? | "Yes, as drawn (Recommended)" |
| The Subject field's maximum length: the Triage composer's 500, or the mail command's 998? | "500, as the Triage composer (Recommended)" |
| The mockup draws Rename on every Files row, the filed estimates included, but a filed estimate row posts nothing. Should filed estimates be renameable? | "No, generation documents only (Recommended)" |
| Should a renamed file's name be remembered for the next send of the same report, or does each send start from the policy name? | "Each send starts fresh (Recommended)" |

**Recorded** as rulings R659–R666 (provisional, renumbered at combine) in Pegasus
`docs/rulings.md` on `task/v48-send-dialog-original-report` (PR #1903).
