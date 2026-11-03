# Case record: Damage impacts, Skip impacts and the readiness item

- **Mockup:** [`pegasus_v47.html`](../../pegasus_v47.html), all eight states
- **Live source:** `src/Pegasus.Web/Pages/Cases/Shared/_CaseDamage.cshtml`,
  `src/Pegasus.Web/wwwroot/js/case-workspace.js` (`bindImpacts`), `_CaseAside.cshtml`,
  `src/Pegasus.Core/Assessment/AssessmentPolicy.cs` (`Evaluate`), from Pegasus `origin/dev`
  `7231a4b37`
- **Dialogs:** [`dialogs/`](dialogs/README.md) · **States:** [`states/`](states/README.md) · **Panels:** [`panels/`](panels/README.md)
- [**How it works**](how-it-works.md) · [**How it should work**](how-it-should-work.md)

## Screenshots

The shots are in [`../../shots/`](../../shots/).

- Each `NNN-<state>-<mode>-<width>.png` is the viewport.
- `…-panel.png` is the Damage section.
- `…-full.png` is the 1580 whole page, with the aside's Next action.

The states table in [`states/`](states/README.md) gives each state's numbers.
