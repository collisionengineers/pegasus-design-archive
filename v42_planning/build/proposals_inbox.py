"""Inbox Proposal patches: the list, No Case Found and the message dialog's Decision panel.

Letters are the v42 sign-off items (v42-notes.md §6): A, B and C are settled; G, H,
I, K, L, N and R are drawn here for sign-off.
"""
from __future__ import annotations

import re

from bs4 import Tag

from proposals_v42 import Ctx, patch, presets

KEPT = ("New instruction", "Triage request", "Cancellation")
CODES = {"Correspondence": "correspondence", "New instruction": "new-instruction",
         "Triage request": "triage-request", "Cancellation": "cancellation"}
REMOVED = ("Pre-instruction", "Images received", "Case update", "Query", "Billing", "General",
           "Not client related", "Internal CC", "Unclassified")
I_SUMMARY = "Category filter and bulk Correct classification (with its dialog) removed; bulk Dismiss and Restore stay."
MESSAGE_STATES = ("message-m1", "message-m2", "message-m3", "message-m4", "message-m4-ai-reply",
                  "message-m7", "message-m11", "message-m12")


# ---------------------------------------------------------------------------
# The list
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


@patch("inbox", "inbox-no-case-found", "inbox-rows-ticked")
def category_filter_removed(ctx: Ctx) -> None:
    select = ctx.one("select#queue-filter")
    if select is None:
        return
    form = select.find_parent("form")
    ctx.remove(select.find_parent("div", class_="field"), "I", I_SUMMARY)
    ctx.mark(form, "I", I_SUMMARY)


@patch("inbox", "inbox-no-case-found", "inbox-rows-ticked")
def bulk_classify_removed(ctx: Ctx) -> None:
    button = ctx.one("[data-bulk-classify]")
    bulk = ctx.one("form#mail-bulk")
    ctx.remove(button, "I", I_SUMMARY)
    ctx.remove(ctx.one("#bulkClassifyDialog"), "I", I_SUMMARY)
    ctx.mark(bulk, "I", I_SUMMARY)


@patch("inbox", "inbox-no-case-found", "inbox-rows-ticked")
def row_category_text(ctx: Ctx) -> None:
    for row in ctx.all("div.inbox-row"):
        meta = _row_category(row)
        if meta is not None and meta.get_text(" ", strip=True) in REMOVED:
            cluster = meta.parent
            meta.decompose()
            ctx.mark(cluster, "A", "Row category text only for New instruction, Triage request and Cancellation.")


@patch("inbox", "inbox-rows-ticked")
def unlinked_correspondence_leaves_all_incoming(ctx: Ctx) -> None:
    removed = 0
    for row in ctx.all("div.inbox-row"):
        meta = _row_category(row)
        category = meta.get_text(" ", strip=True) if meta is not None else ""
        if _unlinked(row) and category not in ("New instruction", "Triage request"):
            row.decompose()
            removed += 1
    if not removed:
        return
    summary = "Unlinked e-mail that is not an instruction or triage request waits only in No Case Found."
    ctx.record("B", summary)
    for form in ctx.all(".scope-list form"):
        if form.get_text(" ", strip=True).startswith("All incoming"):
            for node in form.find_all(string=re.compile(r"^\s*\d+\s*$")):
                node.replace_with(str(int(node.strip()) - removed))
                break
            ctx.mark(form, "B", summary)
    for meta in ctx.all("span.meta"):
        match = re.match(r"^\s*(\d+)\s+messages\s*$", meta.get_text(" ", strip=True))
        if match:
            meta.string = f"{int(match.group(1)) - removed} messages"
            ctx.mark(meta, "B", summary)


# ---------------------------------------------------------------------------
# The message dialog
# ---------------------------------------------------------------------------

def _message_id(ctx: Ctx) -> str:
    form = ctx.one("form#mailClassificationForm")
    match = re.search(r"/Inbox/([0-9a-f-]{36})", form.get("action", "")) if form else None
    return match.group(1) if match else ""


def _case_link(ctx: Ctx) -> Tag | None:
    for row in ctx.all("section.mail-decision .decision-row"):
        label = row.find("span")
        if label is not None and label.get_text(" ", strip=True) == "Case":
            return row
    return None


def _chip(label: str, pressed: bool) -> str:
    if pressed:
        return ('<button type="button" class="chip" aria-pressed="true">'
                '<svg class="icon" aria-hidden="true"><use href="#icon-check"></use></svg>'
                f'<span>{label}</span></button>')
    return (f'<button type="submit" class="chip" name="ClassificationKey" value="{CODES[label]}" '
            f'aria-pressed="false" data-busy-label="Saving…">{label}</button>')


# What each linked message's Query row offers (N, K, C): Case QDOS26214 is Report
# sent, so m2 and m12 offer Open query and m4 holds an open query. QDOS26220 is in
# Report preparation, so m11 has no Query row; m1, m3 and m7 have no Case.
QUERY_ROW = {
    "message-m2": "offer",
    "message-m12": "offer",
    "message-m4": "open",
    "message-m4-ai-reply": "open",
}
# Change case links (G): QDOS26220 offers Place on Hold and Close case in its
# Actions menu; QDOS26214 (Report sent) offers neither, so no row is drawn there.
CHANGE_CASE = {"message-m11": True}


