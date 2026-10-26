"""Inbox Proposal patches: full-width structured Inbox ledger, native .tabs scope bar
(All, No Case Found, Dismissed), Principal & Mailbox filters, and #mailMessageDialog's
streamlined cog settings menu.

Uses ONLY Pegasus's exact operator labels (Case, Type, Subject, Sender, Received,
None, Correspondence, New instruction, Triage request, Cancellation, Inspection,
Audit, Inspection and Audit, Open query, Mark done, Place on Hold, Close case).
"""
from __future__ import annotations

import html as html_mod

from bs4 import Tag

from mail_dialogs import EMAIL_TYPE_OPTIONS, FIXTURES, load_ids
from proposals_v42 import Ctx, patch, presets

KEPT = ("New instruction", "Triage request", "Cancellation")
REMOVED = (
    "Pre-instruction", "Images received", "Case update", "Query", "Billing",
    "General", "Not client related", "Internal CC", "Unclassified",
)
I_SUMMARY = (
    "Inbox scopes simplified to All, No Case Found and Dismissed (Sent Items and Deleted Items "
    "removed); Category select and bulk Correct classification replaced by Principal and Mailbox "
    "filters over a full-width ledger with columns Case, Type, Subject, Sender and Received."
)
G_SUMMARY = (
    "Decision sidebar replaced by the cog settings menu (#icon-settings) in the dialog header, "
    "ordered Case, Type, Query, Change case, with a quiet context line above the full-width message."
)
H_SUMMARY = (
    "Clicky category chip cloud replaced by a single streamlined Type select combining "
    "Correspondence, New instruction (Inspection / Audit / Inspection and Audit), Triage request and Cancellation."
)
MESSAGE_STATES = (
    "message-m1", "message-m2", "message-m3", "message-m4", "message-m4-ai-reply",
    "message-m7", "message-m11", "message-m12",
)
ALL_INBOX_STATES = ("inbox", "inbox-no-case-found", "inbox-dismissed", "inbox-rows-ticked") + MESSAGE_STATES

SCOPE_KEYS: dict[str, list[str]] = {
    "all": ["m1", "m13", "m2", "m14", "m11", "m12", "m4", "m15"],
    "no_case_found": ["m1", "m13", "m7", "m8", "m9", "m10", "m3", "m5"],
    "dismissed": ["m16", "m17"],
}

CHANGE_CASE_BY_KEY = {"m11": True}

REGISTER_IMAGES_DIALOG = """
<div id="messageRegisterImagesDialog" class="dialog-backdrop" role="dialog" aria-modal="true"
     aria-labelledby="messageRegisterImagesDialog_title" data-dialog="messageRegisterImagesDialog" hidden>
  <section class="dialog">
    <div class="dialog-head"><h2 id="messageRegisterImagesDialog_title" tabindex="-1">Register images</h2></div>
    <form method="post" action="/Inbox/{id}?handler=RegisterImages">
      <div class="dialog-body stack">
        <div class="field"><label class="req" for="messageRegisterVrm">Vehicle registration</label>
          <input id="messageRegisterVrm" class="mono" name="vehicleRegistration" maxlength="20" required data-dialog-initial-focus></div>
        <div class="field"><label class="req" for="messageRegisterReason">Reason</label>
          <textarea id="messageRegisterReason" name="reason" maxlength="500" rows="3" required></textarea></div>
      </div>
      <div class="dialog-foot">
        <button type="button" class="btn" data-dialog-close>Cancel</button>
        <button type="submit" class="btn btn--dark" data-busy-label="Registering…">Register images</button>
      </div>
    </form>
  </section>
</div>
"""


def _active_scope(state_key: str) -> str:
    if state_key in ("inbox-no-case-found", "message-m3", "message-m7"):
        return "no_case_found"
    if state_key == "inbox-dismissed":
        return "dismissed"
    return "all"


