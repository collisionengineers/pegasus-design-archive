# v45 discussion log

This log records how the round came to be. It is not design authority.

## 2 November 2026: brief

The operator's words:

> We have a "Report Wording" section that I'd like to improve a bit.
>
> The "Vehicle" section currently has a "On the report" section that Id like to examine. This
> should be taken in both functionality and concept and merged into the lower Report Wording
> section.
>
> I envisage a top setting with the current inclusions as a default.
>
> The statement of truth should also be a field but it's not editable (it is shown on there).
>
> The top settings would allow enable/disable for the various fields as well as the user to write
> in there as needed.
>
> Each of the boxes that are getting integrated from vehicle tab should have their own
> section/wording appear when chosen

### What was explored

The live page was read from Pegasus `origin/dev` `f6de68d1a`.

**The On the report row.** The only "On the report" on the Case page is the Valuation section's
row (`_CaseValuation.cshtml`, v28 P38). Valuation sits directly under Vehicle in the section row.

- The row holds five switches:
  - Disclose guide source;
  - Valuation commentary;
  - Include unrelated damage;
  - FAO The Court;
  - Include statement of truth.
- In read mode it shows one summary line instead (R616).

**The Report wording panel.** This panel is on the Report section (v28 P30).

- It lists nine standard blocks in print order. Each block has a heading, its wording, a chip,
  Recompose, Move up and down, and its own `On report` tick.
- Manual paragraphs can be added.
- The Statement of truth is a separate folded, read-only sub-panel above it.
- The Valuation commentary text is a separate field on the same pane.

**What each switch does to the report.** This was traced from Core.

- **Disclose guide source** adds the Glass's Evaluator sentence. It prints only when the guide is
  Glass's.
- **Valuation commentary** and **Include unrelated damage** gate the `commentary` and `unrelated`
  wording blocks.
- **FAO The Court** prints the line above the addressee, on the assessment report only (R610).
- **Include statement of truth** removes the heading and paragraphs 1–2 when off. Paragraphs 3–4
  and the sign-off still print (R609).

### Questions asked and the operator's answers

1. **Which items should the new top settings list?**
   - Answer: **"Every block"**. One checklist covers the nine blocks, the five moved switches and
     manual paragraphs, and the per-block tick goes.
2. **Where does the writing go?**
   - Answer: **"In each item's block"**. The settings are ticks only. Ticking an item makes its
     block appear, and the writing happens there. Valuation commentary's text box moves into its
     block.
3. **Should the guide-source sentence and the FAO line also appear as read-only blocks?**
   - Answer, in the operator's words: **"Dont include FAO the court as a box but read only for the
     rest"**.
   - FAO The Court is a tick with no block. The guide-source sentence and the Statement of truth
     are read-only blocks.

### What was raised

These are sign-off items A–I in [v45-notes.md §6](v45-notes.md#6-sign-off).

## 2 November 2026: approval and sign-off

The operator's words: "approved for /razor-html-mockup-conversion. convert, integrate and submit a PR
when done". A–E, G and I were taken as proposed.

For **F**, the agent offered replacement words that used "PAV commentary". The operator asked: "It
should not say PAV commentary unless you got that from me, did you make it up?". The agent answered
that "PAV commentary" is the live title of the commentary wording block. It came into the report
work of 28 September 2026 (`2af629ff8`) from the operator's reference file
`pegasus_case_dashboard_2026-09-15.html`, line 1724, and FRD-11 lists it. The operator did not give
it in this round, so item H was reopened. The operator asked "what was that report work" and was
shown the commit. They then answered:

- **H, the tick label:** **"Valuation commentary"**.
- **The commentary block's printed heading:** **"Leave it as PAV commentary"**.
- **F:** **"Swap the place only"**. Both messages now say "… under Report wording on the Report
  section."

These answers are recorded as rulings R624 (the brief) and R625 (the sign-off) in the application
repository.
