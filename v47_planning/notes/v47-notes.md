# v47 notes: an impact, or a deliberate Skip impacts

The round opened on 3 November 2026. The live source was read from Pegasus `origin/dev`
`7231a4b37` (`captured-live/_source/source.txt`), which includes PR 1869 (v46, R642–R646). The
brief, the questions and the operator's answers are in [discussion-log.md](discussion-log.md).

## 1. What changes

| # | Today (problem) | Proposal | Shots |
| --- | --- | --- | --- |
| 1 | A Case with no impact is ready to send. The Next action is Send report, no readiness item names the impacts, and the report silently prints no Nature of Incident | Readiness names **Impacts** ("Assessment record · No impact is entered.") until a complete impact is entered or Skip impacts is ticked. It is the Next action step and a line in Report not ready, and its Damage control jumps to the impacts (A) | 001–004 |
| 2 | Nothing offers a deliberate skip | **Skip impacts**, a tick beside Add impact while editing, offered only while no impact row exists. Ticking it greys out Add impact, and unticking enables it again. Adding a row hides the tick, and clearing the last row offers it again, unticked (B, round 2) | 003/004, 007/008 |
| 3 | — | While reading, Skip impacts is a static tick under No damage recorded., ticked or not (C) | 001/002, 005/006 |
| 3a | With no row, No damage recorded. and Add impact stand on the row grid's Severity column, so they float with nothing to align to | With no row, the empty line, Add impact and the tick sit on the facts' own left edge, the edge of the Unrelated damage and Incident narrative cells. Once a row exists the live row grid is unchanged (round 2) | 001–008 |
| 4 | A row with a severity and no location is kept but prints nothing, and the Case reads ready | The row is not an impact, so Impacts stays outstanding. Skip impacts is not offered because a row exists (B) | 009–012 |
| 5 | Two impacts' sentences sit on consecutive lines in the Incident narrative | A line's space between sentences, read and as the narrative recomposes while editing (G) | 013–016 |

Shot numbers are the `NNN-` prefixes in [../shots](../shots): odd is Today, even is Proposal.
Each comes at 1580, 1440 and 760, with a `-panel` crop of the Damage section and a 1580
`-full` page.

## 2. Live rules the mockup mirrors

