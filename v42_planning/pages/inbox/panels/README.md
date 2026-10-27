# Inbox — panels

| Panel | Source | v42 Proposal |
| --- | --- | --- |
| Scope rail (`.scope-list`) | `Pages/Mail/Index.cshtml` | `All incoming` lists instructions, triage requests and Case-linked mail; unlinked correspondence waits in `No Case Found` (**B**). |
| Filter bar (`form.inbox-filter`) | `Pages/Mail/Index.cshtml` | `Category` select (`#queue-filter`) removed; 3-column grid keeps `Mailbox`, full-width `Search` input and compact `Search` button (**I**). |
| Bulk bar (`form#mail-bulk`) | `Pages/Mail/Index.cshtml` | `Correct classification` button removed; `Dismiss` (and `Restore` in Dismissed) remains (**I**). |
| Message settings cog menu (`[data-mail-settings]`) & context bar (`[data-mail-context-bar]`) | `Pages/Mail/Shared/_MessageDialog.cshtml`, `_MessageDecision.cshtml` | Replaces the right-hand `Decision` column on `#mailMessageDialog`: `.mail-context-bar` shows **Case**, **Type** and **Query** pills at a glance above the full-width message; clicking the `#icon-settings` cog button opens the popover ordered **Case** (with Case / PO picker and Link / Change linked Case / Unlink), **Type** (four chips: `Correspondence`, `New instruction` with Case type select, `Triage request`, `Cancellation`), **Query** (`Open query` or `Query` chip + `Unassigned`/assignee + `Mark done`), **Change case** (`Place on Hold`, `Close case`), **Decided** (**A**, **C**, **E**, **G**, **H**, **K**, **N**). |
| Reply composer | `Pages/Mail/Shared/_MessageRecord.cshtml` | `Also resolve query` checkbox renamed **Mark query done**, offered only when replying to an e-mail that holds an open query (**L**). |
