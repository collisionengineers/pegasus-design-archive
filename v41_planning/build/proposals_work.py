"""W: Work Centre and Search.

Every value a patch draws (engineer names, Principal codes, Type, Due) comes from the
same captured page. Where a capture lacks one, the live "Not recorded" stands. The one exception is the
viewer's staff id on Take, which is read from the shell lane's work-centre-assign capture (see _shell_staff_ids).
"""
from __future__ import annotations

import copy
import functools
import pathlib
import re
from datetime import datetime
from html import escape

from bs4 import BeautifulSoup, NavigableString, Tag
from bs4.element import TemplateString

from proposals_v41 import Ctx, patch

SHELL_ASSIGN_CAPTURE = pathlib.Path(__file__).resolve().parent.parent / "captured-live" / "shell" / "work-centre-assign.html"

WORK_CENTRE_STATES = (
    "work-centre", "work-centre-selected", "work-centre-assign", "work-centre-mine",
    "work-centre-new-cases", "work-centre-ai-jobs",
)
SEARCH_STATES = ("search", "search-filters")

W1 = "The Work Centre scope switch takes the shared control height and the ledger table header takes the 11px table header."
W2 = "Search: Engineer and Principal are selects, and State is relabelled Case stage."
W3 = "Search: results gain Type and Due columns, the preview gains Copy Case/PO, and its Our ref label reads Claim reference."


@patch(*WORK_CENTRE_STATES)
def w1_shared_control_and_header(ctx: Ctx) -> None:
    switch = ctx.one(".wc-switch")
    ledgers = ctx.all(".wc-ledger-table")
    css = []
    if switch is not None:
        css.append(".work-centre .wc-switch{box-sizing:border-box;height:var(--control)}"
                   ".work-centre .wc-switch a{height:100%}")
    if ledgers:
        css.append(".work-centre .wc-ledger-table th{font-size:11px}")
    if not css:
        return
    ctx.style("".join(css), "W1", W1)
    ctx.mark(switch, "W1", W1)
    for ledger in ledgers:
        ctx.mark(ledger.select_one("thead"), "W1", W1)


def _select(ctx: Ctx, field_id: str, name: str, blank: str, values: list[str], current: str) -> Tag:
    if current and current not in values:
        values = [current] + values
    options = [f'<option value="">{escape(blank)}</option>']
    for value in values:
        picked = " selected" if value == current else ""
        options.append(f'<option value="{escape(value)}"{picked}>{escape(value)}</option>')
    return ctx.html(f'<select id="{field_id}" name="{name}">{"".join(options)}</select>')


def _text(element: Tag) -> str:
    """Text including <template> content, which get_text() skips by default."""
    return element.get_text(" ", strip=True, types=(NavigableString, TemplateString))


def _fact(canvas: Tag, label: str) -> str | None:
    for fact in canvas.select("dl.fact"):
        dt, dd = fact.select_one("dt"), fact.select_one("dd")
        if dt is not None and dd is not None and _text(dt) == label:
            return _text(dd)
    return None


@patch(*SEARCH_STATES)
def w2_search_selects_and_case_stage(ctx: Ctx) -> None:
    state_label = ctx.one('label[for="search-state"]')
    if state_label is not None and state_label.get_text(strip=True) == "State":
        state_label.string = "Case stage"
        ctx.mark(state_label, "W2", W2)

    principal = ctx.one("input#search-principal")
    if principal is not None:
        codes: list[str] = []
        for row in ctx.all(".case-search-layout table tbody tr"):
            cells = row.find_all("td", recursive=False)
            if len(cells) > 3:
                code = cells[3].get_text(strip=True)
                if code and code not in codes:
                    codes.append(code)
        select = _select(ctx, "search-principal", "principal", "All principals", sorted(codes),
                         principal.get("value", ""))
        principal.replace_with(select)
        ctx.mark(select, "W2", W2)

    engineer = ctx.one("input#search-engineer")
    if engineer is not None:
        names: list[str] = []
        rail_user = ctx.one(".rail-user strong")
        if rail_user is not None:
            names.append(rail_user.get_text(strip=True))
        for canvas in ctx.all(".detail-canvas"):
            name = _fact(canvas, "Engineer")
            if name and name != "Unassigned" and name not in names:
                names.append(name)
        select = _select(ctx, "search-engineer", "engineerId", "All engineers", sorted(names),
                         engineer.get("value", ""))
        engineer.replace_with(select)
        ctx.mark(select, "W2", W2)


