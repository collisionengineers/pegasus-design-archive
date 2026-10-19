"""U: Upload, Cases, Create case, Triage, Unidentified and Vehicle images.

Each patch edits the captured live page only where the capture holds the element it
changes. A capture without the element is left as it is.
"""
from __future__ import annotations

import functools
import pathlib
import re

from bs4 import BeautifulSoup, NavigableString, Tag

from proposals_v41 import Ctx, patch
from states_v41 import STATES

HERE = pathlib.Path(__file__).resolve().parent
INTAKE_CAPTURES = HERE.parent / "captured-live" / "intake"

INTAKE_STATES = tuple(state["key"] for state in STATES if state["lane"] == "intake")
CASES_STATES = tuple(key for key in INTAKE_STATES if key.startswith("cases-"))

U1 = ("U1", "The page subtitle and the narration sentences that carry no consequence go; the Attached, Discarded and Pending sentences stay as they are.")
U2 = ("U2", "The label Image intake reads Vehicle images, because the word intake does not appear in the interface.")
U3_FILTER = ("U3", "The Principal filter lists every Principal that appears in the queues, and Page N shows only when there is a previous or next page.")
U4 = ("U4", "Create case: each field is a label and input pair in the form grid, the Extracted from sentences and the provenance word go, and a value taken from the file carries the Extracted pill.")
U5 = ("U5", "Triage: Link case uses the Case picker with the label Case / PO, response evidence options read time and mailbox only, and Documents rows gain the View button beside Save as.")
U6 = ("U6", "The first card no longer repeats the facts the ribbon above it already shows.")


# -- U1 ---------------------------------------------------------------------

@patch("upload-review", "upload-review-new-case")
def u1_upload_review_narration(ctx: Ctx) -> None:
    ctx.remove(ctx.one(".up-head .up-subtitle"), *U1)
    decision = ctx.one('[data-upload-phase="decision"]')
    if decision is None:
        return
    ctx.remove(decision.select_one(".up-decision-head .up-explainer"), *U1)
    ctx.remove(decision.select_one(".up-choice-hint"), *U1)
    ctx.remove(decision.select_one(".up-proposal .up-explainer"), *U1)


# -- U2 ---------------------------------------------------------------------

IMAGE_INTAKE = re.compile(r"\bImage [Ii]ntake\b")
LABEL_ATTRIBUTES = ("title", "aria-label", "placeholder", "alt")


@patch(*INTAKE_STATES)
def u2_image_intake_label(ctx: Ctx) -> None:
    for node in list(ctx.body.find_all(string=IMAGE_INTAKE)):
        parent = node.parent
        if parent is None or parent.name in ("script", "style"):
            continue
        node.replace_with(NavigableString(IMAGE_INTAKE.sub("Vehicle images", str(node))))
        ctx.mark(parent, *U2)
    for element in ctx.body.find_all(True):
        for attribute in LABEL_ATTRIBUTES:
            value = element.get(attribute)
            if isinstance(value, str) and IMAGE_INTAKE.search(value):
                element[attribute] = IMAGE_INTAKE.sub("Vehicle images", value)
                ctx.mark(element, *U2)


# -- U3 ---------------------------------------------------------------------

@functools.lru_cache(maxsize=1)
def principals_in_the_queues() -> tuple[str, ...]:
    """Every Principal code on a row of any captured Cases queue."""
    codes: set[str] = set()
    for path in sorted(INTAKE_CAPTURES.glob("cases-*.html")):
        page = BeautifulSoup(path.read_text(encoding="utf-8"), "lxml")
        headers = [th.get_text(strip=True) for th in page.select(".cases-table thead th")]
        if "Principal" not in headers:
            continue
        column = headers.index("Principal")
        for row in page.select("tr[data-cases-row]"):
            cells = row.find_all("td")
            if column < len(cells) and cells[column].get_text(strip=True):
                codes.add(cells[column].get_text(strip=True))
    return tuple(sorted(codes))


@patch(*CASES_STATES)
def u3_principal_filter_and_page_text(ctx: Ctx) -> None:
    select = ctx.one("select#queue-principal")
    if select is not None:
        present = {option.get("value") for option in select.find_all("option")}
        for code in principals_in_the_queues():
            if code in present:
                continue
            new = ctx.html(f'<option value="{code}">{code}</option>')
            later = next((option for option in select.find_all("option")
                          if option.get("value") and option["value"] > code), None)
            if later is not None:
                later.insert_before(new)
            else:
                select.append(new)
            ctx.mark(select, *U3_FILTER)

    pagination = ctx.one("nav.pagination")
    if pagination is None or pagination.select("a"):
        return
    label = pagination.find("span")
    if label is None:
        return
    text = label.get_text(" ", strip=True)
    rest = re.sub(r"^Page\s+\d+\s*\S\s*", "", text)
    if rest != text and rest:
        label.string = rest[0].upper() + rest[1:]
        ctx.mark(label, *U3_FILTER)


# -- U4 ---------------------------------------------------------------------

