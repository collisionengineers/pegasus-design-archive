# v42 discussion log

Chronological. Records how the v42 mockup came to be; not design authority.

## 26 October 2026: the operator's request

The operator invoked `/razor-html-mockup-creation` with the following brief (quoted verbatim):

> *"We need to simplify the e-mail categories process.*
>
> *Let's have 'Case Correspondence' as the catch-all for any e-mail that is linked to a Case. We will still have Queries.*
>
> *A Query can be opened in 5 ways:*
> *1. Manually from an e-mail in the Inbox*
> *2. Automatically via criteria*
> *3. AI classifier*
> *4. MCP tool for the Automation actor*
> *5. An option on the Case page*
>
> *We must make sure all of these use 1 clean route.*
>
> *A query is usually an e-mail, but a user could log one manually (e.g. a WhatsApp, a phone call). If it's an e-mail, it can be marked as done or replied to (and when replying, an option to mark as done). If it's manual, it's just marked as done. There is no oversight on queries. Queries can be reopened by users, engineers, or admins.*
>
> *Queries only ever come in after the report is sent. Queries are assignable, and separate from the Case. They move the Case from 'Report sent' into 'Query' (purple).*
>
> *Let's get rid of all the other noise categories (pre-instruction, billing, internal CC, not client related, case update). Instead of tagging, let's give options to change the Case. The main question for any e-mail is: which Case is it for?*
>
> *If an e-mail is linked to a Case, it shows up in the Case's correspondence.*
>
> *An e-mail is either 'Instructions' (with a subtype) or Case Correspondence. We link it by thread, Principal claim reference, VRM + accident date.*
>
> *Build the mockup first. Consider the full blast radius. Once approved, we'll implement it."*

## 26 October 2026: blast-radius exploration

Six read-only scouts mapped the live codebase on `origin/dev` (`373dcc81a`) and the governing documentation (`CONTEXT.md`, `ADR-0067`, `ADR-0069`, `ADR-0070`, `FRD-08`, `FRD-09`, `FRD-10`, `FRD-12`, `FRD-13`, `FRD-15`, `FRD-16`, `FRD-17`, `FRD-19`, `FRD-20`, `FRD-22`):

1. **Core & Infrastructure classification (`MailCategory`, `PrincipalMailClassificationPolicy`, `CaseStateMailClassification`).**
   - `MailCategory` (`src/Pegasus.Core/Intake/Classification/MailClassificationContracts.cs`) has 11 values stored as string codes. Six (`PreInstruction`, `ImagesReceived`, `Cancellation`, `Billing`, `NotClientRelated`, `InternalCc`) are never emitted by any deterministic rule.
   - `PrincipalMailClassificationPolicy` (QDOS path) uses garage-allocation, repairs-authorised and report-chase tells to emit `CaseUpdate`, and a PAV-dispute sentence predicate to emit `Query`.
   - `CaseStateMailClassification` rewrites categories when an e-mail is linked to a Case (turning linked mail on a Report sent Case into `Query` or `CaseUpdate`).
   - `ImageIntakeLifecycleRules.IsImageRegistrationEligible` requires `MailCategory.ImagesReceived` for manual image registration from the Inbox.
2. **Queries (`CaseQueryEntity`, `CaseQueryLedger`, `CaseQueryLifecycle`).**
   - `CaseQueryLedger` (`src/Pegasus.Infrastructure/Persistence/CaseQueryLedger.cs`) is the sole writer of `CaseQueries` and `CaseWorkflows.HasOpenQuery` (enforced by `CaseQueryLedgerOwnershipTests`).
   - Queries are raised by `RaiseForMailAsync` (when a `Query`-classified e-mail joins a Report sent Case) and `RaiseCaseQuery` (staff/MCP logging), and resolved all at once by `ResolveCaseQueries` (`CaseQueryLedger.ResolveAllAsync`).
   - `CaseQueryEntity` has no `AssigneeStaffId`, no per-query mark-done and no reopen transition. Logging and resolving require a Case edit lease and expected Case version.
3. **Web Inbox, Case workspace & Work Centre.**
   - `/Inbox` (`Pages/Mail/Index.cshtml`) has a `Category` filter select (`#queue-filter`) and a bulk `Correct classification` button and dialog (`#bulkClassifyDialog`).
   - `_MessageDecision.cshtml` orders `Classification` (12 chips) before `Case`, and has no Query row and no Case state actions.
   - `_CaseCorrespondence.cshtml` has a `Classification` column and a `Tag as query` form (which posts `CorrectClassification` with `ClassificationKey=query`).
   - `_CaseQueries.cshtml` has no `Assigned to` column and no row-level `Mark done`, `Assign`, `Take` or `Reopen`.
   - `OperationsSnapshot.cs` (`GetOperationsSnapshot.FetchAttentionInputsAsync`) has no `NeedsAttentionKind.Query` row.