def _build_ledger_row(key: str, msg_id: str, scope: str, *, ticked: bool = False) -> str:
    fx = FIXTURES[key]
    unread_cls = " unread" if fx["unread"] else ""
    checked_attr = ' checked="checked"' if ticked else ""
    unread_dot = (
        '<span class="unread-indicator" aria-hidden="true"></span><span class="sr-only">Unread</span>'
        if fx["unread"] else ""
    )
    principal = fx["principal"] or ""
    mailbox = fx["mailbox"]

    # Cell 2: Case (exact Pegasus label: Case reference link when linked, quiet "None" when unlinked)
    if fx["case_ref"] and fx["case_id"]:
        sub = f'<small class="inbox-cell-sub">{html_mod.escape(fx["vehicle"])}</small>' if fx.get("vehicle") else ""
        case_cell = (
            f'<div class="inbox-cell-case">'
            f'<a class="mail-row-case" href="/Cases/{fx["case_id"]}">{html_mod.escape(fx["case_ref"])}</a>'
            f'{sub}</div>'
        )
    else:
        sub = f'<small class="inbox-cell-sub">{html_mod.escape(fx["vehicle"])}</small>' if fx.get("vehicle") else ""
        case_cell = (
            f'<div class="inbox-cell-case">'
            f'<span class="quiet">None</span>'
            f'{sub}</div>'
        )

    # Cell 3: Type (only exact Pegasus labels: New instruction + Case type, Triage request, Cancellation, Correspondence, Query)
    if fx.get("query_state") == "open":
        assignee = fx.get("query_assignee") or "Unassigned"
        type_cell = (
            f'<div class="inbox-cell-type cluster">'
            f'<span class="status status--purple" data-row-query>Query</span>'
            f'<small class="inbox-cell-sub">{html_mod.escape(assignee)}</small></div>'
        )
    elif fx["short_type"] == "New instruction":
        sub = html_mod.escape(fx.get("work_type_sub") or "Inspection")
        type_cell = (
            f'<div class="inbox-cell-type cluster">'
            f'<span class="status status--navy">New instruction</span>'
            f'<span class="row-meta" hidden>New instruction</span>'
            f'<small class="inbox-cell-sub">{sub}</small></div>'
        )
    elif fx["short_type"] == "Triage request":
        type_cell = (
            '<div class="inbox-cell-type cluster">'
            '<span class="status status--amber">Triage request</span>'
            '<span class="row-meta" hidden>Triage request</span></div>'
        )
    elif fx["short_type"] == "Cancellation":
        type_cell = (
            '<div class="inbox-cell-type cluster">'
            '<span class="status status--neutral">Cancellation</span>'
            '<span class="row-meta" hidden>Cancellation</span></div>'
        )
    else:
        type_cell = (
            '<div class="inbox-cell-type cluster">'
            '<span class="inbox-type-correspondence">Correspondence</span></div>'
        )

    # Cell 4: Subject & excerpt
    att_count = len(fx["attachments"])
    att_pill = (
        f'<span class="mail-att-pill" title="{att_count} attachment(s)">'
        f'<svg class="icon" aria-hidden="true"><use href="#icon-file"></use></svg>'
        f'<span>{att_count}</span></span>'
        if att_count > 0 else ""
    )
    msg_cell = (
        f'<div class="inbox-cell-message">'
        f'<div class="inbox-subject-line">'
        f'<a class="row-title" data-mail-open href="/Inbox/{msg_id}">{html_mod.escape(fx["subject"])}</a>'
        f'{att_pill}'
        f'</div>'
        f'<span class="row-excerpt">{html_mod.escape(fx["excerpt"])}</span>'
        f'</div>'
    )

    # Cell 5: Sender
    principal_line = (
        f'<span class="inbox-principal-text" data-principal-badge>{html_mod.escape(principal)}</span>'
        if principal else ""
    )
    sender_cell = (
        f'<div class="inbox-cell-sender">'
        f'<span class="inbox-sender-addr">{html_mod.escape(fx["sender"])}</span>'
        f'{principal_line}</div>'
    )

    # Cell 6: Received
    time_cell = (
        f'<div class="inbox-cell-time">'
        f'<time datetime="{fx["iso"]}">{fx["date"]}</time>'
        f'<small class="tabular">{fx["clock"]}</small></div>'
    )

    # Cell 7: Actions
    is_dismissed = scope == "dismissed"
    act_handler = "Restore" if is_dismissed else "Dismiss"
    act_icon = "icon-undo" if is_dismissed else "icon-x"
    act_busy = "Restoring…" if is_dismissed else "Dismissing…"
    reply_btn = (
        f'<a class="icon-button" href="/Inbox/{msg_id}?compose=reply" data-mail-row-reply data-mail-open '
        f'title="Reply" aria-label="Reply {html_mod.escape(fx["subject"])}">'
        f'<svg class="icon" aria-hidden="true"><use href="#icon-reply"></use></svg></a>'
        if fx["sender"] != "Sender not recorded" and not is_dismissed else ""
    )
    actions_cell = (
        f'<div class="inbox-row-actions">'
        f'{reply_btn}'
        f'<form action="/Inbox?handler={act_handler}" method="post" class="inbox-row-action" '
        f'data-mail-row-action="{act_handler.lower()}">'
        f'<input type="hidden" name="id" value="{msg_id}">'
        f'<button type="submit" class="icon-button" data-busy-label="{act_busy}" '
        f'title="{act_handler}" aria-label="{act_handler} {html_mod.escape(fx["subject"])}">'
        f'<svg class="icon" aria-hidden="true"><use href="#{act_icon}"></use></svg></button>'
        f'</form></div>'
    )

    return (
        f'<div class="row-button inbox-row inbox-ledger-row{unread_cls}" '
        f'data-mail-row="{msg_id}" data-mail-key="{key}" '
        f'data-principal="{html_mod.escape(principal)}" data-mailbox="{html_mod.escape(mailbox)}">'
        f'<label class="inbox-row-tick">'
        f'<input type="checkbox" form="mail-bulk" name="ids" value="{msg_id}" '
        f'aria-label="{html_mod.escape(fx["subject"])}" data-mail-tick{checked_attr}>'
        f'{unread_dot}</label>'
        f'{case_cell}{type_cell}{msg_cell}{sender_cell}{time_cell}{actions_cell}'
        f'</div>'
    )


