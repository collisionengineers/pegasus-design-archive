"""Generate v41_planning/pages/ documentation folders for all 10 application surfaces."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "pages"

SURFACE_SPECS = [
    {
        "slug": "sign-in",
        "title": "Shared Shell, Auth, Consent, Error & Utility Pages",
        "routes": "`/Account/SignIn`, `/Account/SignOut`, `/Account/PasswordChange`, `/Account/AccessDenied`, `/Connect/Authorize`, `/Error`, `/StatusCode`, `/ReleaseNotes`, `/Notifications`, `/ProblemReports`, plus shared shell `_Layout.cshtml` & `_ShellDialogs.cshtml`",
        "frds": "[FRD-04](../../../pegasus/docs/frd/frd-04-parties-accounts-and-access.md) and [FRD-12](../../../pegasus/docs/frd/frd-12-operator-experience.md)",
        "mock": "pegasus_shell_v41.html",
        "state": "auth-signin",
        "shots": [
            ("Sign-in & Password Change (proposal)", "01-auth-signin"),
            ("OAuth Consent (proposal)", "02-auth-consent"),
            ("OAuth Consent (today)", "03-auth-consent-today"),
            ("Error, Status Code & Release Notes (proposal)", "04-auth-errors"),
            ("Shell Dialogs & Utility Bar (proposal)", "05-shell-dialogs"),
        ],
        "files_web": [
            "`src/Pegasus.Web/Pages/Shared/_Layout.cshtml`, `_LayoutAuth.cshtml`, `_ShellDialogs.cshtml`, `_PageHeader.cshtml`, `_RefreshButton.cshtml`, `_FreshnessBanner.cshtml`, `_ErrorSummary.cshtml`, `_StatusChip.cshtml`, `_ReasonDialog.cshtml`, `_ReleaseNoteBody.cshtml`",
            "`src/Pegasus.Web/Pages/Account/SignIn.cshtml` (`.cs`), `SignOut.cshtml` (`.cs`), `PasswordChange.cshtml` (`.cs`), `AccessDenied.cshtml` (`.cs`)",
            "`src/Pegasus.Web/Pages/Connect/Authorize.cshtml` (`.cs`)",
            "`src/Pegasus.Web/Pages/Error.cshtml` (`.cs`), `StatusCode.cshtml` (`.cs`), `ReleaseNotes.cshtml` (`.cs`), `Notifications.cshtml` (`.cs`), `ProblemReports.cshtml` (`.cs`)",
            "`src/Pegasus.Web/wwwroot/css/site.css` and `src/Pegasus.Web/wwwroot/js/site.js`",
        ],
        "today_summary": """- `_Layout.cshtml` renders the 5-destination left rail (`Work Centre`, `Search`, `Inbox`, `Cases`, `Administration`), primary `Create Case` CTA (`-> /Upload`), theme switcher, notification bell, account dialog button, and `.utility-bar` containing a static `<span class="utility-freshness">Current · HH:MM</span>` and `#global-search`.
- Pressing `Enter` inside `#global-search` is intercepted by `site.js:2051` to open `#cmd-dialog` instead of submitting to `/Search`.
- `#account-dialog` (`_ShellDialogs.cshtml:38-68`) shows `Name`, `Username`, and `Role` (omitting `Session started`) and crowds 5 buttons into `.dialog-foot`.
- `#notifications-dialog` places `Mark all read` in `.dialog-foot` instead of `.dialog-head`.
- `#cmd-dialog` uses `#icon-list`, `#icon-folder-open`, and `#icon-layout-grid` instead of `#icon-list-checks`, `#icon-search`, and `#icon-settings`.
- `/Connect/Authorize` prints an explanatory paragraph, uses the banned internal word `"intake"` twice in UI copy, and exposes raw `<code>mcp:intake</code>` / `<code>offline_access</code>` identifiers.
- `/Account/PasswordChange` includes an explanatory paragraph in forced mode, wraps its submit button in `.button-row` instead of `.btn--block`, omits `Show`/`Hide` password reveal buttons, and in voluntary mode omits the `Account` eyebrow and `Cancel` link.""",
        "proposal_summary": """- **Item A (`f01`)**: `#account-dialog` includes `Session started` (`dd MMM yyyy HH:mm`) in its `.kv` list, moves `Release notes`, `Report a problem`, and `Change password` into `.dialog-body`, and keeps only `Close` and `Sign out` in `.dialog-foot`.
