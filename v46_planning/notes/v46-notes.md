# v46 notes: impacts entered by hand, damage markers for the picture only

The round opened on 3 November 2026. The live source was read from Pegasus `origin/dev`
`fb4c5e741` (`captured-live/_source/source.txt`), which includes PR 1862 (R639). The brief, the
questions and the operator's answers are in [discussion-log.md](discussion-log.md).

## 1. What changes

| # | Today (problem) | Proposal | Shots |
| --- | --- | --- | --- |
| 1 | Impact location and severity are derived from the markers: touching bursts are grouped, and separate groups read Multiple. Two bursts on the RH Rear and the Rear already read Multiple | Staff type each impact as a row: Impact · Severity · Location · Note · ×. Rows are added with Add impact. Nothing is derived | 001–004, 005–008 |
| 2 | Each marker carries its areas, a severity and a note, listed under the derived cells with a × | A marker is a burst on the plan and nothing else; the list goes | 003/004, 007/008 |
| 3 | Underside, Interior and Mechanical are chips under the plan, each one recorded damage | They are Location values on an impact row; the chips go | 007/008 |
| 4 | Removing a marker uses the × on its list row | Clear markers beside Reset removes every marker (J, round 3). A marker dragged and let go outside the plan is also removed (J2) | 007/008 |
| 5 | Nature of Incident reads "…damage to the following areas:" and one area per line whenever several areas are recorded; the Damage section's Incident narrative echoes it | A separate sentence for each impact, one to a line, in row order (A, round 3). The Incident narrative and the Nature of Incident block recompose as rows are added, changed or cleared | 015/016, 005–008 |
| 6 | With nothing recorded, the derived cells read Not recorded and the list reads No damage recorded. Report not ready lists Impact location and Impact severity, and Report wording shows its settings alone | No damage recorded. and Add impact while editing. Impacts are optional: the report is not blocked, and Nature of Incident is skipped, with no block and no tick (G, ruled) | 011–014, 017/018 |
| 7 | (variant) | The impacts run the full width under the plan (item K) | 009/010 |

Shot numbers are the `NNN-` prefixes in [../shots](../shots): odd is Today, even is Proposal. Each
comes at 1580, 1440 and 760, with a `-panel` crop and a 1580 `-full` page.

## 2. Live rules the mockup mirrors

| Rule | Source |
| --- | --- |
| The plan, the yellow burst, press-to-draw, drag-to-size, drag-to-move and Reset are unchanged | `_CaseDamage.cshtml`, `case-workspace.js` damage editor, `DamagePlanGeometry`, `DamageBurst` |
| A disc's centre is clamped to the plan box, so live can never drag a burst off the vehicle | `bound()` in `case-workspace.js` |
| Severity words and order | `AssessmentVocabulary.DamageSeverities` |
| Location words and order | `AssessmentVocabulary.DamageAreas` (the 11 areas; no "Multiple") |
| "Severity", "Note", "No damage recorded." | `CaseWorkspaceLabels.Damage` |
| Read shows values and edit shows controls in the same cells | `.fc .fv` / `.fc .fi` in `site.css` |
| The report's sentence pattern "The vehicle has suffered {severity} collision/impact damage to the {location}." in small letters; "collision/impact" stays fixed wording, as live has it, now that there is no Type | `ReportWording.NatureOfIncidentSentence`, FRD-11 |
| The report's Impact Magnitude "{Severity} — {Location}" | `AssessmentReportWording.ImpactMagnitude` |

## 3. Frame numbers

- The live workbench grid is unchanged: plan 220–300 px and facts `1fr`, stacking below 900 px.
- Impact row at 1100 px and above: `52px | minmax(148px,1fr) | minmax(110px,.9fr) |
  minmax(0,2fr) | 28px`, with a 6 px gap and 36 px controls.
- Below 1100 px a row folds into a bordered two-column card. Each cell carries its caption, the
  Note spans the card, and the × sits on the Impact line.
