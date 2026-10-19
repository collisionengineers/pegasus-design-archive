"""A: Administration.

Patches over the captured Administration pages (lane "admin"). Each is one ID from
proposals-brief.md. Only labels, values and existing classes are used; a patch whose
element is not in the capture does nothing.
"""
from __future__ import annotations

import re

from bs4 import NavigableString, Tag

from proposals_v41 import Ctx, patch

# Same tone table the live status chip uses (OperatorLabels.StatusTone): Active is navy,
# a word the table does not list reads neutral.
_CHIP_TONE = {"active": "navy", "enabled": "navy"}

A1 = ("The hub's cards are its navigation: their descriptions go, the Automation icon matches, "
      "and the duplicate side nav leaves the hub page.")
A2 = ("Staff accounts: the temporary password panel sits at the top of the right-hand column, \"Manage this account's login.\" "
      "goes, and the Glass's login dialog no longer shows Generation and Version.")
A3 = ("Contacts: the \"(optional)\" label suffixes and the Linked principals note go, Principal API state shows the status chip, "
      "Replace code moves from the foot of every tab to the head of the Contact tab, and hint lines take the field-hint style.")
A4 = ("Workflow configuration: the Administration eyebrow is added, the labour-rate table is compact with right-aligned figures, "
      "the fieldset border is reset, and the range hint lines go (the minimum and maximum stay).")
A6 = "Logs: the AI actor chip is the shared status chip."
A7 = "Management reports: the sentence above the Case list controls goes."
A8 = "Automation: the checkbox uses the shared choice label."
A8_LINK = "AI jobs: a Case subject links to its Case."
A9 = "Bare Administration tables take the compact table style used by the other Administration lists."
A10 = ("Account settings has one foot: Disable and Delete set apart on the left, Cancel and Save on the right; "
       "Force logout and Reset password sit in the body as small actions.")
A11 = ("Report sending reads as a form, not nested boxes: fieldsets lose their browser borders and "
       "Add address / Add reminder are small buttons at their natural width.")
A12 = "Problem reports keeps the reconciliation form compact on one line, and the report ID shows only on the row that needs it."
A13 = "Logs reads in words: action codes become plain wording and results share one spelling."

ACCOUNT_STATES = ("accounts", "accounts-settings", "accounts-glass", "accounts-temp-password")
CONTACT_STATES = (
    "contacts", "contacts-principal-contact", "contacts-principal-report-generation",
    "contacts-principal-report-sending", "contacts-principal-salvage-matrix",
    "contacts-principal-default-inspection-location", "contacts-principal-principal-api", "contacts-other",
)
PRINCIPAL_TABS = tuple(key for key in CONTACT_STATES if key.startswith("contacts-principal-"))
MAILBOX_STATES = ("mailboxes", "mailboxes-settings", "mailboxes-new")
# Management reports: the Engineers tab is the captured page's own state; the other three tabs are
# the same capture (admin/reports) read with their own panels (A26).
REPORTS_STATES = ("reports", "reports-principals", "reports-queues", "reports-case-list")


# -- A1 ---------------------------------------------------------------------
@patch("admin-hub")
def hub_cards(ctx: Ctx) -> None:
    for description in ctx.all(".admin-content .admin-card > p"):
        ctx.remove(description, "A1", A1)
    card = ctx.one('.admin-content .admin-card[href="/Administration/Automation"]')
    use = card.select_one("svg use") if card else None
    if use is not None:
        use["href"] = "#icon-bot"
        ctx.mark(card, "A1", A1)
    # The cards repeat the side nav entry for entry, so on the hub the cards are the navigation.
    if ctx.remove(ctx.one(".admin-layout > nav.admin-nav"), "A1", A1):
        ctx.style(".admin-layout:has(> .admin-content){grid-template-columns:minmax(0,1fr)}", "A1", A1)


# -- A2 ---------------------------------------------------------------------
@patch("accounts-temp-password")
def accounts_temp_password_panel(ctx: Ctx) -> None:
    panel = ctx.one('section[aria-labelledby="temporary-password-title"]')
    stack = ctx.one(".admin-layout > .stack")
    if panel is None or stack is None:
        return
    stack.insert(0, panel.extract())
    ctx.mark(panel, "A2", A2)


@patch(*ACCOUNT_STATES)
def accounts_login_line(ctx: Ctx) -> None:
    for line in ctx.all(".account-settings-section .settings-line .meta"):
        if line.get_text(" ", strip=True) == "Manage this account's login.":
            ctx.remove(line, "A2", A2)


@patch(*ACCOUNT_STATES)
def accounts_glass_generation_version(ctx: Ctx) -> None:
    for row in ctx.all(".credentials-summary > div"):
        label = row.find("dt")
        if label is not None and label.get_text(" ", strip=True) in ("Generation", "Version"):
            ctx.remove(row, "A2", A2)


# -- A3 ---------------------------------------------------------------------
@patch(*CONTACT_STATES)
def contacts_optional_wording(ctx: Ctx) -> None:
    for note in ctx.all("small"):
        if note.get_text(" ", strip=True).startswith("Optional. Select every"):
            ctx.remove(note, "A3", A3)
    for label in ctx.all("label"):
        for text in list(label.find_all(string=re.compile(r"\s*\(optional\)\s*$"))):
            text.replace_with(re.sub(r"\s*\(optional\)\s*$", "", str(text)))
            ctx.mark(label, "A3", A3)


@patch(*CONTACT_STATES)
def contacts_hint_class(ctx: Ctx) -> None:
    for hint in ctx.all("p.hint"):
        hint["class"] = ["field-hint"]
        ctx.mark(hint, "A3", A3)


@patch("contacts-principal-principal-api")
def contacts_principal_api_state_chip(ctx: Ctx) -> None:
    for term in ctx.all("main .definition-list .definition dt"):
        if term.get_text(" ", strip=True) != "State":
            continue
        value = term.find_next_sibling("dd")
        text = value.get_text(" ", strip=True) if value is not None else ""
        if value is None or not text:
            continue
        tone = _CHIP_TONE.get(text.lower(), "neutral")
        value.clear()
        value.append(ctx.html(f'<span class="status status--{tone}">{text}</span>'))
        ctx.mark(value, "A3", A3)


@patch(*PRINCIPAL_TABS)
def contacts_replace_code(ctx: Ctx) -> None:
    opener = ctx.one('button[data-dialog-open="replace-principal"]')
    if opener is None:
        return
    row = opener.find_parent("div", class_="button-row")
    head = ctx.one('section[aria-labelledby="contact-title"] > .panel-head')
    if head is not None:
        opener.extract()
        opener["class"] = ["btn", "btn--small", "btn--danger"]
        status = head.find("span", class_="status", recursive=False)
        cluster = ctx.html('<span class="cluster"></span>')
        if status is not None:
            cluster.append(status.extract())
        cluster.append(opener)
        head.append(cluster)
        ctx.mark(opener, "A3", A3)
        if row is not None and not row.get_text(strip=True):
            row.decompose()
    else:
        ctx.remove(row if row is not None else opener, "A3", A3)
        dialog = ctx.one("dialog#replace-principal")
        if dialog is not None:
            dialog.decompose()


