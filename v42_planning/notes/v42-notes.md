# v42 notes: mail simplification (instructions, Case correspondence and assignable queries)

**Temporary design review artifact.** It is not application code, not design authority
and not implementation evidence. Behaviour is owned by the FRDs, and presentation by the
[design authority](../../../pegasus/docs/design/README.md). The sign-off list in §6
decides what Stage 2 changes.

## 1. What changed from v41 and why

Today `MailCategory` has eleven values (`NewInstruction`, `TriageRequest`, `PreInstruction`,
`ImagesReceived`, `CaseUpdate`, `Cancellation`, `Query`, `Billing`, `General`,
`NotClientRelated`, `InternalCc`) plus `Unclassified`; six are never produced by any
deterministic rule, and `CaseStateMailClassification` rewrites categories when an e-mail
is linked. Queries are child rows on a Case raised by two different writers, resolved all
at once by `ResolveCaseQueries`, not assignable and not reopenable.

v42 cuts the mail model back to what matters — which Case an e-mail is for — and makes
each query an assignable record opened through one Core route from all five entry points
(Inbox, deterministic criteria, AI classifier, Automation MCP, Case page), marked done
one at a time and reopenable.

| Previous problem | v42 change | Shots (`shots/`) |
| --- | --- | --- |
| Eleven mail categories plus Unclassified clutter the Inbox list, filter bar, bulk bar and message Decision panel with labels that carry no workflow behaviour (`Pre-instruction`, `Images received`, `Case update`, `Query`, `Billing`, `General`, `Not client related`, `Internal CC`), and changing a category requires clicking a chip cloud plus a conditional `Case type` dropdown. | Three categories remain: `New instruction` (with Case type), `Triage request` and `Cancellation`. Every other e-mail has no category: linked it is **Case correspondence**, unlinked it waits in **No Case Found**. Inside the `#icon-settings` cog menu, the clicky chip cloud is replaced by a single streamlined **Type** `<select>` (`Correspondence`, `New instruction · Inspection`, `New instruction · Audit`, `New instruction · Inspection and Audit`, `Triage request`, `Cancellation`). (**A**, **H**) | `001`–`008`, `009`–`024` |
| Unlinked noise (`Billing`, `Not client related`, `Internal CC`, `Pre-instruction`, unlinked photographs) sits in **All incoming** alongside live instructions and Case mail, and a 220px left scope sidebar with `Sent Items` and `Deleted Items` wastes screen width above tall 4-line cards. | `Sent Items` and `Deleted Items` leave the Inbox; the three scopes (**All**, **No Case Found**, **Dismissed**) use the shared `.tabs` strip above a single toolbar (**Search**, **All principals**, **All Mailboxes**) and a full-width ledger with exact column headers (**Case**, **Type**, **Subject**, **Sender**, **Received**). Unlinked non-instruction mail appears **only in No Case Found**, and unlinked rows read `None` in the `Case` column. (**B**, **I**) | `001`–`008`, `019`–`020` |
| The Inbox **Category** select and bulk **Correct classification** dialog exist only to sort or relabel the eleven categories, and the bulk bar sits visible when `0` rows are ticked. | Both are removed from the Inbox. The bulk bar (`Dismiss` / `Restore`) is contextual — hidden when `0` rows are ticked and revealed when rows are ticked. (**I**) | `001`–`008` |
| Linking any e-mail to a Report sent Case (`CaseStateMailClassification`) or tagging it as `Query` raises a query, and `#mailMessageDialog` devotes a permanent 380px right-hand `Decision` column to Classification chips before Case, with no route to open a query or change the Case's state. | Automatic queries come from deterministic criteria (the QDOS PAV-dispute sentence) and the AI classifier only; any other e-mail joining a Report sent Case is plain correspondence. On `#mailMessageDialog`, the right-hand `Decision` column is replaced by a **settings menu (cog icon `#icon-settings`, `[data-mail-settings]`)** in the dialog header paired with a quiet metadata strip above the full-width message. Inside the cog menu, the order is **Case**, **Type** (`<select>`), **Query** (`Open query` or `Mark done`), **Change case** (`Place on Hold`, `Close case`). (**C**, **E**, **G**, **K**, **N**) | `009`–`014`, `021`–`024` |
| `Images received` is a separate category required before **Register images** is offered on an unlinked image e-mail. | `Images received` is removed; **Register images** is offered on any image-only, unlinked e-mail whose Type is `Correspondence` (no instruction, triage or cancellation type). (**R**) | `017`–`018` |
| The reply composer's `Also resolve query` checkbox resolves every open query on the Case when the Sent item is observed. | Renamed **Mark query done**; offered only when replying to an e-mail that holds an open query, and marks only that e-mail's query done on observed Sent. (**L**) | `015`–`016` |
| Case **Correspondence** calls its column `Classification`, repeats an `[Open message]` button on every row, and offers `Tag as query` (a classification correction). | Column header becomes **Type**, showing `Correspondence` (or one of the three types) plus the e-mail's query chip (`Query` or `Done`); clicking the **Subject** opens the message dialog directly, and **Open query** is the sole row button once the report is sent. (**N**, **X**, **AA**) | `025`–`026`, `033`–`034` |
| Case **Queries** has no assignee, resolves all open queries together from the ribbon/aside (`Resolve query`), cannot reopen a closed query, and crowds six buttons into the row's action cell. | Each query is **Unassigned** until taken or assigned: the **Assigned to** column carries the compact inline assignee control (`Unassigned ▾` + `Take`), clicking the message **Subject** opens the e-mail, and the action cell carries only `Reply` + `Mark done` (mail), `Mark done` (logged), or `Reopen` (`Done` rows). **Resolve query** leaves the Actions menu; **Next action** reads **Answer query**. Query acts need no edit lease, expected version or reason. (**D**, **J**, **K**, **M**, **O**, **AA**) | `027`–`032` |
| Open queries do not appear as their own rows in the Work Centre. | **Needs attention** gains a `Query` kind chip and one row per open query: Unassigned rows on the Office view with **Take** and **Open query**, and queries assigned to the viewer in **Mine**. **Cases › Queries** keeps one row per Case. (**P**) | `035`–`039` |

