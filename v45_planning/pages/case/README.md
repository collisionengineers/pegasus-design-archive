# Case record: Report wording

- **Mockup:** [`pegasus_v45.html`](../../pegasus_v45.html), states `case-*` and `valuation-*`
- **Live source:** `src/Pegasus.Web/Pages/Cases/Shared/_CaseReport.cshtml`,
  `_CaseValuation.cshtml` (Pegasus `origin/dev` `f6de68d1a`)
- **Dialogs:** [`dialogs/`](dialogs/README.md) · **States:** [`states/`](states/README.md) · **Panels:** [`panels/`](panels/README.md)
- [**How it works**](how-it-works.md) · [**How it should work**](how-it-should-work.md)

## Screenshots

The shots are in [`../../shots/`](../../shots/).

- Each `NNN-<state>-<mode>-<width>.png` is the viewport.
- `…-panel.png` is the Report wording panel, or the Valuation section for the `valuation-*`
  states.
- `…-full.png` is the 1580 whole page.

The states table in [`states/`](states/README.md) gives each state's numbers.

## Notes

The Today view of the `case-switches-*` and `case-edit-columns` states adds two things the
capture's fake projection leaves out but live draws: the PAV commentary block and the Glass's
guide sentence. See [v45-notes §8](../../notes/v45-notes.md#8-known-limits).
