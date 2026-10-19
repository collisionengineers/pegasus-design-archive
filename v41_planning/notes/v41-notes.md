# v41 notes: the Pegasus redesign

**Temporary design review artifact.** It is not application code, not design
authority and not implementation evidence. Behaviour is owned by the FRDs, and
presentation by the [design authority](../../../../docs/design/README.md). The
sign-off list in §5 decides what Stage 2 changes.

## 1. What this is

There is one mockup, [pegasus_v41.html](../pegasus_v41.html), covering 104 states across
six areas. Every state has two views:

- **Today** is the page captured from the running application. It is not redrawn. The
  source is `dev` `365d83064be7fa7a0144928f5953cb341e7d7dda` (waves 1 to 4 landed; PR 1331 is in `dev`), captured 2026-10-19 (`../captured-live/_source/source.txt`).
  The live stylesheets and `site.js` run inside it. Requests are stubbed, the captured
  message previews and contents answer the scripts, and links between captured pages
  switch state.
- **Proposal** is the same captured page with the proposed changes applied as patches:
  the open items of §5 and the items settled in §4. Each changed element carries its
  ID, and **Diff badges** outlines them. The strip lists the changes on the page you are
  looking at.

The Inbox Proposal is the one exception to patch-on-capture. The message becomes one
dialog, drawn by `inbox-designs-v41.js` inside the captured page's shell: the message on
the left, and Decision on the right with the eleven Classification chips and the Case
picker. Tags and the six designs were dropped on 15 October (§4). The list carries a
checkbox on each row and one bulk form (I18).

Open the file in a browser. The query string is
`?state=<key>&mode=today|proposal&diff=1&strip=0`. On Inbox states,
`selected=m1..m6`, `dialog=message|attachments|thread|compose|link|unlink|bulk-classify`,
`scope=incoming|nocase|sent|dismissed|deleted`, `ticked=m1,m5` and `dismissed=m2,m4`
open a sub-state.

## 2. How it is made

Paths are under `v41-redesign/`; the scripts live in `build/` and run from `v41-redesign/`.

| Piece | Role |
| --- | --- |
| `tests/Pegasus.IntegrationTests/ZzMockupCapture*.cs` | Excluded scratch tests, never committed. They seed realistic data and save each page, its lazy Case sections and its fragments into `captured-live/<area>/`. Run them from a worktree of the source above with `MOCKUP_CAPTURE_DIR` and `MOCKUP_REPO_ROOT` unset, then copy the lanes they wrote here: the Admin and Shell lanes read back from the worktree's own `artifacts/` path and ignore `MOCKUP_CAPTURE_DIR`. |
| `build/states_v41.py` | The 104 states: area, capture and label. |
| `build/proposals_v41.py` + `build/proposals_<area>.py` | The patch API and one module per area. A patch edits a copy of the capture and marks what it changed. |
| `build/inbox-designs-v41.js` / `.css` | The Inbox Proposal: list, row ticks and bulk form, the one message dialog, Classification chips and the Case picker. |
| `build/build-v41.py` | Writes `pegasus_v41.html` (live CSS, JS, sprite and images inlined once, page bodies gzip-packed) and `build/v41-changes.json`. |
| `build/pagedocs-v41.py` | Writes `pages/<area>/README.md` from `v41-changes.json`. |
| `build/check-v41.py` | The self-check and the screenshots (§6). |
| `build/preview_patch.py` | Shows one state's changes and its Today→Proposal diff without building. |

`MOCKUP_CAPTURE` (R96, 16 October 2026): every `ZzMockupCapture*` Fact returns at once unless it is non-empty, so a capture run sets `$env:MOCKUP_CAPTURE = '1'`.

## 3. What the 15 October review changed

The first v41 drawing (14 October) was hand-written HTML, and a review against
`dev` found that its Today views were not the live pages. Examples:

- The consent page, error pages, command palette, notifications and Work Centre rows did not match live.
- The Accounts, Configuration, Mailboxes and Automation pages were invented in places.
- The Cases queue showed filters that do not exist.
- The Case frames were about a week old: no Report sent, Tasks still a section, the old Next action.

About 30 of its "what happens today" findings were false or already fixed, and several
proposals added sentences nobody approved. This round replaces all of it. Today is now
captured, every finding was re-checked against the source, and the proposal list in §5
keeps only what held, with invented copy removed. Findings dropped:

| Earlier finding | Why it went |
| --- | --- |
| f10 Assign Engineer opens the wrong Case | The mechanism described is not the live one. The real narrower bug is in `work-centre.js` (no visual change); a Stage 2 note. |
| f12 Work Centre `since` and tab `selected` | Not how the live page works. |
| f20 Upload column swap | The proposed CSS reversed the FRD-18 layout. The DOM-order fix has no visual change; a Stage 2 note. |
| f22 `InstructionPdfParser` text, "Optional for Triage" | Not in the source. U4 keeps the real provenance clean-up. |
| f24 Pair dialog, Dismiss-reading dialog | They contradict FRD-19 or add little. |
| f26 damage Reset alignment, blank select options | Already fixed, or the blank option is how a field is cleared. |
| f29 Unassigned option, Reopen/Remove | Not live. Adding them would invent behaviour. |
| f30 double-click title, "Could not save this section" | Not in the source. |
| f31 nav missing AI jobs/Automation | Already handled by the nav's fallback. |
| f33 `.definition-list` missing | It exists. |
| f37 release notes not editable | Titles already link to Edit. |
| f38 problem-report dialog, Stop dialog | The existing inline forms work. A dialog would hide the report ID the Unknown row needs. |
| Item Q "Every delivery rule is met. Ready to send." | Invented copy. |
| W3's header Create Case on Search | The live Search header has none. |

