# Administration Hub & All 13 Sub-Areas: how it works today (`origin/dev`)

## Source files

- `src/Pegasus.Web/Pages/Administration/Index.cshtml` (`.cs`), `Shared/_AdminNav.cshtml`, `AdministrationPageModel.cs`
- `src/Pegasus.Web/Pages/Administration/Accounts/Index.cshtml` (`.cs`), `Contacts/Index.cshtml` (`.cs`), `Contacts/Edit.cshtml` (`.cs`)
- `src/Pegasus.Web/Pages/Administration/Configuration.cshtml` (`.cs`), `Mailboxes.cshtml` (`.cs`), `EmailTemplates/Index.cshtml` (`.cs`), `ValuationPresets/Index.cshtml` (`.cs`)
- `src/Pegasus.Web/Pages/Administration/Health.cshtml` (`.cs`), `Logs.cshtml` (`.cs`), `Reports.cshtml` (`.cs`), `ReleaseNotes/Index.cshtml` (`.cs`), `ReleaseNotes/Edit.cshtml` (`.cs`), `ProblemReports.cshtml` (`.cs`), `AiJobs.cshtml` (`.cs`), `Automation/Index.cshtml` (`.cs`)
- `src/Pegasus.Web/wwwroot/css/admin.css`, `logs.css`

## Current behaviour and audit findings

- `/Administration` hub uses `#icon-sparkles` on `Automation & AI` (while `_AdminNav` uses `#icon-bot`), describes `Configuration` as `"View the current workflow policy."`, and `ReleaseNotes`/`Health` omit `ViewData["AdminAutomationComposed"]`.
- `/Administration/Accounts` renders the `Temporary password` panel outside `.admin-layout` at the bottom of the page, includes `"Manage this account's login."`, uses a bare unstyled `<dialog>` for `Delete account`, and exposes raw `Generation` and `Version` columns in `#glass-credential-dialog`.
- `/Administration/Contacts` includes `Optional.` and `(optional)` suffixes, uses non-existent `.definition-list` on `Principal API`, uses a bare `<dialog id="replace-principal">`, and lacks `.hint` CSS in `site.css` for the 5 settled Report sending hints (`v40` S).
- `/Administration/Configuration` lacks the `Administration` eyebrow, draws a browser `<fieldset>` border around workflow settings, renders six `Minimum to Maximum` `.field-hint` lines, and left-aligns Labour-rate card inputs/buttons.
- `/Administration/Mailboxes` renders an obsolete editable `Mail categories` panel and `Add category` dialog (contrary to `ADR-0069` / `FRD-20`), mixes 3 dialog close-button patterns, and prints raw `LastFailureCode`.
- `/Administration/Logs` exposes an internal memory-cache byte/hit-miss telemetry `<details>` panel on `Action logs` and uses legacy `status-chip`.
- `/Administration/ReleaseNotes` has no `Edit` action column; `/Administration/ProblemReports` prints a raw GUID in `When` and stacks two inline forms in `Actions`; `/Administration/AiJobs` uses plain-text Case references and an inline `<details>` confirm; `/Administration/Automation` uses `<label class="cluster">` instead of `<label class="choice">`.

See [../../current/v41-notes.md](../../current/v41-notes.md) for the complete `f01`–`f39` table and exact file/line citations.
