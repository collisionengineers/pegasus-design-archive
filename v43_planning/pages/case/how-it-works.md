# Case details: how it works

Read from the live source on 2 November 2026 (`origin/dev` `826c2aed7`).

## What the page does not show

- The card headed **Principal** holds no Principal fact. The Principal is a ribbon fact
  (v36 item E, 9 October 2026); the card holds the Claim source and its contact.
- The **Case contact** is filled at creation, without staff seeing it happen, from two
  places: the instruction e-mail's sender and signature (R462), or the Principal API's
  `fileHandler` block. Nothing reads the values afterwards: no report, export or recipient
  suggestion prints or uses them.
- **Notes from client** is printed nowhere; changing it does not make a generated report
  stale (`CaseReportFreshness`).
- A record's notes on every Case are absent, with no empty cell, when the record has none.

## Governing documentation

| Document | What it settles here |
| --- | --- |
| FRD-16 §Case details (`docs/frd/frd-16-case-record-workspace.md:424–436`) | The Case and Principal cards, the Claim source chosen from active Claim Source contacts, the Notes band, Accident circumstances beside Notes from client |
| FRD-23 instruction field table (`frd-23-case-draft-fields-provenance-and-global-checks.md:110`) | Contact name, e-mail and phone: from the instruction, else the sender (R462) |
| FRD-04 §Contacts administration | A Claim source record's *Notes on every Case* |
| `docs/rulings.md` R462 | #1682: Case contact details from the e-mail, kept as a feature (28 October 2026) |
| `docs/engineering/principal-api.openapi.yaml` | The `fileHandler` block of a Principal instruction |

## Source by layer

| Layer | File | What it owns |
| --- | --- | --- |
| Web | `Pages/Cases/Shared/_CaseOverview.cshtml` | The section's markup: cards, Case contact, Notes band, accident band |
| Web | `Pages/Cases/Details.cshtml.cs` | The Save handler's posted fields (`contactName`…, `clientNotes`, `principalNotes`, `claimSourceNotes`, `claimSourceId`…), the proposed-values table |
| Web | `wwwroot/js/case-workspace.js:4404–4433` | The Claim source select fills the contact inputs and the record-notes cell before Save |
| Web | `wwwroot/css/case-workspace.css:118–128` | The card grid and Notes band columns |
| Web | `Mcp/CaseEditMcpTools.cs` | The Automation actor's Case edit: contact and `clientNotes` parameters |
| Core | `Cases/CaseDataContracts.cs`, `CaseWorkspace.cs`, `CaseDataOperations.cs`, `CaseDataFieldNames.cs` | `CaseContactData`, `CaseWorkspaceData.ClientNotes`, `CaseWorkspaceOverview`, normalisation |
| Core | `Intake/SenderContactFill.cs`, `Intake/InstructionDraftFields.cs:57–59`, `PrincipalApi/PrincipalInstructionJson.cs` | The two fill paths |
| Infrastructure | `Persistence/EfCaseDataStore.cs`, `CaseDataSnapshotFactory.cs`, `EfCaseAcceptanceStore.cs`, `EfIntakeReceiptStore.cs` | Facts in `CaseDataFields`; `InstructionDrafts.FileHandler*` columns |

## Behaviours

### Claim source card (headed "Principal")
The select lists the active Claim source contacts while editing. A recorded source that is
no longer active stays as its own option. Each option carries the record's notes and
contact, so the contact inputs and the record-notes cell follow a change before Save. The
three contact cells show the Case's override where one is recorded, else the record's copy.
Save keeps an override only where it differs (operator, 23 September 2026).

### Case contact
Three cells (name, e-mail, phone) with source tags. Facts are created at acceptance. The
instruction's file handler (Principal API) fills them where given. Otherwise the R462 sender
fill gives the sender's name and e-mail, then the first UK phone number below the sign-off.
Nothing already recorded is replaced.

### Notes band
Two columns: the Principal's notes on every Case, then this Case's Principal notes; the
Claim source's notes on every Case, then this Case's Claim source notes. The record cells
are read-only and absent when empty. While editing, a hidden slot stands in for an absent
Claim source record cell.

### Accident band
Accident circumstances beside Notes from client, each a multi-line cell.

## Things the FRD does not settle

- Where a lone cell sits when its partner is absent (now items F and G).
