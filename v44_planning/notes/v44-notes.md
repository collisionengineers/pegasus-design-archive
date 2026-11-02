# v44 notes: Message settings, Case linking clean-up

Round opened 2 November 2026. Live source read from Pegasus `origin/dev` `b78a4f63c`
(`build/live/source.txt`). The cog menu was settled as v42 D6 (item G, 26 October 2026);
this round changes its presentation only.

## 1. What is wrong today

The operator's screenshot shows the linked state. Every item below is reproduced in
`shots/001-today-linked-*.png`.

| # | What the operator sees | Cause in live source |
| --- | --- | --- |
| T1 | `Unlink` is a boxed browser-default button squeezed beside the reference | `.mail-settings-link` has no CSS rule anywhere |
| T2 | `Change linked Case` is a grey full-width bar that reads as a disabled field | `button.mail-settings-item` gets layout CSS but no button reset; the `<a>` items with the same class render as links |
| T3 | An empty `Case / PO` box sits under a Case that is already linked, with nothing tying it to Change linked Case | The picker posts into the dialog's form through `form="changeLinkedCaseForm"`, so it has to stay visible and apart from its button |
| T4 | Three label styles: `Case` 10px muted, `Case / PO` 11px weight 780, `Type` 10px muted | `.field label` (0,1,1) beats `.mail-decision-label` (0,1,0); `Case` is a `.decision-row` span |
| T5 | `Change case` (hold or close the Case) sits directly under `Change linked Case` (move the e-mail) | Two different acts with nearly the same words |
| T6 | Sections run together | `.mail-settings-popover` is a 10px-gap grid with no dividers; `.mail-settings-section`, `.mail-settings-row-head` and `.mail-settings-foot` have no CSS |
| T7 | `Decided` and the time run into one label/value pair with no separation | `.mail-settings-foot` has no CSS |

## 2. Proposal

- **Case section:** the label `Case`, then a single row holding the reference (or `None`)
  and its actions as `btn--small` buttons: `Change linked Case` and `Unlink` when linked,
  `Link to Case` when not. The popover has no input.
- **Case / PO picker:** pressing Change linked Case or Link to Case opens the existing
  reason dialog. The `Case / PO` picker now sits in that dialog above `Reason for action`
  and gets initial focus. It is the same picker (`[data-case-picker]`, `_CaseOptions`
  list), moved. The number of steps is unchanged: live is type → button → reason; the
  proposal is button → type → reason.
- **Type:** unchanged.
- **Query:** labelled `Query` like every other section. Its single button is unchanged
  (`Mark query done` or `Open query`). The context bar already shows the query chip, so
  the popover does not repeat it.
- **Change case:** `Place on Hold` and `Close case` as `btn--small` buttons in a row. Same
  targets (`/Cases/{id}?dialog=hold|close`) and same availability rules.
- **Decided:** a muted 11px footer line, `Decided 02 Nov 2026 12:35 · Automatic`.
- **One look:** every section label is `.mail-decision-label` (10px, weight 400, muted),
  and a 1px `--line` divider sits between sections. No new token, colour, icon or copy
  is introduced.
- **Dialogs:** Unlink is unchanged. The approved consequence sentence
  `Unlinking this email cancels case {ref}.` still appears where unlinking cancels the
  Case.

The proposal CSS is the `#proposal-css` block in `build/template-v44.html`. In Stage 2 it
replaces the live `.mail-settings-*` rules in `inbox.css`.

### Variables (strip)

| Variable | Options | Default |
| --- | --- | --- |
| `picker` (A) | `dialog`: picker in the reason dialog · `inline`: picker opens in the popover after Change, with Cancel and the confirm button | `dialog` |
| `changelabel` (B) | `Change linked Case` (live) · `Change` | `Change linked Case` |
| `caseactions` (D) | `buttons` · `links` (live) | `buttons` |

## 3. Frame numbers

- Popover width 364px, as live. Section padding 10px 0, gaps 6px, and 32px small
  controls (`btn--small`), all on the design authority's spacing rhythm.
- Section label 10px/400 `--muted`; footer 11px `--muted`; reference 13px/600.
- At 760px the popover stays inside the viewport and the page does not spill
  (self-checked).

## 4. Departures and limits

- **Today is transcribed, not captured.** The live Razor markup was copied into the
  template and drawn with the live CSS, the Lucide sprite and Inter. No running
  application was used. The operator's screenshot is the live reference;
  `shots/001-today-linked-1440.png` matches it in label weights, the boxed Unlink, the
  grey bar and the empty input.
- The message dialog is drawn in reduced form: subject, route line, context bar, the
  tools and a short body. Tabs, attachments and the record foot are not part of this
  round.
- The self-check is a Python Playwright script (`build/check-v44.py`), as v42 used,
  rather than an HTML `selfcheck` page.
- The fixtures are synthetic: references `a.QDOS26157` (taken from the operator's
  screenshot), `QDOS26149`, `t.QDOS26160` and picker candidates `QDOS26162` and
  `QDOS26163`.