- The × (Clear) keeps its 28 px column in read mode (`visibility:hidden`), so entering edit moves
  nothing.
- At 1580 the Note column is about 280 px wide beside the plan and about 420 px under it
  (item K).

## 4. Decisions and authority

| Decision | Authority |
| --- | --- |
| The fourth box is a free-text note | Operator, 3 November 2026 |
| No Type box (round 2: "we dont need the "type" box"), replacing round 1's "Collision/Impact only for now" | Operator, 3 November 2026 |
| Rows are added as needed | Operator, 3 November 2026 |
| A marker keeps its position only; Underside, Interior and Mechanical become Location values | Operator, 3 November 2026 |
| Clear is an × | Operator, 3 November 2026 (round 2) |
| The Incident narrative follows the impacts | Operator, 3 November 2026 (round 2) |
| With no impact recorded, Nature of Incident is skipped on the report, so impacts are optional | Operator, 3 November 2026 (round 2); settles G |
| A separate sentence for each impact | Operator, 3 November 2026 (round 3); settles A's composition |
| A Clear markers button | Operator, 3 November 2026 (round 3); settles J |
| Labels are live strings or the operator's example | Design authority; repository rule that operator-facing copy is never invented (new words are item D) |

## 5. Coverage audit and departures from live

Every control and fact in the live Damage section, from `v46-apart-edit.html`:

| Live item | Proposal |
| --- | --- |
| Panel head (title, Edit, collapse) | Kept |
| Plan SVG, FRONT/REAR captions, artwork, hit paths | Kept |
| Plan-area keyboard controls (`data-damage-plan-area`, edit only) | **Removed**: they record a damage by area, which a marker no longer names |
| Bursts (`data-mark`) | Kept; removing one is item J |
| Area readout under the pointer | **Removed** (I) |
| Underside / Interior / Mechanical chips | **Removed** (I), now Location values (B) |
| Reset | Kept; it resets the markers only. Clear markers stands beside it while editing (J) |
| Impact location and Impact severity cells | **Removed** (I) |
| Marker list: number, areas, severity, note, × | **Removed** (I) |
| Unrelated damage | Kept |
| Incident narrative | Kept; it reads the item A composition, follows the rows as they change, and reads Not recorded with no impact |
| Hidden `damageImpacts` input | Kept for the markers (Stage 2 reshapes it) |

Departures with no item of their own:

- The Report wording's Nature of Incident block (outside the section) follows item A, and is
  skipped with no impact (G).
- For the no-impact states the Proposal takes the Report section and Next action from the same
  fixture's capture with damage recorded (`v46-apart-*`). It removes Nature of Incident and drops
  the aside's Report not ready card, whose only blockers were Impact location and Impact
  severity. Live cannot draw that page today because it refuses to project the report.
- The van and motorbike plans are not captured separately. The plan drawings are unchanged by
  this round.

## 6. Sign-off

Each item reads "Confirm, or …". Nothing here is built until every item is settled.

