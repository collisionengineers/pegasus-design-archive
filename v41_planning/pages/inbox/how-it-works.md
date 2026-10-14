# Inbox & Message Record: how it works today (`origin/dev`)

## Source files

- `src/Pegasus.Web/Pages/Mail/Index.cshtml` (`.cs`), `Message.cshtml` (`.cs`), `Shared/_MessageBody.cshtml`, `Shared/_MessageContent.cshtml`
- `src/Pegasus.Web/wwwroot/css/inbox.css`

## Current behaviour and audit findings

- `/Inbox` (`Mail/Index.cshtml:47-105`) puts `Sent Items` in both the left scope rail AND the `Folder` dropdown, puts `No Case Found` in both the left scope rail AND the `Category` dropdown, puts `Deleted Items` only inside `Folder`, and breaks the 5-column `.inbox-filter` grid when `Dismissed` hides `Folder`.
- Empty `Sent Items` renders an empty `<div class="empty"></div>`; `Deleted Items` header always says `0 messages`; `.inbox-layout.pane-layout--3` stays 3 columns down to `761px`.
- `/Inbox/{id}` (`Mail/Message.cshtml`) prints `Subject` 3 times vertically, prints the linked Case reference twice in `Decision` (`Destination` and `Filed to`), uses a forbidden `.provenance` tooltip icon, prints raw MIME strings (`application/pdf`) in `Attachments`, lacks a `Cancel` link on the inline reply composer, and requires a two-step server round-trip (`PrepareUnlinkCase` / `PrepareLinkCase`) that acquires a Case edit lease on the first click, reloads the page, and requires a second click to open `#unlinkCaseDialog` / `#linkCaseDialog`.

See [../../current/v41-notes.md](../../current/v41-notes.md) for the complete `f01`–`f39` table and exact file/line citations.
