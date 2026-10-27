# Inbox — how it should work

Decided with the operator on 26 October 2026 (rules **D1**–**D6**, settled items **A**–**F**)
and proposed for sign-off (rules **D7**–**D17**, open items **G**–**I**, **K**, **L**, **N**, **R**–**W**).

## Rules

- **D1 (A, settled 26 October 2026):** `MailCategory` has three values — `NewInstruction` (with Case type `Inspection`, `Audit`, `InspectionAndAudit`), `TriageRequest` and `Cancellation` — and every other e-mail has no category (linked it is Case correspondence; unlinked it waits in No Case Found).
- **D2 (B, settled 26 October 2026):** Unlinked e-mail that is neither a `New instruction` nor a `Triage request` appears only in `No Case Found`; `All incoming` lists instructions, triage requests and Case-linked mail.
- **D3 (C, settled 26 October 2026):** Linking an e-mail to a `Report sent` Case opens a query only when deterministic query criteria (`OpensQuery = true`) hold; the AI classifier and staff may also open a query through the shared Core route, and any other linked e-mail is plain Case correspondence.
- **D4 (E, settled 26 October 2026):** `Cancellation` remains a category with its Case aside row (`Cancellation received`) and Engineer notification alongside the **Change case** links on the message.
- **D5 (F, settled 26 October 2026):** Automatic mail-to-Case association links by conversation thread, by `In-Reply-To`/`References` headers, by Principal claim reference in subject/body, and by VRM narrowed by accident date.
- **D6 (G, cog menu settled 26 October 2026):** On `#mailMessageDialog` (`_MessageDialog.cshtml`), the right-hand `Decision` column is replaced by a **settings menu (cog icon `#icon-settings`, `details[data-mail-settings]`)** in `.mail-dialog-tools` and an at-a-glance context pill bar (`.mail-context-bar`) beneath the `From · To · Time` route line so the message body reads at full width; inside the cog menu the sections are ordered **Case** (with the `Case / PO` picker and `Link to Case` / `Change linked Case` / `Unlink`), **Type**, **Query**, **Change case**, then **Decided**, and **Change case** renders links **Place on Hold** (`/Cases/{id}?dialog=case-hold-dialog`) and **Close case** (`/Cases/{id}?dialog=case-close-dialog`) whenever the linked Case permits those acts.
  - Open: **G** — confirm the order inside the cog menu (**Case**, **Type**, **Query**, **Change case**), the `.mail-context-bar` header strip and the `/Cases/{id}?dialog=…` links, or specify another order or interaction.
- **D7 (H):** The classification row is labelled **Type** and offers four chips — **Correspondence** (the default chip when no category is set, replacing `Unclassified`), **New instruction**, **Triage request** and **Cancellation** — with the `Case type` select inside the **Type** row when `New instruction` is chosen.
  - Open: **H** — confirm the label **Type** and default chip **Correspondence**, or give another label.
- **D8 (I):** The Inbox filter bar has no `Category` select and the bulk bar has no `Correct classification` button or dialog; `Mailbox`, `Search` and bulk `Dismiss` / `Restore` remain.
  - Open: **I** — confirm removing the `Category` filter and bulk `Correct classification`, or say which control should stay.
- **D9 (K, N):** When a message is linked to a Case, Decision shows a **Query** row: if the message holds an open query it shows the purple `Query` chip, the assignee (or `Unassigned`) and **Mark done**; if the message's query is closed it shows the green `Done` chip; if the message holds no query and the Case's report is sent (`CaseQueryRules.CanOpen`) it shows **Open query**.
  - Open: **K**, **N** — confirm the **Query** row states (`Open query`, open `Query` + `Mark done`, `Done`) and one query per e-mail.
- **D10 (L):** The reply composer offers **Mark query done** (replacing `Also resolve query`) only when replying (`reply` or `reply_all`) to an e-mail that holds an open query, and observing the Sent item marks only that e-mail's query done.
  - Open: **L** — confirm **Mark query done** and its single-query scope.
- **D11 (R):** On an unlinked e-mail whose Type is **Correspondence** (no category) and for which `Offers.CanRegisterImages` is true, the record bar offers **Register images**.
  - Open: **R** — confirm **Register images** eligibility on unlinked `Correspondence` image mail.