- **Item B (`f04`)**: Pressing `Enter` inside `#global-search` submits directly to `/Search?query=...`; `Ctrl+K` / `Cmd+K` opens `#cmd-dialog`.
- **Item C (`f05`)**: Removes the duplicate static `Current · HH:MM` freshness stamp from `.utility-bar`.
- **Item D (`f07`)**: `/Connect/Authorize` removes the explanatory paragraph and raw `<code>` scope identifiers, and replaces `"intake"` with `"Inbox & Upload"` (`"Inspect and process Inbox messages, uploads, and Cases"`).
- **Item E (`f08`)**: `/Account/PasswordChange` removes the explanatory paragraph, adds `Show`/`Hide` reveal toggles on all 3 password inputs, uses a full-width `.btn--primary.btn--block` submit button, and in voluntary mode includes the `Account` eyebrow and `Cancel`.
- **Tier `a` (`f02`, `f03`, `f06`, `f09`)**: `Mark all read` in `#notifications-dialog` `.dialog-head`; canonical rail icons in `#cmd-dialog`; sentence-case defaults in `_ReasonDialog.cshtml`; `System` eyebrow on `/Error` and `/StatusCode`; `.btn--primary` on `Return to Work Centre`; no `.lede` on `/ReleaseNotes`.""",
        "states": [
            ("`auth-signin`", "`SignIn`, forced `PasswordChange`, voluntary `PasswordChange`, `SignOut`, `AccessDenied`"),
            ("`auth-consent`", "OAuth `/Connect/Authorize` consent screen (`Proposal` vs `Today`)"),
            ("`auth-errors`", "`/Error`, `/StatusCode`, `/ReleaseNotes`, `/Notifications`, `/ProblemReports`"),
            ("`shell-dialogs`", "`#account-dialog`, `#notifications-dialog`, `#cmd-dialog`, `#report-problem-dialog`, `#global-search`"),
        ],
        "panels": [
            ("`.auth-card`", "`400px` centered card on `_LayoutAuth.cshtml` for Sign-in, Password change, Sign-out, Access denied, and StatusCode"),
            ("`.consent-card`", "`480px` centered card on `_LayoutAuth.cshtml` for OAuth `/Connect/Authorize`"),
        ],
        "dialogs": [
            ("`#account-dialog`", "Operator session details (`Name`, `Username`, `Role`, `Session started`), links (`Release notes`, `Report a problem`, `Change password`), and `Close` / `Sign out`"),
            ("`#notifications-dialog`", "Unread and recent notifications with `Mark all read` in `.dialog-head`"),
            ("`#cmd-dialog`", "Quick jump palette (`Ctrl+K` / `Cmd+K`)"),
            ("`#report-problem-dialog`", "Operator problem report modal"),
        ],
    },
    {
        "slug": "work-centre",
        "title": "Work Centre",
        "routes": "`/` (`/Index`)",
        "frds": "[FRD-12](../../../pegasus/docs/frd/frd-12-operator-experience.md) and [FRD-15](../../../pegasus/docs/frd/frd-15-work-centre-queues-and-search.md)",
        "mock": "pegasus_shell_v41.html",
        "state": "work-centre",
        "shots": [
            ("Work Centre — Unassigned & Assign Engineer fix (proposal)", "06-work-centre"),
            ("Work Centre — New cases & AI jobs tabs (proposal)", "07-work-centre-tabs"),
        ],
        "files_web": [
            "`src/Pegasus.Web/Pages/Index.cshtml` (`.cs`) and `src/Pegasus.Web/Pages/_WorkCentreBody.cshtml`",
            "`src/Pegasus.Web/wwwroot/css/work-centre.css` and `src/Pegasus.Web/wwwroot/js/work-centre.js`",
        ],
        "today_summary": """- Renders the single-table Work Centre ledger switching between `Assigned to me`, `Unassigned`, `New cases`, and `AI jobs`.
- **Critical bug (`f10`)**: `_WorkCentreBody.cshtml:335, 427` and `Index.cshtml.cs:594` only populate `#wc-assign-dialog` when `Model.SelectedCaseForAssignment` is non-null (requiring a row to be expanded via `Selected`). Every unexpanded row in `Unassigned` still renders `<button data-dialog-open="wc-assign-dialog">Assign Engineer</button>`, so clicking `Assign Engineer` on an unexpanded row either does nothing or opens the dialog pre-filled for the **wrong Case** (whichever other row is expanded).
- `work-centre.css:5, 56, 70` overrides `.page-header h1` to `25px` (instead of `20px`), `.wc-switch a` to `28px`/`2px` radius (instead of `32px`/`4px` inside `36px` `.seg`), and `.wc-ledger-table th` to `9px` non-sticky (instead of `11px` `34px` sticky).
- `.wc-find` omits hidden `since` (`DividerUtc`), `Dismiss` does a full page reload, and `selected` leaks into `New cases` / `AI jobs`.""",
        "proposal_summary": """- **`f10` (Bug fix)**: Always renders `#wc-assign-dialog` and binds each row's `Assign Engineer` button (`data-case-id`, `data-case-ref`, `data-current-assignee`) so clicking `Assign Engineer` on any row opens the dialog for that exact Case.
- **`f11` (Token alignment)**: Removes local overrides in `work-centre.css` so Work Centre uses the canonical `20px` `h1`, `36px` `.seg` (`4px` inner radius), `11px` `34px` sticky table headers, and `6px` `--r-md` radius.
- **`f12` (Interaction)**: Adds `data-row-list` keyboard navigation, includes `<input type="hidden" name="since" />` in `.wc-find`, refreshes `Dismiss` via `[data-wc-Refresh]`, and clears `selected` when switching to `New cases` or `AI jobs`.""",
        "states": [
            ("`work-centre`", "`Unassigned` tab with inline row expansion and `#wc-assign-dialog` bound to the clicked row (`f10`, `f11`, `f12`)"),
            ("`work-centre-tabs`", "`New cases` (with `New` session divider) and `AI jobs` ledger tabs"),
        ],
        "panels": [
            ("`.wc-ledger`", "Single-table ledger with sticky `34px` header and inline `.wc-expand-row` detail drawer"),
        ],
        "dialogs": [
            ("`#wc-assign-dialog`", "Modal dialog to assign or change the Engineer on any Case row (`f10`)"),
        ],
    },
    {
        "slug": "search",
        "title": "Search",
        "routes": "`/Search`",
        "frds": "[FRD-15](../../../pegasus/docs/frd/frd-15-work-centre-queues-and-search.md#search)",
        "mock": "pegasus_shell_v41.html",
        "state": "search",
        "shots": [
            ("Search (proposal)", "08-search"),
            ("Search (today)", "09-search-today"),
        ],
        "files_web": [
            "`src/Pegasus.Web/Pages/Search/Index.cshtml` (`.cs`) and `src/Pegasus.Web/Pages/Search/_CasePreview.cshtml`",
        ],
        "today_summary": """- `Search/Index.cshtml:58-63` renders `Engineer` as a raw 36-character GUID text box (`placeholder="Account ID"`), and `Principal` (`lines 86-90`) and `Origin` (`lines 103-107`) as free-text inputs.
- Labels the stage filter `State` instead of `Case stage` (`CONTEXT.md:189`) and collapses `More filters` on reload even when secondary filters have active values.
- `.page-header` includes a duplicate `Create Case` button (`href="/Upload"`).
- Results and Preview Documents tables omit `class="table"`; Results omits `Type` and `Due` columns (`FRD-15:436`).
- `_CasePreview.cshtml:29` labels `PrincipalReference` as `Our ref` instead of `Claim ref`, omits `Copy Case/PO` (`FRD-15:440`), and hardcodes `Next action` to `"Not recorded"` for every Case past `Not ready`.""",
        "proposal_summary": """- **Item F (`f13`)**: Replaces the raw GUID text box for `Engineer` and free-text inputs for `Principal` and `Origin` with `<select>` dropdowns, renames `State` to `Case stage`, and keeps `More filters` open whenever any secondary filter is active.
