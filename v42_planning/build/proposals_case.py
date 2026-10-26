"""Case Proposal patches: Correspondence, the Queries section, Next action and the Actions menu.

Letters are the v42 sign-off items (v42-notes.md §6). Every QDOS26214 state is the
same page, so each carries the whole Case Proposal; the Assign query dialog opens on
load only in case-queries-assign.
"""
from __future__ import annotations

import re

from bs4 import Tag

from proposals_v42 import Ctx, patch, presets

QDOS26214 = ("case", "case-queries", "case-queries-assign", "case-aside-query")
REMOVED = ("Pre-instruction", "Images received", "Case update", "Query", "Billing", "General",
           "Not client related", "Internal CC", "Unclassified")
VIEWER = "development-offline-administrator"
COLLEAGUES = ("e.mawdsley", "r.okafor")
ICON_SPARKLES = '<svg class="icon" aria-hidden="true"><use href="#icon-sparkles"></use></svg>'



@presets("case", "case-qdos26220")
def open_correspondence_tab(body: Tag, state: dict) -> None:
    body.insert(0, Ctx.html('<script>try{location.hash="#case-files-correspondence";}catch(e){}</script>'))


@presets("case-aside-query")
def open_actions_menu(body: Tag, state: dict) -> None:
    log_btn = body.select_one(".menu-body [data-log-query]")
    menu = log_btn.find_parent("details") if log_btn else None
    if menu is not None:
        menu["open"] = ""

def _case_id(ctx: Ctx) -> str:
    section = ctx.one("[data-case-id]")
    if section is not None:
        return section["data-case-id"]
    for form in ctx.all("form[action^='/Cases/']"):
        match = re.match(r"/Cases/([0-9a-f-]{36})", form["action"])
        if match:
            return match.group(1)
    return ""


def _correspondence_table(ctx: Ctx) -> Tag | None:
    for table in ctx.all("#section-files table"):
        heads = [th.get_text(" ", strip=True) for th in table.select("thead th")]
        if "Classification" in heads or "Type" in heads:
            return table
    return None


def _query_message_row(ctx: Ctx) -> Tag | None:
    table = _correspondence_table(ctx)
    if table is None:
        return None
    for row in table.select("tbody tr[data-correspondence-row]"):
        cells = row.find_all("td", recursive=False)
        if len(cells) > 2 and cells[2].get_text(" ", strip=True).startswith("Query —"):
            return row
    return None


# ---------------------------------------------------------------------------
# Correspondence (X, N)
# ---------------------------------------------------------------------------

@patch(*QDOS26214, "case-qdos26220")
def correspondence_type_column(ctx: Ctx) -> None:
    table = _correspondence_table(ctx)
    if table is None:
        return
    case_id = _case_id(ctx)
    summary = "Correspondence column Type: Correspondence or the e-mail's type, with its query chip."
    for th in table.select("thead th"):
        if th.get_text(" ", strip=True) == "Classification":
            th.string = "Type"
            ctx.mark(th, "X", summary)
    query_row = _query_message_row(ctx)
    for row in table.select("tbody tr[data-correspondence-row]"):
        cells = row.find_all("td", recursive=False)
        if len(cells) < 5:
            continue
        type_cell = cells[3]
        text = type_cell.get_text(" ", strip=True)
        if text in REMOVED:
            type_cell.clear()
            type_cell.append("Correspondence")
            ctx.mark(type_cell, "X", summary)
        if row is query_row:
            type_cell.append(" ")
            type_cell.append(Ctx.html('<span class="status status--purple">Query</span>'))
            ctx.mark(type_cell, "X", summary)
        tag = row.select_one("form[data-tag-as-query]")
        if tag is not None and ctx.key not in QDOS26214:
            # QDOS26220 is in Report preparation: a query opens only once the report is sent (AA).
            cell = tag.parent
            tag.decompose()
            ctx.mark(cell, "AA", "Open query is offered only once the Case's report is sent.")
        elif tag is not None:
            message = row["data-correspondence-row"]
            opener = Ctx.html(
                f'<form method="post" action="/Cases/{case_id}?handler=OpenQuery" class="inline-form" data-open-query="{message}">'
                f'<input type="hidden" name="retainedMessageId" value="{message}">'
                '<input type="hidden" name="section" value="files">'
                '<button class="btn btn--small" type="submit" data-busy-label="Saving…">Open query</button></form>')
            tag.replace_with(opener)
            ctx.mark(opener, "N", "Tag as query becomes Open query: one query per e-mail, opened through the one route.")


# ---------------------------------------------------------------------------
# Queries (D, K, M, O, J)
# ---------------------------------------------------------------------------

