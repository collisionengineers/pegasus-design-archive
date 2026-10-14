# Triage Case Workspace: how it works today (`origin/dev`)

## Source files

- `src/Pegasus.Web/Pages/Cases/Shared/_TriageCase.cshtml`, `_TriageDeterminationFields.cshtml`, `src/Pegasus.Web/Pages/Cases/Details.Triage.cs`, `src/Pegasus.Web/wwwroot/css/triage.css`

## Current behaviour and audit findings

- `#triage-link-case-dialog` (`_TriageCase.cshtml:748-776`) asks the operator to paste a raw 36-character `Case ID` GUID (`placeholder="Case GUID"`) to link an existing Case.
- `Exact response evidence` (`_TriageCase.cshtml:466-476`) prints raw RFC 5322 `InternetMessageIdentity` strings or `SentEvidenceId` GUIDs.
- The `Documents` tab (`_TriageCase.cshtml:364-396`) offers only `Save as` download links with no inline `Preview` action (`FRD-15:381`).

See [../../current/v41-notes.md](../../current/v41-notes.md) for the complete `f01`–`f39` table and exact file/line citations.
