# Case Record Workspace: how it should work (v41 proposal)

## Proposed design, UI & UX improvements

- **Items P & Q (`f27`)**: Confirms Report Delivery `.fg`/`.fc` read/edit parity (`To`, `Cc`, `Subject`, `Standard message` or `Covering note`, `Attachments`), visible `Yes`/`No` radio pills on undecided rule questions, inline `Done` hold tick on the hold's own line, and one-step `"send"` wording (`Send report`, `"Add at least one To recipient before sending."`).
- **Item R (`f28`)**: Renders post-report open tasks in `.aside-card--action` as `.next-step-list` / `.next-step--item` row buttons that open `#case-tasks-dialog` on click, matching pre-report blockers.
- **Item S (`f29`)**: Styles `#case-tasks-dialog` inputs with `.fi`, labels the blank assignee option `Unassigned`, keeps task row actions (`Save`, `Complete`, `Reopen`, `Remove`) on one `.cluster` line, and pairs `Target Estimate (%)` in `#send-to-ai-dialog` with a synchronized range slider + `.fc` number input.
- **Tier `a`/`c` (`f26`, `f30`)**: Fixes `#icon-square-check`, `.empty-line`, dynamic `Expand`/`Collapse` titles, right-aligned `[data-damage-reset]`, suggested `To`/`Cc` display in read mode, duplicate blank `<option>`, `[data-estimate-tab-label]` double-click rename, and `list="report-address-book"` on added recipient inputs.

## Interactive comparison

Open [`pegasus_case_workspace_v41.html`](../../current/pegasus_case_workspace_v41.html) at `?state=v41-overview&design=proposal` and toggle **Proposal** vs **Today** in the bottom-left Mockup controls strip.

See [../../current/v41-notes.md#6-sign-off-list](../../current/v41-notes.md#6-sign-off-list) for the lettered sign-off items.
