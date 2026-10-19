# Administration

Today is the page captured from the application; it is not redrawn. The Proposal is the same page with the changes below.

| State | Page | Changes |
| --- | --- | --- |
| `admin-hub` | Administration | A1, S1, S3, S4 |
| `accounts` | Staff accounts | A9, A20, S1, S3, S4 |
| `accounts-settings` | Staff accounts · settings | A2, A9, A10, A14, A20, S1, S3, S4 |
| `accounts-glass` | Staff accounts · Glass's login | A2, A9, A14, A20, S1, S3, S4 |
| `accounts-glass-empty` | Staff accounts · Glass's login, not set | A14, A20, S1, S3, S4 |
| `accounts-temp-password` | Staff accounts · temporary password | A2, A9, A20, S1, S3, S4 |
| `contacts` | Contacts | A9, A15, A30, S1, S3, S4 |
| `contacts-create` | Contacts · Add Repairer | A15, A30, S1, S3, S4 |
| `contacts-principal-contact` | Contacts · Principal | A3, A16, S1, S3, S4 |
| `contacts-principal-report-generation` | Contacts · Principal, Report generation | A3, A16, S1, S3, S4 |
| `contacts-principal-report-sending` | Contacts · Principal, Report sending | A3, A11, A16, S1, S3, S4 |
| `contacts-principal-salvage-matrix` | Contacts · Principal, Salvage matrix | A3, A9, A16, S1, S3, S4 |
| `contacts-principal-default-inspection-location` | Contacts · Principal, Inspection location | A3, A16, S1, S3, S4 |
| `contacts-principal-principal-api` | Contacts · Principal, Principal API | A3, A16, S1, S3, S4 |
| `contacts-other` | Contacts · Repairer | A16, S1, S3, S4 |
| `configuration` | Workflow configuration | A4, A17, S1, S3, S4 |
| `mailboxes` | Mail settings | A18, S1, S3, S4 |
| `mailboxes-settings` | Mail settings · mailbox | A18, S1, S3, S4 |
| `mailboxes-new` | Mail settings · Add mailbox | A18, S1, S3, S4 |
| `email-templates` | E-mail templates | A19, S1, S3, S4 |
| `valuation-presets` | Valuation presets | A21, S1, S3, S4 |
| `health` | Service health | A20, A22, S1, S3, S4 |
| `logs` | Logs | A6, A13, A24, S1, S3, S4 |
| `logs-intake` | Logs · intake | A20, A24, S1, S3, S4 |
| `logs-intake-drawer` | Logs · intake, drawer open | A20, A24, S1, S3, S4 |
| `reports` | Management reports · Engineers tab | A7, A20, A26, S1, S3, S4 |
| `reports-principals` | Management reports · Principals tab | A7, A20, A26, S1, S3, S4 |
| `reports-queues` | Management reports · Queues tab | A7, A20, A26, S1, S3, S4 |
| `reports-case-list` | Management reports · Case list tab | A7, A20, A26, S1, S3, S4 |
| `admin-release-notes` | Release notes (Administration) | A20, A27, S1, S3, S4 |
| `release-note-edit` | Release note · edit | A27, S1, S3, S4 |
| `release-note-new` | Release note · new | A27, S1, S3, S4 |
| `release-note-published` | Release note · published | A27, S1, S3, S4 |
| `problem-reports` | Problem reports | A12, A20, A25, S1, S3, S4 |
| `ai-jobs` | AI jobs | A20, A28, S1, S3, S4 |
| `automation` | Automation & AI | A8, A23, S1, S3, S4 |

## Changes

