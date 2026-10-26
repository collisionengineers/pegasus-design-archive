"""Build #mailMessageDialog (_MessageDialog.cshtml) fragments for m1..m12 from captured-live/inbox/.

In the live application (v41 Stage 2), clicking an e-mail row on /Inbox fetches
/Inbox/{id}?handler=Dialog and mounts #mailMessageDialog into [data-mail-dialog-root].
The capture tests saved /Inbox/{id} (Message.cshtml, which renders the identical
_MessageRecord and _MessageNested partials with InDialog=false). This module converts
each captured message record into the exact InDialog=true _MessageDialog.cshtml
markup for Today (and synthesizes m5, m6, m8, m9 and m10 from the captured templates
and their captured fragment-content-m*.html files), together with the Attachments tab,
Thread tab and Reply / Reply all / Forward composer views for interactive browsing.
"""
from __future__ import annotations

import copy
import html as html_mod
import pathlib
import re

from bs4 import BeautifulSoup, Tag

CAPTURED_INBOX = pathlib.Path(__file__).resolve().parent.parent / "captured-live" / "inbox"

# Metadata for the twelve seeded fixtures in ZzMockupCaptureInbox.cs.
FIXTURES: dict[str, dict] = {
    "m1": {
        "sender": "instructions@northline.example",
        "to": "desk@collisionengineers.co.uk",
        "subject": "New instruction — MA59 BDY — rear impact",
        "body": "Please instruct an engineer to inspect our insured vehicle following a rear impact on 24 September.\nThe vehicle is at the policyholder's address.",
        "time": "13 Oct 2026 09:14",
        "iso": "2026-10-13T09:14:00.0000000+01:00",
        "decided": "13 Oct 2026 09:16",
        "category": "New instruction",
        "code": "new-instruction",
        "case_ref": None,
        "case_id": None,
        "attachments": [
            ("rear-quarter.jpg", "image/jpeg", "1.2 MB", "Pending Case"),
            ("odometer.jpg", "image/jpeg", "400 KB", "Pending Case"),
        ],
        "thread": ["m1", "m5"],
    },
    "m2": {
        "sender": "claims@northline.example",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Update — QDOS26214 — repair authority",
        "body": "Repair authority is attached. Please proceed on QDOS26214 and confirm the engineer.",
        "time": "13 Oct 2026 08:02",
        "iso": "2026-10-13T08:02:00.0000000+01:00",
        "decided": "13 Oct 2026 08:04",
        "category": "Case update",
        "code": "case-update",
        "case_ref": "QDOS26214",
        "case_id": "85de4c48-ed02-445f-a2ce-d97a087c19dd",
        "attachments": [
            ("repair-authority.pdf", "application/pdf", "210 KB", "Attached to QDOS26214"),
        ],
        "thread": ["m2", "m12", "m4", "m6"],
    },
    "m3": {
        "sender": "Sender not recorded",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Please see attached",
        "body": "Photographs attached. No reference in the message.",
        "time": "12 Oct 2026 17:48",
        "iso": "2026-10-12T17:48:00.0000000+01:00",
        "decided": "12 Oct 2026 17:50",
        "category": "Unclassified",
        "code": "unclassified",
        "case_ref": None,
        "case_id": None,
        "attachments": [
            ("IMG_0001.jpg", "image/jpeg", "900 KB", "No Case Found"),
            ("IMG_0002.jpg", "image/jpeg", "870 KB", "No Case Found"),
            ("IMG_0003.jpg", "image/jpeg", "880 KB", "No Case Found"),
        ],
        "thread": ["m3"],
    },
    "m4": {
        "sender": "claims@northline.example",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Query — QDOS26214 — hire charges",
        "body": "Please explain the hire charges on the report for QDOS26214.",
        "time": "12 Oct 2026 11:20",
        "iso": "2026-10-12T11:20:00.0000000+01:00",
        "decided": "12 Oct 2026 11:22",
        "category": "Query",
        "code": "query",
        "case_ref": "QDOS26214",
        "case_id": "85de4c48-ed02-445f-a2ce-d97a087c19dd",
        "attachments": [],
        "thread": ["m2", "m12", "m4", "m6"],
    },
    "m5": {
        "sender": "photos@northline.example",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Images — MA59 BDY",
        "body": "Further photographs of the rear quarter and the odometer.",
        "time": "11 Oct 2026 15:05",
        "iso": "2026-10-11T15:05:00.0000000+01:00",
        "decided": "11 Oct 2026 15:07",
        "category": "Images received",
        "code": "images-received",
        "case_ref": None,
        "case_id": None,
        "attachments": [
            ("rear-quarter-2.jpg", "image/jpeg", "1.1 MB", "No Case Found"),
            ("odometer-2.jpg", "image/jpeg", "380 KB", "No Case Found"),
        ],
        "thread": ["m1", "m5"],
    },
    "m6": {
        "sender": "desk@collisionengineers.co.uk",
        "to": "claims@northline.example",
        "subject": "Re: QDOS26214 — engineer's report",
        "body": "The engineer's report is attached.",
        "time": "10 Oct 2026 14:11",
        "iso": "2026-10-10T14:11:00.0000000+01:00",
        "decided": "10 Oct 2026 14:11",
        "category": "Unclassified",
        "code": "unclassified",
        "case_ref": "QDOS26214",
        "case_id": "85de4c48-ed02-445f-a2ce-d97a087c19dd",
        "attachments": [
            ("QDOS26214_report.pdf", "application/pdf", "640 KB", "Sent"),
        ],
        "thread": ["m2", "m12", "m4", "m6"],
    },
    "m7": {
        "sender": "accounts@northline.example",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Remittance advice — October",
        "body": "Please find attached our remittance advice for October.",
        "time": "13 Oct 2026 07:41",
        "iso": "2026-10-13T07:41:00.0000000+01:00",
        "decided": "13 Oct 2026 07:43",
        "category": "Billing",
        "code": "billing",
        "case_ref": None,
        "case_id": None,
        "attachments": [],
        "thread": ["m7"],
    },
    "m8": {
        "sender": "news@toolvendor.example",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Your October product update",
        "body": "New diagnostic tools are now available. View our catalogue online.",
        "time": "13 Oct 2026 06:30",
        "iso": "2026-10-13T06:30:00.0000000+01:00",
        "decided": "13 Oct 2026 06:32",
        "category": "Not client related",
        "code": "not-client-related",
        "case_ref": None,
        "case_id": None,
        "attachments": [],
        "thread": ["m8"],
    },
    "m9": {
        "sender": "alex@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "FW: QDOS26214 — engineer note",
        "body": "Forwarding for the file. Engineer's note on the rear quarter.",
        "time": "13 Oct 2026 05:55",
        "iso": "2026-10-13T05:55:00.0000000+01:00",
        "decided": "13 Oct 2026 05:57",
        "category": "Internal CC",
        "code": "internal-cc",
        "case_ref": None,
        "case_id": None,
        "attachments": [],
        "thread": ["m9"],
    },
    "m10": {
        "sender": "claims@northline.example",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Possible instruction — LK21 ABC",
        "body": "We may need an inspection on LK21 ABC next week. We will confirm.",
        "time": "13 Oct 2026 05:12",
        "iso": "2026-10-13T05:12:00.0000000+01:00",
        "decided": "13 Oct 2026 05:14",
        "category": "Pre-instruction",
        "code": "pre-instruction",
        "case_ref": None,
        "case_id": None,
        "attachments": [],
        "thread": ["m10"],
    },
    "m11": {
        "sender": "claims@meridian.example",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Cancellation — QDOS26220",
        "body": "Please cancel the instruction on QDOS26220. The claim has been withdrawn.",
        "time": "13 Oct 2026 04:48",
        "iso": "2026-10-13T04:48:00.0000000+01:00",
        "decided": "13 Oct 2026 04:50",
        "category": "Cancellation",
        "code": "cancellation",
        "case_ref": "QDOS26220",
        "case_id": "bee37ce3-c710-4a5b-8e2c-67e8ed6ad8cb",
        "attachments": [],
        "thread": ["m11"],
    },
    "m12": {
        "sender": "claims@northline.example",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Re: QDOS26214 — thank you",
        "body": "Thank you for the report on QDOS26214.",
        "time": "13 Oct 2026 04:03",
        "iso": "2026-10-13T04:03:00.0000000+01:00",
        "decided": "13 Oct 2026 04:05",
        "category": "Case update",
        "code": "case-update",
        "case_ref": "QDOS26214",
        "case_id": "85de4c48-ed02-445f-a2ce-d97a087c19dd",
        "attachments": [],
        "thread": ["m2", "m12", "m4", "m6"],
    },
}