def _actions(case_id: str, query_id: str, *, open_: bool, assigned_to_viewer: bool = False) -> str:
    if not open_:
        return (f'<form method="post" action="/Cases/{case_id}?handler=ReopenQuery" data-reopen-query="{query_id}">'
                f'<input type="hidden" name="queryId" value="{query_id}">'
                '<button class="btn btn--small" type="submit" data-busy-label="Saving…">Reopen</button></form>')
    markup = (f'<form method="post" action="/Cases/{case_id}?handler=MarkQueryDone" data-mark-query-done="{query_id}">'
              f'<input type="hidden" name="queryId" value="{query_id}">'
              '<button class="btn btn--small" type="submit" data-busy-label="Saving…">Mark done</button></form>'
              f'<button class="btn btn--small" type="button" data-dialog-open="case-assign-query-dialog" data-assign-query="{query_id}">Assign</button>')
    if not assigned_to_viewer:
        markup += (f'<form method="post" action="/Cases/{case_id}?handler=AssignQuery" data-take-query="{query_id}">'
                   f'<input type="hidden" name="queryId" value="{query_id}">'
                   '<input type="hidden" name="assignee" value="d47fbbae-ea22-4ca6-b983-01e2ed1fbd13">'
                   '<button class="btn btn--small btn--primary" type="submit" data-busy-label="Assigning…">Take</button></form>')
    return markup


@patch(*QDOS26214)
def queries_section(ctx: Ctx) -> None:
    table = ctx.one("table[data-queries-table]")
    if table is None:
        return
    case_id = _case_id(ctx)
    head = table.select_one("thead tr")
    for th in head.find_all("th"):
        if th.get_text(" ", strip=True) == "Resolved":
            th.string = "Done"
            th.insert_before(Ctx.html("<th>Assigned to</th>"))
            ctx.mark(head, "D", "Assigned to column; a new query is Unassigned until taken or assigned.")
    body = table.select_one("tbody")
    for row in body.select("tr[data-case-query]"):
        cells = row.find_all("td", recursive=False)
        cells[5].insert_before(Ctx.html("<td>Unassigned</td>"))
        actions = row.select_one("td.row-actions")
        actions.clear()
        actions.append(Ctx.html(f'<span class="cluster">{_actions(case_id, row["data-case-query"], open_=True)}</span>'))
        ctx.mark(actions, "K", "Per-query Mark done replaces Resolve query (which closed every open query).")

    query_row = _query_message_row(ctx)
    if query_row is not None:
        message = query_row["data-correspondence-row"]
        dialog = f"case-message-{message.replace('-', '')}"
        mail_id = "00000000-0000-4000-8000-0000000c0e41"
        reply = f"/Inbox/{message}?compose=reply&amp;correspondenceCaseReference=QDOS26214&amp;markQueryDone=true"
        mail = Ctx.html(
            f'<tr data-case-query="{mail_id}" data-case-query-open="true">'
            '<td><span class="status status--purple">Query</span></td>'
            '<td><time datetime="2026-10-12T11:20:00.0000000+01:00">12 Oct 2026 11:20</time></td>'
            '<td>Automatic</td><td>E-mail</td>'
            '<td class="wrap"><span>claims@northline.example</span><br><span>Query — QDOS26214 — hire charges</span></td>'
            '<td>Unassigned</td><td>Not recorded</td>'
            '<td class="row-actions nowrap"><span class="cluster">'
            f'<a class="btn btn--small" href="/Inbox/{message}" data-dialog-open="{dialog}">Open message</a>'
            f'<a class="btn btn--small" href="{reply}" data-query-reply="{message}">Reply</a>'
            f'<form method="post" action="/Cases/{case_id}?handler=DraftQueryReply" data-query-ai-draft-start="{message}">'
            f'<button class="btn btn--small" type="submit" data-busy-label="Drafting…">{ICON_SPARKLES}<span>Draft reply with AI</span></button></form>'
            f'{_actions(case_id, mail_id, open_=True)}</span></td></tr>')
        body.insert(0, mail)
        ctx.mark(mail, "O", "Assign and Take on each open query; Take on an Unassigned row assigns the viewer.")
    done_id = "00000000-0000-4000-8000-0000000c0e40"
    done = Ctx.html(
        f'<tr data-case-query="{done_id}" data-case-query-open="false">'
        '<td><span class="status status--green">Done</span></td>'
        '<td><time datetime="2026-10-10T16:05:00.0000000+01:00">10 Oct 2026 16:05</time></td>'
        '<td>e.mawdsley</td><td>WhatsApp</td>'
        '<td class="wrap">Asked for a copy of the engineer\'s report</td>'
        '<td>e.mawdsley</td>'
        '<td><time datetime="2026-10-11T09:12:00.0000000+01:00">11 Oct 2026 09:12</time><br><span>e.mawdsley</span></td>'
        f'<td class="row-actions nowrap">{_actions(case_id, done_id, open_=False)}</td></tr>')
    body.append(done)
    ctx.mark(done, "M", "Reopen on a Done row: any staff role and Automation, no reason, while the Case is not archived or closed.")
    ctx.record("K", "Done replaces Resolved as the closed query's chip and column.")
    ctx.record("J", "Query acts need no edit session, expected version or reason.")
    ctx.style("[data-queries-table] td.row-actions{display:table-cell;height:auto}"
              "[data-queries-table] td.row-actions .cluster{justify-content:flex-end;gap:6px}",
              "K", "Per-query Mark done replaces Resolve query (which closed every open query).")


