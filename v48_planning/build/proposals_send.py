"""v48 Proposal patches: Send report moves from the Report section into a composer dialog.

The letters are the sign-off items in notes/v48-notes.md §6.
  A  Send report opens from a head primary (editing, report Stored) and from Next action
  B  the dialog is the Triage composer's shape (.dialog.mail-compose-dialog) at 880px
  C  Subject, editable, prefilled with the derived subject (ReportDispatchPolicy.Subject)
  D  Files: one row per attachment; the name opens the viewer; the include tick is the live one
  E  every attachment renameable: the stem, .pdf fixed, Reset to the policy name
  F  preview opens the Case viewer over the dialog (the runtime lifts the dialog's inert)
  G  the Report section keeps the preview card; the inline form and the greyed read cells go
  N  Already sent reads under the preview card as well as in the dialog

Every field, notice, question, hold and tick is the live node moved into the dialog, so its
name, label, hooks and words are the application's. Only Subject, the Files rows' names and
sizes, the rename controls and the Cancel button are new. Labels: "Send report" is the live
submit's; "Subject", "From", "To", "Cc", "Message" are the Triage composer's; "Files" is the
section's name; "Cancel" is the shared dialog word; "Rename" and "Reset" are the controls'
names.
"""
from __future__ import annotations

import re

from bs4 import Tag

from proposals_v48 import Anchor, Ctx, patch
from states_v48 import EDIT_STATES, READ_STATES, STATES

DIALOG_ID = "case-send-report-dialog"
ICON = '<svg class="icon" aria-hidden="true"><use href="#icon-{name}"></use></svg>'
# Synthetic sizes for the files behind a mockup (there are no files): MB to one decimal, as
# OperatorLabels.FileSize draws them.
SIZES = {"AssessmentReport": "1.2 MB", "FeeNote": "under 0.1 MB", "RepairSpecification": "0.3 MB",
         "ImagePack": "4.8 MB", "estimate": "0.2 MB"}
KIND_LABEL = {"AssessmentReport": "Report", "FeeNote": "Fee note", "RepairSpecification": "Repair Spec",
              "ImagePack": "Images"}

