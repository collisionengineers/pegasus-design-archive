"""Upload initial screen Proposal patches: 5 visual designs (UB1..UB5, sign-off AB).

Covers both entry points to /Upload:
1. Left-hand navigation rail (/Upload): upload-a .. upload-e
2. Case workspace "Add evidence" (/Upload?caseId=85de4c48-ed02-445f-a2ce-d97a087c19dd
   for QDOS26214): upload-a-case .. upload-e-case

Today on upload-a..upload-e is the exact live /Upload capture; Today on
upload-a-case..upload-e-case seeds the live Upload.cshtml DeclaredCaseId +
_UploadDestinationCard.cshtml block inside form.up-select.

Proposal replaces the narrow 760px floating column with one of five structured
Pegasus workspace layouts while preserving every OperatorLabels.Upload string,
limit (20 files maximum, 100.0 MB per file, 200.0 MB per upload), accepted
extension list, and upload.js progressive-enhancement hook.
"""
from __future__ import annotations

from bs4 import Tag

from proposals_v42 import Ctx, patch, presets

CASE_ID = "85de4c48-ed02-445f-a2ce-d97a087c19dd"
CASE_HREF = f"/Cases/{CASE_ID}"
CASE_REF = "QDOS26214"
CASE_PERSON = "MA59BDY · R. Whitfield"
CASE_PRINCIPAL = "QDOS"
CASE_STAGE = "Report sent"
APPEAR_UNDER_FILES = "They appear under Files once processed."

ACCEPT_ATTR = (
    ".eml,.pdf,.docx,.doc,.msg,.jpg,.jpeg,.png,.mp4,.mov,"
    "message/rfc822,application/pdf,"
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document,"
    "application/msword,application/vnd.ms-outlook,"
    "image/jpeg,image/png,video/mp4,video/quicktime"
)
RECEIPT_TOKEN = "23f51bedec61438f9e284c292be06b9d"
ANTIFORGERY_TOKEN = (
    "CfDJ8AAAAAAAAAAAAAAAAAAAAAB8NRR7hNIQb-OmJmmBFSD4rJJHTDIiNb3jCHH727gEL9dmYQ9i"
    "5REzE9CQFm_d_K1_50MMrKzcp2sV0RzhWo61T91r0wUTXnsE76ZgcJUrStvt6x6YKUrALD9hokHoXrM"
)

AB_SUMMARY = (
    "Initial Upload screen (/Upload and /Upload?caseId=…): choose Design A, B, C, D or E "
    "to replace the floating 760px single-column picker and frame the Case destination."
)

DESIGN_META: dict[str, tuple[str, str, str]] = {
    "a": (
        "UB1",
        "Design A · Split workbench",
        "Design A (Split workbench): permanent 2-pane .pane-layout with drop zone + limit "
        "fact strip on the left and a live Selected files queue pane + action footer on the right.",
    ),
    "b": (
        "UB2",
        "Design B · Panel & format guide",
        "Design B (Structured panel & format guide): .panel workspace pairing the drop well "
        "with a 310px Accepted formats reference card and, on Case upload, a top Case identity ribbon.",
    ),
    "c": (
        "UB3",
        "Design C · Staging ledger",
        "Design C (Intake staging ledger): compact horizontal drop & pick bar over a "
        "full-width .table-wrap staging ledger with File, Kind & size, Destination and Remove columns.",
    ),
    "d": (
        "UB4",
        "Design D · Destination-first split",
        "Design D (Destination-first split): 350px left context .panel for target Case / "
        "routing rules and 2×2 batch limits beside a right-hand Choose & review files .panel.",
    ),
    "e": (
        "UB5",
        "Design E · Focused record sheet",
        "Design E (Focused record sheet): full-width .record sheet with dark .record-head header, "
        "4px .record-accent stripe, and a clean full-bleed drop zone with zero redundant copy "
        "(Selected files and the Upload action bar appear only once files are chosen).",
    ),
}