- **A1**: The hub's cards are its navigation: their descriptions go, the Automation icon matches, and the duplicate side nav leaves the hub page.
- **A2**: Staff accounts: the temporary password panel sits at the top of the right-hand column, "Manage this account's login." goes, and the Glass's login dialog no longer shows Generation and Version.
- **A3**: Contacts: the "(optional)" label suffixes and the Linked principals note go, Principal API state shows the status chip, Replace code moves from the foot of every tab to the head of the Contact tab, and hint lines take the field-hint style.
- **A4**: Workflow configuration: the Administration eyebrow is added, the labour-rate table is compact with right-aligned figures, the fieldset border is reset, and the range hint lines go (the minimum and maximum stay).
- **A6**: Logs: the AI actor chip is the shared status chip.
- **A7**: Management reports: the sentence above the Case list controls goes.
- **A8**: Automation: the checkbox uses the shared choice label.
- **A9**: Bare Administration tables take the compact table style used by the other Administration lists.
- **A10**: Account settings has one foot: Disable and Delete set apart on the left, Cancel and Save on the right; Force logout and Reset password sit in the body as small actions.
- **A11**: Report sending reads as a form, not nested boxes: fieldsets lose their browser borders and Add address / Add reminder are small buttons at their natural width.
- **A12**: Problem reports keeps the reconciliation form compact on one line, and the report ID shows only on the row that needs it.
- **A13**: Logs reads in words: action codes become plain wording and results share one spelling.
- **A14**: Staff accounts: the settings dialog's Username and State fact grid goes, the Delete confirmation takes the shared dialog classes, the Glass's login dialog keeps its one close (the x) and its legend-less fieldset is a plain stack, and the dialog's "Not configured" reads "Not set" like the list.
- **A15**: Contacts list: Add contact carries the plus icon, the panel's Contacts heading goes and the panel head keeps the filter toolbar, Default inspection reads Inspection mode with the full Image Based Assessment, and the Add dialog closes the way the Type dialog does (x and a Cancel button).
- **A16**: Contacts edit: the inactive-Principal panel goes, the browser fieldsets become plain stacks, the Replace dialog takes the shared dialog classes, each Rule legend is numbered, Add rule / Add band are small buttons, the API sentence goes, Report generation, Location and API are bounded like the Contact tab, the spacer field goes and every tab's foot is Cancel then Save.
- **A17**: Workflow configuration: the Reset buttons (form and each rate row) go; Save is the form's last control.
- **A18**: Mail settings: Last checked shows the time only (or Not polled / Not activated without full stops), the dialog keeps Last success / Freshness / Last error with Last error in words, Add mailbox is the primary button and the panel head gains the count meta as Staff accounts has, the Add and Settings dialogs share one width, Used for loses its fieldset border and uses the choice label, and the literal x is the sprite icon. QUESTION: the count meta's unit word is drawn as the plural of the label Mailbox; confirm it.
- **A19**: E-mail templates: built-in rows read Built-in wording, the panel heading goes, the action cell is right-aligned like Staff accounts, and the placeholder chip row is labelled with the existing label Placeholders.
- **A20**: Administration, across pages: notices share one success treatment (success tone and check-circle), the local Confirmation copy that repeats the layout's goes, a panel heading that repeats the page title goes, empty lists use the empty state, and Apply / Add buttons use the one primary class.
- **A21**: Valuation presets: the head reads Presets, the State column reads Enabled, the amount inputs sit inside the .input-money wrapper (the pound sign shows and figures right-align), and the count takes panel-title-meta.
- **A22**: Service health: Working chips take the green tone. A Needs attention row shows its mapped reason under the chip the way the Intake log does (small.admin-service-area, which Stage 2 treats as shared and moves to site.css); no captured row carries a failure code, so none is drawn here.
- **A23**: Automation and AI: the scope reads Received files, the checkbox reads Send to AI, the AI settings panel shows its state once (the chip goes, the checkbox states it) and Stop automation sits at the end of its panel on the right like Save AI settings. Registered clients and Client identifier collapse to one fact when they are equal (they differ on the capture, so nothing is drawn). QUESTION: the label of that one fact; the plan writes Client and no existing label is that word. Stage 2: the notice and the error summary sit inside the admin column (neither is on the capture), the dead Reason binding goes and FRD-17's optional-reason line is aligned, since no reason is captured.
- **A24**: Logs: the Recorded counts and processing times panel goes (Service health owns service facts). Action logs: the filter labels match their column headers (Keywords to Search, Activity to Action, Case/reference to Reference, Outcome to Result). Intake log: the tiles read Failed files and Oldest file waiting and take the shared metric strip, and the filter takes the Action logs structure with a primary Apply. The drawer takes the shared dialog frame with one close (the x) and drops the facts the row already shows (Received, Source, Outcome, Became), keeping Attempts and the evidence. Stage 2: the logs-tabs class and the logs.css colour fallbacks go.
- **A25**: Problem reports: the Unknown chip reads Delivery unknown, Page shows the page name instead of a route, and the table caption that repeats the page title goes (A20 takes the panel heading). Stage 2: a failed Retry gives no feedback.
- **A26**: Management reports: four tabs under the period bar, Engineers / Principals / Queues / Case list, as ?tab= links like Logs; Download workbook stays in the header; the six Case-list fieldsets lose their borders. Stage 2: LoadAsync scopes its reads by tab through the existing Reads flags; the header uses the shared page-header pattern (_PageHeader secondary action, eyebrow from the label).
- **A27**: Release notes: the list heading goes (A20), the edit page's eyebrow reads Administration like its siblings, a draft row's three Not recorded cells read an em dash, and the page for a new note does not repeat its title in the panel head.
- **A28**: AI jobs: Stop is one small danger button with no reason form, the kind reads AI Proposal (no captured job is an Estimate), the meta reads Send to AI on or off, a stopped job reads Cancelled (the state's own word, R160; no captured job is stopped) and the Action header aligns over its buttons. The status notice takes the shared tone (A20) and a Case subject links to the Case (A8). Stage 2: Stop posts no reason; the reason is optional (R160, FRD-27).
- **A30**: Contacts list: Apply renders only without script (noscript), as FRD-17 says, for no-script use; the Proposal hides it.
- **S1**: Release notes, Report a problem and Change password move into the Account dialog body; the foot keeps Close and Sign out.
- **S3**: The command palette's Cases icon matches the rail's Cases icon.
- **S4**: The utility bar's freshness line goes; the rail health line keeps the one clock.