def load_ids() -> dict[str, str]:
    ids: dict[str, str] = {}
    notes = CAPTURED_INBOX / "notes.txt"
    if notes.exists():
        for line in notes.read_text(encoding="utf-8").splitlines():
            parts = line.strip().split("\t")
            if len(parts) == 2:
                ids[parts[0]] = parts[1]
    return ids


def _frag(markup: str) -> Tag:
    soup = BeautifulSoup(f"<div>{markup}</div>", "lxml")
    return soup.div


def _normalize_icons(root: Tag) -> None:
    for use in root.select("use[href]"):
        href = use["href"]
        if "lucide-sprite" in href and "#" in href:
            use["href"] = "#" + href.split("#", 1)[1]


def _synthesize_message_page(key: str, msg_id: str, template_body: Tag, template_id: str) -> Tag:
    """Create a synthetic Message.cshtml body for m5/m6/m8/m9/m10 from message-m7."""
    fx = FIXTURES[key]
    raw = str(template_body).replace(template_id, msg_id)
    doc = BeautifulSoup(raw, "lxml").body
    for h in doc.select("header.page-header h1, header.record-head h2"):
        h.string = fx["subject"]
    spans = doc.select("header.record-head .record-identity > span")
    if len(spans) >= 3:
        spans[0].string = fx["sender"]
        t = spans[2].select_one("time")
        if t is not None:
            t["datetime"] = fx["iso"]
            t.string = fx["time"]
    body_div = doc.select_one(".mail-body")
    if body_div is not None:
        body_div.clear()
        for line in fx["body"].split("\n"):
            p = BeautifulSoup(f"<p>{html_mod.escape(line)}</p>", "lxml").p
            body_div.append(p)
    # Attachments tab badge
    att_tab = doc.select_one('nav.tabs a[href*="section=attachments"]')
    if att_tab is not None:
        att_tab.clear()
        att_tab.append("Attachments")
        if fx["attachments"]:
            att_tab.append(_frag(f' <span class="tab-count">{len(fx["attachments"])}</span>').span)
    # Classification chips in Today
    chips = doc.select_one("#mailClassificationForm .mail-chips")
    if chips is not None:
        all_opts = [
            ("new-instruction", "New instruction"),
            ("triage-request", "Triage request"),
            ("pre-instruction", "Pre-instruction"),
            ("images-received", "Images received"),
            ("case-update", "Case update"),
            ("cancellation", "Cancellation"),
            ("query", "Query"),
            ("billing", "Billing"),
            ("general", "General"),
            ("not-client-related", "Not client related"),
            ("internal-cc", "Internal CC"),
            ("unclassified", "Unclassified"),
        ]
        chips.clear()
        for code, label in all_opts:
            if code == fx["code"]:
                chips.append(_frag(
                    '<button type="button" class="chip" aria-pressed="true">'
                    '<svg class="icon" aria-hidden="true"><use href="#icon-check"></use></svg>'
                    f'<span>{label}</span></button>'
                ).button)
            else:
                chips.append(_frag(
                    f'<button type="submit" class="chip" name="ClassificationKey" value="{code}" '
                    f'aria-pressed="false" data-busy-label="Saving…">{label}</button>'
                ).button)
    # m5 is Images received in Today, so it offers Register images in Today too.
    if key == "m5":
        foot = doc.select_one(".dialog-foot")
        if foot is not None:
            foot.append(_frag(
                '<button class="btn btn--dark" type="button" data-offered-action="RegisterImages" '
                'data-dialog-open="messageRegisterImagesDialog">'
                '<svg class="icon" aria-hidden="true"><use href="#icon-image"></use></svg>'
                '<span>Register images</span></button>'
            ).button)
    _normalize_icons(doc)
    return doc