- **Item G (`f14`)**: Removes the duplicate `Create Case` button from `.page-header`, adds `class="table"` and the `Type` and `Due` columns to Results, relabels `PrincipalReference` to `Claim ref` in `_CasePreview.cshtml`, adds `Copy Case/PO`, and computes `Next action` via `CaseNextAction` across all stages.""",
        "states": [
            ("`search`", "Search filter bar, 7-column `.table` results list (`Case`, `Reg`, `Principal`, `Type`, `Stage`, `Engineer`, `Due`), and right-hand `Selected Case` preview pane (`Proposal` vs `Today`)"),
        ],
        "panels": [
            ("`.compact-search`", "Primary search bar (`Search`, `Case stage`, `Engineer`) + collapsible `More filters` (`Principal`, `Type`, `Origin`, `From`, `To`, `Include closed`)"),
            ("`#case-search-preview`", "Right-hand `Selected Case` preview pane (`440px`)"),
        ],
        "dialogs": [],
    },
    {
        "slug": "inbox",
        "title": "Inbox & Message Record",
        "routes": "`/Inbox` and `/Inbox/{id:guid}`",
        "frds": "[FRD-20](../../../pegasus/docs/frd/frd-20-mailbox-workspace.md)",
        "mock": "pegasus_shell_v41.html",
        "state": "inbox",
        "shots": [
            ("Inbox 3-pane workspace (proposal)", "10-inbox"),
            ("Inbox 3-pane workspace (today)", "11-inbox-today"),
            ("Message Record `/Inbox/{id}` (proposal)", "12-mail-message"),
        ],
        "files_web": [
            "`src/Pegasus.Web/Pages/Mail/Index.cshtml` (`.cs`), `Message.cshtml` (`.cs`), `Shared/_MessageBody.cshtml`, `Shared/_MessageContent.cshtml`",
            "`src/Pegasus.Web/wwwroot/css/inbox.css`",
        ],
        "today_summary": """- `/Inbox` (`Mail/Index.cshtml:47-105`) puts `Sent Items` in both the left scope rail AND the `Folder` dropdown, puts `No Case Found` in both the left scope rail AND the `Category` dropdown, puts `Deleted Items` only inside `Folder`, and breaks the 5-column `.inbox-filter` grid when `Dismissed` hides `Folder`.
- Empty `Sent Items` renders an empty `<div class="empty"></div>`; `Deleted Items` header always says `0 messages`; `.inbox-layout.pane-layout--3` stays 3 columns down to `761px`.
- `/Inbox/{id}` (`Mail/Message.cshtml`) prints `Subject` 3 times vertically, prints the linked Case reference twice in `Decision` (`Destination` and `Filed to`), uses a forbidden `.provenance` tooltip icon, prints raw MIME strings (`application/pdf`) in `Attachments`, lacks a `Cancel` link on the inline reply composer, and requires a two-step server round-trip (`PrepareUnlinkCase` / `PrepareLinkCase`) that acquires a Case edit lease on the first click, reloads the page, and requires a second click to open `#unlinkCaseDialog` / `#linkCaseDialog`.""",
        "proposal_summary": """- **Item H (`f15`)**: Consolidates all 5 mailbox scopes in the left scope rail (`All incoming`, `No Case Found`, `Sent Items`, `Dismissed`, `Deleted Items`) and uses a consistent 3-column filter bar (`Mailbox`, `Category`, `Search`).
- **Item I (`f17`)**: Shows `Subject` once in `.page-header h1`, merges `Destination`/`Filed to` into a single `Case` row in `Decision`, replaces `.provenance` tooltip with plain text, shows human file types (`PDF document`, `Word document`) + size in `Attachments`, and adds `Cancel` to the inline reply composer.
- **Item J (`f18`)**: Opens `#unlinkCaseDialog` and `#linkCaseDialog` directly on click (`data-dialog-open`) and acquires/consumes the Case lease in the single confirmation POST.
- **Tier `a`/`c` (`f16`)**: Non-empty `Sent Items` empty-state message, accurate `Deleted Items` header count, `1180px` responsive rail collapse, and `selected` preserved on sort links.""",
        "states": [
            ("`inbox`", "3-pane `/Inbox` workspace (`Proposal` vs `Today`)"),
            ("`mail-message`", "Full `/Inbox/{id}` Message Record with single-home facts, inline reply composer, and direct Link/Unlink Case dialogs (`Proposal` vs `Today`)"),
        ],
        "panels": [
            ("`.inbox-layout`", "Left scope rail (`212px`), middle message list, and right reading pane (`460px`)"),
            ("`.record`", "2-column `/Inbox/{id}` message record (`1fr` message + attachments, `360px` Decision card)"),
        ],
        "dialogs": [
            ("`#linkCaseDialog`", "Direct modal dialog to link or change the linked Case (`f18`)"),
            ("`#unlinkCaseDialog`", "Direct modal dialog to unlink a message from its Case with a reason (`f18`)"),
        ],
    },
    {
        "slug": "upload",
        "title": "Upload & Upload Review",
        "routes": "`/Upload`, `/Upload/{id:guid}`, and `/Upload/Group/{id:guid}`",
        "frds": "[FRD-18](../../../pegasus/docs/frd/frd-18-manual-upload.md)",
        "mock": "pegasus_shell_v41.html",
        "state": "upload-review",
        "shots": [
            ("Upload & Upload Review (proposal)", "13-upload-review"),
        ],
        "files_web": [
            "`src/Pegasus.Web/Pages/Upload.cshtml` (`.cs`), `UploadStatus.cshtml` (`.cs`), `UploadGroupStatus.cshtml` (`.cs`), `UploadConfirmationPageModel.cs`",
            "`src/Pegasus.Web/Pages/Shared/_UploadReview.cshtml`, `_UploadDestinationCard.cshtml`, `_UploadReviewCandidate.cshtml`, `_UploadReviewLeave.cshtml`, `_UploadReviewRecord.cshtml`",
            "`src/Pegasus.Web/wwwroot/css/upload.css` and `src/Pegasus.Web/wwwroot/js/upload.js`",
        ],
        "today_summary": """- `Upload.cshtml:21` omits `.eyebrow` (`Files`) in `.page-header`.