CSS = """
/* B: the Triage composer's dialog, 880px (the Inbox message dialog's width), 1100 as a variable. */
.dialog.mail-compose-dialog.dialog--send{width:min(880px,calc(100vw - 32px));height:min(760px,calc(100vh - 40px))}
html[data-v48-opt-width="1100"] .dialog.mail-compose-dialog.dialog--send{width:min(1100px,calc(100vw - 32px))}
/* The delivery form's own rules, scoped to the section today, follow it into the dialog. */
.dialog--send .mail-compose-form .lg,.dialog--send .mail-compose-form .lbl{font-size:10.5px;color:var(--quiet);font-weight:650;text-transform:uppercase;letter-spacing:.06em}
.dialog--send .mail-compose-form .stack{display:grid;gap:4px}
.dialog--send .mail-compose-form input:not([type=checkbox]):not([type=radio]),.dialog--send .mail-compose-form select{min-height:var(--control);padding:6px 9px;border:1px solid var(--line-strong);border-radius:var(--radius);font-size:13px;width:100%;background:#fff}
.dialog--send .mail-compose-form .btn{justify-self:start}
.dialog--send .choice{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:500;white-space:nowrap}
.dialog--send .choice input{width:15px;height:15px;min-height:0;accent-color:var(--red)}
.dialog--send .choice.is-static{cursor:default;color:var(--muted)}
.dialog--send .choice.is-static[data-on="true"]{color:var(--ink)}
.dialog--send .choice.is-static .tick{display:inline-grid;place-items:center;width:15px;height:15px;flex:none;border:1px solid var(--line-strong);border-radius:2px;background:var(--surface-2)}
.dialog--send .choice.is-static .tick .icon{width:11px;height:11px}
.dialog--send .cluster{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.dialog--send .mail-compose-form-fields>.v48-block{display:grid;gap:6px}
.dialog--send .mail-compose-addresses .field .stack+.btn{margin-top:4px}
/* F: the viewer takes focus when it opens, and site.css's [tabindex]:focus-visible rule
   (z-index:2) outranks .case-viewer's 1200 on specificity; under a dialog at 1000 the viewer
   would sit behind it. The implementation needs this rule, or an equivalent. */
.case-viewer[tabindex]:focus-visible{z-index:1200}
/* O: each recipient box with its × (operator, 4 November 2026). */
.dialog--send .v48-recipient{display:flex;gap:6px;align-items:center}
.dialog--send .v48-recipient input{flex:1 1 auto;min-width:0}
.dialog--send .v48-recipient .btn--icon{flex:none;padding:0;width:28px;min-height:28px;justify-content:center;justify-self:auto}
.dialog--send .v48-recipient .btn--icon[hidden]{display:none}
.dialog--send .mail-compose-message textarea{min-height:120px}
/* D: Files, one row each, in the Files section's row shape: tick · glyph · name and kind · Rename. */
.dialog--send .mail-compose-attachments{max-height:none;border:0;padding:0;display:grid;gap:6px}
.dialog--send .mail-compose-attachments>legend{font-size:10.5px;color:var(--quiet);font-weight:650;text-transform:uppercase;letter-spacing:.06em;padding:0;margin-bottom:2px}
.dialog--send .v48-file{display:grid;grid-template-columns:auto 20px minmax(0,1fr) auto;gap:9px;align-items:center;padding:6px 9px;border:1px solid var(--line);border-radius:3px;font-size:12px}
.dialog--send .v48-file>.icon{color:var(--muted);width:18px;height:18px}
.dialog--send .v48-file .choice{position:relative}
.dialog--send .v48-file .choice>span:not(.tick){position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.dialog--send .v48-file-name{min-width:0;display:grid;gap:1px}
.dialog--send .v48-file-open{appearance:none;background:none;border:0;padding:0;margin:0;font:inherit;text-align:left;color:var(--ink);font-weight:650;cursor:pointer;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-height:0}
.dialog--send .v48-file-open:hover{color:var(--red);text-decoration:underline}
.dialog--send .v48-file-open:focus-visible{outline:3px solid var(--focus);outline-offset:2px;border-radius:2px}
.dialog--send .v48-file small{color:var(--muted);font-size:10.5px}
.dialog--send .v48-rename-row{display:flex;align-items:center;gap:6px}
.dialog--send .v48-rename-row input{flex:1 1 auto;min-width:0}
.dialog--send .v48-rename-row .mono{color:var(--muted);font-size:12px}
.dialog--send .v48-rename-row .btn{flex:none;justify-self:auto}
.dialog--send .v48-file [hidden]{display:none!important}
.dialog--send .v48-file .btn--icon{padding:0;width:28px;min-height:28px;justify-content:center}
/* Files beside the message (a variable): two columns from 900px up. */
@media(min-width:900px){
html[data-v48-opt-files="beside"] .dialog--send .mail-compose-form-fields{display:grid;grid-template-columns:minmax(0,1fr) minmax(300px,36%);grid-auto-rows:max-content;align-items:start;column-gap:14px;row-gap:9px}
html[data-v48-opt-files="beside"] .dialog--send .mail-compose-form-fields>*{grid-column:1}
html[data-v48-opt-files="beside"] .dialog--send .mail-compose-form-fields>.mail-compose-attachments{grid-column:2;grid-row:1/span 12;align-self:stretch;align-content:start}
html[data-v48-opt-files="beside"] .dialog--send .mail-compose-form-fields>.mail-compose-message textarea{min-height:200px}
}
@media(max-width:540px){.dialog.mail-compose-dialog.dialog--send{height:calc(100vh - 20px)}}
"""


def edit_keys() -> tuple[str, ...]:
    return EDIT_STATES


def is_audit_view(ctx: Ctx) -> bool:
    return ctx.one('[data-case-view-row="audit"] [aria-current="page"]') is not None


def has_audit(ctx: Ctx) -> bool:
    return ctx.one("[data-case-views]") is not None


# ---------------------------------------------------------------------------
# A: the openers
# ---------------------------------------------------------------------------

