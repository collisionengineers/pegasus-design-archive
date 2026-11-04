# v48: the Send report dialog and the Original report card

**Stage 1, awaiting the operator's sign-off.** Nothing here is implemented.

- Created at the operator's request on 4 November 2026: "Send report moves to a dialogue box
  with a composer (files clickable to preview, files renameable)" and "an additional box on
  the right hand rail for Inspection + Audit cases (only for the audit case)" showing the
  original report's repair cost, salvage value on a total loss, and the Engineer's Value with
  the guide chosen for the original report in brackets.
- It is built over live captures of Pegasus `origin/dev` (`8da7957ce`, 4 November 2026), which
  includes PR 1883 (From is a default on every send, R655).
- It is not application code, not design authority and not implementation evidence. The
  self-check and screenshots test the mockup against itself, not the application.
- Behaviour is owned by the FRDs (FRD-11 reports and delivery, FRD-16 the Case record and its
  aside, FRD-21 outbound correspondence, FRD-24 valuation and settlement). Presentation is
  owned by the [design authority](https://github.com/collisionengineers/pegasus/blob/dev/docs/design/README.md).
- The sign-off list in [notes/v48-notes.md §6](notes/v48-notes.md#6-sign-off) decides what
  Stage 2 changes.

Open [pegasus_v48.html](pegasus_v48.html) in a browser. It is one self-contained file with 14
states of the Case record's Report section, its send, and the aside.

- **Today** is the page as captured from the running application. The delivery form sits
  inline in the Report section while editing (From, To, Cc, Attach ticks, a read-only File
  name, Message, Send report), reading shows the same cells greyed, and the Audit view of an
  Inspection + Audit Case shows nothing of the Inspection report's figures.
- **Proposal** is the same page with the changes applied:
  - **Send report** is the Report head's primary while editing with the report stored, and the
    aside's Next action step; both open the **Send report** dialog, a composer in the Triage
    composer's shape: From, To, Cc (each extra box removable), Subject, Message, then **Files**,
    one row per attachment with its include tick, its name (opens the Case viewer over the
    dialog), its kind and size, and Rename (the stem is edited, `.pdf` stays, Reset restores
    the policy name). The Principal's rule blocks (Already sent, Stop and Override reason,
    missing companion, Questions, Cc hint, After sending, Holds) keep their live words.
  - The Report section keeps its preview card; the inline form and the greyed read cells go.
  - **Original report**, a card after Figures on the Audit view of an Inspection + Audit Case:
    Repair cost inc VAT, Salvage value (on a Total loss) and Engineer's Value with the guide
    in brackets, read from the Inspection report as it was generated.

The floating strip at the bottom left (`Mockup controls`) is a demo control, not product UI. It
switches states, Today / Proposal and **Diff badges**, opens the dialog, the preview and the
rename, holds the four variables (dialog width, Files placement, card placement, money
format) and lists the changes on the current state. Hide it with `?strip=0`.

Query string: `?state=<key>&mode=today|proposal&diff=1&dialog=send-report&viewer=0&rename=1
&opt=width:1100,files:beside,card:before-figures,money:pounds&strip=0`. The state keys are
`plain-edit`, `plain-dialog`, `plain-viewer`, `plain-rename`, `plain-read`, `rules-dialog`,
`stop-dialog`, `missing-dialog`, `resend-dialog`, `audit-edit`, `audit-dialog`, `audit-read`,
`audit-repairable` and `audit-inspection`.

## Layout

| Path | What it is |
| --- | --- |
| `pegasus_v48.html` | The interactive mockup: 14 states, Today and Proposal. It is built, so do not edit it by hand |
| `notes/v48-notes.md` | Change table, live rules mirrored, frame numbers, coverage audit and departures, sign-off items A–O, self-check record, known limits |
| `notes/discussion-log.md` | The operator's brief, the three planning questions and answers, and the note on removable recipients, 4 November 2026 |
| `notes/stage-2-plan.md` | The Stage 2 implementation plan, written during Stage 1. Not started |
| `notes/capture-run-2026-11-04.log` | Result of the `ZzMockupCaptureCase.CaptureV48*` run against `8da7957ce` |
| `pages/` | The Case page folder: how it works today, how it should work, the dialog, the panel and the states |
| `captured-live/case/` | The server-rendered pages the mockup is built over, each with its `.facts.json` fixture facts |
| `captured-live/_source/` | The live `wwwroot` the captures reference, and `source.txt` naming the commit |
| `build/` | `build-v48.py` (assemble), `proposals_send.py` and `proposals_card.py` (the patches), `proposal-v48.js` (the in-page behaviour of the patches), `check-v48.py` (self-check and shots), `patch_capture_facts.py` (the scratch capture facts' changes), `preview_patch.py` |
| `shots/` | Screenshots at 1580×1000, 1440×900 and 760×1000, with dialog, panel and card crops and `verification.json` |

## Rebuild

```powershell
python -X utf8 build/build-v48.py
python -X utf8 build/check-v48.py            # add --no-shots to skip screenshots
```

To recapture, run the `ZzMockupCaptureCase.CaptureV48*` facts in a capture worktree with
`MOCKUP_CAPTURE=1` and `MOCKUP_CAPTURE_DIR` set to this folder's `captured-live`. The facts are
the excluded `ZzMockupCapture*.cs` files from the v46 round with `build/patch_capture_facts.py`
applied; they are never committed.

## Status

- The operator's three planning answers (4 November 2026) are built in: the card reads the
  Inspection report as generated; Subject is editable and prefilled; Send report opens only
  while editing.
- The operator's note during the build, "extra recipients/cc box isn't removable - adjust",
  is item O: each extra To or Cc box has its ×.
- Items A–O await sign-off.