### 16 October 2026 recapture

- **Source.** `dev` `b8124e3f0` with PR 1331 at `235567b0d51766cb9e04e9d7aa6f5dbd2c64bb20` merged locally as `be14764eb` (never pushed), captured 2026-10-16 15:11. The 15 October capture (PR 1331 `a65e89d6c`, merged as `fb6d446ff`) is kept beside it as `captured-live-2026-10-15/`.
- **Run.** One `dotnet test tests/Pegasus.IntegrationTests --filter "FullyQualifiedName~ZzMockupCapture"` with `MOCKUP_CAPTURE=1`: 16 of 16 passed, 1.8 minutes (`capture-run-2026-10-16.log`). The first run (`capture-run-2026-10-16-run1.log`) also passed 16 of 16, but the Admin lane saved HTTP 500 on every page: the scratch Fact's fixed clock (15 October 10:30) came before the start of the development OAuth certificates, which are valid from one day before the run. The scratch `Start` in `ZzMockupCaptureAdmin.cs` now reads today 10:30 UTC (worktree and main checkout copies), and the second run saved all 33 Admin pages as 200. The Admin and Shell read-back path equalled the write path in the worktree (`v41_planning/current/captured-live`), so no `OutputDirectory()` edit was needed.
- **Differences to `captured-live-2026-10-15/`.** The file list of every lane is identical (`_source` 32, `admin` 35, `case` 46, `inbox` 41, `intake` 26, `shell` 20), and `_source/wwwroot` and `_LucideSprite.cshtml` are byte-identical. Compared as text with GUIDs, 32-character hex keys, timestamps, anti-forgery and trace ids, attachment hashes, the temporary password and the PKCE challenge ignored, the only difference is `_source/source.txt`. Nothing differs that is not a generated id or time: dates and clock times read from the real clock (the Admin lane now reads 16 October, the Work Centre "Due" weekdays, "Taken until" times and the rail "Current" time) and row order where `admin/logs.html` and `intake/triage.html`, `triage-link.html`, `triage-finding.html` list the same lines in another order (log rows by sub-second time, attachments by generated id). PR 1331's changes after `a65e89d6c` alter no rendered output in these lanes. The Mail categories panel is still on `mailboxes.html`, so A5's patch still finds it.

### 2026-10-19 recapture

- **Source.** `origin/dev` `365d83064be7fa7a0144928f5953cb341e7d7dda` (waves 1 to 4 landed, nothing merged on top; PR 1331 landed earlier as PR 1337), captured 2026-10-19 09:48 from the detached `v41-capture` worktree. The 16 October set is kept beside the new one as `captured-live-2026-10-16/`. `captured-live/_source/wwwroot` is copied from the worktree's `src/Pegasus.Web/wwwroot` and holds `images/lucide-sprite.svg` (PR 1449 made the sprite a static fingerprinted file; there is no `_LucideSprite.cshtml` any more).
- **Runs.** Three runs on 19 October; only the third counts. Run 1 did not compile (CS1729: `CaseSearchItem` lost its circumstances argument; `ZzMockupCaptureShell.cs` now carries a `ShellCircumstances` stub). Run 2 passed 17 of 17 Facts but the Case lane saved no page, because `CaseWebTestSupport` now builds the database-less host and the Case page's one snapshot read (PR 1435) needs the database (`keepDatabase: true` at its eight `OpenEngineerWorkspaceAsync` / `EnterEngineerEditModeAsync` calls fixes it; the Shell lane now empties the host's `IMemoryCache` so the What's new dialog is captured; the `CaptureClosed` Fact adds `case-closed`). Run 3: `MOCKUP_CAPTURE=1`, 17 of 17 passed, 1 m 35 s of tests inside a 4 m 4 s command (`capture-run-2026-10-19-run3.log`; logs of runs 1 and 2 are `capture-run-2026-10-19.log` and `capture-run-2026-10-19-run2.log`).
- **Files per lane.** `_source` 32, `admin` 35, `case` 52, `inbox` 41, `intake` 26, `shell` 20. Every `index.tsv` row is HTTP 200 except `shell` `status-404`, `intake` `pre-case-images` (POST-only) and `case` `case-audit-inspection.section-report` (a 404 and a zero-byte file on 16 October as well).
- **Differences to `captured-live-2026-10-16/`**, compared as text with GUIDs, 32-character hex keys, timestamps and dates, weekday names, anti-forgery and trace ids, attachment hashes, the temporary password and the PKCE challenge ignored. Only `case` gains files: `case-closed.html` and its `section-files`, `section-notes`, `section-queries`, `section-valuation`, `section-vehicle` (46 to 52). Nothing is removed. On every page: the inline Lucide sprite is gone, each icon is `<use href="/images/lucide-sprite.<hash>.svg#icon-x">` and `<html>` carries `data-icon-sprite` (PR 1449, `build-v41.py` inlines the sprite once and rewrites the references); the stylesheet and script names carry new hashes; the rail counts (`nav-count`) are gone from all 93 pages that had them (sc-07). Pages whose markup changed beyond that:
  - `admin/admin-hub`: the card reads "Approve mailboxes." for "Approve mailboxes and mail categories." (PR 1332).
  - `admin/mailboxes`, `mailboxes-settings`, `mailboxes-new`: the Mail categories panel and the Add category dialog are gone (PR 1332).
  - `admin/contacts`, `contacts-create`: Principals are paged (a "Page 1" and Next bar under the table; the create links and form carry `pageNumber`); FRZ (Fraz, Disabled) is listed, PCH reads "PCH / Connexus" for "Performance Car Hire / Parkhouse", and WLS, YML and ZEN are no longer on the first page; the Repairers table gains iRevolution Repair Network.
  - `admin/contacts-other`: the Linked principals list reads "PCH / Connexus (PCH)".
  - `admin/contacts-principal-contact`: a hidden `PrincipalInspectionMode` input sits before the fieldset.
  - `admin/contacts-principal-report-sending`: each rule gains a Rate card checkbox and an Attach fieldset (Fee note is a separate PDF, Estimate, Audatex, Vehicle images document required, Figure breakdown required, each As the Principal / Attach / Do not attach); the condition kinds gain Reference prefix and Previous job, and the Repairer condition lists iRevolution Repair Network.
  - `admin/logs` (the same rows in another order) and `admin/accounts-temp-password` (the password) differ only in generated values.
  - `case/*` (every Case page with the Return to Review dialog): the hidden `instructionsComplete`, `imagesComplete` and `evidenceReference` inputs are gone from Return to Review; the Close case Outcome reads "Principal cancelled" for "Cancelled"; where the page has a repairer picker it lists iRevolution Repair Network.
  - `case/case-report-sent`, `case-tasks-open`, `inbox/case`, `inbox/case-ai-ready`: the Actions menu no longer has Place on Hold or Close case, and the Place on Hold and Close case dialogs are not on the page.
  - `shell/search`, `search-filters`: the Status filter has one option, Closed, for the four "Closed ·" options; each result's circumstances line is "Loading…" with a `data-circumstances-url` (loaded by a request the mockup does not answer) where it read the text.
  - `intake/create-manual`: the repairer select lists iRevolution Repair Network.
  - `intake/upload-review`, `upload-review-find`, `upload-review-new-case`: the review surface carries `data-status-url` (empty on new-case).
  - `intake/triage-finding` lists the same lines in another order.
  - Every other page (shell and Inbox lanes, the other Admin, Case and Intake pages) is unchanged beyond the sprite, the hashes and the rail counts.