| Rule | Source |
| --- | --- |
| An impact is complete when it names a severity and a location | `AssessmentImpact.IsComplete` |
| A readiness item is drawn as the Next action step (requirement, then "source · why", then the section's control) and as a line in Report not ready. The "how to resolve" sentence is shown only to automation (MCP) | `_CaseAside.cshtml`; `AssessmentMcpTools`, `ReportMcpTools` |
| A blocker naming a Damage field jumps to Damage and outlines the cell carrying that `data-field` | `CaseWorkspaceLabels.Report.BlockerSection`, `BlockerField` |
| A tick while editing is `label.choice` with a checkbox, then a hidden `false` | `_CaseEstimate.cshtml` (Explain on report), `_CaseReport.cshtml` `SwitchSetting` |
| A tick while reading is `span.choice.is-static` with `.tick` holding `icon-check` when on | `_CaseReport.cshtml` `StaticTick` (v45) |
| Add impact and the rows' JavaScript are unchanged; the mockup's hooks (narrative blocks, the tick's offer, Add impact greyed) act only on Proposal markup | `bindImpacts` in `case-workspace.js`; `JS_CORRECTIONS` in `build/build-v47.py` |

The readiness item in the blocked states is the application's own rendering. The Proposal of
`none-*` and `partial-*` is built over the same Cases captured with a scratch rule switched on
in the capture worktree (`MOCKUP_V47_RULE=1`, never committed). The mockup draws only the tick,
the narrative's spacing and the `data-field` the jump outlines.

## 3. Frame numbers

- **Empty state (no row), every width.** "No damage recorded." takes the facts column's left
  edge (live indents it 58 px, to the Severity column). While editing, the foot below it is a
  flex line on the same edge: Add impact, then Skip impacts 16 px after it, centred on one
  line. While reading, the static tick stands alone on that edge. The edge is the one the
  Unrelated damage and Incident narrative cells start on.
- **With rows.** The live grid is unchanged: Add impact stays under the Severity column and the
  tick is hidden.
- **Tick size.** 15 px, 12.5 px text, weight 500, `accent-color: var(--red)`, at the 36 px
  control height. These are the live estimate ticks' numbers.
- **Narrative.** Each sentence is a block, with one line height (`1lh`) of space before the
  second and later ones. The cell keeps its 72 px minimum.

## 4. Decisions and authority

| Decision | Authority |
| --- | --- |
| A Case needs a complete impact or a deliberate skip before its report; the narrative itself stays optional | Operator brief, 3 November 2026 |
| The skip is a tick on the Damage section beside Add impact | Operator, 3 November 2026 (round 1, "Damage section (Recommended)") |
| It is offered only while no impact row exists | Operator, 3 November 2026 (round 1, "Offered only with no rows (Recommended)") |
| Its label is "Skip impacts" | Operator, 3 November 2026 (round 1) |
| Existing Cases are blocked, with no backfill | Operator, 3 November 2026 (round 1, "Block existing Cases (Recommended)") |
| A space between the narrative's lines | Operator, 3 November 2026 ("each Impact entry should have a space between the lines") |
| The empty state is organized on one edge, not floating | Operator, 3 November 2026 (round 2) |
| Skip impacts greys out Add impact | Operator, 3 November 2026 (round 2) |
| The readiness item's words | Proposal, item A. They follow the live `RequireField` pattern and are not operator words yet |

## 5. Coverage audit and departures from live

Every control and fact in the live Damage section (`v47-none-edit.html`, `v47-two-read.html`)
and the aside readiness (`v47-rule-none-read.html`):

| Live item | Proposal |
| --- | --- |
| Plan, markers, Clear markers | Unchanged |
| Impact rows: Impact · Severity · Location · Note · × | Unchanged |
| "No damage recorded." | Unchanged, and still shown with Skip impacts ticked |
| Add impact | Unchanged; Skip impacts stands beside it |
| Unrelated damage | Unchanged |
| Incident narrative | Spaced lines (G); otherwise unchanged, and `Not recorded` with no impact |
| Next action step and Report not ready | Impacts added while outstanding (A); otherwise the application's own |
| The Report section, Report wording and Nature of Incident | Unchanged: with no complete impact the block is still not offered, and nothing prints |

**Departures from live, deliberate:**
- With no row, "No damage recorded." and Add impact move from the Severity column to the
  facts' left edge (round 2: "it does look odd with things kinda floating rather than being
  organized"). With rows, nothing moves.

**Not shown:**
- The Report section's own not-ready state. It is the application's rendering in the rule
  captures, and the round changes nothing there.

## 6. Sign-off

**Outcome, 3 November 2026.** The operator: "Design approved." Every item is confirmed as
proposed. B's open point, the save given a skip beside a row, was asked separately, and the
operator chose **"Refuse (Recommended)"**: the save is refused with "Skip impacts can be
ticked only while no impact is entered." (R649).

Each item read "Confirm, or …".

- **A. The readiness item.** Requirement **Impacts**, source **Assessment record**, why **"No
  impact is entered."**, and for automation the resolution **"Enter an impact, or tick Skip
  impacts, on the Damage section."**. It is outstanding while no impact names both a severity
  and a location and Skip impacts is not ticked. FRD-24's "Impacts are optional: none blocks
  the report" and FRD-11's readiness row "impacts are optional" are replaced. **Confirm, or**
  give the words.
- **B. Skip impacts while editing.** It stands beside Add impact and is offered only while no
  impact row exists:
  - ticking it greys out Add impact (round 2, settled), and unticking enables it again;
  - adding a row hides it;
  - clearing the last row offers it again, unticked;
  - the save refuses or drops a skip sent with any impact row (Stage 2), so the two never
    stand together.

  A row with a severity and no location (or the reverse) is a row. It hides the tick and does
  not satisfy A. **Confirm, or** say whether an incomplete row should leave Skip impacts
  offered.
- **C. Skip impacts while reading.** It is a static tick in the same place, ticked or not,
  shown only while no row exists. Nothing prints on the report: no Nature of Incident, and
  Impact Magnitude keeps `—`. **Confirm, or** show the tick only once it is ticked.
- **D. Automation.** `pegasus_assessment_update` writes the skip
  (`assessment.impacts_skipped`, `true` or `false`) like any staff field, with no new tool;
  `pegasus_vocabulary_get` describes it, and the automation is refused a skip beside an impact
  as staff are. **Confirm, or** keep the skip staff-only.
- **E. Staleness.** Ticking or unticking Skip impacts does not by itself make a sent report
  out of date, since it prints nothing. **Confirm, or** treat it as a report change.
- **F. History.** The tick is saved and audited as any assessment field (`case_assessment_saved`,
  with its before and after). There is no new audit event. **Confirm, or** name an event.
- **G. Where the space between lines applies.** The space is the Case page's Incident
  narrative only, and it includes an Engineer's own multi-line wording. The printed Nature of
  Incident and the Report wording text box keep R645's one sentence to a line, with no space.
  **Confirm, or** the report prints the same space.

## 7. Self-check

`python -X utf8 build/check-v47.py`, on 3 November 2026: `RESULT {"fail": [], "okCount": 166}`,
with no page or console error in any state or mode.

It checks:
- Today: a no-impact Case is ready, its Next action is Send report, there is no Skip impacts,
  and the narrative is plain text.
- A: the Impacts step and list line in `none-*` and `partial-*`, routed to Damage, and their
  absence with a skip or an impact.
- C: the static tick, off and on.
- B: the tick offered; ticking it greys out Add impact, which then adds no row; unticking
  enables it; a row hides the tick; and clearing the last row offers it again, unticked. It is
  not offered beside a partial row or two rows.
- Round 2's layout: with no row, Add impact, the empty line and the reading tick start on the
  Unrelated damage cell's edge. With rows, Add impact stays under Severity as live.
- G: one block per sentence with about one line height between them, read and as the
  narrative recomposes when a location changes and rows are cleared.
- 760: the tick shown and inside the page. 1580: the tick on Add impact's line.
- The screenshots, with no console error.

The self-check and the screenshots test the mockup against itself. They are not application
evidence.

## 8. Known limits

- Ticking Skip impacts in the mockup does not clear the Impacts step. Readiness is computed
  when the page renders, so it clears on Save, as live. `skipped-*` shows the Case as saved.
- The rule captures run Core's scratch rule. The Stage 2 rule will live in
  `AssessmentPolicy.Evaluate` with the same words unless A changes them.

## 9. Stage 2

Planned in [stage-2-plan.md](stage-2-plan.md) and built on `task/v47-impact-skip`. The
conformance evidence is in [../conformance/README.md](../conformance/README.md).
