# Search: how it should work (v41 proposal)

## Proposed design, UI & UX improvements

- **Item F (`f13`)**: Replaces the raw GUID text box for `Engineer` and free-text inputs for `Principal` and `Origin` with `<select>` dropdowns, renames `State` to `Case stage`, and keeps `More filters` open whenever any secondary filter is active.
- **Item G (`f14`)**: Removes the duplicate `Create Case` button from `.page-header`, adds `class="table"` and the `Type` and `Due` columns to Results, relabels `PrincipalReference` to `Claim ref` in `_CasePreview.cshtml`, adds `Copy Case/PO`, and computes `Next action` via `CaseNextAction` across all stages.

## Interactive comparison

Open [`pegasus_shell_v41.html`](../../current/pegasus_shell_v41.html) at `?state=search&design=proposal` and toggle **Proposal** vs **Today** in the bottom-left Mockup controls strip.

See [../../current/v41-notes.md#6-sign-off-list](../../current/v41-notes.md#6-sign-off-list) for the lettered sign-off items.