- **Unpatched baseline.** `python build/build-v41.py && python build/pagedocs-v41.py && python build/check-v41.py` from `v41-redesign/` with the unedited `build-v41.py`: 92 states, 87 with proposals; `RESULT {"fail": [], "okCount": 1106}`, 736 screenshots, check 6 m 21 s. The built mockup inlines the sprite once (75 symbols), no `lucide-sprite` URL is left and the screenshots show the icons. The check passed because `Ctx.remove(None)` is a no-op, so a patch whose target is gone fails silently. Comparing each state's recorded change ids and marked-element counts on the 16 October and 19 October captures, the only drift is A5: on `mailboxes`, `mailboxes-settings` and `mailboxes-new` its panel and dialog lookups find nothing and A5 records no change.
- **Environment.** `chromium-1234` under `%LOCALAPPDATA%\ms-playwright` had been emptied at 09:28 (no `chrome.exe`; the installed Playwright expects 1223), so `check-v41.py` could not launch; `python -m playwright install chromium --no-shell` installed 1223 and the check ran.

### 2026-10-19 Stage 2 step 1: the 15 October plan applied

[plan-2026-10-15.md](plan-2026-10-15.md) §2 is applied inside this folder, with the corrections of [v41-stage-2.md](../../plans/v41-stage-2.md): W7 and W3's "Create Case leaves the header" clause are dropped (#1216 delivered them), A5's patch is dropped (PR 1332 delivered it and the captures post-date it), the PERF-WEB-09 row reads R42, and the state count is 104. Nothing under `src/` or `tests/` changed and no tracked file was touched.

- **States.** 92 before the round. The two `case-query-view-*` states went (K6 to K8) and `case-with-engineer-unassigned` (K9) and `case-closed` (K10, from the 19 October capture) came in, which is 92 again. Twelve more are registered because a capture or a change needs them: `inbox-rows-ticked`, `inbox-rows-ticked-classify`, `inbox-rows-ticked-busy` and `inbox-dismissed-rows-ticked` (I18), `contacts-create` (A15), `accounts-glass-empty` (A14), `logs-intake-drawer` (A24), `release-note-new` and `release-note-published` (A27), and `reports-principals`, `reports-queues` and `reports-case-list` (A26, three tab states over the one `reports` capture, which is now the Engineers tab). 99 of the 104 states have a Proposal.
- **Inbox.** Tags and the six designs are gone: I3, I7, I8 and I14 are dropped, I1, I2, I4 and I6 to I17 are redrawn without them and I18 is new.
- **Case, Work Centre, Shell, Upload.** K5, K9 and K10 and W8 are new; K6 to K8 are gone; S5's consent summary marks the intake sentence and leaves its wording to Stage 2 PR 1; U2's pattern also matches "Image Intake" (R158).
- **Administration.** A14 to A28 and A30 are drawn; A29 is Stage 2 only. A6 keeps only the AI actor chip, because A24 removes the whole diagnostics panel.
- **Routes.** `?tab=` links reach their own state: the route list is first-match and the build strips queries from the captured routes, so the Logs and Reports tab links are listed with their queries in `states_v41.py`.

## 4. Already settled

Nothing in this section is a sign-off item.

### The brief, 13 October 2026

The operator wrote: *"We do not need a full page to view an email. This should be a dialogue box. We need a system to tag/alter emails in the same way as images at present."*

- **I2** is settled: the opened message is a dialog over the Inbox. `/Inbox/{id}` stays for a new tab and for no script (R159 c).
- The tagging half of the brief (I3) was dropped on 15 October (below). The dialog edits the two properties that exist, Classification and Case. Classification is drawn as chips applied at once, the way an image tag is.

### Decided 15 October 2026 (interview and rulings; full table in [plan-2026-10-15.md](plan-2026-10-15.md) §1)