# -- A4 ---------------------------------------------------------------------
@patch("configuration")
def configuration_polish(ctx: Ctx) -> None:
    title = ctx.one(".page-header .page-title")
    heading = title.find("h1") if title is not None else None
    if title is not None and heading is not None and title.select_one(".eyebrow") is None:
        eyebrow = ctx.html('<p class="eyebrow">Administration</p>')
        heading.insert_before(eyebrow)
        ctx.mark(eyebrow, "A4", A4)

    table = ctx.one('section[aria-labelledby="rates-title"] table')
    if table is not None:
        table["class"] = ["table", "table--compact"]
        ctx.mark(table, "A4", A4)
        for row in table.select("tr"):
            cells = row.find_all(["th", "td"], recursive=False)
            if len(cells) > 1:
                cells[1]["class"] = cells[1].get("class", []) + ["num"]
                for field in cells[1].select("input"):
                    field["class"] = field.get("class", []) + ["num"]

    form = ctx.one('form[action$="handler=SaveWorkflow"]')
    if form is not None and form.select_one(":scope > fieldset") is not None:
        ctx.style('form[action$="handler=SaveWorkflow"] > fieldset{min-width:0;margin:0;padding:0;border:0}',
                  "A4", A4)

    for hint in ctx.all("[data-workflow-settings-edit] .field-hint"):
        if re.fullmatch(r"\d+ to \d+", hint.get_text(" ", strip=True)):
            ctx.remove(hint, "A4", A4)


# -- A5 ---------------------------------------------------------------------
# No patch: PR 1332 delivered A5. The Mail categories panel and the Add category dialog are
# gone from the mailboxes captures (dev 365d83064), and the dialog close buttons are already
# the shared dialog-close style. The only literal x left is A18's.


# -- A6 ---------------------------------------------------------------------
# The seven cache rows left Recorded counts and processing times under A6; the 15 October ruling
# (plan-2026-10-15.md section 1) takes the whole panel away, so A24 removes it and A6 keeps the chip.
@patch("logs")
def logs_actor_chip_shared(ctx: Ctx) -> None:
    for chip in ctx.all("td .status-chip"):
        chip["class"] = ["status", "status--neutral"]
        ctx.mark(chip, "A6", A6)


# -- A7 ---------------------------------------------------------------------
@patch(*REPORTS_STATES)
def reports_case_list_note(ctx: Ctx) -> None:
    ctx.remove(ctx.one("section[data-case-list] p.admin-report-note"), "A7", A7)


# -- A8 ---------------------------------------------------------------------
@patch("automation")
def automation_checkbox_label(ctx: Ctx) -> None:
    for label in ctx.all("label.cluster"):
        if label.select_one('input[type="checkbox"]') is not None:
            label["class"] = ["choice"]
            ctx.mark(label, "A8", A8)


# The AI jobs Case subject links to the Case (15 October ruling). No captured job has a
# Case subject (the subjects are U779 ... and "Unidentified queue"), so this patch records
# no change here, as U2 does. The live link carries the job's SubjectId; the mockup routes
# any /Cases/ path to the Case page, as its other Case references do.
_CASE_REFERENCE = re.compile(r"(?:[a-z]\.)?[A-Z][A-Z0-9]*\d{5,}")


@patch("ai-jobs")
def ai_jobs_case_subject_link(ctx: Ctx) -> None:
    for cell in ctx.all("table[data-admin-ai-jobs] tbody td.mono"):
        reference = cell.get_text(strip=True)
        if cell.find("a") is not None or not _CASE_REFERENCE.fullmatch(reference):
            continue
        link = ctx.html(f'<a href="/Cases/{reference}">{reference}</a>')
        cell.clear()
        cell.append(link)
        ctx.mark(link, "A8", A8_LINK)


# -- A9 ---------------------------------------------------------------------
@patch(*ACCOUNT_STATES, *CONTACT_STATES, "configuration")
def bare_tables_compact(ctx: Ctx) -> None:
    for table in ctx.all("table"):
        if not table.get("class"):
            table["class"] = ["table", "table--compact"]
            ctx.mark(table, "A9", A9)


# -- A10 --------------------------------------------------------------------
# The Save form wraps only the fields, and Disable, Force logout, Reset password and Delete
# are forms of their own, so neither the one foot nor the body actions can sit inside the Save
# form (a form inside a form is not valid). The one foot follows the Save form and Save keeps
# its submit through the form attribute; the actions row is a second body block above the foot.
@patch("accounts-settings")
def accounts_settings_one_foot(ctx: Ctx) -> None:
    for dialog in ctx.all(".account-settings-dialog"):
        save_form = dialog.select_one("form[data-account-settings]")
        save_foot = save_form.select_one(":scope > .dialog-foot") if save_form is not None else None
        action_foot = next((foot for foot in dialog.select(":scope > .dialog-foot") if foot.select_one(".left")), None)
        if save_foot is None or action_foot is None:
            continue
        quiet = [form for form in action_foot.find_all("form", recursive=False)
                 if form.select_one("button.btn:not(.btn--danger)") is not None]
        if not quiet:
            continue
        form_id = f"{dialog.get('aria-labelledby', 'settings').removesuffix('-title')}-form"
        save_form["id"] = form_id

        row = ctx.html('<div class="cluster"></div>')
        for form in quiet:
            form.select_one("button.btn")["class"] = ["btn", "btn--small"]
            row.append(form.extract())
        actions = ctx.html('<div class="dialog-body stack"><p class="eyebrow">Account</p></div>')
        actions.append(row)
        save_form.insert_after(actions)
        ctx.mark(actions, "A10", A10)

        for button in list(save_foot.find_all("button", recursive=False)):
            if button.get("type") == "submit":
                button["form"] = form_id
            action_foot.append(button.extract())
        save_foot.decompose()
        ctx.mark(action_foot, "A10", A10)
        ctx.style('.account-settings-dialog .dialog-body[data-v41-change~="A10"]{padding-top:0}', "A10", A10)


# -- A11 --------------------------------------------------------------------
@patch(*PRINCIPAL_TABS)
def report_sending_form(ctx: Ctx) -> None:
    scope = "form[data-report-sending-editor]"
    if ctx.one(scope) is None:
        return
    for button in ctx.all(f"{scope} button[data-rs-add]"):
        button["class"] = ["btn", "btn--small"]
        ctx.mark(button, "A11", A11)
    ctx.style(
        f"{scope} fieldset{{min-width:0;margin:0;padding:0;border:0}}"
        f"{scope} fieldset.contact-section{{margin-top:18px;padding-top:16px;border-top:1px solid var(--line)}}"
        f"{scope} legend{{padding:0;margin-bottom:6px;font-size:11px;font-weight:780;color:#45433f}}"
        f"{scope} fieldset.contact-section>legend{{float:left;width:100%}}"
        f"{scope} button[data-rs-add]{{width:auto;align-self:flex-start;justify-self:start}}",
        "A11", A11)


# -- A12 --------------------------------------------------------------------
@patch("problem-reports")
def problem_reports_compact(ctx: Ctx) -> None:
    reconcile = False
    for row in ctx.all("tr[data-problem-report]"):
        issue_form = row.select_one('form[action*="handler=ConfirmIssue"]')
        if issue_form is None:
            ctx.remove(row.select_one("td:first-child > small.mono"), "A12", A12)
            continue
        group = issue_form.find_parent("div", class_="stack")
        if group is None:
            continue
        group["class"] = ["cluster"]
        sentence = group.find("p", class_="muted", recursive=False)
        if sentence is not None:
            group.append(sentence.extract())
        ctx.mark(group, "A12", A12)
        reconcile = True
    if reconcile:
        scope = "[data-problem-reports] td > .cluster"
        ctx.style(
            f"{scope}{{gap:6px 8px}}"
            f"{scope} form{{display:contents}}"
            f"{scope} label{{font-size:11px;font-weight:600;color:var(--muted)}}"
            f"{scope} input[type=number]{{width:140px;max-width:140px;min-height:32px;padding:5px 8px}}"
            f"{scope}>p{{flex:1 1 100%;margin:0}}",
            "A12", A12)


