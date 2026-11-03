# v47 Stage 2 plan (built 3 November 2026)

Written during Stage 1, 3 November 2026, against Pegasus `origin/dev` `7231a4b37`. It waits
for items A–G and the operator's approval. Re-derive it if it is older than a week when
built.

The branch is `task/v47-impact-skip`, from `origin/dev`, in
`../pegasus-worktrees/v47-impact-skip`. Delivery follows `razor-html-mockup-conversion`.

## Core

- In `Assessment/AssessmentContracts.cs`, add `AssessmentVocabulary.ImpactsSkipped =
  "assessment.impacts_skipped"`, a Boolean definition in `Definitions`, so the MCP vocabulary
  describes it (D).
- In `Assessment/AssessmentPolicy.cs` `Evaluate`, add item A after Pre-incident condition:
  no `IsComplete` impact and the skip not `"true"` gives `"Impacts"`, `"Assessment record"`,
  `"No impact is entered."`, `"Enter an impact, or tick Skip impacts, on the Damage
  section."`, with `Field: AssessmentVocabulary.Impacts`. Use A's words as settled.
- The save, on the existing path (`CaseWorkspacePolicy` → `AssessmentFieldWriter`): a skip of
  `true` together with any impact row is refused, or the skip is dropped, as B settles. The
  same applies to the automation (D).
- `CaseReportFreshness`: leave the skip out, as E proposes.
- No migration. An absent skip means not skipped, which blocks existing Cases (round 1).

## Web

- `_CaseDamage.cshtml`:
  - add Skip impacts in `impact-entry-foot` (`label.choice`, a checkbox, then a hidden
    `false`, named with `CaseWorkspaceLabels.Editors.FormName`), hidden while a row exists;
  - add the static tick while reading (the `StaticTick` shape);
  - add `data-field="assessment.impacts"` on `.impact-entry`;
  - render the narrative as one block per line (G).
- `CaseWorkspaceLabels.Damage.SkipImpacts = "Skip impacts"`.
- `case-workspace.css`: the empty-state edge (round 2), the tick, the static tick, and the
  narrative line space (`1lh`).
- `case-workspace.js` `bindImpacts`:
  - the tick greys out Add impact;
  - a row hides the tick, and clearing the last row offers it again;
  - `recompose` builds line blocks.
- Follow `pegasus-ui-guardrails`.

## Documentation

- FRD-24 Damage record: replace "Impacts are optional: none blocks the report".
- FRD-11: the readiness table's Damage row, and Nature of Incident as G settles.
- FRD-16 Damage: the tick, the greyed Add impact, the empty state and the spaced narrative.
- FRD-10 MCP: the skip field.
- Rulings: rows for the brief, round 1, round 2 and sign-off, renumbered at combine.
- The guardrail reference `case-workspace.md`.

## Tests

- `AssessmentPolicyTests`: Impacts outstanding with no row; cleared by a complete impact;
  cleared by the skip; not cleared by a partial row.
- Save policy: a skip beside a row is refused or dropped (B).
- `CaseDamageAndViewerWebTests`:
  - the tick in the empty state, and absent beside rows;
  - the static tick while reading;
  - two narrative line blocks;
  - the save round-trip.
- `AutomationAssessmentIngressTests` and the vocabulary format (D).
- The architecture test's automation write-surface count, if it grows (33 → 34).
- Query-count tests keep ceilings only.

## Conformance

- Capture the implemented page from the same fixtures, with the Zz capture facts in the task
  worktree.
- Build it with the worktree's own CSS and JS, with no proposal patches or JS corrections.
- Rerun this round's behaviours as a conformance check.

CI on the PR head is the evidence for the suites.