@patch(*MESSAGE_STATES)
def decision_panel(ctx: Ctx) -> None:
    section = ctx.one("section.mail-decision")
    form = ctx.one("form#mailClassificationForm")
    if section is None or form is None:
        return
    facts = section.select_one(".decision-facts")

    # H, A: the Type row with four chips.
    pressed_now = form.select_one('button[aria-pressed="true"]')
    current = pressed_now.get_text(" ", strip=True) if pressed_now else "Unclassified"
    selected = current if current in KEPT else "Correspondence"
    if current in REMOVED:
        ctx.record("A", f"{current} removed: this e-mail is Case correspondence when linked, No Case Found when not.")
    label = form.select_one(".mail-decision-label")
    label.string = "Type"
    ctx.mark(label, "H", "Row label Type; default chip Correspondence replaces Unclassified.")
    chips = form.select_one(".mail-chips")
    chips.clear()
    for name in CODES:
        chips.append(Ctx.html(_chip(name, name == selected)))
    ctx.mark(chips, "H", "Row label Type; default chip Correspondence replaces Unclassified.")

    # G: Case first, then Type, Query and Change case.
    case_row = _case_link(ctx)
    picker = section.select_one(".mail-decision-block:not(form)")
    work_type = picker.select_one("[data-work-type-field]") if picker else None
    actions = section.select_one(".mail-decision-actions")
    if work_type is not None:
        chips.insert_after(work_type.extract())
    if picker is not None and not picker.select(".field"):
        picker.decompose()
        picker = None
    anchor = form
    for node in (case_row, picker, actions):
        if node is not None:
            anchor.insert_before(node.extract())
    ctx.mark(case_row, "G", "Decision order: Case, Type, Query, Change case.")

    case_href = case_row.select_one("a")["href"] if case_row and case_row.select_one("a") else None
    after = form
    kind = QUERY_ROW.get(ctx.key)
    if kind and case_href:
        message = _message_id(ctx)
        if kind == "open":
            body = ('<span class="status status--purple">Query</span><span class="muted">Unassigned</span>'
                    f'<form method="post" action="/Inbox/{message}?handler=MarkQueryDone">'
                    '<button class="btn btn--small" type="submit" data-busy-label="Saving…">Mark done</button></form>')
            change, summary = "K", "Query row: open query, Unassigned, Mark done marks this query done."
        else:
            body = (f'<form method="post" action="/Inbox/{message}?handler=OpenQuery">'
                    '<button class="btn btn--small" type="submit" data-busy-label="Saving…">Open query</button></form>')
            change, summary = "N", "Query row: Open query on an e-mail on a Report sent Case that holds no query."
        row = Ctx.html('<div class="mail-decision-block" data-mail-query>'
                       '<span class="mail-decision-label">Query</span>'
                       f'<div class="mail-decision-actions">{body}</div></div>')
        after.insert_after(row)
        after = row
        ctx.mark(row, change, summary)
        if kind == "offer":
            ctx.record("C", "Joining a Report sent Case opens no query by itself; criteria and the AI classifier may.")
    if CHANGE_CASE.get(ctx.key) and case_href:
        row = Ctx.html('<div class="mail-decision-block" data-mail-change-case>'
                       '<span class="mail-decision-label">Change case</span>'
                       '<div class="mail-decision-actions">'
                       f'<a class="btn btn--small" href="{case_href}?dialog=case-hold-dialog">Place on Hold</a>'
                       f'<a class="btn btn--small" href="{case_href}?dialog=case-close-dialog">Close case</a>'
                       '</div></div>')
        after.insert_after(row)
        ctx.mark(row, "G", "Change case: Place on Hold and Close case open the Case with that dialog.")
        ctx.record("E", "The Cancellation type stays, with its Case aside row and notification.")
    if facts is not None:
        ctx.mark(facts, "G", "Decision order: Case, Type, Query, Change case.")


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


@patch("message-m3")
def register_images_on_correspondence(ctx: Ctx) -> None:
    dismissal = ctx.one("form[data-message-dismissal]")
    foot = dismissal.find_parent("div", class_="dialog-foot") if dismissal else None
    if foot is None:
        return
    button = Ctx.html('<button class="btn btn--dark" type="button" data-offered-action="RegisterImages" '
                      'data-dialog-open="messageRegisterImagesDialog">'
                      '<svg class="icon" aria-hidden="true"><use href="#icon-image"></use></svg>'
                      '<span>Register images</span></button>')
    foot.append(button)
    ctx.mark(button, "R", "Register images on any image-only unlinked e-mail with no instruction, triage or cancellation type.")
    ctx.body.append(Ctx.html(REGISTER_IMAGES_DIALOG.replace("{id}", _message_id(ctx))))


@patch("message-m4-ai-reply")
def mark_query_done_tick(ctx: Ctx) -> None:
    tick = ctx.one("input[data-resolve-query]")
    label = tick.find_parent("label") if tick else None
    if label is None:
        return
    for node in list(label.strings):
        if node.strip() == "Also resolve query":
            node.replace_with(" Mark query done")
    ctx.mark(label, "L", "Composer tick Mark query done: marks only the replied e-mail's query done once the Sent item is observed.")
