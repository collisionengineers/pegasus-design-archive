"""K: the Case workspace.

K1 repairs the broken Tasks icon reference, K2 the Report delivery form (radio
labels and the hold's Done tick), K3 the open-task rows in Next action, K4 the
Tasks dialog, K5 the recipients a read-mode Report sent Case shows, K9 a With
Engineer Case that has no Engineer, K10 the Return to work dialog on a closed
Case. K6, K7 and K8 (the query as a view) were dropped by the operator on 15
October 2026: the Queries section stays as live. Every patch looks for its
element first; a capture that lacks it is left alone.
"""
from __future__ import annotations

import copy
from html import escape

from proposals_v41 import Ctx, patch

K9_STATE = "case-with-engineer-unassigned"
K10_STATE = "case-closed"

CASE_STATES = (
    "case-read", "case-edit", "case-not-ready",
    "case-delivery-rules", "case-delivery-plain", "case-delivery-stop", "case-delivery-missing",
    "case-report-sent", "case-audit", "case-tasks",
    K9_STATE, K10_STATE,
)
DELIVERY_STATES = CASE_STATES + ("case-correspondence",)

K1_SUMMARY = "The Tasks icon points at a symbol the sprite does not have, so it draws nothing. It now uses the symbol the sprite has, #icon-square-check."
K2_RADIO_SUMMARY = "The Yes and No answers on a rule question show their labels. The radios were stretched to the full width of the form and pushed the labels out of sight."
K2_HOLD_SUMMARY = "The Done tick for a hold sits on the same line as the hold, not on a line of its own beneath it."
K3_SUMMARY = "Each open task in Next action opens the Tasks dialog itself, so the repeated Tasks button on every row goes."
K4_INPUT_SUMMARY = "The add-task box takes the field style the other Case inputs use."
K4_ACTIONS_SUMMARY = "A task's Assign, Complete and Cancel task controls sit on one line."


@patch(*DELIVERY_STATES)
def k1_square_check_icon(ctx: Ctx) -> None:
    """Replace #icon-check-square with #icon-square-check on every svg <use>."""
    for use in ctx.all("use"):
        for attr in ("href", "xlink:href"):
            if use.get(attr) == "#icon-check-square":
                use[attr] = "#icon-square-check"
                ctx.mark(use.parent, "K1", K1_SUMMARY)


@patch(*DELIVERY_STATES)
def k2_report_delivery_form(ctx: Ctx) -> None:
    """Radios keep their size beside their label; the hold's Done tick joins the hold's line."""
    radios = ctx.all("#section-report .recip-form input[type=radio]")
    if radios:
        # The live rule `#section-report .recip-form input:not([type=checkbox])` gives every
        # non-checkbox input width:100%, padding and a border. Restore the checkbox sizing
        # (case-workspace.css: `.recip-form .choice input`) for radios.
        ctx.style(
            "#section-report .recip-form .choice input[type=radio]"
            "{width:15px;height:15px;min-height:0;padding:0;border:0;background:none}",
            "K2", K2_RADIO_SUMMARY)
        seen: set[int] = set()
        for radio in radios:
            group = radio.find_parent(attrs={"data-report-question": True}) or radio.find_parent("div")
            if group is not None and id(group) not in seen:
                seen.add(id(group))
                ctx.mark(group, "K2", K2_RADIO_SUMMARY)
    for row in ctx.all("#section-report .recip-form [data-report-hold-row]"):
        # A live .cluster is a row of items; the live .stack is a column.
        classes = [c for c in row.get("class", []) if c != "stack"]
        row["class"] = classes + ["cluster"]
        ctx.mark(row, "K2", K2_HOLD_SUMMARY)


@patch(*DELIVERY_STATES)
def k3_open_task_rows_open_the_dialog(ctx: Ctx) -> None:
    """The open-task row is the control; the per-row Tasks button goes."""
    converted = False
    for row in ctx.all("[data-open-tasks] li.blocker[data-open-task]"):
        button = row.select_one(".blocker-actions [data-dialog-open]")
        if button is None:
            continue
        row["data-dialog-open"] = button["data-dialog-open"]
        row["role"] = "button"
        row["tabindex"] = "0"
        actions = button.find_parent(class_="blocker-actions") or button
        ctx.remove(actions, "K3", K3_SUMMARY)
        ctx.mark(row, "K3", K3_SUMMARY)
        converted = True
    if converted:
        ctx.style("[data-open-tasks] .blocker[data-dialog-open]{cursor:pointer}", "K3", K3_SUMMARY)


