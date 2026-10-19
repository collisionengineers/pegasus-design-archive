# v41 discussion log

Chronological. Not design authority.

## 14 October 2026: the round is asked for

The operator invoked `/razor-html-mockup-creation` and `/razor-pages-ui-design` with the brief:

> *"Examine every single page on the app. See if there are any ways you can improve the design, UI, or UX"*
> *"Mockups only."*

## 14 October 2026: full-application audit and mockup build

Every routed Razor page, shared layout, dialog, partial, stylesheet, script, and label owner under `src/Pegasus.Web` on `origin/dev` was inspected across four audit lanes:

1. **Lane 1 — Shared Shell, Auth, Consent, Error, Utility, Work Centre & Search**:
   - Audited `_Layout.cshtml`, `_LayoutAuth.cshtml`, `_ShellDialogs.cshtml`, shared partials (`_PageHeader`, `_RefreshButton`, `_FreshnessBanner`, `_ErrorSummary`, `_StatusChip`, `_ReasonDialog`, `_ReleaseNoteBody`), `/Account/SignIn`, `/Account/SignOut`, `/Account/PasswordChange`, `/Account/AccessDenied`, `/Connect/Authorize`, `/Error`, `/StatusCode`, `/ReleaseNotes`, `/Notifications`, `/ProblemReports`, `/Index` (`_WorkCentreBody.cshtml`, `work-centre.css`, `work-centre.js`), `/Search` (`_CasePreview.cshtml`), `site.css`, and `site.js`.
   - Identified `f01`–`f14`, including:
     - `f01` (`#account-dialog` omitting `Session started` and crowding 5 buttons into `.dialog-foot`),
     - `f04` (`#global-search` intercepting `Enter` to open `#cmd-dialog` instead of submitting to `/Search`),
     - `f05` (duplicate `Current · HH:MM` freshness stamp in `.utility-bar`),
     - `f07` (`/Connect/Authorize` printing the banned word `"intake"`, raw `<code>mcp:intake</code>` identifiers, and an explanatory paragraph),
     - `f08` (`/Account/PasswordChange` explanatory paragraph, non-full-width submit button, missing `Show`/`Hide` toggles, and missing voluntary-mode `Account` eyebrow / `Cancel`),
     - `f10` (Work Centre `Assign Engineer` bug where clicking `Assign Engineer` on an unexpanded row opens `#wc-assign-dialog` for the wrong Case or does nothing),
     - `f11` (`work-centre.css` local overrides for `h1`, `.wc-switch a`, and `.wc-ledger-table th`),
     - `f13` & `f14` (`/Search` exposing a raw 36-char GUID text box for `Engineer`, free-text `Principal`/`Origin`, `State` instead of `Case stage`, duplicate `Create Case -> /Upload` button, missing `class="table"`, missing `Type`/`Due` columns, `Our ref` mislabelling `PrincipalReference`, missing `Copy Case/PO`, and hardcoded `Next action = "Not recorded"` past `Not ready`).

2. **Lane 2 — Inbox, Message Record, Upload, Cases Queue, Create Case, Triage, Unidentified & Vehicle Images**:
   - Audited `Mail/Index.cshtml`, `Mail/Message.cshtml`, `_MessageBody.cshtml`, `_MessageContent.cshtml`, `inbox.css`, `Upload.cshtml`, `UploadStatus.cshtml`, `UploadGroupStatus.cshtml`, `_UploadReview*.cshtml`, `upload.css`, `upload.js`, `Cases/Index.cshtml`, `cases-index.css`, `cases-index.js`, `Cases/Create.cshtml`, `_InstructionDraftFields.cshtml`, `_TriageCase.cshtml`, `_TriageDeterminationFields.cshtml`, `triage.css`, `Unidentified/Details.cshtml`, `ImageIntake/Details.cshtml`, `PreCaseImages/Index.cshtml`, `Cases/Chaser.cshtml`, `Cases/Custody.cshtml`, `Cases/Images.cshtml`, `Cases/Closure.cshtml`, `Cases/Workflow.cshtml`, `Cases/Vehicle.cshtml`, `Cases/Tasks.cshtml`, `Integrations/Glass/*`, `_EvidenceViewer.cshtml`, and `_ImageGallery.cshtml`.
   - Identified `f15`–`f25`, including:
     - `f15` (`/Inbox` duplicating `Sent Items` in both rail and `Folder` select, duplicating `No Case Found` in both rail and `Category` select, hiding `Deleted Items` inside `Folder`, and breaking the 5-column filter grid on `Dismissed`),
     - `f17` & `f18` (`/Inbox/{id}` repeating `Subject` 3 times and Case ref twice, forbidden `.provenance` tooltip icon, raw MIME types, missing reply `Cancel`, and the two-step server round-trip `PrepareUnlinkCase` / `PrepareLinkCase` that strands a Case edit lease if cancelled),
     - `f19` & `f20` (`/Upload` and `_UploadReview.cshtml` `.up-subtitle` and six `.up-explainer` paragraphs, reversed DOM vs visual column order on desktop, and `upload.js` double-submitting up to 200 MB on error),
     - `f21` (`/Cases` populating the `Principal` filter only from the 25 rows on the current page),
     - `f22` (`/Cases/Create` unwrapped `<details>` fields and internal `Extracted from InstructionPdfParser` string),
     - `f23` (Triage `#triage-link-case-dialog` asking for a raw 36-char `Case ID` GUID, raw RFC 5322 `InternetMessageIdentity` in `Exact response evidence`, and missing `Preview` on Triage `Documents`),
     - `f24` (`Unidentified` and `VehicleImages` duplicating ribbon facts in the first card, inline `<details>` table-cell form on `Unidentified`, `/VehicleImages/{id}` navigating away to `/Cases` instead of pairing in a dialog, and `#evidence-viewer` closing on every Crop/Tag POST).