@patch(*SEARCH_STATES)
def w3_search_results_and_preview(ctx: Ctx) -> None:
    # Results gain Type (before State) and Due (after State), read from each row's own preview.
    table = ctx.one(".case-search-layout .table-wrap table")
    if table is not None:
        heads = table.select("thead th")
        state_head = next((th for th in heads if th.get_text(strip=True) == "State"), None)
        if state_head is not None:
            index = heads.index(state_head)
            type_head = ctx.html('<th scope="col">Type</th>')
            due_head = ctx.html('<th scope="col">Due</th>')
            state_head.insert_before(type_head)
            state_head.insert_after(due_head)
            ctx.mark(type_head, "W3", W3)
            ctx.mark(due_head, "W3", W3)
            for row in table.select("tbody tr"):
                cells = row.find_all("td", recursive=False)
                if len(cells) <= index:
                    continue
                canvas = row.select_one("template .detail-canvas")
                eyebrow = canvas.select_one(".eyebrow") if canvas is not None else None
                kind = _text(eyebrow) if eyebrow is not None else "Not recorded"
                due = (_fact(canvas, "Due") if canvas is not None else None) or "Not recorded"
                type_cell = ctx.html(f"<td>{escape(kind)}</td>")
                due_cell = ctx.html(f"<td>{escape(due)}</td>")
                cells[index].insert_before(type_cell)
                cells[index].insert_after(due_cell)
                ctx.mark(type_cell, "W3", W3)
                ctx.mark(due_cell, "W3", W3)

    # Preview (the selected Case and every row's template): Claim reference label, Copy Case/PO.
    for canvas in ctx.all(".detail-canvas"):
        for dt in canvas.select("dl.fact dt"):
            if _text(dt) == "Our ref":
                dt.string = "Claim reference"
                ctx.mark(dt, "W3", W3)
        heading = canvas.select_one("h2")
        actions = canvas.select_one(".button-row")
        if heading is None or actions is None or canvas.select_one("[data-copy-target]") is not None:
            continue
        text = _text(heading)
        case_po, _, rest = text.partition(" · ")
        if not case_po:
            continue
        heading.clear()
        heading.append(ctx.html(f'<span id="selected-case-po">{escape(case_po)}</span>'))
        if rest:
            heading.append(NavigableString(f" · {rest}"))
        button = ctx.html('<button type="button" class="btn" data-copy-target="selected-case-po">Copy Case/PO</button>')
        actions.append(button)
        ctx.mark(button, "W3", W3)


# -- W5, W6 -----------------------------------------------------------------

W5 = "Row actions are quiet buttons and the dismiss × loses its box; only the opened row's action stays dark, so the table is no longer a column of black buttons."
W6 = "Activity figures are set at table size, so the panel takes half the height."


@patch(*WORK_CENTRE_STATES)
def w5_quiet_row_actions(ctx: Ctx) -> None:
    changed = False
    for button in ctx.all("td.wc-col-action .btn--dark"):
        button["class"] = [name for name in button.get("class", []) if name != "btn--dark"]
        ctx.mark(button, "W5", W5)
        changed = True
    for button in ctx.all("td.wc-col-dismiss .wc-dismiss .btn--icon"):
        ctx.mark(button, "W5", W5)
        changed = True
    if changed:
        # The opened row's own action (.wc-context-actions .btn--dark) is not inside a ledger cell, so it stays dark.
        ctx.style(
            ".work-centre .wc-dismiss .btn--icon{border-color:transparent;background:transparent;box-shadow:none;color:var(--muted)}"
            ".work-centre .wc-dismiss .btn--icon:hover{background:var(--surface-3);border-color:var(--line-strong);color:var(--ink)}",
            "W5", W5)