# -- A13 --------------------------------------------------------------------
def _action_words(code: str) -> str:
    if "_" not in code:
        code = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", code)
    words = [{"ai": "AI", "api": "API"}.get(word.lower(), word.lower()) for word in code.split("_") if word]
    if words and words[0] not in ("AI", "API"):
        words[0] = words[0].capitalize()
    return " ".join(words)


def _capitalised(value: str) -> str:
    return value[:1].upper() + value[1:]


@patch("logs")
def logs_in_words(ctx: Ctx) -> None:
    for table in ctx.all("table"):
        headings = [th.get_text(" ", strip=True) for th in table.select("thead th")]
        if "Action" not in headings or "Result" not in headings:
            continue
        columns = ((headings.index("Action"), _action_words), (headings.index("Result"), _capitalised))
        for row in table.select("tbody tr"):
            cells = row.find_all("td", recursive=False)
            for index, convert in columns:
                if index >= len(cells) or cells[index].find(True) is not None:
                    continue
                text = cells[index].get_text(" ", strip=True)
                words = convert(text)
                if text and words != text:
                    cells[index].string = words
                    ctx.mark(cells[index], "A13", A13)


@patch(*REPORTS_STATES)
def reports_apply_natural_width(ctx: Ctx) -> None:
    apply = ctx.by_text(".admin-report-period button", "Apply")
    if apply is None:
        return
    ctx.mark(apply, "A7", "Reports: the Case list's explanatory note goes, and the period form's Apply keeps its natural width.")
    ctx.style(".admin-report-period .cluster{justify-content:flex-start}.admin-report-period .cluster .btn{width:auto;flex:0 0 auto}",
              "A7", "Reports: the Case list's explanatory note goes, and the period form's Apply keeps its natural width.")


# ===========================================================================
# Stage 2 step 1 (v41-stage-2.md): A14-A21, plan-2026-10-15.md section 2.3.
# One @patch per change. Words come from the 15 October rulings or from labels the
# live pages already print; where a capture does not hold the element, the patch records
# no change (noted per item in the lane return).
# ===========================================================================
A14 = ("Staff accounts: the settings dialog's Username and State fact grid goes, the Delete confirmation takes the "
       "shared dialog classes, the Glass's login dialog keeps its one close (the x) and its legend-less fieldset is a plain "
       "stack, and the dialog's \"Not configured\" reads \"Not set\" like the list.")
A15 = ("Contacts list: Add contact carries the plus icon, the panel's Contacts heading goes and the panel head keeps the "
       "filter toolbar, Default inspection reads Inspection mode with the full Image Based Assessment, and the Add "
       "dialog closes the way the Type dialog does (x and a Cancel button).")
A16 = ("Contacts edit: the inactive-Principal panel goes, the browser fieldsets become plain stacks, the Replace dialog "
       "takes the shared dialog classes, each Rule legend is numbered, Add rule / Add band are small buttons, the API "
       "sentence goes, Report generation, Location and API are bounded like the Contact tab, the spacer field goes and "
       "every tab's foot is Cancel then Save.")
A17 = "Workflow configuration: the Reset buttons (form and each rate row) go; Save is the form's last control."
A18 = ("Mail settings: Last checked shows the time only (or Not polled / Not activated without full stops), the dialog keeps "
       "Last success / Freshness / Last error with Last error in words, Add mailbox is the primary button and the panel "
       "head gains the count meta as Staff accounts has, the Add and Settings dialogs share one width, Used for loses its "
       "fieldset border and uses the choice label, and the literal x is the sprite icon. QUESTION: the count meta's unit "
       "word is drawn as the plural of the label Mailbox; confirm it.")
A19 = ("E-mail templates: built-in rows read Built-in wording, the panel heading goes, the action cell is right-aligned "
       "like Staff accounts, and the placeholder chip row is labelled with the existing label Placeholders.")
A20 = ("Administration, across pages: notices share one success treatment (success tone and check-circle), the local "
       "Confirmation copy that repeats the layout's goes, a panel heading that repeats the page title goes, empty lists "
       "use the empty state, and Apply / Add buttons use the one primary class.")
A21 = ("Valuation presets: the head reads Presets, the State column reads Enabled, the amount inputs sit inside the "
       ".input-money wrapper (the pound sign shows and figures right-align), and the count takes panel-title-meta.")

GLASS_STATES = ("accounts-glass", "accounts-glass-empty")
CONTACT_EDIT_STATES = tuple(key for key in CONTACT_STATES if key != "contacts")
NOTICE_STATES = (*MAILBOX_STATES, "email-templates", "valuation-presets", "automation", "ai-jobs")
CONFIRMATION_STATES = ("configuration", "email-templates", "valuation-presets", "admin-release-notes",
                       "release-note-edit", "release-note-new", "release-note-published")
REPEATED_HEADING_STATES = (*ACCOUNT_STATES, "accounts-glass-empty", "health", "problem-reports", "ai-jobs",
                           "admin-release-notes")
# Every Administration state, including the captures the integrator may register.
ADMIN_STATES = (
    "admin-hub", *ACCOUNT_STATES, "accounts-glass-empty", *CONTACT_STATES, "contacts-create", "configuration",
    *MAILBOX_STATES, "email-templates", "valuation-presets", "health", "logs", "logs-intake", "logs-intake-drawer",
    *REPORTS_STATES, "admin-release-notes", "release-note-edit", "release-note-new", "release-note-published",
    "problem-reports", "ai-jobs", "automation",
)


# -- helpers ----------------------------------------------------------------
def _icon(ctx: Ctx, name: str) -> Tag:
    return ctx.html(f'<svg class="icon" aria-hidden="true"><use href="#icon-{name}" /></svg>')


def _close_button(ctx: Ctx) -> Tag:
    button = ctx.html('<button type="button" class="dialog-close" data-dialog-close aria-label="Close"></button>')
    button.append(_icon(ctx, "x"))
    return button


def _shared_dialog(ctx: Ctx, native: Tag | None, change_id: str, summary: str) -> Tag | None:
    """A native <dialog> confirmation redrawn on .dialog-backdrop/.dialog/.dialog-head/.dialog-foot."""
    form = native.find("form", recursive=False) if native is not None else None
    heading = form.find("h2") if form is not None else None
    if native is None or form is None or heading is None:
        return None
    heading.extract()
    heading["tabindex"] = "-1"
    heading["data-dialog-initial-focus"] = ""
    fieldset = form.find("fieldset", recursive=False)
    if fieldset is not None and fieldset.find("legend") is None:
        fieldset.unwrap()
    foot = form.find("div", class_="button-row", recursive=False)
    if foot is not None:
        foot.extract()
        foot["class"] = ["dialog-foot"]
    body = ctx.html('<div class="dialog-body stack"></div>')
    for child in list(form.children):
        if isinstance(child, Tag) and not (child.name == "input" and child.get("type") == "hidden"):
            body.append(child.extract())
    form.attrs.pop("class", None)
    if body.find(True) is not None:
        form.append(body)
    if foot is not None:
        form.append(foot)
    backdrop = ctx.html('<div class="dialog-backdrop" hidden><section class="dialog dialog--compact" role="dialog" '
                        'aria-modal="true"></section></div>')
    backdrop["data-dialog"] = native["id"]
    section = backdrop.find("section")
    section["aria-labelledby"] = native.get("aria-labelledby") or heading.get("id", "")
    head = ctx.html('<div class="dialog-head"></div>')
    head.append(heading)
    head.append(_close_button(ctx))
    section.append(head)
    section.append(form.extract())
    native.replace_with(backdrop)
    ctx.mark(backdrop, change_id, summary)
    return backdrop


