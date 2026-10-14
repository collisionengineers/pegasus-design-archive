# Cases Queue & Create Case: how it works today (`origin/dev`)

## Source files

- `src/Pegasus.Web/Pages/Cases/Index.cshtml` (`.cs`), `src/Pegasus.Web/wwwroot/css/cases-index.css`, `src/Pegasus.Web/wwwroot/js/cases-index.js`
- `src/Pegasus.Web/Pages/Cases/Create.cshtml` (`.cs`) and `src/Pegasus.Web/Pages/Shared/_InstructionDraftFields.cshtml`

## Current behaviour and audit findings

- `Cases/Index.cshtml.cs:878` populates `AvailablePrincipals` only from the 25 Cases on the current page (`all.Select(r => r.PrincipalDisplayName)`), hiding any active Principal not on that page.
- `Cases/Index.cshtml:131` prints `Page 1 · newest first` on empty, single-page, and unpaged tabs (`Triage`, `Unidentified`, `Vehicle Images`).
- `cases-index.js` performs a full page reload on row click and has no `ArrowUp`/`ArrowDown` keyboard navigation.
- `_InstructionDraftFields.cshtml:1-103` renders bare unwrapped inputs inside `<details><summary>More instruction details</summary>` and prints internal parser provenance (`"Extracted from InstructionPdfParser"`).

See [../../current/v41-notes.md](../../current/v41-notes.md) for the complete `f01`–`f39` table and exact file/line citations.