@patch(*WORK_CENTRE_STATES)
def w6_compact_activity(ctx: Ctx) -> None:
    panel = ctx.one(".wc-activity")
    if panel is None:
        return
    ctx.style(
        ".work-centre .wc-activity-table td{height:auto;padding:5px 16px;font-size:16px;font-weight:600;letter-spacing:0}"
        ".work-centre .wc-activity-table tbody th{padding:5px 16px}"
        ".work-centre .wc-activity-table thead th{height:30px;padding-top:4px;padding-bottom:4px}",
        "W6", W6)
    ctx.mark(panel, "W6", W6)


@patch("search", "search-filters")
def search_results_get_the_width(ctx: Ctx) -> None:
    """W3's Type and Due columns need room: the results take the wider share and Case/PO stays on one line."""
    if ctx.one(".case-search-layout") is None:
        return
    ctx.style(
        ".case-search-layout{grid-template-columns:minmax(0,1.75fr) minmax(360px,1fr)}"
        ".case-search-layout table td:first-child,"
        ".case-search-layout table td:first-child *{white-space:nowrap}",
        "W3", "Search results gain Type and Due (FRD-15), the preview gains Copy Case/PO and reads Claim reference for the claim number, and the results take the wider share of the page so the table does not wrap.")


# -- W8 (#1213: Unassigned as a target, and Take) ----------------------------

W8_ROWS = "An Unassigned row carries Take, a small primary button, beside Assign Engineer."
W8_DIALOG = "The Assign Engineer list shows the signed-in person first as Name (you) and gains an Unassigned option; the dialog has no Reason box."
W8_MINE = ("Mine gains a With Engineer row: its kind chip reads With Engineer, its Owner is the Engineer and its action is Open Case. "
           "It repeats the Review row's layout; its Case is the oldest one in this page's New cases list that has no row here. "
           "The capture holds no due instant for that Case, so Due reads No due date, last in Later (question: FRD-15 says every "
           "kind but Open tasks has a due instant).")
W8_CASES = "Cases · With Engineer: the Engineer cell reads Unassigned where the Case has no Engineer."

TAKE_STATES = ("work-centre", "work-centre-assign", "work-centre-mine")

# One description per state: the strip shows the first summary a change id records on a page.
W8_SUMMARY = {
    "work-centre": W8_ROWS,
    "work-centre-assign": f"{W8_ROWS} The open row carries it too. {W8_DIALOG}",
    "work-centre-mine": f"{W8_ROWS} {W8_MINE}",
    "cases-with-engineer": W8_CASES,
}


@functools.lru_cache(maxsize=None)
def _shell_staff_ids() -> dict[str, str]:
    """Staff id by username, from the Assign Engineer list of the work-centre-assign capture.

    The three Take states share one shell-lane test store, and only that capture renders the dialog (it is
    drawn when an Unassigned row is open), so it is the one place a Work Centre capture holds the viewer's id.
    """
    page = BeautifulSoup(SHELL_ASSIGN_CAPTURE.read_text(encoding="utf-8"), "lxml")
    return {option.get_text(strip=True): option["value"]
            for option in page.select("select#wc-assign-engineer option[value]") if option["value"]}


def _viewer_staff_id(ctx: Ctx) -> str:
    """The signed-in person's staff id: Take posts it as engineerId (issue-1213 criterion 10), and an omitted
    Engineer means Unassigned (criteria 9 and 13), so a Take form without it would post Set to Unassigned."""
    signed_in = ctx.one(".rail-user strong")
    name = signed_in.get_text(strip=True) if signed_in is not None else ""
    staff_id = _shell_staff_ids().get(name)
    if staff_id is None:
        raise RuntimeError(f"{ctx.key}: no staff id for the signed-in person {name!r} in {SHELL_ASSIGN_CAPTURE.name}")
    return staff_id


