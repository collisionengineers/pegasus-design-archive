# v41 pages index

One folder per application surface audited in the v41 full-application UI, UX, and design review round (14 October 2026). See [../current/v41-notes.md](../current/v41-notes.md) for the consolidated `f01`–`f39` catalogue and lettered sign-off list (`A`–`Y`).

| Folder | Surface | Routes | Mockup & state |
| --- | --- | --- | --- |
| [sign-in/](sign-in/README.md) | Shared Shell, Auth, Consent, Error & Utility Pages | `/Account/SignIn`, `/Account/SignOut`, `/Account/PasswordChange`, `/Account/AccessDenied`, `/Connect/Authorize`, `/Error`, `/StatusCode`, `/ReleaseNotes`, `/Notifications`, `/ProblemReports`, plus shared shell `_Layout.cshtml` & `_ShellDialogs.cshtml` | [pegasus_shell_v41.html](../current/pegasus_shell_v41.html) (`?state=auth-signin`) |
| [work-centre/](work-centre/README.md) | Work Centre | `/` (`/Index`) | [pegasus_shell_v41.html](../current/pegasus_shell_v41.html) (`?state=work-centre`) |
| [search/](search/README.md) | Search | `/Search` | [pegasus_shell_v41.html](../current/pegasus_shell_v41.html) (`?state=search`) |
| [inbox/](inbox/README.md) | Inbox & Message Record | `/Inbox` and `/Inbox/{id:guid}` | [pegasus_shell_v41.html](../current/pegasus_shell_v41.html) (`?state=inbox`) |
| [upload/](upload/README.md) | Upload & Upload Review | `/Upload`, `/Upload/{id:guid}`, and `/Upload/Group/{id:guid}` | [pegasus_shell_v41.html](../current/pegasus_shell_v41.html) (`?state=upload-review`) |
| [cases/](cases/README.md) | Cases Queue & Create Case | `/Cases` and `/Cases/Create` | [pegasus_shell_v41.html](../current/pegasus_shell_v41.html) (`?state=cases-queue`) |
| [triage/](triage/README.md) | Triage Case Workspace | `/Cases/{id:guid}` (when `Type == Triage`) | [pegasus_shell_v41.html](../current/pegasus_shell_v41.html) (`?state=triage-case`) |
| [unidentified/](unidentified/README.md) | Unidentified, Vehicle Images, Pre-Case Images & Auxiliary Case Routes | `/Unidentified/{id:guid}`, `/VehicleImages/{id:guid}`, `/PreCaseImages`, `/Cases/{id}/Chaser`, `/Integrations/Glass/*` | [pegasus_shell_v41.html](../current/pegasus_shell_v41.html) (`?state=unidentified-images`) |
| [case/](case/README.md) | Case Record Workspace | `/Cases/{id:guid}` | [pegasus_case_workspace_v41.html](../current/pegasus_case_workspace_v41.html) (`?state=v41-overview`) |
| [administration/](administration/README.md) | Administration Hub & All 13 Sub-Areas | `/Administration`, `/Administration/Accounts`, `/Administration/Contacts`, `/Administration/Contacts/{id}`, `/Administration/Configuration`, `/Administration/Mailboxes`, `/Administration/EmailTemplates`, `/Administration/ValuationPresets`, `/Administration/Health`, `/Administration/Logs`, `/Administration/Reports`, `/Administration/ReleaseNotes`, `/Administration/ProblemReports`, `/Administration/AiJobs`, `/Administration/Automation` | [pegasus_shell_v41.html](../current/pegasus_shell_v41.html) (`?state=admin-accounts`) |
