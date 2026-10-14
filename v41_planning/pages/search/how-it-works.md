# Search: how it works today (`origin/dev`)

## Source files

- `src/Pegasus.Web/Pages/Search/Index.cshtml` (`.cs`) and `src/Pegasus.Web/Pages/Search/_CasePreview.cshtml`

## Current behaviour and audit findings

- `Search/Index.cshtml:58-63` renders `Engineer` as a raw 36-character GUID text box (`placeholder="Account ID"`), and `Principal` (`lines 86-90`) and `Origin` (`lines 103-107`) as free-text inputs.
- Labels the stage filter `State` instead of `Case stage` (`CONTEXT.md:189`) and collapses `More filters` on reload even when secondary filters have active values.
- `.page-header` includes a duplicate `Create Case` button (`href="/Upload"`).
- Results and Preview Documents tables omit `class="table"`; Results omits `Type` and `Due` columns (`FRD-15:436`).
- `_CasePreview.cshtml:29` labels `PrincipalReference` as `Our ref` instead of `Claim ref`, omits `Copy Case/PO` (`FRD-15:440`), and hardcodes `Next action` to `"Not recorded"` for every Case past `Not ready`.

See [../../current/v41-notes.md](../../current/v41-notes.md) for the complete `f01`–`f39` table and exact file/line citations.