def _take_form(ctx: Ctx, case_id: str, staff_id: str) -> Tag:
    return ctx.html(
        '<form action="/?handler=AssignEngineer" method="post" data-wc-take>'
        f'<input name="caseId" type="hidden" value="{escape(case_id)}"/>'
        f'<input name="engineerId" type="hidden" value="{escape(staff_id)}"/>'
        '<button class="btn btn--primary btn--small" type="submit">Take</button></form>')


@patch(*TAKE_STATES)
def w8_take_beside_assign_engineer(ctx: Ctx) -> None:
    if ctx.one('tr[data-wc-row-kind="unassigned"]') is None:
        return
    staff_id = _viewer_staff_id(ctx)
    changed = False
    for row in ctx.all('tr[data-wc-row-kind="unassigned"]'):
        cell = row.select_one("td.wc-col-action")
        assign = cell.select_one(":scope > a.btn") if cell is not None else None
        if assign is None:
            continue
        # The capture's own action cell: the Assign Engineer button moves into the shared action row.
        wrapper = ctx.html('<div class="wc-row-actions"></div>')
        assign.insert_before(wrapper)
        wrapper.append(assign.extract())
        take = _take_form(ctx, row.get("data-wc-row", ""), staff_id)
        wrapper.append(take)
        ctx.mark(take, "W8", W8_SUMMARY[ctx.key])
        changed = True
    # The open row's own actions (a dark Assign Engineer) gain Take beside it.
    if ctx.one('tr[data-wc-row-kind="unassigned"][aria-selected="true"]') is not None:
        for assign in ctx.all('.wc-context-actions a[data-wc-dialog="wc-assign-dialog"]'):
            take = _take_form(ctx, ctx.one('tr[aria-selected="true"]').get("data-wc-row", ""), staff_id)
            assign.insert_after(take)
            ctx.mark(take, "W8", W8_SUMMARY[ctx.key])
    if changed:
        ctx.style(
            ".work-centre .wc-ledger-table:has(.wc-row-actions) .wc-col-action{width:196px}"
            ".work-centre .wc-ledger-table .wc-row-actions>.btn{flex:1 1 auto;justify-content:flex-start;white-space:nowrap}"
            "@media (max-width:979px){.work-centre .wc-ledger-table:has(.wc-row-actions) .wc-col-action{width:186px}}",
            "W8", W8_SUMMARY[ctx.key])


@patch("work-centre-assign")
def w8_assign_dialog_you_first_and_unassigned(ctx: Ctx) -> None:
    select = ctx.one("select#wc-assign-engineer")
    signed_in = ctx.one(".rail-user strong")
    if select is None or signed_in is None:
        return
    name = signed_in.get_text(strip=True)
    engineers = [option for option in select.find_all("option") if option.get("value")]
    mine = next((option for option in engineers if option.get_text(strip=True) == name), None)
    if mine is None:
        return
    mine.string = f"{name} (you)"
    if mine is not engineers[0]:
        engineers[0].insert_before(mine.extract())
    unassigned = ctx.html('<option value="unassigned">Unassigned</option>')
    select.append(unassigned)
    ctx.mark(mine, "W8", W8_SUMMARY[ctx.key])
    ctx.mark(unassigned, "W8", W8_SUMMARY[ctx.key])


