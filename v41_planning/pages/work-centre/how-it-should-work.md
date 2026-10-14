# Work Centre: how it should work (v41 proposal)

## Proposed design, UI & UX improvements

- **`f10` (Bug fix)**: Always renders `#wc-assign-dialog` and binds each row's `Assign Engineer` button (`data-case-id`, `data-case-ref`, `data-current-assignee`) so clicking `Assign Engineer` on any row opens the dialog for that exact Case.
- **`f11` (Token alignment)**: Removes local overrides in `work-centre.css` so Work Centre uses the canonical `20px` `h1`, `36px` `.seg` (`4px` inner radius), `11px` `34px` sticky table headers, and `6px` `--r-md` radius.
- **`f12` (Interaction)**: Adds `data-row-list` keyboard navigation, includes `<input type="hidden" name="since" />` in `.wc-find`, refreshes `Dismiss` via `[data-wc-Refresh]`, and clears `selected` when switching to `New cases` or `AI jobs`.

## Interactive comparison

Open [`pegasus_shell_v41.html`](../../current/pegasus_shell_v41.html) at `?state=work-centre&design=proposal` and toggle **Proposal** vs **Today** in the bottom-left Mockup controls strip.

See [../../current/v41-notes.md#6-sign-off-list](../../current/v41-notes.md#6-sign-off-list) for the lettered sign-off items.