@patch(*EDIT_STATES)
def head_opener(ctx: Ctx) -> None:
    """A: Send report is the Report head's primary while editing with the report Stored."""
    form = ctx.one("#section-report form[data-send-report]")
    if form is None:
        raise Anchor(f"{ctx.key}: the inline send form is not in this capture")
    actions = ctx.need("#section-report .panel-head .panel-actions")
    if actions.select_one(".btn--primary") is not None:
        raise Anchor(f"{ctx.key}: the Report head already has a primary (Generate report)")
    submit = form.select_one('button[type="submit"]')
    label = submit.select_one("span").get_text(strip=True) if submit else "Send report"
    opener = ctx.html(
        f'<button type="button" class="btn btn--small btn--primary" data-dialog-open="{DIALOG_ID}" data-v48-send-open>'
        f'{ICON.format(name="send")}<span>{label}</span></button>')
    actions.insert(0, opener)
    ctx.mark(opener, "A", "Send report is the Report head's primary while editing; it opens the dialog")


@patch(*EDIT_STATES)
def next_action_opener(ctx: Ctx) -> None:
    """A: the aside's Send report step opens the dialog instead of jumping to the section."""
    for step in ctx.all("[data-next-action] [data-next-step]"):
        label = step.select_one("[data-next-label]")
        if label is None or label.get_text(strip=True) != "Send report":
            continue
        jump = step.select_one('a[data-section-jump="report"]')
        if jump is None:
            raise Anchor(f"{ctx.key}: the Send report step has no section jump")
        button = ctx.html(
            f'<button type="button" class="{" ".join(jump.get("class", []))}" data-dialog-open="{DIALOG_ID}" '
            f'data-v48-send-open-next>{jump.get_text(strip=True)}</button>')
        jump.replace_with(button)
        ctx.mark(button, "A", "Send report is the Report head's primary while editing; it opens the dialog")


# ---------------------------------------------------------------------------
# B–F: the dialog
# ---------------------------------------------------------------------------

def take(ctx: Ctx, form: Tag, css: str, required: bool = False) -> Tag | None:
    node = form.select_one(css)
    if node is None:
        if required:
            raise Anchor(f"{ctx.key}: {css} is not in the send form")
        return None
    return node.extract()


def take_all(form: Tag, css: str) -> list[Tag]:
    return [node.extract() for node in form.select(css)]


def label_before(form: Tag, node: Tag) -> Tag | None:
    """The .lbl / label element just before a control, when the form draws one."""
    previous = node.find_previous_sibling()
    if previous is not None and ("lbl" in previous.get("class", []) or previous.name == "label"):
        return previous
    return None


def file_row(ctx: Ctx, key: str, name: str, kind: str, size: str, tick: Tag, post_name: str | None,
             change: bool = True) -> Tag:
    """D/E: one Files row: the tick (the live element), the glyph, the name (opens the viewer),
    the kind and size, and Rename. The posted name is empty until renamed."""
    stem = name[:-4] if name.lower().endswith(".pdf") else name
    row = ctx.html(
        f'<div class="v48-file" data-v48-file="{key}" data-v48-default="{name}">'
        f'<span class="v48-file-tick"></span>'
        f'{ICON.format(name="file-text")}'
        f'<div class="v48-file-name">'
        f'<button type="button" class="v48-file-open" data-v48-file-open data-file-name="{name}" '
        f'title="Open {name}"><b>{name}</b></button>'
        f'<span class="v48-rename-row" data-v48-rename-row hidden>'
        f'<input type="text" aria-label="File name" value="{stem}" maxlength="120" />'
        f'<span class="mono">.pdf</span>'
        f'<button type="button" class="btn btn--small" data-v48-rename-reset>Reset</button>'
        f'</span>'
        f'<small>{kind} · {size}</small>'
        f'</div>'
        f'<span class="v48-file-actions">'
        f'<button type="button" class="btn btn--small btn--icon" data-v48-rename title="Rename" aria-label="Rename {name}">'
        f'{ICON.format(name="pencil")}</button>'
        f'</span>'
        + (f'<input type="hidden" name="{post_name}" value="" data-v48-file-name />' if post_name else "")
        + '</div>')
    row.select_one(".v48-file-tick").append(tick)
    return row


def artifact_names(facts: dict, which: str = "artifacts") -> dict[str, str]:
    return {item["kind"]: item["fileName"] for item in facts.get(which) or [] if item.get("fileName")}


def static_tick(ctx: Ctx, label: str) -> Tag:
    return ctx.html(
        f'<span class="choice is-static" data-on="true"><span class="tick">{ICON.format(name="check")}</span>'
        f'<span>{label}</span></span>')