- `_UploadReview.cshtml:39, 77, 88, 101, 110, 146, 234` renders a `.up-subtitle` lede and six `.up-explainer` narration paragraphs violating *No explanatory copy*.
- `_UploadReview.cshtml:55, 249` places `.up-decision` before `.up-inspector` in the DOM while `upload.css:17-18` swaps them visually on desktop (`>900px`), reversing keyboard `Tab` order.
- `upload.js:276` calls `form.submit()` in the XHR `.catch()` handler on HTTP 400/500, re-uploading up to 200 MB a second time; and `Find another Case` resets `inspect` to `0`.""",
        "proposal_summary": """- **Item K (`f19`)**: Adds the `Files` eyebrow to `Upload.cshtml` and removes `.up-subtitle` and all six `.up-explainer` paragraphs from `_UploadReview.cshtml`.
- **Tier `a`/`c` (`f20`)**: Places `.up-inspector` first and `.up-decision` second in DOM order (matching visual left-to-right order), removes the duplicate `form.submit()` fallback on HTTP status errors in `upload.js`, and preserves `inspect` when opening `Find another Case`.""",
        "states": [
            ("`upload-review`", "`/Upload` dropzone + `/Upload/Group/{id}` side-by-side inspector and destination decision card (`Proposal` vs `Today`)"),
        ],
        "panels": [
            ("`.up-inspector`", "Left file strip and document/image preview pane"),
            ("`.up-decision`", "Right destination decision card (`Create new Case`, `Attach to existing Case`, `Leave in Vehicle Images`)"),
        ],
        "dialogs": [],
    },
    {
        "slug": "cases",
        "title": "Cases Queue & Create Case",
        "routes": "`/Cases` and `/Cases/Create`",
        "frds": "[FRD-15](../../../pegasus/docs/frd/frd-15-work-centre-queues-and-search.md#cases-queue) and [FRD-18](../../../pegasus/docs/frd/frd-18-manual-upload.md)",
        "mock": "pegasus_shell_v41.html",
        "state": "cases-queue",
        "shots": [
            ("Cases Queue `/Cases` (proposal)", "14-cases-queue"),
            ("Create Case `/Cases/Create` (proposal)", "15-create-case"),
        ],
        "files_web": [
            "`src/Pegasus.Web/Pages/Cases/Index.cshtml` (`.cs`), `src/Pegasus.Web/wwwroot/css/cases-index.css`, `src/Pegasus.Web/wwwroot/js/cases-index.js`",
            "`src/Pegasus.Web/Pages/Cases/Create.cshtml` (`.cs`) and `src/Pegasus.Web/Pages/Shared/_InstructionDraftFields.cshtml`",
        ],
        "today_summary": """- `Cases/Index.cshtml.cs:878` populates `AvailablePrincipals` only from the 25 Cases on the current page (`all.Select(r => r.PrincipalDisplayName)`), hiding any active Principal not on that page.
- `Cases/Index.cshtml:131` prints `Page 1 · newest first` on empty, single-page, and unpaged tabs (`Triage`, `Unidentified`, `Vehicle Images`).
- `cases-index.js` performs a full page reload on row click and has no `ArrowUp`/`ArrowDown` keyboard navigation.
- `_InstructionDraftFields.cshtml:1-103` renders bare unwrapped inputs inside `<details><summary>More instruction details</summary>` and prints internal parser provenance (`"Extracted from InstructionPdfParser"`).""",
        "proposal_summary": """- **Item L (`f21`)**: Populates the `/Cases` `Principal` filter from the full active Principal directory (all 15 Principals), shows `Page N` only when paged (`total > pageSize`), and supports `data-row-list` keyboard navigation.
- **Item M (`f22`)**: Wraps `<details>` fields in `.form-grid .field`, removes internal parser provenance strings (`InstructionPdfParser`), and removes the `"Optional for Triage"` hint.""",
        "states": [
            ("`cases-queue`", "`/Cases` queue with full Principal directory filter, clean count header, and right-hand preview pane (`Proposal` vs `Today`)"),
            ("`create-case`", "`/Cases/Create` instruction draft and manual creation form (`Proposal` vs `Today`)"),
        ],
        "panels": [
            ("`.cases-workspace`", "2-column queue table + right-hand selected item preview pane (`440px`)"),
        ],
        "dialogs": [],
    },
    {
        "slug": "triage",
        "title": "Triage Case Workspace",
        "routes": "`/Cases/{id:guid}` (when `Type == Triage`)",
        "frds": "[FRD-15](../../../pegasus/docs/frd/frd-15-work-centre-queues-and-search.md#triage-workspace)",
        "mock": "pegasus_shell_v41.html",
        "state": "triage-case",
        "shots": [
            ("Triage Case `/Cases/{id}` (proposal)", "16-triage-case"),
        ],
        "files_web": [
            "`src/Pegasus.Web/Pages/Cases/Shared/_TriageCase.cshtml`, `_TriageDeterminationFields.cshtml`, `src/Pegasus.Web/Pages/Cases/Details.Triage.cs`, `src/Pegasus.Web/wwwroot/css/triage.css`",
        ],
        "today_summary": """- `#triage-link-case-dialog` (`_TriageCase.cshtml:748-776`) asks the operator to paste a raw 36-character `Case ID` GUID (`placeholder="Case GUID"`) to link an existing Case.