4. **Automatic mail-to-Case association (`AutomaticMailCaseAssociation`, `EfIntakeMutationStore`).**
   - `SelectTarget` (v1) links only when a single non-archived Case matches by `ConversationId` or system-wide unique VRM, and abstains if signals disagree or any signal has multiple candidates. It does not inspect `In-Reply-To`/`References`, Principal claim references in subject/body, or accident dates to narrow multiple VRM candidates.
5. **MCP & Classifier agent (`src/Pegasus.Web/Mcp`, `src/pegasus-classifier-agent`).**
   - `pegasus_case_action` carries `log_query` and `resolve_query` (requiring a Case edit lease); `pegasus_mail_send` carries `resolveQuery`; the classifier agent's `prompt.ts` and `tools.ts` list the 11 categories.

## 26 October 2026: five operator rulings before drawing

Five design choices that materially affected the mockup were put to the operator and answered:

1. **Unlinked non-instruction mail in Inbox scopes** → **No Case Found only**: unlinked e-mail that is not a New instruction or Triage request waits only in `No Case Found` (staff link or Dismiss it); `All incoming` lists instructions, triage requests and Case-linked mail. *(Settled item **B**.)*
2. **Automatic query opening when an e-mail joins a Report sent Case** → **Criteria + AI only**: deterministic query criteria (such as the QDOS PAV-dispute sentence) and the AI classifier open a query; any other e-mail joining a Report sent Case is plain correspondence unless staff press `Open query`. *(Settled item **C**.)*
3. **Initial assignee of a new query** → **Unassigned until taken**: a newly opened query starts `Unassigned`; staff or engineers `Take` it or `Assign` it. *(Settled item **D**.)*
4. **Cancellation e-mails and changing the Case from a message** → **Keep a cancellation marker**: keep `Cancellation` as the third mail category (with its Case aside row and notification) alongside `New instruction` and `Triage request`, and add `Change case` links (`Place on Hold`, `Close case`) on the message Decision panel. *(Settled items **A**, **E**.)*
5. **Automatic mail-to-Case linking rules** → **Widen**: link by conversation thread or `In-Reply-To`/`References` to a message on one Case, by Principal claim reference found in subject/body, and by VRM narrowed by accident date when several Cases share the VRM. *(Settled item **F**.)*

## 26 October 2026: live capture and v42 mockup build