| Item | Decision |
| --- | --- |
| Inbox tags (I3, I7, I8, I14 design 5, the six designs) | Tags are dropped. One dialog on design 3's layout: the Classification chips and the Case picker in the right column. I2 stands. |
| Session started | The mandate is dropped (`docs/design/README.md:107`, FRD-12:97). A Stage 2 documentation change; no patch. |
| W4, W7 | `/Cases/Create` everywhere. #1216 delivered it (the Search header Create Case is gone), so W7 has no patch and W3's "Create Case leaves the header" clause is removed. |
| S5 and Unidentified "intake" | The Unidentified history line reads "Unrecognised Principal". The consent scope line loses the word; its exact words are put to the operator when Stage 2 PR 1 is drafted (R159 b). |
| U1 | The Attached, Discarded and Pending sentences stay. |
| K6, K7, K8 | The Queries section stays as live. The `case-query-view-*` states and their patches are gone. |
| K5 | Read mode shows the last recipients the sent report used. |
| A8 | The AI jobs Case subject links to the Case. |
| #1213 | In as W8 and K9. No reason for Take or Assign Engineer. Assigned With Engineer Cases appear in Mine only. |
| PERF-WEB-08 | In as part of A26 (four `?tab=` tabs). PERF-WEB-09 is not withdrawn: R42 builds it, in its own PR (`finding-work-centre-focus-refresh`, wave 4). |
| Administration | The twelve rulings of [plan-2026-10-15.md](plan-2026-10-15.md) §1 (tile words, "Received files", "Send to AI", "AI Proposal", the Mail settings time and Last error, valuation presets "Presets" and "Enabled", problem reports, "Built-in wording", one-click Stop, the Delete confirmation, the Logs diagnostics panel, the Reports tabs). |
| Everything else drawn | Accepted as drawn: S1 to S7, W1 to W6, I1, I2, I4, I6, I9 to I17 (redrawn without tags; I9 returns in §5 with the one question that redraw raised), U2 to U12, K1 to K4, A1 to A13. |

Button placement and page layout were reviewed screen by screen on 15 October at the operator's instruction ("a lot of the button placements, or general look, are terrible"). W5, W6, U7 to U12, A10 to A13 and the dialog's I17 come from that pass.

### Rulings of 15 and 16 October 2026 that settled a question ([rulings-2026-10-15.md](../../audits/rulings-2026-10-15.md))

| Ruling | What it settled | Where it shows in v41 |
| --- | --- | --- |
| R41 | #1213: Core composes the history reason; rows keep today's chip. | W8: the Review row keeps its chip, and the Mine With Engineer row's kind chip reads With Engineer (`issue-1213-with-engineer-handoff`). The history reason is Core's; nothing to draw. |
| R42 | Build the Work Centre focus-refresh gap, the Cases quick-detail lighter read, upload group status polling and Search circumstances on selection. | U8 stays as drawn; the other three change no page. |
| R105 | The mileage discrepancy and range lines are held for Stage 2 PR 4. | None is drawn. |
| R140 | Inbox bulk actions: (a) a row-selection and bulk-bar item is drawn and signed off before any Razor; (b) the bulk-control words are asked once the item exists; (c) one shared reason for bulk classify; (d) ADR-0069 untouched; (e) bulk Restore in Dismissed. | I18 (§5). |
| R155 | The Cases quick detail also reads the document facts for an Audit Case, so Current work matches the aside. | No page change. |
| R156 | The Engineers tab keeps its previous-period figures; only tabs that draw none skip those reads. | A26's Engineers tab. |
| R157 | The Web offers Return to work: a dialog on a closed Case, built in Stage 2 PR 4. | K10 (§5). |
| R158 | "Image Intake" reads "Vehicle images" in all eleven places. | U2's pattern also matches "Image Intake"; no capture shows either. |
| R159 | (a) No Service health truncation notice; (b) the consent scope line is put to the operator when PR 1 is drafted; (c) `/Inbox/{id}` stays; (f) `f10` and `f20` are built; (g) the Logs Area binding stays. | A22 draws no notice; S5 and I2 text; `f10` and `f20` below; A24. |
| R160 | A stopped AI job reads "Cancelled" everywhere; the Stop reason is optional. | A28. |
| R161 | (a) History lines have no full stops; (b) the Review and Not ready ribbons read Unassigned in place of Not recorded, and the Cases quick detail keeps "Not assigned"; (c) the new blocker's words are confirmed at the PR. | (b) is K9's ribbon. No captured Review or Not ready ribbon reads Not recorded, so nothing else is drawn for it; no history line is drawn, so (a) and (c) show nowhere. |

### Stage 2 items with no visual change (no patch)

- **`f10`**: Assign Engineer in `work-centre.js` (v41 §3 "f10 Assign Engineer opens the wrong Case"). Built in Stage 2 PR 1 (R159 f).
- **`f20`**: the Upload DOM order (§3, "f20 Upload column swap"). Built in Stage 2 PR 3 (R159 f).

## 5. Sign-off

**19 October 2026.** The 15 October plan is applied to the mockup (§3). This list is what is still open. Confirm each item, or say otherwise. IDs match the strip and the Diff badges; `../pages/` lists which states show each one. Each item names only what no ruling has settled; the clauses a ruling settled are in §4. A **question** has no patch: a word or a choice that no ruling and no existing label gives, left visible in the item and never filled in.

