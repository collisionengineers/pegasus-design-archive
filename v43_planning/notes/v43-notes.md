# v43 notes: Case details

Round opened 2 November 2026 at the operator's request. Captured from `origin/dev`
`826c2aed70555ac68fd4d2ce0bde032901db206d` with the excluded `ZzMockupCaptureCase` scratch
lane ([capture log](capture-run-2026-11-02.log)).

## 1. What changes, and why

| Today (live) | Proposal | Item | Shots |
| --- | --- | --- | --- |
| The card holding the Claim source select and its three contact cells is headed **Principal**. | Headed **Claim source**. | A | 001→002, 003→004 |
| Claim source notes (the record's, read-only, and this Case's) sit in the Notes band beside the Principal's. | Both sit in the Claim source card, under its contact cells: the record's first, then this Case's. | B | 002, 004, 010 |
| A **Notes** band holds the Principal's and the Claim source's notes. | The band becomes a full-width sub-panel headed **Principal**, holding only the Principal's notes (the record's, read-only, and this Case's). | C | 002, 004, 006 |
| A **Case contact** sub-panel (Contact name, Contact e-mail, Contact phone). | Removed, with its data and every path that fills it (Stage 2). | D | 001→002 |
| **Notes from client** beside Accident circumstances. | Removed, with its data (Stage 2). | E | 001→002 |
| Accident circumstances takes half of the accident band. | Accident circumstances, now alone, spans the band (open: F). | F | 002, 011→012 |
| With no Principal record notes, the Notes band packs the remaining cells. | This Case's Principal notes cell keeps its half-width place (open: G). | G | 006, 013→014 |

Shot numbers refer to `shots/NNN-<state>-<mode>-<width>[-case-details].png`. Each state has
a 1580×1000, 1440×900 and 760×1000 frame, a crop of the Case details section at each
width, and a 1580 whole page.

## 2. Live rules the mockup mirrors

| Rule | Live source |
| --- | --- |
| One look for read and edit: each fact is a `.fc` cell whose value box and control share the grid position; a cell with no control is `.ro`. | `Pages/Cases/Shared/_CaseOverview.cshtml` header comment, `Ro()` |
| The Claim source is chosen from the active Claim source contacts while editing; each option carries the record's notes and contact. | `_CaseOverview.cshtml:165–182`, `DetailsModel.ClaimSourceChoices` |
| The contact cells show the effective contact: the Case's override where one is recorded, otherwise the record's copy. | `CaseWorkspaceClaimSource.EffectiveContactName/Telephone/EmailAddress` |
| A record's notes on every Case are read live and locked, and absent when the record has none. | `CaseRecordNotes`, `_CaseOverview.cshtml:203–216` |
| While editing a Case whose Claim source has no notes, a hidden slot lets the select fill the record's notes before Save. | `data-record-notes-slot="claim-source"`; `wwwroot/js/case-workspace.js:4404–4433` |
| The select's change handler is scoped to the Case details section, not to the Notes band, so the moved cells keep working. | `case-workspace.js:4416` (`select.closest('[data-section="overview"]')`) |
| Labels | `CaseWorkspaceLabels.Frame.ClaimSource`, `ClaimSourceNotes`, `ClaimSourceNotesThisCase`, `PrincipalNotes`, `PrincipalNotesThisCase` |
| A Triage Case shows the Principal's notes, read-only (operator, 22 October 2026). It has no Case contact or Notes from client and is unchanged by this round. | `_TriageCase.cshtml:286–288` |

## 3. Frame numbers

| Measure | Value | Source |
| --- | --- | --- |
| Viewports checked and captured | 1580×1000 (plus whole page), 1440×900, 760×1000 | design authority capture rule |
| Card grid (Case, Claim source) | `1.1fr 1fr`, gap 10px; `1fr 1fr` at ≤1180px; one column at ≤760px | `case-workspace.css:118,127,128` |
| Principal panel | full width of the section, two cells (`.fg.g2`) | Notes band geometry, kept |
| Accident band | one cell spanning the band (F proposed) | `.fg` without `g2` |

## 4. What the operator has already settled

