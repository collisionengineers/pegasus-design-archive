# Unidentified, Vehicle Images, Pre-Case Images & Auxiliary Case Routes: how it works today (`origin/dev`)

## Source files

- `src/Pegasus.Web/Pages/Unidentified/Details.cshtml` (`.cs`), `src/Pegasus.Web/wwwroot/css/unidentified.css`
- `src/Pegasus.Web/Pages/ImageIntake/Details.cshtml` (`.cs`), `src/Pegasus.Web/wwwroot/css/image-record.css`
- `src/Pegasus.Web/Pages/PreCaseImages/Index.cshtml` (`.cs`), `src/Pegasus.Web/wwwroot/css/pre-case-images.css`
- `src/Pegasus.Web/Pages/Shared/_EvidenceViewer.cshtml`, `_ImageGallery.cshtml`
- `src/Pegasus.Web/Pages/Cases/Chaser.cshtml` (`.cs`), `Integrations/Glass/Opening.cshtml`, `Shared/_GlassReturn.cshtml`

## Current behaviour and audit findings

- Both `Unidentified/Details.cshtml` and `ImageIntake/Details.cshtml` repeat the top ribbon facts (`Status`, `Source`, `Captured`, `Registration`) inside the first card immediately below the ribbon.
- `Unidentified/Details.cshtml:198-219` embeds an inline `<details>` form inside the narrow `Actions` table cell to dismiss a registration reading.
- `/VehicleImages/{id}` (`ImageIntake/Details.cshtml:175-190`) navigates away to `/Cases?pairImageId=...` to pair with a Case instead of offering a pairing dialog on the record.
- `#evidence-viewer` closes on every pre-Case Crop or Tag POST (`?viewer=open` is not preserved).
- `/Cases/{id}/Chaser` omits `.req`/`required` on `To`, `Subject`, `Message` and has no `Cancel` button; `Integrations/Glass/Opening.cshtml` and `_GlassReturn.cshtml` omit `site.css`.

See [../../current/v41-notes.md](../../current/v41-notes.md) for the complete `f01`–`f39` table and exact file/line citations.
