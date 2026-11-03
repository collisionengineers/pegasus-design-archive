# v47 discussion log

How the round came to be. This log is not design authority.

## Round 1: brief and questions, 3 November 2026

**Brief (operator):**

> Examine PR1869 and its changes. These have landed in main and deployed now.
>
> This has presented an unintended side effect, whereby the "Incident Narrative" is an optional
> field. Whilst we do want it to be skippable, nothing prompts the user to enter or skip this.
>
> Therefore, we need this to work as follows:
>
> The user MUST enter an impact for the incident narrative, OR deliberately select an option to
> skip this.
>
> The incident narrative shall not be required for a report, but there must be a deliberate
> choice to skip this, rather than at present, where an uninformed user may not realize.

**Explored.**
- The live Damage section (`_CaseDamage.cshtml`, and `bindImpacts` in `case-workspace.js`).
- Readiness (`AssessmentPolicy.Evaluate`, `AssessmentReportProjection.Prepare`).
- The blocker routing (`CaseWorkspaceLabels.Report.BlockerSection`, which routes by the item's
  field).
- Report wording's Nature of Incident block (`ReportWordingComposition.Offered`, which offers no
  block that composes nothing).
- FRD-24 and FRD-11, which say "Impacts are optional: none blocks the report" (R646).

**Questions and answers.**

| Question | Operator's answer |
| --- | --- |
| Where should the skip control sit: on the Damage section beside the impact rows, or as Report wording's Nature of Incident tick? | "Damage section (Recommended)" |
| While the skip is ticked, what happens to the impact rows? | "Offered only with no rows (Recommended)": the tick shows while no impact row exists; adding a row removes it, and it cannot be set while a row is there |
| What does the tick say? | "Skip impacts" |
| Existing Cases, which the PR 1869 migration left with no impacts: blocked, or pre-ticked by a migration? | "Block existing Cases (Recommended)": no backfill; each open Case needs an impact or the skip before its next report |

**Addition (operator, with a screenshot of the live Incident narrative reading two sentences on
consecutive lines):**

> addition small change: on the incident narrative, each Impact entry should have a space
> between the lines

**Made.**
- The mockup over six fresh captures of `origin/dev` `7231a4b37`: two impacts, none and one
  partial row, each in read and edit.
- Three more captures of the same Cases with the proposed readiness item, so the blocked Case
  page is the application's own rendering and not a drawing.

**Raised.** Items A–G in [v47-notes.md §6](v47-notes.md#6-sign-off).

## Round 2: the mockup's layout, 3 November 2026

**Operator (on a screenshot of the `none-read` Proposal, where No damage recorded. and Skip
impacts stood on the row grid's columns):**

> it does look odd with things kinda "floating" rather than being organized

> "skip impacts" should grey out the "add impact" box

**Changed.**
- With no impact row, the empty line, Add impact and Skip impacts sit on the facts' own left
  edge, the edge the Unrelated damage and Incident narrative cells use. Add impact and the
  tick share one line while editing. With rows, the live grid is unchanged.
- Ticking Skip impacts greys out (disables) Add impact, and unticking enables it again. A row
  can therefore only be added while the tick is off.

**Raised.** Nothing new. Item B records the greyed Add impact as settled.

## Sign-off, 3 November 2026

**Operator:**

> Design approved.
>
> /razor-html-mockup-conversion
>
> Integrate into our case page, with consideration to core rules, testing, and necessary files to edit

**Asked:** what the save does when Skip impacts arrives with an impact row, which the page cannot
send but automation can (item B's open point; D said automation is refused).

| Question | Operator's answer |
| --- | --- |
| A skip saved beside an impact row: refuse, or drop the skip silently? | "Refuse (Recommended)": the save fails with "Skip impacts can be ticked only while no impact is entered." |

## Stage 2: the markers, 3 November 2026

**Operator** (asked whether both the markers and the impacts were required):

> The markers are always required, no matter what. The impacts section is required regardless (or skipped).

> This isnt an edge case, this is intended behaviour. The markers are required. The "add impact" must either be entered, or skipped.

| Question | Operator's answer |
| --- | --- |
| The markers blocker's words | "Damage markers (Recommended)": Damage markers · Assessment record · "No damage marker is drawn."; "Draw a marker on the plan on the Damage section." |

**Changed.** A second readiness item, Damage markers, is outstanding until a marker is drawn,
Skip impacts or not (R650).