3. **Lane 3 — Case Record Workspace (`/Cases/{id}`)**:
   - Audited `Cases/Details.cshtml`, all `Details*.cs` files, all 35 partials in `Cases/Shared/`, `case-workspace.css`, `case-workspace.js`, `CaseWorkspaceLabels.cs`, and `CaseNextAction.cs` against `.agents/skills/pegasus-ui-guardrails/references/case-workspace.md` and `FRD-16`.
   - Identified `f26`–`f30`, including:
     - `f26` (broken `#icon-check-square` sprite reference in `_CaseRibbon.cshtml` and `_CaseTasks.cshtml`, `.empty`/`.muted` vs `.empty-line`, hardcoded `title="Collapse section"` on collapsed panels, centered `[data-damage-reset]`, `"Not recorded"` masking suggested `To`/`Cc` in read mode, and blank `<option value="">` in `_CaseReport` and `_CaseOriginalReport`),
     - `f27` (Items `P` & `Q`: formal `v41` sign-off on Report Delivery `.fg`/`.fc` read/edit parity, visible `Yes`/`No` radio pills on undecided rule questions, inline `Done` hold tick, and one-step `"send"` wording),
     - `f28` (Item `R`: post-report open tasks in `.aside-card--action` styled as `.next-step-list` / `.next-step--item` row buttons matching pre-report blockers),
     - `f29` (Item `S`: `#case-tasks-dialog` `.fi` styling, `Unassigned` option, single-line `.cluster` row actions, and `#send-to-ai-dialog` `.fc` range+number pairing).

4. **Lane 4 — Administration Hub & 13 Sub-Areas**:
   - Audited `Administration/Index.cshtml`, `_AdminNav.cshtml`, `Accounts`, `Contacts`, `Configuration`, `Mailboxes`, `EmailTemplates`, `ValuationPresets`, `Health`, `Logs`, `Reports`, `ReleaseNotes`, `ProblemReports`, `AiJobs`, `Automation`, `admin.css`, `logs.css`, `accounts.js`, `contacts-edit.js`, and `email-templates.js`.
   - Identified `f31`–`f39`, including:
     - `f32` (Item `T`: `Accounts` rendering `Temporary password` outside `.admin-layout`, `"Manage this account's login."` restatement, bare `<dialog>` for Delete account, and raw `Generation`/`Version` in `#glass-credential-dialog`),
     - `f33` (Item `U`: `Contacts` `(optional)` suffixes, non-existent `.definition-list` on `Principal API`, bare `<dialog id="replace-principal">`, and missing `.hint` CSS rule for the 5 settled Report sending hints from `v40` S),
     - `f34` (Item `V`: `Configuration` missing `Administration` eyebrow, browser `<fieldset>` border, 6 `Minimum to Maximum` `.field-hint` spans, and Labour-rate right-alignment),
     - `f35` (Item `W`: `Mailboxes` rendering the obsolete editable `Mail categories` panel and `Add category` dialog contrary to `ADR-0069` / `FRD-20`, mixed dialog close buttons, and raw `LastFailureCode`),
     - `f36` (Item `X`: `Logs` rendering an internal cache telemetry `<details>` panel on `Action logs`),
     - `f38` (Item `Y`: `ProblemReports` printing a raw GUID in `When` and stacking two inline forms per row; `AiJobs` inline `<details>` confirm and plain-text Case ref; `Automation` `<label class="cluster">` vs `<label class="choice">`).

Built `pegasus_shell_v41.html` (18 states) and `pegasus_case_workspace_v41.html` (9 states) via `build-v41.py`, verified with `v41-selfcheck.html` and `check-v41.py`.

