# Send report dialog

## The action

Send report, from the Report section head (editing, report stored) or the aside's Next action
step. It posts the live `SendReport` handler's form: the dialog holds the one
`form[data-send-report]` with every hidden field (operation key, lease token, versions,
generation, view, dispatch fingerprint).

## The dialog

`div.dialog-backdrop[data-dialog="case-send-report-dialog"]` in `[data-case-dialogs]`, so
`site.js` binds it like every Case dialog. `section.dialog.mail-compose-dialog.dialog--send`
(the Triage composer's grid: fields scroll, the foot is pinned), 880px wide, 760px tall at
most. Head: eyebrow "Report · {Case/PO}", "Send report", ×.

| Block | What it is | Live node |
| --- | --- | --- |
| Already sent | "Already sent on … to …" | `[data-report-already-sent]` |
| Stop | the warning notice and "Override reason" | `[data-report-stop]`, `#report-stop-override` |
| Missing companion | the notice; Send withheld, Cancel only | `[data-report-missing-companion]` |
| Reviewed recipients | From (select, starts on the default, R655); To and Cc stacks, each box with its × (O), Add To recipient, Add Cc recipient; the address book datalist; the Cc hint | `[data-report-from]`, `#report-recipient-to`, `#report-recipient-cc`, `[data-add-report-recipient]`, `#report-address-book`, `[data-report-cc-hint]` |
| Subject | `input[name=subject]`, prefilled with the derived subject (C) | new |
| Message | the textarea, 5000 | `#report-message` |
| Files | one row per attachment (D, E), see below | from `[data-report-attach]`, `[data-report-attach-other]`, `[data-report-filed-estimates]`, `[data-report-file-name]` |
| Answer before sending | the Yes/No questions | `[data-report-question]` |
| Warnings | "No recognised estimate…", "…fee note as a separate document…" | `[data-report-warning]` |
| After sending | the tasks a rule adds | `[data-report-after-sending]` |
| Holds | each hold with Done | `[data-report-hold-row]` |
| Foot | Cancel; Send report (busy "Sending…") | the live submit |

### A Files row

`div.v48-file[data-v48-file=<kind>][data-v48-default=<policy name>]`: the live include tick
(a static tick + hidden `attach` for the report and a required companion; the live checkbox
for Fee note, Repair Spec, Images, `secondGenerationId` and `secondAttach`; a static tick for
a filed estimate, posting nothing), the file glyph, the name as a button (`[data-v48-file-open]`,
opens the viewer), "{kind} · {size}", Rename (`[data-v48-rename]`, pencil). Renaming shows an
input of the stem, ".pdf" and Reset; Enter or leaving keeps it, Escape cancels. A hidden
`fileName-<kind>` (`secondFileName-<kind>` for the other work) posts a changed name, empty
when it is the policy name.

Kinds, in order: Report, Fee note, Repair Spec, Images (the generation's confirmed
artifacts), Filed estimate(s), then on an Inspection + Audit Case "Inspection · Report",
"Inspection · Fee note", "Inspection · Repair Spec", "Inspection · Images" (or "Audit · …" in
the Inspection view). Sizes are synthetic (there are no files behind a mockup).

## What Send posts

The live fields (`operationKey`, `editLeaseToken`, `expectedCaseVersion`, `generationId`,
`expectedGenerationVersion`, `view`, `dispatchFingerprint`, `fromMailboxId`, `toRecipients`,
`ccRecipients`, `attach`, `secondGenerationId`, `secondExpectedGenerationVersion`,
`secondAttach`, `decision-*`, `holdsDone`, `stopOverrideReason`, `coveringMessage`) plus
`subject` and the `fileName-*` / `secondFileName-*` names. In the mockup the post goes to the
strip (`window.__mock.lastPost`); nothing is sent.

## Presets and shots

`?state=plain-dialog`, `rules-dialog`, `stop-dialog`, `missing-dialog`, `resend-dialog`,
`audit-dialog` (`dialog=send-report`), `plain-viewer` (`viewer=0`), `plain-rename`
(`rename=1`); variables `opt=width:1100`, `opt=files:beside`. Shots: see
[../../../../notes/v48-notes.md §1](../../../../notes/v48-notes.md#1-what-changes).
