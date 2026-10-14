# Work Centre: how it works today (`origin/dev`)

## Source files

- `src/Pegasus.Web/Pages/Index.cshtml` (`.cs`) and `src/Pegasus.Web/Pages/_WorkCentreBody.cshtml`
- `src/Pegasus.Web/wwwroot/css/work-centre.css` and `src/Pegasus.Web/wwwroot/js/work-centre.js`

## Current behaviour and audit findings

- Renders the single-table Work Centre ledger switching between `Assigned to me`, `Unassigned`, `New cases`, and `AI jobs`.
- **Critical bug (`f10`)**: `_WorkCentreBody.cshtml:335, 427` and `Index.cshtml.cs:594` only populate `#wc-assign-dialog` when `Model.SelectedCaseForAssignment` is non-null (requiring a row to be expanded via `Selected`). Every unexpanded row in `Unassigned` still renders `<button data-dialog-open="wc-assign-dialog">Assign Engineer</button>`, so clicking `Assign Engineer` on an unexpanded row either does nothing or opens the dialog pre-filled for the **wrong Case** (whichever other row is expanded).
- `work-centre.css:5, 56, 70` overrides `.page-header h1` to `25px` (instead of `20px`), `.wc-switch a` to `28px`/`2px` radius (instead of `32px`/`4px` inside `36px` `.seg`), and `.wc-ledger-table th` to `9px` non-sticky (instead of `11px` `34px` sticky).
- `.wc-find` omits hidden `since` (`DividerUtc`), `Dismiss` does a full page reload, and `selected` leaks into `New cases` / `AI jobs`.

See [../../current/v41-notes.md](../../current/v41-notes.md) for the complete `f01`–`f39` table and exact file/line citations.
