# Upload — Dialogs

The initial `/Upload` screen (`is-choosing` phase) opens no modal dialogs of its own; validation errors render inline in `[data-select-errors]` (`.up-alert--error`). Confirmation and discard dialogs (`#up-confirm`, `#up-discard`, `#up-preview`) belong to the post-upload review screens (`UploadGroupStatus.cshtml` and `UploadStatus.cshtml`), which are unchanged in v42.
