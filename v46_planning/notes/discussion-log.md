# v46 discussion log

How the round came to be. This log is not design authority.

## Round 1: brief and questions, 3 November 2026

**Brief (operator):**

> PR1862 added a functionality for determining the impact location based on the damage markers
> touching and their area.
>
> We are going to remove and simplify this process into two.
>
> [an image of another system's three "Impact" rows: Moderate · Collision/Impact · Rear · (empty)
> · Clear, then two empty rows]
>
> The new process: The impact markers are purely for report illustration purposes rather than
> calculating the impact area. The impact areas will be manually entered by a staff member.
> Consider that we will also need MCP tools if we do not already have this.

**Explored.** The live Damage section (`_CaseDamage.cshtml`, `case-workspace.js`), Core's
derivation (`AssessmentPolicy.DeriveImpactValues`, `DamageAreaGeometry`), the report's two
readers (`AssessmentReportWording.ImpactMagnitude`, `ReportWording.NatureOfIncidentSentence`),
readiness (`AcceptedReportSource`) and the MCP tools (`pegasus_assessment_update` refuses
`DerivedPaths`; `pegasus_vocabulary_get` lists formats). `reference/rendererref1/DESIGN_SPEC.md`
first had `impact_severity` and `impact_location` as dropdowns.

**Questions and answers.**

| Question | Operator's answer |
| --- | --- |
| The example row has four boxes; nothing in Pegasus says what the fourth holds | "Free-text note" |
| Type: a pick list or free text? | "Collision/Impact only for now" |
| How many rows, and how does the report use them? | "Add rows as needed" |
| What does a damage marker keep? | "Position only (Recommended)": a marker is a burst on the plan; its areas, severity and note go; Underside, Interior and Mechanical become Location values |

**Made.** The mockup over six fresh captures. It adds a K variant with the impacts under the plan
and an A variant where Nature of Incident uses the first impact only.

**Raised.** Items A–L in [v46-notes.md §6](v46-notes.md#6-sign-off). The rows answer did not
settle how several rows reach the report (A).

## Round 2: while the mockup was built, 3 November 2026

**Operator:**

> could do an X for clear instead
>
> The incident narrative also needs to adjust
>
> And if no impact area is chosen, the nature of incident block would be skipped on report
>
> we dont need the "type" box

**Changed.**

- Each row's Clear button is now an ×, with the spoken label and tooltip "Clear" (C, D).
- The Damage section's Incident narrative and the Nature of Incident block recompose as rows are
  added, changed or cleared, and read Not recorded with no impact (A).
- New state `wording-none`. In the no-impact states, Impact location and Impact severity stop
  blocking the report, and Nature of Incident has no block and no tick. Clearing every row hides
  them live.
- The Type box is gone, replacing round 1's "Collision/Impact only for now". The sentence keeps
  live's fixed "collision/impact" wording. With Type gone the Note column is wider, and at 760 it
  spans the card.

**Closed.** G is settled by the third line. It leaves G2 open: whether a row missing its Severity
or Location counts as an impact.

## Round 3: sign-off answers, 3 November 2026

**Operator:**

> A - No, there should be a seperate sentence for each impact
>
> J - Include a clear markers button

**Changed.**

- Nature of Incident and the Incident narrative are a separate sentence for each impact, one to a
  line, in row order. The single joined sentence and the `wording-row1` variant are gone (A).
- While editing, a Clear markers button beside Reset removes every marker and leaves the impacts
  alone. Dragging a single marker off the plan still removes it (J).

**Raised.** A2: what Impact Magnitude prints when there are several impacts, and whether the
sentences sit one to a line. J2: whether dragging a marker off the plan stays as a way to remove
one. The other items (B–F, G2, H, I, K, L) still wait for an answer.
