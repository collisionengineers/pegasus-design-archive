# Inbox & Message Record: how it should work (v41 proposal)

## Proposed design, UI & UX improvements

- **Item H (`f15`)**: Consolidates all 5 mailbox scopes in the left scope rail (`All incoming`, `No Case Found`, `Sent Items`, `Dismissed`, `Deleted Items`) and uses a consistent 3-column filter bar (`Mailbox`, `Category`, `Search`).
- **Item I (`f17`)**: Shows `Subject` once in `.page-header h1`, merges `Destination`/`Filed to` into a single `Case` row in `Decision`, replaces `.provenance` tooltip with plain text, shows human file types (`PDF document`, `Word document`) + size in `Attachments`, and adds `Cancel` to the inline reply composer.
- **Item J (`f18`)**: Opens `#unlinkCaseDialog` and `#linkCaseDialog` directly on click (`data-dialog-open`) and acquires/consumes the Case lease in the single confirmation POST.
- **Tier `a`/`c` (`f16`)**: Non-empty `Sent Items` empty-state message, accurate `Deleted Items` header count, `1180px` responsive rail collapse, and `selected` preserved on sort links.

## Interactive comparison

Open [`pegasus_shell_v41.html`](../../current/pegasus_shell_v41.html) at `?state=inbox&design=proposal` and toggle **Proposal** vs **Today** in the bottom-left Mockup controls strip.

See [../../current/v41-notes.md#6-sign-off-list](../../current/v41-notes.md#6-sign-off-list) for the lettered sign-off items.
