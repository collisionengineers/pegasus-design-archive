# Case details: how it should work

Decided with the operator on 2 November 2026 (brief and answers in the
[discussion log](../../notes/discussion-log.md)). Open lines await sign-off.

- **D1** The card holding the Claim source and its contact is headed **Claim source**. (A)
- **D2** The Claim source card shows, under its contact cells, the Claim source record's
  notes on every Case (read-only, absent when the record has none) and then this Case's
  Claim source notes. While editing, the record's notes follow the Claim source select
  before Save. The card lays its cells two across, like the Case card (feedback,
  2 November 2026). (B)
- **D3** The Principal's notes on every Case (read-only, absent when the record has none)
  and this Case's Principal notes form their own full-width sub-panel headed
  **Principal**, below the Case and Claim source cards. (C)
- **D4** A Case has no Case contact. Nothing fills one: not the instruction e-mail's sender
  or signature, and not the Principal API, whose instruction has no `fileHandler`. Stored
  values are deleted. This supersedes R462. (D)
- **D5** A Case has no Notes from client. Stored values are deleted. (E)
- Open: **F** — Accident circumstances spans the accident band's full width, or keeps its
  half-width cell.
- Open: **G** — With no Principal record notes, this Case's Principal notes cell keeps its
  half-width place, or spans the panel.
- Open: **H** — The DFD form's *Contact details if not client* review line stays, or goes
  with the Case contact.

## Where this lands

| Page or owner | Entry |
| --- | --- |
| Case record, Case details | D1–D5, F, G |
| Triage Case | Unchanged: its read-only Principal notes cell stays |
| Principal API | D4: no `fileHandler` |
| MCP Case edit | D4, D5: no contact or Notes from client parameters |
| Instruction review (DFD) | H |

## Documentation impact when the FRD is written

- FRD-16 §Case details: D1–D5 (and F, G once settled), dated 2 November 2026, citing the
  new rulings.
- FRD-23 instruction field table: the *Contact name, e-mail and phone* row is removed.
- `docs/rulings.md`: new rows for the brief and answers; R462 marked superseded.
- `docs/engineering/principal-api.openapi.yaml`: `fileHandler` removed.
- `docs/current-architecture.md`: the `SenderContactFill` row is removed.