- `Exact response evidence` (`_TriageCase.cshtml:466-476`) prints raw RFC 5322 `InternetMessageIdentity` strings or `SentEvidenceId` GUIDs.
- The `Documents` tab (`_TriageCase.cshtml:364-396`) offers only `Save as` download links with no inline `Preview` action (`FRD-15:381`).""",
        "proposal_summary": """- **Item N (`f23`)**: Replaces the raw 36-character GUID input in `#triage-link-case-dialog` with a Case search/select (`QDOS ref, Registration, or Claim ref`), formats `Exact response evidence` as human-readable subject + recipient + timestamp (`dd MMM yyyy HH:mm`), and adds `Preview` alongside `Save as` on Triage `Documents`.""",
        "states": [
            ("`triage-case`", "Triage Case workspace with `Documents` preview, human-readable `Exact response evidence`, and Case search in `#triage-link-case-dialog` (`Proposal` vs `Today`)"),
        ],
        "panels": [
            ("`.triage-main`", "Left evidence tabs (`Instruction`, `Images`, `Documents`, `Correspondence`) and determination workspace"),
            ("`.triage-aside`", "Right sticky aside (`Next step`, `Case team`, `Integrity`)"),
        ],
        "dialogs": [
            ("`#triage-link-case-dialog`", "Modal dialog to link an existing Case by searching `QDOS ref`, `Registration`, or `Claim ref` (`f23`)"),
        ],
    },
    {
        "slug": "unidentified",
        "title": "Unidentified, Vehicle Images, Pre-Case Images & Auxiliary Case Routes",
        "routes": "`/Unidentified/{id:guid}`, `/VehicleImages/{id:guid}`, `/PreCaseImages`, `/Cases/{id}/Chaser`, `/Integrations/Glass/*`",
        "frds": "[FRD-15](../../../pegasus/docs/frd/frd-15-work-centre-queues-and-search.md)",
        "mock": "pegasus_shell_v41.html",
        "state": "unidentified-images",
        "shots": [
            ("Unidentified, Vehicle Images & Chaser (proposal)", "17-unidentified-images"),
        ],
        "files_web": [
            "`src/Pegasus.Web/Pages/Unidentified/Details.cshtml` (`.cs`), `src/Pegasus.Web/wwwroot/css/unidentified.css`",
            "`src/Pegasus.Web/Pages/ImageIntake/Details.cshtml` (`.cs`), `src/Pegasus.Web/wwwroot/css/image-record.css`",
            "`src/Pegasus.Web/Pages/PreCaseImages/Index.cshtml` (`.cs`), `src/Pegasus.Web/wwwroot/css/pre-case-images.css`",
            "`src/Pegasus.Web/Pages/Shared/_EvidenceViewer.cshtml`, `_ImageGallery.cshtml`",
            "`src/Pegasus.Web/Pages/Cases/Chaser.cshtml` (`.cs`), `Integrations/Glass/Opening.cshtml`, `Shared/_GlassReturn.cshtml`",
        ],
        "today_summary": """- Both `Unidentified/Details.cshtml` and `ImageIntake/Details.cshtml` repeat the top ribbon facts (`Status`, `Source`, `Captured`, `Registration`) inside the first card immediately below the ribbon.
- `Unidentified/Details.cshtml:198-219` embeds an inline `<details>` form inside the narrow `Actions` table cell to dismiss a registration reading.
- `/VehicleImages/{id}` (`ImageIntake/Details.cshtml:175-190`) navigates away to `/Cases?pairImageId=...` to pair with a Case instead of offering a pairing dialog on the record.
- `#evidence-viewer` closes on every pre-Case Crop or Tag POST (`?viewer=open` is not preserved).
- `/Cases/{id}/Chaser` omits `.req`/`required` on `To`, `Subject`, `Message` and has no `Cancel` button; `Integrations/Glass/Opening.cshtml` and `_GlassReturn.cshtml` omit `site.css`.""",
        "proposal_summary": """- **Item O (`f24`)**: Removes duplicate ribbon facts from the first card below the ribbon on `/Unidentified/{id}` and `/VehicleImages/{id}`, replaces the inline table-cell `<details>` form with `#dismiss-reading-dialog`, adds `#pair-case-dialog` on `/VehicleImages/{id}`, and preserves `?viewer=open&photo=N` across pre-Case Crop/Tag saves.
- **Tier `a` (`f25`)**: Adds `.req`/`required` and `Cancel` to `/Cases/{id}/Chaser`, and links `site.css` in the Glass integration pages.""",
        "states": [
            ("`unidentified-images`", "`/Unidentified/{id}`, `/VehicleImages/{id}` with `#pair-case-dialog`, and `/Cases/{id}/Chaser` (`Proposal` vs `Today`)"),
        ],
        "panels": [
            ("`.unid-ribbon` / `.img-ribbon`", "Single-home top facts strip"),
        ],
        "dialogs": [
            ("`#dismiss-reading-dialog`", "Modal dialog to dismiss a candidate registration reading with a reason (`f24`)"),
            ("`#pair-case-dialog`", "Modal dialog on `/VehicleImages/{id}` to search and pair with a Case directly (`f24`)"),
        ],
    },
    {
        "slug": "case",
        "title": "Case Record Workspace",
        "routes": "`/Cases/{id:guid}`",
        "frds": "[FRD-16](../../../pegasus/docs/frd/frd-16-case-record-workspace.md)",
        "mock": "pegasus_case_workspace_v41.html",
        "state": "v41-overview",
        "shots": [
            ("Case Workspace — Overview & Report Delivery (proposal)", "22-case-overview"),
            ("Case Workspace — Delivery rules & inline Yes/No + hold Done (proposal)", "23-case-delivery-rules"),
            ("Case Workspace — Plain delivery without rules (proposal)", "24-case-delivery-plain"),
            ("Case Workspace — Delivery stop rule (proposal)", "25-case-delivery-stop"),
            ("Case Workspace — Delivery missing To warning (proposal)", "26-case-delivery-missing"),
            ("Case Workspace — Post-report open tasks in Next step (proposal)", "27-case-next-action-tasks"),
            ("Case Workspace — Tasks dialog & Send to AI dialog (proposal)", "28-case-tasks-dialog"),
            ("Case Workspace — Engineer read view (proposal)", "29-case-engineer-read"),
            ("Case Workspace — Engineer edit view (proposal)", "30-case-engineer-edit"),
        ],
        "files_web": [
            "`src/Pegasus.Web/Pages/Cases/Details.cshtml` and `Details*.cs`",
            "All 35 partials in `src/Pegasus.Web/Pages/Cases/Shared/` (`_CaseRibbon.cshtml`, `_CaseAside.cshtml`, `_CaseReport.cshtml`, `_CaseTasks.cshtml`, `_CaseEstimate.cshtml`, `_CaseValuation.cshtml`, `_CaseFiles.cshtml`, `_CaseHistory.cshtml`, etc.)",
            "`src/Pegasus.Web/wwwroot/css/case-workspace.css` and `src/Pegasus.Web/wwwroot/js/case-workspace.js`",
            "`src/Pegasus.Web/Presentation/CaseWorkspaceLabels.cs` and `CaseNextAction.cs`",
        ],
        "today_summary": """- Preserves all settled Case Workspace guardrails (`.agents/skills/pegasus-ui-guardrails/references/case-workspace.md`): one scrolling page, save-as-you-go, sticky ribbon with `Tasks (N)` modal trigger, sticky right aside (`Next step`, `Case team`, `Integrity`), Valuation guide cards, and v38 Repair Spec bars.
