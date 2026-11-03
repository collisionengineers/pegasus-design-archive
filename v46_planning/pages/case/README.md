# Case record: Damage and the impacts

- **Mockup:** [`pegasus_v46.html`](../../pegasus_v46.html), states `damage-*` and `wording-*`
- **Live source:** `src/Pegasus.Web/Pages/Cases/Shared/_CaseDamage.cshtml`,
  `src/Pegasus.Web/wwwroot/js/case-workspace.js` (damage editor), `_CaseReport.cshtml`
  (Pegasus `origin/dev` `fb4c5e741`)
- **Dialogs:** [`dialogs/`](dialogs/README.md) · **States:** [`states/`](states/README.md) · **Panels:** [`panels/`](panels/README.md)
- [**How it works**](how-it-works.md) · [**How it should work**](how-it-should-work.md)

## Screenshots

The shots are in [`../../shots/`](../../shots/).

- Each `NNN-<state>-<mode>-<width>.png` is the viewport.
- `…-panel.png` is the Damage section, or the Report wording panel for the `wording-*` states.
- `…-full.png` is the 1580 whole page.

The states table in [`states/`](states/README.md) gives each state's numbers.

## Notes

Live derives Multiple even for the two-damage fixture. Its RH Rear and Rear damages, recorded by
area alone, have discs that do not touch. This is the behaviour the round removes.
