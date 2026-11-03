# v46 Stage 2 plan (not started)

Written during Stage 1 on 3 November 2026 against `origin/dev` `fb4c5e741`. It is built only
after items A–L are settled, and is re-derived if the head moves more than a week. Branch
`task/v46-impact-entry` from `origin/dev`.

## Core (`src/Pegasus.Core/Assessment`, `src/Pegasus.Core/Reports`)

- `AssessmentVocabulary`: a new staff-edited JSON field for the impact rows (severity, location,
  note; no type, round 2), with its `Format` text for `pegasus_vocabulary_get`. Location codes are
  the 11 areas (B).
- Remove the derived pair `assessment.impact_location` / `assessment.impact_severity`,
  `DerivedPaths`, `SeveralAreas`, `DeriveImpactValues`, `GroupAreas`, and
  `DamageAreaGeometry.AreaAt` / `Touch` once nothing else uses them (I).
- `damage.impacts` shrinks to markers `{x, y, r}`. `AssessmentImpact` loses areas, severity and
  note, and the reader refuses them.
- Report: `AssessmentReportWording.ImpactMagnitude` and `ReportWording.NatureOfIncidentSentence` /
  `NatureOfIncidentOf` read the rows per item A, and with no impact Nature of Incident is not
  offered (G, ruled). `ReportImpact` carries a disc only. `AcceptedReportSource` stops requiring
  ImpactSeverity and ImpactLocation, and the two readiness items in `AssessmentPolicy` go (G).
- `CaseReportFreshness` watches the new field instead of the derived pair.

## Infrastructure

- `AssessmentFieldWriter` stops deriving.
- A data migration reshapes the stored `damage.impacts` to discs and applies item F. Item F decides
  whether it is destructive. If it is, the release runbook's destructive-migration steps apply.

## Web (`pegasus-ui-guardrails`)

- `_CaseDamage.cshtml`: remove the derived cells, the list, the chips, the readout and the
  plan-area controls, and add the impact rows per K, with read and edit sharing one geometry.
- `case-workspace.js`: the damage editor loses areas, severity, notes, chips and derivation, and
  gains removal per J. A small row editor handles Add and the × (C), and recomposes the Incident
  narrative.
- `CaseWorkspaceLabels.Damage` gets the item D words. `OperatorLabels.CaseWorkspace.EngineerSections`
  drops Impact location and Impact severity.
- `CaseWorkspaceLabels.Editors` lists the new field so `pegasus_assessment_update` accepts it (H).
- `AssessmentMcpTools.WriteRefusal` and the tool description drop "Derived from damage.impacts".

## Documentation

- Rewrite FRD-24's Damage record clause and short version, and FRD-11's "Damage to several areas"
  line. Both are dated and cite the new rulings.
- Add `docs/rulings.md` rows in the operator's words: the round 1 answers and the sign-off.
  Renumber at combine.

## Tests (CI runs them)

- Core: remove the derivation tests in `AssessmentPolicyTests`, add row parsing and refusal tests,
  and update the report wording and projection tests for item A.
- Integration: `CaseDamageAndViewerWebTests`, `CaseEngineerSectionsWebTests`,
  `AssessmentPersistenceIntegrationTests`, `CaseWorkspacePersistenceTests`,
  `AssessmentReportDraftWebTests` and `TemplateSampleJobs` per
  `git grep "ImpactLocation\|DeriveImpactValues"`.
- MCP: the update tool writes the rows, and the vocabulary read lists them.
- Conformance: side-by-sides of the Damage section against this mockup.
