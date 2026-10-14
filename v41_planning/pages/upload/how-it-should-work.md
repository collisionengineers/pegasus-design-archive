# Upload & Upload Review: how it should work (v41 proposal)

## Proposed design, UI & UX improvements

- **Item K (`f19`)**: Adds the `Files` eyebrow to `Upload.cshtml` and removes `.up-subtitle` and all six `.up-explainer` paragraphs from `_UploadReview.cshtml`.
- **Tier `a`/`c` (`f20`)**: Places `.up-inspector` first and `.up-decision` second in DOM order (matching visual left-to-right order), removes the duplicate `form.submit()` fallback on HTTP status errors in `upload.js`, and preserves `inspect` when opening `Find another Case`.

## Interactive comparison

Open [`pegasus_shell_v41.html`](../../current/pegasus_shell_v41.html) at `?state=upload-review&design=proposal` and toggle **Proposal** vs **Today** in the bottom-left Mockup controls strip.

See [../../current/v41-notes.md#6-sign-off-list](../../current/v41-notes.md#6-sign-off-list) for the lettered sign-off items.
