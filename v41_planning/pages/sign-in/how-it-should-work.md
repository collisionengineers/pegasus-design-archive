# Shared Shell, Auth, Consent, Error & Utility Pages: how it should work (v41 proposal)

## Proposed design, UI & UX improvements

- **Item A (`f01`)**: `#account-dialog` includes `Session started` (`dd MMM yyyy HH:mm`) in its `.kv` list, moves `Release notes`, `Report a problem`, and `Change password` into `.dialog-body`, and keeps only `Close` and `Sign out` in `.dialog-foot`.
- **Item B (`f04`)**: Pressing `Enter` inside `#global-search` submits directly to `/Search?query=...`; `Ctrl+K` / `Cmd+K` opens `#cmd-dialog`.
- **Item C (`f05`)**: Removes the duplicate static `Current · HH:MM` freshness stamp from `.utility-bar`.
- **Item D (`f07`)**: `/Connect/Authorize` removes the explanatory paragraph and raw `<code>` scope identifiers, and replaces `"intake"` with `"Inbox & Upload"` (`"Inspect and process Inbox messages, uploads, and Cases"`).
- **Item E (`f08`)**: `/Account/PasswordChange` removes the explanatory paragraph, adds `Show`/`Hide` reveal toggles on all 3 password inputs, uses a full-width `.btn--primary.btn--block` submit button, and in voluntary mode includes the `Account` eyebrow and `Cancel`.
- **Tier `a` (`f02`, `f03`, `f06`, `f09`)**: `Mark all read` in `#notifications-dialog` `.dialog-head`; canonical rail icons in `#cmd-dialog`; sentence-case defaults in `_ReasonDialog.cshtml`; `System` eyebrow on `/Error` and `/StatusCode`; `.btn--primary` on `Return to Work Centre`; no `.lede` on `/ReleaseNotes`.

## Interactive comparison

Open [`pegasus_shell_v41.html`](../../current/pegasus_shell_v41.html) at `?state=auth-signin&design=proposal` and toggle **Proposal** vs **Today** in the bottom-left Mockup controls strip.

See [../../current/v41-notes.md#6-sign-off-list](../../current/v41-notes.md#6-sign-off-list) for the lettered sign-off items.
