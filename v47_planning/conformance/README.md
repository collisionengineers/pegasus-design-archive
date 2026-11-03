# v47 Stage 2 conformance

The implemented Skip impacts, Impacts readiness and spaced Incident narrative, proven on the page
the implementation renders, 3 November 2026.

- **Captures.** `captured-routed/case/` holds the Case page as Pegasus `task/v47-impact-skip`
  renders it. It was captured by the scratch `ZzMockupCaptureCase.CaptureV47*` facts from the
  same fixtures as the Stage 1 captures (two impacts, none, one partial row), plus a Case saved
  with `assessment.impacts_skipped` = `true`. The readiness item is the application's own
  (`AssessmentPolicy.Evaluate`), with no scratch rule.
- **Build.** `build-conformance.py <task worktree>` does three things:
  - it copies the worktree's `wwwroot` into `captured-routed/_source/`;
  - it builds `pegasus_v47_routed.html` through `../build/build-v47.py`, with no proposal
    patches, no presets and no script corrections;
  - every state is therefore the implementation with its own CSS and script.
- **Check.** `check-conformance.py` is the Stage 1 self-check run against the implementation,
  without the Today-only checks. It prints `RESULT {"fail": [], "okCount": 112}`. It proves:
  - the Impacts step and blocker on the none and partial Cases, routed to Damage, and absent
    when skipped or with impacts;
  - the impacts block carrying the `data-field` the jump outlines;
  - the static tick while reading, off and on;
  - while editing, Skip impacts beside Add impact. Ticking it greys out Add impact, and a
    greyed Add impact adds no row; unticking enables it. A row hides the tick, and clearing the
    last row offers it again, unticked. It is not offered beside a partial row or two rows;
  - the round-2 left edge with no row;
  - one block per narrative sentence with about a line height between them, read and as the
    rows are edited;
  - at 760, the tick inside the page; at 1580, the tick on Add impact's line, and Add impact
    under Severity once rows exist.
- **R650.** The check also proves that Damage markers is outstanding on every Case with no
  marker, the skipped one included, and not on the Cases with markers. With no marker, Damage
  markers is the first Next action step, because the plan comes before the rows. The plan
  carries the `data-field` its jump outlines.
- **Shots.** `shots/NNN-<state>-routed-<width>.png`, with `-panel` crops and a 1580 `-full`
  page. Each takes the number of the Stage 1 Proposal shot it compares with,
  `../shots/NNN-<state>-proposal-<width>.png`.

The first run found one departure: the reading foot lacked the empty spacer span the mockup
puts first, so the empty-state rule hid the static tick. The partial now carries the spacer.

The save itself is proven by the integration tests in the pull request, which CI runs:
- the tick posting `true` ahead of its hidden `false`;
- the refusal of a skip beside a row;
- the automation write.

The tests are in `CaseDamageAndViewerWebTests`, `AssessmentPersistenceIntegrationTests` and
`AutomationAssessmentIngressTests`.