@presets("upload-a-case", "upload-b-case", "upload-c-case", "upload-d-case", "upload-e-case")
def seed_live_declared_case(body: Tag, state: dict) -> None:
    """Seed the exact live Upload.cshtml lines 42-49 DeclaredCaseId + _UploadDestinationCard markup."""
    title = body.select_one("form.up-select .up-select-title")
    if title is None or body.select_one("[data-upload-declared]") is not None:
        return
    declared = Ctx.html(
        '<div class="up-declared" data-upload-declared>'
        '<p class="up-eyebrow">Adding to</p>'
        '<div class="up-final-destination" data-upload-destination>'
        f'<strong class="mono">{CASE_REF}</strong>'
        f"<p>{CASE_PERSON}</p>"
        f"<p>{CASE_PRINCIPAL}</p>"
        f'<span class="status status--blue">{CASE_STAGE}</span>'
        "</div>"
        "</div>"
    )
    hidden = Ctx.html(
        f'<input id="DeclaredCaseId" name="DeclaredCaseId" type="hidden" value="{CASE_ID}" />'
    )
    title.insert_after(declared)
    title.insert_after(hidden)


def _hidden_inputs(case_upload: bool) -> str:
    declared = (
        f'<input id="DeclaredCaseId" name="DeclaredCaseId" type="hidden" value="{CASE_ID}" />'
        if case_upload
        else ""
    )
    return (
        '<input type="hidden" data-val="true" '
        'data-val-required="The ExternalReceiptToken field is required." '
        f'id="ExternalReceiptToken" name="ExternalReceiptToken" value="{RECEIPT_TOKEN}" />'
        f"{declared}"
        f'<input name="__RequestVerificationToken" type="hidden" value="{ANTIFORGERY_TOKEN}" />'
    )


def _error_alert() -> str:
    return (
        '<div class="up-alert up-alert--error" role="alert" tabindex="-1" hidden data-select-errors>'
        '<svg class="icon" aria-hidden="true"><use href="#icon-alert-circle"></use></svg>'
        "<div>"
        '<strong data-select-error-title>Check the selected files</strong>'
        "<div data-select-error-list></div>"
        "</div>"
        "</div>"
    )


def _drop_box(extra_class: str = "") -> str:
    cls = f"up-drop {extra_class}".strip()
    return (
        f'<div class="{cls}" data-drop>'
        '<span class="up-drop-badge" aria-hidden="true">'
        '<svg class="icon" aria-hidden="true"><use href="#icon-upload"></use></svg>'
        "</span>"
        '<h2 data-drop-heading>Drop files here</h2>'
        "<p>Images, documents, emails and video<br />"
        "JPG, JPEG, PNG, PDF, DOC, DOCX, EML, MSG, MP4 or MOV</p>"
        f'<input type="file" multiple class="up-file-input" accept="{ACCEPT_ATTR}" '
        'data-val="true" data-val-required="The Upload field is required." id="Upload" name="Upload" />'
        '<label class="btn btn--primary" data-select-choose for="Upload">'
        '<svg class="icon" aria-hidden="true"><use href="#icon-plus"></use></svg>'
        "<span>Choose files</span>"
        "</label>"
        "</div>"
    )


def _back_to_case_btn(extra_class: str = "") -> str:
    cls = f"btn {extra_class}".strip()
    return (
        f'<a class="{cls}" href="{CASE_HREF}" data-upload-back-case>'
        '<svg class="icon" aria-hidden="true"><use href="#icon-arrow-left"></use></svg>'
        f"<span>Back to {CASE_REF}</span>"
        "</a>"
    )


def _action_buttons() -> str:
    return (
        '<div class="button-row">'
        '<button type="reset" class="btn">Clear</button>'
        '<button type="submit" class="btn btn--primary" data-select-submit data-busy-label="Uploading…">'
        '<span data-select-submit-label>Upload 1 file</span>'
        '<svg class="icon" aria-hidden="true"><use href="#icon-arrow-right"></use></svg>'
        "</button>"
        "</div>"
    )