def page_to_dialog_wrapper(page_body: Tag, key: str, msg_id: str, *, composing_mode: str | None = None) -> Tag:
    """Convert a Message.cshtml body into a wrapper <div> holding #mailMessageDialog + nested dialogs."""
    fx = FIXTURES[key]
    doc = copy.copy(page_body)
    _normalize_icons(doc)
    article = doc.select_one("article.record")
    tabs = article.select_one("nav.tabs")
    rec_body = article.select_one("div.record-body")
    foot = article.select_one("div.dialog-foot")

    # Remove the inner .mail-header route line when in dialog mode (the dialog head carries it).
    inner_hdr = rec_body.select_one(".mail-read > .mail-header")
    if inner_hdr is not None:
        inner_hdr.decompose()
    rec_body["class"] = ["dialog-body"]

    # Ensure data-mail-next-id hidden input exists on the dismissal form.
    dismiss_form = foot.select_one("form[data-message-dismissal]") if foot else None
    if dismiss_form is not None and dismiss_form.select_one("[data-mail-next-id]") is None:
        dismiss_form.append(_frag('<input type="hidden" name="next" value="" data-mail-next-id>').input)

    if composing_mode:
        label_map = {"reply": "Reply", "reply-all": "Reply all", "forward": "Forward"}
        prefix = f"{label_map.get(composing_mode, 'Reply')} · "
        title_html = (
            f'<div class="mail-dialog-title">'
            f'<h2 id="mailMessageDialog_title" class="wrap" tabindex="-1" data-dialog-initial-focus>'
            f'{html_mod.escape(prefix + fx["subject"])}</h2></div>'
        )
        tools_html = (
            '<span class="mail-dialog-tools">'
            '<button type="button" class="dialog-close" data-dialog-close aria-label="Close dialog">'
            '<svg class="icon" aria-hidden="true"><use href="#icon-x"></use></svg></button></span>'
        )
        # In dialog composing mode, only the composer sits in .dialog-body, and foot has Cancel + Send.
        composer = rec_body.select_one("form#mailComposerForm")
        if composer is not None:
            composer["class"] = ["stack", "mail-compose"]
            ph = composer.select_one(".panel-head")
            if ph is not None:
                ph.decompose()
            pb = composer.select_one(".panel-body")
            if pb is not None:
                pb["class"] = ["stack"]
            br = composer.select_one(".button-row")
            if br is not None:
                br.decompose()
            split = rec_body.select_one(".mail-split")
            if split is not None:
                split.decompose()
        tabs = None
        foot = _frag(
            f'<div class="dialog-foot">'
            f'<a class="btn" href="/Inbox/{msg_id}" data-mail-dialog-link>Cancel</a>'
            f'<button type="submit" form="mailComposerForm" class="btn btn--dark" data-busy-label="Sending…">'
            f'<svg class="icon" aria-hidden="true"><use href="#icon-send"></use></svg><span>Send</span></button>'
            f'</div>'
        ).div
    else:
        title_html = (
            f'<div class="mail-dialog-title">'
            f'<h2 id="mailMessageDialog_title" class="wrap" tabindex="-1" data-dialog-initial-focus>'
            f'{html_mod.escape(fx["subject"])}</h2>'
            f'<p class="mail-route">From {html_mod.escape(fx["sender"])} · To {html_mod.escape(fx["to"])} · '
            f'<time datetime="{fx["iso"]}">{fx["time"]}</time></p></div>'
        )
        tools_html = (
            '<span class="mail-dialog-tools">'
            '<span class="cluster mail-dialog-nav">'
            '<button type="button" class="icon-button" data-mail-previous aria-label="Previous message" title="Previous message">'
            '<svg class="icon" aria-hidden="true"><use href="#icon-chevron-left"></use></svg></button>'
            '<button type="button" class="icon-button" data-mail-next aria-label="Next message" title="Next message">'
            '<svg class="icon" aria-hidden="true"><use href="#icon-chevron-right"></use></svg></button>'
            '</span>'
            '<button type="button" class="dialog-close" data-dialog-close aria-label="Close dialog">'
            '<svg class="icon" aria-hidden="true"><use href="#icon-x"></use></svg></button>'
            '</span>'
        )

    wrapper = _frag(
        f'<div id="mailMessageDialog" class="dialog-backdrop" data-dialog="mailMessageDialog" '
        f'data-mail-message="{msg_id}" data-mail-key="{key}" hidden>'
        f'<section class="dialog dialog--mail" role="dialog" aria-modal="true" aria-labelledby="mailMessageDialog_title">'
        f'<div class="dialog-head">{title_html}{tools_html}</div>'
        f'</section></div>'
    )
    section = wrapper.select_one("section.dialog--mail")
    if tabs is not None:
        section.append(tabs.extract())
    section.append(rec_body.extract())
    if foot is not None:
        section.append(foot.extract() if foot.parent else foot)

    # Append sibling nested dialogs (#linkCaseDialog, #changeLinkedCaseDialog, #unlinkCaseDialog, etc.)
    for nested in doc.select("main .dialog-backdrop, body > .dialog-backdrop"):
        nid = nested.get("id") or ""
        if nid in ("linkCaseDialog", "changeLinkedCaseDialog", "unlinkCaseDialog",
                   "messageTriageDialog", "messageRegisterImagesDialog"):
            wrapper.append(nested.extract())
    return wrapper


