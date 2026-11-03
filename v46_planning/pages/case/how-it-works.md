# Case record: Damage, how it works

Read from the live source on 3 November 2026 (Pegasus `origin/dev` `fb4c5e741`, after PR 1862).

## What the page does not show

- Staff cannot type an impact location or severity. Both are derived from the markers on every
  save, and a field save that names one is refused.
- Whether separate bursts read as one location or as Multiple depends on whether their discs
  touch on the canonical plan, and nothing on the page shows that.
- A damage recorded by area alone (keyboard, or before discs existed) is drawn with the disc its
  areas give. Two such damages in neighbouring areas can stand apart and read Multiple: the
  `v46-two-*` fixture's RH Rear and Rear do.
- The only way to remove a marker is the × on its list row. Live clamps a disc's centre to the
  plan box, so a burst cannot be dragged off.

## Governing documentation

| Document | What it settles here |
| --- | --- |
| FRD-24 Damage record | Entries record areas, severity and note. Location and severity are derived by Core (R639: touching bursts are one damage; separate groups read Multiple; the highest severity) |
| FRD-11 Report wording blocks | The Nature of Incident sentence. Several areas end "to the following areas:" with one area per line |
| R639 | The grouping rule and "no backfill" for stale Cases |
| `reference/rendererref1/DESIGN_SPEC.md` | Originally, `impact_severity` and `impact_location` were dropdowns |

## Source by layer

| Layer | File | Owns |
| --- | --- | --- |
| Web | `Pages/Cases/Shared/_CaseDamage.cshtml` | The plan, bursts, chips, derived cells, marker list, Unrelated damage and Incident narrative |
| Web | `wwwroot/js/case-workspace.js` (damage editor) | Drawing, moving and sizing discs, the readout, the chips, the list, client-side grouping for the live cell, and Reset |
| Web | `Presentation/CaseWorkspaceLabels.cs` (`Damage`) | The section's words |
| Web | `Mcp/AssessmentMcpTools.cs` | `pegasus_assessment_update` refuses `DerivedPaths` ("Derived from damage.impacts.") |
| Core | `Assessment/AssessmentContracts.cs` | `AssessmentImpact`, `DamageAreas`, `DamageSeverities`, `SeveralAreas`, `DerivedPaths`, `DamageImpactsFormat` |
| Core | `Assessment/AssessmentPolicy.cs` | `ParseImpacts`, `DeriveImpactValues`, `GroupAreas`, and the readiness items for Impact severity and location |
| Core | `Reports/ReportWording.cs`, `AssessmentReportWording.cs` | Nature of Incident and Impact Magnitude |
| Core | `Reports/AssessmentReportRendering.cs` | `AcceptedReportSource` requires ImpactSeverity and ImpactLocation; `ReportImpact` draws the diagram |
| Infrastructure | `Persistence/AssessmentFieldWriter.cs` | Writes the derived pair beside `damage.impacts` on every save |

## Behaviours

### Recording a damage

Pressing on the vehicle starts a disc, and dragging sizes it. Each disc names the plan areas it
touches and defaults to Moderate with no note. Its list row offers a severity select, a note and
a ×. Underside, Interior and Mechanical are toggle chips, each recorded alone.

### The derived cells

Impact location is the area most of a touching group's centres sit in, or Multiple for several
groups. Impact severity is the highest recorded. The script recomputes the location cell as the
section edits, and Core recomputes both on save.

### The report

Nature of Incident composes from the derived pair, and lists the areas whenever there are
several. Impact Magnitude prints "{Severity} — {Location}". The diagram draws every disc as the
same burst.

## Things the FRD does not settle

- How several typed impacts reach the report (v46 item A).
- What becomes of existing Cases' derived values and area-only damages (v46 item F).
