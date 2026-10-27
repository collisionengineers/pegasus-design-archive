# v42: mail simplification (instructions, Case correspondence and assignable queries)

**Temporary design review artifact**, created at the operator's request on 26 October
2026 and built over live captures of `origin/dev` (`373dcc81a`, 26 October 2026). It is
not application code, not design authority and not implementation evidence. Behaviour is
owned by the FRDs, and presentation by the [design authority](../../pegasus/docs/design/README.md).
Once the Stage 2 implementation lands and the owning FRDs and ADRs carry the settled
behaviour, this folder is historical provenance only. The sign-off list in
[notes/v42-notes.md §6](notes/v42-notes.md#6-sign-off) decides what Stage 2 changes.

Open [pegasus_v42.html](pegasus_v42.html) in a browser. It is one self-contained file
with 20 states across the Inbox, the Case workspace and the Work Centre. **Today** is
each page captured from the running application, and **Proposal** is the same page with
the proposed changes applied. The floating strip at the bottom left (`Mockup controls`)
is a demo control for switching states, toggling Today / Proposal and **Diff badges**,
and reading the changes on the current state; it is not product UI and is hidden with
`?strip=0`. Query string: `?state=<key>&mode=today|proposal&diff=1&strip=0`.

## Layout

| Path | What it is |
| --- | --- |
| `pegasus_v42.html` | The interactive mockup (20 states, Today and Proposal) |
| `notes/v42-notes.md` | Change table, live rules mirrored, frame numbers, settled decisions A–F, departures, sign-off list G–AA, self-check record, known limits |
| `notes/discussion-log.md` | Chronological log of the operator's 26 October 2026 brief, the five rulings A–F and the blast-radius exploration |
| `notes/capture-run-2026-10-26.log` | Output of the three `ZzMockupCapture*` test lanes against `origin/dev` `373dcc81a` |
| `build/states_v42.py` | The 20 states and their captures |
| `build/proposals_v42.py`, `build/proposals_{inbox,case,work}.py` | The patch API, presets and one patch module per area |
| `build/build-v42.py` | Builds `pegasus_v42.html` and `build/v42-changes.json` from `captured-live/` |
| `build/pagedocs-v42.py` | Writes `pages/README.md` and `pages/<area>/states/README.md` from `v42-changes.json` |
| `build/check-v42.py` | Playwright self-check and screenshots into `shots/` |
| `build/preview_patch.py` | Inspects one state's changes and Today→Proposal diff without building |
| `build/runtime-v42.js`, `bridge-v42.js`, `strip-v42.html`, `shell-v42.css`, `frame-v42.css` | Mockup runtime: frame, request stubs, control strip |
| `captured-live/` | Captured pages, Case section fragments, message previews/contents and live assets (`_source/`, with `source.txt`) |
| `shots/` | 156 screenshots (`001`–`039` across 1580×1000, 1580 whole page, 1440×900 and 760×1000) and `verification.json` |
| `pages/` | Per-area documentation (`inbox/`, `case/`, `work-centre/`): `README.md`, `dialogs/`, `states/`, `panels/`, `how-it-works.md`, `how-it-should-work.md` |

## Building

Run from `v42_planning/`:

```powershell
python build/build-v42.py && python build/pagedocs-v42.py && python build/check-v42.py
```

## Status

**Signed off (27 October 2026).** Items **A** to **AA** are settled and signed off by the
operator ([notes/v42-notes.md §6](notes/v42-notes.md#6-sign-off)). Ready for Stage 2
implementation. Nothing under `src/` or `tests/` in the application repository has been
modified yet.
