# Inbox message settings: how it should work (proposal)

Status: proposed on 2 November 2026; items A–F are open
([notes §5](../../notes/v44-notes.md#5-sign-off)). Behaviour, availability rules and
handlers are unchanged from [how-it-works.md](how-it-works.md); only the presentation
changes.

## Menu

1. **Case** (label). One row:
   - linked: the reference link, then `Change linked Case` and `Unlink` as `btn--small`
     buttons (A, B);
   - not linked: `None`, then `Link to Case` as a `btn--small` button.

   The menu has no input (A).
2. **Type** (label). Unchanged.
3. **Query** (label). Shows only when it applies, holding its one `btn--small` button
   (F).
4. **Change case** (label; C). Holds `Place on Hold` and `Close case` as `btn--small`
   buttons in a row (D).
5. A footer line: `Decided {time} · {actor}`, muted (E).

There is a 1px divider between sections, and every section label uses one style (E).

## Dialogs

- `Link to Case` and `Change linked Case` hold the `Case / PO` picker, with initial
  focus, above `Reason for action` (A).
- `Unlink` is unchanged.

## Evidence

Mockup screenshots `shots/002`, `004`, `006`, `008`–`011` and `013`–`016`. Self-check:
see [notes §6](../../notes/v44-notes.md#6-self-check-record).