def _design_switcher_bar(design: str, case_upload: bool) -> str:
    tabs = []
    labels = [
        ("a", "A · Split workbench"),
        ("b", "B · Panel & format guide"),
        ("c", "C · Staging ledger"),
        ("d", "D · Destination-first split"),
        ("e", "E · Focused record sheet"),
    ]
    suffix = "-case" if case_upload else ""
    for d_key, d_label in labels:
        target_state = f"upload-{d_key}{suffix}"
        pressed = "true" if d_key == design else "false"
        tabs.append(
            f'<button type="button" class="up-design-pill" '
            f'data-upload-switch-state="{target_state}" aria-pressed="{pressed}">'
            f"{d_label}</button>"
        )
    rail_state = f"upload-{design}"
    case_state = f"upload-{design}-case"
    rail_pressed = "false" if case_upload else "true"
    case_pressed = "true" if case_upload else "false"
    return (
        '<nav class="up-design-bar" aria-label="Upload design options" data-v42-demo>'
        '<div class="up-design-group">'
        '<span class="up-design-label">v42 Upload layout</span>'
        f'<div class="up-design-pills" role="group" aria-label="Choose Upload design">{"".join(tabs)}</div>'
        "</div>"
        '<div class="up-design-right">'
        '<div class="up-design-group">'
        '<span class="up-design-label">Entry</span>'
        '<div class="up-design-pills" role="group" aria-label="Entry point">'
        f'<button type="button" class="up-design-pill" data-upload-switch-state="{rail_state}" '
        f'aria-pressed="{rail_pressed}">Left-nav (/Upload)</button>'
        f'<button type="button" class="up-design-pill" data-upload-switch-state="{case_state}" '
        f'aria-pressed="{case_pressed}">Case ({CASE_REF})</button>'
        "</div>"
        "</div>"
        '<div class="up-design-group">'
        '<span class="up-design-label">Preview</span>'
        '<div class="up-design-pills" role="group" aria-label="Sample files preview">'
        '<button type="button" class="up-design-pill" data-upload-sample-toggle="0" aria-pressed="true">Empty</button>'
        '<button type="button" class="up-design-pill" data-upload-sample-toggle="1" aria-pressed="false">3 sample files</button>'
        "</div>"
        "</div>"
        "</div>"
        "</nav>"
    )


def _build_design_a(case_upload: bool) -> tuple[str, str]:
    if case_upload:
        header = (
            '<header class="page-header up-head">'
            '<div class="page-title">'
            f'<p class="eyebrow">Adding to {CASE_REF}</p>'
            "<h1>Upload</h1>"
            "</div>"
            f'<div class="page-actions">{_back_to_case_btn()}</div>'
            "</header>"
        )
        pane_badge = f'<span class="status status--navy">Adding to {CASE_REF}</span>'
        declared_banner = (
            '<div class="up-a-case-banner" data-upload-declared>'
            '<div class="up-a-case-main">'
            '<p class="up-eyebrow">Adding to</p>'
            '<div class="up-final-destination" data-upload-destination>'
            f'<strong class="mono"><a href="{CASE_HREF}">{CASE_REF}</a></strong>'
            f"<p>{CASE_PERSON}</p>"
            f"<p>{CASE_PRINCIPAL}</p>"
            f'<span class="status status--blue">{CASE_STAGE}</span>'
            "</div>"
            "</div>"
            f'<p class="up-a-case-caption">{APPEAR_UNDER_FILES}</p>'
            "</div>"
        )
    else:
        header = (
            '<header class="page-header up-head">'
            '<div class="page-title">'
            '<p class="eyebrow">Add files to Pegasus</p>'
            "<h1>Upload</h1>"
            "</div>"
            '<div class="page-actions">'
            '<span class="up-meta">20 files maximum · 100.0 MB per file · 200.0 MB per upload</span>'
            "</div>"
            "</header>"
        )
        pane_badge = '<span class="meta">Step 1 of 2 · Store files</span>'
        declared_banner = ""

    surface = (
        '<div class="up-surface up-v42-root up-v42--a" data-upload-design="a">'
        '<div class="up-workspace is-choosing" data-upload-select '
        'data-max-files="20" data-max-bytes="100000000" data-max-total="200000000">'
        '<form method="post" enctype="multipart/form-data" class="up-v42-form pane-layout up-a-workbench" data-upload-form>'
        f"{_hidden_inputs(case_upload)}"
        '<section class="pane up-a-pane-left" aria-labelledby="up-a-choose-title">'
        '<header class="pane-head">'
        '<h2 id="up-a-choose-title" data-select-heading>Choose the files for this upload</h2>'
        f"{pane_badge}"
        "</header>"
        '<div class="pane-body up-a-left-body">'
        f"{declared_banner}"
        f"{_error_alert()}"
        f"{_drop_box('up-a-drop')}"
        '<dl class="fact-grid up-a-facts">'
        '<div class="fact"><dt>Maximum files</dt><dd>20 files maximum</dd></div>'
        '<div class="fact"><dt>Single file limit</dt><dd>100.0 MB per file</dd></div>'
        '<div class="fact"><dt>Total upload limit</dt><dd>200.0 MB per upload</dd></div>'
        "</dl>"
        "</div>"
        "</section>"
        '<section class="pane up-a-pane-right up-v42-keep-visible" aria-labelledby="up-selected-title" data-select-files>'
        '<header class="pane-head">'
        '<h2 id="up-selected-title">Selected files</h2>'
        '<span class="meta tabular" data-select-count data-empty-text="0 files · 0.0 MB">0 files · 0.0 MB</span>'
        "</header>"
        '<div class="pane-body up-a-right-body">'
        '<div class="up-empty-slate" data-select-empty>'
        '<span class="up-empty-icon" aria-hidden="true">'
        '<svg class="icon" aria-hidden="true"><use href="#icon-file-text"></use></svg>'
        "</span>"
        "<h3>No files selected yet</h3>"
        "<p>Choose or drop files on the left to review their names, sizes and types before uploading.</p>"
        "</div>"
        '<ul class="up-file-list" data-select-list role="status" aria-live="polite"></ul>'
        "</div>"
        '<footer class="pane-foot up-select-actions up-v42-keep-visible" data-select-actions>'
        '<p data-select-summary data-empty-text="No files selected">No files selected</p>'
        f"{_action_buttons()}"
        "</footer>"
        "</section>"
        "</form>"
        "</div>"
        "</div>"
    )
    return header, surface