Open: items `A` to `Y` in [v41-notes.md](v41-notes.md#6-sign-off-list).

## 15 October 2026: the Inbox message dialog joins the round

The operator pointed at mockups in `../pegasus-worktrees/inbox-message-dialog`, drawn on 13 October from the brief *"We do not need a full page to view an email. This should be a dialogue box. We need a system to tag/alter emails in the same way as images at present."* They are six designs for opening a message as a dialog and tagging it. The operator asked for all six to come into this round as variants. They are now the Inbox Proposal (designs 1–6), rebuilt over the live Inbox in the next entry.

## 15 October 2026: one redesign, rebuilt over the live application

Requests that day, in order:
- Collapse the three identical mockup files into one, building off the current page state with the additions shown as a proposal.
- Run an improvement pass over v41.
- Drop the distinction between the two rounds and treat everything as one redesign.
- Improve on the message dialog proposals.
- Factor in PR 1331 (AI-drafted query replies, open).

An area-by-area review against the source found that most of the hand-drawn Today views were not the live pages. About 30 "today" claims were false or already fixed, and several proposals added unapproved sentences. The operator chose to rebase everything on live captures.

What changed:

- The mockup is one file, `pegasus_v41.html`. The two copies and the iframe self-check are gone.
- Every Today view is captured from the application. The excluded `ZzMockupCapture*` scratch tests seed data and save each page. The source is `dev` `b8124e3f0` with PR 1331 merged locally as `fb6d446ff` in `../pegasus-worktrees/v41-capture`, and nothing was pushed.
- Proposals are patches on those captures, one module per area. Each change has one ID, which is also its sign-off item. False findings were dropped, and invented copy and rules were removed (v41-notes §3).
- The Inbox dialog designs are part of this round. They are rebuilt on the live Inbox data and markup and improved: Previous/Next message, tag chips on every row, a Tag filter, the Case tab folded into Decision, Dismiss moving on, and the duplicate Classified chip removed. They carry PR 1331's AI draft in the record bar and the composer.
- Two glossary breaches seen in the live captures are raised: "Post-report" on the query record bar (I16), and "intake" in the consent and Unidentified copy (questions).

Open: the sign-off list in [v41-notes.md](v41-notes.md#5-sign-off).

## 15 October 2026: questions settled and the folder restructured

The operator settled the §5 questions, folded in #1213 and PERF-WEB-08/09, and asked for an
Administration pass; the rulings and the work are in [plan-2026-10-15.md](plan-2026-10-15.md).
The same day the readiness folder was restructured: `v41_planning/current/` became
`v41-redesign/` with the mockup at the top, the notes in `notes/`, the scripts and patch
modules in `build/`, the screenshots in `shots/`, and `captured-live/` and `pages/` beside
them. Nothing in the mockup changed.

## 2026-10-19: Stage 2 step 1, the 15 October plan applied to the mockup

Step 1 of `../../plans/v41-stage-2.md` ran against the 19 October capture (`dev` `365d83064`). Four lanes each edited their own files (Inbox; Case, Work Centre, Shell and Upload; Administration in two parts) and one integrator joined them. No tracked file was touched, and no build or test that CI runs was run.

Applied, from [plan-2026-10-15.md](plan-2026-10-15.md) §2 with the corrections in `plans/v41-stage-2.md`:

- The Inbox is one dialog on design 3's frame. Tags, the Tag filter, row chips, the preview and the six designs are gone (I3, I7, I8, I14 dropped; I4 now reads "the preview goes"). The right column holds the eleven Classification chips (one pressed, applied at once) and the Case / PO picker, with I9's buttons beneath. I18, row ticks and one bulk form, is new (R140 a).
- K6 to K8 and the two `case-query-view-*` states are gone. K5 (To from the capture's Sent evidence), K9 (a With Engineer Case with no Engineer, #1213) and K10 (Return to work on a closed Case, R157) are new, as is W8 (#1213 in the Work Centre).
- A14 to A28 and A30 are drawn; A29 is Stage 2 only. A6 keeps only the AI actor chip, because A24 removes the whole diagnostics panel. A5 has no patch: PR 1332 delivered it and the 19 October captures no longer hold the panel. W7 has none either: #1216 delivered it.
- Rulings applied: R41, R105 (no mileage line is drawn), R140, R156, R157, R158, R159, R160 and R161. The PERF-WEB-09 row of the plan now reads R42.
- 92 states became 104: twelve registered: the four new Inbox states (the fourth, `inbox-rows-ticked-busy`, added in the second review pass for I18's busy state), `contacts-create`, `accounts-glass-empty`, `logs-intake-drawer`, the two release-note states and the three Reports tab states.

Open: the sign-off list in [v41-notes.md](v41-notes.md#5-sign-off) (§5 now holds only what no ruling settled; §4 holds what was settled). The self-check record is in §6.