ASSIGN_DIALOG = """
<div class="dialog-backdrop" data-dialog="case-assign-query-dialog" id="case-assign-query-dialog" data-dialog-open-on-load="{open}" hidden>
  <section aria-labelledby="case-assign-query-dialog-title" aria-modal="true" class="dialog dialog--compact" role="dialog">
    <div class="dialog-head">
      <h2 id="case-assign-query-dialog-title" tabindex="-1">Assign query</h2>
      <button aria-label="Close dialog" class="dialog-close" data-dialog-close type="button"><svg aria-hidden="true" class="icon"><use href="#icon-x"></use></svg></button>
    </div>
    <form action="/Cases/{case}?handler=AssignQuery" method="post" data-assign-query-form>
      <input name="queryId" type="hidden" value="00000000-0000-4000-8000-0000000c0e41">
      <div class="dialog-body stack">
        <div class="field">
          <label for="case-assign-query-assignee">Assigned to</label>
          <select id="case-assign-query-assignee" name="assignee" data-dialog-initial-focus>
            <option value="d47fbbae-ea22-4ca6-b983-01e2ed1fbd13">{viewer} (you)</option>
            {colleagues}
            <option value="unassigned" selected>Unassigned</option>
          </select>
        </div>
      </div>
      <div class="dialog-foot">
        <button class="btn" data-dialog-close type="button">Cancel</button>
        <button class="btn btn--primary" data-busy-label="Assigning…" type="submit">Assign</button>
      </div>
    </form>
  </section>
</div>
"""


@patch(*QDOS26214)
def assign_query_dialog(ctx: Ctx) -> None:
    log_dialog = ctx.one("#case-log-query-dialog")
    if log_dialog is None:
        return
    colleagues = "".join(f'<option value="{name}">{name}</option>' for name in COLLEAGUES)
    dialog = Ctx.html(ASSIGN_DIALOG.replace("{open}", "true" if ctx.key == "case-queries-assign" else "false")
                      .replace("{case}", _case_id(ctx)).replace("{viewer}", VIEWER).replace("{colleagues}", colleagues))
    log_dialog.insert_after(dialog)
    ctx.mark(dialog.select_one("section.dialog"), "O",
             "Assign query dialog: Assigned to lists the viewer first, enabled casework staff, then Unassigned.")


# ---------------------------------------------------------------------------
# Next action and Actions menu (K, AA)
# ---------------------------------------------------------------------------

@patch(*QDOS26214)
def next_action_answer_query(ctx: Ctx) -> None:
    step = ctx.one("[data-next-resolve-query]")
    query_row = _query_message_row(ctx)
    if step is None or query_row is None:
        return
    message = query_row["data-correspondence-row"]
    step.clear()
    step.append(Ctx.html('<strong data-next-label>Answer query</strong>'))
    step.append(Ctx.html(
        f'<a class="btn next-step-go" href="/Inbox/{message}?compose=reply&amp;correspondenceCaseReference=QDOS26214&amp;markQueryDone=true" '
        'data-next-reply-query>Reply</a>'))
    ctx.mark(step, "K", "Next action Answer query: Reply when the oldest open query is an e-mail, Mark done when it was logged.")


@patch(*QDOS26214)
def actions_menu_without_resolve(ctx: Ctx) -> None:
    for form in ctx.all(".menu-body form[data-resolve-query-form]"):
        menu = form.parent
        form.decompose()
        ctx.mark(menu, "K", "Resolve query leaves the Actions menu; Log query stays.")
    chip = ctx.one(".ribbon-chips .status--purple")
    ctx.mark(chip, "AA", "Query stays the purple stage word while any query is open.")


@patch("case-qdos26220")
def cancellation_marker_stays(ctx: Ctx) -> None:
    for row in ctx.all(".next-row"):
        if "Cancellation received" in row.get_text(" ", strip=True):
            ctx.mark(row, "E", "The Cancellation type and its Case aside row stay.")