def _build_design_b(case_upload: bool) -> tuple[str, str]:
    if case_upload:
        header = (
            '<header class="page-header up-head">'
            '<div class="page-title">'
            f'<p class="eyebrow">Adding to {CASE_REF}</p>'
            "<h1>Upload</h1>"
            "</div>"
            f'<div class="page-actions">{_back_to_case_btn()}</div>'
            "</header>"
        )
        case_ribbon = (
            '<section class="panel up-b-case-ribbon" data-upload-declared aria-label="Target Case">'
            '<div class="up-b-ribbon-grid" data-upload-destination>'
            '<div class="ribbon-item">'
            '<span class="ribbon-label">Adding to</span>'
            f'<strong class="ribbon-value mono"><a href="{CASE_HREF}">{CASE_REF}</a></strong>'
            "</div>"
            '<div class="ribbon-item">'
            '<span class="ribbon-label">Registration · Claimant</span>'
            f'<span class="ribbon-value">{CASE_PERSON}</span>'
            "</div>"
            '<div class="ribbon-item">'
            '<span class="ribbon-label">Principal</span>'
            f'<span class="ribbon-value">{CASE_PRINCIPAL}</span>'
            "</div>"
            '<div class="ribbon-item">'
            '<span class="ribbon-label">Stage</span>'
            f'<span class="ribbon-value"><span class="status status--blue">{CASE_STAGE}</span></span>'
            "</div>"
            '<div class="ribbon-item">'
            '<span class="ribbon-label">Filing destination</span>'
            f'<span class="ribbon-value muted">{APPEAR_UNDER_FILES}</span>'
            "</div>"
            "</div>"
            "</section>"
        )
    else:
        header = (
            '<header class="page-header up-head">'
            '<div class="page-title">'
            '<p class="eyebrow">Add files to Pegasus</p>'
            "<h1>Upload</h1>"
            "</div>"
            "</header>"
        )
        case_ribbon = ""

    surface = (
        '<div class="up-surface up-v42-root up-v42--b" data-upload-design="b">'
        '<div class="up-workspace is-choosing" data-upload-select '
        'data-max-files="20" data-max-bytes="100000000" data-max-total="200000000">'
        '<form method="post" enctype="multipart/form-data" class="up-v42-form up-b-stack" data-upload-form>'
        f"{_hidden_inputs(case_upload)}"
        f"{case_ribbon}"
        '<section class="panel up-b-panel">'
        '<header class="panel-head up-b-panel-head">'
        "<div>"
        '<p class="eyebrow">Add files to Pegasus</p>'
        '<h2 data-select-heading>Choose the files for this upload</h2>'
        "</div>"
        '<div class="up-b-limits-pills">'
        '<span class="up-limit-pill">20 files maximum</span>'
        '<span class="up-limit-pill">100.0 MB per file</span>'
        '<span class="up-limit-pill">200.0 MB per upload</span>'
        "</div>"
        "</header>"
        '<div class="panel-body up-b-body">'
        '<div class="up-b-main">'
        f"{_error_alert()}"
        f"{_drop_box('up-b-drop')}"
        '<section class="up-b-files up-v42-keep-visible" aria-labelledby="up-selected-title" data-select-files>'
        '<header class="up-section-head">'
        '<h2 id="up-selected-title">Selected files</h2>'
        '<span class="tabular" data-select-count data-empty-text="0 files · 0.0 MB">0 files · 0.0 MB</span>'
        "</header>"
        '<div class="up-b-empty-row" data-select-empty>'
        "No files selected yet — choose or drop files above to stage them for upload."
        "</div>"
        '<ul class="up-file-list" data-select-list role="status" aria-live="polite"></ul>'
        "</section>"
        "</div>"
        '<aside class="up-b-guide" aria-label="Accepted file formats">'
        '<div class="up-b-guide-head">'
        "<h3>Accepted formats</h3>"
        "<p>Images, documents, emails and video</p>"
        "</div>"
        '<div class="up-b-format-list">'
        '<div class="up-b-format-item">'
        '<span class="up-b-format-icon"><svg class="icon" aria-hidden="true"><use href="#icon-image"></use></svg></span>'
        '<div><strong>Images</strong><small class="mono">JPG, JPEG, PNG</small></div>'
        "</div>"
        '<div class="up-b-format-item">'
        '<span class="up-b-format-icon"><svg class="icon" aria-hidden="true"><use href="#icon-file-text"></use></svg></span>'
        '<div><strong>Documents</strong><small class="mono">PDF, DOC, DOCX</small></div>'
        "</div>"
        '<div class="up-b-format-item">'
        '<span class="up-b-format-icon"><svg class="icon" aria-hidden="true"><use href="#icon-mail"></use></svg></span>'
        '<div><strong>Emails</strong><small class="mono">EML, MSG</small></div>'
        "</div>"
        '<div class="up-b-format-item">'
        '<span class="up-b-format-icon"><svg class="icon" aria-hidden="true"><use href="#icon-file"></use></svg></span>'
        '<div><strong>Video</strong><small class="mono">MP4, MOV</small></div>'
        "</div>"
        "</div>"
        '<div class="up-b-guide-foot">'
        "<p>JPG, JPEG, PNG, PDF, DOC, DOCX, EML, MSG, MP4 or MOV</p>"
        "<p>20 files maximum · 100.0 MB per file · 200.0 MB per upload</p>"
        "</div>"
        "</aside>"
        "</div>"
        '<footer class="panel-foot up-select-actions up-v42-keep-visible" data-select-actions>'
        '<p data-select-summary data-empty-text="No files selected">No files selected</p>'
        f"{_action_buttons()}"
        "</footer>"
        "</section>"
        "</form>"
        "</div>"
        "</div>"
    )
    return header, surface


