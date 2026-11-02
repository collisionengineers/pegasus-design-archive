# Inbox message settings: how it works (live)

Read 2 November 2026 from Pegasus `origin/dev` `b78a4f63c`.

## Where

The message dialog (`_MessageDialog.cshtml`) draws `_MessageDecision.cshtml` twice:

- once as `bar`: the `.mail-context-bar` under the route line, showing Case, Type and the
  query chip;
- once as `menu`: the `details[data-mail-settings]` cog in `.mail-dialog-tools`.

The reason dialogs come from `_MessageNested.cshtml` and sit beside the record.

## Menu contents, in order

1. **Case.** A `.decision-row` showing `Case` and the reference link. When linked it
   adds ` · ` and an `Unlink` button (`.mail-settings-link`, which opens
   `unlinkCaseDialog`); when not linked it shows `None`.
   - If `OffersLinkToCase || OffersChangeLinkedCase`, the menu adds a `Case / PO`
     combobox (`#mailLinkCaseReference`, `[data-case-picker][data-case-picker-fill]`,
     options from the `LinkCaseOptions` handler). The combobox posts into the dialog
     form through `form="linkCaseForm"` or `form="changeLinkedCaseForm"`.
   - Under it is one `.mail-settings-item` button: `Change linked Case` (opens
     `changeLinkedCaseDialog`) or `Link to Case` (opens `linkCaseDialog`).
2. **Type.** The `#mailTypeSelect` form posts `CorrectClassification` on change; a
   noscript Save button is the fallback.
3. **Query.** Shown when linked and not a Triage. It holds `Mark query done` (open query)
   or `Open query` (none yet, `CaseQueryRules.CanOpen`).
4. **Change case.** Shown when `OffersPlaceOnHold || OffersCloseCase`. It holds the links
   `Place on Hold` and `Close case` to `/Cases/{id}?dialog=hold|close`.
5. **Decided.** `.mail-settings-foot`: `Decided`, then the office time and `Automatic`
   or the actor's name.

## Dialogs

- `unlinkCaseDialog`: titled `Unlink from {ref}`, with Reason. It shows
  `Unlinking this email cancels case {ref}.` when `UnlinkCancelsCase`.
- `changeLinkedCaseDialog`: titled `Change linked Case`, with Reason and the same
  consequence sentence. On the server it runs Unlink and then Link (`OnPostChangeLinkedCaseAsync`).
- `linkCaseDialog`: titled `Link to Case`, with Reason.

All three use `_ReasonDialog.cshtml`.

## Styling

`inbox.css` styles only `.mail-settings-popover`, `.mail-settings-list`,
`.mail-settings-item`, `.mail-type-select` and `.mail-decision-label`. These classes
have no rule anywhere: `.mail-settings-link`, `.mail-settings-section`,
`.mail-settings-row-head` and `.mail-settings-foot`. `.field label` overrides
`.mail-decision-label` on the `Case / PO` label.
