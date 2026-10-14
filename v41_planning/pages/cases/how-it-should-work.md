# Cases Queue & Create Case: how it should work (v41 proposal)

## Proposed design, UI & UX improvements

- **Item L (`f21`)**: Populates the `/Cases` `Principal` filter from the full active Principal directory (all 15 Principals), shows `Page N` only when paged (`total > pageSize`), and supports `data-row-list` keyboard navigation.
- **Item M (`f22`)**: Wraps `<details>` fields in `.form-grid .field`, removes internal parser provenance strings (`InstructionPdfParser`), and removes the `"Optional for Triage"` hint.

## Interactive comparison

Open [`pegasus_shell_v41.html`](../../current/pegasus_shell_v41.html) at `?state=cases-queue&design=proposal` and toggle **Proposal** vs **Today** in the bottom-left Mockup controls strip.

See [../../current/v41-notes.md#6-sign-off-list](../../current/v41-notes.md#6-sign-off-list) for the lettered sign-off items.
