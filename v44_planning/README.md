# v44: Message settings, Case linking clean-up

**Temporary design review artifact**, created at the operator's request on 2 November 2026
from a screenshot of the Inbox message dialog's cog menu (`Message settings`) in the linked
state. It is not application code, not design authority and not implementation evidence.
Behaviour is owned by the FRDs, and presentation by the
[design authority](https://github.com/collisionengineers/pegasus/blob/dev/docs/design/README.md).
The sign-off list in [notes/v44-notes.md §5](notes/v44-notes.md#5-sign-off) decides what
Stage 2 changes.

Open [pegasus_v44.html](pegasus_v44.html) in a browser. It is one self-contained file with
the message dialog open and its cog menu dropped down, in four states: **unlinked**,
**linked** (the operator's screenshot), **query** (linked, open query) and **triage**
(linked to a Triage). **Today** is the live markup of `_MessageDecision.cshtml` drawn with the
live `site.css` and `inbox.css`. **Proposal** is the same dialog with the redesign applied.

The dark strip at the bottom left (`Mockup controls`) is a demo control, not product UI. It
switches Mode, State, the open Dialog, the menu, Diff badges and the three design variables.
It is hidden with `?strip=0`.

Query string:
`?mode=today|proposal&state=unlinked|linked|query|triage&dialog=linkCaseDialog|changeLinkedCaseDialog|unlinkCaseDialog&menu=0&diff=1&inline=1&opt=picker:dialog|inline,changelabel:Change linked Case|Change,caseactions:buttons|links&strip=0`

## Layout

| Path | What it is |
| --- | --- |
| `pegasus_v44.html` | The interactive mockup (built; do not edit by hand) |
| `build/template-v44.html` | Mockup source: the Today transcription, the Proposal, the proposal CSS and the strip |
| `build/build-v44.py` | Inlines the live CSS, Lucide sprite and Inter font into `pegasus_v44.html` |
| `build/check-v44.py` | Playwright self-check and screenshots into `shots/` |
| `build/live/` | The live sources read from Pegasus `origin/dev` (`source.txt` holds the SHA) |
| `notes/v44-notes.md` | Problem, proposal, frame numbers, departures, sign-off list, self-check record |
| `notes/discussion-log.md` | The operator's brief and the feedback rounds |
| `pages/inbox/` | `how-it-works.md` (live, dated), `how-it-should-work.md`, `dialogs/`, `states/`, `panels/` |
| `shots/` | 48 screenshots (16 presets × 1580×1000, 1440×900, 760×1000) and `verification.json` |

## Building

Run these from `v44_planning/`:

```powershell
python -X utf8 build/build-v44.py; python -X utf8 build/check-v44.py
```

`check-v44.py` launches the installed Playwright Chromium (`%LOCALAPPDATA%/ms-playwright/chromium-1223`).

## Status

**Signed off and implemented (2 November 2026).** Items A–F are settled (R607–R612), and
Stage 2 is on Pegasus `task/v44-mail-link-settings`, with routed-page conformance shots in
`shots/live/` ([notes §7](notes/v44-notes.md#7-stage-2-conformance-2-november-2026)). This
folder is now historical reference. Current behaviour is owned by
[FRD-20](https://github.com/collisionengineers/pegasus/blob/dev/docs/frd/frd-20-mailbox-workspace.md)
and rulings R607–R612 in the application repository.

The screenshots and self-check are mockup evidence only, not application evidence.