Everything else in the round was accepted as drawn on 15 October (§4). Delivered earlier: W4 and W7 (#1216), A5 (PR 1332). Dropped by ruling: I3, I7, I8, I14, K6, K7, K8.

The operator's answers are logged under a dated **Decided** heading at the end of this section once the list has been read out. Logged 19 October 2026 (see **Decided** below).

### I: Inbox

- **I9** Decision, redrawn without tags. The right column holds the eleven Classification chips (one pressed; pressing another applies at once), the Case, the Case / PO picker, then Change linked Case and Unlink (or Link to Case) as one row of small buttons, then Decided. The Correct classification button is gone from the row because the chips replace it. **Question:** a chip applies at once, but Correct classification needs a Reason for correction (1 to 500 characters) and, for New instruction, a Case type, and the dialog draws no field for either. Where are they entered? Tag as query is the one existing one-click correction, and it records the fixed reason "Tagged as query". Unclassified is a Correct classification option but not one of the eleven chips, so the chips cannot reach it.
- **I18** Row selection and the bulk bar (R36, R140 a). In All incoming, No Case Found and Dismissed each row has a checkbox in a left gutter; ticking it neither opens nor pins the row. One bulk form sits above the list, outside the rows: the count of ticked rows and, in the incoming scopes, Dismiss and Correct classification, or, in Dismissed, Restore (R140 e). Sent Items and Deleted Items have none. Correct classification opens the existing dialog once, so Classification, Case type and Reason for correction are entered once for every ticked row (R140 c). Each row keeps its own Reply, Dismiss and Restore. The bulk buttons are always enabled: a post with nothing ticked writes nothing (`finding-mail-bulk-actions` criterion 5), and a button drawn disabled could not be enabled without script (criterion 11). The pressed bulk control shows its existing busy word and the loader glyph, as the live row Dismiss does (criteria 12 and 13): Dismissing… on Dismiss, Restoring… on Restore, and Saving… on the dialog's Save correction. States: `inbox-rows-ticked`, `inbox-rows-ticked-classify`, `inbox-rows-ticked-busy` (bulk Dismiss pressed), `inbox-dismissed-rows-ticked` (two dismissed messages are seeded, because the live Dismissed capture is empty). **Questions (R140 b):**
  1. The words for the bulk controls. Drawn with the single-message labels Dismiss, Restore and Correct classification; confirm them or give others.
  2. The count of ticked rows. Drawn as a bare number with no noun; the ticked set is not called "selected".
  3. The failure line for a message a bulk post could not change. Not drawn; no partial-failure state exists until the words are given.
  4. The checkbox's accessible name. Drawn as the message's subject alone, a stand-in for the operator's word.
  5. `finding-mail-bulk-actions` criterion 11 (the bulk bar works without script) against the classify inputs living in a dialog, which needs script. Keep the dialog (drawn), or put the inputs inline in the bar behind a disclosure?
  6. No select-all checkbox is drawn, because neither R36 nor R140 asks for one. Add one, or leave it out?

### W: Work Centre

- **W8** (#1213) as drawn. The Assign Engineer list shows the signed-in person first as "Name (you)" and gains an Unassigned option; the dialog has no Reason box (the live dialog has none). An Unassigned row carries Take, a small primary button, beside Assign Engineer (`work-centre`, `work-centre-assign`, `work-centre-mine`). Mine gains a With Engineer row whose kind chip reads With Engineer, whose action is Open Case and whose Due reads No due date, last in Later. Cases · With Engineer's Engineer cell reads Unassigned where the Case has none. **Questions:** (1) the title word of the Mine With Engineer row is drawn as "With Engineer" (the same as its kind chip, `issue-1213-with-engineer-handoff` criterion 12), and a "With Engineer" kind-filter chip is drawn beside Unassigned as a copy of the Review chip; the plan names neither. Confirm or give the words. (2) A With Engineer row's Due is the Case's one due instant (its next chase time, else the end of its Due by date; criterion 8), so a Case with neither has none. The capture holds no due instant for the Case drawn, so the row is undated and reads No due date, the label an Open tasks row already uses, last in Later. FRD-15:90-91 says every kind but Open tasks has a due instant. Confirm that a With Engineer row may be undated (the FRD line then changes, as the plan's Notes say it settles with this sign-off), or say what a With Engineer Case with no chase or Due by shows. The other Work Centre states that carry an Unassigned row (`work-centre-selected`, `work-centre-new-cases`, `work-centre-ai-jobs`) are not redrawn.

### K: Case

- **K9** (#1213) as drawn, on `case-with-engineer-unassigned`. The ribbon and the Overview read Unassigned (R161 b); Next action opens with Assign Engineer and Take beside it; the Actions menu lists Assign Engineer; the Assign Engineer dialog lists the signed-in person first as "Name (you)", then the other Engineer, then Unassigned, with no Reason box. The dialog is drawn from the live Razor markup, because no With Engineer capture holds it. **Question:** the live Overview has no assigned-Engineer fact, only Sign-off Engineer, which is decided apart from the assigned Engineer. It is drawn reading Unassigned, as the plan says; confirm it or drop it.
- **K10** (R157) Return to work on a closed Case, on `case-closed`. The Actions menu lists Return to work before Archive case. The dialog uses the Archive dialog's frame (title, a stage select, Reason for action, Cancel, Confirm Action) and posts the Closure page's Reopen handler with the destination and the reason. The stage options read the existing stage names: Not ready, Review, With Engineer, Report sent (the four `CaseReopenDestination` values). FRD-13:442 offers it for every closed disposition except Created in error; the capture does not show the disposition, so that gate is not drawn. **Question:** the label of the stage field. No ruling gives it and no live label names it, so it reads "Case stage", the word W2 gives the Search filter that reads State today. Confirm it or give another.

### A: Administration

- **A14** Staff accounts. The settings dialog's Username and State fact grid goes (the title is the username; Disable and Enable state the state). Glass's login dialog keeps one close (the ×) and its legend-less fieldset is a plain stack; its "Not configured" reads "Not set" like the list.
- **A15** Contacts list. Add contact carries the plus icon. The panel's Contacts heading goes and the panel head keeps the filter toolbar. "Default inspection" reads "Inspection mode" with the full "Image Based Assessment". The Add dialog closes the way the Type dialog does (× and a Cancel button). **Question:** the toolbar is drawn as the Name or contact and Type filters moved into the panel head beside Add contact once the heading goes; confirm that reading. (The Inspection mode label is not drawn: only a Repairer Add dialog is captured.)
- **A16** Contacts edit. The inactive-Principal explanation goes (the chip and the Active tick say it; every captured Principal is Active, so it is not drawn). The browser fieldsets on Report generation, Salvage matrix, Location, Principal API and the Replace dialog become plain stacks. The Replace dialog takes the shared dialog classes. Each Rule legend reads "Rule 1", "Rule 2" and so on. Add rule and Add band are small buttons. The API sentence goes. Report generation, Location and API are bounded at 720px like the Contact tab. The spacer field goes. Every tab's foot is Cancel then Save; the Principal API tab has only Reset API key, Pause and Revoke, so it gets no Cancel. Readings to check: Cancel links to the Contacts list as the Contact tab's does; the Remove buttons are already small.
- **A17** Workflow configuration. The Reset buttons (form and each rate row) go; Save is the form's last control.
- **A18** Mail settings. Add mailbox is the primary button and the panel head gains the count meta as Staff accounts has. The Add and Settings dialogs share one width. "Used for" loses its fieldset border and uses the choice label. The literal × is the sprite icon. One error summary per page (no capture shows a summary, so none is drawn). **Questions:** (1) the count meta's unit word is drawn as "4 mailboxes", the plural of the existing label Mailbox; confirm it or give the word. (2) "Last checked shows the time only" is drawn as the last completed poll's date and time ("19 Oct 2026 11:28") with Next due dropped; confirm that, or say clock time only. (3) The shared dialog width is drawn at the Settings dialog's width (720px); confirm it or name the other. (The Settings dialog keeps its detail, Activation and Subscription included: that is the 15 October ruling, in §4, not a question.)
- **A19** E-mail templates. The panel heading goes. The action cell is right-aligned like Staff accounts. The placeholder chip row is labelled with the existing label "Placeholders" (today only the group's aria-label). **Question:** confirm that label or drop the hint.
- **A20** Administration, across pages. Notices share one success treatment (success tone and check-circle) on Mail settings, E-mail templates, Valuation presets, Automation and AI jobs. The local Confirmation copy that repeats the layout's goes (Configuration, E-mail templates, Valuation presets, Release notes list and edit). A panel heading that repeats the page title goes (Service health, E-mail templates, Problem reports, AI jobs, Release notes, Contacts, Staff accounts). Empty lists use the empty state. Apply and Add use the one primary class, not the dark one (Download CSV and Download workbook stay dark). Drawn only where a capture holds the element: the first-load captures hold no notice, Confirmation copy or empty list. Where a panel heading goes, the section keeps its `aria-labelledby`; Stage 2 names the section.
- **A21** Valuation presets. The amount inputs sit inside the `.input-money` wrapper, so the £ shows and figures right-align. The count takes `panel-title-meta`. The checkbox uses the choice label (the capture already prints it, so nothing changes on the page).
- **A22** Service health. Working chips take the green tone. A Needs attention row shows its mapped reason under the chip, the way the Intake log does (`small.admin-service-area`, moved to `site.css` in Stage 2). The mapped-reason line is not drawn: no 19 October capture holds a Service health row with a failure code, and a sentence drawn there would be invented data.
- **A23** Automation and AI. The AI settings panel shows its state once (the chip goes; the checkbox states it). Registered clients and Client identifier collapse to one fact when they are equal (they differ on the capture, so nothing is drawn). The notice and the error summary sit inside the admin column (neither is on the capture). Stop automation sits at the end of its panel on the right, like Save AI settings. **Question:** the label of the one collapsed fact. The plan writes "Client"; no existing label is that word. Stage 2: the dead `Reason` binding goes and FRD-17's optional-reason line is aligned, since no reason is captured.
- **A24** Logs. The Action logs filter labels match their column headers (Keywords to Search, Activity to Action, Case/reference to Reference, Outcome to Result). The Intake log tiles take the shared `.metric-strip` and `.metric`, and its filter takes the Action logs structure with a primary Apply. The drawer takes the shared dialog frame with one close (the ×) and drops the facts the row already shows (Received, Source, Outcome, Became), keeping Attempts and the evidence. Stage 2: the dead `logs-tabs` class and the `logs.css` colour fallbacks go.
- **A25** Problem reports. The panel heading and the table caption that repeat the page title go. **Question:** the ruled "Page shows the page name" (§4) is drawn as the route's first segment (`/Cases` reads Cases), because no ruling or existing label names the other routes; confirm that reading or give the words. Stage 2: a failed Retry gives no feedback.
- **A26** Management reports. The six Case-list fieldsets lose their borders. The header uses the shared page-header pattern (Stage 2: the `_PageHeader` secondary action, the eyebrow from the label). Stage 2: `LoadAsync` scopes its reads by tab through the existing `Reads` flags, and `PageOnly` is split.
- **A27** Release notes. The list heading goes (A20). The edit page's eyebrow reads Administration like its siblings. A draft row's three "Not recorded" cells read "—". The page for a new note does not repeat its title in the panel head.
- **A28** AI jobs. The Action header aligns over its buttons. The status notice takes the shared tone (A20).
- **A29** Administration literals, Stage 2 only (no patch). The hard-coded "Administration" eyebrows and titles (Reports, AiJobs, ProblemReports, ReleaseNotes, Health) use `OperatorLabels`; the dead data hooks in `Accounts/Index.cshtml` and the `accounts.js` comment, the dead CSS (`site.css`, `preset-row--add`, `dialog--mailbox`), and the `Reason` fields that are never posted go; `_AdminNav` stops reading `AdminAutomationComposed`; the `ActionLogs` shim stays.
- **A30** Contacts list. Apply renders only without script (`<noscript>`), as FRD-17 says. The Proposal hides it.

### Carried to the Stage 2 draft (not lettered items)

- **K5** To and Cc in read mode are the ruled change (15 October, §4); nothing is left to confirm. The capture already seeds a send history: `ZzMockupCaptureCase.cs` gives the Sent report the last recipient `claims@northline.example`, the sender of the instruction e-mail that the Sent item "Re: New instruction" replies to. Read mode prints no recipient today (only the edit-mode already-sent line does), so the captured page cannot show it and a recapture would change nothing; the patch draws To as that address, read from the Case's own correspondence. Cc stays "Not recorded", because the send history is one joined list (`v41-stage-2.md`) and names no Cc.
- **S5** The consent line for the intake scope is put to the operator when Stage 2 PR 1 is drafted (R159 b). The capture requests only `automation.cases` and `automation.documents`, so no such sentence is on the page and none is drawn.
- **Mileage lines** The mileage discrepancy and range lines are held for Stage 2 PR 4 (R105). None is drawn.

### Decided (19 October 2026)

The operator's words, 19 October 2026, 11:41Z, in the session chat after the list above was reported with its eight open questions: **"v41 approved"**.

The lead's reading of that approval, recorded so the Stage 2 PRs can cite it:

- Every lettered item (I9, I18, W8, K9, K10, A14 to A28, A30) is confirmed as drawn.
- Where an item asked "confirm, or give another", the drawn stand-in stands: I18's bulk controls read Dismiss, Restore and Correct classification, the ticked count is the bare number, the checkbox's accessible name is the message subject, the classify inputs stay in the dialog, and no select-all is added; W8's Mine row title and kind-filter chip read "With Engineer", and a With Engineer row may be undated (the FRD-15:90-91 line changes at the PR); K9's Overview reads Unassigned; K10's field label reads "Case stage"; A15's toolbar reading; A18's "4 mailboxes", the last poll's date and time, and the 720px shared width; A19's "Placeholders" label; A25's first-segment reading of the Page cell.
- Not answered by the approval, because nothing was drawn to approve: I9's entry point for Reason for correction, Case type and Unclassified when a chip applies at once; I18's failure line for a message a bulk post could not change; A23's label for the collapsed Client fact. These stay open as PR-time copy (Stage 2 PRs 2 and 6) and are held, not invented, until the operator gives the words.
- Held for PR time by ruling, unchanged: the consent scope line (PR 1, R159 b), the mileage discrepancy and range lines (PR 4, R105), the #1213 blocker words (PR 1 review, R161 c).

## 6. Self-check and screenshots

`python build/check-v41.py` loads every state in Today and Proposal and fails on any page error. It checks that each Proposal marks its changes, then runs:
- the Inbox assertions: no tag model, no design choice and no preview; the eleven Classification chips with one pressed and a press applying at once; the Case picker beside them and I9's buttons beneath; Previous/Next, Dismiss moving on and the composer; one-step Unlink and the five scopes, with no email called Unidentified; and I18's ticks, the one bulk form, bulk Dismiss, Correct classification and Restore, and its three states;
- W8 (you first, the Unassigned option, no Reason box, Take on an Unassigned row posting the signed-in person's staff id as `engineerId`, the Mine With Engineer row, Unassigned in Cases · With Engineer), K5, K9 (Take posting the `engineerId` that the dialog's Name (you) option posts), K10 and the Administration hooks A21 (`.input-money > input`), A22, A23, A24 (no `<details>` on Logs, the tiles use `.metric`, the drawer's one close), A26 (four tabs on every Reports state, and tab links that land on their state), A28 (no `.row-confirm`) and A30.

It then takes 1580×1000, 1440×900 and 760×1000 captures plus a 1580 whole-page capture of every state, writing them to `shots/` with `verification.json`.

15 October 2026 run: `RESULT {"fail":[],"okCount":1106}`, 736 screenshots, with no page or console error.

16 October 2026 run (after the recapture in §3, build, page docs and check in 5.6 minutes): `RESULT {"fail": [], "okCount": 1106}`, 736 screenshots. Both figures equal the 15 October run, as the lanes differ only in generated ids and times.

19 October 2026 baseline (unpatched `build-v41.py` over the 19 October capture, §3): `RESULT {"fail": [], "okCount": 1106}`, 736 screenshots.

19 October 2026, Stage 2 step 1 (the 15 October plan applied; `python build/build-v41.py && python build/pagedocs-v41.py && python build/check-v41.py` from `v41-redesign/`, run last, 5 m 58 s end to end after the second review pass): `RESULT {"fail": [], "okCount": 1208}`, 812 screenshots (813 files with `verification.json`), 104 states, 99 with a Proposal, no page or console error (1190 before the second review pass below, 1185 before the first). `python build/preview_patch.py --all` ran for all 104 states with no exception. Each figure moved from the 1106 / 736 baseline for one reason:

| Figure | Baseline | Now | Why |
| --- | --- | --- | --- |
| States | 92 | 104 | Two `case-query-view-*` states out (K6 to K8), `case-with-engineer-unassigned` (K9) and `case-closed` (K10) in, and twelve registered: `inbox-rows-ticked`, `inbox-rows-ticked-classify`, `inbox-rows-ticked-busy`, `inbox-dismissed-rows-ticked`, `contacts-create`, `accounts-glass-empty`, `logs-intake-drawer`, `release-note-new`, `release-note-published`, `reports-principals`, `reports-queues`, `reports-case-list`. |
| States with a Proposal | 87 | 99 | The same twelve states each have one. |
| okCount | 1106 | 1208 (+102) | Four checks per state (each of Today and Proposal loads with no page error and renders the page) 368 to 416 (+48); "proposal marks its changes" 73 to 82 (+9: eight new Administration states, K9 and K10 in, the two query views out, and `case-correspondence` no longer an Inbox state, so it is checked like any other); the per-screenshot "no console error" checks 552 to 609 (+57: 203 state and mode pages against 179, less the five `mail-message` design shots); the named assertions 113 to 101 (-12: the six-design Inbox loop, 17 assertions a design, and its tag assertions give way to one dialog's assertions, the chip, picker and I18 assertions, and the W8, K5, K9, K10, A21 to A24, A26, A28 and A30 assertions, five of them the staff-id checks the first review pass added: the (you) option's id, Take's `engineerId` on the three Work Centre states, and K9's Take against its dialog, and eight the second review pass added, listed below). |
| Screenshots | 736 | 812 (+76) | 24 more state and mode pages at four files each (96), less the 20 design shots (designs 1, 2, 4, 5 and 6 of `mail-message`, four files each). |

An earlier run of the same command, before the Inbox presets lost their unused `entry` key and the page docs intro was reworded, gave the same result: `RESULT {"fail": [], "okCount": 1185}`, 804 screenshots. The review pass (Take posting the viewer's staff id, K10's label source, the patches split to one per change, the ruling clauses out of A22, A24 and A26) changed no state count or screenshot: only those five checks were added.

The second review pass (19 October 2026, after the run that gave 1190) fixed six defects, registered one state and added eight named assertions, four checks per state for the new state and its six console checks (1190 to 1208, 804 to 812 screenshots, 103 to 104 states):
- **K5** (`proposals_case.py`, §5): the confirm request is gone. The capture rig already seeds a send history (`claims@northline.example`), which read mode never prints, so a recapture changes nothing; K5's description says so and Cc stays Not recorded because the history is one joined list.
- **W8** (`proposals_work.py`, §5): the Mine With Engineer row is undated (No due date, last in Later) instead of keeping the Review row's Due today, and W8 raises the FRD-15:90-91 question the plan said the sign-off settles. One assertion.
- **I18** (`inbox-designs-v41.js`, §5): the bulk buttons are always enabled (both enabled with nothing ticked, and a bare Dismiss or Correct classification writes and opens nothing; these two assertions replace the one that asserted disabled), carry the existing busy words (Dismissing…, Restoring…, Saving… on the dialog's Save correction; three assertions), and the new state `inbox-rows-ticked-busy` draws the pressed Dismiss through `pegasusBusy` (one assertion).
- **No Case Found** (`inbox-designs-v41.js`): m1, m3 and m5 are the scope's messages, as the capture lists them, so it shows 3 messages and the rail counts 3 (one assertion). Nothing to record: this restores Today.
- **Received sort toggle** (`inbox-designs-v41.js`): the live link with its `Received ↓` text and aria-label in place of an `#icon-arrow-up-down` the sprite does not have (one assertion). Nothing to record: this restores Today.

## 7. Known limits

- Fixture data comes from each area's capture test. Some Case fixtures carry the test store's 2031 dates and the reference `QDOS3100042`. The rail user is the test sign-in on some pages, and `alex`/`e.mawdsley` on others.
- Nothing is saved or sent. Forms show a toast. Links to pages that were not captured say so.
- Photographs served by handlers are drawn as a grey placeholder.
- `/PreCaseImages` is POST-only, so it is not a state; its tools render inside Unidentified.
- PR 1331 landed as PR 1337 and is in the 19 October capture.
- The #1213 states (W8, K9) are drawn on captures that hold no Unassigned With Engineer Case:
  - **K9** reuses the `case-read` capture as `case-with-engineer-unassigned` and rewrites its Engineer facts. The Assign Engineer dialog is drawn from the live `_CaseDialogs.cshtml` markup, because no With Engineer capture holds it. Link clicks on that state resolve to `case-read`, the first route for the capture. Its Take posts `engineerId`; the viewer there is `integration-user` and no Case capture holds a staff id, so the viewer's name stands in for it, as it does for the dialog's Name (you) option.
  - **W8** draws Take on the Unassigned rows of `work-centre`, `work-centre-assign` and `work-centre-mine` only; the other states that carry such a row stay as Today. Take is a form that posts `?handler=AssignEngineer` with the Case id and the viewer's staff id as `engineerId` (an omitted Engineer is Unassigned). Only `work-centre-assign` holds that id (its Assign Engineer list gives e.mawdsley `00000000-0000-4000-8000-0000000000e1`), so the other two states read it from that capture, the same shell-lane store. The Mine With Engineer row clones the Review row and takes its Case from the oldest New cases row that has no row on that page, so no Case is repeated or invented. Its Due is not the Review row's, which belongs to another Case: the capture holds no due instant for the Case drawn, so it reads No due date, last in Later (W8 question 2). In Cases · With Engineer all three captured Cases have an Engineer, so the last is drawn as a Case with none.
- Some Administration items change an element no capture holds, so the patch is written and tested on synthetic markup only and records no change on the page: the A8 Case-subject link (no captured job has a Case subject), the A15 Inspection mode label, the A16 inactive-Principal panel (every captured Principal is Active), the A18 Last error in words and the one error summary, the A20 notice tone, local Confirmation copy and empty states, and the A21 choice label.
- The route list is first-match, and a captured route keeps its query only where `states_v41.py` lists it: the Logs and Reports tab links are listed, so `?tab=` reaches its own state.
- Five states have no Proposal because nothing changes there: `auth-signin`, `auth-signin-failed`, `auth-signed-out`, `auth-access-denied` and `error`.
