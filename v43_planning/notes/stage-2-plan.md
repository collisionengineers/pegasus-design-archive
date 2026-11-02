# v43 Case details: Claim source card, Principal panel, Case contact and Notes from client removed

## Context

The operator's brief (2 November 2026) for the Case record's **Case details** section
(`src/Pegasus.Web/Pages/Cases/Shared/_CaseOverview.cshtml`, read at `origin/dev` `826c2aed7`):

1. **Case contact**: remove the sub-panel and everything behind it: the Case data, persistence,
   MCP, and every fill path (R462 sender fill `SenderContactFill`, the Principal API `fileHandler`
   block → `InstructionDraft.FileHandler*` → Case contact). Supersedes R462 (28 Oct 2026).
2. The card headed **Principal** really holds the Claim source select + its three contact
   cells. Relabel it **Claim source**.
3. Put two notes cells under the Claim source card: the Claim source record's notes on
   every Case (read-only), and this Case's Claim source notes.
4. Move the Principal notes (the record's notes plus this Case's) into their own container.
5. **Notes from client** (`ClientNotes`): remove end to end. It has no extraction; only staff
   (Case page) and MCP (`CaseEditMcpTools` `clientNotes`) write it, and no document prints it.

Operator answers (2 Nov 2026), recorded as rulings in Stage 2:
- The round lives in `../pegasus-design-archive/v43_planning/`, committed like v42. This
  overrides the 15 Oct "archive is storage only" note. Update that memory.
- The Principal container is a **full-width sub-panel** where the Notes band is today, headed
  **Principal**. Its cells keep the live labels `Principal notes` (read-only, absent when none)
  and `Principal notes · this Case`.
- Stored Case contact and Notes from client values are **dropped** with a destructive migration.
- Principal API `fileHandler` is **removed** from the contract.

Workflow: a Stage 1 mockup round (razor-html-mockup-creation), then stop for sign-off; after
that, Stage 2 (razor-html-mockup-conversion) as one PR.

## Stage 1: mockup round v43 (this turn's deliverable after approval)

Use the v42 shape, with Today captured and never drawn:
- Detached worktree `../pegasus-worktrees/v43-capture` at `origin/dev`. Run the excluded
  `ZzMockupCaptureCase` lane (on disk, in `.git/info/exclude`) with `MOCKUP_CAPTURE=1`,
  `MOCKUP_CAPTURE_DIR=../pegasus-design-archive/v43_planning/captured-live`,
  `MOCKUP_REPO_ROOT`, and copy `wwwroot` + `_LucideSprite.cshtml` to `captured-live/_source/`.
  Strip asset fingerprints and shoot with reduced motion (v41 traps).
- Base the archive branch `design/v43-case-details` on `origin/main`. v42 sits on its own
  branch, so do not stack on it. Copy and trim v42's `build/` (states, `proposals_case.py`
  BeautifulSoup patches, `build-v43.py`, `pagedocs-v43.py`, `check-v43.py`, runtime/strip)
  down to the Case page.
- States: Instruction Case read; edit mode; edit with the Claim source changed (the notes cell
  follows the select); no Claim source; record with no Claim source / Principal notes; 1440
  and 760 folds; Triage Case for parity.
- Strip variable for item E (accident band: full width / half width).
- Deliver `pegasus_v43.html`, `notes/v43-notes.md` (change table, live rules mirrored,
  frame numbers, departures, sign-off list, self-check RESULT, known limits),
  `notes/discussion-log.md` (the brief and the answers above verbatim), `pages/case/`
  (`how-it-works.md` read from live on 2 Nov 2026, `how-it-should-work.md`), and `shots/` at
  1580×1000, 1440×900 and 760×1000. Commit to the archive branch, then **stop for sign-off**.

Sign-off items (each "Confirm, or …"):
- **A** Card `Principal` → `Claim source`. Its collapse key `case.overview.principal` →
  `case.overview.claim-source`, so per-browser fold state resets once.
- **B** Claim source card: the select and three contact cells, then `Claim source notes`
  (read-only, absent when none; the hidden edit slot still lets the select fill it) and
  `Claim source notes · this Case`, each spanning the card.
- **C** A full-width `Principal` sub-panel replaces the Notes band (key `case.overview.notes`
  → `case.overview.principal-notes`).
- **D** Case contact sub-panel removed.
- **E** Notes from client removed. Accident circumstances then stands alone: full width, or
  half width?
- **F** Triage Case unchanged. Its read-only Principal notes cell stays.
- **G** The DFD form's `Contact details if not client` review label
  (`DfdInstructionExtractionPolicy.cs:24`) stays. It is a review-only line that fills no Case
  field.

## Stage 2: implementation (only after A–G are signed off)

Task worktree `../pegasus-worktrees/case-details-claim-source`, branch
`task/case-details-claim-source` from `origin/dev` (`--no-track`), one PR. Follow
`pegasus-ui-guardrails`.

### Web
- `_CaseOverview.cshtml`:
  - Rename the card and move the Claim source notes cells (208–217, including the
    `data-record-notes-slot`) under the contact cells.
  - Turn the Notes band (201–219) into the `Principal` panel holding only the Principal cells.
  - Delete the Case contact sub-panel (189–196) and its locals (46–51).
  - Delete the client-notes cell (224) and set the accident layout per E.
- `case-workspace.js:4404–4433`: the select's notes and contact lookups are scoped to the
  section, so check they still find the moved cell. No change is expected.
- `case-workspace.css:120,127`: retarget or drop `.notes-band`, and set the accident band per E.
- `Details.cshtml.cs`:
  - Remove the `contactName`, `contactEmailAddress`, `contactPhoneNumber` and `clientNotes`
    parameters (2214–2216, 2238).
  - Remove them from the submitted lists (2417, 2420), the `Submitted(...)` rows (2530–2532,
    2543) and the `FieldBaseline`/`FieldLabel` arms (5356–5358, 5394–5396).
