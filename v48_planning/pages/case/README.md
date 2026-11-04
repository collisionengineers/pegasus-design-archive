# Case record: Report delivery and the aside

- **Mockup route:** `pegasus_v48.html?state=<key>` (keys in [states](states/README.md)).
- **Live source:** `src/Pegasus.Web/Pages/Cases/Details.cshtml`, `Details.cshtml.cs`,
  `Details.Report.cs`, `Details.Views.cs`, `Pages/Cases/Shared/_CaseReport.cshtml`,
  `_CaseAside.cshtml`, `_CaseDialogs.cshtml`, `_CaseViewer.cshtml`; `wwwroot/js/site.js`
  (dialogs), `wwwroot/js/case-workspace.js` (the delivery form, the viewer, in-place posts);
  `wwwroot/css/case-workspace.css`, `site.css`. Read at `origin/dev` `8da7957ce`.
- [Dialogs](dialogs/README.md) · [States](states/README.md) · [Panels](panels/README.md)
- [How it works](how-it-works.md) · [How it should work](how-it-should-work.md)

## Screenshots

See [../../notes/v48-notes.md §1](../../notes/v48-notes.md#1-what-changes) for the shot numbers
per change, and `../../shots/verification.json` for the full list.

## Notes

The Report section is drawn in every state; the aside's Original report card only on the
Audit view of the Inspection + Audit captures. Today of a dialog state is the inline form,
shot once on `plain-dialog`.
