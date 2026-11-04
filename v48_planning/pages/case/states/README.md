# Case record states in this round

| Key | Capture (fact) | Preset | Shows |
| --- | --- | --- | --- |
| `plain-edit` | `v48-plain-edit` (`CaptureV48PlainEdit`) | — | Editing, plain Principal: Send report in the head, no inline form (A, G) |
| `plain-dialog` | `v48-plain-edit` | `dialog=send-report` | The dialog: From, To, Cc, Subject, Message, Files (B, C, D, O) |
| `plain-viewer` | `v48-plain-edit` | `viewer=0` | The report opened in the Case viewer over the dialog (F) |
| `plain-rename` | `v48-plain-edit` | `rename=1` | Renaming the report (E) |
| `plain-read` | `v48-plain-read` (`CaptureV48PlainRead`) | — | Reading: no Send report, no greyed cells (G, H) |
| `rules-dialog` | `v48-rules-edit` (`CaptureV48RulesEdit`) | `dialog=send-report` | Questions, Cc hint, After sending, Holds, an Audatex estimate expected |
| `stop-dialog` | `v48-stop-edit` (`CaptureV48StopEdit`) | `dialog=send-report` | A Stop with Override reason; a filed estimate row; the "{REG} Report" subject |
| `missing-dialog` | `v48-missing-edit` (`CaptureV48MissingEdit`) | `dialog=send-report` | Missing companion: the notice, Cancel only |
| `resend-dialog` | `v48-resend-edit` (`CaptureV48ResendEdit`) | `dialog=send-report` | Already sent; the resend name with its dot (N) |
| `audit-edit` | `v48-audit-edit` (`CaptureV48AuditEdit`) | — | Audit view editing: the Original report card (I–M) |
| `audit-dialog` | `v48-audit-edit` | `dialog=send-report` | The Inspection report and its documents as Files rows |
| `audit-read` | `v48-audit-read` (`CaptureV48AuditRead`) | — | Audit view reading: the card |
| `audit-repairable` | `v48-audit-repairable-read` (`CaptureV48AuditRepairable`) | — | The Inspection was Repairable: no Salvage value row, Glass's |
| `audit-inspection` | `v48-audit-inspection` (`CaptureV48AuditEdit`) | — | The Inspection view: no card |

Every state opens in Today and Proposal (`mode=`). Today of a dialog state is the inline form.