def _build_design_c(case_upload: bool) -> tuple[str, str]:
    header = (
        '<header class="page-header up-head">'
        '<div class="page-title">'
        f'<p class="eyebrow">{"Adding to " + CASE_REF if case_upload else "Add files to Pegasus"}</p>'
        "<h1>Upload</h1>"
        "</div>"
        '<div class="page-actions">'
        f'{_back_to_case_btn() if case_upload else """<span class="up-meta">20 files maximum · 100.0 MB per file · 200.0 MB per upload</span>"""}'
        "</div>"
        "</header>"
    )
    if case_upload:
        case_strip = (
            '<div class="presence-strip up-c-case-strip" data-upload-declared>'
            '<div class="up-c-case-info" data-upload-destination>'
            '<span class="up-eyebrow">Adding to</span>'
            f'<strong class="mono"><a href="{CASE_HREF}">{CASE_REF}</a></strong>'
            f"<span>{CASE_PERSON}</span>"
            '<span class="up-c-sep">·</span>'
            f"<span>{CASE_PRINCIPAL}</span>"
            f'<span class="status status--blue">{CASE_STAGE}</span>'
            f'<span class="up-c-dest-note">{APPEAR_UNDER_FILES}</span>'
            "</div>"
            "</div>"
        )
        dest_col = f"{CASE_REF} · Files"
    else:
        case_strip = ""
        dest_col = "Chosen after upload"

    surface = (
        '<div class="up-surface up-v42-root up-v42--c" data-upload-design="c">'
        '<div class="up-workspace is-choosing" data-upload-select '
        'data-max-files="20" data-max-bytes="100000000" data-max-total="200000000">'
        '<form method="post" enctype="multipart/form-data" class="up-v42-form panel up-c-panel" data-upload-form>'
        f"{_hidden_inputs(case_upload)}"
        '<header class="pane-head up-c-head">'
        "<div>"
        '<p class="eyebrow">Add files to Pegasus</p>'
        '<h2 data-select-heading>Choose the files for this upload</h2>'
        "</div>"
        '<div class="up-c-head-limits">'
        "<span>20 files maximum</span>"
        "<span>·</span>"
        "<span>100.0 MB per file</span>"
        "<span>·</span>"
        "<span>200.0 MB per upload</span>"
        "</div>"
        "</header>"
        f"{case_strip}"
        f"{_error_alert()}"
        '<div class="up-drop up-c-dropbar" data-drop>'
        '<span class="up-c-drop-icon" aria-hidden="true">'
        '<svg class="icon" aria-hidden="true"><use href="#icon-upload"></use></svg>'
        "</span>"
        '<div class="up-c-drop-copy">'
        '<h2 data-drop-heading>Drop files here</h2>'
        "<p>Images, documents, emails and video · JPG, JPEG, PNG, PDF, DOC, DOCX, EML, MSG, MP4 or MOV</p>"
        "</div>"
        '<div class="up-c-drop-cta">'
        f'<input type="file" multiple class="up-file-input" accept="{ACCEPT_ATTR}" '
        'data-val="true" data-val-required="The Upload field is required." id="Upload" name="Upload" />'
        '<label class="btn btn--primary" data-select-choose for="Upload">'
        '<svg class="icon" aria-hidden="true"><use href="#icon-plus"></use></svg>'
        "<span>Choose files</span>"
        "</label>"
        "</div>"
        "</div>"
        '<section class="up-c-ledger up-v42-keep-visible" aria-labelledby="up-selected-title" data-select-files>'
        '<div class="up-c-ledger-head" role="presentation">'
        '<span id="up-selected-title">Selected files</span>'
        "<span>Destination</span>"
        '<span class="right">Remove</span>'
        "</div>"
        '<div class="up-c-ledger-empty" data-select-empty>'
        '<svg class="icon" aria-hidden="true"><use href="#icon-file-text"></use></svg>'
        "<div>"
        "<strong>No files staged in this upload</strong>"
        "<p>Drop files onto the bar above or click Choose files to stage up to 20 files (200.0 MB total).</p>"
        "</div>"
        "</div>"
        f'<ul class="up-file-list up-c-file-list" data-select-list data-dest-col="{dest_col}" '
        'role="status" aria-live="polite"></ul>'
        "</section>"
        '<footer class="panel-foot up-select-actions up-v42-keep-visible" data-select-actions>'
        '<div class="cluster">'
        '<span class="tabular" data-select-count data-empty-text="0 of 20 files · 0.0 MB">0 of 20 files · 0.0 MB</span>'
        '<span class="sr-only" data-select-summary></span>'
        "</div>"
        f"{_action_buttons()}"
        "</footer>"
        "</form>"
        "</div>"
        "</div>"
    )
    return header, surface


