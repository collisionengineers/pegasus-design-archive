# Work Centre — dialogs

No dialog on the Work Centre is added or changed by v42. Assigning a query to someone other than the viewer uses `#case-assign-query-dialog` on `/Cases/{id}?section=queries` (see [`../../case/dialogs/`](../../case/dialogs/README.md)); taking an Unassigned query from the Work Centre posts `/?handler=TakeQuery` directly (`data-wc-take`).