def _plain_stack(ctx: Ctx, fieldset: Tag | None, change_id: str, summary: str) -> bool:
    """A legend-less browser fieldset becomes a plain stack."""
    if fieldset is None or fieldset.find("legend") is not None:
        return False
    fieldset.name = "div"
    ctx.mark(fieldset, change_id, summary)
    return True


def _link_to_button(ctx: Ctx, link: Tag | None, change_id: str, summary: str) -> None:
    if link is None:
        return
    button = ctx.html('<button type="button" data-dialog-close></button>')
    button["class"] = link.get("class", [])
    if link.get("aria-label"):
        button["aria-label"] = link["aria-label"]
    for child in list(link.contents):
        button.append(child.extract())
    link.replace_with(button)
    ctx.mark(button, change_id, summary)


def _count_meta(ctx: Ctx, head: Tag | None, text: str, change_id: str, summary: str) -> None:
    """The panel head's count line under the heading, as Staff accounts has it."""
    heading = head.find("h2", recursive=False) if head is not None else None
    if heading is None:
        return
    wrapper = ctx.html("<div></div>")
    heading.insert_before(wrapper)
    wrapper.append(heading.extract())
    meta = ctx.html('<p class="panel-title-meta"></p>')
    meta.string = text
    wrapper.append(meta)
    ctx.mark(meta, change_id, summary)


def _plural(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular}" if count == 1 else f"{count} {plural}"


def _drop_empty_head(head: Tag | None) -> None:
    if head is not None and not head.get_text(strip=True) and head.find(["button", "a", "form", "input"]) is None:
        head.decompose()


# -- A14 --------------------------------------------------------------------
@patch("accounts-settings")
def accounts_settings_fact_grid_goes(ctx: Ctx) -> None:
    ctx.remove(ctx.one("dl.account-settings-facts"), "A14", A14)


@patch("accounts-settings")
def accounts_delete_shared_dialog(ctx: Ctx) -> None:
    for native in ctx.all("dialog[id$='-delete']"):
        _shared_dialog(ctx, native, "A14", A14)


@patch(*GLASS_STATES)
def accounts_glass_one_close(ctx: Ctx) -> None:
    ctx.remove(ctx.one('.glass-credential-dialog .dialog-foot > button.btn[form="glass-close-form"]'), "A14", A14)


@patch(*GLASS_STATES)
def accounts_glass_plain_stack(ctx: Ctx) -> None:
    _plain_stack(ctx, ctx.one("form#glass-save-form > fieldset"), "A14", A14)


@patch(*GLASS_STATES)
def accounts_glass_not_set(ctx: Ctx) -> None:
    for chip in ctx.all(".glass-credential-dialog .dialog-head .status"):
        if chip.get_text(" ", strip=True) == "Not configured":
            chip.string = "Not set"
            ctx.mark(chip, "A14", A14)


# -- A15 --------------------------------------------------------------------
@patch("contacts", "contacts-create")
def contacts_add_contact_plus_icon(ctx: Ctx) -> None:
    add = ctx.one('button[data-dialog-open="contact-type-dialog"]')
    if add is None or add.find("svg") is not None:
        return
    label = ctx.html("<span></span>")
    label.string = add.get_text(" ", strip=True)
    add.clear()
    add.append(_icon(ctx, "plus"))
    add.append(label)
    ctx.mark(add, "A15", A15)


@patch("contacts", "contacts-create")
def contacts_panel_heading_goes(ctx: Ctx) -> None:
    panel = ctx.one('section[aria-labelledby="contacts-title"]')
    head = panel.select_one(":scope > .panel-head") if panel is not None else None
    heading = head.find("h2", recursive=False) if head is not None else None
    if heading is None:
        return
    toolbar = panel.select_one(":scope > form.contact-toolbar")
    ctx.remove(heading, "A15", A15)
    if toolbar is not None:
        head.insert(0, toolbar.extract())
        ctx.mark(toolbar, "A15", A15)
    ctx.style('.panel-head>.contact-toolbar{flex:1 1 auto;padding:0;border-bottom:0}'
              '.panel-head>button[data-dialog-open="contact-type-dialog"]{margin-left:auto}', "A15", A15)


@patch("contacts", "contacts-create")
def contacts_inspection_mode_label(ctx: Ctx) -> None:
    for label in ctx.all('.dialog-backdrop[data-dialog="contact-create-dialog"] label'):
        if label.get_text(" ", strip=True) != "Default inspection":
            continue
        label.string = "Inspection mode"
        ctx.mark(label, "A15", A15)
        field = label.find_parent(class_="field")
        for option in (field.select("option") if field is not None else []):
            if option.get_text(strip=True) == "Image based assessment":
                option.string = "Image Based Assessment"


@patch("contacts-create")
def contacts_add_dialog_close_pattern(ctx: Ctx) -> None:
    dialog = ctx.one('.dialog-backdrop[data-dialog="contact-create-dialog"]')
    if dialog is None:
        return
    _link_to_button(ctx, dialog.select_one(".dialog-head > a.dialog-close"), "A15", A15)
    cancel = dialog.select_one(".dialog-foot > a.btn")
    if cancel is not None and cancel.get_text(strip=True) == "Cancel":
        _link_to_button(ctx, cancel, "A15", A15)


# -- A16 --------------------------------------------------------------------
@patch(*CONTACT_EDIT_STATES)
def contacts_inactive_principal_panel_goes(ctx: Ctx) -> None:
    for panel in ctx.all("main .admin-layout > .stack > section.panel"):
        notice = panel.select_one(":scope > .empty > p")
        if notice is not None and notice.get_text(" ", strip=True).startswith("This principal is inactive"):
            ctx.remove(panel, "A16", A16)


@patch(*CONTACT_EDIT_STATES)
def contacts_plain_stacks(ctx: Ctx) -> None:
    for fieldset in ctx.all("main section.panel form > fieldset.stack"):
        form = fieldset.parent
        if form.has_attr("data-report-sending-editor") or "contact-editor" in form.get("class", []):
            continue
        _plain_stack(ctx, fieldset, "A16", A16)


@patch(*CONTACT_EDIT_STATES)
def contacts_replace_shared_dialog(ctx: Ctx) -> None:
    _shared_dialog(ctx, ctx.one("dialog#replace-principal"), "A16", A16)


@patch(*CONTACT_EDIT_STATES)
def contacts_rule_legends_numbered(ctx: Ctx) -> None:
    for number, legend in enumerate(ctx.all("form[data-report-sending-editor] fieldset[data-rs-rule] > legend"), 1):
        legend.string = f"Rule {number}"
        ctx.mark(legend, "A16", A16)


@patch(*CONTACT_EDIT_STATES)
def contacts_small_add_buttons(ctx: Ctx) -> None:
    for button in ctx.all("button[data-add-rs-rule], button[data-add-salvage-band]"):
        if "btn--small" not in button.get("class", []):
            button["class"] = button.get("class", []) + ["btn--small"]
            ctx.mark(button, "A16", A16)


@patch(*CONTACT_EDIT_STATES)
def contacts_api_sentence_goes(ctx: Ctx) -> None:
    for sentence in ctx.all("main section.panel form p"):
        if sentence.get_text(" ", strip=True).startswith("Resetting or revoking"):
            ctx.remove(sentence, "A16", A16)


