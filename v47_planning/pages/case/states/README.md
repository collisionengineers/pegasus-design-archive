# Damage: states

| State key | What it shows | Capture (Today → Proposal) | Shots |
| --- | --- | --- | --- |
| `none-read` | Read, no impact. Today it is ready to send. The Proposal names Impacts and shows the static tick, off (A, C) | `v47-none-read` → `v47-rule-none-read` | 001, 002 |
| `none-edit` | Editing, no impact: Add impact and Skip impacts on one line (A, B) | `v47-none-edit` → `v47-rule-none-edit` | 003, 004 |
| `skipped-read` | Read, saved with Skip impacts ticked: no Impacts item (C) | `v47-none-read` | 005, 006 |
| `skipped-edit` | Editing, Skip impacts ticked: Add impact greyed out (B) | `v47-none-edit` | 007, 008 |
| `partial-read` | Read, one row with a severity and no location: Impacts still outstanding (B) | `v47-partial-read` → `v47-rule-partial-read` | 009, 010 |
| `partial-edit` | Editing the same: Skip impacts not offered beside a row (B) | `v47-partial-edit` → `v47-rule-partial-edit` | 011, 012 |
| `two-read` | Read, two impacts: a line's space between the narrative's sentences (G) | `v47-two-read` | 013, 014 |
| `two-edit` | Editing two impacts: no Skip impacts; the narrative recomposes spaced (B, G) | `v47-two-edit` | 015, 016 |

Odd shot numbers are Today and even are Proposal. A `v47-rule-*` capture is the same Case
rendered by the application with the scratch readiness item A switched on.