@patch("case-tasks")
def k4_tasks_dialog(ctx: Ctx) -> None:
    """Add-task input takes .fi; row actions stay on one line."""
    dialog = ctx.one("#case-tasks-dialog")
    if dialog is None:
        return
    field = dialog.select_one("#case-task-description")
    if field is not None:
        field["class"] = field.get("class", []) + ["fi"]
        ctx.mark(field, "K4", K4_INPUT_SUMMARY)
        # .fi is drawn only inside .fc in the live sheet; carry its text metrics here.
        ctx.style(
            "#case-tasks-dialog .note-form input.fi{font-size:13.5px;line-height:1.4}",
            "K4", K4_INPUT_SUMMARY)
    containers = dialog.select("[data-case-tasks] td > .button-row")
    for container in containers:
        ctx.mark(container, "K4", K4_ACTIONS_SUMMARY)
    if containers:
        ctx.style(
            "#case-tasks-dialog [data-case-tasks] td .button-row{flex-wrap:nowrap}"
            "#case-tasks-dialog [data-case-tasks] td .button-row select{width:auto}"
            "#case-tasks-dialog [data-case-tasks] td .button-row .btn{white-space:nowrap}",
            "K4", K4_ACTIONS_SUMMARY)


# -- K5 ---------------------------------------------------------------------

K5 = ("Reading a Case whose report was sent, To shows the recipient of the report that was sent instead of Not recorded; "
      "Cc keeps Not recorded, because the send history is one joined list and names no Cc. The capture seeds that history with "
      "claims@northline.example, the sender of the instruction e-mail that the Sent item replies to, and read mode prints it "
      "nowhere today, so the address is read from the Case's own correspondence.")


def _column(table, heading: str) -> int | None:
    heads = [th.get_text(" ", strip=True) for th in table.select("thead th")]
    return heads.index(heading) if heading in heads else None


def _sent_report_recipient(ctx: Ctx) -> str | None:
    """The sender of the instruction e-mail the Sent item answers, read from the Case's own correspondence."""
    rows = ctx.all("tr[data-correspondence-row]")
    if not rows:
        return None
    table = rows[0].find_parent("table")
    sender, subject, kind = (_column(table, name) for name in ("Sender", "Subject", "Classification"))
    if None in (sender, subject, kind):
        return None

    def cells(row):
        return [td.get_text(" ", strip=True) for td in row.find_all("td")]

    parsed = [cells(row) for row in rows]
    for sent in parsed:
        if sent[kind] != "Sent" or not sent[subject].startswith("Re: "):
            continue
        original = sent[subject][len("Re: "):]
        for earlier in parsed:
            if earlier[kind] == "New instruction" and earlier[subject] == original and "@" in earlier[sender]:
                return earlier[sender]
    return None


@patch("case-report-sent")
def k5_read_mode_recipients(ctx: Ctx) -> None:
    form = ctx.one("#report-pane-report .recip-form[data-send-report-read]")
    if form is None:
        return
    address = _sent_report_recipient(ctx)
    if address is None:
        return
    for cell in form.select(":scope > .fc.ro"):
        label = cell.select_one(".lbl")
        value = cell.select_one(".fv")
        if label is None or value is None or label.get_text(strip=True) != "To":
            continue
        value.string = address
        value["class"] = [name for name in value.get("class", []) if name != "empty"]
        ctx.mark(cell, "K5", K5)


# -- K9 ---------------------------------------------------------------------

K9 = ("A With Engineer Case that has no Engineer reads Unassigned on the ribbon and in the Overview (the Overview's only Engineer fact is "
      "Sign-off Engineer, which is the fact drawn). Next action opens with Assign Engineer and Take beside it, the Actions menu lists "
      "Assign Engineer, and the Assign Engineer dialog lists the signed-in person first as Name (you), then the other Engineers, "
      "then Unassigned, with no Reason box.")


def _icon(name: str) -> str:
    return f'<svg class="icon" aria-hidden="true"><use href="#icon-{name}"></use></svg>'


