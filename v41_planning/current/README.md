# v41 current: Full-Application UI, UX & Design Review

A temporary design review artifact created at operator request on 14 October 2026 (`"Examine every single page on the app. See if there are any ways you can improve the design, UI, or UX"` — `"Mockups only."`). It is not application code, not design authority, and not implementation evidence. The sign-off list in [v41-notes.md](v41-notes.md#6-sign-off-list) decides what Stage 2 changes.

## What this is

Every routed page, shared layout, dialog, partial, stylesheet, and client script in `src/Pegasus.Web` on `origin/dev` was audited line by line across four lanes:

1. **Shared Shell, Auth, Consent, Error, Utility, Work Centre & Search** (`_Layout.cshtml`, `_LayoutAuth.cshtml`, `_ShellDialogs.cshtml`, `/Account/*`, `/Connect/Authorize`, `/Error`, `/StatusCode`, `/ReleaseNotes`, `/Notifications`, `/ProblemReports`, `/Index`, `/Search`)
2. **Inbox, Message Record, Upload, Cases Queue, Create Case, Triage, Unidentified & Vehicle Images** (`/Inbox`, `/Inbox/{id}`, `/Upload`, `/Upload/Group/{id}`, `/Cases`, `/Cases/Create`, `/Cases/{id}` Triage, `/Unidentified/{id}`, `/VehicleImages/{id}`, `/PreCaseImages`, `/Cases/{id}/Chaser`, `/Integrations/Glass/*`)
3. **Case Record Workspace** (`/Cases/{id}`, all 10 workspace sections, sticky ribbon, aside column, and all Case dialogs)
4. **Administration Hub & 13 Sub-Areas** (`/Administration`, `Accounts`, `Contacts`, `Configuration`, `Mailboxes`, `EmailTemplates`, `ValuationPresets`, `Health`, `Logs`, `Reports`, `ReleaseNotes`, `ProblemReports`, `AiJobs`, `Automation`)

Unified self-contained offline HTML mockups (`pegasus_v41.html`, `pegasus_shell_v41.html`, and `pegasus_case_workspace_v41.html`) render the entire application (`27` states across all `4` lanes) in a single interactive SPA with a live `Proposal` vs `Today (origin/dev)` toggle, inline `f01`–`f39` diff callouts, a state selector, and a `36px` / `40px` height ruler. All live CSS (`site.css`, `work-centre.css`, `inbox.css`, `upload.css`, `cases-index.css`, `triage.css`, `unidentified.css`, `image-record.css`, `pre-case-images.css`, `admin.css`, `logs.css`, `case-workspace.css`), Inter variable font, Lucide SVG icon sprite, and mark PNG are inlined directly from `src/Pegasus.Web/wwwroot`. Every left-rail link, Administration sub-nav link, Case link, table row, filter input, tab strip, inline expansion, slider, and modal dialog works interactively in-place without page reloads.

Open `pegasus_v41.html` in a browser. Add `?state=<key>&mode=proposal|today` for any state; use **Mockup controls** (bottom left) to switch states, toggle `Proposal` vs `Today`, show or hide `Diff` callouts, or toggle the `36px` / `40px` ruler. Append `&strip=0` to hide the control strip.

## Files

| File | What it is |
| --- | --- |
| `pegasus_v41.html` | **Unified full interactive application mockup** combining all `27` states across all `4` lanes (`work-centre` default), in-place SPA navigation across every left-rail / Administration / Case route, live modal `<dialog>` overlay (`account-dialog`, `notifications-dialog`, `cmd-dialog`, `whats-new-dialog`, `report-problem-dialog`, `wc-assign-dialog`, `unlinkCaseDialog`, `problem-report-dialog`, `stop-ai-job-dialog`, `new-mailbox-dialog`, `replace-principal`, `preview-media`), live table filtering & row selection previews, Principal/Triage/Upload/Case tab switching, and Case Workspace `Edit` ↔ `Done editing` / `Scroll` ↔ `Tabs` / section collapse / slider sync / interactive tasks. |
| `pegasus_shell_v41.html` | Same unified `27`-state interactive mockup defaulting to `auth-signin`. |
| `pegasus_case_workspace_v41.html` | Same unified `27`-state interactive mockup defaulting to `v41-overview` (Case Record Workspace `/Cases/91042`). |
| `build-v41.py` | Builds the self-contained interactive offline HTML mockups from `src/Pegasus.Web/wwwroot` assets and captured Case frames. |
| `v41-selfcheck.html` | Scripted browser self-check asserting every state, `Proposal` vs `Today` toggle, and `f01`–`f38` / `A`–`Y` invariant across both mockups, ending `RESULT {"fail":[],"okCount":N}`. |
| `check-v41.py` | Runs `v41-selfcheck.html` in headless Chromium (`--allow-file-access-from-files`) and captures screenshots at `1580×1000`, `1440×900`, and `760×1000` (plus `1580` whole-page captures) into `v41-shots/` with `verification.json`. |
| `v41-shots/` | Viewport and whole-page screenshots across all states and `verification.json`. |
| `v41-notes.md` | Full audit report: findings `f01`–`f39` by surface with exact file + line citations, Tier classification (`a` polish, `b` sign-off decision, `c` JS/interaction), lettered operator sign-off list (`A`–`Y`), self-check result, and Stage 2 implementation plan. |
| `discussion-log.md` | Chronological log of the v41 design review round. |

## Status

**Stage 1 complete — awaiting operator sign-off on items `A` to `Y` in [v41-notes.md](v41-notes.md#6-sign-off-list).** No files under `src/Pegasus.Web`, `src/Pegasus.Core`, `src/Pegasus.Infrastructure`, or `tests/` have been modified.