@patch(*CONTACT_EDIT_STATES)
def contacts_forms_bounded(ctx: Ctx) -> None:
    # Report generation, Location and Principal API take the Contact tab's 720px bound.
    for section in ctx.all("section.panel[aria-labelledby]"):
        if section["aria-labelledby"] not in ("principal-report-title", "principal-location-title", "principal-api-title"):
            continue
        body = section.select_one(":scope > .panel-body")
        if body is not None and "contact-editor" not in body.get("class", []):
            body["class"] = body.get("class", []) + ["contact-editor"]
            ctx.mark(body, "A16", A16)


@patch(*CONTACT_EDIT_STATES)
def contacts_spacer_field_goes(ctx: Ctx) -> None:
    for spacer in ctx.all('.form-grid > div.field[aria-hidden="true"]'):
        if not spacer.get_text(strip=True) and spacer.find(True) is None:
            ctx.remove(spacer, "A16", A16)


@patch(*CONTACT_EDIT_STATES)
def contacts_foot_cancel_then_save(ctx: Ctx) -> None:
    for save in ctx.all("main section.panel form button[type=submit].btn--primary"):
        if not save.get_text(" ", strip=True).startswith("Save"):
            continue
        row = save.find_parent("div", class_="button-row")
        if row is None:
            continue
        cancel = next((link for link in row.find_all("a", class_="btn") if link.get_text(strip=True) == "Cancel"), None)
        if cancel is not None:
            save.insert_before(cancel.extract())
        else:
            save.insert_before(ctx.html('<a class="btn" href="/Administration/Contacts">Cancel</a>'))
        ctx.mark(row, "A16", A16)


# -- A17 --------------------------------------------------------------------
@patch("configuration")
def configuration_reset_buttons_go(ctx: Ctx) -> None:
    for button in ctx.all('main button[type="reset"]'):
        row = button.find_parent("div", class_="button-row")
        ctx.remove(button, "A17", A17)
        ctx.mark(row, "A17", A17)


# -- A18 --------------------------------------------------------------------
_POLL_COMPLETED = re.compile(r"Last completed (?P<time>.+?)\. Next due .+?\.(?: .*)?")
_LAST_ERROR_SENTENCES = {
    "mailbox_access_denied": "The tenant has not granted this application access to this mailbox.",
    "mailbox_not_approved": "The last attempt stopped because this mailbox was no longer approved.",
}


def _last_checked(text: str) -> str:
    completed = _POLL_COMPLETED.fullmatch(text)
    if completed:
        return completed["time"]
    if text in ("Not polled.", "Not activated.", "Not yet polled."):
        return text[:-1]
    return text


@patch(*MAILBOX_STATES)
def mailboxes_last_checked_time_only(ctx: Ctx) -> None:
    for table in ctx.all("table.mailbox-table"):
        headings = [th.get_text(" ", strip=True) for th in table.select("thead th")]
        if "Last checked" not in headings:
            continue
        index = headings.index("Last checked")
        for row in table.select("tbody tr"):
            cells = row.find_all("td", recursive=False)
            if index >= len(cells):
                continue
            text = cells[index].get_text(" ", strip=True)
            if _last_checked(text) != text:
                cells[index].string = _last_checked(text)
                ctx.mark(cells[index], "A18", A18)


@patch(*MAILBOX_STATES)
def mailboxes_last_error_in_words(ctx: Ctx) -> None:
    for term in ctx.all(".dialog-backdrop .definition dt"):
        value = term.find_next_sibling("dd")
        code = value.get_text(strip=True) if value is not None else ""
        if term.get_text(strip=True) == "Last error" and re.fullmatch(r"[a-z0-9]+(?:_[a-z0-9]+)+", code):
            value.string = _LAST_ERROR_SENTENCES.get(code, _action_words(code))
            ctx.mark(value, "A18", A18)


def _mailbox_panel(ctx: Ctx) -> Tag | None:
    return ctx.one('section[aria-labelledby="approved-mailboxes-title"]')


@patch(*MAILBOX_STATES)
def mailboxes_add_mailbox_primary(ctx: Ctx) -> None:
    panel = _mailbox_panel(ctx)
    add = panel.select_one(':scope > .panel-head button[data-dialog-open="new-mailbox-dialog"]') if panel is not None else None
    if add is not None and "btn--primary" not in add.get("class", []):
        add["class"] = [name for name in add.get("class", []) if name != "btn--dark"] + ["btn--primary"]
        ctx.mark(add, "A18", A18)


@patch(*MAILBOX_STATES)
def mailboxes_count_meta(ctx: Ctx) -> None:
    panel = _mailbox_panel(ctx)
    head = panel.select_one(":scope > .panel-head") if panel is not None else None
    rows = [row for row in panel.select("table tbody tr") if row.find("td", attrs={"colspan": True}) is None] if panel is not None else []
    if head is not None and rows:
        _count_meta(ctx, head, _plural(len(rows), "mailbox", "mailboxes"), "A18", A18)


@patch(*MAILBOX_STATES)
def mailboxes_dialogs_share_one_width(ctx: Ctx) -> None:
    add = ctx.one('.dialog-backdrop[data-dialog="new-mailbox-dialog"] > .dialog')
    if add is not None and "dialog--compact" in add.get("class", []):
        add["class"] = [("dialog--contact" if name == "dialog--compact" else name) for name in add["class"]]
        ctx.mark(add, "A18", A18)
        body = add.select_one(".dialog-body")
        if body is not None and "stack" not in body.get("class", []):
            body["class"] = body.get("class", []) + ["stack"]


@patch(*MAILBOX_STATES)
def mailboxes_dialog_close_icon(ctx: Ctx) -> None:
    for close in ctx.all('.dialog-backdrop[data-dialog*="mailbox"] .dialog-head .dialog-close'):
        if close.get_text(strip=True) == "×":
            close.clear()
            close.append(_icon(ctx, "x"))
            ctx.mark(close, "A18", A18)


@patch(*MAILBOX_STATES)
def mailboxes_used_for_choice_label(ctx: Ctx) -> None:
    border = False
    for legend in ctx.all('.dialog-backdrop[data-dialog*="mailbox"] fieldset > legend'):
        if legend.get_text(strip=True) == "Used for":
            ctx.mark(legend.parent, "A18", A18)
            border = True
    for label in ctx.all('.dialog-backdrop[data-dialog*="mailbox"] fieldset label.cluster'):
        if label.select_one('input[type="checkbox"]') is not None:
            label["class"] = ["choice"]
            ctx.mark(label, "A18", A18)
    if border:
        scope = '.dialog-backdrop[data-dialog*="mailbox"] fieldset'
        ctx.style(f"{scope}{{min-width:0;margin:0;padding:0;border:0}}"
                  f"{scope}>legend{{padding:0;margin-bottom:6px;font-size:11px;font-weight:780;color:#45433f}}",
                  "A18", A18)


# -- A19 --------------------------------------------------------------------
@patch("email-templates")
def templates_built_in_wording(ctx: Ctx) -> None:
    for row in ctx.all("tr[data-email-template]"):
        changed = row.select_one("td:nth-of-type(2) > span.muted")
        if changed is not None and changed.get_text(strip=True) == "Not recorded":
            changed.string = "Built-in wording"
            ctx.mark(changed, "A19", A19)


@patch("email-templates")
def templates_action_cell_right_aligned(ctx: Ctx) -> None:
    for row in ctx.all("tr[data-email-template]"):
        actions = row.select_one("td.num")
        if actions is not None:
            actions["class"] = ["right"]
            ctx.mark(actions, "A19", A19)


