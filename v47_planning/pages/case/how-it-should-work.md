# Case record: Damage impacts and the report's readiness, how it should work

Proposed in the v47 round, 3 November 2026. Letters are the sign-off items in
[v47-notes.md §6](../../notes/v47-notes.md#6-sign-off). Nothing here is settled until the
dated "Decided" heading below is written.

## The rule

- A Case's report needs either a complete impact (a severity and a location) or a deliberate
  **Skip impacts**. The Incident narrative itself stays optional, and a skipped Case prints no
  Nature of Incident.
- Until one of the two is recorded, readiness names **Impacts** (A). It is the Next action
  step and a line in Report not ready, and its Damage control jumps to the impacts block.
- Existing Cases are blocked the same way. There is no backfill (round 1).

## The Damage section

- **With no impact row, while editing:** "No damage recorded.", then Add impact and **Skip
  impacts** on one line, on the facts' left edge (B, round 2).
  - Ticking Skip impacts greys out Add impact; unticking enables it again (round 2).
  - The tick is saved by the section's one Save, like any field.
- **With a row:** the live row grid, unchanged. Skip impacts is not offered, and a partial row
  does not satisfy the rule (B). Clearing the last row offers the tick again, unticked.
- **While reading:** with no row, a static Skip impacts tick under "No damage recorded.",
  ticked or not (C).
- **Incident narrative:** each sentence is its own line, with a line's space between them,
  both read and as the rows are edited (G). The printed report keeps one sentence to a line
  unless G says otherwise.

## Report and automation

- Nothing prints for the skip. Nature of Incident is not offered, and Impact Magnitude reads
  `—` (C).
- `pegasus_assessment_update` writes `assessment.impacts_skipped` like any staff field (D). The
  skip does not by itself make a sent report stale (E), and it is audited as any assessment
  field (F).

## Decided 3 November 2026

The operator approved the round: "Design approved." Items A–G stand as proposed in
[v47-notes.md §6](../../notes/v47-notes.md#6-sign-off). For B's open point, a save that would
leave Skip impacts ticked beside any impact row, the operator chose **"Refuse
(Recommended)"**. The save is refused with "Skip impacts can be ticked only while no impact is
entered.", for staff and automation alike (D). Recorded as R647–R649 in the Pegasus rulings.