- `_CaseRibbon.cshtml:241` and `_CaseTasks.cshtml:76` reference non-existent `#icon-check-square` instead of `#icon-square-check` (rendering a blank icon on `Tasks`).
- Empty states in Tasks, Images, Documents, Correspondence, and Queries use `.empty` or `.muted` instead of `.empty-line` (`v36 f46`).
- `_CaseSectionHeadTools.cshtml` and `_SubPanelToggle.cshtml` hardcode `title="Collapse section"` even when collapsed; `case-workspace.css:177` centers `[data-damage-reset]` instead of right-aligning it; `_CaseReport.cshtml:588-590` displays `"Not recorded"` in read mode when `To`/`Cc` suggestions exist; `_CaseReport.cshtml:840` and `_CaseOriginalReport.cshtml:76` include a duplicate blank `<option value="">`.
- Post-report open tasks in `.aside-card--action` (`_CaseAside.cshtml:300-315`) render as an unstyled `ul.blocker-list` with repeated `Tasks` buttons instead of `.next-step-list` / `.next-step--item` row buttons.
- `#case-tasks-dialog` uses bare inputs without `.fi`, `"None"` instead of `"Unassigned"`, and wraps row action buttons; `#send-to-ai-dialog` uses a bare number input for `Target Estimate (%)`.
- `case-workspace.js` lacks a `dblclick` listener on `[data-estimate-tab-label]` (`v28 P32`) and omits `list="report-address-book"` on dynamically added `Add To`/`Add Cc` inputs.""",
        "proposal_summary": """- **Items P & Q (`f27`)**: Confirms Report Delivery `.fg`/`.fc` read/edit parity (`To`, `Cc`, `Subject`, `Standard message` or `Covering note`, `Attachments`), visible `Yes`/`No` radio pills on undecided rule questions, inline `Done` hold tick on the hold's own line, and one-step `"send"` wording (`Send report`, `"Add at least one To recipient before sending."`).
- **Item R (`f28`)**: Renders post-report open tasks in `.aside-card--action` as `.next-step-list` / `.next-step--item` row buttons that open `#case-tasks-dialog` on click, matching pre-report blockers.
- **Item S (`f29`)**: Styles `#case-tasks-dialog` inputs with `.fi`, labels the blank assignee option `Unassigned`, keeps task row actions (`Save`, `Complete`, `Reopen`, `Remove`) on one `.cluster` line, and pairs `Target Estimate (%)` in `#send-to-ai-dialog` with a synchronized range slider + `.fc` number input.
- **Tier `a`/`c` (`f26`, `f30`)**: Fixes `#icon-square-check`, `.empty-line`, dynamic `Expand`/`Collapse` titles, right-aligned `[data-damage-reset]`, suggested `To`/`Cc` display in read mode, duplicate blank `<option>`, `[data-estimate-tab-label]` double-click rename, and `list="report-address-book"` on added recipient inputs.""",
        "states": [
            ("`v41-overview`", "Full Case Workspace overview uniting `f26`–`f30` / Items `P`–`S`"),
            ("`delivery-rules`", "Report Delivery with Principal rules (`Yes`/`No` radio pills + inline hold `Done` tick)"),
            ("`delivery-plain`", "Report Delivery for a Principal without rules"),
            ("`delivery-stop`", "Report Delivery when a rule stops sending (`Do not send here`)"),
            ("`delivery-missing`", "Report Delivery when `To` is empty (`Add at least one To recipient before sending.`)"),
            ("`next-action-tasks`", "Post-report open tasks in `.aside-card--action` styled as `.next-step-list` / `.next-step--item` row buttons (`Item R`)"),
            ("`tasks-dialog`", "`#case-tasks-dialog` (`Tasks (2)`) and `#send-to-ai-dialog` (`Item S`)"),
            ("`engineer-read`", "Report Delivery in read mode (`To`, `Cc`, `Subject`, `Standard message`, `Attachments`)"),
            ("`engineer-edit`", "Report Delivery in edit mode with shared `.fg`/`.fc` geometry"),
        ],
        "panels": [
            ("`.case-ribbon`", "Sticky Case header ribbon with `#icon-square-check` on `Tasks`"),
            ("`#case-report`", "Section 9 — Report & Report Delivery sub-panel"),
            ("`.case-aside`", "Sticky right column (`Next step`, `Case team`, `Integrity`)"),
        ],
        "dialogs": [
            ("`#case-tasks-dialog`", "Modal dialog for Case Tasks (`f26`, `f29`)"),
            ("`#send-to-ai-dialog`", "Modal dialog for Send to AI with paired range + `.fc` number input (`f29`)"),
        ],
    },
    {
        "slug": "administration",
        "title": "Administration Hub & All 13 Sub-Areas",
        "routes": "`/Administration`, `/Administration/Accounts`, `/Administration/Contacts`, `/Administration/Contacts/{id}`, `/Administration/Configuration`, `/Administration/Mailboxes`, `/Administration/EmailTemplates`, `/Administration/ValuationPresets`, `/Administration/Health`, `/Administration/Logs`, `/Administration/Reports`, `/Administration/ReleaseNotes`, `/Administration/ProblemReports`, `/Administration/AiJobs`, `/Administration/Automation`",
        "frds": "[FRD-17](../../../pegasus/docs/frd/frd-17-administration-workspace.md)",
        "mock": "pegasus_shell_v41.html",
        "state": "admin-accounts",
        "shots": [
            ("Administration — Accounts (proposal)", "18-admin-accounts"),
            ("Administration — Contacts & Principal Edit (proposal)", "19-admin-contacts"),
            ("Administration — Configuration & Mailboxes (proposal)", "20-admin-config-mail"),
            ("Administration — Hub, Logs, Problem Reports, AI Jobs & Automation (proposal)", "21-admin-logs-ops"),
        ],
        "files_web": [
            "`src/Pegasus.Web/Pages/Administration/Index.cshtml` (`.cs`), `Shared/_AdminNav.cshtml`, `AdministrationPageModel.cs`",
            "`src/Pegasus.Web/Pages/Administration/Accounts/Index.cshtml` (`.cs`), `Contacts/Index.cshtml` (`.cs`), `Contacts/Edit.cshtml` (`.cs`)",
            "`src/Pegasus.Web/Pages/Administration/Configuration.cshtml` (`.cs`), `Mailboxes.cshtml` (`.cs`), `EmailTemplates/Index.cshtml` (`.cs`), `ValuationPresets/Index.cshtml` (`.cs`)",
            "`src/Pegasus.Web/Pages/Administration/Health.cshtml` (`.cs`), `Logs.cshtml` (`.cs`), `Reports.cshtml` (`.cs`), `ReleaseNotes/Index.cshtml` (`.cs`), `ReleaseNotes/Edit.cshtml` (`.cs`), `ProblemReports.cshtml` (`.cs`), `AiJobs.cshtml` (`.cs`), `Automation/Index.cshtml` (`.cs`)",
            "`src/Pegasus.Web/wwwroot/css/admin.css`, `logs.css`",
        ],
        "today_summary": """- `/Administration` hub uses `#icon-sparkles` on `Automation & AI` (while `_AdminNav` uses `#icon-bot`), describes `Configuration` as `"View the current workflow policy."`, and `ReleaseNotes`/`Health` omit `ViewData["AdminAutomationComposed"]`.