def build_attachments_view(dialog_wrapper: Tag, key: str, msg_id: str) -> Tag:
    """Return a copy of dialog_wrapper showing the Attachments tab."""
    fx = FIXTURES[key]
    clone = copy.copy(dialog_wrapper)
    for tab in clone.select("nav.tabs a.tab"):
        if "section=attachments" in tab.get("href", ""):
            tab["aria-current"] = "page"
        else:
            tab.attrs.pop("aria-current", None)
    body = clone.select_one(".dialog-body")
    body.clear()
    if not fx["attachments"]:
        body.append(_frag('<div class="empty"><p>This message has no attachments.</p></div>').div)
    else:
        rows_html = []
        for fname, mime, size, outcome in fx["attachments"]:
            tone = "green" if outcome.startswith(("Attached", "Sent")) else "amber"
            rows_html.append(
                f'<tr data-attachment-outcome="{html_mod.escape(outcome)}">'
                f'<td><strong>{html_mod.escape(fname)}</strong></td>'
                f'<td>{html_mod.escape(mime)}</td>'
                f'<td class="tabular">{size}</td>'
                f'<td><span class="attachment-outcome"><span class="status status--{tone}">{html_mod.escape(outcome)}</span></span></td>'
                f'<td class="row-actions"><button type="button" class="btn btn--small" data-preview-attachment="{html_mod.escape(fname)}">Open file</button></td>'
                f'</tr>'
            )
        body.append(_frag(
            '<div class="table-wrap message-attachments">'
            '<table class="table table--compact" data-message-attachments>'
            '<thead><tr><th scope="col">File</th><th scope="col">Type</th><th scope="col">Size</th>'
            '<th scope="col">Outcome</th><th scope="col"><span class="sr-only">Open</span></th></tr></thead>'
            f'<tbody>{"".join(rows_html)}</tbody></table></div>'
        ).div)
    return clone