def _provenance(small: Tag) -> str | None:
    """"extracted" for an Extracted from sentence or the word Extracted, "staff" for Staff."""
    text = small.get_text(" ", strip=True)
    if text.startswith("Extracted from") or text == "Extracted":
        return "extracted"
    if text == "Staff":
        return "staff"
    return None


@patch("create-seeded")
def u4_create_seeded_fields(ctx: Ctx) -> None:
    first = ctx.one('label[for^="draft-"]')
    if first is None:
        return
    container = first.parent
    groups: list[dict] = []
    for child in list(container.children):
        if not isinstance(child, Tag):
            continue
        if child.name == "label" and (child.get("for") or "").startswith("draft-"):
            groups.append({"label": child, "controls": [], "smalls": []})
        elif groups and child.name in ("input", "textarea", "select"):
            groups[-1]["controls"].append(child)
        elif groups and child.name == "small":
            groups[-1]["smalls"].append(child)
    if not groups:
        return

    grid = ctx.html('<div class="form-grid"></div>')
    first.insert_before(grid)
    for group in groups:
        extracted = False
        for small in group["smalls"]:
            kind = _provenance(small)
            if kind is None:
                continue
            extracted = extracted or kind == "extracted"
            ctx.remove(small, *U4)
        field = ctx.html('<div class="field"></div>')
        grid.append(field)
        field.append(group["label"].extract())
        if extracted:
            group["label"].append(" ")
            group["label"].append(ctx.html('<span class="src-tag">Extracted</span>'))
        for control in group["controls"]:
            field.append(control.extract())
    ctx.mark(grid, *U4)


# -- U5 ---------------------------------------------------------------------

MEDIA_TYPES = {
    ".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".mp4": "video/mp4", ".mov": "video/quicktime",
}


@patch("triage", "triage-finding")
def u5_triage(ctx: Ctx) -> None:
    # The Link case dialog's Case ID box becomes the Case picker (Mail/Message.cshtml markup).
    box = ctx.one('[data-dialog="triage-link-case-dialog"] #triage-link-case-id')
    if box is not None and box.find_parent(class_="field") is not None:
        field = box.find_parent(class_="field")
        label = field.find("label")
        if label is not None:
            label.string = "Case / PO"
        field["class"] = field.get("class", []) + ["case-picker"]
        field["data-case-picker"] = ""
        box["type"] = "text"
        box["autocomplete"] = "off"
        box["role"] = "combobox"
        box["aria-autocomplete"] = "list"
        box["aria-expanded"] = "false"
        box["aria-controls"] = "triage-link-case-options"
        field.append(ctx.html('<div id="triage-link-case-options" class="case-picker-options" data-case-picker-options hidden></div>'))
        ctx.mark(field, *U5)

    # Response evidence options keep the time and the mailbox.
    for option in ctx.all("select#triage-response-candidate option"):
        if not option.get("value"):
            continue
        parts = [part.strip() for part in option.get_text(" ", strip=True).split("—")]
        if len(parts) > 2:
            option.string = f"{parts[0]} — {parts[1]}"
            ctx.mark(option, *U5)

    # Documents rows gain the live View button beside Save as.
    for row in ctx.all("#triage-files-documents .doc-row"):
        actions = row.select_one(".doc-row-actions")
        download = actions.select_one("a[download]") if actions else None
        if download is None or actions.select_one("[data-evidence-item]") is not None:
            continue
        name_tag = row.select_one(".doc-row-name b")
        name = name_tag.get_text(strip=True) if name_tag else ""
        media = MEDIA_TYPES.get(pathlib.PurePosixPath(name.lower()).suffix)
        if media is None:
            continue
        href = download["href"]
        view = ctx.html(
            f'<a class="btn btn--small" href="{href}&amp;inline=true" data-evidence-item '
            f'data-download-href="{href}" data-media-type="{media}" data-file-name="{name}">'
            '<svg class="icon" aria-hidden="true"><use href="#icon-eye" /></svg><span>View</span></a>')
        download.insert_before(view)
        listing = row.find_parent(attrs={"data-document-list": True})
        if listing is not None and not listing.has_attr("data-evidence-set"):
            listing["data-evidence-set"] = ""
        ctx.mark(view, *U5)


# -- U6 ---------------------------------------------------------------------

@patch("unidentified", "vehicle-images")
def u6_first_card_repeats_ribbon(ctx: Ctx) -> None:
    ribbon = ctx.one(".record .ribbon")
    if ribbon is None:
        return
    shown = {node.get_text(" ", strip=True)
             for node in ribbon.select(".ribbon-value, .ribbon-chips .status")}
    card = next((panel for panel in ctx.all(".record .panel") if panel.select_one("dl.fact-grid")), None)
    if card is None:
        return
    facts = card.select_one("dl.fact-grid")
    for fact in facts.select(":scope > .fact"):
        value = fact.find("dd")
        if value is not None and value.get_text(" ", strip=True) in shown:
            ctx.remove(fact, *U6)
    if facts.select_one(".fact") is None:
        facts.decompose()


# -- U7 to U10 --------------------------------------------------------------