@presets("inbox-rows-ticked")
def tick_two_rows(body: Tag, state: dict) -> None:
    """Two linked rows ticked (m2 and m4) in Today's list."""
    for row in body.select("div.inbox-row"):
        title = row.select_one("a.row-title")
        if title and title.get_text(" ", strip=True).startswith(("Update — QDOS26214", "Query — QDOS26214")):
            tick = row.select_one("input[data-mail-tick]")
            if tick is not None:
                tick["checked"] = ""


@patch(*ALL_INBOX_STATES)
def inbox_workspace_overhaul(ctx: Ctx) -> None:
    """Transform /Inbox into a full-width ledger with native .tabs (All, No Case Found, Dismissed) and Principal/Mailbox filters."""
    ids = load_ids()
    scope = _active_scope(ctx.key)
    keys = SCOPE_KEYS[scope]
    is_dismissed = scope == "dismissed"
    ticked_keys = {"m2", "m4"} if ctx.key == "inbox-rows-ticked" else set()

    ctx.remove(ctx.one("#bulkClassifyDialog"), "I", I_SUMMARY)

    layout = ctx.one("section.inbox-layout")
    if layout is None:
        return
    layout["class"] = ["pane-layout", "inbox-layout", "inbox-layout--v42"]

    aside = layout.select_one("aside.pane")
    if aside is not None:
        aside.decompose()

    pane = layout.select_one("div.pane")
    if pane is None:
        return

    all_cnt = len(SCOPE_KEYS["all"])
    ncf_cnt = len(SCOPE_KEYS["no_case_found"])
    dis_cnt = len(SCOPE_KEYS["dismissed"])

    # Native Pegasus .tabs bar for the 3 scopes (All, No Case Found, Dismissed)
    scope_tabs = Ctx.html(
        '<nav class="tabs scope-list" data-mail-scopes aria-label="Inbox">'
        f'<button type="button" class="tab" data-scope-switch="all" '
        f'aria-selected="{"true" if scope == "all" else "false"}" '
        f'{"aria-current=\"page\"" if scope == "all" else ""}>'
        f'All <span class="tab-count tabular" data-scope-count="all">{all_cnt}</span></button>'
        f'<button type="button" class="tab" data-scope-switch="no_case_found" '
        f'aria-selected="{"true" if scope == "no_case_found" else "false"}" '
        f'{"aria-current=\"page\"" if scope == "no_case_found" else ""}>'
        f'No Case Found <span class="tab-count tabular" data-scope-count="no_case_found">{ncf_cnt}</span></button>'
        f'<button type="button" class="tab" data-scope-switch="dismissed" '
        f'aria-selected="{"true" if scope == "dismissed" else "false"}" '
        f'{"aria-current=\"page\"" if scope == "dismissed" else ""}>'
        f'Dismissed <span class="tab-count tabular" data-scope-count="dismissed">{dis_cnt}</span></button>'
        '</nav>'
    )

    toolbar = Ctx.html(
        '<div class="inbox-toolbar" data-inbox-command-top>'
        '<form method="get" class="inbox-filter" data-auto-submit aria-label="Mail view">'
        '<div class="inbox-search-box">'
        '<svg class="icon" aria-hidden="true"><use href="#icon-search"></use></svg>'
        '<input id="mail-search" type="search" name="search" maxlength="200" '
        'placeholder="Subject, sender, reference">'
        '</div>'
        '<select id="principal-filter" name="principal" class="inbox-compact-select" aria-label="Principal" data-principal-filter>'
        '<option value="">All principals</option>'
        '<option value="QDOS">QDOS</option>'
        '<option value="Northline">Northline</option>'
        '<option value="Meridian">Meridian</option>'
        '<option value="Connexus">Connexus</option>'
        '</select>'
        '<select id="mailbox-filter" name="mailbox" class="inbox-compact-select" aria-label="Mailbox" data-mailbox-filter>'
        '<option value="">All Mailboxes</option>'
        '<option value="desk@collisionengineers.co.uk">desk@collisionengineers.co.uk</option>'
        '<option value="instructions@collisionengineers.co.uk">instructions@collisionengineers.co.uk</option>'
        '</select>'
        '<div class="inbox-toolbar-meta">'
        f'<span class="meta tabular" data-inbox-count>{len(keys)} messages</span>'
        '<a class="btn btn--small sort-toggle" href="/Inbox?sort=oldest" '
        'aria-label="Received order: newest first; activate for oldest first">Received ↓</a>'
        '</div>'
        '</form>'
        '</div>'
    )

    bulk_hidden = "" if ticked_keys else " hidden"
    bulk_btn = (
        '<button type="submit" class="btn btn--small" formaction="/Inbox?handler=BulkRestore" formnovalidate data-busy-label="Restoring…">'
        '<svg class="icon" aria-hidden="true"><use href="#icon-undo"></use></svg><span>Restore</span></button>'
        if is_dismissed else
        '<button type="submit" class="btn btn--small" formaction="/Inbox?handler=BulkDismiss" formnovalidate data-busy-label="Dismissing…">'
        '<svg class="icon" aria-hidden="true"><use href="#icon-x"></use></svg><span>Dismiss</span></button>'
    )
    bulk_bar = Ctx.html(
        f'<form id="mail-bulk" method="post" class="inbox-bulk"{bulk_hidden}>'
        '<input type="hidden" name="operationKey" value="e58d0fa34c7b4226aef8552887b03865">'
        '<span class="inbox-bulk-count tabular" data-bulk-count>'
        f'{len(ticked_keys)}</span>'
        f'{bulk_btn}'
        '</form>'
    )

    # Exact Pegasus table header words: Case, Type, Subject, Sender, Received
    ledger_head = Ctx.html(
        '<div class="inbox-ledger-head" aria-hidden="true">'
        '<span></span>'
        '<span>Case</span>'
        '<span>Type</span>'
        '<span>Subject</span>'
        '<span>Sender</span>'
        '<span>Received</span>'
        '<span></span>'
        '</div>'
    )

    rows_html = "".join(
        _build_ledger_row(k, ids[k], scope, ticked=(k in ticked_keys))
        for k in keys
    )
    scroll_body = Ctx.html(
        f'<div class="pane-body pane-scroll" tabindex="0">'
        f'<div data-row-list>{rows_html}</div>'
        f'</div>'
    )

    pane.clear()
    pane.append(scope_tabs)
    pane.append(toolbar)
    pane.append(bulk_bar)
    pane.append(ledger_head)
    pane.append(scroll_body)

    ctx.mark(scope_tabs, "I", I_SUMMARY)
    ctx.mark(toolbar, "I", I_SUMMARY)
    if ticked_keys:
        ctx.mark(bulk_bar, "I", I_SUMMARY)
    ctx.record("A", "Three categories (New instruction, Triage request, Cancellation); everything else is Case correspondence or No Case Found.")
    ctx.record("B", "Unlinked e-mail that is not an instruction or triage request waits only in No Case Found.")