- **A. How the impacts reach the report.** *Round 3, 3 November 2026: the proposed single
  sentence naming every impact was rejected ("No, there should be a seperate sentence for each
  impact"), and so was the first-impact-only variant.* The Nature of Incident block and the
  Damage section's Incident narrative (round 2: "The incident narrative also needs to adjust")
  are a separate sentence for each impact, one to a line, in row order: "The vehicle has suffered
  light collision/impact damage to the front." / "The vehicle has suffered moderate
  collision/impact damage to the right side." / … This replaces FRD-11's "Damage to several
  areas" list. Open (A2): the report's Impact Magnitude prints the first impact ("Light —
  Front"). Confirm, or say what it prints when there are several. Also confirm one sentence to a
  line, or say if they should run on as one paragraph.
- **B. Location list.** The 11 recorded areas (Front, LH Front, RH Front, LH Side, RH Side, Rear,
  LH Rear, RH Rear, Underside, Interior, Mechanical), with no Multiple. Confirm, or use the
  reference spec's list, which adds Roof, Wheel(s) and Multiple.
- **C. Clear.** The × (round 2: "could do an X for clear instead") removes its row, because rows
  are added as needed. Confirm, or the × empties the row and leaves it in place.
- **D. Words.** The row label "Impact" comes from your example, and "Clear" is the ×'s spoken
  label and tooltip. "Severity", "Note" and "No damage recorded." are live strings. "Location"
  (a column caption) and "Add impact" are new. Confirm, or give the words.
- **E. The note on the report.** The note is for the record and does not print, because the report
  prints no damage table (operator, 27 September 2026). Confirm, or say where it prints.
- **F. Existing Cases.** Existing Cases start with no impacts, and the Engineer enters them. The
  stored derived location and severity are dropped. Markers keep their disc. A damage recorded by
  area alone becomes the disc its areas give, and an Underside, Interior or Mechanical damage
  (which has no disc) is dropped. Confirm, or copy each Case's stored location and severity into
  one row where it is not Multiple.
- **G. Report readiness.** *Settled 3 November 2026 (round 2): "if no impact area is chosen, the
  nature of incident block would be skipped on report".* Impacts are optional. Impact location
  and Impact severity stop being report blockers, and with no complete impact Nature of Incident
  has no block and no tick. Open (G2): whether a row with no Severity or no Location counts as an
  impact. The mockup leaves an incomplete row out of the sentence. Confirm, or say how an
  incomplete row is treated.
- **H. MCP.** No new tool. The impacts are one staff-edited field (a JSON array of severity,
  location and note) that `pegasus_assessment_update` writes and `pegasus_vocabulary_get`
  describes. The markers stay in `damage.impacts` as positions only. Confirm, or ask for
  dedicated add/remove impact tools.
- **I. Removed.** The derived Impact location and Impact severity, the marker's areas, severity and
  note, the per-marker list, the Underside/Interior/Mechanical chips, the area readout and the
  plan-area keyboard controls. This supersedes R639 and FRD-24's Damage record clause. Confirm,
  or keep any of them.
- **J. Removing a marker.** *Round 3, 3 November 2026: "Include a clear markers button".* While
  the section edits, a **Clear markers** button beside Reset removes every marker, leaving the
  impacts untouched. Reset still returns the markers held when the edit opened. Open (J2):
  dragging a marker and letting go outside the plan also removes that one marker. Confirm keeping
  it, or drop it so Clear markers is the only way to remove a marker.
- **K. Where the impacts stand.** Beside the plan, where the derived cells and list stood. Confirm,
  or put them under the plan at full width (state `damage-apart-edit-under`).
- **L. A new row.** Severity and Location start blank. Confirm, or give the defaults.

## 7. Self-check

`python -X utf8 build/check-v46.py`, 3 November 2026 (round 3): `RESULT {"fail": [], "okCount": 256}`.
It covers every state in Today and Proposal with no page or console error, the Diff marks, Today
reading live (Multiple, the list, the chips), the row counts, the vocabularies, read/edit
visibility and geometry, Add/fill/× with the narrative and Nature of Incident following, G's
skipped block, tick and blockers, J (drag-off in Today and Proposal, Clear markers and Reset),
A's sentence for each impact, K and its variant, the 760 fold, and the 1580 single line. Shots and their record are in
`shots/verification.json`.

## 8. Known limits

- Fonts fall back to the system's when the live web font is missing; images are the capture's
  placeholders.
- Add, × and fills change only the page; there is no save behind the mockup.
- The report PDF is not drawn: its Impact Magnitude is stated in item A, and its marked diagram is
  unchanged.
- The van and motorbike plans are not drawn separately (unchanged by this round).
- Item J is shown by changing the live script in Proposal only (`JS_CORRECTIONS` in
  `build-v46.py`, each matched once).
