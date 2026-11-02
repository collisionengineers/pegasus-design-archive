# Case details: states

| State key | What it shows | Capture | Shots |
| --- | --- | --- | --- |
| `case-read` | Read mode. Claim source recorded; the Principal's and Claim source's record notes; this Case's notes; Notes from client | `case-read` | 001, 002 |
| `case-edit` | The same Case in the edit session | `case-edit` | 003, 004 |
| `case-read-bare` | Read mode. No Claim source, no record notes, no Case notes | `case-read-bare` | 005, 006 |
| `case-edit-bare` | The same in the edit session (the hidden record-notes slot) | `case-edit-bare` | 007, 008 |
| `case-edit-claim-source-changed` | Editing a bare Case with `Car 2 Go` chosen: contact and record notes follow the select | `case-edit-bare` + preset | 009, 010 |
| `case-read-f-half` | Item F variant: Accident circumstances keeps its half-width cell | `case-read` | 011, 012 |
| `case-read-bare-g-span` | Item G variant: this Case's Principal notes span the panel | `case-read-bare` | 013, 014 |