- `CaseMutationPageModel.cs:60–62`: remove the contact fields from `RetainableFormFields`.
- `CaseWorkspaceLabels.cs`: remove `NotesFromClient`. **Keep** `ContactName`, `ContactEmail`
  and `ContactPhone`, which the claim-source labels reuse, and `Contact`, which the claimant
  uses.
- `Mcp/CaseEditMcpTools.cs`: remove the contact parameters (167–169), `clientNotes` (179),
  the `Any(...)` guard terms (235–238), the positional arguments (290–292, 308), and update
  the description (157).

### Core
- `CaseDataFieldNames.cs`: remove `ContactName`, `ContactEmailAddress` and
  `ContactPhoneNumber` (19–21), and `ClientNotes` (73–75).
- `CaseDataContracts.cs`:
  - Remove the `CaseContactData` record (110–113) and its doc comment (80–81).
  - Remove `CaseDataProjection.Contact` (178), which shifts the positional constructors.
  - Remove `CaseEditableData` contact and `ClientNotes` (226–228, 280) and
    `CaseWorkspaceData.ClientNotes` (214).
- `CaseDataOperations.cs`: remove the normalise lines (169–171, 193).
- `CaseWorkspace.cs`: remove the `CaseWorkspaceOverview` contact and `ClientNotes` parameters
  (195–197, 206) and the `Overlay` copies (1035–1037, 1042).
- Intake:
  - Delete `Intake/SenderContactFill.cs`.
  - Remove the three entries in `InstructionDraftFields.cs:57–59`.
  - Remove `InstructionDraft.FileHandler*` in `IntakeContracts.cs:721–731`.
- `PrincipalApi/PrincipalInstructionJson.cs`: remove `FileHandler` (105, 137–139, 240). Delete
  `PrincipalInstructionPartyBody` (208) if nothing else uses it.

### Infrastructure
- `EfCaseDataStore.cs`: remove the projection (148–150, 213), writer (349–351, 398) and
  reader (458–460, 501) lines.
- `CaseDataSnapshotFactory.cs`: remove the `fileHandler` facts (303–305), `AddSenderContact`
  (78, 359–409), the `instructionEmail` parameter (29–38) and `InstructionEmailSender`
  (669–670).
- `EfCaseAcceptanceStore.cs:280–294`: remove the retained-message read that only serves the
  fill.
- `EfIntakeReceiptStore.cs`: remove 489–491, 678–680 and 908–910.
- `PegasusDbContext.cs`: remove 341–343 and 1599–1601.
- Migration `RemoveCaseContactAndClientNotes`, created with `dotnet ef migrations add`, which
  also updates the snapshot:
  - Drop `InstructionDrafts.FileHandlerName`, `FileHandlerEmailAddress` and
    `FileHandlerPhoneNumber`.
  - Add `DELETE FROM CaseDataFields WHERE FieldName IN ('contact_name',
    'contact_email_address','contact_phone_number','client_notes')`.
  - Forward-only and destructive. Apply it to a scratch LocalDB with `ef database update`.

### Tests
- Delete `Core.Tests/Intake/SenderContactFillTests.cs` and
  `IntegrationTests/SenderContactSnapshotTests.cs`.
- Delete `CaseRecordFieldsWebTests.NotesFromClientSitBeside…` (35–54) and the ClientNotes
  cases in `CaseRecordGapsTests` (16–41, 56).
- Split `CaseWorkspacePersistenceTests:2247`: keep the claim-source half.
- Repoint `CaseReportFreshnessTests:24` to another unprinted field.
- Fix the positional call sites in `AssessmentReportDraftWebTests:571`,
  `CaseWorkspacePersistenceTests:2675`, `CaseRecordGapsTests:34`,
  `AssessmentWorkspaceTestData:19–37` and `CaseCapabilityPagesTestSupport:1208`.
- Fix the assertion and field-list sites in `AutomationAssessmentIngressTests`,
  `CaseVehicleSaveWebTests`, `CaseEditModeWebTests`, `CaseDetailsWebTests:352`,
  `CaseTasksWebTests:103`, `CaseDataCompletenessPersistenceTests:260` and
  `PrincipalInstructionPolicyTests:16`.
- `CaseActionsMenuWebTests:489–493` anchors on `case.overview.contact`. Re-anchor it.
- Add one render test: the Claim source heading, both Claim source notes cells inside that
  card, the Principal panel with its two cells, no Case contact, and no `data-client-notes`.

### Docs
- `docs/rulings.md`:
  - Add rows (next free numbers at build time) for the brief and the five answers.
  - Mark R462 superseded.
- FRD-16 §Case details (424–436): Case and Claim source cards, the Claim source notes under
  the Claim source card, a Principal panel with the Principal's notes, no Case contact and no
  Notes from client. Date it 2 Nov 2026 and cite the rulings.
- FRD-23 row 110: removed.
- `current-architecture.md:165`: SenderContactFill row removed.
- `principal-api.openapi.yaml`: remove the `fileHandler` example, property and schema
  (248–251, 508–509, 560–575).
- PR body: flag the destructive migration (the release takes the destructive window) and
  include the side-by-side conformance evidence against the signed-off mockup.

## Verification

- Stage 1: the self-check prints `RESULT {"fail":[],"okCount":N}` with no console errors, and
  the shots are taken at all three sizes. Neither is application evidence.
- Stage 2: CI on the PR head is the evidence; no local build or test run is repeated. Locally:
  - Apply the migration to a scratch LocalDB.
  - Do one visual walk on the capture host, diffed against `pegasus_v43.html`.
