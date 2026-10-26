"""Inbox Proposal patches: the list, No Case Found and #mailMessageDialog's cog settings menu.

Letters are the v42 sign-off items (v42-notes.md §6): A, B and C are settled; G, H,
I, K, L, N and R are drawn here for sign-off.

In the live application (v41 Stage 2), clicking an e-mail on /Inbox opens
#mailMessageDialog (_MessageDialog.cshtml) over the list. In Today, #mailMessageDialog
carries a 380px right-hand Decision column alongside the message body. In the v42
Proposal (G, H), that right-hand Decision column is replaced by a cog settings menu
(#icon-settings, [data-mail-settings]) in the dialog header's tool bar, paired with
an at-a-glance context pill bar (.mail-context-bar) beneath the From/To route line so
the message body reads at full width.
"""
from __future__ import annotations

import html as html_mod
import re

from bs4 import Tag

from mail_dialogs import FIXTURES
from proposals_v42 import Ctx, patch, presets

KEPT = ("New instruction", "Triage request", "Cancellation")
CODES = {
    "Correspondence": "correspondence",
    "New instruction": "new-instruction",
    "Triage request": "triage-request",
    "Cancellation": "cancellation",
}
REMOVED = (
    "Pre-instruction", "Images received", "Case update", "Query", "Billing",
    "General", "Not client related", "Internal CC", "Unclassified",
)
I_SUMMARY = "Category filter and bulk Correct classification (with its dialog) removed; bulk Dismiss and Restore stay."
G_SUMMARY = (
    "Decision sidebar replaced by the cog settings menu (#icon-settings) in the dialog header, "
    "ordered Case, Type, Query, Change case, with an at-a-glance context bar above the full-width message."
)
H_SUMMARY = "Row label Type; default chip Correspondence replaces Unclassified."
MESSAGE_STATES = (
    "message-m1", "message-m2", "message-m3", "message-m4", "message-m4-ai-reply",
    "message-m7", "message-m11", "message-m12",
)
ALL_INBOX_STATES = ("inbox", "inbox-no-case-found", "inbox-rows-ticked") + MESSAGE_STATES
INCOMING_SCOPE_STATES = (
    "inbox", "inbox-rows-ticked",
    "message-m1", "message-m2", "message-m4", "message-m4-ai-reply", "message-m11", "message-m12",
)