The operator's brief, 2 November 2026 (quoted in full in the
[discussion log](discussion-log.md)):

- **A** — "The "Claim Source" section is actually erroneously labelled as Principal."
- **B** — ""Claim Source" needs two notes sections - one for every case, and one for this
  case. They should be under the "Claim Source" container".
- **C** — "Principal notes can go in its own container seperate from claim source." Answers
  the same day: a **full-width band** where the Notes band is today, headed **Principal**.
- **D** — "Case Contact section - to remove. Include the extraction logic in the removal,
  not just the frontend. We dont need the case contact at all." This reverses R462
  (28 October 2026, #1682: Case contact details from the e-mail). Answer the same day: the
  Principal API's `fileHandler` block, the other source of the Case contact, is removed too.
- **E** — ""Notes from client" - to remove". Notes from client has no extraction; staff and
  the MCP Case-edit tool are its only writers.
- Stored Case contact and Notes from client values are **dropped**, with a destructive
  migration (answer, 2 November 2026).
- This round lives in `pegasus-design-archive` (answer, 2 November 2026).

## 5. Deliberate departures from live

1. **Fixture.** The live capture fixture recorded no Case workspace. For this round the
   scratch `ZzMockupCaptureCase.cs` gives the filled Case a Claim source (`Claims Direct`,
   Sam Patel), Principal and Claim source notes for this Case, and Notes from client, and
   adds the two "bare" captures. All values are synthetic.
2. **Claim source chosen.** The capture's directory options carry no notes or contact. The
   `case-edit-claim-source-changed` preset gives the `Car 2 Go` option synthetic ones and
   fires the live change handler, in both Today and Proposal.

## 6. Sign-off

Settled (§4): **A**, **B**, **C**, **D**, **E**.

Open, each "Confirm, or …":

- **F** — Accident circumstances is alone in the accident band once Notes from client goes.
  Confirm it spans the band's full width (shots 002, 012), or keep its live half-width cell
  (state `case-read-f-half`, shot 012 vs 011).
- **G** — A Case whose Principal record has no notes shows only this Case's Principal notes
  in the Principal panel. Confirm the cell keeps its half-width place, as the live grid
  does today (shot 006), or let it span the panel (state `case-read-bare-g-span`,
  shot 014).
- **H** — The DFD instruction form's *Contact details if not client* line
  (`DfdInstructionExtractionPolicy.cs:24`) is read into the instruction review as a
  labelled line. It fills no Case field, and not the Case contact. Confirm it stays, or
  remove it with the Case contact.

Consequences Stage 2 carries without a further question (from §4):

- The Claim source card's collapse key becomes `case.overview.claim-source` and the
  Principal panel's `case.overview.principal-notes`. A browser that folded the old Principal
  card or Notes band sees them open once.
- R462 is marked superseded in `docs/rulings.md`. FRD-23's instruction field row
  *Contact name, e-mail and phone* is removed, and FRD-16 §Case details is rewritten.
- The Principal API contract loses `fileHandler` (`docs/engineering/principal-api.openapi.yaml`).
- The release that ships Stage 2 carries a destructive data migration.

## 7. Self-check

2 November 2026, `python -X utf8 build/check-v43.py` against `pegasus_v43.html` built from
the `826c2aed7` captures:

```text
RESULT {"fail": [], "okCount": 112}
```

7 states × Today and Proposal, no page or console error, every Proposal marks its changes,
and the A–G hooks hold in read, edit, bare, Claim-source-changed and the F/G variants.
98 screenshots are listed in `shots/verification.json`. This tests the mockup against
itself; it is not application evidence.

## 8. Known limits

- Fonts fall back to the system UI font where the live font is not embedded.
- Requests are stubbed. Save, Edit and the Actions menu do nothing beyond a toast.
- The Claim-source-changed state is a preset with synthetic directory values (§5).
- Between 761px and 1180px the live Notes band drops to one column (`.notes-band .fg.g2`).
  The Proposal's Principal panel loses that class, so it stays two columns there. Stage 2
  either retargets the rule to the Principal panel or drops it; the mockup is not shot at
  those widths.
- Only the Case details section is proposed. The rest of the page is the capture unchanged.