## 2. Live rules the mockup mirrors

| Rule | Live source symbol | How v42 mirrors or changes it |
| --- | --- | --- |
| Classification chip set andCase type select on `New instruction` | `MailClassificationSelection.Options`, `MailClassificationSelection.WorkTypeOptions` (`src/Pegasus.Web/Pages/Mail/MailClassificationSelection.cs`) | Four options (`correspondence`, `new-instruction`, `triage-request`, `cancellation`); `WorkTypeOptions` (`Inspection`, `Audit`, `InspectionAndAudit`) stays inside `#mailClassificationForm` when `New instruction` is pressed (**A**, **H**). |
| Case / PO picker and one-step Link / Change linked Case / Unlink dialogs | `MessageModel.OffersLinkToCase`, `OffersChangeLinkedCase`, `IntakeAssociationDestinationPolicy.CanOffer` (`src/Pegasus.Web/Pages/Mail/Message.cshtml.cs`, `_MessageDecision.cshtml`) | Kept unchanged and moved to the top of Decision (**G**). |
| Next action offered by an unlinked message's classification | `MessageModel.Offer`, `ImageIntakeLifecycleRules.IsImageRegistrationEligible` (`Message.cshtml.cs:275`, `src/Pegasus.Core/Intake/ImageIntakeLifecycle.cs:191`) | `New instruction` → `Create case`; `Triage request` → `Open the Triage`; `Correspondence` (no category) with `CanRegisterImages` → `Register images` (**R**). |
| Queries open only once the Case's report is sent, and an open query overlays the Case's stage with purple `Query` | `CaseQueryRules.CanLog`, `CaseQueryRules.IsQueryStage`, `CaseLifecycleRules.ReportIsSent` (`src/Pegasus.Core/Lifecycle/CaseQueryLifecycle.cs:19`) | Renamed `CaseQueryRules.CanOpen`; `QDOS26214` (`ReportSent`) offers `Open query` and shows the purple `Query` chip, while `QDOS26220` (`ReportPreparation`) offers neither (**N**, **AA**). |
| Place on Hold and Close case eligibility on a Case | `Details.Frame.cs` ribbon predicates (`src/Pegasus.Web/Pages/Cases/Details.Frame.cs`) | **Change case** links on the message (`Place on Hold`, `Close case`) are drawn on `message-m11` (`QDOS26220`, `ReportPreparation`, where both dialogs exist on the Case page) and omitted on `QDOS26214` (`ReportSent`, where neither is offered) (**G**). |
| Cancellation notice on the Case aside | `EfCaseQueryStore.ReadLinkedCancellationMessageIdAsync`, `_CaseAside.cshtml` (`Cancellation received`) | Kept unchanged on `case-qdos26220` (**E**). |
| Assign Engineer option order (`Name (you)` first, enabled casework staff, `Unassigned`) | `AssignEngineerViewModel.Label`, `ICaseEngineerChoices` (`src/Pegasus.Web/Pages/Cases/CaseWorkspaceViewModels.cs`) | Reused verbatim by `#case-assign-query-dialog` (**O**). |
| Work Centre `Needs attention` row layout, kind chips and `Take` form | `NeedsAttentionKind`, `NeedsAttentionPolicy`, `_WorkCentreBody.cshtml:339` (`src/Pegasus.Core/Operations/DashboardCounts.cs`, `OperationsSnapshot.cs`) | `NeedsAttentionKind.Query` adds a `Query` chip and row; Unassigned rows carry `data-wc-take` on the Office view, and viewer-assigned rows appear in `Mine` without `Take` (**P**). |
| Automatic mail-to-Case association | `AutomaticMailCaseAssociation.SelectTarget`, `EfIntakeMutationStore.LoadMailAssociationEvidenceAsync` (`src/Pegasus.Core/Intake/AutomaticMailCaseAssociation.cs`) | Widened in Stage 2 (`SelectTarget` v2) to intersect conversation thread, `In-Reply-To`/`References`, Principal claim reference in subject/body, and VRM narrowed by accident date (**F**, **T**–**W**). |

