# Case Record Workspace: how it works today (`origin/dev`)

## Source files

- `src/Pegasus.Web/Pages/Cases/Details.cshtml` and `Details*.cs`
- All 35 partials in `src/Pegasus.Web/Pages/Cases/Shared/` (`_CaseRibbon.cshtml`, `_CaseAside.cshtml`, `_CaseReport.cshtml`, `_CaseTasks.cshtml`, `_CaseEstimate.cshtml`, `_CaseValuation.cshtml`, `_CaseFiles.cshtml`, `_CaseHistory.cshtml`, etc.)
- `src/Pegasus.Web/wwwroot/css/case-workspace.css` and `src/Pegasus.Web/wwwroot/js/case-workspace.js`
- `src/Pegasus.Web/Presentation/CaseWorkspaceLabels.cs` and `CaseNextAction.cs`

## Current behaviour and audit findings

- Preserves all settled Case Workspace guardrails (`.agents/skills/pegasus-ui-guardrails/references/case-workspace.md`): one scrolling page, save-as-you-go, sticky ribbon with `Tasks (N)` modal trigger, sticky right aside (`Next step`, `Case team`, `Integrity`), Valuation guide cards, and v38 Repair Spec bars.
- `_CaseRibbon.cshtml:241` and `_CaseTasks.cshtml:76` reference non-existent `#icon-check-square` instead of `#icon-square-check` (rendering a blank icon on `Tasks`).
- Empty states in Tasks, Images, Documents, Correspondence, and Queries use `.empty` or `.muted` instead of `.empty-line` (`v36 f46`).
- `_CaseSectionHeadTools.cshtml` and `_SubPanelToggle.cshtml` hardcode `title="Collapse section"` even when collapsed; `case-workspace.css:177` centers `[data-damage-reset]` instead of right-aligning it; `_CaseReport.cshtml:588-590` displays `"Not recorded"` in read mode when `To`/`Cc` suggestions exist; `_CaseReport.cshtml:840` and `_CaseOriginalReport.cshtml:76` include a duplicate blank `<option value="">`.
- Post-report open tasks in `.aside-card--action` (`_CaseAside.cshtml:300-315`) render as an unstyled `ul.blocker-list` with repeated `Tasks` buttons instead of `.next-step-list` / `.next-step--item` row buttons.
- `#case-tasks-dialog` uses bare inputs without `.fi`, `"None"` instead of `"Unassigned"`, and wraps row action buttons; `#send-to-ai-dialog` uses a bare number input for `Target Estimate (%)`.
- `case-workspace.js` lacks a `dblclick` listener on `[data-estimate-tab-label]` (`v28 P32`) and omits `list="report-address-book"` on dynamically added `Add To`/`Add Cc` inputs.

See [../../current/v41-notes.md](../../current/v41-notes.md) for the complete `f01`–`f39` table and exact file/line citations.