def build_files(ctx: Ctx, form: Tag) -> Tag:
    """D: the Files list from the live Attach ticks, the other work's report and the filed estimates."""
    facts = ctx.facts
    names = artifact_names(facts)
    report_name = ctx.need("[data-report-file-name]", form).get_text(strip=True)
    files = ctx.html('<fieldset class="field mail-compose-attachments v48-files" data-v48-files><legend>Files</legend></fieldset>')

    attach = take(ctx, form, "[data-report-attach]", required=True)
    for choice in attach.select("[data-report-attach-choice]"):
        kind = choice.get("data-report-attach-choice")
        tick = choice.find_parent("label") if choice.name == "input" else choice
        tick = tick.extract()
        hidden = None
        if tick.name == "span":
            # The static tick posts its kind through the hidden input that followed it.
            hidden = attach.select_one(f'input[type="hidden"][name="attach"][value="{kind}"]')
            if hidden is not None:
                hidden = hidden.extract()
        name = report_name if kind == "AssessmentReport" else names.get(kind, f"{kind}.pdf")
        label = KIND_LABEL.get(kind, kind)
        row = file_row(ctx, kind, name, label, SIZES.get(kind, "0.1 MB"), tick, f"fileName-{kind}")
        if hidden is not None:
            row.append(hidden)
        files.append(row)
    rest = attach.get_text(strip=True)
    if rest:
        raise Anchor(f"{ctx.key}: Attach held more than its ticks: {rest!r}")

    # The filed estimates the Principal's rules attach (static rows, posting nothing, as live).
    filed = take(ctx, form, "[data-report-filed-estimates]")
    if filed is not None:
        filed_label = label_before(form, filed) if filed.parent else None
        for index, name in enumerate(part.strip() for part in filed.get_text(strip=True).split(",")):
            if not name:
                continue
            files.append(file_row(ctx, f"estimate-{index}", name, "Filed estimate", SIZES["estimate"],
                                  static_tick(ctx, "Filed estimate"), None))
    for lbl in form.select(".lbl"):
        if lbl.get_text(strip=True) in ("Filed estimate", "File name", "Attach"):
            lbl.decompose()

    # The other work's report and its documents (Audit exists), each its own row.
    other = take(ctx, form, "[data-report-attach-other]")
    if other is not None:
        other_facts = facts.get("other") or {}
        other_names = artifact_names(other_facts)
        view_word = "Inspection" if is_audit_view(ctx) else "Audit"
        report_tick = other.select_one("[data-report-attach-other-report]").find_parent("label").extract()
        report_label = report_tick.select_one("span").get_text(strip=True)
        version = other.select_one('input[type="hidden"][name="secondExpectedGenerationVersion"]').extract()
        row = file_row(ctx, "other-AssessmentReport", report_label, f"{view_word} · Report", SIZES["AssessmentReport"],
                       report_tick, "secondFileName-AssessmentReport")
        row.append(version)
        files.append(row)
        for choice in other.select("[data-report-attach-other-choice]"):
            kind = choice.get("data-report-attach-other-choice")
            tick = choice.find_parent("label").extract()
            name = other_names.get(kind, f"{kind}.pdf")
            files.append(file_row(ctx, f"other-{kind}", name, f"{view_word} · {KIND_LABEL.get(kind, kind)}",
                                  SIZES.get(kind, "0.1 MB"), tick, f"secondFileName-{kind}"))
    take(ctx, form, "[data-report-file-name]", required=True)
    return files


def field(ctx: Ctx, css_class: str, label_html: str, *controls: Tag) -> Tag:
    box = ctx.html(f'<div class="field {css_class}">{label_html}</div>')
    for control in controls:
        if control is not None:
            box.append(control)
    return box


