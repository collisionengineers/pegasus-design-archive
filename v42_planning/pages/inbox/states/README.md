# Inbox — states

Today is the page captured from the application; it is not redrawn. The Proposal is the same page with the changes below.

| State | Page | Changes |
| --- | --- | --- |
| `inbox` | Inbox · All incoming | A, B, I |
| `inbox-no-case-found` | Inbox · No Case Found | A, B, I |
| `inbox-rows-ticked` | Inbox · two rows ticked | A, B, I |
| `message-m1` | Message dialog · New instruction, no Case (settings open) | A, B, G, H, I |
| `message-m2` | Message dialog · Case update on a Report sent Case (settings open) | A, B, C, G, H, I, N |
| `message-m4` | Message dialog · Query on a Report sent Case (settings open) | A, B, G, H, I, K |
| `message-m4-ai-reply` | Message dialog · Query, composer on the AI draft | A, B, I, L |
| `message-m3` | Message dialog · photographs, no Case | A, B, G, H, I, R |
| `message-m7` | Message dialog · Billing, no Case (settings open) | A, B, G, H, I |
| `message-m11` | Message dialog · Cancellation on a Case in Report preparation (settings open) | A, B, E, G, H, I |
| `message-m12` | Message dialog · thank-you on a Report sent Case (settings open) | A, B, C, G, H, I, N |

## Changes

- **A**: Row category text only for New instruction, Triage request and Cancellation.
- **B**: Unlinked e-mail that is not an instruction or triage request waits only in No Case Found.
- **C**: Joining a Report sent Case opens no query by itself; criteria and the AI classifier may.
- **E**: The Cancellation type stays, with its Case aside row and notification.
- **G**: Decision sidebar replaced by the cog settings menu (#icon-settings) in the dialog header, ordered Case, Type, Query, Change case, with an at-a-glance context bar above the full-width message.
- **H**: Row label Type; default chip Correspondence replaces Unclassified.
- **I**: Category filter and bulk Correct classification (with its dialog) removed; bulk Dismiss and Restore stay.
- **K**: Query row in Message settings: open query, Unassigned, Mark done marks this query done.
- **L**: Composer tick Mark query done: marks only the replied e-mail's query done once the Sent item is observed.
- **N**: Query row in Message settings: Open query on an e-mail on a Report sent Case that holds no query.
- **R**: Register images on any image-only unlinked e-mail with no instruction, triage or cancellation type.
