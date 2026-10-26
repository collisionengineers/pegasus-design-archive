# Inbox — states

Today is the page captured from the application; it is not redrawn. The Proposal is the same page with the changes below.

| State | Page | Changes |
| --- | --- | --- |
| `inbox` | Inbox · All incoming | A, B, I |
| `inbox-no-case-found` | Inbox · No Case Found | A, I |
| `inbox-rows-ticked` | Inbox · two rows ticked | A, B, I |
| `message-m1` | Message · New instruction, no Case | G, H |
| `message-m2` | Message · Case update on a Report sent Case | A, C, G, H, N |
| `message-m4` | Message · Query on a Report sent Case | A, G, H, K |
| `message-m4-ai-reply` | Message · Query, composer on the AI draft | A, G, H, K, L |
| `message-m3` | Message · photographs, no Case | A, G, H, R |
| `message-m7` | Message · Billing, no Case | A, G, H |
| `message-m11` | Message · Cancellation on a Case in Report preparation | E, G, H |
| `message-m12` | Message · thank-you on a Report sent Case | A, C, G, H, N |

## Changes

- **A**: Row category text only for New instruction, Triage request and Cancellation.
- **B**: Unlinked e-mail that is not an instruction or triage request waits only in No Case Found.
- **C**: Joining a Report sent Case opens no query by itself; criteria and the AI classifier may.
- **E**: The Cancellation type stays, with its Case aside row and notification.
- **G**: Decision order: Case, Type, Query, Change case.
- **H**: Row label Type; default chip Correspondence replaces Unclassified.
- **I**: Category filter and bulk Correct classification (with its dialog) removed; bulk Dismiss and Restore stay.
- **K**: Query row: open query, Unassigned, Mark done marks this query done.
- **L**: Composer tick Mark query done: marks only the replied e-mail's query done once the Sent item is observed.
- **N**: Query row: Open query on an e-mail on a Report sent Case that holds no query.
- **R**: Register images on any image-only unlinked e-mail with no instruction, triage or cancellation type.
