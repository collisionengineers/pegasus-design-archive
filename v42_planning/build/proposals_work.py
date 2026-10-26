"""Work Centre Proposal patches: open queries in Needs attention (P).

An Unassigned open query is a Needs attention row with Take; a query assigned to the
viewer is in Mine. The row's record is the Case; its action opens the Case's Queries.
"""
from __future__ import annotations

import re

from bs4 import Tag

from proposals_v42 import Ctx, patch

QUERY_ID = "00000000-0000-4000-8000-0000000c0e42"
SUMMARY = "Open queries in Needs attention: Unassigned ones with Take, the viewer's own in Mine."


def _row(case_href: str, owner: str, take: bool, scope: str) -> str:
    take_form = (
        '<form action="/?handler=TakeQuery" data-wc-take="" method="post">'
        f'<input name="queryId" type="hidden" value="{QUERY_ID}">'
        f'<input name="returnUrl" type="hidden" value="/?scope={scope}">'
        '<button class="btn btn--primary btn--small" data-busy-label="Assigning…" type="submit">Take</button></form>'
    ) if take else ""
    return (
        f'<tr aria-selected="false" data-wc-record="{QUERY_ID}" data-wc-row="{QUERY_ID}" data-wc-row-kind="query" id="wc-row-{QUERY_ID}">'
        '<td class="wc-col-task">'
        f'<a aria-expanded="false" class="wc-task-link" href="{case_href}?section=queries">Query — QDOS26190 — storage charges</a>'
        f'<small>Query</small><span class="wc-fold">{owner} · 1 d ago</span></td>'
        f'<td class="wc-col-record"><span class="mono"><a href="{case_href}">QDOS26190</a></span><small>Mercedes A180 PO16DDF</small></td>'
        f'<td class="wc-col-owner">{owner}</td>'
        '<td class="wc-col-due">No due date</td>'
        '<td class="wc-col-received">1 d ago</td>'
        '<td class="wc-col-action"><div class="wc-row-actions">'
        f'<a class="btn btn--small" href="{case_href}?section=queries">'
        '<svg aria-hidden="true" class="icon"><use href="#icon-arrow-right"></use></svg><span>Open query</span></a>'
        f'{take_form}</div></td>'
        '<td class="wc-col-dismiss"></td></tr>'
    )


def _bump(node: Tag | None) -> None:
    if node is None:
        return
    for text in node.find_all(string=re.compile(r"^\s*\d+\s*$")):
        text.replace_with(str(int(text.strip()) + 1))
        return


def _query_row(ctx: Ctx, owner: str, take: bool, scope: str) -> None:
    ai = ctx.one('tr[data-wc-row-kind="ai"]')
    anchor = ai or ctx.all("tr[data-wc-row]")[-1]
    case_href = "/Cases/2dc71cf4-debc-403d-be99-241d73c16bd2"
    row = Ctx.html(_row(case_href, owner, take, scope))
    if ai is not None:
        anchor.insert_before(row)
    else:
        anchor.insert_after(row)
    ctx.mark(row, "P", SUMMARY)
    chips = ctx.one("nav.wc-filters")
    if chips is not None:
        chip = Ctx.html(f'<a aria-current="false" class="chip" data-wc-kind="query" href="/?scope={scope}&amp;kind=query">'
                        'Query <span class="n">1</span></a>')
        chips.append(chip)
        ctx.mark(chip, "P", SUMMARY)
    _bump(ctx.one("#wc-tab-attention .tab-count"))
    for meta in ctx.all("span.meta"):
        match = re.match(r"^\s*(\d+)\s+items\s*$", meta.get_text(" ", strip=True))
        if match:
            meta.string = f"{int(match.group(1)) + 1} items"
    for group in ctx.all("tr.wc-group-row td"):
        match = re.match(r"^\s*Later\s*\((\d+)\)\s*$", group.get_text(" ", strip=True))
        if match:
            group.string = f"Later ({int(match.group(1)) + 1})"


@patch("work-centre")
def office_query_row(ctx: Ctx) -> None:
    _query_row(ctx, "Unassigned", take=True, scope="office")


@patch("work-centre-mine")
def mine_query_row(ctx: Ctx) -> None:
    _query_row(ctx, "e.mawdsley", take=False, scope="mine")
