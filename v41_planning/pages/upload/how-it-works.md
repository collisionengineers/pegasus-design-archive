# Upload & Upload Review: how it works today (`origin/dev`)

## Source files

- `src/Pegasus.Web/Pages/Upload.cshtml` (`.cs`), `UploadStatus.cshtml` (`.cs`), `UploadGroupStatus.cshtml` (`.cs`), `UploadConfirmationPageModel.cs`
- `src/Pegasus.Web/Pages/Shared/_UploadReview.cshtml`, `_UploadDestinationCard.cshtml`, `_UploadReviewCandidate.cshtml`, `_UploadReviewLeave.cshtml`, `_UploadReviewRecord.cshtml`
- `src/Pegasus.Web/wwwroot/css/upload.css` and `src/Pegasus.Web/wwwroot/js/upload.js`

## Current behaviour and audit findings

- `Upload.cshtml:21` omits `.eyebrow` (`Files`) in `.page-header`.
- `_UploadReview.cshtml:39, 77, 88, 101, 110, 146, 234` renders a `.up-subtitle` lede and six `.up-explainer` narration paragraphs violating *No explanatory copy*.
- `_UploadReview.cshtml:55, 249` places `.up-decision` before `.up-inspector` in the DOM while `upload.css:17-18` swaps them visually on desktop (`>900px`), reversing keyboard `Tab` order.
- `upload.js:276` calls `form.submit()` in the XHR `.catch()` handler on HTTP 400/500, re-uploading up to 200 MB a second time; and `Find another Case` resets `inspect` to `0`.

See [../../current/v41-notes.md](../../current/v41-notes.md) for the complete `f01`–`f39` table and exact file/line citations.
