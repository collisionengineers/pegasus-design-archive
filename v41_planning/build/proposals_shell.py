"""S: shell, sign-in, consent, errors, release notes.

S1-S4 live in the app shell, so they are registered for every app page ("*app").
S5-S7 are single captured pages. Each patch does nothing when its element is not in
the capture, and none writes a new sentence.
"""
from __future__ import annotations

import re

from bs4 import NavigableString

from proposals_v41 import EVERY_APP_PAGE, Ctx, patch

S1 = "Release notes, Report a problem and Change password move into the Account dialog body; the foot keeps Close and Sign out."
S2 = "Mark all read moves to the Notifications dialog head."
S3 = "The command palette's Cases icon matches the rail's Cases icon."
S4 = "The utility bar's freshness line goes; the rail health line keeps the one clock."
S5 = ("The raw scope identifiers go from the connector request; the descriptions stay. One scope's description (the intake scope's, not requested "
      "here) contains the word intake, which the interface does not use; its wording is left to Stage 2 PR 1 and is put to the operator when that PR is drafted.")
S6 = "Change password: the submit button sits directly in the form, full width as on sign-in, and each password field gets the Show/Hide control."
S7 = "The Not found page's one action is the primary button."


@patch(EVERY_APP_PAGE)
def s1_account_dialog_actions_in_body(ctx: Ctx) -> None:
    dialog = ctx.one('[data-dialog="account-dialog"]')
    if dialog is None:
        return
    body, foot = dialog.select_one(".dialog-body"), dialog.select_one(".dialog-foot")
    if body is None or foot is None:
        return
    actions = [
        foot.select_one('a[href="/ReleaseNotes"]'),
        foot.select_one('button[data-dialog-open="problem-dialog"]'),
        foot.select_one('a[href="/Account/PasswordChange"]'),
    ]
    actions = [a for a in actions if a is not None]
    if not actions:
        return
    row = ctx.html('<div class="button-row"></div>')
    for action in actions:
        row.append(action.extract())
    body.append(row)
    ctx.mark(row, "S1", S1)


@patch(EVERY_APP_PAGE)
def s2_mark_all_read_in_the_head(ctx: Ctx) -> None:
    dialog = ctx.one('[data-dialog="notifications-dialog"]')
    if dialog is None:
        return
    head = dialog.select_one(".dialog-head")
    form = dialog.select_one('.dialog-foot form[action*="MarkAllRead"]')
    close = head.select_one(".dialog-close") if head is not None else None
    if head is None or form is None or close is None:
        return
    classes = [c for c in form.get("class", []) if c != "left"]
    if classes:
        form["class"] = classes
    else:
        del form["class"]
    close.insert_before(form.extract())
    ctx.mark(form, "S2", S2)
    ctx.style(
        '[data-dialog="notifications-dialog"] .dialog-head form{margin-left:auto}',
        "S2", S2,
    )


@patch(EVERY_APP_PAGE)
def s3_command_palette_cases_icon(ctx: Ctx) -> None:
    result = ctx.one('.command-result[data-route="/Cases"]')
    use = result.select_one("use") if result is not None else None
    if use is None:
        return
    use["href"] = "#icon-list-checks"
    ctx.mark(result, "S3", S3)


@patch(EVERY_APP_PAGE)
def s4_utility_freshness_goes(ctx: Ctx) -> None:
    ctx.remove(ctx.one(".utility-bar .utility-freshness"), "S4", S4)


@patch("consent")
def s5_consent_scope_identifiers_go(ctx: Ctx) -> None:
    for code in ctx.all("ul.plain li code"):
        item = code.parent
        code.decompose()
        # The description keeps its words; only the dash that joined it to the identifier goes.
        for node in list(item.contents):
            if isinstance(node, NavigableString) and node.strip():
                node.replace_with(re.sub(r"^\s*[—–-]\s*", "", str(node)))
                break
        ctx.mark(item, "S5", S5)


@patch("auth-password-forced", "auth-password-voluntary")
def s6_password_change_button_and_reveal(ctx: Ctx) -> None:
    form = ctx.one("main form.stack")
    if form is None:
        return
    for field in form.select(".field"):
        field_input = field.select_one('input[type="password"]')
        if field_input is None or field_input.parent.get("class") == ["password-control"]:
            continue
        wrapper = ctx.html('<div class="password-control"></div>')
        field_input.insert_before(wrapper)
        wrapper.append(field_input.extract())
        wrapper.append(ctx.html(
            f'<button type="button" class="password-reveal" data-password-reveal '
            f'aria-controls="{field_input.get("id", "")}" aria-pressed="false" '
            f'aria-label="Show password">Show</button>'
        ))
        ctx.mark(wrapper, "S6", S6)
    row = form.select_one(":scope > .button-row")
    submit = row.select_one('button[type="submit"]') if row is not None else None
    if row is not None and submit is not None:
        row.replace_with(submit.extract())
        ctx.mark(submit, "S6", S6)


@patch("status-404")
def s7_not_found_primary_action(ctx: Ctx) -> None:
    action = ctx.one(".auth-card .button-row a.btn")
    if action is None:
        return
    classes = action.get("class", [])
    if "btn--primary" not in classes:
        action["class"] = classes + ["btn--primary"]
    ctx.mark(action, "S7", S7)