- Created detached capture worktree `../pegasus-worktrees/v42-capture` at `origin/dev` `373dcc81aedd7ff1415090b4fb50486652ebc595`.
- Extended `ZzMockupCaptureInbox.cs` with fixtures `m7` (`Billing`), `m8` (`NotClientRelated`), `m9` (`InternalCc`), `m10` (`PreInstruction`), `m11` (`Cancellation` on a second Case `QDOS26220` in `ReportPreparation`), `m12` (`CaseUpdate` on `QDOS26214` in `ReportSent`), and a staff-logged `Phone` query on `QDOS26214`.
- Ran `ZzMockupCaptureInbox`, `ZzMockupCaptureIntake` and `ZzMockupCaptureShell` with `MOCKUP_CAPTURE=1` (5 of 5 passed, 1 m 20 s; `notes/capture-run-2026-10-26.log`). Copied `inbox`, `intake`, `shell` and `wwwroot` into `v42_planning/captured-live/`.
- Built `pegasus_v42.html` (19 states, 18 with Proposals) and ran `check-v42.py`: `RESULT {"fail": [], "okCount": 316}`, 148 screenshots in `shots/`.
- Raised sign-off items **G** to **AA** in [v42-notes.md §6](v42-notes.md#6-sign-off).

## 26 October 2026: `#mailMessageDialog` over `/Inbox`, cog settings menu and interactive fake emails

The operator reviewed the initial v42 drawing and directed:

> *"the mockup, particularly with regards to emails, is wrong to the current live state.*
>
> *additionally we will just replace the 'decision' with a settings menu (cog icon) on the email dialogue (its not its own page anymore, though the mockup has it like this).*
>
> *Make sure the mockup is fully interactive with fake emails etc that i can open.*
>
> *Improve the overall design and UX on this emails part and view.*
>
> *Push when done. This is mockup only so far."*

What changed:

- **True live Today state (`#mailMessageDialog` over `/Inbox`):** Every `message-m*` state now renders `/Inbox` (or `/Inbox?queue=no_case_found` for `m3` and `m7`) with `#mailMessageDialog` (`_MessageDialog.cshtml`) open in `[data-mail-dialog-root]`, instead of the standalone `/Inbox/{id}` fallback page. In Today, `#mailMessageDialog` shows the live 1080px split layout with the 380px right-hand `Decision` column and 12 `Classification` chips.
- **Decision replaced by the cog settings menu (`#icon-settings`) in Proposal:** In Proposal, the right-hand `Decision` column is removed so the message body reads at full width (`880px` dialog) with an inline attachment strip (`.mail-inline-attachments`). An at-a-glance context pill bar (`.mail-context-bar`) beneath the `From · To · Time` route line shows the linked **Case** (or `No Case Found` + `Link to Case`), **Type**, and **Query** status (`Query · Unassigned` or `Open query`). A cog button (`#icon-settings`, `details[data-mail-settings]`) in `.mail-dialog-tools` opens the settings popover ordered **Case** (with interactive `Case / PO` autocomplete and `Link to Case` / `Change linked Case` / `Unlink`), **Type** (four chips + `Case type`), **Query** (`Open query` or `Query` + `Unassigned` + `Mark done`), **Change case** (`Place on Hold`, `Close case`), and `Decided`.
- **Inbox list & filter UX:** Fixed `.inbox-filter` to a 3-column grid once `Category` is removed so the `Search` input fills the bar and the `Search` button stays compact; surfaced prominent Case reference pills (`.mail-row-case`) and open `Query` chips directly in each linked row's status cluster; made clicking anywhere on an `.inbox-row` open `#mailMessageDialog`.
- **Full interactivity across all 12 fake emails (`m1`–`m12`):** Built `mail_dialogs.py` and updated `bridge-v42.js` (including a `window.URL` wrapper and `<base href>` for `about:srcdoc`) so clicking any email row on `/Inbox`, stepping with `Previous`/`Next`, switching `Message`/`Attachments`/`Thread` tabs, composing `Reply`/`Reply all`/`Forward`, searching/filtering/sorting, dismissing rows, and changing `Case`, `Type` or `Query` inside the cog settings menu all work live in the browser.
- Re-ran `python build/build-v42.py && python build/pagedocs-v42.py && python build/check-v42.py`: `RESULT {"fail": [], "okCount": 335}`, 148 screenshots updated in `shots/`.

## 26 October 2026: 3-scope full-width Inbox ledger, Principal filter, 1-step Email type select and button-minimal Case tables

The operator reviewed the second iteration and directed:

> *"we dont really need sent or deleted items on the inbox either.*
>
> *just all, no case found, dismissed and maybe filters for principles and such*
>
> *Your inbox design was very bad and basic. you need to enhance this. I also dont want the clicky thing for changing the emails category anymore, make that different and more streamlined.*
>
> *Try a lot harder on the design to make it GOOD and make it look good too ultrathink"*
>
> *"make sure the pages arent just messes of buttons. thats a critique of the last design. you added the buttons but everything looks kinda... bad. e.g. the case page"*

What changed:

- **Full-width 6-column Inbox ledger with 3 scopes (`All`, `No Case Found`, `Dismissed`) and Principal / Signal filters:** Removed `Sent Items`, `Deleted Items` and the 220px left scope `<aside>`, replacing them with a single unified toolbar (`All 8` · `No Case Found 8` · `Dismissed 2` segmented tabs, live search, `All Principals` select for `QDOS` / `Northline` / `Meridian` / `Connexus`, `All signals` select for `Instructions` / `Open queries` / `Cancellations` / `Unread`, and a contextual bulk bar that stays hidden when `0` rows are ticked). Replaced the tall 4-line cards with a structured 6-column ledger (`Case / Stage`, `Type / Signal`, `Message`, `Sender / Principal`, `Received`, and hover-revealed row actions) seeded with 17 realistic emails (`m1`–`m17`).
- **1-step `Email type` `<select>` and borderless menu items inside the `#icon-settings` cog menu:** Replaced the clicky category chip cloud + conditional `Case type` dropdown with a single `<select id="mailTypeSelect">` (`Case correspondence`, `New instruction — Inspection`, `New instruction — Audit`, `New instruction — Inspection and Audit`, `Triage request`, `Cancellation`), and styled `Open query` / `Mark query done` and `Place Case on Hold…` / `Close Case…` as clean borderless menu rows inside the cog popover.
- **Button-minimal Case `Correspondence` and `Queries` tables:** Made the message **Subject** itself the link that opens the message dialog in both `Correspondence` and `Queries` (removing the redundant `[Open message]` button from every row), and moved query assignment into the **`Assigned to` cell** (`Unassigned ▾` + inline `Take` link) so each `Queries` row carries only `Reply` + `Mark done` (mail), `Mark done` (logged), or `Reopen` (`Done` rows) on a single clean line.
- Re-ran `python build/build-v42.py && python build/pagedocs-v42.py && python build/check-v42.py`: `RESULT {"fail": [], "okCount": 339}`, 156 screenshots updated in `shots/`.

## 27 October 2026: operator sign-off

After reviewing the exact Pegasus `Inter` font, colour tokens, `Case` / `Type` / `Subject` / `Sender` / `Received` headers, `None` for unlinked Cases, removal of `"Early triage"` / `"Signal"`, `.table td.row-actions` button containment fix, and default-to-Proposal mode (`9fd9869`), the operator signed off:

> *"I sign off on this design. Consider the existing session plan, and create a full plan for the integration of this into our design, taking into consideration concerns regarding blast radius, existing features, and documentation that may contradict. Do not proceed to integration yet."*