U7 = ("U7", "The Principal filter sits in the list head beside the count, so the band that held one select goes.")
U8 = ("U8", "Quick detail shows what the row does not: one compact fact grid without repeating Case/PO, registration and claimant.")
U9 = ("U9", "Review new Case proposal is the decision's primary button; Find a Case and Leave undecided stay secondary.")
U10 = ("U10", "The form is bounded and short fields share rows, so controls are not stretched across the page; Create case sits at the form's end.")


# -- U7 ---------------------------------------------------------------------
# Registered after U3, so the moved select already carries U3's option list.

@patch(*CASES_STATES)
def u7_principal_filter_in_list_head(ctx: Ctx) -> None:
    form = ctx.one(".cases-list > form.cases-filters")
    head = ctx.one(".cases-list > .pane-head")
    if form is None or head is None or form.select_one("select#queue-principal") is None:
        return
    label = form.select_one('label[for="queue-principal"]')
    if label is not None:
        label["class"] = label.get("class", []) + ["sr-only"]
    form.extract()
    head.append(form)
    ctx.mark(form, *U7)
    ctx.style(
        ".cases-list .pane-head .cases-filters{margin:0 0 0 12px;padding:0;border:0;background:none}"
        ".cases-list .pane-head .cases-filters .field{min-width:0}"
        ".cases-list .pane-head .cases-filters select{width:auto;min-height:32px;font-size:12px}",
        *U7)


# -- U8 ---------------------------------------------------------------------

U8_IN_THE_ROW = ("Case/PO", "Registration", "Claimant")


@patch(*CASES_STATES)
def u8_quick_detail_one_fact_grid(ctx: Ctx) -> None:
    canvas = ctx.one('.cases-detail [data-cases-detail="Case"]')
    grid = canvas.select_one("dl.cases-facts") if canvas is not None else None
    if grid is None:
        return
    for fact in grid.select(":scope > .fact"):
        label = fact.find("dt")
        if label is not None and label.get_text(strip=True) in U8_IN_THE_ROW:
            ctx.remove(fact, *U8)
    work = canvas.select_one(".cases-work")
    if work is not None:
        for row in work.select(".decision-row"):
            label, value = row.find("span"), row.find("strong")
            if label is None or value is None:
                continue
            fact = ctx.html('<div class="fact"><dt></dt><dd></dd></div>')
            fact.dt.string = label.get_text(strip=True)
            fact.dd.string = value.get_text(" ", strip=True)
            grid.append(fact)
        ctx.remove(work, *U8)
    ctx.mark(grid, *U8)
    ctx.style(
        ".cases-detail .cases-facts .fact{display:grid;grid-template-columns:96px minmax(0,1fr);gap:8px;align-items:baseline;padding:6px 11px}"
        ".cases-detail .cases-facts .fact dd{margin:0}",
        *U8)


# -- U9 ---------------------------------------------------------------------

@patch("upload-review-new-case")
def u9_review_new_case_proposal_is_primary(ctx: Ctx) -> None:
    decision = ctx.one('[data-upload-phase="decision"]')
    link = decision.select_one(".up-proposal a.up-text-link") if decision is not None else None
    find = decision.select_one("details.up-search") if decision is not None else None
    if link is None or find is None:
        return
    link["class"] = ["btn", "btn--primary"]
    for node in list(link.children):
        if isinstance(node, NavigableString) and node.strip():
            node.replace_with(ctx.html(f"<span>{node.strip()}</span>"))
    block = link.find_parent(class_="up-proposal")
    block.extract()
    find.insert_before(block)
    ctx.mark(link, *U9)
    ctx.style(
        '[data-upload-phase="decision"] .up-proposal{border-top:0;padding-top:0}'
        '[data-upload-phase="decision"] .up-proposal > .btn{width:100%}',
        *U9)


# -- U10 --------------------------------------------------------------------

@patch("create-manual", "create-seeded")
def u10_create_form_bounded(ctx: Ctx) -> None:
    form = ctx.one('form[action^="/Cases/Create"]')
    if form is None:
        return
    ctx.mark(form, *U10)
    # Short fields share rows: the manual form's two field grids become three columns.
    if ctx.key == "create-manual":
        for grid in form.select(".grid.grid-2"):
            grid["class"] = [name if name != "grid-2" else "grid-3" for name in grid.get("class", [])]
            ctx.mark(grid, *U10)
    # The button row sits directly under the last panel, Cancel to the left of the primary.
    buttons = form.select_one(".cluster")
    if buttons is not None:
        if buttons.parent is not form:
            panel = buttons.find_parent("section", class_="panel")
            buttons.extract()
            panel.insert_after(buttons)
        primary = buttons.select_one(".btn--primary")
        cancel = buttons.select_one('a.btn[href="/Cases"]')
        if primary is not None and cancel is not None and primary.find_next_sibling(cancel.name) is cancel:
            primary.insert_before(cancel.extract())
        ctx.mark(buttons, *U10)
    ctx.style(
        'form[action^="/Cases/Create"]{max-width:960px}'
        'form[action^="/Cases/Create"] > .cluster{justify-content:flex-end}',
        *U10)