## 3. Frame rules as numbers

Unchanged from v41 (`captured-live/_source/wwwroot/css/site.css`):

| Element | Measurement |
| --- | --- |
| Top utility bar height | `48px` |
| Left navigation rail width | `220px` expanded, `56px` collapsed |
| Message dialog (`.dialog--mail`) max-width | `1080px` Today (with 380px Decision sidebar), `880px` Proposal (full-width body + `364px` cog settings popover) |
| Standard dialog (`.dialog`) max-width | `720px` |
| Compact dialog (`.dialog--compact`, Log query / Assign query) max-width | `480px` |
| Table header (`th`) height | `34px` (`11px` uppercase, `padding: 0 12px`) |
| Table row (`td`) height | `40px` standard, `34px` compact (`.table--compact`) |
| Controls (`input`, `select`, `.btn`) height | `32px` standard, `28px` `.btn--small` |
| Viewports checked and captured | `1580×1000` ( plus whole-page), `1440×900`, `760×1000` |

## 4. Decisions taken and their authority

Settled with the operator on 26 October 2026 before the mockup was built (see
[discussion-log.md](discussion-log.md)):

| Item | Ruling | Authority |
| --- | --- | --- |
| **A** | Categories shrink to three: `New instruction` (Case type `Inspection`, `Audit`, `Inspection and Audit`), `Triage request`, `Cancellation`. Every other e-mail has no category: linked it is Case correspondence, unlinked it is No Case Found. `Pre-instruction`, `Images received`, `Case update`, `Query`, `Billing`, `General`, `Not client related` and `Internal CC` are removed. | Operator, 26 October 2026 |
| **B** | Unlinked non-instruction mail appears **only in No Case Found** (staff link or Dismiss it). **All incoming** lists instructions, triage requests and Case-linked mail. | Operator, 26 October 2026 |
| **C** | Automatic queries: **deterministic criteria (QDOS PAV-dispute sentence) and the AI classifier only**. Any other e-mail joining a Report sent Case is plain correspondence. | Operator, 26 October 2026 |
| **D** | A new query is **Unassigned until taken or assigned**. | Operator, 26 October 2026 |
| **E** | **Keep a cancellation marker** (the `Cancellation` category) with its existing Case aside row and notification, alongside new options to change the Case from the message. | Operator, 26 October 2026 |
| **F** | **Widen linking**: thread (conversation or `In-Reply-To`/`References` to a message already on exactly one Case), Principal claim reference found in subject/body, VRM narrowed by accident date. | Operator, 26 October 2026 |
| **G (cog menu)** | **Replace the `Decision` sidebar on `#mailMessageDialog` with a settings menu (cog icon `#icon-settings`)** in the dialog header over `/Inbox` (emails open in `#mailMessageDialog`, not a standalone page). | Operator, 26 October 2026 |

