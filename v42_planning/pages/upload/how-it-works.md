# Upload — How it works today (`origin/dev` `373dcc81a`)

## Live files

- `src/Pegasus.Web/Pages/Upload.cshtml` & `Upload.cshtml.cs`
- `src/Pegasus.Web/Pages/Shared/_UploadDestinationCard.cshtml`
- `src/Pegasus.Web/Presentation/OperatorLabels.cs` (`OperatorLabels.Upload`)
- `src/Pegasus.Web/wwwroot/css/upload.css`
- `src/Pegasus.Web/wwwroot/js/upload.js`

## Two entry points

1. **Left-hand navigation rail (`/Upload`):**
   - `Model.DeclaredCaseId` is `null`.
   - Operator chooses up to 20 files (`100.0 MB per file`, `200.0 MB per upload`), submits the batch, and lands on `/Upload/Group/{groupId}` (`UploadGroupStatus.cshtml`) or `/Upload/Status/{receiptId}` (`UploadStatus.cshtml`) to confirm the Case destination.
2. **Case workspace `Add evidence` (`/Upload?caseId={id}`):**
   - Linked from `[data-add-evidence]` in `_CaseFiles.cshtml` (`#section-files`).
   - `UploadModel.OnGetAsync(Guid? caseId)` loads the target `UploadReviewDestination` (`Reference`, `Registration · Claimant`, `Principal`, `Stage`).
   - Renders `<input asp-for="DeclaredCaseId" type="hidden" />` and `<div class="up-declared" data-upload-declared>` containing `<p class="up-eyebrow">Adding to</p>` and `_UploadDestinationCard.cshtml` directly between `.up-select-title` and `.up-drop`.

## Current visual defects on the initial screen

1. **Box-in-a-box empty margins (`.up-workspace.is-choosing:not(.has-files) > .up-select`):**
   - `.up-surface` stretches full content width (`1304px` at `1580px` viewport), while `.up-select` is constrained to `max-width: 760px; margin-inline: auto; padding: 30px` and `.up-evidence` (`Selected files`) has `hidden`.
   - This leaves `~272px` of blank white space on both sides inside `.up-surface` and `~400px` of empty grey canvas below `.up-surface`.
2. **Layout shift when the first file is picked:**
   - As soon as 1 file is selected, `upload.js` toggles `.has-files` and unhides `.up-evidence`, snapping `.up-workspace` from a centred `760px` column into a 2-column grid (`minmax(320px, 1.25fr) minmax(0, .88fr)`).
3. **Unframed Case destination on `/Upload?caseId=…`:**
   - `.up-declared .up-final-destination` removes `border-top` and sits inline between `Choose the files for this upload` and the dashed drop box with no card framing, no `They appear under Files once processed.` caption, and no `Back to {Reference}` return action.