@patch("email-templates")
def templates_panel_heading_goes(ctx: Ctx) -> None:
    heading = ctx.one('section[aria-labelledby="email-templates-title"] > .panel-head > h2')
    head = heading.parent if heading is not None else None
    if ctx.remove(heading, "A19", A19):
        _drop_empty_head(head)


@patch("email-templates")
def templates_placeholder_label(ctx: Ctx) -> None:
    # OperatorLabels.EmailTemplates.Placeholders is the chip row's existing label (its aria-label).
    for group in ctx.all('.dialog-body > .button-row[role="group"][aria-label]'):
        label = ctx.html('<span class="field-hint"></span>')
        label.string = group["aria-label"]
        group.insert(0, label)
        ctx.mark(label, "A19", A19)


# -- A20 --------------------------------------------------------------------
@patch(*NOTICE_STATES)
def admin_notice_treatment(ctx: Ctx) -> None:
    for notice in ctx.all('main .notice[role="status"]:not([data-confirmation])'):
        classes = notice.get("class", [])
        if any(name in classes for name in ("notice--warning", "notice--danger", "notice--info")):
            continue
        if "notice--success" not in classes:
            notice["class"] = classes + ["notice--success"]
        if notice.find("svg") is None:
            for node in list(notice.children):
                if isinstance(node, NavigableString) and node.strip():
                    text = ctx.html("<span></span>")
                    text.string = node.strip()
                    node.replace_with(text)
            notice.insert(0, _icon(ctx, "check-circle"))
        ctx.mark(notice, "A20", A20)


@patch(*CONFIRMATION_STATES)
def admin_local_confirmation_goes(ctx: Ctx) -> None:
    layout = ctx.one("[data-confirmation]")
    if layout is None:
        return
    shown = layout.get_text(" ", strip=True)
    for local in ctx.all('.admin-layout .notice--success[role="status"]'):
        if local.get_text(" ", strip=True) == shown:
            ctx.remove(local, "A20", A20)


@patch(*REPEATED_HEADING_STATES)
def admin_repeated_panel_heading_goes(ctx: Ctx) -> None:
    title = ctx.one("main h1")
    if title is None:
        return
    for panel in ctx.all(".admin-layout > .stack > section.panel"):
        heading = panel.select_one(":scope > .panel-head h2")
        if heading is None:
            continue
        if not title.get_text(" ", strip=True).lower().startswith(heading.get_text(" ", strip=True).lower()):
            continue
        head = heading.find_parent(class_="panel-head")
        ctx.remove(heading, "A20", A20)
        _drop_empty_head(head)
        ctx.mark(panel, "A20", A20)


@patch(*MAILBOX_STATES, "admin-release-notes")
def admin_empty_state(ctx: Ctx) -> None:
    for wrap in ctx.all("main .table-wrap"):
        rows = wrap.select("tbody tr")
        if len(rows) == 1 and len(rows[0].find_all("td")) == 1 and rows[0].find("td", attrs={"colspan": True}):
            empty = ctx.html('<div class="empty"><p></p></div>')
            empty.find("p").string = rows[0].get_text(" ", strip=True)
            wrap.replace_with(empty)
            ctx.mark(empty, "A20", A20)


@patch(*ADMIN_STATES)
def admin_one_primary_button_class(ctx: Ctx) -> None:
    for button in ctx.all("main button.btn--dark"):
        text = button.get_text(" ", strip=True)
        if text == "Apply" or text.startswith("Add"):
            button["class"] = [name for name in button["class"] if name != "btn--dark"] + ["btn--primary"]
            ctx.mark(button, "A20", A20)


# -- A21 --------------------------------------------------------------------
def _presets_head(ctx: Ctx) -> Tag | None:
    panel = ctx.one('section[aria-labelledby="valuation-presets-title"]')
    return panel.select_one(":scope > .panel-head") if panel is not None else None


@patch("valuation-presets")
def presets_head_reads_presets(ctx: Ctx) -> None:
    head = _presets_head(ctx)
    heading = head.find("h2", recursive=False) if head is not None else None
    if heading is not None:
        heading.string = "Presets"
        ctx.mark(heading, "A21", A21)


@patch("valuation-presets")
def presets_count_takes_panel_title_meta(ctx: Ctx) -> None:
    head = _presets_head(ctx)
    heading = head.find("h2", recursive=False) if head is not None else None
    count = head.find("span", class_="meta", recursive=False) if head is not None else None
    if heading is not None and count is not None:
        text = count.get_text(" ", strip=True)
        count.decompose()
        _count_meta(ctx, head, text, "A21", A21)


@patch("valuation-presets")
def presets_enabled_column(ctx: Ctx) -> None:
    for heading in ctx.all("table.preset-table thead th"):
        if heading.get_text(strip=True) == "State":
            heading.string = "Enabled"
            ctx.mark(heading, "A21", A21)


@patch("valuation-presets")
def presets_amount_money_wrapper(ctx: Ctx) -> None:
    for field in ctx.all("table.preset-table input.input-money"):
        wrapper = ctx.html('<div class="input-money"></div>')
        field.insert_before(wrapper)
        classes = [name for name in field.get("class", []) if name != "input-money"]
        if classes:
            field["class"] = classes
        else:
            del field["class"]
        wrapper.append(field.extract())
        ctx.mark(wrapper, "A21", A21)


# ===========================================================================
# Stage 2 step 1, admin-2: A22-A30 (plan-2026-10-15.md section 2.3), over the rulings
# R156 (the Engineers tab keeps its previous-period figures), R159 (a) (no Service health
# truncation notice) and (g) (the Logs Area binding stays), R160 (a stopped AI job reads Cancelled).
# A29 is Stage 2 only: it has no patch.
# ===========================================================================
A22 = ("Service health: Working chips take the green tone. A Needs attention row shows its mapped reason under the chip "
       "the way the Intake log does (small.admin-service-area, which Stage 2 treats as shared and moves to site.css); "
       "no captured row carries a failure code, so none is drawn here.")
A23 = ("Automation and AI: the scope reads Received files, the checkbox reads Send to AI, the AI settings panel shows its "
       "state once (the chip goes, the checkbox states it) and Stop automation sits at the end of its panel on the right "
       "like Save AI settings. Registered clients and Client identifier collapse to one fact when they are equal (they "
       "differ on the capture, so nothing is drawn). QUESTION: the label of that one fact; the plan writes Client and no "
       "existing label is that word. Stage 2: the notice and the error summary sit inside the admin column (neither is "
       "on the capture), the dead Reason binding goes and FRD-17's optional-reason line is aligned, since no reason is captured.")
A24 = ("Logs: the Recorded counts and processing times panel goes (Service health owns service facts). Action logs: the "
       "filter labels match their column headers (Keywords to Search, Activity to Action, Case/reference to Reference, "
       "Outcome to Result). Intake log: the tiles read Failed files and Oldest file waiting and take the shared metric "
       "strip, and the filter takes the Action logs structure with a primary Apply. The drawer takes the shared dialog "
       "frame with one close (the x) and drops the facts the row already shows (Received, Source, Outcome, Became), keeping "
       "Attempts and the evidence. Stage 2: the logs-tabs class and the logs.css colour fallbacks go.")
A25 = ("Problem reports: the Unknown chip reads Delivery unknown, Page shows the page name instead of a route, and the table "
       "caption that repeats the page title goes (A20 takes the panel heading). Stage 2: a failed Retry gives no feedback.")
A26 = ("Management reports: four tabs under the period bar, Engineers / Principals / Queues / Case list, as ?tab= links "
       "like Logs; Download workbook stays in the header; the six Case-list fieldsets lose their borders. Stage 2: "
       "LoadAsync scopes its reads by tab through the existing Reads flags; the header uses the shared "
       "page-header pattern (_PageHeader secondary action, eyebrow from the label).")