def _build_design_d(case_upload: bool) -> tuple[str, str]:
    header = (
        '<header class="page-header up-head">'
        '<div class="page-title">'
        f'<p class="eyebrow">{"Adding to " + CASE_REF if case_upload else "Add files to Pegasus"}</p>'
        "<h1>Upload</h1>"
        "</div>"
        f'<div class="page-actions">{_back_to_case_btn() if case_upload else ""}</div>'
        "</header>"
    )
    if case_upload:
        left_card = (
            '<aside class="panel context-card up-d-left" aria-label="Upload destination and limits">'
            '<header class="panel-head">'
            "<h2>Adding to</h2>"
            f'<span class="status status--blue">{CASE_STAGE}</span>'
            "</header>"
            '<div class="panel-body stack">'
            '<div class="up-d-case-card" data-upload-declared>'
            '<p class="up-eyebrow">Target Case</p>'
            '<div class="up-final-destination" data-upload-destination>'
            f'<strong class="mono"><a href="{CASE_HREF}">{CASE_REF}</a></strong>'
            f"<p>{CASE_PERSON}</p>"
            f"<p>{CASE_PRINCIPAL}</p>"
            f'<span class="status status--blue">{CASE_STAGE}</span>'
            "</div>"
            f'<p class="up-d-case-rule">{APPEAR_UNDER_FILES}</p>'
            f'{_back_to_case_btn("up-d-back-btn")}'
            "</div>"
            '<dl class="fact-grid up-d-facts">'
            '<div class="fact"><dt>Maximum files</dt><dd>20 files maximum</dd></div>'
            '<div class="fact"><dt>Per file</dt><dd>100.0 MB per file</dd></div>'
            '<div class="fact"><dt>Total upload</dt><dd>200.0 MB per upload</dd></div>'
            '<div class="fact"><dt>Accepted kinds</dt><dd>Images, documents, emails and video</dd></div>'
            "</dl>"
            '<p class="up-d-ext mono">JPG, JPEG, PNG, PDF, DOC, DOCX, EML, MSG, MP4 or MOV</p>'
            "</div>"
            "</aside>"
        )
    else:
        left_card = (
            '<aside class="panel context-card up-d-left" aria-label="Upload destination and limits">'
            '<header class="panel-head">'
            "<h2>Destination &amp; limits</h2>"
            '<span class="status status--neutral">Chosen on review</span>'
            "</header>"
            '<div class="panel-body stack">'
            '<div class="up-d-dest-box">'
            '<p class="up-eyebrow">Add files to Pegasus</p>'
            "<h3>Confirm Case after storage</h3>"
            "<p>Files are stored in a single upload batch first. On the next screen, review each file and confirm its Case destination.</p>"
            "</div>"
            '<dl class="fact-grid up-d-facts">'
            '<div class="fact"><dt>Maximum files</dt><dd>20 files maximum</dd></div>'
            '<div class="fact"><dt>Per file</dt><dd>100.0 MB per file</dd></div>'
            '<div class="fact"><dt>Total upload</dt><dd>200.0 MB per upload</dd></div>'
            '<div class="fact"><dt>Accepted kinds</dt><dd>Images, documents, emails and video</dd></div>'
            "</dl>"
            '<p class="up-d-ext mono">JPG, JPEG, PNG, PDF, DOC, DOCX, EML, MSG, MP4 or MOV</p>'
            "</div>"
            "</aside>"
        )

    surface = (
        '<div class="up-surface up-v42-root up-v42--d" data-upload-design="d">'
        '<div class="up-workspace is-choosing" data-upload-select '
        'data-max-files="20" data-max-bytes="100000000" data-max-total="200000000">'
        '<form method="post" enctype="multipart/form-data" class="up-v42-form up-d-split" data-upload-form>'
        f"{_hidden_inputs(case_upload)}"
        f"{left_card}"
        '<section class="panel up-d-right" aria-labelledby="up-d-choose-title">'
        '<header class="panel-head">'
        '<h2 id="up-d-choose-title" data-select-heading>Choose the files for this upload</h2>'
        '<span class="meta tabular" data-select-count data-empty-text="0 files · 0.0 MB">0 files · 0.0 MB</span>'
        "</header>"
        '<div class="panel-body stack">'
        f"{_error_alert()}"
        f"{_drop_box('up-d-drop')}"
        '<section class="up-d-files up-v42-keep-visible" aria-labelledby="up-selected-title" data-select-files>'
        '<header class="up-section-head">'
        '<h2 id="up-selected-title">Selected files</h2>'
        "</header>"
        '<div class="up-d-empty" data-select-empty>'
        "No files selected yet — choose or drop files above."
        "</div>"
        '<ul class="up-file-list" data-select-list role="status" aria-live="polite"></ul>'
        "</section>"
        "</div>"
        '<footer class="panel-foot up-select-actions up-v42-keep-visible" data-select-actions>'
        '<p data-select-summary data-empty-text="No files selected">No files selected</p>'
        f"{_action_buttons()}"
        "</footer>"
        "</section>"
        "</form>"
        "</div>"
        "</div>"
    )
    return header, surface