@patch(*EDIT_STATES)
def dialog(ctx: Ctx) -> None:
    """B–F: the live form, moved whole into a composer dialog mounted with the Case dialogs."""
    form = ctx.need("#section-report form[data-send-report]").extract()
    facts = ctx.facts
    form["class"] = ["mail-compose-form"]
    fields = ctx.html('<div class="mail-compose-form-fields"></div>')
    footer = ctx.html('<footer class="mail-compose-footer"></footer>')

    # Notices first: Already sent, the Stop and its reason, the missing companion.
    for css in ("[data-report-already-sent]", "[data-report-stop]"):
        node = take(ctx, form, css)
        if node is not None:
            fields.append(node)
    override = take(ctx, form, "#report-stop-override")
    if override is not None:
        override_label = form.select_one('label[for="report-stop-override"]')
        block = ctx.html('<div class="v48-block" data-v48-override></div>')
        if override_label is not None:
            block.append(override_label.extract())
        block.append(override)
        fields.append(block)
    for node in take_all(form, "[data-report-missing-companion]"):
        fields.append(node)

    # Reviewed recipients: From, To and Cc as the Triage composer lays them out.
    legend = next((lbl for lbl in form.select(".lg") if lbl.get_text(strip=True) == "Reviewed recipients"), None)
    if legend is not None:
        legend = legend.extract()
    from_select = take(ctx, form, "select[data-report-from]", required=True)
    from_select["id"] = "report-from"
    from_lbl = label_before(form, from_select) if from_select.parent else None
    for lbl in form.select(".lbl"):
        if lbl.get_text(strip=True) in ("From", "To", "Cc"):
            lbl.decompose()
    to_stack = take(ctx, form, "#report-recipient-to", required=True)
    add_to = take(ctx, form, '[data-add-report-recipient="report-recipient-to"]', required=True)
    cc_stack = take(ctx, form, "#report-recipient-cc", required=True)
    add_cc = take(ctx, form, '[data-add-report-recipient="report-recipient-cc"]', required=True)
    for stack in (to_stack, cc_stack):
        for box in stack.select(":scope > input"):
            box.wrap(ctx.html('<div class="v48-recipient" data-v48-recipient></div>'))
        for wrapper in stack.select("[data-v48-recipient]"):
            wrapper.append(ctx.html(
                '<button type="button" class="btn btn--small btn--icon" data-v48-remove-recipient '
                f'aria-label="Remove recipient">{ICON.format(name="x")}</button>'))
    to_stack["data-v48-keep-one"] = ""
    ctx.record("O", "Every To or Cc box can be removed with its ×; the one remaining To box stays")
    datalist = take(ctx, form, "datalist#report-address-book")
    cc_hint = take(ctx, form, "[data-report-cc-hint]")
    addresses = ctx.html('<div class="mail-compose-addresses"></div>')
    addresses.append(field(ctx, "mail-compose-from", '<label for="report-from">From</label>', from_select))
    addresses.append(field(ctx, "mail-compose-to", '<label class="req">To</label>', to_stack, add_to))
    addresses.append(field(ctx, "mail-compose-cc", '<label>Cc</label>', cc_stack, add_cc))
    if cc_hint is not None:
        hint_box = ctx.html('<div class="field mail-compose-cc-hint"></div>')
        hint_box.append(cc_hint)
        addresses.append(hint_box)
    if legend is not None:
        fields.append(legend)
    fields.append(addresses)
    if datalist is not None:
        fields.append(datalist)

    # C: Subject, prefilled with the subject the send derives today, editable.
    subject = ctx.html(
        '<div class="field mail-compose-subject" data-v48-subject>'
        '<label class="req" for="report-subject">Subject</label>'
        f'<input id="report-subject" name="subject" value="{facts["subject"]}" required maxlength="500" />'
        '</div>')
    fields.append(subject)
    ctx.mark(subject, "C", "Subject is a field of the composer, prefilled with the subject the send derives today")

    # Message: the live textarea with its label.
    message = take(ctx, form, "#report-message", required=True)
    message_label = form.select_one('label[for="report-message"]')
    if message_label is not None:
        message_label.decompose()
    fields.append(field(ctx, "mail-compose-message", '<label class="req" for="report-message">Message</label>', message))

    # D/E: Files.
    files = build_files(ctx, form)
    fields.append(files)
    ctx.mark(files, "D", "Files: one row per attachment, the name opens it in the viewer, the live include tick, Rename")

    # The rules' blocks keep their live words: Questions, warnings, After sending, Holds.
    questions = take_all(form, "[data-report-question]")
    if questions:
        block = ctx.html('<div class="v48-block" data-v48-questions></div>')
        for lbl in form.select(".lg"):
            if lbl.get_text(strip=True) == "Answer before sending":
                block.append(lbl.extract())
        for question in questions:
            block.append(question)
        fields.append(block)
    for warning in take_all(form, "[data-report-warning]"):
        fields.append(warning)
    after = take(ctx, form, "[data-report-after-sending]")
    if after is not None:
        block = ctx.html('<div class="v48-block" data-v48-after-sending></div>')
        for lbl in form.select(".lbl"):
            if lbl.get_text(strip=True) == "After sending":
                block.append(lbl.extract())
        block.append(after)
        fields.append(block)
    holds = take_all(form, "[data-report-hold-row]")
    if holds:
        block = ctx.html('<div class="v48-block" data-v48-holds></div>')
        for hold in holds:
            block.append(hold)
        fields.append(block)

    # The foot: Cancel, then the live Send report (absent while a companion is missing).
    footer.append(ctx.html('<button type="button" class="btn" data-dialog-close>Cancel</button>'))
    submit = take(ctx, form, 'button[type="submit"]')
    if submit is not None:
        footer.append(submit)

    # Whatever the form still holds must be its hidden inputs only.
    leftover = [node for node in form.contents if isinstance(node, Tag)
                and not (node.name == "input" and node.get("type") == "hidden")]
    if leftover:
        raise Anchor(f"{ctx.key}: the send form kept nodes the dialog did not place: "
                     + ", ".join(f"<{node.name} {node.get('class', '')}>" for node in leftover))
    stray = form.get_text(strip=True)
    if stray:
        raise Anchor(f"{ctx.key}: the send form kept text the dialog did not place: {stray!r}")
    form.append(fields)
    form.append(footer)

    reference = facts.get("reference", "")
    backdrop = ctx.html(
        f'<div class="dialog-backdrop" data-dialog="{DIALOG_ID}" hidden>'
        f'<section class="dialog mail-compose-dialog dialog--send" role="dialog" aria-modal="true" '
        f'aria-labelledby="case-send-report-title" data-v48-send-dialog>'
        f'<header class="dialog-head"><div><p class="eyebrow">Report · {reference}</p>'
        f'<h2 id="case-send-report-title" tabindex="-1">Send report</h2></div>'
        f'<button type="button" class="dialog-close" data-dialog-close aria-label="Close dialog">{ICON.format(name="x")}</button>'
        f'</header><div class="dialog-body mail-compose-body"></div></section></div>')
    backdrop.select_one(".mail-compose-body").append(form)
    ctx.need("[data-case-dialogs]").append(backdrop)
    ctx.mark(backdrop.select_one("section.dialog"), "B", "The delivery form is a composer dialog in the Triage composer's shape, 880px wide")
    ctx.record("E", "Every attachment can be renamed: the stem is edited, .pdf stays, Reset restores the policy name")
    ctx.record("F", "A file's name opens it in the Case viewer over the dialog")
    ctx.style(CSS, "B")


