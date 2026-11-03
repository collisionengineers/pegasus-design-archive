# v46 Stage 2 conformance

The implemented Damage section and Report wording, proven on the page the implementation
renders, 3 November 2026.

- **Captures.** `captured-routed/case/` holds the Case page as Pegasus `task/v46-impact-entry`
  renders it, captured by the scratch `ZzMockupCaptureCase.CaptureV46*` facts from the same
  fixtures as the Stage 1 captures (the mockup's impacts and markers). The capture database was
  migrated through `ImpactsEnteredByHand`.
- **Build.** `build-conformance.py <task worktree>` copies the worktree's `wwwroot` (CSS, JS,
  images, fonts) into `captured-routed/_source/` and builds `pegasus_v46_routed.html` through
  `../build/build-v46.py` with no proposal patches and no script corrections, so every state is
  the implementation with its own script.
- **Check.** `check-conformance.py` prints `RESULT {"fail": [], "okCount": 65}`. It proves, with
  the implementation's own script: the rows as captured; one geometry in read and edit (cells
  and row heights alike, no value beside its control); Add impact; filling a row; the × removing
  its row; an incomplete row kept but left out of the narrative; the Incident narrative
  following the rows, one sentence to a line; a marker drawn and moved but never removed by
  dragging; Clear markers leaving the impacts; no Reset, chips, readout or plan-area controls;
  the 1580 single line and the 760 fold; and, with no impact, no Nature of Incident block or
  tick and no impact blocker.
- **Shots.** `shots/<state>-routed-<width>.png`, `-panel` crops and a 1580 `-full` page, for the
  nine Stage 1 states. Compare each with `../shots/NNN-<state>-proposal-<width>.png`.

The save itself (the hidden JSON fields reaching the Case workspace command) is proven by the
integration tests `CaseDamageAndViewerWebTests` and `AutomationAssessmentIngressTests` in the
pull request, which CI runs.

## Departures from the mockup

- The Report wording's Nature of Incident block refreshes when the Case saves, not as the rows
  change. The save compares the posted wording with the sentence composed from the stored
  impacts and records any difference as the Engineer's own wording, so recomposing the text box
  in the browser would mark the new sentence hand-edited. The Damage section's Incident
  narrative, which is read-only, does follow the rows as they change, from Core's sentence and
  words.
- A row with nothing chosen or written is not saved; it stays on the page until the Case is
  reloaded.