A27 = ("Release notes: the list heading goes (A20), the edit page's eyebrow reads Administration like its siblings, a draft "
       "row's three Not recorded cells read an em dash, and the page for a new note does not repeat its title in the panel head.")
A28 = ("AI jobs: Stop is one small danger button with no reason form, the kind reads AI Proposal (no captured job is an "
       "Estimate), the meta reads Send to AI on or off, a stopped job reads Cancelled (the state's own word, R160; no "
       "captured job is stopped) and the Action header aligns over its buttons. The status notice takes the shared tone "
       "(A20) and a Case subject links to the Case (A8). Stage 2: Stop posts no reason; the reason is optional (R160, FRD-27).")
A30 = "Contacts list: Apply renders only without script (noscript), as FRD-17 says, for no-script use; the Proposal hides it."

# -- A22--------------------------------------------------------------------
@patch("health")
def health_working_chips_green(ctx: Ctx) -> None:
    for chip in ctx.all(".service-health-table td .status--neutral"):
        if chip.get_text(strip=True) == "Working":
            chip["class"] = ["status", "status--green"]
            ctx.mark(chip, "A22", A22)


# -- A23 --------------------------------------------------------------------
@patch("automation")
def automation_scope_received_files(ctx: Ctx) -> None:
    for scope in ctx.all('.fact-grid dd span[title="automation.intake"]'):
        if scope.get_text(strip=True) == "Intake":
            scope.string = "Received files"
            ctx.mark(scope, "A23", A23)


@patch("automation")
def automation_send_to_ai_label(ctx: Ctx) -> None:
    box = ctx.one("input#SendToAiEnabled")
    label = box.find_parent("label") if box is not None else None
    text = label.find("span") if label is not None else None
    if text is not None and text.get_text(strip=True) == "Reviewed AI proposals enabled":
        text.string = "Send to AI"
        ctx.mark(text, "A23", A23)


@patch("automation")
def automation_ai_state_once(ctx: Ctx) -> None:
    ctx.remove(ctx.one('section[aria-labelledby="ai-settings-panel-title"] > .panel-head > .status'), "A23", A23)


@patch("automation")
def automation_stop_placement(ctx: Ctx) -> None:
    stop = ctx.one('form[action$="handler=SetEnabled"]')
    if stop is not None and "admin-actions-end" not in stop.get("class", []):
        stop["class"] = stop.get("class", []) + ["admin-actions-end"]
        ctx.mark(stop, "A23", A23)


# -- A24 --------------------------------------------------------------------
_LOG_FILTER_LABELS = {"Keywords": "Search", "Activity": "Action", "Case/reference": "Reference", "Outcome": "Result"}
_DRAWER_FACTS_ON_THE_ROW = ("Received", "Source", "Outcome", "Became")
_INTAKE_TILE_LABELS = {"Failed intake": "Failed files", "Oldest pending intake": "Oldest file waiting"}
LOGS_INTAKE_STATES = ("logs-intake", "logs-intake-drawer")


@patch("logs")
def logs_diagnostics_panel_goes(ctx: Ctx) -> None:
    for panel in ctx.all("details.panel"):
        summary = panel.find("summary", recursive=False)
        if summary is not None and summary.get_text(" ", strip=True) == "Recorded counts and processing times":
            ctx.remove(panel, "A24", A24)


@patch("logs")
def logs_filter_labels_match_columns(ctx: Ctx) -> None:
    for label in ctx.all("form.compact-log-filter label"):
        words = _LOG_FILTER_LABELS.get(label.get_text(" ", strip=True))
        if words is not None:
            label.string = words
            ctx.mark(label, "A24", A24)


@patch(*LOGS_INTAKE_STATES)
def logs_intake_tiles_metric_strip(ctx: Ctx) -> None:
    strip = ctx.one(".figures.logs-figures[data-intake-counts]")
    if strip is None:
        return
    strip["class"] = ["metric-strip"]
    for tile in strip.select(":scope > .figure"):
        tile["class"] = ["metric"]
        for part, name in (("label", "metric-label"), ("value", "metric-value")):
            span = tile.find("span", class_=part, recursive=False)
            if span is not None:
                span["class"] = [name]
                if part == "label":
                    span.string = _INTAKE_TILE_LABELS.get(span.get_text(" ", strip=True), span.get_text(" ", strip=True))
    ctx.mark(strip, "A24", A24)
    # The shared strip is three columns; two tiles fill the row (the strip keeps its data hook).
    ctx.style(".metric-strip[data-intake-counts]{grid-template-columns:repeat(2,minmax(0,1fr))}", "A24", A24)


@patch(*LOGS_INTAKE_STATES)
def logs_intake_filter_structure(ctx: Ctx) -> None:
    form = ctx.one("form.logs-filter")
    fields = form.select_one(":scope > .logs-filter__fields") if form is not None else None
    head = ctx.one('section[aria-labelledby="intake-log-title"] > .panel-head')
    if form is None or fields is None or head is None:
        return
    for child in list(fields.children):
        form.append(child.extract())
    fields.decompose()
    form["class"] = ["compact-log-filter"]
    body = ctx.html('<div class="panel-body panel-body--compact"></div>')
    body.append(form.extract())
    head.insert_after(body)
    apply = form.select_one('button[type="submit"]')
    if apply is not None and "btn--dark" in apply.get("class", []):
        apply["class"] = [name for name in apply["class"] if name != "btn--dark"] + ["btn--primary"]
    ctx.mark(form, "A24", A24)


@patch("logs-intake-drawer")
def logs_drawer_shared_dialog(ctx: Ctx) -> None:
    drawer = ctx.one("aside.logs-drawer")
    head = drawer.select_one(":scope > .logs-drawer__head") if drawer is not None else None
    body = drawer.select_one(":scope > .logs-drawer__body") if drawer is not None else None
    foot = drawer.select_one(":scope > .logs-drawer__foot") if drawer is not None else None
    heading = head.find("h2") if head is not None else None
    close = head.select_one("a.icon-button") if head is not None else None
    if heading is None or close is None or body is None or foot is None:
        return
    for term in body.select("dl.logs-facts > dt"):
        if term.get_text(" ", strip=True) in _DRAWER_FACTS_ON_THE_ROW:
            ctx.remove(term.find_next_sibling("dd"), "A24", A24)
            term.decompose()
    for link in foot.find_all("a", class_="btn", recursive=False):
        if link.get_text(strip=True) == "Close":
            link.decompose()
    heading.extract()
    heading["tabindex"] = "-1"
    heading["data-dialog-initial-focus"] = ""
    close.extract()
    close["class"] = ["dialog-close"]
    body.extract()
    body["class"] = ["dialog-body", "stack"]
    foot.extract()
    foot["class"] = ["dialog-foot"]
    dialog = ctx.html('<div class="dialog-backdrop" data-dialog="intake-drawer" data-dialog-open-on-load="true">'
                      '<section class="dialog" role="dialog" aria-modal="true"></section></div>')
    section = dialog.find("section")
    section["aria-labelledby"] = drawer.get("aria-labelledby", "")
    if drawer.get("data-intake-drawer"):
        section["data-intake-drawer"] = drawer["data-intake-drawer"]
    dialog_head = ctx.html('<div class="dialog-head"></div>')
    dialog_head.append(heading)
    dialog_head.append(close)
    section.append(dialog_head)
    section.append(body)
    section.append(foot)
    # Like the other Administration dialogs, the frame sits in the page content, not in the column.
    content = drawer.find_parent(class_="content")
    drawer.decompose()
    (content if content is not None else ctx.body).append(dialog)
    ctx.mark(dialog, "A24", A24)