- `/Administration/Accounts` renders the `Temporary password` panel outside `.admin-layout` at the bottom of the page, includes `"Manage this account's login."`, uses a bare unstyled `<dialog>` for `Delete account`, and exposes raw `Generation` and `Version` columns in `#glass-credential-dialog`.
- `/Administration/Contacts` includes `Optional.` and `(optional)` suffixes, uses non-existent `.definition-list` on `Principal API`, uses a bare `<dialog id="replace-principal">`, and lacks `.hint` CSS in `site.css` for the 5 settled Report sending hints (`v40` S).
- `/Administration/Configuration` lacks the `Administration` eyebrow, draws a browser `<fieldset>` border around workflow settings, renders six `Minimum to Maximum` `.field-hint` lines, and left-aligns Labour-rate card inputs/buttons.
- `/Administration/Mailboxes` renders an obsolete editable `Mail categories` panel and `Add category` dialog (contrary to `ADR-0069` / `FRD-20`), mixes 3 dialog close-button patterns, and prints raw `LastFailureCode`.
- `/Administration/Logs` exposes an internal memory-cache byte/hit-miss telemetry `<details>` panel on `Action logs` and uses legacy `status-chip`.
- `/Administration/ReleaseNotes` has no `Edit` action column; `/Administration/ProblemReports` prints a raw GUID in `When` and stacks two inline forms in `Actions`; `/Administration/AiJobs` uses plain-text Case references and an inline `<details>` confirm; `/Administration/Automation` uses `<label class="cluster">` instead of `<label class="choice">`.""",
        "proposal_summary": """- **Item T (`f32` — Accounts)**: Moves `Temporary password` inside `.admin-main` at the top of the workspace, removes `"Manage this account's login."`, styles `#delete-account-dialog` with `.dialog`, and removes `Generation` and `Version` from `#glass-credential-dialog`.