def _build_design_e(case_upload: bool) -> tuple[str, str]:
    header = (
        '<header class="page-header up-head up-e-page-head" hidden>'
        '<div class="page-title"><h1>Upload</h1></div>'
        "</header>"
    )
    if case_upload:
        record_head = (
            '<header class="record-head up-e-head" data-upload-declared>'
            '<span class="up-e-head-badge" aria-hidden="true">'
            '<svg class="icon" aria-hidden="true"><use href="#icon-upload"></use></svg>'
            "</span>"
            '<div data-upload-destination>'
            f'<h1>Upload · <a class="mono" href="{CASE_HREF}">{CASE_REF}</a></h1>'
            '<div class="record-identity">'
            f"<span><b>{CASE_PERSON}</b></span>"
            f"<span>{CASE_PRINCIPAL}</span>"
            f'<span class="status status--blue">{CASE_STAGE}</span>'
            "</div>"
            "</div>"
            f'{_back_to_case_btn("btn--dark")}'
            "</header>"
        )
    else:
        record_head = (
            '<header class="record-head up-e-head">'
            '<span class="up-e-head-badge" aria-hidden="true">'
            '<svg class="icon" aria-hidden="true"><use href="#icon-upload"></use></svg>'
            "</span>"
            "<div>"
            "<h1>Upload</h1>"
            "</div>"
            "</header>"
        )

    surface = (
        '<div class="up-surface up-v42-root up-v42--e" data-upload-design="e">'
        '<div class="up-workspace is-choosing" data-upload-select '
        'data-max-files="20" data-max-bytes="100000000" data-max-total="200000000">'
        '<form method="post" enctype="multipart/form-data" class="up-v42-form record up-e-sheet" data-upload-form>'
        f"{_hidden_inputs(case_upload)}"
        f"{record_head}"
        '<div class="record-accent"></div>'
        '<div class="record-body up-e-body">'
        '<span class="sr-only" data-select-heading>Choose the files for this upload</span>'
        f"{_error_alert()}"
        '<div class="up-drop up-e-drop" data-drop>'
        '<span class="up-drop-badge" aria-hidden="true">'
        '<svg class="icon" aria-hidden="true"><use href="#icon-upload"></use></svg>'
        "</span>"
        '<h2 data-drop-heading>Drop files here</h2>'
        f'<input type="file" multiple class="up-file-input" accept="{ACCEPT_ATTR}" '
        'data-val="true" data-val-required="The Upload field is required." id="Upload" name="Upload" />'
        '<label class="btn btn--primary" data-select-choose for="Upload">'
        '<svg class="icon" aria-hidden="true"><use href="#icon-plus"></use></svg>'
        "<span>Choose files</span>"
        "</label>"
        "</div>"
        '<section class="up-e-files" aria-labelledby="up-selected-title" hidden data-select-files>'
        '<header class="up-section-head">'
        '<h2 id="up-selected-title">Selected files</h2>'
        '<span class="tabular" data-select-count></span>'
        "</header>"
        '<ul class="up-file-list" data-select-list role="status" aria-live="polite"></ul>'
        "</section>"
        "</div>"
        '<footer class="record-bar up-e-foot up-select-actions" hidden data-select-actions>'
        '<p data-select-summary></p>'
        f'<div class="record-bar-end">{_action_buttons()}</div>'
        "</footer>"
        "</form>"
        "</div>"
        "</div>"
    )
    return header, surface

BUILDERS = {
    "a": _build_design_a,
    "b": _build_design_b,
    "c": _build_design_c,
    "d": _build_design_d,
    "e": _build_design_e,
}


@patch(
    "upload-a",
    "upload-b",
    "upload-c",
    "upload-d",
    "upload-e",
    "upload-a-case",
    "upload-b-case",
    "upload-c-case",
    "upload-d-case",
    "upload-e-case",
)
def apply_upload_design(ctx: Ctx) -> None:
    design = str(ctx.state.get("upload_design", "a")).lower()
    case_upload = bool(ctx.state.get("case_upload", False))
    change_id, _, summary = DESIGN_META[design]

    old_head = ctx.one("header.page-header.up-head")
    old_surface = ctx.one("div.up-surface")
    if old_head is None or old_surface is None:
        return

    header_html, surface_html = BUILDERS[design](case_upload)
    switcher = Ctx.html(_design_switcher_bar(design, case_upload))
    new_head = Ctx.html(header_html)
    new_surface = Ctx.html(surface_html)

    old_head.insert_before(switcher)
    old_head.replace_with(new_head)
    old_surface.replace_with(new_surface)

    ctx.mark(new_surface, change_id, summary)
    ctx.mark(new_surface, "AB", AB_SUMMARY)
