# Unidentified, Vehicle Images, Pre-Case Images & Auxiliary Case Routes: how it should work (v41 proposal)

## Proposed design, UI & UX improvements

- **Item O (`f24`)**: Removes duplicate ribbon facts from the first card below the ribbon on `/Unidentified/{id}` and `/VehicleImages/{id}`, replaces the inline table-cell `<details>` form with `#dismiss-reading-dialog`, adds `#pair-case-dialog` on `/VehicleImages/{id}`, and preserves `?viewer=open&photo=N` across pre-Case Crop/Tag saves.
- **Tier `a` (`f25`)**: Adds `.req`/`required` and `Cancel` to `/Cases/{id}/Chaser`, and links `site.css` in the Glass integration pages.

## Interactive comparison

Open [`pegasus_shell_v41.html`](../../current/pegasus_shell_v41.html) at `?state=unidentified-images&design=proposal` and toggle **Proposal** vs **Today** in the bottom-left Mockup controls strip.

See [../../current/v41-notes.md#6-sign-off-list](../../current/v41-notes.md#6-sign-off-list) for the lettered sign-off items.
