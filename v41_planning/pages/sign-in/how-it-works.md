# Shared Shell, Auth, Consent, Error & Utility Pages: how it works today (`origin/dev`)

## Source files

- `src/Pegasus.Web/Pages/Shared/_Layout.cshtml`, `_LayoutAuth.cshtml`, `_ShellDialogs.cshtml`, `_PageHeader.cshtml`, `_RefreshButton.cshtml`, `_FreshnessBanner.cshtml`, `_ErrorSummary.cshtml`, `_StatusChip.cshtml`, `_ReasonDialog.cshtml`, `_ReleaseNoteBody.cshtml`
- `src/Pegasus.Web/Pages/Account/SignIn.cshtml` (`.cs`), `SignOut.cshtml` (`.cs`), `PasswordChange.cshtml` (`.cs`), `AccessDenied.cshtml` (`.cs`)
- `src/Pegasus.Web/Pages/Connect/Authorize.cshtml` (`.cs`)
- `src/Pegasus.Web/Pages/Error.cshtml` (`.cs`), `StatusCode.cshtml` (`.cs`), `ReleaseNotes.cshtml` (`.cs`), `Notifications.cshtml` (`.cs`), `ProblemReports.cshtml` (`.cs`)
- `src/Pegasus.Web/wwwroot/css/site.css` and `src/Pegasus.Web/wwwroot/js/site.js`

## Current behaviour and audit findings

- `_Layout.cshtml` renders the 5-destination left rail (`Work Centre`, `Search`, `Inbox`, `Cases`, `Administration`), primary `Create Case` CTA (`-> /Upload`), theme switcher, notification bell, account dialog button, and `.utility-bar` containing a static `<span class="utility-freshness">Current · HH:MM</span>` and `#global-search`.
- Pressing `Enter` inside `#global-search` is intercepted by `site.js:2051` to open `#cmd-dialog` instead of submitting to `/Search`.
- `#account-dialog` (`_ShellDialogs.cshtml:38-68`) shows `Name`, `Username`, and `Role` (omitting `Session started`) and crowds 5 buttons into `.dialog-foot`.
- `#notifications-dialog` places `Mark all read` in `.dialog-foot` instead of `.dialog-head`.
- `#cmd-dialog` uses `#icon-list`, `#icon-folder-open`, and `#icon-layout-grid` instead of `#icon-list-checks`, `#icon-search`, and `#icon-settings`.
- `/Connect/Authorize` prints an explanatory paragraph, uses the banned internal word `"intake"` twice in UI copy, and exposes raw `<code>mcp:intake</code>` / `<code>offline_access</code>` identifiers.
- `/Account/PasswordChange` includes an explanatory paragraph in forced mode, wraps its submit button in `.button-row` instead of `.btn--block`, omits `Show`/`Hide` password reveal buttons, and in voluntary mode omits the `Account` eyebrow and `Cancel` link.

See [../../current/v41-notes.md](../../current/v41-notes.md) for the complete `f01`–`f39` table and exact file/line citations.