def build_thread_view(dialog_wrapper: Tag, key: str, msg_id: str, ids: dict[str, str]) -> Tag:
    """Return a copy of dialog_wrapper showing the Thread tab."""
    fx = FIXTURES[key]
    clone = copy.copy(dialog_wrapper)
    for tab in clone.select("nav.tabs a.tab"):
        if "section=thread" in tab.get("href", ""):
            tab["aria-current"] = "page"
        else:
            tab.attrs.pop("aria-current", None)
    body = clone.select_one(".dialog-body")
    body.clear()
    thread_keys = fx.get("thread") or [key]
    if len(thread_keys) <= 1:
        body.append(_frag('<div class="empty"><p>No other message in this conversation is kept here.</p></div>').div)
    else:
        for tkey in thread_keys:
            tfx = FIXTURES[tkey]
            tid = ids[tkey]
            current = ' aria-current="page"' if tkey == key else ""
            body.append(_frag(
                f'<a class="row-button" href="/Inbox/{tid}" data-mail-dialog-link{current}>'
                f'<span class="row-top"><span class="row-title">{html_mod.escape(tfx["sender"])}</span>'
                f'<span class="row-time"><time datetime="{tfx["iso"]}">{tfx["time"]}</time></span></span>'
                f'<span class="row-title">{html_mod.escape(tfx["subject"])}</span></a>'
            ).a)
    return clone


