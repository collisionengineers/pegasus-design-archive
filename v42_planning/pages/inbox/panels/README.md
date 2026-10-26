# Inbox — panels

| Panel | Source | v42 Proposal |
| --- | --- | --- |
| Scope rail (`.scope-list`) | `Pages/Mail/Index.cshtml` | `All incoming` lists instructions, triage requests and Case-linked mail; unlinked correspondence waits in `No Case Found` (**B**). |
| Filter bar (`form.inbox-filter`) | `Pages/Mail/Index.cshtml` | `Category` select (`#queue-filter`) removed; `Mailbox` and `Search` remain (**I**). |
| Bulk bar (`form#mail-bulk`) | `Pages/Mail/Index.cshtml` | `Correct classification` button removed; `Dismiss` (and `Restore` in Dismissed) remains (**I**). |
| Message Decision (`section.mail-decision`) | `Pages/Mail/Shared/_MessageDecision.cshtml` | Ordered **Case** (with Case / PO picker and Link / Change linked Case / Unlink), **Type** (four chips: `Correspondence`, `New instruction` with Case type select, `Triage request`, `Cancellation`), **Query** (`Open query` or `Query` chip + `Unassigned`/assignee + `Mark done`), **Change case** (`Place on Hold`, `Close case`), **Decided** (**A**, **C**, **E**, **G**, **H**, **K**, **N**). |
| Reply composer | `Pages/Mail/Shared/_MessageRecord.cshtml` | `Also resolve query` checkbox renamed **Mark query done**, offered only when replying to an e-mail that holds an open query (**L**). |