@patch("work-centre-mine")
def w8_mine_with_engineer_row(ctx: Ctx) -> None:
    review = ctx.one('tr[data-wc-row-kind="review"]')
    later = ctx.one('tr.wc-group-row[data-wc-group="later"]')
    if review is None or later is None:
        return
    # The Case: the oldest row of this page's New cases list that is not already a row here.
    new_rows = ctx.all("table.wc-new-cases-table tr[data-wc-new-case-row]")
    days = [datetime.fromisoformat(time["datetime"]).date() for time in
            (new.select_one("time[datetime]") for new in new_rows) if time is not None]
    case_id = reference = detail = received = None
    for new in reversed(new_rows):
        link = new.select_one(".wc-col-ref a")
        time = new.select_one("time[datetime]")
        if link is None or time is None or ctx.one(f'tr[data-wc-row="{new.get("data-wc-record", "")}"]') is not None:
            continue
        case_id, reference = new["data-wc-record"], link.get_text(strip=True)
        detail = new.find_all("td")[1].get_text(" ", strip=True).split("·")[0].strip()
        age = (max(days) - datetime.fromisoformat(time["datetime"]).date()).days
        received = "Today" if age == 0 else f"{age} d ago"
        break
    owner = review.select_one(".wc-col-owner")
    if case_id is None or owner is None:
        return
    old_id, old_reference = review["data-wc-row"], review.select_one(".wc-col-record a").get_text(strip=True)
    row = copy.copy(review)
    for element in [row] + row.find_all(True):
        for attribute, value in list(element.attrs.items()):
            if isinstance(value, str):
                element[attribute] = value.replace(old_id, case_id).replace(old_reference, reference)
    row["data-wc-row-kind"] = "with-engineer"
    for text in row.find_all(string=True):
        if old_reference in text:
            text.replace_with(text.replace(old_reference, reference))
    task = row.select_one(".wc-col-task")
    task.select_one("a.wc-task-link").string = "With Engineer"
    task.select_one("small").string = "With Engineer"
    task.select_one(".wc-fold").string = f"{owner.get_text(strip=True)} · {received}"
    record_small = row.select_one(".wc-col-record small")
    if record_small is not None:
        record_small.string = detail
    row.select_one(".wc-col-received").string = received
    row.select_one(".wc-col-action .btn span").string = "Open Case"
    # The cloned Review row's Due belongs to another Case. The capture holds no due instant for this one (a With
    # Engineer Case's Due is its one due instant, a chase time or Due by date), so it is drawn undated with the label
    # an Open tasks row already uses, last in Later where FRD-15 puts undated rows.
    due = row.select_one(".wc-col-due")
    due.clear()
    due.append(ctx.html('<span class="wc-due wc-due--later">No due date</span>'))
    last = later
    for sibling in later.find_next_siblings("tr"):
        if not sibling.has_attr("data-wc-row"):
            break
        last = sibling
    last.insert_after(row)
    ctx.mark(row, "W8", W8_SUMMARY[ctx.key])
    # The counts that name this list follow the new row.
    title = later.select_one("h3")
    if title is not None:
        title.string = re.sub(r"\((\d+)\)", lambda m: f"({int(m.group(1)) + 1})", title.get_text(strip=True))
    meta = ctx.one("#wc-panel-attention .wc-toolbar .meta")
    if meta is not None:
        meta.string = re.sub(r"\d+", lambda m: str(int(m.group(0)) + 1), meta.get_text(strip=True), count=1)
    tab = ctx.one("#wc-tab-attention .tab-count")
    if tab is not None:
        tab.string = str(int(tab.get_text(strip=True)) + 1)
    # A kind filter for it, beside Unassigned (a copy of the Review filter chip).
    review_chip = ctx.one('.wc-filters a.chip[data-wc-kind="review"]')
    unassigned_chip = ctx.one('.wc-filters a.chip[data-wc-kind="unassigned"]')
    if review_chip is not None and unassigned_chip is not None:
        chip = copy.copy(review_chip)
        chip["data-wc-kind"] = "with-engineer"
        chip["href"] = chip["href"].replace("kind=review", "kind=with-engineer")
        chip.find(string=lambda s: s.strip() == "Review").replace_with("With Engineer")
        chip.select_one(".n").string = "1"
        unassigned_chip.insert_after(chip)
        ctx.mark(chip, "W8", W8_SUMMARY[ctx.key])


@patch("cases-with-engineer")
def w8_cases_engineer_unassigned(ctx: Ctx) -> None:
    table = ctx.one(".cases-table table")
    if table is None:
        return
    heads = [th.get_text(strip=True) for th in table.select("thead th")]
    if "Engineer" not in heads:
        return
    column = heads.index("Engineer")
    rows = table.select("tbody tr[data-cases-row]")
    if not rows:
        return
    # The capture's three Cases all have an Engineer; the last is drawn as a Case with none.
    cell = rows[-1].find_all("td")[column]
    cell.string = "Unassigned"
    ctx.mark(cell, "W8", W8_SUMMARY[ctx.key])