- **Item U (`f33` — Contacts)**: Removes `Optional.` and `(optional)` suffixes, styles `Principal API` with `.kv` + `.chip`, styles `#replace-principal` with `.dialog`, and adds `.hint` CSS (`11px`, `--ink-3`) to `site.css`.
- **Item V (`f34` — Configuration)**: Adds the `Administration` eyebrow, resets `fieldset` borders, removes the six `Minimum to Maximum` `.field-hint` lines, and right-aligns Labour-rate inputs and `Save`.
- **Item W (`f35` — Mailboxes)**: Removes the obsolete editable `Mail categories` panel and `Add category` dialog, standardizes dialog close buttons, and maps `LastFailureCode` to human labels.
- **Item X (`f36` — Logs)**: Removes the internal cache telemetry `<details>` panel from `Logs.cshtml` and uses `.chip.chip--Accent` on `AI`.
- **Item Y (`f38` — ProblemReports, AiJobs, Automation)**: Removes the raw GUID from `ProblemReports` `When` and replaces stacked inline forms with `#problem-report-dialog`; links `Case` references on `AiJobs` and moves `Stop` confirmation to `#stop-ai-job-dialog`; uses `<label class="choice">` on `Automation`.
- **Tier `a` (`f31`, `f37`, `f39`)**: Hub `#icon-bot` and `Configuration` description, `AdminAutomationComposed` in `AdministrationPageModel`, `Edit` link column on `ReleaseNotes`, and `Reports` lede/fieldset cleanup.""",
        "states": [
            ("`admin-accounts`", "`/Administration/Accounts` with top `Temporary password` banner, styled `#delete-account-dialog`, and clean `#glass-credential-dialog` (`Item T`)"),
            ("`admin-contacts`", "`/Administration/Contacts` & `/Administration/Contacts/{id}` with `.hint` styling, `.kv` `Principal API`, and styled `#replace-principal` (`Item U`)"),
            ("`admin-config-mail`", "`/Administration/Configuration` (`Item V`) and `/Administration/Mailboxes` without obsolete `Mail categories` (`Item W`)"),
            ("`admin-logs-ops`", "`/Administration` hub, `Logs` (`Item X`), `ReleaseNotes`, `ProblemReports`, `AiJobs`, and `Automation` (`Item Y`)"),
        ],
        "panels": [
            ("`.admin-layout`", "Left `.admin-nav` (`220px`) + right `.admin-main` workspace across all 13 areas"),
        ],
        "dialogs": [
            ("`#delete-account-dialog`", "Styled `.dialog` confirmation for deleting an account (`Item T`)"),
            ("`#glass-credential-dialog`", "Glass credentials modal without internal `Generation`/`Version` integers (`Item T`)"),
            ("`#replace-principal`", "Styled `.dialog` confirmation for replacing a Principal code (`Item U`)"),
            ("`#problem-report-dialog`", "Modal dialog to review and confirm or dismiss an operator problem report (`Item Y`)"),
            ("`#stop-ai-job-dialog`", "Modal dialog to stop a running AI job (`Item Y`)"),
        ],
    },
]


def main() -> None:
    PAGES.mkdir(parents=True, exist_ok=True)
    index_lines = [
        "# v41 pages index",
        "",
        "One folder per application surface audited in the v41 full-application UI, UX, and design review round (14 October 2026). See [../current/v41-notes.md](../current/v41-notes.md) for the consolidated `f01`–`f39` catalogue and lettered sign-off list (`A`–`Y`).",
        "",
        "| Folder | Surface | Routes | Mockup & state |",
        "| --- | --- | --- | --- |",
    ]
    for spec in SURFACE_SPECS:
        slug = spec["slug"]
        folder = PAGES / slug
        (folder / "states").mkdir(parents=True, exist_ok=True)
        (folder / "panels").mkdir(parents=True, exist_ok=True)
        (folder / "dialogs").mkdir(parents=True, exist_ok=True)

        index_lines.append(
            f"| [{slug}/]({slug}/README.md) | {spec['title']} | {spec['routes']} | [{spec['mock']}](../current/{spec['mock']}) (`?state={spec['state']}`) |"
        )

        shot_rows = []
        for label, prefix in spec["shots"]:
            shot_rows.append(
                f"| {label} | [1580](../current/v41-shots/{prefix}-1580.png) · [1440](../current/v41-shots/{prefix}-1440.png) · [760](../current/v41-shots/{prefix}-760.png) · [full](../current/v41-shots/{prefix}-full.png) |"
            )

        readme = f"""# {spec['title']}

**Temporary v41 design review notes (14 October 2026).** Governing behaviour: {spec['frds']}; presentation: [design authority](../../../pegasus/docs/design/README.md).

- **Routes**: {spec['routes']}
- **Interactive mockup**: [`{spec['mock']}`](../../current/{spec['mock']}) (`?state={spec['state']}&design=proposal` vs `&design=today`)
- [how-it-works.md](how-it-works.md): live implementation on `origin/dev` and usability/design findings.
- [how-it-should-work.md](how-it-should-work.md): proposed v41 design, UI, and UX improvements.
- [states/README.md](states/README.md), [panels/README.md](panels/README.md), [dialogs/README.md](dialogs/README.md).

## Screenshots

| View | Captures (`1580×1000`, `1440×900`, `760×1000`, `1580` whole page) |
| --- | --- |
{chr(10).join(shot_rows)}
"""
        (folder / "README.md").write_text(readme, encoding="utf-8")

        files_list = "\n".join(f"- {f}" for f in spec["files_web"])
        how_it_works = f"""# {spec['title']}: how it works today (`origin/dev`)

## Source files

{files_list}

## Current behaviour and audit findings

{spec['today_summary']}

See [../../current/v41-notes.md](../../current/v41-notes.md) for the complete `f01`–`f39` table and exact file/line citations.
"""
        (folder / "how-it-works.md").write_text(how_it_works, encoding="utf-8")

        how_it_should_work = f"""# {spec['title']}: how it should work (v41 proposal)

## Proposed design, UI & UX improvements

{spec['proposal_summary']}

## Interactive comparison

Open [`{spec['mock']}`](../../current/{spec['mock']}) at `?state={spec['state']}&design=proposal` and toggle **Proposal** vs **Today** in the bottom-left Mockup controls strip.

See [../../current/v41-notes.md#6-sign-off-list](../../current/v41-notes.md#6-sign-off-list) for the lettered sign-off items.
"""
        (folder / "how-it-should-work.md").write_text(
            how_it_should_work, encoding="utf-8"
        )

        state_rows = "\n".join(f"| {s[0]} | {s[1]} |" for s in spec["states"])
        (folder / "states" / "README.md").write_text(
            f"# {spec['title']}: states\n\n| State (`?state=`) | What it shows |\n| --- | --- |\n{state_rows}\n",
            encoding="utf-8",
        )

        panel_rows = (
            "\n".join(f"| {p[0]} | {p[1]} |" for p in spec["panels"])
            if spec["panels"]
            else "| — | Standard page layout |"
        )
        (folder / "panels" / "README.md").write_text(
            f"# {spec['title']}: panels\n\n| Panel | Purpose |\n| --- | --- |\n{panel_rows}\n",
            encoding="utf-8",
        )

        dialog_rows = (
            "\n".join(f"| {d[0]} | {d[1]} |" for d in spec["dialogs"])
            if spec["dialogs"]
            else "| — | No page-specific modal dialogs |"
        )
        (folder / "dialogs" / "README.md").write_text(
            f"# {spec['title']}: dialogs\n\n| Dialog | Purpose |\n| --- | --- |\n{dialog_rows}\n",
            encoding="utf-8",
        )

    (PAGES / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"Generated {len(SURFACE_SPECS)} page folders under {PAGES}")


if __name__ == "__main__":
    main()
