# Case record: Damage, how it should work

Proposed on 3 November 2026 from the operator's brief and answers. D1–D10 come from the brief and
answers and are settled. The open lines wait for the sign-off list in
[v46-notes §6](../../notes/v46-notes.md#6-sign-off).

## Rules

- **D1.** Impacts are entered by staff, never derived. Each impact is a row: Severity, Location
  and a free-text Note.
- **D2.** There is no Type box (round 2, replacing "Collision/Impact only for now").
- **D3.** Rows are added as needed. There is no fixed number.
- **D4.** A damage marker is a position on the plan, drawn as the burst for the report's picture.
  It records no area, severity or note. Underside, Interior and Mechanical are Location values on
  an impact.
- **D5.** An impact is cleared with an × on its row.
- **D6.** The Incident narrative follows the impacts.
- **D7.** With no impact recorded, the report skips the Nature of Incident block. Impacts are
  optional, so Impact location and Impact severity no longer block the report.
- **D8.** Nature of Incident, and the Incident narrative, are a separate sentence for each
  impact, in row order: "The vehicle has suffered {severity} collision/impact damage to the
  {location}."
- **D9.** While the Damage section edits, a Clear markers button removes every marker. There is
  no Reset, and dragging never removes a marker.
- **D10.** Where several impacts exist, the report's Impact Magnitude and Nature of Incident
  give one impact to a line.

## Open

- Open: the Location list (B).
- Open: the × removes or empties its row (C).
- Open: the captions, "Add impact" and the empty state (D).
- Open: whether the note prints (E).
- Open: existing Cases (F).
- Open: whether an incomplete row counts as an impact (G2).
- Open: the MCP shape (H).
- Open: the removals and superseding R639 (I).
- Open: where the impacts stand (K).
- Open: a new row's defaults (L).

## Where this lands

| Page | Entry |
| --- | --- |
| Case record, Damage section | The impact rows; the markers only |
| Case record, Report wording | Nature of Incident per A |
| Report PDF | Impact Magnitude and Nature of Incident per A; the diagram unchanged |
| MCP | `pegasus_assessment_update` and `pegasus_vocabulary_get` per H |

## Documentation impact when the FRD is written

- FRD-24 Damage record: the short version, the entry rule and the derivation paragraph are
  replaced.
- FRD-11 Report wording blocks: the "Damage to several areas" bullet.
- `docs/rulings.md`: the round 1 answers and the sign-off.
