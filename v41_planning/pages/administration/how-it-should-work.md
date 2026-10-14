# Administration Hub & All 13 Sub-Areas: how it should work (v41 proposal)

## Proposed design, UI & UX improvements

- **Item T (`f32` — Accounts)**: Moves `Temporary password` inside `.admin-main` at the top of the workspace, removes `"Manage this account's login."`, styles `#delete-account-dialog` with `.dialog`, and removes `Generation` and `Version` from `#glass-credential-dialog`.
- **Item U (`f33` — Contacts)**: Removes `Optional.` and `(optional)` suffixes, styles `Principal API` with `.kv` + `.chip`, styles `#replace-principal` with `.dialog`, and adds `.hint` CSS (`11px`, `--ink-3`) to `site.css`.
- **Item V (`f34` — Configuration)**: Adds the `Administration` eyebrow, resets `fieldset` borders, removes the six `Minimum to Maximum` `.field-hint` lines, and right-aligns Labour-rate inputs and `Save`.
- **Item W (`f35` — Mailboxes)**: Removes the obsolete editable `Mail categories` panel and `Add category` dialog, standardizes dialog close buttons, and maps `LastFailureCode` to human labels.
- **Item X (`f36` — Logs)**: Removes the internal cache telemetry `<details>` panel from `Logs.cshtml` and uses `.chip.chip--Accent` on `AI`.
- **Item Y (`f38` — ProblemReports, AiJobs, Automation)**: Removes the raw GUID from `ProblemReports` `When` and replaces stacked inline forms with `#problem-report-dialog`; links `Case` references on `AiJobs` and moves `Stop` confirmation to `#stop-ai-job-dialog`; uses `<label class="choice">` on `Automation`.
- **Tier `a` (`f31`, `f37`, `f39`)**: Hub `#icon-bot` and `Configuration` description, `AdminAutomationComposed` in `AdministrationPageModel`, `Edit` link column on `ReleaseNotes`, and `Reports` lede/fieldset cleanup.

## Interactive comparison

Open [`pegasus_shell_v41.html`](../../current/pegasus_shell_v41.html) at `?state=admin-accounts&design=proposal` and toggle **Proposal** vs **Today** in the bottom-left Mockup controls strip.

See [../../current/v41-notes.md#6-sign-off-list](../../current/v41-notes.md#6-sign-off-list) for the lettered sign-off items.