def _ribbon_engineer(ctx: Ctx):
    for item in ctx.all(".ribbon-item"):
        label = item.select_one(".ribbon-label")
        if label is not None and label.get_text(strip=True) == "Engineer":
            return item.select_one(".ribbon-value span")
    return None


def _case_form_fields(ctx: Ctx):
    """The Case id and version that the ribbon's own forms post, which every K9 form repeats."""
    claim = ctx.one('.ribbon-actions form input[name="id"]')
    version = ctx.one('.ribbon-actions form input[name="expectedVersion"]')
    if claim is None or version is None:
        return None
    return claim["value"], version["value"]


def _viewer(ctx: Ctx) -> str | None:
    signed_in = ctx.one(".rail-user strong")
    return signed_in.get_text(strip=True) if signed_in is not None else None


# The viewer's staff id is in no Case capture (the viewer is integration-user, and a Case page lists no staff ids), so the
# viewer's name stands in for it: it is the value K9's dialog gives its Name (you) option, and Take is that same choice.
# The patches run in this order because the dialog reads the Engineer that the ribbon patch, last, overwrites.
@patch(K9_STATE)
def k9_assign_engineer_dialog(ctx: Ctx) -> None:
    """The Assign Engineer dialog (not captured on a With Engineer Case; drawn from the live Razor): "(you)" first,
    the other Engineers, then Unassigned; the Engineer select is its only field."""
    value = _ribbon_engineer(ctx)
    fields = _case_form_fields(ctx)
    me = _viewer(ctx)
    if value is None or fields is None or me is None:
        return
    case_id, case_version = fields
    previous = value.get_text(strip=True)
    choices = [(me, me + " (you)")] + [(name, name) for name in (previous,) if name and name != me] + [("unassigned", "Unassigned")]
    options = '<option value=""></option>' + "".join(
        f'<option value="{escape(value)}">{escape(label)}</option>' for value, label in choices)
    dialog = ctx.html(
        '<div id="case-handoff-dialog" class="dialog-backdrop" data-dialog="case-handoff-dialog" hidden>'
        '<section class="dialog" role="dialog" aria-modal="true" aria-labelledby="case-handoff-dialog-title">'
        '<div class="dialog-head"><h2 id="case-handoff-dialog-title" tabindex="-1">Assign Engineer</h2>'
        f'<button type="button" class="dialog-close" data-dialog-close aria-label="Close dialog">{_icon("x")}</button></div>'
        '<div class="dialog-body stack">'
        f'<form method="post" action="/Cases/{case_id}/Workflow?handler=AssignEngineer" class="stack" id="case-handoff-form">'
        f'<input type="hidden" name="id" value="{case_id}"/>'
        f'<input type="hidden" name="expectedVersion" value="{case_version}"/>'
        '<div class="field"><label class="req" for="case-handoff-engineer">Engineer</label>'
        f'<select id="case-handoff-engineer" name="engineerId" required data-dialog-initial-focus>{options}</select></div>'
        '</form></div>'
        '<div class="dialog-foot"><button type="submit" form="case-handoff-form" class="btn btn--primary">Assign Engineer</button></div>'
        '</section></div>')
    anchor = ctx.one('[data-dialog="case-return-review-dialog"]')
    if anchor is not None:
        anchor.insert_before(dialog)
    else:
        ctx.body.append(dialog)
    ctx.mark(dialog, "K9", K9)


@patch(K9_STATE)
def k9_next_action_assign_and_take(ctx: Ctx) -> None:
    """Next action: Assign Engineer first, Take beside it (the live Assign Engineer step is a dialog button)."""
    step = ctx.one("[data-next-action] [data-next-step]")
    fields = _case_form_fields(ctx)
    me = _viewer(ctx)
    if step is None or fields is None or me is None:
        return
    case_id, case_version = fields
    row = ctx.html(
        '<div class="next-step" data-next-step>'
        '<div class="next-row" data-next-assign>'
        '<button type="button" class="btn next-step-go" data-dialog-open="case-handoff-dialog" '
        'data-next-assign-engineer>Assign Engineer</button>'
        f'<form method="post" action="/Cases/{case_id}/Workflow?handler=AssignEngineer" data-case-take>'
        f'<input type="hidden" name="id" value="{case_id}"/>'
        f'<input type="hidden" name="expectedVersion" value="{case_version}"/>'
        f'<input type="hidden" name="engineerId" value="{escape(me)}"/>'
        '<button type="submit" class="btn btn--primary btn--small">Take</button>'
        '</form></div></div>')
    step.replace_with(row)
    ctx.mark(row, "K9", K9)
    # Assign Engineer takes the row's room; Take keeps its own width beside it.
    ctx.style("[data-next-assign] .next-step-go{flex:1 1 auto;width:auto}[data-next-assign] form{flex:none;margin:0}", "K9", K9)