# ---------------------------------------------------------------------------
# The message dialog (#mailMessageDialog): calm header + streamlined cog menu
# ---------------------------------------------------------------------------

def _build_context_bar(key: str, fx: dict, case_ref: str | None, case_href: str | None, query_kind: str | None) -> Tag:
    """Quiet one-line metadata strip under From/To/Time using exact Pegasus labels."""
    parts: list[str] = []
    if case_ref and case_href:
        parts.append(
            f'<span data-context-case>Case <a class="mail-context-case-link" href="{case_href}">'
            f'{html_mod.escape(case_ref)}</a></span>'
        )
    else:
        parts.append(
            '<span data-context-case>Case <span class="quiet">None</span> · '
            '<button type="button" class="mail-context-inline-link" data-open-settings-case>Link to Case</button></span>'
        )
    parts.append(
        f'<span>Type <strong data-context-type>{html_mod.escape(fx["type_label"])}</strong></span>'
    )
    if query_kind == "open":
        assignee = fx.get("query_assignee") or "Unassigned"
        parts.append(f'<span class="status status--purple" data-context-query>Query · {html_mod.escape(assignee)}</span>')
    joined = '<span class="mail-context-sep">·</span>'.join(parts)
    return Ctx.html(f'<div class="mail-context-bar" data-mail-context-bar>{joined}</div>')


