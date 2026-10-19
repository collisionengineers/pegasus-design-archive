# Case

Today is the page captured from the application; it is not redrawn. The Proposal is the same page with the changes below.

| State | Page | Changes |
| --- | --- | --- |
| `case-read` | Case · With Engineer | K1, S1, S3, S4 |
| `case-edit` | Case · editing | K1, S1, S3, S4 |
| `case-not-ready` | Case · report not ready | K1, S1, S3, S4 |
| `case-delivery-rules` | Case · Report, rules to answer | K1, K2, S1, S3, S4 |
| `case-delivery-plain` | Case · Report, ready to send | K1, S1, S3, S4 |
| `case-delivery-stop` | Case · Report, a rule stops sending | K1, S1, S3, S4 |
| `case-delivery-missing` | Case · Report, missing attachment | K1, S1, S3, S4 |
| `case-report-sent` | Case · Report sent, open query | K1, K5, S1, S3, S4 |
| `case-audit` | Case · Inspection and Audit | K1, S1, S3, S4 |
| `case-tasks` | Case · Tasks dialog | K1, K3, K4, S1, S3, S4 |
| `case-with-engineer-unassigned` | Case · With Engineer, no Engineer | K1, K9, S1, S3, S4 |
| `case-closed` | Case · Closed, Return to work | K1, K10, S1, S3, S4 |

## Changes

- **K1**: The Tasks icon points at a symbol the sprite does not have, so it draws nothing. It now uses the symbol the sprite has, #icon-square-check.
- **K2**: The Yes and No answers on a rule question show their labels. The radios were stretched to the full width of the form and pushed the labels out of sight.
- **K3**: Each open task in Next action opens the Tasks dialog itself, so the repeated Tasks button on every row goes.
- **K4**: The add-task box takes the field style the other Case inputs use.
- **K5**: Reading a Case whose report was sent, To shows the recipient of the report that was sent instead of Not recorded; Cc keeps Not recorded, because the send history is one joined list and names no Cc. The capture seeds that history with claims@northline.example, the sender of the instruction e-mail that the Sent item replies to, and read mode prints it nowhere today, so the address is read from the Case's own correspondence.
- **K9**: A With Engineer Case that has no Engineer reads Unassigned on the ribbon and in the Overview (the Overview's only Engineer fact is Sign-off Engineer, which is the fact drawn). Next action opens with Assign Engineer and Take beside it, the Actions menu lists Assign Engineer, and the Assign Engineer dialog lists the signed-in person first as Name (you), then the other Engineers, then Unassigned, with no Reason box.
- **K10**: A closed Case offers Return to work in the Actions menu. Its dialog posts the Closure page's Reopen handler with the stage to return to and a reason; the stage options read the existing stage names. Question: the stage field's label is given by no ruling and no live label, so it reads Case stage, the word W2 gives the Search State filter.
- **S1**: Release notes, Report a problem and Change password move into the Account dialog body; the foot keeps Close and Sign out.
- **S3**: The command palette's Cases icon matches the rail's Cases icon.
- **S4**: The utility bar's freshness line goes; the rail health line keeps the one clock.
