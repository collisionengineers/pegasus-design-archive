# v44 discussion log

## 2 November 2026 — brief

The operator attached a screenshot of the message dialog's cog menu in the linked state
(`a.QDOS26157`, `New instruction · Audit`, Decided 02 Nov 2026 12:35 · Automatic):

> examine this image — this relates to the "linking" settings in an emails dialogue
> window. This could be cleaned up and the UX enhanced. Think on this and create a new
> design/view.

Work done:

- Read `_MessageDecision.cshtml`, `_MessageNested.cshtml`, `_ReasonDialog.cshtml`,
  `inbox.css` and `site.css` at `origin/dev` `b78a4f63c`, and the v42 D6/G record.
- Traced every visual defect to its CSS cause (notes §1, T1–T7). Four of the classes the
  menu uses have no rule at all.
- Built the mockup with Today and Proposal views, four states and three variables. Raised
  items A–F.

Open: A–F.

## 2 November 2026 — sign-off

> B - shorten
> c - keep
> E = yes
> F = yes
> use recommendeds for any other answers. proceed to /razor-html-mockup-conversion

Settled: A dialog picker, B `Change`, C keep `Change case`, D buttons, E yes, F yes.
The mockup default for `changelabel` is now `Change`. Stage 2 began on Pegasus
`task/v44-mail-link-settings`.