# What each linked message's Query row offers (N, K, C): Case QDOS26214 is Report
# sent, so m2 and m12 offer Open query and m4 holds an open query. QDOS26220 is in
# Report preparation, so m11 has no Query row; m1, m3, m5, m7..m10 have no Case.
QUERY_ROW_BY_KEY = {
    "m2": "offer",
    "m12": "offer",
    "m4": "open",
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


# ---------------------------------------------------------------------------
# The Inbox list
# ---------------------------------------------------------------------------

def _row_category(row: Tag) -> Tag | None:
    return row.select_one(".cluster > .row-meta")


def _unlinked(row: Tag) -> bool:
    chip = row.select_one(".cluster > .status")
    return chip is not None and chip.get_text(" ", strip=True) == "No Case Found"


@presets("inbox-rows-ticked")
def tick_two_rows(body: Tag, state: dict) -> None:
    """Two linked rows ticked (m2 and m4), so the bulk bar shows its count and buttons."""
    for row in body.select("div.inbox-row"):
        title = row.select_one("a.row-title")
        if title and title.get_text(" ", strip=True).startswith(("Update — QDOS26214", "Query — QDOS26214")):
            tick = row.select_one("input[data-mail-tick]")
            if tick is not None:
                tick["checked"] = ""


@patch(*ALL_INBOX_STATES)
def category_filter_removed(ctx: Ctx) -> None:
    select = ctx.one("select#queue-filter")
    if select is None:
        return
    form = select.find_parent("form")
    ctx.remove(select.find_parent("div", class_="field"), "I", I_SUMMARY)
    ctx.mark(form, "I", I_SUMMARY)


@patch(*ALL_INBOX_STATES)
def bulk_classify_removed(ctx: Ctx) -> None:
    button = ctx.one("[data-bulk-classify]")
    bulk = ctx.one("form#mail-bulk")
    ctx.remove(button, "I", I_SUMMARY)
    ctx.remove(ctx.one("#bulkClassifyDialog"), "I", I_SUMMARY)
    ctx.mark(bulk, "I", I_SUMMARY)


@patch(*ALL_INBOX_STATES)
def row_category_and_case_badges(ctx: Ctx) -> None:
    for row in ctx.all("div.inbox-row"):
        cluster = row.select_one(".cluster")
        meta = _row_category(row)
        cat_text = meta.get_text(" ", strip=True) if meta is not None else ""
        if meta is not None and cat_text in REMOVED:
            meta.decompose()
            ctx.mark(cluster, "A", "Row category text only for New instruction, Triage request and Cancellation.")
        # On linked rows, surface the Case reference pill and any open Query chip right in the cluster.
        status_chip = cluster.select_one(".status") if cluster else None
        if status_chip is not None and status_chip.get_text(" ", strip=True) == "Case created":
            right_case_link = row.select_one(".row-top:last-of-type > .row-meta > a[href^='/Cases/']")
            if right_case_link is not None:
                case_href = right_case_link["href"]
                case_ref = right_case_link.get_text(" ", strip=True)
                case_pill = Ctx.html(f'<a class="mail-row-case" href="{case_href}">{html_mod.escape(case_ref)}</a>')
                status_chip.replace_with(case_pill)
                # Keep only attachment count on the right if present.
                right_meta = right_case_link.parent
                full_right = right_meta.get_text(" ", strip=True)
                if "·" in full_right:
                    right_meta.clear()
                    right_meta.append(full_right.split("·", 1)[1].strip())
                else:
                    right_meta.decompose()
        title_link = row.select_one("a.row-title[data-mail-open]")
        if cluster is not None and title_link and title_link.get_text(" ", strip=True).startswith("Query — QDOS26214"):
            if cluster.select_one(".status--purple") is None:
                cluster.append(Ctx.html('<span class="status status--purple">Query</span>'))


@patch(*ALL_INBOX_STATES)
def unlinked_correspondence_leaves_all_incoming(ctx: Ctx) -> None:
    summary = "Unlinked e-mail that is not an instruction or triage request waits only in No Case Found."
    removed = 0
    if ctx.key in INCOMING_SCOPE_STATES:
        for row in ctx.all("div.inbox-row"):
            meta = _row_category(row)
            category = meta.get_text(" ", strip=True) if meta is not None else ""
            if _unlinked(row) and category not in ("New instruction", "Triage request"):
                row.decompose()
                removed += 1
        for meta in ctx.all("span.meta"):
            match = re.match(r"^\s*(\d+)\s+messages\s*$", meta.get_text(" ", strip=True))
            if match:
                meta.string = f"{int(match.group(1)) - removed} messages"
                ctx.mark(meta, "B", summary)
    ctx.record("B", summary)
    for form in ctx.all(".scope-list form"):
        if form.get_text(" ", strip=True).startswith("All incoming"):
            for node in form.find_all(string=re.compile(r"^\s*\d+\s*$")):
                node.replace_with("5")
                break
            ctx.mark(form, "B", summary)


# ---------------------------------------------------------------------------
# The message dialog (#mailMessageDialog): replace Decision column with cog menu
# ---------------------------------------------------------------------------

def _chip(label: str, pressed: bool) -> str:
    if pressed:
        return (
            '<button type="button" class="chip" aria-pressed="true">'
            '<svg class="icon" aria-hidden="true"><use href="#icon-check"></use></svg>'
            f'<span>{label}</span></button>'
        )
    return (
        f'<button type="submit" class="chip" name="ClassificationKey" value="{CODES[label]}" '
        f'aria-pressed="false" data-busy-label="Saving…">{label}</button>'
    )


def _build_context_bar(key: str, selected_type: str, case_ref: str | None, case_href: str | None, query_kind: str | None) -> Tag:
    pills: list[str] = []
    if case_ref and case_href:
        pills.append(
            f'<a class="mail-pill mail-pill--case" href="{case_href}" data-context-case>'
            '<svg class="icon" aria-hidden="true"><use href="#icon-folder-open"></use></svg>'
            f'<span>Case</span><strong>{html_mod.escape(case_ref)}</strong></a>'
        )
    else:
        pills.append('<span class="status status--amber" data-context-case>No Case Found</span>')
        pills.append(
            '<button type="button" class="mail-pill mail-pill--action" data-open-settings-case>'
            '<svg class="icon" aria-hidden="true"><use href="#icon-link"></use></svg>'
            '<span>Link to Case</span></button>'
        )
    pills.append(
        '<button type="button" class="mail-pill" data-open-settings-type title="Change type in Message settings">'
        f'<span>Type</span><strong data-context-type>{html_mod.escape(selected_type)}</strong></button>'
    )
    if query_kind == "open":
        pills.append('<span class="status status--purple" data-context-query>Query · Unassigned</span>')
    elif query_kind == "offer":
        pills.append(
            '<button type="button" class="mail-pill mail-pill--action" data-quick-open-query>'
            '<svg class="icon" aria-hidden="true"><use href="#icon-flag"></use></svg>'
            '<span>Open query</span></button>'
        )
    return Ctx.html(f'<div class="mail-context-bar" data-mail-context-bar>{"".join(pills)}</div>')


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

    # If this is a composer dialog (e.g. message-m4-ai-reply), update the query checkbox label (L).
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
        pressed_now = form.select_one('button[aria-pressed="true"]')
        current = pressed_now.get_text(" ", strip=True) if pressed_now else fx["category"]
        selected = current if current in KEPT else "Correspondence"
        if current in REMOVED and ctx is not None:
            ctx.record("A", f"{current} removed: this e-mail is Case correspondence when linked, No Case Found when not.")

        label = form.select_one(".mail-decision-label")
        label.string = "Type"
        chips = form.select_one(".mail-chips")
        chips.clear()
        for name in CODES:
            chips.append(Ctx.html(_chip(name, name == selected)))

        case_row = None
        decided_row = None
        for row in section.select(".decision-row"):
            sp = row.find("span")
            txt = sp.get_text(" ", strip=True) if sp else ""
            if txt == "Case":
                case_row = row
            elif txt == "Decided":
                decided_row = row

        picker_block = section.select_one(".mail-decision-block:not(form)")
        work_type = picker_block.select_one("[data-work-type-field]") if picker_block else None
        actions_row = section.select_one(".mail-decision-actions")
        if work_type is not None:
            chips.insert_after(work_type.extract())
        if picker_block is not None:
            hint = picker_block.select_one(".field-hint")
            inp = picker_block.select_one("input#mailLinkCaseReference")
            if inp is not None:
                inp["placeholder"] = "Search Case / PO, VRM, claimant…"
            if hint is not None:
                hint.decompose()
            if not picker_block.select(".field"):
                picker_block.decompose()
                picker_block = None

        # Build the cog settings menu (<details class="menu mail-settings-menu" data-menu data-mail-settings>)
        open_attr = " open" if settings_open else ""
        menu = Ctx.html(
            f'<details class="menu mail-settings-menu" data-menu data-mail-settings{open_attr}>'
            '<summary class="icon-button mail-settings-trigger" data-mail-settings-toggle '
            'aria-label="Message settings" title="Message settings">'
            '<svg class="icon" aria-hidden="true"><use href="#icon-settings"></use></svg>'
            '</summary>'
            '<div class="mail-settings-popover" data-mail-settings-popover>'
            '<div class="mail-settings-head"><span>Message settings</span></div>'
            '<div class="decision-facts"></div>'
            '</div></details>'
        )
        facts = menu.select_one(".decision-facts")
        for node in (case_row, picker_block, actions_row):
            if node is not None:
                facts.append(node.extract())
        facts.append(form.extract())

        case_link_a = case_row.select_one("a") if case_row else None
        case_href = case_link_a["href"] if case_link_a else (f"/Cases/{fx['case_id']}" if fx.get("case_id") else None)
        case_ref = case_link_a.get_text(" ", strip=True) if case_link_a else fx.get("case_ref")

        query_kind = QUERY_ROW_BY_KEY.get(key)
        if query_kind and case_href:
            if query_kind == "open":
                q_body = (
                    '<span class="status status--purple">Query</span><span class="muted">Unassigned</span>'
                    f'<form method="post" action="/Inbox/{msg_id}?handler=MarkQueryDone">'
                    '<button class="btn btn--small" type="submit" data-busy-label="Saving…">Mark done</button></form>'
                )
                q_change, q_summary = "K", "Query row in Message settings: open query, Unassigned, Mark done marks this query done."
            else:
                q_body = (
                    f'<form method="post" action="/Inbox/{msg_id}?handler=OpenQuery">'
                    '<button class="btn btn--small" type="submit" data-busy-label="Saving…">Open query</button></form>'
                )
                q_change, q_summary = "N", "Query row in Message settings: Open query on an e-mail on a Report sent Case that holds no query."
            q_row = Ctx.html(
                '<div class="mail-decision-block" data-mail-query>'
                '<span class="mail-decision-label">Query</span>'
                f'<div class="mail-decision-actions">{q_body}</div></div>'
            )
            facts.append(q_row)
            if ctx is not None:
                ctx.mark(q_row, q_change, q_summary)
                if query_kind == "offer":
                    ctx.record("C", "Joining a Report sent Case opens no query by itself; criteria and the AI classifier may.")

        if CHANGE_CASE_BY_KEY.get(key) and case_href:
            cc_row = Ctx.html(
                '<div class="mail-decision-block" data-mail-change-case>'
                '<span class="mail-decision-label">Change case</span>'
                '<div class="mail-decision-actions">'
                f'<a class="btn btn--small" href="{case_href}?dialog=case-hold-dialog">Place on Hold</a>'
                f'<a class="btn btn--small" href="{case_href}?dialog=case-close-dialog">Close case</a>'
                '</div></div>'
            )
            facts.append(cc_row)
            if ctx is not None:
                ctx.mark(cc_row, "G", "Change case in Message settings: Place on Hold and Close case open the Case with that dialog.")
                ctx.record("E", "The Cancellation type stays, with its Case aside row and notification.")

        if decided_row is not None:
            decided_row["class"] = ["decision-row", "mail-settings-decided"]
            facts.append(decided_row.extract())

        # Remove the entire right-hand <aside class="stack"> (Decision + Corrections cards)
        aside = section.find_parent("aside")
        if aside is not None:
            aside.decompose()
        else:
            section.decompose()

        # Mount the cog menu at the start of .mail-dialog-tools in .dialog-head
        tools = dialog.select_one(".mail-dialog-tools")
        if tools is not None:
            tools.insert(0, menu)

        # Add the at-a-glance context bar (.mail-context-bar) beneath .mail-route in .mail-dialog-title
        title_box = dialog.select_one(".mail-dialog-title")
        if title_box is not None and title_box.select_one("[data-mail-context-bar]") is None:
            cbar = _build_context_bar(key, selected, case_ref, case_href, query_kind)
            title_box.append(cbar)
            if ctx is not None:
                ctx.mark(cbar, "G", G_SUMMARY)

        # Add inline attachment chips under .mail-body when attachments exist
        mail_read = dialog.select_one(".mail-read")
        if mail_read is not None and mail_read.select_one("[data-mail-inline-attachments]") is None:
            att_strip = _build_inline_attachments(key, msg_id)
            if att_strip is not None:
                mail_read.append(att_strip)

        if ctx is not None:
            ctx.mark(menu.select_one(".mail-settings-trigger"), "G", G_SUMMARY)
            ctx.mark(case_row, "G", G_SUMMARY)
            ctx.mark(label, "H", H_SUMMARY)
            ctx.mark(chips, "H", H_SUMMARY)

    # R: Register images offered on unlinked image-only Correspondence (m3 and m5).
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
    transform_dialog_to_proposal(
        mount,
        base_key,
        settings_open=bool(ctx.state.get("settings_open")),
        ctx=ctx,
    )
