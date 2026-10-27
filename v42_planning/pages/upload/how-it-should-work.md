# Upload — How it should work (v42 5-Design Comparison, Sign-off AB)

## Shared invariants across all 5 designs (`UB1`–`UB5`)

- **Vocabulary (`OperatorLabels.Upload`):**
  - Eyebrow: `Add files to Pegasus` (or `Adding to` when `DeclaredCaseId` is present).
  - Heading: `Choose the files for this upload` (`Ready to upload` once files are chosen).
  - Drop target: `Drop files here` (`Add more files` once files are chosen), `Images, documents, emails and video`, `JPG, JPEG, PNG, PDF, DOC, DOCX, EML, MSG, MP4 or MOV`, `+ Choose files`.
  - Limits: `20 files maximum`, `100.0 MB per file`, `200.0 MB per upload`.
  - Queue & actions: `Selected files`, `Clear` (`button[type="reset"]`), `Upload N files` (`button[type="submit"][data-select-submit]`).
- **Case upload (`/Upload?caseId=…`):**
  - Displays the target Case identity (`QDOS26214`, `MA59BDY · R. Whitfield`, `QDOS`, `<span class="status status--blue">Report sent</span>`), the filing rule caption `They appear under Files once processed.`, and a `Back to QDOS26214` link back to `/Cases/{id}`.
- **No layout jump on file selection:**
  - Every design reserves a stable home for `Selected files` and the `Clear` / `Upload` action footer from initial load, so choosing files populates the queue in place without shifting the page geometry.

## The 5 candidate designs

| Design | Change ID | States | Structure |
| --- | --- | --- | --- |
| **Design A — Split workbench** | **UB1** | `upload-a`, `upload-a-case` | 2-pane `.pane-layout` (`minmax(400px, 1.08fr) minmax(340px, 0.92fr)`): left pane holds the Case destination banner (on Case upload), tactile `.up-drop` well, and 3-cell `.fact-grid` limit strip; right pane permanently displays the `Selected files` queue (structured empty slate when `0` files, file rows when populated) and `.pane-foot` action bar. |
| **Design B — Structured panel & format guide** | **UB2** | `upload-b`, `upload-b-case` | `.panel` workspace with limit pills in `.panel-head`, a 2-column body (`1fr` drop well + live `Selected files` list on the left; `310px` **Accepted formats** reference card with `Images`, `Documents`, `Emails`, `Video` rows on the right), and `.panel-foot`. On Case upload, a dedicated horizontal Case identity ribbon card (`.up-b-case-ribbon`) sits above the panel. |
| **Design C — Intake staging ledger** | **UB3** | `upload-c`, `upload-c-case` | Mirrors the full-width v42 Inbox ledger: top `.pane-head` + Case `.presence-strip` (on Case upload), compact horizontal 3-part `.up-c-dropbar` (`icon` + `Drop files here` + `+ Choose files`), and a full-width staging ledger table (`Selected files`, `Destination`, `Remove`) with `.panel-foot`. |
| **Design D — Destination-first split** | **UB4** | `upload-d`, `upload-d-case` | 2-column `.up-d-split` (`350px` left `.context-card.panel` + `1fr` right `.panel`): left card frames **Where the files go** (`Confirm Case after storage` on rail upload; full target Case card + `Back to QDOS26214` on Case upload) and a 2×2 `.fact-grid` of limits; right card holds the drop zone, `Selected files` list, and `.panel-foot`. |
| **Design E — Focused record sheet** | **UB5** | `upload-e`, `upload-e-case` | Full-width, full-height `.record.up-e-sheet` with dark charcoal `.record-head` header band (`Upload` on `/Upload`, and `Upload · QDOS26214` with `MA59BDY · R. Whitfield · QDOS · Report sent` + `Back to QDOS26214` on Case upload), 4px `.record-accent` stripe, and a clean full-bleed `.up-drop` drop target with zero redundant limit/extension/empty-state copy (`Selected files` and the `.record-bar` footer appear only once files are selected). |