# -- A25 --------------------------------------------------------------------
@patch("problem-reports")
def problem_reports_delivery_unknown(ctx: Ctx) -> None:
    for chip in ctx.all("table[data-problem-reports] td .status"):
        if chip.get_text(strip=True) == "Unknown":
            chip.string = "Delivery unknown"
            ctx.mark(chip, "A25", A25)


@patch("problem-reports")
def problem_reports_page_name(ctx: Ctx) -> None:
    # The page name is the route's first segment (/Cases/<guid> reads Cases); only /Cases is on the capture.
    for table in ctx.all("table[data-problem-reports]"):
        headings = [th.get_text(" ", strip=True) for th in table.select("thead th")]
        if "Page" not in headings:
            continue
        for row in table.select("tbody tr"):
            cells = row.find_all("td", recursive=False)
            cell = cells[headings.index("Page")] if headings.index("Page") < len(cells) else None
            route = cell.get_text(strip=True) if cell is not None else ""
            name = route.split("?")[0].strip("/").split("/")[0]
            if cell is not None and route.startswith("/") and name:
                cell.string = name
                cell.attrs.pop("class", None)
                ctx.mark(cell, "A25", A25)


@patch("problem-reports")
def problem_reports_caption_goes(ctx: Ctx) -> None:
    title = ctx.one("main h1")
    for caption in ctx.all("table[data-problem-reports] > caption"):
        if title is not None and caption.get_text(" ", strip=True) == title.get_text(" ", strip=True):
            ctx.remove(caption, "A25", A25)


# -- A26 --------------------------------------------------------------------
_REPORT_TABS = (("engineers", "Engineers"), ("principals", "Principals"), ("queues", "Queues"), ("case-list", "Case list"))
_REPORT_TAB_OF_STATE = dict(zip(REPORTS_STATES, (key for key, _ in _REPORT_TABS)))
_REPORT_TAB_OF_PANEL = {
    "mi01-title": "engineers",
    "mi02-title": "principals", "months-title": "principals", "outcomes-title": "principals", "mi03-title": "principals",
    "queues-title": "queues",
    "mi04-title": "case-list",
}


@patch(*REPORTS_STATES)
def reports_tabs(ctx: Ctx) -> None:
    stack = ctx.one(".admin-layout > .stack")
    period = ctx.one("form.admin-report-period")
    active = _REPORT_TAB_OF_STATE.get(ctx.key)
    if stack is None or period is None or active is None:
        return
    nav = ctx.html('<nav class="tabs" aria-label="Management Reports"></nav>')
    for key, label in _REPORT_TABS:
        link = ctx.html(f'<a class="tab" href="/Administration/Reports?tab={key}">{label}</a>')
        if key == active:
            link["aria-current"] = "page"
        nav.append(link)
    period.insert_after(nav)
    ctx.mark(nav, "A26", A26)
    for panel in stack.find_all("section", recursive=False):
        tab = _REPORT_TAB_OF_PANEL.get(panel.get("aria-labelledby"))
        if tab is not None and tab != active:
            ctx.remove(panel, "A26", A26)


@patch(*REPORTS_STATES)
def reports_case_list_fieldsets_borderless(ctx: Ctx) -> None:
    fieldsets = ctx.all("section[data-case-list] form fieldset")
    for fieldset in fieldsets:
        ctx.mark(fieldset, "A26", A26)
    if fieldsets:
        scope = "section[data-case-list] form fieldset"
        ctx.style(f"{scope}{{min-width:0;margin:0;padding:0;border:0}}"
                  f"{scope}>legend{{padding:0;margin-bottom:6px;font-size:11px;font-weight:780;color:#45433f}}",
                  "A26", A26)


# -- A27 --------------------------------------------------------------------
RELEASE_NOTE_PAGES = ("release-note-edit", "release-note-new", "release-note-published")


@patch("admin-release-notes")
def release_notes_draft_absent_cells(ctx: Ctx) -> None:
    for row in ctx.all("table[data-release-notes] tbody tr"):
        chip = row.select_one(".status")
        if chip is None or chip.get_text(strip=True) != "Draft":
            continue
        for cell in row.find_all("td", recursive=False):
            if cell.get_text(strip=True) == "Not recorded":
                cell.string = "—"
                ctx.mark(cell, "A27", A27)


@patch(*RELEASE_NOTE_PAGES)
def release_note_eyebrow(ctx: Ctx) -> None:
    eyebrow = ctx.one("main .page-header .eyebrow")
    if eyebrow is not None and eyebrow.get_text(strip=True) == "Release notes":
        eyebrow.string = "Administration"
        ctx.mark(eyebrow, "A27", A27)


@patch("release-note-new")
def release_note_new_heading_goes(ctx: Ctx) -> None:
    title = ctx.one("main h1")
    heading = ctx.one('section[aria-labelledby="release-note-title"] > .panel-head > h2')
    if title is None or heading is None or heading.get_text(" ", strip=True) != title.get_text(" ", strip=True):
        return
    head = heading.parent
    ctx.remove(heading, "A27", A27)
    _drop_empty_head(head)


# -- A28 --------------------------------------------------------------------
@patch("ai-jobs")
def ai_jobs_stop_one_click(ctx: Ctx) -> None:
    for details in ctx.all("table[data-admin-ai-jobs] td.row-actions > details"):
        form = details.find("form")
        confirm = form.select_one('button[type="submit"]') if form is not None else None
        if form is None or confirm is None:
            continue
        for reason in form.select('label, input[name="reason"]'):
            reason.decompose()
        confirm.string = "Stop"
        form.attrs.pop("class", None)
        details.replace_with(form.extract())
        ctx.mark(confirm, "A28", A28)


@patch("ai-jobs")
def ai_jobs_meta_send_to_ai(ctx: Ctx) -> None:
    for meta in ctx.all("span.meta[data-ai-jobs-counts]"):
        text = meta.get_text(" ", strip=True)
        for old, new in (("· Active", "· Send to AI on"), ("· Stopped", "· Send to AI off")):
            if text.endswith(old):
                meta.string = text[: -len(old)] + new
                ctx.mark(meta, "A28", A28)
                break


@patch("ai-jobs")
def ai_jobs_kind_ai_proposal(ctx: Ctx) -> None:
    for kind in ctx.all("table[data-admin-ai-jobs] tbody td > strong"):
        if kind.get_text(strip=True) == "Estimate":
            kind.string = "AI Proposal"
            ctx.mark(kind, "A28", A28)


@patch("ai-jobs")
def ai_jobs_action_header_aligned(ctx: Ctx) -> None:
    # The row-actions cells sit at the row's end, so the Action header sits over them.
    for heading in ctx.all("table[data-admin-ai-jobs] thead th"):
        if heading.get_text(strip=True) == "Action":
            heading["class"] = ["right"]
            ctx.mark(heading, "A28", A28)


# -- A30 --------------------------------------------------------------------
@patch("contacts", "contacts-create")
def contacts_apply_without_script(ctx: Ctx) -> None:
    toolbar = ctx.one("form.contact-toolbar")
    apply = toolbar.select_one(':scope > button[type="submit"]') if toolbar is not None else None
    if apply is None or apply.get_text(strip=True) != "Apply":
        return
    wrapper = ctx.html("<noscript></noscript>")
    apply.insert_before(wrapper)
    wrapper.append(apply.extract())
    ctx.mark(toolbar, "A30", A30)