- Triage state: the Change case and Query rules follow live (`CurrentCase` is null for a
  Triage, so neither section draws). Whether Change linked Case is offered for a Triage
  is Core's `CanOfferToChange`; the mockup shows it.

## 5. Sign-off

Settled by the operator on 2 November 2026 (rulings R607–R612 in the application
repository's `docs/rulings.md`). The operator's words: "B - shorten", "c - keep",
"E = yes", "F = yes", "use recommendeds for any other answers".

| Item | Outcome |
| --- | --- |
| A | Recommended: picker in the Link to Case and Change linked Case dialogs (R607) |
| B | **Shorten**: the menu button reads `Change`; the dialog keeps `Change linked Case` (R608) |
| C | **Keep** `Change case` (R609) |
| D | Recommended: small buttons in a row (R610) |
| E | **Yes** (R611) |
| F | **Yes** (R612) |

The list as raised:

- **A** — Confirm that the `Case / PO` picker moves into the Link to Case and Change linked
  Case reason dialogs, so the cog menu shows no input (amends v42 D6). Or keep it in the
  menu, shown only after Change linked Case or Link to Case is pressed (variable
  `picker:inline`).
- **B** — Confirm that the menu button keeps the live label `Change linked Case`. Or
  shorten it to `Change` (the dialog title stays `Change linked Case`).
- **C** — The heading `Change case` (Place on Hold, Close case) sits under
  `Change linked Case` and the two read alike. Confirm keeping `Change case`, or give
  the label to use. The round does not propose one.
- **D** — Confirm that `Place on Hold` and `Close case` become small buttons in a row. Or
  keep the live link list (variable `caseactions:links`).
- **E** — Confirm one label style and a divider between sections, with `Decided` as a
  muted footer line.
- **F** — Confirm that the Query section carries the label `Query` and shows only its
  button. The chip stays in the context bar.

## 6. Self-check record

- 2 November 2026: `RESULT {"fail":[],"okCount":516}`, no console errors. Covers every
  state × variable combination, the three dialogs, the Change and Link flows, the
  unlink consequence rule, divider and label-style checks, the 760px viewport and the
  strip. Screenshots: 48 (`shots/verification.json`).

## 7. Stage 2 conformance (2 November 2026)

Pegasus `task/v44-mail-link-settings` (commits `b431dadb1`, `2b0e46b9b`). The routed
Inbox message dialog was served by a scratch Kestrel host over the integration-test
fixtures (four states) and driven with Playwright. Shots are in `shots/live/`, named
after the mockup shot of the same number (`002`, `004`, `006`, `008`–`011`) at 1580, 1440
and 760, plus `009b` (the picker's live options in the Change linked Case dialog).
`shots/live/conformance.json` records the result: no failures and no console errors.
It checked that:

- the menu has no field;
- the menu uses one label style, with dividers;
- each state shows the expected buttons: Change, Unlink, Place on Hold and Close case
  when linked; Link to Case when unlinked; Mark query done with a query; no Change case
  on a Triage;
- the picker in the Change linked Case dialog has initial focus, comes before Reason,
  lists the Case from the live `LinkCaseOptions` handler, fills on choice and returns
  focus to the field;
- at 760px the menu stays inside the viewport.

The walk found one defect in the picker script: choosing an option re-entered
`close()` through `focusout`, which threw and dropped focus. Inside a dialog, focus
left the modal. It is fixed in `2b0e46b9b`.

Differences from the mockup:

- The fixtures name their own subjects and references (`MAIL44001`), not the mockup's
  synthetic ones.
- The fixture's linked Case was not created by its message's acceptance, so the
  Change linked Case dialog carries no consequence sentence there. The rule is
  unchanged.
- The query state was reached by pressing `Open query` in the menu (Case in Report
  sent).

## 8. Stage 2 (delivered)

- `src/Pegasus.Web/Pages/Mail/Shared/_MessageDecision.cshtml`: the Case row with
  `btn--small` actions and no inline picker (A); Query and Change case as sections
  (D, F); the Decided footer (E).
- `src/Pegasus.Web/Pages/Shared/_ReasonDialog.cshtml` and
  `src/Pegasus.Web/Pages/Mail/Shared/_MessageNested.cshtml`: the Link to Case and Change
  linked Case dialogs draw the `Case / PO` picker in their body. This replaces the
  `DialogFormId` external-field hook, whose only consumer is this picker (grep before
  removing).
- `src/Pegasus.Web/wwwroot/css/inbox.css`: the `#proposal-css` rules, replacing the live
  `.mail-settings-*` rules (T1, T2, T6, T7).
- `tests/Pegasus.IntegrationTests/MailWorkspaceWebTests.cs`: the `mailLinkCaseReference`
  assertions move to the dialog markup.
- The owning FRD clause (Inbox message settings) and a `docs/rulings.md` row for each
  settled item.
- Follow `pegasus-ui-guardrails` and `razor-html-mockup-conversion`.
