# Case — dialogs

| Dialog | Today | v42 Proposal |
| --- | --- | --- |
| `#case-log-query-dialog` (`Log query`) | Opened from the `Actions` menu once the report is sent and no colleague holds the edit lease; posts `Closure?handler=LogQuery` with `expectedVersion`. | Posts `Details?handler=LogQuery` without an edit lease or expected version (**J**). |
| `#case-assign-query-dialog` (`Assign query`) | Does not exist. | New compact dialog (`dialog--compact`) opened by `Assign` on an open query row; `<select name="assignee">` labelled **Assigned to** lists the viewer first (`Name (you)`), then enabled casework staff, then `Unassigned`; Cancel / Assign (**O**, **J**). |
| `#case-hold-dialog`, `#case-close-dialog` | Opened from the Case's `Actions` menu when eligible. | Also auto-opened on page load when the URL query string carries `?dialog=case-hold-dialog` or `?dialog=case-close-dialog` from the Inbox Decision panel's **Change case** links (**G**). |
| `case-message-<id>` | Opens a linked correspondence or query e-mail in a dialog over the Case workspace (`_CaseMessageDialog.cshtml`). | Unchanged. |