- **D12 (S):** QDOS garage-allocation, repairs-authorised and report-chase tells and automatic-reply detection no longer assign a category; the QDOS PAV-dispute sentence sets `OpensQuery = true` on the classification decision.
  - Open: **S** — confirm dropping QDOS notice labels and using the PAV-dispute sentence as a deterministic query criterion.
- **D13 (T):** Reply-header linking (`In-Reply-To` and `References`) matches retained received messages and Pegasus Sent items across any approved mailbox when they point to a single non-archived Case.
  - Open: **T** — confirm cross-mailbox reply-header linking.
- **D14 (U):** Claim-reference linking matches any token (6–100 chars of `[A-Za-z0-9/\-]` containing a digit, plus its normalised QDOS tail) in the subject or current body equal to a single non-archived Case's `CaseMatchIndex.DurableClaimToken` across all Principals.
  - Open: **U** — confirm free-text claim-reference linking across all Principals.
- **D15 (V):** When VRM matches multiple Cases and the incoming message has an extracted accident date, candidates with a different accident date are dropped and candidates with an equal accident date win if exactly one remains.
  - Open: **V** — confirm accident-date narrowing for VRM candidates.
- **D16 (W):** When multiple linking signals are non-empty, their candidate Case sets are intersected; if the intersection is a single non-eliminated, non-archived Case, the message is associated with it.
  - Open: **W** — confirm intersecting non-empty signal sets.

## The actions and dialogs

- **Open query (from Decision):** posts `OnPostOpenQueryAsync` on `/Inbox/{id}` → `IOpenCaseQuery.ExecuteAsync` with the message's `RetainedMessageId` and current `CaseId`, no lease or reason.
- **Mark done (from Decision):** posts `OnPostMarkQueryDoneAsync` on `/Inbox/{id}` → `IMarkCaseQueryDone.ExecuteAsync` with the message's open `QueryId`.
- **Place on Hold / Close case (from Decision):** links to `/Cases/{id}?dialog=case-hold-dialog` or `?dialog=case-close-dialog`; `site.js` opens the named dialog on load.

## Where this lands

| Page / component | Entry |
| --- | --- |
| `src/Pegasus.Web/Pages/Mail/Index.cshtml(.cs)` | Remove `#queue-filter`, `[data-bulk-classify]`, `#bulkClassifyDialog`, `OnPostBulkClassify`; show row category text only for the three categories. |
| `src/Pegasus.Web/Pages/Mail/Shared/_MessageDialog.cshtml`, `_MessageRecord.cshtml`, `_MessageDecision.cshtml`, `Message.cshtml.cs` | Replace the `.mail-split > aside` `Decision` column with the `#icon-settings` cog menu in `.mail-dialog-tools` and `.mail-context-bar` in `.mail-dialog-title`; reorder to Case, Type, Query, Change case, Decided; add `OnPostOpenQueryAsync` and `OnPostMarkQueryDoneAsync`; update `Offer` for `RegisterImages`. |
| `src/Pegasus.Web/Pages/Mail/Shared/_MessageRecord.cshtml` | Rename `Also resolve query` to `Mark query done` (`markQueryDone`). |
| `src/Pegasus.Core/Intake/` & `src/Pegasus.Infrastructure/Persistence/` | Three `MailCategory` values, `OpensQuery`, `All incoming` filter, `SelectTarget` v2, migration `_ThreeMailCategories` and `_RetainedMailReplyIdentities`. |
| `src/Pegasus.Web/Mcp/MailMcpTools.cs`, `SendMcpTools.cs`, `src/pegasus-classifier-agent/` | Add `pegasus_mail_open_query`, rename `resolveQuery` → `markQueryDone`, update classifier categories and `open_query` tool. |

## Documentation impact when the FRD is written

- New `ADR-0085` superseding `ADR-0069` and `ADR-0070` and amending `ADR-0067`.
- Update `FRD-08`, `FRD-09`, `FRD-10`, `FRD-19`, `FRD-20`, `FRD-22`, `CONTEXT.md`, `docs/capabilities.md` (`MAIL-22`), `docs/current-architecture.md` and `docs/principal-profiles/qdos.md`.

## Decided 27 October 2026

Signed off by the operator ("I sign off on this design"): all rules **D1**–**D16** and items **A**–**I**, **K**, **L**, **N**, **R**–**W** are settled as drawn in `pegasus_v42.html` (`9fd9869`).
