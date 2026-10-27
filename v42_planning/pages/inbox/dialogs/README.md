# Inbox — dialogs

| Dialog | Today | v42 Proposal |
| --- | --- | --- |
| `#mailMessageDialog` (`_MessageDialog.cshtml`) | 1080px dialog mounted in `[data-mail-dialog-root]` over `/Inbox`, split into `.mail-read` on the left and a 380px `Decision` sidebar (12 `Classification` chips) on the right. | 880px full-width reading dialog: the right-hand `Decision` sidebar is replaced by the **cog settings menu (`#icon-settings`, `[data-mail-settings]`)** in `.mail-dialog-tools` and an at-a-glance `.mail-context-bar` strip in `.dialog-head` (**G**, **H**). |
| `#bulkClassifyDialog` (`Correct classification` for ticked rows) | Opened by `[data-bulk-classify]` on `/Inbox`; selects one of 12 classifications, optional Case type and a reason. | **Removed** (**I**). Bulk `Dismiss` and `Restore` remain. |
| `#linkCaseDialog`, `#changeLinkedCaseDialog`, `#unlinkCaseDialog` | One-step reason confirmation dialogs joined by `form="…"` to `#mailLinkCaseReference` (`_MessageNested.cshtml`). | Unchanged. |
| `#messageTriageDialog` (`Open the Triage`) | Offered when `Category == TriageRequest` and `Offers.CanOpenTriage`. | Unchanged. |
| `#messageRegisterImagesDialog` (`Register images`) | Offered only when `Category == ImagesReceived` and `Offers.CanRegisterImages`. | Offered when the e-mail is unlinked, has `Type = Correspondence` (no category) and `Offers.CanRegisterImages` (**R**). |
| `case-hold-dialog`, `case-close-dialog` (on `/Cases/{id}`) | Opened from the Case page's `Actions` menu. | Also opened on load when reached from the message Decision panel's **Change case** links (`/Cases/{id}?dialog=case-hold-dialog\|case-close-dialog`, **G**). |
