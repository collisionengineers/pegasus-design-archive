# Damage: states

| State key | What it shows | Capture | Shots |
| --- | --- | --- | --- |
| `damage-two-read` | Read mode, two damages (RH Rear moderate, Rear light) | `v46-two-read` | 001, 002 |
| `damage-two-edit` | The same Case in the edit session | `v46-two-edit` | 003, 004 |
| `damage-apart-read` | Read mode, three damages drawn apart (Front, RH Side, Rear) | `v46-apart-read` | 005, 006 |
| `damage-apart-edit` | The same in the edit session | `v46-apart-edit` | 007, 008 |
| `damage-apart-edit-under` | Item K variant: the impacts under the plan at full width | `v46-apart-edit` | 009, 010 |
| `damage-none-read` | Read mode, nothing recorded; the report is not blocked (G) | `v46-none-read` (+ `v46-apart-read` report) | 011, 012 |
| `damage-none-edit` | The edit session, nothing recorded: Add impact | `v46-none-edit` (+ `v46-apart-edit` report) | 013, 014 |
| `wording-apart` | Report wording: Nature of Incident, a sentence for each impact (A) | `v46-apart-edit` | 015, 016 |
| `wording-none` | G (ruled): no impact recorded. Today the report is blocked; the Proposal skips Nature of Incident | `v46-none-edit` (+ `v46-apart-edit` report) | 017, 018 |

Odd shot numbers are Today and even are Proposal.
