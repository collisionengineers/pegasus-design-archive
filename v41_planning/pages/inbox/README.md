# Inbox

Today is the page captured from the application; it is not redrawn. The Proposal is the same page with the changes below.

| State | Page | Changes |
| --- | --- | --- |
| `inbox` | Inbox | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `inbox-no-case-found` | Inbox · No Case Found | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `inbox-sent` | Inbox · Sent Items | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `inbox-dismissed` | Inbox · Dismissed | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `inbox-deleted` | Inbox · Deleted Items | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `inbox-rows-ticked` | Inbox · rows ticked | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `inbox-rows-ticked-classify` | Inbox · Correct classification for the ticked rows | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `inbox-rows-ticked-busy` | Inbox · bulk Dismiss pressed | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `inbox-dismissed-rows-ticked` | Inbox · Dismissed, bulk Restore | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `mail-message` | Message · Case update, linked | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `mail-message-new-instruction` | Message · New instruction | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `mail-message-no-case` | Message · No Case Found | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `mail-message-reply` | Message · Reply | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `mail-message-query` | Message · Query, Draft reply with AI | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `mail-message-query-queued` | Message · Query, AI draft queued | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `mail-message-query-ready` | Message · Query, Reply with AI draft | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `mail-message-query-ai-reply` | Message · Query, composer on the AI draft | I1, I2, I4, I6, I9, I10, I11, I12, I13, I15, I16, I17, I18, S1, S3, S4 |
| `case-correspondence` | Case · Correspondence and Queries | K1, S1, S3, S4 |

## Changes

- **I1**: Scopes: All incoming, No Case Found, Sent Items, Dismissed and Deleted Items all sit on the rail. The Folder select goes, the filter's columns take its width, and Category holds the eleven categories only.
- **I2**: The message opens as a dialog over the Inbox, not the /Inbox/{id} page (brief, 13 Oct). /Inbox/{id} stays for a new tab and with no script (R159).
- **I4**: The quick preview goes, because the dialog is the reader. The list takes the width the preview had.
- **I6**: Previous and Next message buttons sit in the dialog head beside Close, so the list can be read without closing the dialog.
- **I9**: The Case tab folds into Decision, the dialog's right column. Classification is the eleven categories as chips, one pressed, applied at once as an image tag is. The Case is its link, with the Case / PO picker under it, then Decided once; Change linked Case and Unlink (or Link to Case) are one row of small buttons under the picker. The tabs are Message, Attachments and Thread. Question for the operator: a chip applies at once, but Correct classification needs a Reason for correction (and a Case type for New instruction), and no field for them is drawn. Where are they entered? Tag as query is the one existing one-click correction, and it records a fixed reason.
- **I10**: Dismiss in the dialog moves on to the next message.
- **I11**: The Classified chip goes from the head. Classification is shown once, in Decision.
- **I12**: Decision shows Decided as plain text with its actor (no provenance icon) and the linked Case once (no Destination and Filed to).
- **I13**: Link, Change linked Case and Unlink open their reason dialog in one step. There is no prepare round trip.
- **I15**: Reply, Reply all and Forward compose inside the dialog: the tabs step aside, From, To and Case sit on one line, and the foot is Cancel and Send. On a query the composer carries PR 1331's AI draft: the AI line, the prefilled Message and Also resolve query.
- **I16**: A query's record bar names its classification, Query, instead of Post-report, which the glossary avoids. Draft reply with AI, AI draft · Queued and Reply with AI draft (PR 1331) stay as they are.
- **I17**: The dialog has one head (subject; From, To and received beneath; Previous/Next and close at the right), the tabs, then the message beside Decision. The foot carries Dismiss apart on the left, and Reply, Reply all and Forward as plain buttons. The classification's next action (Create case, Register images, PR 1331's Draft reply with AI or Reply with AI draft) is the one dark button, at the far right, in place of the record bar.
- **I18**: Bulk actions on the list (R36, R140). In All incoming, No Case Found and Dismissed each row carries a checkbox in its left gutter; ticking it neither opens nor pins the row. One bulk form sits above the list, outside the rows: the ticked count and, in the incoming scopes, Dismiss and Correct classification, or, in Dismissed, Restore. Sent Items and Deleted Items have none. Correct classification opens the existing dialog once, so Classification, Case type and Reason for correction are entered once for every ticked row (R140 c); each row keeps its own Reply, Dismiss and Restore. The bulk buttons are always enabled, because a post with nothing ticked writes nothing (finding-mail-bulk-actions criterion 5) and a disabled button cannot be enabled without script (criterion 11). The pressed bulk control says its existing busy word (Dismissing…, Restoring…, and Saving… on the dialog's Save correction) with the loader glyph, as the single-message controls do; inbox-rows-ticked-busy draws bulk Dismiss pressed. Questions for the operator (R140 b): the words for the bulk controls (drawn with the single-message labels Dismiss, Restore and Correct classification), the count (drawn as a bare number), the failure line for a message that is not changed (not drawn), the checkbox's accessible name (drawn as the message's subject), and where the no-script path enters the classify inputs.
- **K1**: The Tasks icon points at a symbol the sprite does not have, so it draws nothing. It now uses the symbol the sprite has, #icon-square-check.
- **S1**: Release notes, Report a problem and Change password move into the Account dialog body; the foot keeps Close and Sign out.
- **S3**: The command palette's Cases icon matches the rail's Cases icon.
- **S4**: The utility bar's freshness line goes; the rail health line keeps the one clock.