def build_compose_view(key: str, msg_id: str, mode: str, *, proposal: bool, ai_draft: bool = False) -> Tag:
    """Build a Reply / Reply all / Forward composer dialog wrapper for key."""
    fx = FIXTURES[key]
    label_map = {"reply": "Reply", "reply-all": "Reply all", "forward": "Forward"}
    label = label_map.get(mode, "Reply")
    subj_prefix = "FW: " if mode == "forward" else "Re: "
    subj = fx["subject"] if fx["subject"].startswith(("Re:", "FW:")) else subj_prefix + fx["subject"]
    case_ref = fx["case_ref"] or ""
    route_html = (
        '<div class="field"><label for="CorrespondenceTo">To</label>'
        '<input id="CorrespondenceTo" name="CorrespondenceTo" type="text" value=""></div>'
        if mode == "forward"
        else f'<p class="mail-route">From desk@collisionengineers.co.uk · To {html_mod.escape(fx["sender"])}</p>'
    )
    ai_banner = (
        '<div class="notice" role="status" data-ai-draft="72329218-8fe1-441c-8628-9e540bdc738f">'
        '<svg class="icon" aria-hidden="true"><use href="#icon-sparkles"></use></svg>'
        '<span><span class="src-tag src-tag--ai">AI</span> Draft prepared by Claude · Edit before sending</span></div>'
        if ai_draft else ""
    )
    body_text = (
        "Dear Northline Claims,\n\nThank you for your e-mail of 12 October. The hire charges on the report "
        "for QDOS26214 cover 14 days at the agreed daily rate while the vehicle was off the road awaiting parts.\n\n"
        "Kind regards,\nCollision Engineers"
        if ai_draft else ""
    )
    # In Today, any reply on a Case with an open query offers "Also resolve query".
    # In Proposal (L), only replying to an e-mail that holds an open query (m4) offers "Mark query done".
    show_query_tick = mode in ("reply", "reply-all") and (
        (proposal and key == "m4") or (not proposal and fx["case_ref"] == "QDOS26214")
    )
    tick_label = "Mark query done" if proposal else "Also resolve query"
    tick_checked = " checked" if ai_draft or key == "m4" else ""
    query_tick_html = (
        f'<div class="field"><label>'
        f'<input type="checkbox" id="ResolveQuery" name="ResolveQuery" value="true" data-resolve-query{tick_checked}>'
        f' {tick_label}</label></div>'
        if show_query_tick else ""
    )
    return _frag(
        f'<div id="mailMessageDialog" class="dialog-backdrop" data-dialog="mailMessageDialog" '
        f'data-mail-message="{msg_id}" data-mail-key="{key}" hidden>'
        f'<section class="dialog dialog--mail" role="dialog" aria-modal="true" aria-labelledby="mailMessageDialog_title">'
        f'<div class="dialog-head">'
        f'<div class="mail-dialog-title">'
        f'<h2 id="mailMessageDialog_title" class="wrap" tabindex="-1" data-dialog-initial-focus>'
        f'{html_mod.escape(label + " · " + fx["subject"])}</h2></div>'
        f'<span class="mail-dialog-tools">'
        f'<button type="button" class="dialog-close" data-dialog-close aria-label="Close dialog">'
        f'<svg class="icon" aria-hidden="true"><use href="#icon-x"></use></svg></button></span>'
        f'</div>'
        f'<div class="dialog-body">'
        f'<form method="post" id="mailComposerForm" action="/Inbox/{msg_id}?handler={label.replace(" ", "")}&amp;dialog=true" class="stack mail-compose">'
        f'<div class="stack">'
        f'<input type="hidden" name="compose" value="{mode}">'
        f'<div class="mail-compose-route">{route_html}'
        f'<div class="field case-picker" data-case-picker data-case-picker-fill '
        f'data-case-picker-url="/Inbox/{msg_id}?handler=CorrespondenceCaseOptions">'
        f'<label for="CorrespondenceCaseReference">Case / PO</label>'
        f'<input id="CorrespondenceCaseReference" name="CorrespondenceCaseReference" type="text" '
        f'value="{html_mod.escape(case_ref)}" maxlength="100" autocomplete="off" role="combobox" '
        f'aria-autocomplete="list" aria-expanded="false" aria-controls="message-case-options">'
        f'<div id="message-case-options" class="case-picker-options" data-case-picker-options hidden></div>'
        f'</div></div>'
        f'<div class="field"><label for="CorrespondenceSubject">Subject</label>'
        f'<input id="CorrespondenceSubject" name="CorrespondenceSubject" type="text" value="{html_mod.escape(subj)}"></div>'
        f'{ai_banner}'
        f'<div class="field"><label for="CorrespondenceBody">Message</label>'
        f'<textarea id="CorrespondenceBody" name="CorrespondenceBody" rows="8">{html_mod.escape(body_text)}</textarea></div>'
        f'{query_tick_html}'
        f'</div></form></div>'
        f'<div class="dialog-foot">'
        f'<a class="btn" href="/Inbox/{msg_id}" data-mail-dialog-link>Cancel</a>'
        f'<button type="submit" form="mailComposerForm" class="btn btn--dark" data-busy-label="Sending…">'
        f'<svg class="icon" aria-hidden="true"><use href="#icon-send"></use></svg><span>Send</span></button>'
        f'</div></section></div>'
    )


def mount_dialog_on_inbox(inbox_body: Tag, dialog_wrapper: Tag, msg_id: str) -> None:
    """Pin the message's row on the Inbox list and mount dialog_wrapper into [data-mail-dialog-root]."""
    for row in inbox_body.select("div.inbox-row[data-mail-row]"):
        if row.get("data-mail-row") == msg_id:
            row["aria-current"] = "true"
        else:
            row.attrs.pop("aria-current", None)
    mount = inbox_body.select_one("[data-mail-dialog-root]")
    if mount is None:
        return
    mount.clear()
    clone = copy.copy(dialog_wrapper)
    dialog = clone.select_one("#mailMessageDialog")
    if dialog is not None:
        dialog.attrs.pop("hidden", None)
        dialog["data-dialog-open-on-load"] = "true"
    for child in list(clone.contents):
        if isinstance(child, Tag):
            mount.append(child.extract())