def _build_inline_attachments(key: str, msg_id: str) -> Tag | None:
    fx = FIXTURES.get(key)
    if not fx or not fx["attachments"]:
        return None
    chips = []
    for fname, mime, size, _outcome in fx["attachments"]:
        icon = "icon-image" if mime.startswith("image/") else "icon-file-text"
        chips.append(
            f'<a class="mail-attachment-chip" href="/Inbox/{msg_id}?section=attachments" data-mail-dialog-link>'
            f'<svg class="icon" aria-hidden="true"><use href="#{icon}"></use></svg>'
            f'<span>{html_mod.escape(fname)}</span><small>{size}</small></a>'
        )
    return Ctx.html(f'<div class="mail-inline-attachments" data-mail-inline-attachments>{"".join(chips)}</div>')


def transform_dialog_to_proposal(
    dialog_wrapper: Tag,
    key: str,
    *,
    settings_open: bool = False,
    ctx: Ctx | None = None,
) -> Tag:
    """Replace the right-hand Decision column in #mailMessageDialog with the cog settings menu."""
    dialog = dialog_wrapper.select_one("#mailMessageDialog")
    if dialog is None:
        return dialog_wrapper
    msg_id = dialog.get("data-mail-message", "")
    fx = FIXTURES.get(key, FIXTURES["m2"])

    tick = dialog.select_one("input[data-resolve-query]")
    if tick is not None:
        lbl = tick.find_parent("label")
        if lbl is not None:
            for node in list(lbl.strings):
                if node.strip() == "Also resolve query":
                    node.replace_with(" Mark query done")
            if ctx is not None:
                ctx.mark(lbl, "L", "Composer tick Mark query done: marks only the replied e-mail's query done once the Sent item is observed.")

    section = dialog.select_one("section.mail-decision")
    form = dialog.select_one("form#mailClassificationForm")
    if section is not None and form is not None:
        current = fx["category"]
        if current in REMOVED and ctx is not None:
            ctx.record("A", f"{current} removed: this e-mail is Case correspondence when linked, No Case Found when not.")

        case_link_a = section.select_one(".decision-row a[href^='/Cases/']")
        case_href = case_link_a["href"] if case_link_a else (f"/Cases/{fx['case_id']}" if fx.get("case_id") else None)
        case_ref = case_link_a.get_text(" ", strip=True) if case_link_a else fx.get("case_ref")

        if case_ref and case_href:
            case_head_right = (
                f'<strong><a class="mail-row-case" href="{case_href}">{html_mod.escape(case_ref)}</a>'
                f' · <button type="button" class="mail-settings-link" data-dialog-open="unlinkCaseDialog">Unlink</button></strong>'
            )
            picker_form = "changeLinkedCaseForm"
        else:
            case_head_right = '<strong class="quiet">None</strong>'
            picker_form = "linkCaseForm"

        case_section = Ctx.html(
            '<div class="mail-settings-section">'
            f'<div class="decision-row mail-settings-row-head"><span>Case</span>{case_head_right}</div>'
            f'<div class="field case-picker" data-case-picker data-case-picker-fill '
            f'data-case-picker-url="/Inbox/{msg_id}?handler=LinkCaseOptions">'
            '<label class="mail-decision-label" for="mailLinkCaseReference">Case / PO</label>'
            f'<input id="mailLinkCaseReference" name="caseReference" form="{picker_form}" type="text" '
            'maxlength="100" autocomplete="off" role="combobox" '
            'aria-autocomplete="list" aria-expanded="false" aria-controls="mailLinkCaseOptions">'
            '<div id="mailLinkCaseOptions" class="case-picker-options" data-case-picker-options hidden></div>'
            '</div></div>'
        )

        # 2. Type section (H): ONE streamlined <select> labelled "Type"
        type_options_html = "".join(
            f'<option value="{val}"{" selected" if val == fx["type_value"] else ""}>{html_mod.escape(opt_label)}</option>'
            for val, opt_label, _short in EMAIL_TYPE_OPTIONS
        )
        new_type_form = Ctx.html(
            f'<form method="post" id="mailClassificationForm" class="mail-settings-section" '
            f'action="/Inbox/{msg_id}?handler=CorrectClassification">'
            '<label class="mail-decision-label" id="mailClassificationLabel" for="mailTypeSelect">Type</label>'
            f'<select id="mailTypeSelect" name="ClassificationKey" class="mail-type-select" '
            f'aria-labelledby="mailClassificationLabel" data-mail-type-select>'
            f'{type_options_html}</select>'
            '</form>'
        )

        open_attr = " open" if settings_open else ""
        menu = Ctx.html(
            f'<details class="menu mail-settings-menu" data-menu data-mail-settings{open_attr}>'
            '<summary class="icon-button mail-settings-trigger" data-mail-settings-toggle '
            'aria-label="Decision" title="Decision">'
            '<svg class="icon" aria-hidden="true"><use href="#icon-settings"></use></svg>'
            '</summary>'
            '<div class="mail-settings-popover" data-mail-settings-popover>'
            '<div class="decision-facts"></div>'
            '</div></details>'
        )
        facts = menu.select_one(".decision-facts")
        facts.append(case_section)
        facts.append(new_type_form)

        query_kind = fx.get("query_state")
        if query_kind and case_href:
            if query_kind == "open":
                assignee = fx.get("query_assignee") or "Unassigned"
                q_row = Ctx.html(
                    '<div class="mail-settings-list" data-mail-query>'
                    f'<form method="post" action="/Inbox/{msg_id}?handler=MarkQueryDone">'
                    '<button class="mail-settings-item" type="submit" data-busy-label="Saving…">'
                    '<span class="mail-settings-item-left"><svg class="icon" aria-hidden="true"><use href="#icon-check-circle"></use></svg>'
                    '<span>Mark done</span></span>'
                    f'<span class="status status--purple">Query · {html_mod.escape(assignee)}</span>'
                    '</button></form></div>'
                )
                q_change, q_summary = "K", "Query action in settings menu: Mark done closes this e-mail's open query."
            else:
                q_row = Ctx.html(
                    '<div class="mail-settings-list" data-mail-query>'
                    f'<form method="post" action="/Inbox/{msg_id}?handler=OpenQuery">'
                    '<button class="mail-settings-item" type="submit" data-busy-label="Saving…">'
                    '<span class="mail-settings-item-left"><svg class="icon" aria-hidden="true"><use href="#icon-flag"></use></svg>'
                    '<span>Open query</span></span>'
                    f'<small class="muted">{html_mod.escape(case_ref)}</small>'
                    '</button></form></div>'
                )
                q_change, q_summary = "N", "Query action in settings menu: Open query on an e-mail on a Report sent Case that holds no query."
            facts.append(q_row)
            if ctx is not None:
                ctx.mark(q_row, q_change, q_summary)
                if query_kind == "offer":
                    ctx.record("C", "Joining a Report sent Case opens no query by itself; criteria and the AI classifier may.")

        if CHANGE_CASE_BY_KEY.get(key) and case_href:
            cc_row = Ctx.html(
                '<div class="mail-settings-list" data-mail-change-case>'
                f'<a class="mail-settings-item" href="{case_href}?dialog=case-hold-dialog">'
                '<span class="mail-settings-item-left"><svg class="icon" aria-hidden="true"><use href="#icon-pause"></use></svg>'
                '<span>Place on Hold</span></span></a>'
                f'<a class="mail-settings-item" href="{case_href}?dialog=case-close-dialog">'
                '<span class="mail-settings-item-left"><svg class="icon" aria-hidden="true"><use href="#icon-archive"></use></svg>'
                '<span>Close case</span></span></a>'
                '</div>'
            )
            facts.append(cc_row)
            if ctx is not None:
                ctx.mark(cc_row, "G", "Change case in settings menu: Place on Hold and Close case open the Case with that dialog.")
                ctx.record("E", "The Cancellation type stays, with its Case aside row and notification.")

        facts.append(Ctx.html(
            f'<div class="mail-settings-foot"><span>Decided</span>'
            f'<span><time datetime="{fx["iso"]}">{fx["decided"]}</time> · Automatic</span></div>'
        ))

        aside = section.find_parent("aside")
        if aside is not None:
            aside.decompose()
        else:
            section.decompose()

        tools = dialog.select_one(".mail-dialog-tools")
        if tools is not None:
            tools.insert(0, menu)

        title_box = dialog.select_one(".mail-dialog-title")
        if title_box is not None and title_box.select_one("[data-mail-context-bar]") is None:
            cbar = _build_context_bar(key, fx, case_ref, case_href, query_kind)
            title_box.append(cbar)

        mail_read = dialog.select_one(".mail-read")
        if mail_read is not None and mail_read.select_one("[data-mail-inline-attachments]") is None:
            att_strip = _build_inline_attachments(key, msg_id)
            if att_strip is not None:
                mail_read.append(att_strip)

        if ctx is not None:
            ctx.mark(menu.select_one(".mail-settings-trigger"), "G", G_SUMMARY)
            ctx.mark(case_section, "G", G_SUMMARY)
            ctx.mark(new_type_form, "H", H_SUMMARY)

    if key in ("m3", "m5"):
        foot = dialog.select_one(".dialog-foot")
        if foot is not None and foot.select_one('[data-offered-action="RegisterImages"]') is None:
            button = Ctx.html(
                '<button class="btn btn--dark" type="button" data-offered-action="RegisterImages" '
                'data-dialog-open="messageRegisterImagesDialog">'
                '<svg class="icon" aria-hidden="true"><use href="#icon-image"></use></svg>'
                '<span>Register images</span></button>'
            )
            foot.append(button)
            if ctx is not None:
                ctx.mark(button, "R", "Register images on any image-only unlinked e-mail with no instruction, triage or cancellation type.")
        if dialog_wrapper.select_one("#messageRegisterImagesDialog") is None:
            dialog_wrapper.append(Ctx.html(REGISTER_IMAGES_DIALOG.replace("{id}", msg_id)))

    return dialog_wrapper


@patch(*MESSAGE_STATES)
def message_dialog_proposal(ctx: Ctx) -> None:
    dialog_key = ctx.state.get("dialog", "")
    base_key = "m4" if dialog_key.startswith("m4") else dialog_key.replace("message-", "")
    mount = ctx.one("[data-mail-dialog-root]")
    if mount is None:
        return
    ids = load_ids()
    msg_id = ids.get(base_key, "")
    for row in ctx.all("[data-mail-row]"):
        if row.get("data-mail-row") == msg_id:
            row["aria-current"] = "true"
        else:
            row.attrs.pop("aria-current", None)
    transform_dialog_to_proposal(
        mount,
        base_key,
        settings_open=bool(ctx.state.get("settings_open")),
        ctx=ctx,
    )