# ---------------------------------------------------------------------------
# G/N: the Report section without the form
# ---------------------------------------------------------------------------

@patch(*READ_STATES)
def read_cells(ctx: Ctx) -> None:
    """G: reading, the greyed From / To / Cc / Attach / File name / Message cells go."""
    read = ctx.one("#section-report [data-send-report-read]")
    if read is None:
        raise Anchor(f"{ctx.key}: the greyed read cells are not in this capture")
    ctx.remove(read, "G", "The Report section keeps the preview card; the inline form and the greyed read cells go")
    ctx.mark(ctx.need("#section-report [data-report-preview-card]"), "G",
             "The Report section keeps the preview card; the inline form and the greyed read cells go")


@patch(*EDIT_STATES)
def already_sent_line(ctx: Ctx) -> None:
    """N: a report already sent says so under the preview card too (the dialog keeps its line)."""
    ctx.record("G", "The Report section keeps the preview card; the inline form and the greyed read cells go")
    line = ctx.one(f'[data-dialog="{DIALOG_ID}"] [data-report-already-sent]')
    if line is None:
        return
    card = ctx.need("#section-report [data-report-preview-card]")
    copy_line = ctx.html(f'<p class="muted" data-v48-already-sent>{line.get_text(" ", strip=True)}</p>')
    card.insert_after(copy_line)
    ctx.mark(copy_line, "N", "A report already sent says so under the preview card as well as in the dialog")