## 5. Deliberate departures from live, with reasons

1. **Queries section rows on `QDOS26214` (`proposals_case.py`).** In the live capture, `MailboxIntakeTestData.LinkReceiptAsync` updates `IntakeReceipts` directly without calling `CaseQueryLedger.RaiseForMailAsync`, so only the staff-logged `Phone` query row is in `CaseQueries`. To show all three row states the Proposal introduces — an open mail query (`m4`, with `Open message`, `Reply`, `Draft reply with AI`, `Mark done`, `Assign`, `Take`), an open logged query (`Phone`, with `Mark done`, `Assign`, `Take`), and a closed query (`Done`, `WhatsApp`, with `Reopen`) — `proposals_case.py` inserts the `m4` mail row (using `m4`'s real captured message id and dialog target) and one `Done` row.
2. **Queries action cell height (`proposals_case.py`).** In `site.css`, `.table .row-actions` sets `display: flex` on the `<td>` while `.table--compact td` sets `height: 34px`. When an open mail query carries six controls (`Open message`, `Reply`, `Draft reply with AI`, `Mark done`, `Assign`, `Take`), a flex `<td>` fixed at `34px` overflows into the next row. The Proposal injects `[data-queries-table] td.row-actions { display: table-cell; height: auto }` with an inner right-aligned `.cluster`, so the cell stretches naturally with the row. Stage 2 carries the same rule into `site.css` / `_CaseQueries.cshtml`.
3. **Work Centre Query row (`proposals_work.py`).** The shell capture seeds its own database (`ZzMockupCaptureShell.cs`). Rather than inventing a Case reference, the Proposal's Query row points at `QDOS26190` (`Mercedes A180 PO16DDF`), which the shell capture already seeds in `ReportSent` with a `QueryReceived` notification.
4. **Sub-state presets (`build-v42.py`, `proposals_inbox.py`, `proposals_case.py`).** Three states open a sub-state in both Today and Proposal so the comparison is like-for-like: `inbox-rows-ticked` ticks `m2` and `m4`; `case` and `case-qdos26220` open the `Correspondence` tab in `#section-files`; `case-aside-query` opens the ribbon's `Actions` menu.

## 6. Sign-off

Items **A** to **F** are settled (§4) and kept at the head of the list for traceability.
Items **G** to **AA** are open: confirm each item as drawn, or state the change.

- **A** *(Settled 26 October 2026 — three categories: New instruction with Case type, Triage request, Cancellation; everything else is uncategorised Case correspondence when linked and No Case Found when unlinked.)*
- **B** *(Settled 26 October 2026 — unlinked non-instruction mail appears only in No Case Found; All incoming lists instructions, triage requests and Case-linked mail.)*
- **C** *(Settled 26 October 2026 — automatic queries come from deterministic criteria and the AI classifier only; linking an e-mail to a Report sent Case opens no query by itself.)*
- **D** *(Settled 26 October 2026 — a new query is Unassigned until taken or assigned.)*
- **E** *(Settled 26 October 2026 — keep the Cancellation category, its Case aside row and its notification alongside the new Change case options.)*
- **F** *(Settled 26 October 2026 — widen automatic linking to conversation thread or In-Reply-To/References, Principal claim reference in subject/body, and VRM narrowed by accident date.)*
- **G** *(Cog settings menu settled 26 October 2026 — `#mailMessageDialog` replaces the right-hand `Decision` column with the `#icon-settings` cog menu in `.mail-dialog-tools` and a quiet metadata line above the full-width message.)* Confirm the order inside the cog menu (**Case**, **Type**, **Query**, **Change case**) and that **Change case** items (**Place on Hold**, **Close case**) open `/Cases/{id}?dialog=case-hold-dialog|case-close-dialog`, shown only when the linked Case allows the act, or specify another order or interaction.
- **H** *(1-step selector settled 26 October 2026 — the clicky chip cloud is replaced by a single streamlined `Type` `<select>` combining `Correspondence`, `New instruction · Inspection`, `New instruction · Audit`, `New instruction · Inspection and Audit`, `Triage request` and `Cancellation`.)* Confirm the label **Type** and the combined option labels, or give others.
- **I** *(Three Inbox scopes and Principal/Mailbox filters settled 26 October 2026 — `Sent Items`, `Deleted Items`, the `Category` select and bulk `Correct classification` are removed; `/Inbox` uses a full-width ledger with **All**, **No Case Found** and **Dismissed** `.tabs`, **All principals** and **All Mailboxes** filters, and a contextual bulk **Dismiss** / **Restore** bar shown when rows are ticked.)* Confirm as drawn, or state any filter change.
- **J** Confirm that query acts (open, mark done, reopen, assign) need no Case edit lease, no expected Case version and no reason, so a colleague editing the Case does not block them, or specify which gate should remain.
- **K** Confirm that per-query **Mark done** (closing to the green **Done** chip and **Done** column) replaces **Resolve query** (which closed every open query at once), that **Resolve query** leaves the Actions menu, and that **Next action** reads **Answer query** with **Reply** (when the oldest open query is an e-mail) or **Mark done** (when logged), or specify different wording.
- **L** Confirm that the reply composer's `Also resolve query` checkbox becomes **Mark query done**, offered only when replying to an e-mail that holds an open query, and marks only that e-mail's query done when the Sent item is observed, or specify another rule.
- **M** Confirm that **Reopen** on a **Done** query row is open to any staff role (`Administrator`, `Engineer`, `User`) and the `Automation` actor, with no reason, while the Case is not archived or closed, or restrict who may reopen.
- **N** Confirm one query per e-mail: **Open query** is offered on a linked e-mail (in the Inbox Decision panel and in Case **Correspondence**) when the Case's report is sent and the e-mail holds no query, while an e-mail whose query is **Done** offers **Reopen** in the **Queries** section instead, or allow multiple queries per e-mail.
- **O** Confirm the **Assign query** dialog (`Assigned to` listing the signed-in person first as `Name (you)`, then enabled casework staff, then `Unassigned`), the one-click **Take** button on open rows not already assigned to the viewer, and notifying the assignee (`Query assigned`) when a query is assigned to someone else, or specify another assignment flow.
- **P** Confirm Work Centre **Needs attention** rows for open queries: Unassigned open queries on the Office view with **Take** and **Open query**, queries assigned to the viewer in **Mine**, and **Cases › Queries** keeping one row per Case, or specify another Work Centre treatment.
- **Q** Confirm that `Query received` still notifies the Case's assigned Engineer when a query is opened from an e-mail, or change the notification recipient.
- **R** Confirm that removing `Images received` offers **Register images** on any image-only, unlinked e-mail with no instruction, triage or cancellation type (`Type = Correspondence`), or state another eligibility rule.
- **S** Confirm that QDOS operational notices (garage allocation, repairs authorised, report chase) and automatic replies are no longer given a category label and become plain correspondence, while the QDOS PAV-dispute sentence becomes a deterministic query criterion (`OpensQuery = true`), or keep a label for any of them.
- **T** Confirm that reply-header linking (`In-Reply-To` and `References`) matches a retained received message or Pegasus Sent item in any approved mailbox whose Case is unique, or restrict it to the same mailbox.
- **U** Confirm that claim-reference linking matches any token in the subject or current body equal to a single non-archived Case's indexed claim reference across all Principals (changing FRD-09's "never from free text" restriction), or keep it Principal-restricted.
- **V** Confirm that when a VRM matches several Cases and the message carries an accident date, candidates whose accident date differs are dropped and candidates with an equal accident date win when that leaves one Case (changing FRD-22's "excluding rule, not a matching rule"), or keep VRM-only matching.
- **W** Confirm that when multiple linking signals are present (thread, reply headers, claim reference, VRM + accident date), every non-empty signal set must contain the chosen Case (intersection) so a broader signal no longer vetoes a narrower one that agrees with it, or require every signal to be single-valued.
- **X** Confirm that the Case **Correspondence** table column `Classification` becomes **Type** and displays the e-mail's query chip (`Query` or `Done`) beside the type text, or keep query state only in the **Queries** section.
- **Y** Confirm that unlinking an e-mail from a Case withdraws its open query (`ClosedAs = Withdrawn`) and that no separate withdraw button is offered, or add a manual withdraw action.
- **Z** Confirm that the Engineer activity report's `Queries` column and the Case list's query count count `CaseQueries` records (any source, not withdrawn) rather than `Query`-classified e-mails, or specify another metric definition.
- **AA** Confirm that `Query` remains the purple stage word over the Case's stored state while any query is open (returning to `Report sent` once the last open query is marked done) and that queries open only once the report is sent (`CaseLifecycleRules.ReportIsSent`), or allow pre-report queries.

## 7. Self-check result

`python build/build-v42.py && python build/pagedocs-v42.py && python build/check-v42.py`
run on **26 October 2026** against captures from `origin/dev` `373dcc81aedd7ff1415090b4fb50486652ebc595`:

- **Result:** `RESULT {"fail": [], "okCount": 340}`, zero page or console errors.
- **States:** 20 states registered in `build/states_v42.py`; 19 have a Proposal (`cases-query` is captured unchanged to show **P**'s one-row-per-Case invariant).
- **Screenshots:** 156 PNG files in `shots/` (`001`–`039` across `1580×1000`, `1580` whole page, `1440×900` and `760×1000`) plus `shots/verification.json`.
## 8. Known limits

- Captured fixtures are synthetic (`ZzMockupCaptureInbox.cs`, `ZzMockupCaptureIntake.cs`, `ZzMockupCaptureShell.cs`). The staff-logged `Phone` query on `QDOS26214` carries the test store's clock (`06 May 2031 11:30`) and the offline administrator username (`development-offline-administrator`), while the shell lane signs in as `e.mawdsley`.
- All twelve seeded emails (`m1`–`m12`) are interactively openable from `/Inbox` in `#mailMessageDialog`, with working `Previous`/`Next` buttons, `Message`/`Attachments`/`Thread` tabs, `Reply`/`Reply all`/`Forward` composer, and live cog settings menu actions (`Type` chips, `Case / PO` autocomplete and Link/Change/Unlink, `Open query`/`Mark done`, `Dismiss`, search and sort). Uncaptured routes outside the 19 states display a toast.
- Photographs served by application handlers render as a grey placeholder image.
- Linking v2 (**F**, **T**–**W**: reply headers, claim reference in subject/body, VRM narrowed by accident date, signal intersection) runs inside `EfIntakeMutationStore` / `AutomaticMailCaseAssociation` during intake and has no separate UI surface beyond the resulting Case link on the message.
