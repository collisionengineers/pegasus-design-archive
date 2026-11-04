# Case record: Report delivery and the aside, how it should work

Proposed in the v48 round, 4 November 2026. Letters are the sign-off items in
[v48-notes.md §6](../../notes/v48-notes.md#6-sign-off). Nothing here is settled until the
dated "Decided" heading below is written. The operator's three planning answers of
4 November 2026 (D3, D5 and D9's source) are recorded in the discussion log and become
rulings at Stage 2.

## The send

- **D1.** Send report is the Report head's primary while the Case is in its edit session and
  the report is stored; Generate report is the primary until then. The aside's Send report
  step opens the same dialog while editing and jumps to the section while reading (A).
- **D2.** The Send report dialog is a composer in the Triage composer's shape, 880px wide:
  From, To, Cc, Subject, Message, then Files, then the Principal's rule blocks, with Cancel
  and Send report in its foot (B).
- **D3.** Subject is a field, prefilled with the subject the send derives today, and staff may
  change it (C; operator, 4 November 2026).
- **D4.** Files lists one row per attachment: its include tick as today's Attach rules (the
  report and a required companion static and on, the fee note on, the rest off, the other
  work's report off, filed estimates listed and on), its name, its kind and size, and
  Rename (D).
- **D5.** A file's name opens it in the Case viewer over the dialog; Escape closes the viewer
  first, then the dialog (F). The dialog's inert does not reach the viewer's host, and the
  viewer keeps its z-index when focused.
- **D6.** Every attachment can be renamed: the stem is edited, `.pdf` stays, Reset restores
  the policy name; a renamed file is sent under its new name (E).
- **D7.** Every To or Cc box after the first To carries its × and can be removed; Add To
  recipient and Add Cc recipient add a removable box (O; operator, 4 November 2026).
- **D8.** The rule blocks keep their words and their rule: Already sent, Stop with its Override
  reason, missing companion (Send withheld, Cancel only), Questions, Cc hint, After sending,
  Holds with Done (D).
- **D9.** The Report section keeps its preview card; the inline form and the greyed read cells
  go, so read and edit share one geometry. A report already sent says so under the preview
  card (G, N).
- **D10.** Send report opens only while editing, as today (H; operator, 4 November 2026).
- **D11.** After Send the page swaps and the dialog closes; a refused send reopens the dialog
  with its notice (N).

## The aside

- **D12.** On an Inspection + Audit Case, in the Audit view only, an **Original report** card
  follows Figures (I, J).
- **D13.** It reads the Inspection report as generated (the newest Inspection generation's
  snapshot), and draws "—" until one exists (K; operator, 4 November 2026).
- **D14.** Its rows: Repair cost inc VAT; Salvage value only when that report's outcome is
  Total loss; Engineer's Value with the basis guide's word in brackets as the Valuation label
  draws it, none for a typed value; money as the aside draws it (L).
- **D15.** Below 1441px the card is one more cell of the two-up strip; no new breakpoint (M).

## Decided, 4 November 2026

The operator settled A–O as drawn ("Yes, as drawn") and the three open points: the
Subject is bounded at 500 as the Triage composer's is; filed estimates are not renameable
(Rename on the generation's own documents only, a filed estimate row has no Rename); a
rename holds for that send only, the next send starting from the policy name again. The
heading stays "Original report". Rulings R659–R666 (provisional) in Pegasus
`docs/rulings.md`; implemented on `task/v48-send-dialog-original-report` (PR #1903).

## Where this lands

| Page | Entry |
| --- | --- |
| Case record, Report section head | Send report (primary, editing, report stored) |
| Case record, aside Next action | Send report step opens the dialog while editing |
| Case record, `[data-case-dialogs]` | The Send report dialog |
| Case record, aside | The Original report card after Figures, Audit view |

## Documentation impact when the FRD is written

- FRD-11: "What a delivery is called" (staff names on every attachment, Reset to the policy
  name), "From and subject" (Subject editable, prefilled), "Report sending rules" (the form is
  a dialog; the blocks unchanged).
- FRD-16: "Report" (the head's Send report, the preview card, no inline form, no greyed read
  cells; the delivery paragraph that "awaits its design sign-off" retired), "Case workspace"
  (the aside order with Original report), "Inspection and Audit views" (the card).
- FRD-21: "Outbound correspondence" (where the send controls are: the dialog; what the
  composer carries: Subject, removable recipients, named files).
- Design authority: the Case record frame (the aside order, the `dialog--send` composer,
  the viewer over a dialog); the component catalogue.
- Rulings: the three planning answers, the removable boxes, and the sign-off.
