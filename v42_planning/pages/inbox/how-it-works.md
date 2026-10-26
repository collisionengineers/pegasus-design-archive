# Inbox — how it works

Read from the live source on 26 October 2026 (`origin/dev` `373dcc81a`).

## What the page does not show

- `CaseStateMailClassification` (`src/Pegasus.Core/Intake/Classification/CaseStateMailClassification.cs`) silently rewrites an e-mail's `MailCategory` when it is linked to a Case: linking an e-mail to a `ReportSent` Case rewrites its category to `Query` (or `CaseUpdate`), which in turn causes `CaseQueryLedger.RaiseForMailAsync` to open a `CaseQueries` row even when the e-mail is a thank-you note.
- Six of the eleven `MailCategory` values (`PreInstruction`, `ImagesReceived`, `Cancellation`, `Billing`, `NotClientRelated`, `InternalCc`) are never produced by any deterministic rule in `PrincipalMailClassificationPolicy`; they exist only as manual or classifier choices.
- `AutomaticMailCaseAssociation.SelectTarget` (`src/Pegasus.Core/Intake/AutomaticMailCaseAssociation.cs`) links only on an exact `ConversationId` match or a system-wide unique VRM. It ignores `In-Reply-To`/`References` headers, Principal claim references in the subject/body, and accident dates when a VRM appears on more than one Case, and any multi-candidate signal vetoes another signal that found one Case.
- The reply composer's `Also resolve query` checkbox (`StaffMailSendCommand.ResolvesCaseQueries`) calls `CaseQueryLedger.ResolveAllAsync` when the Sent item is observed, closing every open query on the Case rather than only the query on the e-mail being replied to.

## Governing documentation

| Document | What it settles for this page |
| --- | --- |
| `docs/adr/0069-one-flat-mail-category.md` | One flat `MailCategory` enum across the application. |
| `docs/adr/0070-case-state-mail-classification.md` | Rewriting `MailCategory` from the linked Case's lifecycle state. |
| `docs/frd/frd-08-email-mailbox-and-background-processing.md` | Retained mailbox ingestion, deterministic classification, automatic Case association, staff mail send and observed Sent resolution. |
| `docs/frd/frd-09-principal-and-intermediary-routes.md` | QDOS deterministic classification tells (garage allocation, repairs authorised, report chase, PAV dispute) and claim-reference extraction rules. |
| `docs/frd/frd-19-image-intake-and-vehicle-image-handling.md` | Eligibility for `Register images` from an unlinked mailbox message (`ImagesReceived`). |
| `docs/frd/frd-20-mailbox-workspace.md` | `/Inbox` scopes, filters, bulk actions, `/Inbox/{id}` Decision panel, classification chips, Case picker and next-action offers. |
| `docs/frd/frd-22-pre-case-gates-matching-and-association.md` | Pre-case matching and the rule that incident date is an excluding rule rather than a matching rule. |

## Source by layer

| Layer | File | What it owns |
| --- | --- | --- |
| Web | `src/Pegasus.Web/Pages/Mail/Index.cshtml`, `Index.cshtml.cs` | `/Inbox` scopes (`All incoming`, `No Case Found`, `Sent Items`, `Dismissed`, `Deleted Items`), `Mailbox` and `Category` filters, bulk `Dismiss`/`Restore`/`Correct classification`. |
| Web | `src/Pegasus.Web/Pages/Mail/Message.cshtml`, `Message.cshtml.cs`, `MailClassificationSelection.cs` | `/Inbox/{id}` message view, `ClassificationOptions` (12 chips), `Offer` (`CreateCase`, `OpenTriage`, `RegisterImages`), Case link/unlink handlers, reply composer. |
| Web | `src/Pegasus.Web/Pages/Mail/Shared/_MessageDecision.cshtml`, `_MessageRecord.cshtml`, `_MessageNested.cshtml` | Decision panel markup, record bar and composer markup, Link/Unlink/Triage/Register images dialogs. |
| Web (MCP) | `src/Pegasus.Web/Mcp/MailMcpTools.cs`, `SendMcpTools.cs` | `pegasus_mail_list`, `pegasus_mail_get`, `pegasus_mail_correct_classification`, `pegasus_mail_link_case`, `pegasus_mail_send`. |
| Core | `src/Pegasus.Core/Intake/Classification/MailClassificationContracts.cs`, `PrincipalMailClassificationPolicy.cs`, `CaseStateMailClassification.cs` | `MailCategory` (11 values), deterministic QDOS tells, Case-state category rewrite. |
| Core | `src/Pegasus.Core/Intake/RetainedMail.cs`, `AutomaticMailCaseAssociation.cs`, `ImageIntakeLifecycle.cs` | Inbox list scopes, classification correction, automatic mail-to-Case association (`SelectTarget`), `IsImageRegistrationEligible`. |
| Infrastructure | `src/Pegasus.Infrastructure/Persistence/EfRetainedMailboxMessageStore.cs`, `EfIntakeMutationStore.cs`, `CaseQueryLedger.cs`, `LocalEmailDisplayReader.cs` | Retained message queries, link/unlink transaction, query ledger side-effects on link and classification correction, MIME reading. |
| Classifier | `src/pegasus-classifier-agent/src/{prompt,tools,eligibility,pegasus}.ts` | AI classification prompt, tool schemas and eligibility. |

## Behaviours

### Scopes and category filter

`Index.cshtml.cs` exposes five scopes on the left rail and a `Category` `<select id="queue-filter">` with all eleven `MailCategory` codes. `All incoming` lists every non-dismissed Inbox message regardless of whether it is linked or what category it carries; `No Case Found` lists unlinked Inbox messages whose receipt has no Case.

### Decision panel and classification chips

`_MessageDecision.cshtml` renders `Classification` first as twelve chips (`MailClassificationSelection.Options`: the eleven `MailCategory` codes plus `unclassified`). Clicking a chip submits `CorrectClassification` immediately (`Corrected from the Inbox`), except `New instruction` which reveals `#mailWorkType` when no Case type is selected. Beneath `Classification` sit `Case`, the `Case / PO` combobox (`#mailLinkCaseReference`), `Link to Case` / `Change linked Case` / `Unlink`, and `Decided`.

### Query side-effects of classification and linking

Correcting an e-mail on a `ReportSent` Case to `Query` calls `CaseQueryLedger.RaiseForMailAsync`; correcting it away from `Query` calls `WithdrawForMailAsync`. Linking any e-mail to a `ReportSent` Case runs `CaseStateMailClassification`, which rewrites its category and raises a query.

### Next-action offer on unlinked mail

`MessageModel.Offer` returns `CreateCase` for `NewInstruction`, `OpenTriage` for `TriageRequest`, and `RegisterImages` only when the category is `ImagesReceived` and `Offers.CanRegisterImages` holds.

## Things the FRD does not settle

- How an operator opens a query from a linked e-mail or marks a single e-mail's query done once `Query` is no longer a `MailCategory`.
- Where unlinked non-instruction correspondence sits when the noise categories and the `Category` filter are removed.
- How a staff member places a Case on Hold or closes it starting from a cancellation or correspondence e-mail in the Inbox.
- How reply headers (`In-Reply-To`/`References`), free-text claim references and VRM + accident date combine when associating an incoming e-mail with a Case.