@patch(K9_STATE)
def k9_actions_menu_assign_engineer(ctx: Ctx) -> None:
    """The Actions menu lists Assign Engineer first, as it does in Review."""
    menu = ctx.one("[data-case-actions] .menu-body")
    if menu is None:
        return
    item = ctx.html(
        '<button type="button" class="btn" data-dialog-open="case-handoff-dialog">'
        f'{_icon("arrow-right")}<span>Assign Engineer</span></button>')
    menu.insert(0, item)
    ctx.mark(item, "K9", K9)


@patch(K9_STATE)
def k9_overview_unassigned(ctx: Ctx) -> None:
    sign_off = ctx.one('.fc[data-field="signOffEngineerId"] .fv')
    if sign_off is not None:
        sign_off.string = "Unassigned"
        ctx.mark(sign_off, "K9", K9)


@patch(K9_STATE)
def k9_ribbon_unassigned(ctx: Ctx) -> None:
    value = _ribbon_engineer(ctx)
    if value is not None:
        value.string = "Unassigned"
        ctx.mark(value, "K9", K9)


# -- K10 --------------------------------------------------------------------

K10 = ("A closed Case offers Return to work in the Actions menu. Its dialog posts the Closure page's Reopen handler with the "
       "stage to return to and a reason; the stage options read the existing stage names. Question: the stage field's label "
       "is given by no ruling and no live label, so it reads Case stage, the word W2 gives the Search State filter.")

K10_STAGES = (
    ("NotReady", "Not ready"),
    ("Review", "Review"),
    ("ReportPreparation", "With Engineer"),
    ("ReportSent", "Report sent"),
)


K10_DIALOG = "case-return-to-work-dialog"


@patch(K10_STATE)
def k10_return_to_work_dialog(ctx: Ctx) -> None:
    archive = ctx.one('[data-dialog="case-archive-dialog"]')
    if archive is None:
        return
    dialog_id = K10_DIALOG

    # The dialog is the Archive dialog's frame (title, one Reason for action box, Cancel and Confirm Action),
    # posting the Closure page's Reopen handler, with the stage to return to above the reason.
    dialog = copy.copy(archive)
    for element in [dialog] + dialog.find_all(True):
        for attribute, value in list(element.attrs.items()):
            if isinstance(value, str) and "case-archive-dialog" in value:
                element[attribute] = value.replace("case-archive-dialog", dialog_id)
    dialog["hidden"] = ""
    dialog.select_one("h2").string = "Return to work"
    form = dialog.select_one("form")
    form["action"] = form["action"].replace("handler=Archive", "handler=Reopen")
    reason = dialog.select_one(".dialog-body .field")
    options = '<option value=""></option>' + "".join(
        f'<option value="{value}">{escape(label)}</option>' for value, label in K10_STAGES)
    # "Case stage" is W2's accepted label for the Search State filter; no live label names this field (the K10 question).
    field = ctx.html(
        '<div class="field">'
        f'<label class="req" for="{dialog_id}_destination">Case stage</label>'
        f'<select id="{dialog_id}_destination" name="destination" required>{options}</select></div>')
    reason.insert_before(field)
    archive.insert_before(dialog)
    ctx.mark(dialog, "K10", K10)


@patch(K10_STATE)
def k10_return_to_work_menu_item(ctx: Ctx) -> None:
    archive_item = ctx.one('[data-case-actions] [data-dialog-open="case-archive-dialog"]')
    if archive_item is None:
        return
    item = ctx.html(
        f'<button class="btn" data-dialog-open="{K10_DIALOG}" type="button">'
        f'{_icon("chevron-left")}<span>Return to work</span></button>')
    archive_item.insert_before(item)
    ctx.mark(item, "K10", K10)
