#!/usr/bin/env python3
"""Build self-contained offline HTML mockups for v41 (Full-Application UX Audit).

Produces:
  - pegasus_v41.html                 (unified single-file interactive mockup of the entire application, 27 states)
  - pegasus_shell_v41.html           (all 27 states, opening on Auth & Shell by default)
  - pegasus_case_workspace_v41.html  (all 27 states, opening on Case Workspace by default)

Zero external URLs: all live CSS, woff2 fonts, brand PNGs, sample vehicle photos, and
the Lucide SVG sprite sheet are inlined into each HTML file. Each state activates only
site.css + its own @section Styles stylesheet(s) so there is zero cross-page CSS bleed.
"""
from __future__ import annotations

import base64
import html as html_mod
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
PEGASUS = pathlib.Path(r"C:\Users\PC\Documents\GitHub\pegasus")
WWWROOT = PEGASUS / "src" / "Pegasus.Web" / "wwwroot"
SPRITE_PATH = PEGASUS / "src" / "Pegasus.Web" / "Pages" / "Shared" / "_LucideSprite.cshtml"
V39_CAPTURED = HERE.parent.parent / "v39_planning" / "current" / "captured"
V36_CAPTURED = HERE.parent.parent / "v36_planning" / "current" / "captured"


def read_text(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


def asset_bytes(rel: str) -> bytes:
    return (WWWROOT / rel.lstrip("/")).read_bytes()


def inline_font_urls(css: str) -> str:
    def repl(m: re.Match[str]) -> str:
        raw = m.group(1).strip().strip("'\"")
        if raw.startswith("data:"):
            return m.group(0)
        rel = raw.lstrip("/")
        if rel.startswith("../"):
            rel = rel[3:]
        cand = WWWROOT / rel
        if not cand.exists():
            return m.group(0)
        b64 = base64.b64encode(cand.read_bytes()).decode("ascii")
        mime = "font/woff2" if cand.suffix == ".woff2" else "image/png"
        return f'url("data:{mime};base64,{b64}")'

    return re.sub(r"url\(([^)]+)\)", repl, css)


def css_with_fonts(name: str) -> str:
    return inline_font_urls(read_text(WWWROOT / "css" / name))


def E(s: str) -> str:
    return html_mod.escape(s, quote=True)


MARK_B64 = base64.b64encode(asset_bytes("images/pegasus-mark-refined-128.png")).decode("ascii")
MARK_DATA_URI = f"data:image/png;base64,{MARK_B64}"
# Strip Razor @* ... *@ comments from _LucideSprite.cshtml so raw comment text never renders in HTML
SPRITE_HTML = re.sub(r"@\*[\s\S]*?\*@", "", read_text(SPRITE_PATH)).strip()

TILE_PATHS = sorted((V36_CAPTURED / "images").glob("*.png"))
TILE_URIS = [
    f"data:image/png;base64,{base64.b64encode(p.read_bytes()).decode('ascii')}"
    for p in TILE_PATHS[:4]
]
if not TILE_URIS:
    TILE_URIS = [MARK_DATA_URI]


# ---------------------------------------------------------------------------
# Exact Live Shell & Chrome Builders (_Layout.cshtml, _LayoutAuth.cshtml, _AdminNav.cshtml)
# ---------------------------------------------------------------------------

def render_rail(active_nav: str = "work-centre") -> str:
    def nav_link(key: str, href: str, icon: str, label: str, count: str = "") -> str:
        cur = ' aria-current="page"' if key == active_nav else ""
        badge = f'<span class="nav-count" aria-label="{E(count)} outstanding">{E(count)}</span>' if count else ""
        return (
            f'<a class="nav-link"{cur} href="{href}">'
            f'<svg class="icon" aria-hidden="true"><use href="#icon-{icon}" /></svg>'
            f'<span>{E(label)}</span>{badge}</a>'
        )

    return f"""
    <header class="app-rail">
      <a class="brand" aria-label="Pegasus home" href="#work-centre">
        <img src="{MARK_DATA_URI}" alt="" aria-hidden="true" />
        <span class="brand-copy"><strong>PEGASUS</strong><span>Case management</span></span>
      </a>
      <nav class="primary-nav" aria-label="Primary">
        <div class="nav-label">Work</div>
        {nav_link("work-centre", "#work-centre", "layout-dashboard", "Work Centre")}
        {nav_link("inbox", "#inbox", "inbox", "Inbox", "6")}
        {nav_link("upload", "#upload", "upload", "Upload")}
        {nav_link("cases", "#cases", "list-checks", "Cases", "48")}
        {nav_link("search", "#search", "search", "Search")}
        <div class="nav-label">Manage</div>
        {nav_link("admin", "#admin-accounts", "settings", "Administration")}
      </nav>
      <div class="rail-spacer"></div>
      <button type="button" class="rail-collapse" data-rail-toggle aria-expanded="true" aria-label="Collapse navigation"
              data-label-collapse="Collapse navigation" data-label-expand="Expand navigation">
        <svg class="icon" aria-hidden="true"><use href="#icon-chevron-left" /></svg>
        <span>Collapse</span>
      </button>
      <div class="rail-health" data-rail-health>
        <div class="rail-health-line"><span class="health-dot"></span><span>Current · 14:32</span></div>
      </div>
      <div class="rail-user" role="group" aria-label="User">
        <span class="avatar" aria-hidden="true">AJ</span>
        <div><strong>alex</strong><small>Administrator</small></div>
        <button type="button" class="icon-button rail-account" data-dialog-open="account-dialog" aria-label="Account menu">
          <svg class="icon" aria-hidden="true"><use href="#icon-more-horizontal" /></svg>
        </button>
      </div>
    </header>
    """


def render_utility_bar(crumb: str = "", hide_new_case: bool = False) -> str:
    new_case_btn = (
        ""
        if hide_new_case
        else (
            '<a class="btn btn--primary" href="#create-case" data-utility-new-case>'
            '<svg class="icon" aria-hidden="true"><use href="#icon-plus" /></svg>'
            '<span>New case</span></a>'
        )
    )
    return f"""
    <section class="utility-bar" aria-label="Utility bar">
      <div class="utility-freshness" data-v41-dup-freshness data-v41-change="f05 (C)">
        <span class="health-dot"></span><span>Current · 14:32</span>
      </div>
      <form class="utility-search" role="search" method="get" action="#search" data-v41-global-search data-v41-change="f04 (B)">
        <label class="sr-only" for="global-search">Search Pegasus</label>
        <svg class="icon" aria-hidden="true"><use href="#icon-search" /></svg>
        <input id="global-search" type="search" name="query" data-command-input aria-label="Search Pegasus"
               placeholder="Search cases, references or people" autocomplete="off" />
        <span class="shortcut-hint" aria-hidden="true">Ctrl K</span>
      </form>
      <div class="utility-actions">
        {new_case_btn}
        <span class="bell-wrap">
          <button type="button" class="icon-button utility-bell" data-dialog-open="notifications-dialog" aria-label="Notifications · 2 unread">
            <svg class="icon" aria-hidden="true"><use href="#icon-bell" /></svg>
          </button>
          <span class="bell-count" aria-hidden="true">2</span>
        </span>
        <button type="button" class="icon-button utility-account" data-dialog-open="account-dialog" aria-label="Account menu">
          <svg class="icon" aria-hidden="true"><use href="#icon-more-horizontal" /></svg>
        </button>
      </div>
    </section>
    """


def render_app_shell(active_nav: str, content_html: str, hide_new_case: bool = False) -> str:
    return f"""
    <a class="skip-link" href="#main-content">Skip to main content</a>
    <div class="app-shell" data-app-shell>
      {render_rail(active_nav)}
      <div class="app-column">
        {render_utility_bar(hide_new_case=hide_new_case)}
        <main id="main-content" class="app-main" tabindex="-1">
          <div class="content">
            {content_html}
          </div>
        </main>
      </div>
    </div>
    """


def render_external_shell(panel_html: str) -> str:
    return f"""
    <a class="skip-link" href="#main-content">Skip to main content</a>
    <div class="external-shell">
      <aside class="auth-identity" aria-label="Organisation">
        <div class="auth-brand">
          <img src="{MARK_DATA_URI}" alt="" width="96" height="96" />
          <div class="brand-copy">
            <strong>PEGASUS</strong>
            <span>Case management</span>
          </div>
        </div>
        <p class="auth-company">Collision Engineers</p>
      </aside>
      <main id="main-content" class="auth-panel" tabindex="-1">
        {panel_html}
      </main>
    </div>
    """


def render_freshness(stamp: str = "Current · 14:32") -> str:
    return f"""
    <div class="freshness">
      <span class="freshness-status">
        <span class="health-dot"></span>
        <span><time>{E(stamp)}</time></span>
      </span>
      <div class="refresh-button" data-refresh-region role="status" aria-live="polite">
        <form method="get" data-refresh-form>
          <button type="submit" class="btn btn--small" title="Refresh">
            <svg class="icon icon--spin" aria-hidden="true"><use href="#icon-refresh-cw" /></svg>
            <span data-refresh-label>Refresh</span>
          </button>
        </form>
      </div>
    </div>
    """


def render_admin_nav(active_area: str) -> str:
    groups = [
        ("admin-nav-people", "People and access", [
            ("accounts", "user", "Staff accounts & roles"),
            ("contacts", "shield", "Contacts"),
        ]),
        ("admin-nav-configuration", "Configuration", [
            ("configuration", "settings", "Workflow configuration"),
            ("mailboxes", "mail", "Mail settings"),
            ("email-templates", "mail-open", "Email templates"),
            ("valuation-presets", "pound-sterling", "Valuation presets"),
        ]),
        ("admin-nav-oversight", "Operations and oversight", [
            ("health", "heart-pulse", "Service health"),
            ("logs", "scroll-text", "Action logs"),
            ("reports", "bar-chart", "Management Reports"),
            ("release-notes", "flag", "Release notes"),
            ("problem-reports", "alert-triangle", "Problem reports"),
            ("ai-jobs", "sparkles", "AI jobs"),
            ("automation", "bot", "Automation"),
        ]),
    ]
    out = ['<nav class="admin-nav panel" aria-label="Administration areas">']
    for gid, title, items in groups:
        out.append(f'<div class="admin-nav__group" role="group" aria-labelledby="{gid}">')
        out.append(f'<span class="admin-nav__label" id="{gid}">{E(title)}</span>')
        for key, icon, label in items:
            cur = ' aria-current="page"' if key == active_area else ""
            out.append(
                f'<a href="#admin-{key}"{cur}>'
                f'<svg class="icon" aria-hidden="true"><use href="#icon-{icon}" /></svg>'
                f'<span>{E(label)}</span></a>'
            )
        out.append("</div>")
    out.append("</nav>")
    return "".join(out)


# ---------------------------------------------------------------------------
# State Templates for pegasus_shell_v41.html (18 States across all surfaces)
# Returns [(key, label, sheets_csv, html_markup)]
# ---------------------------------------------------------------------------

def build_shell_states() -> list[tuple[str, str, str, str]]:
    states: list[tuple[str, str, str, str]] = []

    # 1. Sign-in & Password Change (/Account/SignIn, /Account/PasswordChange)
    states.append((
        "auth-signin",
        "1. Sign-in & Password change (/Account/SignIn, /Account/PasswordChange)",
        "",
        render_external_shell(f"""
        <div class="stack" style="width:100%;max-width:960px">
          <div class="v41-card-pair">
            <section class="auth-card" aria-labelledby="signin-title">
              <h1 id="signin-title">Sign in</h1>
              <div class="notice notice--info auth-notice" role="status">
                <svg class="icon" aria-hidden="true"><use href="#icon-info" /></svg>
                <div><strong>Session locked</strong><div>Your session was locked after 15 minutes of inactivity. Sign in again to continue.</div></div>
              </div>
              <form method="post" action="#">
                <div class="field">
                  <label for="signin-user">Username</label>
                  <input id="signin-user" name="Username" value="alex" autocomplete="username" />
                </div>
                <div class="field">
                  <label for="signin-pass">Password</label>
                  <div class="password-control" data-password-field>
                    <input id="signin-pass" name="Password" type="password" value="••••••••••••" autocomplete="current-password" />
                    <button type="button" class="password-reveal" data-password-reveal aria-pressed="false" aria-label="Show password">Show</button>
                  </div>
                </div>
                <button class="btn btn--primary" type="submit" data-busy-label="Signing in…">Sign in</button>
              </form>
            </section>

            <section class="auth-card" aria-labelledby="pw-forced-title" data-v41-change="f08 (E)">
              <h1 id="pw-forced-title">Change your password</h1>
              <p class="muted" data-v41-today-only>You cannot use Pegasus until the password issued to you is replaced. Choose a new password and confirm it.</p>
              <form method="post" action="#" data-v41-pw-form>
                <div class="field">
                  <label for="pw-cur">Current password</label>
                  <div class="password-control">
                    <input id="pw-cur" type="password" value="TempPass!2026" />
                    <button type="button" class="password-reveal" data-v41-proposal-only data-password-reveal aria-pressed="false" aria-label="Show password">Show</button>
                  </div>
                </div>
                <div class="field">
                  <label for="pw-new">New password</label>
                  <div class="password-control">
                    <input id="pw-new" type="password" value="NewSecure!2026" />
                    <button type="button" class="password-reveal" data-v41-proposal-only data-password-reveal aria-pressed="false" aria-label="Show password">Show</button>
                  </div>
                </div>
                <div class="field">
                  <label for="pw-confirm">Confirm new password</label>
                  <div class="password-control">
                    <input id="pw-confirm" type="password" value="NewSecure!2026" />
                    <button type="button" class="password-reveal" data-v41-proposal-only data-password-reveal aria-pressed="false" aria-label="Show password">Show</button>
                  </div>
                </div>
                <div class="button-row" data-v41-today-only>
                  <button class="btn btn--primary" type="submit">Change password</button>
                </div>
                <button class="btn btn--primary" type="submit" data-v41-proposal-only>Change password</button>
              </form>
            </section>
          </div>

          <section class="panel" aria-labelledby="pw-vol-title" data-v41-change="f08 (E)">
            <div class="panel-head">
              <div>
                <p class="eyebrow" data-v41-proposal-only>Account</p>
                <h2 id="pw-vol-title">Change password (Signed-in view · /Account/PasswordChange)</h2>
              </div>
            </div>
            <div class="panel-body stack">
              <div class="form-grid form-grid--2">
                <div class="field">
                  <label for="vol-cur">Current password</label>
                  <div class="password-control">
                    <input id="vol-cur" type="password" value="••••••••••" />
                    <button type="button" class="password-reveal" data-v41-proposal-only data-password-reveal aria-pressed="false" aria-label="Show password">Show</button>
                  </div>
                </div>
                <div class="field">
                  <label for="vol-new">New password</label>
                  <div class="password-control">
                    <input id="vol-new" type="password" value="••••••••••••" />
                    <button type="button" class="password-reveal" data-v41-proposal-only data-password-reveal aria-pressed="false" aria-label="Show password">Show</button>
                  </div>
                </div>
              </div>
              <div class="button-row">
                <button class="btn btn--primary" type="button">Change password</button>
                <a class="btn" href="#work-centre" data-v41-proposal-only>Cancel</a>
              </div>
            </div>
          </section>
        </div>
        """)
    ))

    # 2. MCP Connector Consent (/Connect/Authorize)
    states.append((
        "auth-consent",
        "2. MCP Connector consent (/Connect/Authorize)",
        "",
        render_external_shell("""
        <section class="auth-card auth-card--wide consent-card" aria-labelledby="consent-title" data-v41-change="f07 (D)">
          <header class="auth-header">
            <p class="eyebrow">MCP connector consent</p>
            <h1 id="consent-title">Allow Pegasus Desktop Connector to act as your Pegasus account?</h1>
            <p class="muted" data-v41-today-only>
              Granting access lets this connector perform the actions listed below under your operator identity until access is revoked or expires.
            </p>
          </header>
          <div class="notice notice--info" role="status">
            <svg class="icon" aria-hidden="true"><use href="#icon-user" /></svg>
            <div><strong>Signed in as alex</strong><div>Administrator · Collision Engineers</div></div>
          </div>
          <div class="panel">
            <div class="panel-head"><h2>Permissions requested</h2></div>
            <div class="panel-body">
              <dl class="detail-list consent-scopes">
                <div>
                  <dt>Cases <code data-v41-today-only>mcp:cases</code></dt>
                  <dd>Read and update Case records, engineering assessments, and drafts.</dd>
                </div>
                <div>
                  <dt data-v41-today-only>Intake <code>mcp:intake</code></dt>
                  <dt data-v41-proposal-only>Inbox &amp; Upload</dt>
                  <dd data-v41-today-only>List the intake queue, submit intake, and work Unidentified and Triage records.</dd>
                  <dd data-v41-proposal-only>Read the Inbox and Upload queues, submit files, and work Unidentified and Triage records.</dd>
                </div>
                <div>
                  <dt>Triage <code data-v41-today-only>mcp:triage</code></dt>
                  <dd>Read and record Triage findings, determinations, and responses.</dd>
                </div>
                <div>
                  <dt>Documents <code data-v41-today-only>mcp:documents</code></dt>
                  <dd>Read Case documents, photographs, and generated reports.</dd>
                </div>
                <div>
                  <dt>Stay connected <code data-v41-today-only>offline_access</code></dt>
                  <dd>Keep this connection active without asking each time.</dd>
                </div>
              </dl>
            </div>
          </div>
          <div class="button-row">
            <button class="btn btn--primary" type="button">Allow access</button>
            <button class="btn" type="button">Deny</button>
          </div>
        </section>
        """)
    ))

    # 3. Error, StatusCode & ReleaseNotes (/Error, /StatusCode, /ReleaseNotes)
    states.append((
        "auth-errors",
        "3. Error, 404 Status & Release notes (/Error, /StatusCode, /ReleaseNotes)",
        "",
        render_app_shell("work-centre", """
        <div class="stack">
          <div class="v41-card-pair">
            <section class="auth-card auth-card--wide" aria-labelledby="err-title" data-v41-change="f09">
              <div class="stack" role="alert">
                <p class="eyebrow" data-v41-proposal-only>System</p>
                <h1 id="err-title">Something went wrong</h1>
                <p>The request could not be completed. You can try the page again or report what happened.</p>
                <div class="button-row">
                  <a class="btn btn--primary" href="#work-centre">Return to Work Centre</a>
                  <a class="btn" href="#">Try the page again</a>
                </div>
                <form class="stack" method="post" action="#" style="border-top:1px solid var(--border);padding-top:12px">
                  <div class="field">
                    <label class="req" for="err-desc">What happened?</label>
                    <textarea id="err-desc" rows="2" required>Clicked Generate combined PDF on QDOS26214 and received an error screen.</textarea>
                  </div>
                  <div class="button-row">
                    <button class="btn" type="submit">Send report</button>
                  </div>
                </form>
              </div>
            </section>

            <section class="auth-card auth-card--wide" aria-labelledby="sc-title" data-v41-change="f09">
              <div class="stack" role="alert">
                <p class="eyebrow" data-v41-proposal-only>System</p>
                <h1 id="sc-title">Page not found</h1>
                <p>The page or record you requested does not exist.</p>
                <div class="button-row">
                  <a class="btn" href="#work-centre" data-v41-today-only>Return to Work Centre</a>
                  <a class="btn btn--primary" href="#work-centre" data-v41-proposal-only>Return to Work Centre</a>
                </div>
              </div>
            </section>
          </div>

          <section class="panel" aria-labelledby="rn-page-title" data-v41-change="f09">
            <div class="panel-body stack">
              <header class="page-header">
                <div class="page-title">
                  <p class="eyebrow">Pegasus</p>
                  <h1 id="rn-page-title">Release notes</h1>
                  <p class="lede" data-v41-today-only>What changed in each deployed release.</p>
                </div>
              </header>
              <article class="panel">
                <div class="panel-head">
                  <h2>v2026.10 — One-type Contacts &amp; Report dispatch</h2>
                  <span class="meta">13 Oct 2026</span>
                </div>
                <div class="panel-body">
                  <ul>
                    <li>Contacts directory grouped by Principal, Claim Source, Repairer, Storage and Third Party Engineer.</li>
                    <li>Principal report sending rules, salvage matrix and one-step report delivery.</li>
                  </ul>
                </div>
              </article>
            </div>
          </section>
        </div>
        """)
    ))

    # 4. Shell Dialogs: Account, Notifications & Command Palette (_ShellDialogs.cshtml)
    states.append((
        "shell-dialogs",
        "4. Shell dialogs: Account, Notifications & Command palette (_ShellDialogs.cshtml)",
        "",
        render_app_shell("work-centre", """
        <div class="stack">
          <header class="page-header">
            <div class="page-title">
              <p class="eyebrow">Authenticated shell</p>
              <h1>Shell dialogs &amp; utility bar</h1>
            </div>
          </header>
          <div class="v41-dialog-grid">
            <section class="dialog dialog--compact v41-inline-dialog" aria-labelledby="acc-dlg-title" data-v41-change="f01 (A)">
              <div class="dialog-head">
                <h2 id="acc-dlg-title">Account</h2>
                <button class="icon-button dialog-close" type="button" aria-label="Close"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button>
              </div>
              <div class="dialog-body stack">
                <dl class="detail-list">
                  <div><dt>Name</dt><dd>Alex Jordan</dd></div>
                  <div><dt>Role</dt><dd>Administrator</dd></div>
                  <div data-v41-proposal-only><dt>Session started</dt><dd class="mono">14 Oct 2026 08:45</dd></div>
                  <div><dt>Idle lock</dt><dd>After 15 minutes of inactivity</dd></div>
                </dl>
                <div class="button-row" data-v41-proposal-only style="border-top:1px solid var(--border);padding-top:10px">
                  <button class="btn btn--small" type="button">Release notes</button>
                  <button class="btn btn--small" type="button">Report a problem</button>
                  <a class="btn btn--small" href="#auth-signin">Change password</a>
                </div>
              </div>
              <div class="dialog-foot" data-v41-today-only>
                <button class="btn" type="button">Close</button>
                <button class="btn" type="button">Release notes</button>
                <button class="btn" type="button">Report a problem</button>
                <a class="btn" href="#auth-signin">Change password</a>
                <button class="btn btn--danger" type="button">Sign out</button>
              </div>
              <div class="dialog-foot" data-v41-proposal-only>
                <button class="btn" type="button">Close</button>
                <button class="btn btn--danger" type="button">Sign out</button>
              </div>
            </section>

            <section class="dialog dialog--compact v41-inline-dialog" aria-labelledby="notif-dlg-title" data-v41-change="f02">
              <div class="dialog-head">
                <h2 id="notif-dlg-title">Notifications</h2>
                <div class="cluster">
                  <button class="btn btn--small btn--sm" type="button" data-v41-proposal-only>Mark all read</button>
                  <button class="icon-button dialog-close" type="button" aria-label="Close"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button>
                </div>
              </div>
              <div class="dialog-body stack">
                <a class="row-button notification-item is-unread" href="#engineer-read">
                  <div class="row-top"><span class="row-title">AI Proposal ready · QDOS26214</span><span class="row-time">14:28</span></div>
                  <div class="row-excerpt">Repair specification candidate completed for AB12 CDE.</div>
                </a>
                <a class="row-button notification-item is-unread" href="#unidentified-images">
                  <div class="row-top"><span class="row-title">Images paired · IMG-2026-0019</span><span class="row-time">13:50</span></div>
                  <div class="row-excerpt">14 photographs linked for AB12 CDE.</div>
                </a>
              </div>
              <div class="dialog-foot">
                <button class="btn" type="button" data-v41-today-only>Mark all read</button>
                <button class="btn" type="button">Close</button>
              </div>
            </section>

            <section class="dialog dialog--compact v41-inline-dialog" aria-labelledby="cmd-dlg-title" data-v41-change="f03">
              <div class="dialog-head">
                <h2 id="cmd-dlg-title">Go to</h2>
                <button class="icon-button dialog-close" type="button" aria-label="Close"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button>
              </div>
              <div class="dialog-body stack">
                <input type="search" value="QDOS26214" aria-label="Command search" />
                <div class="stack">
                  <button class="row-button cluster" type="button">
                    <svg class="icon" aria-hidden="true"><use href="#icon-layout-dashboard" /></svg><span>Work Centre</span>
                  </button>
                  <button class="row-button cluster" type="button">
                    <svg class="icon" aria-hidden="true" data-v41-today-only><use href="#icon-list" /></svg>
                    <svg class="icon" aria-hidden="true" data-v41-proposal-only><use href="#icon-list-checks" /></svg>
                    <span>Cases</span>
                  </button>
                  <button class="row-button cluster" type="button">
                    <svg class="icon" aria-hidden="true" data-v41-today-only><use href="#icon-folder-open" /></svg>
                    <svg class="icon" aria-hidden="true" data-v41-proposal-only><use href="#icon-search" /></svg>
                    <span>Search</span>
                  </button>
                  <button class="row-button cluster" type="button">
                    <svg class="icon" aria-hidden="true" data-v41-today-only><use href="#icon-layout-grid" /></svg>
                    <svg class="icon" aria-hidden="true" data-v41-proposal-only><use href="#icon-settings" /></svg>
                    <span>Administration</span>
                  </button>
                </div>
              </div>
            </section>
          </div>
        </div>
        """, hide_new_case=True)
    ))

    # 5. Work Centre: Needs attention & Assign Engineer (/Index)
    states.append((
        "work-centre",
        "5. Work Centre: Needs attention & Assign Engineer (/Index)",
        "work-centre.css",
        render_app_shell("work-centre", f"""
        <div class="work-centre" data-work-centre>
          <header class="page-header" data-v41-change="f11">
            <div class="page-title">
              <p class="eyebrow">Office-wide work</p>
              <h1>Work Centre</h1>
            </div>
            <div class="page-actions">
              {render_freshness("Updated · 14:32")}
              <a class="btn btn--primary" href="#create-case">
                <svg class="icon" aria-hidden="true"><use href="#icon-plus" /></svg>
                <span>Create Case</span>
              </a>
            </div>
          </header>

          <div class="wc-metrics-section" data-wc-refresh-section="metrics" data-wc-refresh-state="current">
            <nav class="wc-metrics" aria-label="Office queue totals">
              <a class="metric" data-value="not_ready" href="#cases">
                <span class="metric-label"><span>Not ready</span></span>
                <span class="metric-value">5</span>
              </a>
              <a class="metric" data-value="review" href="#cases">
                <span class="metric-label"><span>Review</span></span>
                <span class="metric-value">3</span>
              </a>
              <a class="metric" data-value="held" href="#cases">
                <span class="metric-label"><span>Held</span></span>
                <span class="metric-value">2</span>
              </a>
              <a class="metric" data-value="unidentified" href="#unidentified-images">
                <span class="metric-label"><span>Unidentified</span></span>
                <span class="metric-value">2</span>
              </a>
              <a class="metric" data-value="triage" href="#triage-case">
                <span class="metric-label"><span>Triages</span></span>
                <span class="metric-value">4</span>
              </a>
            </nav>
          </div>

          <section class="panel wc-activity" aria-labelledby="wc-act-title" data-wc-activity>
            <div class="panel-head"><h2 id="wc-act-title">Activity</h2></div>
            <table class="wc-activity-table">
              <thead>
                <tr>
                  <th scope="col"><span class="sr-only">Activity</span></th>
                  <th scope="col" data-figure="new-cases"><a href="#work-centre-tabs">New cases</a></th>
                  <th scope="col" data-figure="sent">Sent to Engineer</th>
                  <th scope="col" data-figure="reports">Reports sent</th>
                  <th scope="col" data-figure="completed">Completed</th>
                  <th scope="col" data-figure="emails">E-mails received</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="row">Today</th>
                  <td data-figure="new-cases-today">9</td>
                  <td data-figure="sent-today">7</td>
                  <td data-figure="reports-today">6</td>
                  <td data-figure="completed-today">5</td>
                  <td data-figure="emails-today">38</td>
                </tr>
                <tr>
                  <th scope="row">This week</th>
                  <td data-figure="new-cases-week">44</td>
                  <td data-figure="sent-week">39</td>
                  <td data-figure="reports-week">31</td>
                  <td data-figure="completed-week">28</td>
                  <td data-figure="emails-week">192</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section class="panel wc-ledger" aria-label="Work Centre views">
            <div class="tabs wc-tabs" role="tablist" aria-label="Work Centre sections">
              <a class="tab" role="tab" href="#work-centre" aria-selected="true" aria-current="page">Needs attention<span class="tab-count">14</span></a>
              <a class="tab" role="tab" href="#work-centre-tabs" aria-selected="false">New cases<span class="tab-count">9</span></a>
              <a class="tab" role="tab" href="#work-centre-tabs" aria-selected="false">AI jobs<span class="tab-count">3</span></a>
            </div>

            <div class="wc-toolbar">
              <div class="wc-toolbar-left">
                <h2 id="wc-na-title">Needs attention</h2>
                <span class="meta">14 items</span>
                <div class="wc-switch" role="group" aria-label="Scope" data-v41-change="f11">
                  <a href="#work-centre" aria-current="true">Office</a>
                  <a href="#work-centre" aria-current="false">Mine</a>
                </div>
              </div>
              <form method="get" class="wc-search wc-find" role="search" data-v41-change="f12">
                <input type="hidden" name="since" value="2026-10-14T08:45:00Z" data-v41-proposal-only />
                <label class="sr-only" for="wc-q">Find in this work</label>
                <svg class="icon" aria-hidden="true"><use href="#icon-search" /></svg>
                <input id="wc-q" type="search" name="q" placeholder="Find in this work" autocomplete="off" />
              </form>
            </div>

            <nav class="chips wc-filters" aria-label="Filter Needs attention">
              <a class="chip" href="#work-centre" aria-current="true">All<span class="n">14</span></a>
              <a class="chip" href="#work-centre" aria-current="false">Unassigned<span class="n">4</span></a>
              <a class="chip" href="#work-centre" aria-current="false">Review<span class="n">3</span></a>
              <a class="chip" href="#work-centre" aria-current="false">Held<span class="n">2</span></a>
              <a class="chip" href="#work-centre" aria-current="false">Tasks<span class="n">2</span></a>
              <a class="chip" href="#work-centre" aria-current="false">AI draft<span class="n">1</span></a>
            </nav>

            <div class="wc-table" data-row-list>
              <table class="table wc-ledger-table wc-table--fold" aria-label="Needs attention">
                <thead>
                  <tr>
                    <th scope="col" class="wc-col-task">Next action</th>
                    <th scope="col" class="wc-col-record">Record / detail</th>
                    <th scope="col" class="wc-col-owner">Owner</th>
                    <th scope="col" class="wc-col-due">Due</th>
                    <th scope="col" class="wc-col-received">Received</th>
                    <th scope="col" class="wc-col-action"><span class="sr-only">Action</span></th>
                    <th scope="col" class="wc-col-dismiss"><span class="sr-only">Dismiss</span></th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="wc-group-row" data-wc-group="overdue"><td colspan="7"><h3>Overdue (2)</h3></td></tr>
                  <tr id="wc-row-1" aria-selected="true">
                    <td class="wc-col-task">
                      <a class="wc-task-link" href="#engineer-read" aria-expanded="true">Complete engineering report</a>
                      <small>With Engineer · QDOS</small>
                    </td>
                    <td class="wc-col-record">
                      <span class="mono"><a href="#engineer-read">QDOS26214</a> · AB12 CDE</span>
                      <small>BMW 320d · J. Patel</small>
                    </td>
                    <td class="wc-col-owner">Rashid Khan</td>
                    <td class="wc-col-due"><span class="status status--red">2 days overdue</span></td>
                    <td class="wc-col-received">5 d ago</td>
                    <td class="wc-col-action"><a class="btn btn--small" href="#engineer-read">Open Case</a></td>
                    <td class="wc-col-dismiss"><button class="icon-button wc-dismiss" type="button" aria-label="Dismiss"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button></td>
                  </tr>
                  <tr class="wc-inline-detail">
                    <td colspan="7">
                      <div class="wc-context">
                        <div class="wc-context-head">
                          <div>
                            <div class="eyebrow">Selected Case</div>
                            <h3>QDOS26214 · AB12 CDE</h3>
                          </div>
                          <span class="status status--navy">With Engineer</span>
                        </div>
                        <dl class="fact-grid wc-facts">
                          <div class="fact"><dt>Case stage</dt><dd>With Engineer</dd></div>
                          <div class="fact"><dt>Principal</dt><dd>QDOS</dd></div>
                          <div class="fact"><dt>Engineer</dt><dd>Rashid Khan</dd></div>
                          <div class="fact"><dt>Due date</dt><dd>12 Oct 2026</dd></div>
                        </dl>
                      </div>
                    </td>
                  </tr>
                  <tr id="wc-row-2" data-v41-change="f10">
                    <td class="wc-col-task">
                      <a class="wc-task-link" href="#engineer-read" aria-expanded="false">Assign Engineer</a>
                      <small>Review · Davison Flynn Duke</small>
                    </td>
                    <td class="wc-col-record">
                      <span class="mono"><a href="#engineer-read">DFD26031</a> · YK71 XWB</span>
                      <small>Audi A4 Avant · S. Morris</small>
                    </td>
                    <td class="wc-col-owner muted">Unassigned</td>
                    <td class="wc-col-due"><span class="status status--amber">Due today</span></td>
                    <td class="wc-col-received">Yesterday</td>
                    <td class="wc-col-action">
                      <button class="btn btn--small" type="button" data-wc-open-assign data-wc-case-ref="DFD26031" data-wc-principal="Davison Flynn Duke" data-wc-vehicle="YK71 XWB · Audi A4 Avant">Assign Engineer</button>
                    </td>
                    <td class="wc-col-dismiss"><button class="icon-button wc-dismiss" type="button" aria-label="Dismiss"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section class="dialog dialog--compact v41-inline-dialog" aria-labelledby="wc-assign-title" data-v41-change="f10">
            <div class="dialog-head">
              <h2 id="wc-assign-title">Assign Engineer</h2>
              <button class="icon-button dialog-close" type="button" aria-label="Close"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button>
            </div>
            <div class="dialog-body stack">
              <div class="notice notice--warn" data-v41-today-only>
                <svg class="icon" aria-hidden="true"><use href="#icon-alert-triangle" /></svg>
                <div><strong>Today bug (f10)</strong><div>Clicking Assign Engineer on row 2 (DFD26031) opens the dialog bound to the expanded row 1 (QDOS26214)!</div></div>
              </div>
              <dl class="detail-list">
                <div data-v41-today-only><dt>Case</dt><dd class="mono">QDOS26214 (Wrong Case!)</dd></div>
                <div data-v41-proposal-only><dt>Case</dt><dd class="mono">DFD26031</dd></div>
                <div data-v41-today-only><dt>Principal</dt><dd>QDOS</dd></div>
                <div data-v41-proposal-only><dt>Principal</dt><dd>Davison Flynn Duke</dd></div>
                <div data-v41-today-only><dt>Vehicle</dt><dd>AB12 CDE · BMW 320d</dd></div>
                <div data-v41-proposal-only><dt>Vehicle</dt><dd>YK71 XWB · Audi A4 Avant</dd></div>
              </dl>
              <div class="field">
                <label class="req" for="wc-eng-select">Engineer</label>
                <select id="wc-eng-select">
                  <option value="rk">Rashid Khan</option>
                  <option value="cm" selected>Claire Mercer</option>
                  <option value="dh">David Hughes</option>
                </select>
              </div>
            </div>
            <div class="dialog-foot">
              <button class="btn" type="button">Cancel</button>
              <button class="btn btn--primary" type="button">Assign</button>
            </div>
          </section>
        </div>
        """, hide_new_case=True)
    ))

    # 6. Work Centre: New cases & AI jobs tabs (/Index?tab=new-cases, ?tab=ai-jobs)
    states.append((
        "work-centre-tabs",
        "6. Work Centre: New cases & AI jobs tabs (/Index?tab=new-cases)",
        "work-centre.css",
        render_app_shell("work-centre", f"""
        <div class="work-centre" data-work-centre>
          <header class="page-header">
            <div class="page-title">
              <p class="eyebrow">Office-wide work</p>
              <h1>Work Centre</h1>
            </div>
            <div class="page-actions">
              {render_freshness("Updated · 14:32")}
              <a class="btn btn--primary" href="#create-case">
                <svg class="icon" aria-hidden="true"><use href="#icon-plus" /></svg>
                <span>Create Case</span>
              </a>
            </div>
          </header>

          <section class="panel wc-ledger" aria-labelledby="wc-nc-title" data-v41-change="f12">
            <div class="tabs wc-tabs" role="navigation" aria-label="Work Centre views">
              <a href="#work-centre"><span>Needs attention</span><span class="tab-count">14</span></a>
              <a href="#work-centre-tabs" aria-current="page"><span>New cases</span><span class="tab-count">9</span></a>
              <a href="#work-centre-tabs"><span>AI jobs</span><span class="tab-count">3</span></a>
            </div>
            <div class="wc-toolbar">
              <div class="wc-toolbar-left">
                <h2 id="wc-nc-title">New cases</h2>
                <span class="meta">Last 7 days · 9 rows</span>
              </div>
            </div>
            <div class="wc-table" data-row-list>
              <table class="table wc-ledger-table">
                <thead>
                  <tr><th>Case</th><th>Principal</th><th>Detail</th><th>Arrival</th><th>Owner</th><th>Received</th><th class="right">Actions</th></tr>
                </thead>
                <tbody>
                  <tr>
                    <td class="mono"><a href="#engineer-read">QDOS26218</a></td>
                    <td>QDOS</td>
                    <td><span class="wc-vrm">LM20 TUV</span> · Ford Transit Custom</td>
                    <td><span class="status status--blue">Email</span></td>
                    <td class="muted">Unassigned</td>
                    <td>Today 14:05</td>
                    <td class="right"><button class="icon-button wc-dismiss" type="button" aria-label="Dismiss"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button></td>
                  </tr>
                  <tr class="wc-group-row"><th colspan="7" scope="colgroup">Since you last looked (14 Oct 08:45)</th></tr>
                  <tr>
                    <td class="mono"><a href="#engineer-read">AX26340</a></td>
                    <td>AX</td>
                    <td><span class="wc-vrm">GF19 HJK</span> · Mercedes-Benz C220d</td>
                    <td><span class="status status--navy">Principal API</span></td>
                    <td>C. Mercer</td>
                    <td>Yesterday</td>
                    <td class="right"><button class="icon-button wc-dismiss" type="button" aria-label="Dismiss"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section class="panel wc-ledger" aria-labelledby="wc-ai-title" data-v41-change="f12">
            <div class="wc-toolbar">
              <div class="wc-toolbar-left">
                <h2 id="wc-ai-title">AI jobs</h2>
                <span class="meta">2 draft ready · 1 failed</span>
              </div>
            </div>
            <div class="wc-table" data-row-list>
              <table class="table wc-ledger-table">
                <thead>
                  <tr><th>Job</th><th>State</th><th>Instruction</th><th>Record</th><th>Started</th><th>Note</th><th class="right">Actions</th></tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>Repair spec</strong></td>
                    <td><span class="status status--green">Draft ready</span></td>
                    <td>Target 55% of PAV · include glass</td>
                    <td class="mono"><a href="#engineer-read">QDOS26214</a></td>
                    <td>A. Jordan · 14:10</td>
                    <td>—</td>
                    <td class="right">
                      <div class="wc-row-actions">
                        <a class="btn btn--small" href="#engineer-read">Review AI Proposal</a>
                        <button class="icon-button wc-dismiss" type="button" aria-label="Dismiss"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Query response</strong></td>
                    <td><span class="status status--red">Failed</span></td>
                    <td>Explain labour rate reduction</td>
                    <td class="mono"><a href="#engineer-read">PCH26118</a></td>
                    <td>R. Khan · 11:20</td>
                    <td class="muted">Provider timeout</td>
                    <td class="right">
                      <div class="wc-row-actions">
                        <a class="btn btn--small" href="#engineer-read">Open query</a>
                        <button class="icon-button wc-dismiss" type="button" aria-label="Dismiss"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </div>
        """, hide_new_case=True)
    ))

    # 7. Search (/Search)
    states.append((
        "search",
        "7. Search: Filters, Results & Selected Case Preview (/Search)",
        "",
        render_app_shell("search", f"""
        <div class="stack">
          <header class="page-header" data-v41-change="f14 (G)">
            <div class="page-title">
              <p class="eyebrow">Case lookup</p>
              <h1>Search</h1>
            </div>
            <div class="page-actions">
              {render_freshness("Current · 14:32")}
              <a class="btn btn--primary" href="#upload" data-v41-today-only>Create Case</a>
            </div>
          </header>

          <section class="panel" aria-label="Search filters" data-v41-change="f13 (F)">
            <form class="panel-body stack compact-search" method="get" action="#">
              <div class="form-grid form-grid--auto compact-search__main">
                <div class="field">
                  <label for="s-query" data-v41-today-only>Case or reference</label>
                  <label for="s-query" data-v41-proposal-only>Case/PO or Image reference</label>
                  <input id="s-query" name="query" value="26" />
                </div>
                <div class="field">
                  <label for="s-reg">Registration</label>
                  <input id="s-reg" name="registration" class="mono" value="AB12" />
                </div>
                <div class="field">
                  <label for="s-claimant">Claimant</label>
                  <input id="s-claimant" name="claimant" value="" />
                </div>
                <div class="field">
                  <label for="s-claim" data-v41-today-only>Claim reference</label>
                  <label for="s-claim" data-v41-proposal-only>Claim/Principal reference</label>
                  <input id="s-claim" name="claimNumber" value="" />
                </div>
                <div class="field">
                  <label for="s-principal">Principal</label>
                  <input id="s-principal" name="principalCode" value="QDOS" data-v41-today-only />
                  <select id="s-principal-sel" name="principalCode" data-v41-proposal-only>
                    <option value="">All principals</option>
                    <option value="QDOS" selected>QDOS</option>
                    <option value="DFD">Davison Flynn Duke (DFD)</option>
                    <option value="AX">AX</option>
                    <option value="PCH">Performance Car Hire (PCH)</option>
                  </select>
                </div>
                <div class="field">
                  <label for="s-state" data-v41-today-only>State</label>
                  <label for="s-state" data-v41-proposal-only>Case stage</label>
                  <select id="s-state" name="state">
                    <option value="">All stages</option>
                    <option value="WithEngineer" selected>With Engineer</option>
                    <option value="ReadyForReview">Review</option>
                    <option value="Held">Held</option>
                  </select>
                </div>
                <div class="cluster compact-search__actions">
                  <button class="btn btn--primary" type="submit" data-busy-label="Searching…">Search</button>
                  <a class="btn" href="#search">Clear</a>
                </div>
              </div>

              <details class="compact-search__more" open>
                <summary>More filters</summary>
                <div class="form-grid form-grid--4 compact-search__advanced">
                  <div class="field">
                    <label for="s-eng">Engineer</label>
                    <input id="s-eng" name="engineerId" value="d47fbbae-81c4-4f10-9a11-002918273645" data-v41-today-only />
                    <select id="s-eng-sel" name="engineerId" data-v41-proposal-only>
                      <option value="">All engineers</option>
                      <option value="rk" selected>Rashid Khan</option>
                      <option value="cm">Claire Mercer</option>
                      <option value="dh">David Hughes</option>
                    </select>
                  </div>
                  <div class="field">
                    <label for="s-from">Received from</label>
                    <input id="s-from" type="date" value="2026-10-01" />
                  </div>
                  <div class="field">
                    <label for="s-to">Received to</label>
                    <input id="s-to" type="date" value="2026-10-14" />
                  </div>
                  <div class="field">
                    <label for="s-origin">Origin</label>
                    <input id="s-origin" name="origin" value="E-mail" data-v41-today-only />
                    <select id="s-origin-sel" name="origin" data-v41-proposal-only>
                      <option value="">All origins</option>
                      <option value="Email" selected>E-mail</option>
                      <option value="Manual">Manual upload</option>
                      <option value="PrincipalApi">Principal API</option>
                    </select>
                  </div>
                </div>
              </details>
            </form>
          </section>

          <div class="case-search-layout" data-v41-change="f14 (G)">
            <section class="panel" aria-labelledby="search-res-title">
              <div class="panel-head">
                <h2 id="search-res-title">Results</h2>
                <span class="meta">Showing 1–2 of 2</span>
              </div>
              <div class="table-wrap no-border">
                <table class="table" data-search-results-table>
                  <thead>
                    <tr>
                      <th>Case/PO</th>
                      <th>Vehicle</th>
                      <th>Claimant</th>
                      <th>Principal</th>
                      <th data-v41-proposal-only>Type</th>
                      <th data-v41-today-only>State</th>
                      <th data-v41-proposal-only>Case stage</th>
                      <th data-v41-today-only>Received</th>
                      <th data-v41-proposal-only>Due</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr class="is-selected" aria-selected="true">
                      <td>
                        <a class="mono" href="#engineer-read">QDOS26214</a>
                        <div class="muted mono">CLM-99412</div>
                      </td>
                      <td>
                        <div class="mono">AB12 CDE</div>
                        <div class="muted">BMW 320d</div>
                      </td>
                      <td>J. Patel</td>
                      <td class="mono">QDOS</td>
                      <td data-v41-proposal-only>Standard</td>
                      <td><span class="status status--navy">With Engineer</span></td>
                      <td data-v41-today-only>09 Oct 2026 10:15</td>
                      <td data-v41-proposal-only style="color:var(--red);font-weight:600">12 Oct 2026</td>
                    </tr>
                    <tr>
                      <td>
                        <a class="mono" href="#engineer-read">QDOS26198</a>
                        <div class="muted mono">CLM-98801</div>
                      </td>
                      <td>
                        <div class="mono">AB12 XYZ</div>
                        <div class="muted">Volkswagen Golf</div>
                      </td>
                      <td>M. Evans</td>
                      <td class="mono">QDOS</td>
                      <td data-v41-proposal-only>Audit</td>
                      <td><span class="status status--amber">Review</span></td>
                      <td data-v41-today-only>03 Oct 2026 14:20</td>
                      <td data-v41-proposal-only>15 Oct 2026</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <aside id="case-search-preview" class="panel case-preview-pane" aria-labelledby="preview-ref">
              <div class="panel-head">
                <div>
                  <p class="eyebrow">Selected Case</p>
                  <div class="cluster">
                    <h2 id="preview-ref" class="mono">QDOS26214</h2>
                    <button class="btn btn--small" type="button" data-v41-proposal-only data-copy="QDOS26214">Copy Case/PO</button>
                  </div>
                </div>
                <div class="cluster">
                  <span class="status status--navy">With Engineer</span>
                  <a class="btn btn--primary btn--small" href="#engineer-read">Open Case</a>
                </div>
              </div>
              <div class="panel-body stack">
                <dl class="fact-grid">
                  <div class="fact"><dt>Type</dt><dd>Standard</dd></div>
                  <div class="fact"><dt data-v41-today-only>State</dt><dt data-v41-proposal-only>Case stage</dt><dd>With Engineer</dd></div>
                  <div class="fact"><dt data-v41-today-only>Our ref</dt><dt data-v41-proposal-only>Claim ref</dt><dd class="mono">CLM-99412</dd></div>
                  <div class="fact"><dt>Engineer</dt><dd>Rashid Khan</dd></div>
                  <div class="fact"><dt>Due</dt><dd>12 Oct 2026</dd></div>
                  <div class="fact">
                    <dt>Next action</dt>
                    <dd data-v41-today-only class="muted">Not recorded</dd>
                    <dd data-v41-proposal-only><strong>Complete engineering report</strong> (1 blocker: Valuation PAV)</dd>
                  </div>
                </dl>
              </div>
            </aside>
          </div>
        </div>
        """)
    ))

    # 8. Inbox (/Inbox)
    states.append((
        "inbox",
        "8. Inbox: Consolidated scope rail, 3-col filter bar & Quick preview (/Inbox)",
        "inbox.css",
        render_app_shell("inbox", f"""
        <div class="stack">
          <header class="page-header">
            <div class="page-title">
              <p class="eyebrow">Emails</p>
              <h1>Inbox</h1>
            </div>
            <div class="page-actions">
              {render_freshness("Current · 14:32")}
            </div>
          </header>

          <section class="pane-layout pane-layout--3 inbox-layout" aria-label="Inbox" data-mail-preview-workspace data-v41-change="f15 (H), f16">
            <aside class="pane" aria-label="Views">
              <div class="pane-body pane-scroll">
                <div class="scope-list" data-mail-scopes>
                  <button type="button" class="scope-button" aria-pressed="true">
                    <span class="scope-visual-icon"><svg class="icon" aria-hidden="true"><use href="#icon-inbox" /></svg></span>
                    <span>All incoming</span>
                    <span class="tabular">38</span>
                  </button>
                  <button type="button" class="scope-button" aria-pressed="false">
                    <span class="scope-visual-icon"><svg class="icon" aria-hidden="true"><use href="#icon-search" /></svg></span>
                    <span>No Case Found</span>
                    <span class="tabular">4</span>
                  </button>
                  <button type="button" class="scope-button" aria-pressed="false">
                    <span class="scope-visual-icon"><svg class="icon" aria-hidden="true"><use href="#icon-send" /></svg></span>
                    <span>Sent Items</span>
                    <span class="tabular">19</span>
                  </button>
                  <button type="button" class="scope-button" aria-pressed="false">
                    <span class="scope-visual-icon"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></span>
                    <span>Dismissed</span>
                    <span class="tabular">7</span>
                  </button>
                  <button type="button" class="scope-button" aria-pressed="false" data-v41-proposal-only>
                    <span class="scope-visual-icon"><svg class="icon" aria-hidden="true"><use href="#icon-trash-2" /></svg></span>
                    <span>Deleted Items</span>
                    <span class="tabular">0</span>
                  </button>
                </div>
              </div>
            </aside>

            <div class="pane" aria-label="Message list">
              <form method="get" class="inbox-filter" data-v41-inbox-filter>
                <div class="field">
                  <label for="ib-mailbox">Mailbox</label>
                  <select id="ib-mailbox"><option>All mailboxes</option><option>instructions@collisionengineers.co.uk</option><option>desk@collisionengineers.co.uk</option></select>
                </div>
                <div class="field" data-v41-today-only>
                  <label for="ib-folder">Folder</label>
                  <select id="ib-folder"><option>Inbox</option><option>Sent Items</option><option>Deleted Items</option></select>
                </div>
                <div class="field">
                  <label for="ib-cat">Category</label>
                  <select id="ib-cat">
                    <option value="">All categories</option>
                    <option>New instruction</option>
                    <option>Triage request</option>
                    <option>Images received</option>
                    <option>Query</option>
                    <option data-v41-today-only>No Case Found</option>
                  </select>
                </div>
                <div class="field inbox-filter__search">
                  <label for="ib-q">Search</label>
                  <div class="inbox-filter__search-row">
                    <input id="ib-q" type="search" placeholder="Subject, sender, body, attachment, VRM or QDOS" />
                    <button type="submit" class="btn btn--primary">Search</button>
                  </div>
                </div>
              </form>

              <div class="pane-head inbox-messages-head">
                <div class="inbox-message-title"><h2 id="inbox-list-title">Messages</h2></div>
                <span class="meta">38 messages</span>
                <a class="btn btn--small sort-toggle" href="#inbox">
                  <svg class="icon" aria-hidden="true"><use href="#icon-arrow-up-down" /></svg>
                  <span>Received</span>
                </a>
              </div>

              <div class="pane-body pane-scroll" data-row-list>
                <div class="row-button inbox-row unread inbox-row--two-actions is-active" aria-current="true">
                  <span class="row-top">
                    <span class="row-title"><span class="unread-indicator" aria-hidden="true"></span>claims@dfd-solicitors.co.uk</span>
                    <span class="row-time"><time>14 Oct 2026</time><time>14:12</time></span>
                  </span>
                  <a class="row-title" href="#mail-message">New Instruction — YK71 XWB — S. Morris (DFD-88310)</a>
                  <span class="row-excerpt">Please find attached instruction and repairer estimate for Audi A4 Avant YK71 XWB…</span>
                  <span class="row-top">
                    <span class="cluster">
                      <span class="status status--green">Case created</span>
                      <span class="row-meta">New instruction</span>
                    </span>
                    <span class="row-meta"><a href="#engineer-read">DFD26031</a> · 3 attachments</span>
                  </span>
                </div>

                <div class="row-button inbox-row inbox-row--two-actions">
                  <span class="row-top">
                    <span class="row-title">workshop@riverside-coachworks.example</span>
                    <span class="row-time"><time>14 Oct 2026</time><time>13:04</time></span>
                  </span>
                  <a class="row-title" href="#mail-message">Additional stripping photos — AB12 CDE</a>
                  <span class="row-excerpt">Attached 6 images taken after front bumper removal in bay 3…</span>
                  <span class="row-top">
                    <span class="cluster">
                      <span class="status status--amber">No Case Found</span>
                      <span class="row-meta">Images received</span>
                    </span>
                    <span class="row-meta">6 attachments</span>
                  </span>
                </div>
              </div>
            </div>

            <aside id="mail-quick-preview" class="pane inbox-preview" aria-label="Message preview" data-mail-preview>
              <div class="pane-head">
                <h2 id="ib-prev-title">Message preview</h2>
                <a class="btn btn--small btn--dark" href="#mail-message">
                  <svg class="icon" aria-hidden="true"><use href="#icon-arrow-right" /></svg>
                  <span>Open message</span>
                </a>
              </div>
              <div class="pane-body pane-scroll">
                <div class="detail-canvas stack">
                  <div class="mail-header">
                    <div class="mail-subject">New Instruction — YK71 XWB — S. Morris (DFD-88310)</div>
                    <div class="mail-route">
                      <span><strong>From:</strong> claims@dfd-solicitors.co.uk</span>
                      <span><strong>To:</strong> instructions@collisionengineers.co.uk</span>
                      <span><time>14 Oct 2026 14:12</time></span>
                    </div>
                  </div>
                  <dl class="fact-grid">
                    <div class="fact"><dt>Outcome</dt><dd><span class="status status--green">Case created</span></dd></div>
                    <div class="fact"><dt>Classification</dt><dd>New instruction</dd></div>
                    <div class="fact"><dt>Case</dt><dd><a class="mono" href="#engineer-read">DFD26031</a></dd></div>
                    <div class="fact"><dt>Attachments</dt><dd>1 PDF, 2 images</dd></div>
                  </dl>
                  <div class="mail-plain">Please find attached instruction and repairer estimate for Audi A4 Avant YK71 XWB. Vehicle is currently at Northside ARC.</div>
                  <div class="button-row">
                    <a class="btn btn--primary" href="#mail-message">Open full message</a>
                    <a class="btn" href="#mail-message">Reply</a>
                    <a class="btn" href="#engineer-read">Open Case</a>
                  </div>
                </div>
              </div>
            </aside>
          </section>
        </div>
        """)
    ))

    # 9. Message Record (/Inbox/{id})
    states.append((
        "mail-message",
        "9. Message Record: Deduplicated header, Decision card, Attachments & Case tab (/Inbox/{id})",
        "inbox.css",
        render_app_shell("inbox", f"""
        <div class="stack">
          <header class="page-header" data-v41-change="f17 (I)">
            <div class="page-title">
              <p class="eyebrow">Inbox message</p>
              <h1 class="wrap">New Instruction — YK71 XWB — S. Morris (DFD-88310)</h1>
            </div>
            <div class="page-actions">
              {render_freshness("Current · 14:32")}
              <a class="btn" href="#">Reply</a>
              <a class="btn" href="#">Reply all</a>
              <a class="btn" href="#">Forward</a>
              <a class="btn" href="#inbox">
                <svg class="icon" aria-hidden="true" data-v41-today-only><use href="#icon-arrow-right" /></svg>
                <svg class="icon" aria-hidden="true" data-v41-proposal-only><use href="#icon-chevron-left" /></svg>
                <span>Back to Inbox</span>
              </a>
            </div>
          </header>

          <article class="record">
            <header class="record-head panel-head" data-v41-change="f17 (I)">
              <h2 class="wrap" data-v41-today-only>New Instruction — YK71 XWB — S. Morris (DFD-88310)</h2>
              <span class="record-identity">
                <span><strong>From:</strong> claims@dfd-solicitors.co.uk</span>
                <span><strong>Mailbox:</strong> instructions@collisionengineers.co.uk</span>
                <span><strong>Received:</strong> <time>14 Oct 2026 14:12</time></span>
              </span>
              <span class="record-head-end">
                <span class="status status--green">Classified</span>
              </span>
            </header>
            <div class="record-accent"></div>

            <nav class="tabs" aria-label="Message views">
              <a class="tab" href="#mail-message" aria-current="page">Message</a>
              <a class="tab" href="#mail-message">Attachments · 2</a>
              <a class="tab" href="#mail-message">Case · DFD26031</a>
            </nav>

            <div class="record-body stack">
              <section class="panel mail-compose-panel" aria-labelledby="compose-title" data-v41-change="f17 (I)">
                <div class="panel-head"><h2 id="compose-title">Reply</h2></div>
                <div class="panel-body stack">
                  <div class="form-grid form-grid--2">
                    <div class="field"><label>From</label><input value="instructions@collisionengineers.co.uk" readonly /></div>
                    <div class="field"><label>To</label><input value="claims@dfd-solicitors.co.uk" readonly /></div>
                  </div>
                  <div class="field"><label class="req" for="reply-body">Message</label><textarea id="reply-body" rows="3">Thank you for your instruction. We have allocated reference DFD26031.</textarea></div>
                  <div class="button-row">
                    <button class="btn btn--primary" type="button">Send</button>
                    <a class="btn" href="#" data-v41-proposal-only>Cancel</a>
                  </div>
                </div>
              </section>

              <div class="split">
                <div class="stack" data-v41-change="f17 (I)">
                  <div class="mail-header">
                    <div class="mail-subject" data-v41-today-only>New Instruction — YK71 XWB — S. Morris (DFD-88310)</div>
                    <div class="mail-route">
                      <span><strong>To:</strong> instructions@collisionengineers.co.uk</span>
                      <span><strong>Cc:</strong> handler@dfd-solicitors.co.uk</span>
                    </div>
                  </div>
                  <pre class="mail-plain">Dear Collision Engineers,

Please find attached our instruction letter, client photographs, and repairer estimate for Audi A4 Avant (YK71 XWB).

Kind regards,
Claims Team · Davison Flynn Duke Solicitors</pre>

                  <div class="table-wrap">
                    <table class="table">
                      <thead><tr><th>File</th><th>Kind</th><th>Size</th><th>Outcome</th><th class="right">Open</th></tr></thead>
                      <tbody>
                        <tr>
                          <td>DFD_Instruction_88310.pdf</td>
                          <td class="muted" data-v41-today-only>application/pdf</td>
                          <td class="muted" data-v41-proposal-only>PDF document</td>
                          <td class="tabular">412 KB</td>
                          <td><span class="status status--green">Filed to case</span></td>
                          <td class="right"><a class="btn btn--small" href="#">Open</a></td>
                        </tr>
                        <tr>
                          <td>Northside_Estimate_YK71XWB.docx</td>
                          <td class="muted" data-v41-today-only>application/vnd.openxmlformats-officedocument.wordprocessingml.document</td>
                          <td class="muted" data-v41-proposal-only>Word document</td>
                          <td class="tabular">188 KB</td>
                          <td><span class="status status--green">Filed to case</span></td>
                          <td class="right"><a class="btn btn--small" href="#">Open</a></td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <aside class="stack">
                  <section class="decision-card" aria-labelledby="msg-dec-title" data-v41-change="f17 (I)">
                    <h2 class="decision-head" id="msg-dec-title">Decision</h2>
                    <div class="decision-body">
                      <div class="decision-facts">
                        <div class="decision-row"><span>Classification</span><strong>New instruction</strong></div>
                        <div class="decision-row" data-v41-today-only><span>Destination</span><strong><a class="mono" href="#engineer-read">DFD26031</a></strong></div>
                        <div class="decision-row" data-v41-today-only><span>Filed to</span><strong><a class="mono" href="#engineer-read">DFD26031</a></strong></div>
                        <div class="decision-row" data-v41-proposal-only><span>Case</span><strong><a class="mono" href="#engineer-read">DFD26031</a></strong></div>
                        <div class="decision-row">
                          <span>Decided</span>
                          <strong data-v41-today-only>14 Oct 14:12 <span class="provenance" title="Automated">[i]</span></strong>
                          <strong data-v41-proposal-only>14 Oct 14:12 · Automated</strong>
                        </div>
                      </div>
                      <div class="decision-actions">
                        <button class="btn btn--small" type="button">Correct classification</button>
                      </div>
                    </div>
                  </section>

                  <section class="decision-card" aria-labelledby="msg-case-title" data-v41-change="f18 (J)">
                    <h2 class="decision-head" id="msg-case-title">Linked case (Case tab)</h2>
                    <div class="decision-body">
                      <div class="decision-facts">
                        <div class="decision-row">
                          <span><a class="mono" href="#engineer-read"><strong>DFD26031</strong></a> · YK71 XWB · S. Morris</span>
                          <span class="status status--amber">Review</span>
                        </div>
                      </div>
                      <p class="muted" data-v41-today-only style="margin:0">Today: clicking Unlink posts PrepareUnlinkCase, claims a Case lease, reloads the page, and requires a second click on Confirm unlink.</p>
                      <div class="decision-actions">
                        <button class="btn btn--small btn--danger" type="button" data-dialog-open="unlinkCaseDialog">Unlink from Case</button>
                      </div>
                    </div>
                  </section>
                </aside>
              </div>
            </div>
          </article>
        </div>
        """)
    ))

    # 10. Upload & Upload Review (/Upload, /Upload/Group/{id})
    states.append((
        "upload-review",
        "10. Upload & Upload Review: Inspector-first focus order & clean decision panel (/Upload/Group/{id})",
        "upload.css",
        render_app_shell("upload", f"""
        <div class="up-surface">
          <header class="page-header up-head" data-v41-change="f19 (K)">
            <div class="page-title">
              <p class="eyebrow" data-v41-proposal-only>Files</p>
              <h1>Upload</h1>
              <p class="up-subtitle" data-v41-today-only>Review what Pegasus read from these files and choose where they belong.</p>
            </div>
            <div class="page-actions">
              {render_freshness("Received · 14 Oct 14:25")}
              <a class="btn" href="#upload">New upload</a>
            </div>
          </header>

          <div class="up-workspace" data-v41-change="f19 (K), f20">
            <!-- Inspector placed first in DOM so desktop keyboard Tab order matches visual left-to-right order -->
            <section class="up-inspector" aria-labelledby="up-insp-title">
              <header class="up-inspect-top">
                <strong id="up-insp-title">Files in this upload</strong>
                <span>1 of 3</span>
              </header>
              <div class="up-inspect-media">
                <div class="up-inspect-photo">
                  <img src="{TILE_URIS[0]}" alt="IMG_4021.jpg" />
                </div>
              </div>
              <div class="up-inspect-caption">
                <span class="mono">IMG_4021.jpg · JPEG image · 2.4 MB</span>
                <button class="btn btn--small" type="button" data-dialog-open="preview-media" data-preview-title="IMG_4021.jpg">Open</button>
              </div>
              <div class="up-filmstrip" role="list">
                <a class="up-film" href="#upload-review" aria-pressed="true"><img src="{TILE_URIS[0]}" alt="1" /><span>1</span></a>
                <a class="up-film" href="#upload-review" aria-pressed="false"><img src="{TILE_URIS[1 % len(TILE_URIS)]}" alt="2" /><span>2</span></a>
                <a class="up-film" href="#upload-review" aria-pressed="false"><span class="up-film-doc"><svg class="icon" aria-hidden="true"><use href="#icon-file-text" /></svg><small>PDF</small></span><span>3</span></a>
              </div>
            </section>

            <!-- Decision column second in DOM -->
            <section class="up-decision" aria-labelledby="up-dec-title">
              <section class="up-card">
                <header class="up-card-head">
                  <h2 id="up-dec-title">Proposed destination</h2>
                  <span class="status status--green">1 match</span>
                </header>
                <div class="up-card-body">
                  <p class="up-explainer" data-v41-today-only>
                    Select the Case below and confirm to attach all 3 uploaded files to that Case record.
                  </p>
                  <label class="row-button is-active" style="display:block;cursor:pointer">
                    <div class="cluster--between">
                      <span class="cluster"><input type="radio" name="cand" checked /> <strong class="mono">QDOS26214</strong> · <span class="mono">AB12 CDE</span></span>
                      <span class="status status--blue">Registration and Principal match</span>
                    </div>
                    <div class="muted" style="margin-top:4px">J. Patel · QDOS · With Engineer</div>
                  </label>

                  <div class="up-actions">
                    <button class="btn btn--primary" type="button">Review and add to Case</button>
                  </div>

                  <details class="up-search">
                    <summary>Find another Case</summary>
                    <form class="up-search-row" method="get" action="#">
                      <input type="hidden" name="inspect" value="0" data-v41-proposal-only />
                      <input type="search" placeholder="Case/PO, registration or claimant" />
                      <button class="btn btn--small" type="submit">Search</button>
                    </form>
                  </details>

                  <div class="cluster--between" style="border-top:1px solid var(--border);padding-top:12px">
                    <a class="btn btn--small" href="#cases">Leave undecided</a>
                    <button class="btn btn--small btn--danger" type="button">Discard upload</button>
                  </div>
                </div>
              </section>
            </section>
          </div>
        </div>
        """)
    ))

    # 11. Cases Queue (/Cases)
    states.append((
        "cases-queue",
        "11. Cases Queue: Complete Principal filter, clean footer & in-place preview (/Cases)",
        "cases-index.css",
        render_app_shell("cases", f"""
        <div class="stack">
          <header class="page-header">
            <div class="page-title">
              <p class="eyebrow">Work centre</p>
              <h1>Cases</h1>
            </div>
            <div class="page-actions">
              {render_freshness("Current · 14:32")}
              <a class="btn btn--primary" href="#create-case">
                <svg class="icon" aria-hidden="true"><use href="#icon-plus" /></svg>
                <span>New Case</span>
              </a>
            </div>
          </header>

          <section class="pane-layout pane-layout--3 queue-layout cases-queue" aria-label="Cases queues" data-v41-change="f21 (L)">
            <aside class="pane" aria-label="Queues">
              <form method="get" action="/Cases" class="scope-list" data-row-list>
                <button type="button" class="scope-button" aria-pressed="false"><span class="scope-visual-icon"><svg class="icon" aria-hidden="true"><use href="#icon-clock" /></svg></span><span>Not ready</span><span class="tabular">5</span></button>
                <button type="button" class="scope-button" aria-pressed="false"><span class="scope-visual-icon"><svg class="icon" aria-hidden="true"><use href="#icon-image" /></svg></span><span>Unassigned Images</span><span class="tabular">3</span></button>
                <button type="button" class="scope-button" aria-pressed="false"><span class="scope-visual-icon"><svg class="icon" aria-hidden="true"><use href="#icon-check-circle" /></svg></span><span>Review</span><span class="tabular">4</span></button>
                <button type="button" class="scope-button" aria-pressed="true"><span class="scope-visual-icon"><svg class="icon" aria-hidden="true"><use href="#icon-user" /></svg></span><span>With Engineer</span><span class="tabular">12</span></button>
                <button type="button" class="scope-button" aria-pressed="false"><span class="scope-visual-icon"><svg class="icon" aria-hidden="true"><use href="#icon-reply" /></svg></span><span>Queries</span><span class="tabular">2</span></button>
                <button type="button" class="scope-button" aria-pressed="false"><span class="scope-visual-icon"><svg class="icon" aria-hidden="true"><use href="#icon-file-text" /></svg></span><span>Triage</span><span class="tabular">4</span></button>
                <button type="button" class="scope-button" aria-pressed="false"><span class="scope-visual-icon"><svg class="icon" aria-hidden="true"><use href="#icon-pause" /></svg></span><span>Held</span><span class="tabular">2</span></button>
              </form>
            </aside>

            <div class="pane cases-list" aria-label="Cases list">
              <form method="get" class="filter-bar cases-filters">
                <div class="field filter-grow">
                  <label for="cq-q">Filter</label>
                  <input id="cq-q" type="search" placeholder="Case/PO, VRM or claimant" />
                </div>
                <div class="field">
                  <label for="cq-stage">Stage</label>
                  <select id="cq-stage"><option>All stages</option><option>With Engineer</option><option>Review</option></select>
                </div>
                <div class="field">
                  <label for="cq-prin">Principal</label>
                  <select id="cq-prin" data-v41-principal-filter>
                    <option value="">All principals (15 active)</option>
                    <option>AX</option><option>ALS</option><option>BC</option><option>BLACK</option><option>DFD</option>
                    <option>FW</option><option>KBS</option><option>MP</option><option>OAK</option><option>PCH</option>
                    <option>QCL</option><option>QDOS</option><option>RJS</option><option>SBL</option><option>YML</option>
                  </select>
                </div>
                <div class="filter-actions">
                  <button class="btn btn--primary" type="submit">Apply</button>
                </div>
              </form>

              <div class="pane-head">
                <h2 id="cases-tbl-title">All Open Cases</h2>
                <span class="meta">2 cases</span>
              </div>

              <div class="cases-table" data-row-list>
                <table class="table">
                  <thead>
                    <tr><th>Case/PO</th><th>Registration</th><th>Claimant</th><th>Principal</th><th>Stage</th><th>Engineer</th><th>Next action</th></tr>
                  </thead>
                  <tbody>
                    <tr class="is-selected" aria-selected="true">
                      <td class="mono"><a class="row-primary" href="#engineer-read">QDOS26214</a></td>
                      <td class="mono">AB12 CDE</td>
                      <td>J. Patel</td>
                      <td class="mono">QDOS</td>
                      <td><span class="status status--navy">With Engineer</span></td>
                      <td>R. Khan</td>
                      <td>Complete report</td>
                    </tr>
                    <tr>
                      <td class="mono"><a class="row-primary" href="#engineer-read">DFD26031</a></td>
                      <td class="mono">YK71 XWB</td>
                      <td>S. Morris</td>
                      <td class="mono">DFD</td>
                      <td><span class="status status--amber">Review</span></td>
                      <td class="muted">Unassigned</td>
                      <td>Assign Engineer</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <nav class="pagination pane-foot" aria-label="Cases pagination">
                <span>2 cases shown</span>
                <span class="muted" data-v41-today-only>Page 1 · newest first (shown even on 1-page / unpaged lists)</span>
              </nav>
            </div>

            <div class="pane cases-detail" aria-label="Quick detail">
              <div class="pane-head">
                <h2 id="cq-prev-title">Quick detail</h2>
                <a class="btn btn--small btn--dark" href="#engineer-read">
                  <svg class="icon" aria-hidden="true"><use href="#icon-arrow-right" /></svg>
                  <span>Open full Case</span>
                </a>
              </div>
              <div class="pane-body">
                <div class="detail-canvas stack">
                  <div class="detail-header">
                    <div>
                      <div class="eyebrow">Case/PO · AB12 CDE</div>
                      <h3 class="detail-title">QDOS26214</h3>
                    </div>
                    <span class="status status--navy">With Engineer</span>
                  </div>
                  <dl class="fact-grid cases-facts">
                    <div class="fact"><dt>Registration</dt><dd class="mono">AB12 CDE</dd></div>
                    <div class="fact"><dt>Vehicle</dt><dd>BMW 320d M Sport</dd></div>
                    <div class="fact"><dt>Claimant</dt><dd>J. Patel</dd></div>
                    <div class="fact"><dt>Principal</dt><dd>QDOS</dd></div>
                    <div class="fact"><dt>Engineer</dt><dd>Rashid Khan</dd></div>
                  </dl>
                  <div class="button-row">
                    <a class="btn btn--primary" href="#engineer-read">Open case</a>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
        """)
    ))

    # 12. Create Case (/Cases/Create — Seeded Review & Manual Create)
    states.append((
        "create-case",
        "12. Create Case: Seeded instruction review & Manual Create (/Cases/Create)",
        "",
        render_app_shell("cases", """
        <div class="stack">
          <header class="page-header" data-v41-change="f11, f22 (M)">
            <div class="page-title">
              <p class="eyebrow">Cases</p>
              <h1>Create case</h1>
            </div>
            <div class="page-actions">
              <a class="btn" href="#">Open file</a>
              <a class="btn" href="#mail-message">Open message</a>
              <a class="btn" href="#cases">
                <svg class="icon" aria-hidden="true" data-v41-today-only><use href="#icon-arrow-right" /></svg>
                <svg class="icon" aria-hidden="true" data-v41-proposal-only><use href="#icon-chevron-left" /></svg>
                <span>Cancel</span>
              </a>
            </div>
          </header>

          <div class="split" data-v41-change="f22 (M)">
            <section class="panel" aria-labelledby="cc-sum-title">
              <div class="panel-head"><h2 id="cc-sum-title">Instruction summary</h2></div>
              <div class="panel-body stack">
                <dl class="fact-grid">
                  <div class="fact"><dt>Principal</dt><dd>DFD <span class="status status--neutral">Extracted</span></dd></div>
                  <div class="fact"><dt>Vehicle registration</dt><dd class="mono">YK71 XWB <span class="status status--neutral">Extracted</span></dd></div>
                  <div class="fact"><dt>Claimant</dt><dd>Sarah Morris <span class="status status--neutral">Extracted</span></dd></div>
                  <div class="fact"><dt>Claim reference</dt><dd class="mono">DFD-88310 <span class="status status--neutral">Extracted</span></dd></div>
                </dl>

                <details open>
                  <summary class="btn btn--small">Change a value</summary>
                  <div class="form-grid form-grid--2" style="margin-top:12px" data-v41-draft-fields>
                    <div class="field">
                      <label for="cd-prin">Principal code</label>
                      <input id="cd-prin" value="DFD" />
                      <small class="muted" data-v41-today-only>Extracted from InstructionPdfParser: DFD</small>
                    </div>
                    <div class="field">
                      <label for="cd-vrm">Vehicle registration</label>
                      <input id="cd-vrm" class="mono" value="YK71 XWB" />
                      <small class="muted" data-v41-today-only>Extracted from SubjectLineVrmMatcher: YK71 XWB</small>
                    </div>
                    <div class="field">
                      <label for="cd-claimant">Claimant name</label>
                      <input id="cd-claimant" value="Sarah Morris" />
                      <small class="muted" data-v41-today-only>Extracted from InstructionPdfParser: Sarah Morris</small>
                    </div>
                    <div class="field">
                      <label for="cd-ref">Claim reference</label>
                      <input id="cd-ref" class="mono" value="DFD-88310" />
                    </div>
                    <div class="field field-wide">
                      <label class="req" for="cd-reason">Reason for change</label>
                      <input id="cd-reason" value="Corrected claimant spelling from instruction PDF" />
                    </div>
                  </div>
                </details>

                <div class="button-row">
                  <button class="btn btn--primary" type="button">Confirm and create case</button>
                </div>
              </div>
            </section>

            <aside class="stack">
              <section class="panel" aria-labelledby="cc-manual-title">
                <div class="panel-head"><h2 id="cc-manual-title">Manual New Case (/Cases/Create)</h2></div>
                <div class="panel-body stack">
                  <div class="field">
                    <label for="mc-type">Type</label>
                    <select id="mc-type"><option>Standard</option><option selected>Triage</option><option>Audit</option></select>
                  </div>
                  <div class="field">
                    <label class="req" for="mc-vrm">Vehicle registration</label>
                    <input id="mc-vrm" class="mono" value="LM20 TUV" />
                  </div>
                  <div class="field">
                    <label for="mc-prin">Principal code</label>
                    <input id="mc-prin" value="QDOS" />
                    <small class="field-hint muted" data-v41-today-only>Optional for Triage</small>
                  </div>
                  <div class="button-row">
                    <button class="btn btn--primary" type="button">Create case</button>
                  </div>
                </div>
              </section>
            </aside>
          </div>
        </div>
        """, hide_new_case=True)
    ))

    # 13. Triage Case (/Cases/{id} when CaseType == Triage)
    states.append((
        "triage-case",
        "13. Triage Case: Material preview, Response evidence & Case picker dialog (/Cases/{id})",
        "triage.css",
        render_app_shell("cases", f"""
        <article class="record triage-record" data-v41-change="f23 (N)">
          <div class="triage-sticky">
            <div class="ribbon triage-ribbon" aria-label="Triage identity">
              <div class="ribbon-item ribbon-ref">
                <div class="ribbon-label">Triage · KP21 NRO</div>
                <h1 class="ribbon-value">QDOS26210</h1>
              </div>
              <div class="ribbon-item">
                <div class="ribbon-label">Principal</div>
                <div class="ribbon-value">QDOS</div>
              </div>
              <div class="ribbon-item">
                <div class="ribbon-label">Opened</div>
                <div class="ribbon-value">13 Oct 2026</div>
              </div>
              <div class="ribbon-item">
                <div class="ribbon-label">Assigned to</div>
                <div class="ribbon-value">Rashid Khan</div>
              </div>
              <div class="ribbon-chips">
                <span class="status status--navy">Triage</span>
                <span class="status status--amber">Determination Made</span>
              </div>
              <div class="ribbon-actions">
                <button class="btn btn--small" type="button">Assign</button>
                <button class="btn btn--small btn--primary" type="button">Send outcome reply</button>
                <button class="btn btn--small" type="button">Link case</button>
                <button class="btn btn--small btn--danger" type="button">Cancel Triage</button>
                <a class="btn btn--small" href="#cases">
                  <svg class="icon" aria-hidden="true" data-v41-today-only><use href="#icon-arrow-right" /></svg>
                  <svg class="icon" aria-hidden="true" data-v41-proposal-only><use href="#icon-chevron-left" /></svg>
                  <span>Back to Cases</span>
                </a>
                {render_freshness("Current · 14:32")}
              </div>
            </div>
          </div>

          <div class="record-body stack">
            <div class="triage-split">
              <section class="panel" aria-labelledby="tri-mat-title">
                <div class="panel-head"><h2 id="tri-mat-title">Material</h2></div>
                <div class="panel-body stack">
                  <nav class="tabs">
                    <a class="tab" href="#triage-case">Photographs (4)</a>
                    <a class="tab" href="#triage-case" aria-current="page">Documents (2)</a>
                    <a class="tab" href="#triage-case">Source email</a>
                  </nav>
                  <table class="table">
                    <thead><tr><th>File</th><th class="right">Actions</th></tr></thead>
                    <tbody>
                      <tr>
                        <td>QDOS_Triage_Request_KP21NRO.pdf</td>
                        <td class="right">
                          <div class="cluster" style="justify-content:flex-end">
                            <button class="btn btn--small" type="button" data-v41-proposal-only data-dialog-open="preview-media" data-preview-title="QDOS_Triage_Request_KP21NRO.pdf">Preview</button>
                            <a class="btn btn--small" href="#">Save as</a>
                          </div>
                        </td>
                      </tr>
                      <tr>
                        <td>Claimant_Statement.pdf</td>
                        <td class="right">
                          <div class="cluster" style="justify-content:flex-end">
                            <button class="btn btn--small" type="button" data-v41-proposal-only data-dialog-open="preview-media" data-preview-title="Claimant_Statement.pdf">Preview</button>
                            <a class="btn btn--small" href="#">Save as</a>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              <section class="panel" aria-labelledby="tri-ass-title">
                <div class="panel-head"><h2 id="tri-ass-title">Assessment</h2></div>
                <div class="panel-body stack">
                  <dl class="fact-grid">
                    <div class="fact"><dt>Finding</dt><dd><span class="status status--green">Consistent</span></dd></div>
                    <div class="fact"><dt>Determination</dt><dd><span class="status status--blue">Proceed to full inspection</span></dd></div>
                  </dl>
                  <div class="field">
                    <label for="tri-resp-ev">Exact response evidence</label>
                    <select id="tri-resp-ev">
                      <option data-v41-today-only>14 Oct 11:05 · &lt;AM0PR01MB482199@eurprd01.prod.exchangelabs.com&gt;</option>
                      <option data-v41-today-only>14 Oct 10:12 · Sent evidence 8f2b1c90-4a12-4d99-b120-991827364510</option>
                      <option data-v41-proposal-only>14 Oct 11:05 · Sent to claims@qdos.example (Re: Triage KP21 NRO)</option>
                      <option data-v41-proposal-only>14 Oct 10:12 · Outcome reply from desk@collisionengineers.co.uk</option>
                    </select>
                  </div>
                  <div class="button-row">
                    <button class="btn btn--primary" type="button">Record response</button>
                  </div>
                </div>
              </section>
            </div>

            <section class="dialog dialog--compact v41-inline-dialog" aria-labelledby="tri-link-dlg-title">
              <div class="dialog-head">
                <h2 id="tri-link-dlg-title">Link to instruction Case</h2>
                <button class="icon-button dialog-close" type="button" aria-label="Close"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button>
              </div>
              <div class="dialog-body stack">
                <div class="field" data-v41-today-only>
                  <label class="req" for="tri-raw-guid">Case ID (Today requires raw 36-char GUID!)</label>
                  <input id="tri-raw-guid" class="mono" value="3b9a8410-6c12-4e88-9102-445566778899" />
                </div>
                <div class="field" data-v41-proposal-only>
                  <label class="req" for="tri-picker">Instruction Case (QDOS reference or registration)</label>
                  <input id="tri-picker" role="combobox" aria-expanded="true" value="QDOS26214 · AB12 CDE · J. Patel" />
                </div>
                <div class="field">
                  <label class="req" for="tri-link-reason">Reason</label>
                  <textarea id="tri-link-reason" rows="2">Full instruction received following Triage determination.</textarea>
                </div>
              </div>
              <div class="dialog-foot">
                <button class="btn" type="button">Cancel</button>
                <button class="btn btn--primary" type="button">Link case</button>
              </div>
            </section>
          </div>
        </article>
        """)
    ))

    # 14. Unidentified & Vehicle Images (/Unidentified/{id}, /VehicleImages/{id})
    states.append((
        "unidentified-images",
        "14. Unidentified & Vehicle Images: Deduplicated facts, Case pairing dialog & Chaser (/VehicleImages/{id})",
        "unidentified.css,image-record.css,pre-case-images.css",
        render_app_shell("cases", f"""
        <div class="stack">
          <header class="page-header" data-v41-change="f11, f24 (O)">
            <div class="page-title">
              <p class="eyebrow">Image-initiated Case</p>
              <h1 class="mono">IMG-2026-0019</h1>
            </div>
            <div class="page-actions">
              <a class="btn" href="#cases">
                <svg class="icon" aria-hidden="true" data-v41-today-only><use href="#icon-arrow-right" /></svg>
                <svg class="icon" aria-hidden="true" data-v41-proposal-only><use href="#icon-chevron-left" /></svg>
                <span>Back to Cases</span>
              </a>
              {render_freshness("Current · 14:32")}
            </div>
          </header>

          <article class="record image-record" data-v41-change="f24 (O)">
            <div class="ribbon">
              <div class="ribbon-item ribbon-ref">
                <div class="ribbon-label">Image reference · AB12 CDE</div>
                <div class="ribbon-value">IMG-2026-0019</div>
              </div>
              <div class="ribbon-item">
                <div class="ribbon-label">Registered</div>
                <div class="ribbon-value"><time>14 Oct 2026 09:15</time></div>
              </div>
              <div class="ribbon-item">
                <div class="ribbon-label">Images</div>
                <div class="ribbon-value">14</div>
              </div>
              <div class="ribbon-item">
                <div class="ribbon-label">Principal</div>
                <div class="ribbon-value">QDOS</div>
              </div>
              <div class="ribbon-chips">
                <span class="status status--amber">Awaiting instruction</span>
              </div>
            </div>

            <div class="image-record-body stack">
              <div class="image-record-grid">
                <section class="panel" aria-labelledby="img-rec-title">
                  <div class="panel-head"><h2 id="img-rec-title">Record</h2></div>
                  <div class="panel-body stack">
                    <dl class="fact-grid">
                      <div class="fact" data-v41-today-only><dt>Image-initiated reference</dt><dd class="mono">IMG-2026-0019 (Duplicate of ribbon)</dd></div>
                      <div class="fact" data-v41-today-only><dt>Vehicle registration</dt><dd class="mono">AB12 CDE (Duplicate of ribbon)</dd></div>
                      <div class="fact" data-v41-today-only><dt>Registered</dt><dd>14 Oct 2026 09:15 (Duplicate of ribbon)</dd></div>
                      <div class="fact"><dt>Source</dt><dd>Approved mailbox · desk@collisionengineers.co.uk</dd></div>
                      <div class="fact"><dt>Original file</dt><dd>AB12CDE_Workshop_Photos.zip</dd></div>
                      <div class="fact"><dt>Case association</dt><dd>Not paired</dd></div>
                    </dl>
                  </div>
                </section>

                <section class="panel" aria-labelledby="img-cand-title">
                  <div class="panel-head">
                    <h2 id="img-cand-title">Eligible case candidates</h2>
                    <button class="btn btn--primary btn--small" type="button" data-v41-proposal-only>Pair with Case…</button>
                  </div>
                  <div class="panel-body stack">
                    <table class="table">
                      <thead>
                        <tr>
                          <th>Case/PO</th>
                          <th data-v41-proposal-only>Registration</th>
                          <th data-v41-proposal-only>Claimant</th>
                          <th>Principal</th>
                          <th data-v41-proposal-only>Stage</th>
                          <th class="right" data-v41-proposal-only>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td class="mono"><a href="#engineer-read">QDOS26214</a></td>
                          <td class="mono" data-v41-proposal-only>AB12 CDE</td>
                          <td data-v41-proposal-only>J. Patel</td>
                          <td class="mono">QDOS</td>
                          <td data-v41-proposal-only><span class="status status--navy">With Engineer</span></td>
                          <td class="right" data-v41-proposal-only><button class="btn btn--small btn--primary" type="button">Pair</button></td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </section>
              </div>

              <div class="v41-card-pair">
                <section class="dialog dialog--compact v41-inline-dialog" aria-labelledby="unid-dismiss-title">
                  <div class="dialog-head">
                    <h2 id="unid-dismiss-title">Dismiss registration reading (AB12 CDE)</h2>
                    <button class="icon-button dialog-close" type="button" aria-label="Close"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button>
                  </div>
                  <div class="dialog-body stack">
                    <div class="field">
                      <label class="req" for="unid-reason">Reason</label>
                      <textarea id="unid-reason" rows="2">Plate belongs to recovery truck in background.</textarea>
                    </div>
                  </div>
                  <div class="dialog-foot">
                    <button class="btn" type="button">Cancel</button>
                    <button class="btn btn--danger" type="button">Dismiss reading</button>
                  </div>
                </section>

                <section class="dialog dialog--compact v41-inline-dialog" aria-labelledby="chaser-dlg-title" data-v41-change="f25">
                  <div class="dialog-head">
                    <h2 id="chaser-dlg-title">Send chaser · QDOS26214</h2>
                    <button class="icon-button dialog-close" type="button" aria-label="Close"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button>
                  </div>
                  <div class="dialog-body stack">
                    <div class="field">
                      <label class="req" for="ch-to">To</label>
                      <input id="ch-to" value="claims@qdos.example" required />
                    </div>
                    <div class="field">
                      <label class="req" for="ch-sub">Subject</label>
                      <input id="ch-sub" value="Chase — QDOS26214 — AB12 CDE" required />
                    </div>
                    <div class="field">
                      <label class="req" for="ch-msg">Message</label>
                      <textarea id="ch-msg" rows="2" required>Please confirm when the vehicle will be available for inspection.</textarea>
                    </div>
                  </div>
                  <div class="dialog-foot">
                    <a class="btn" href="#unidentified-images" data-v41-proposal-only>Cancel</a>
                    <button class="btn btn--primary" type="button">Send</button>
                  </div>
                </section>
              </div>
            </div>
          </article>
        </div>
        """)
    ))

    # 15. Administration Hub & Staff Accounts (/Administration, /Administration/Accounts)
    states.append((
        "admin-accounts",
        "15. Administration Hub & Staff Accounts (/Administration, /Administration/Accounts)",
        "admin.css",
        render_app_shell("admin", f"""
        <div class="stack">
          <header class="page-header">
            <div class="page-title">
              <p class="eyebrow">Administration</p>
              <h1>Staff accounts &amp; roles</h1>
            </div>
            <div class="page-actions">
              {render_freshness("Current · 14:32")}
              <button class="btn btn--primary" type="button">Create account</button>
            </div>
          </header>

          <div class="admin-layout" data-v41-change="f31, f32 (T)">
            {render_admin_nav("accounts")}
            <div class="stack">
              <div class="notice notice--success" role="status" data-v41-proposal-only>
                <svg class="icon" aria-hidden="true"><use href="#icon-check-circle" /></svg>
                <div><strong>Temporary password issued</strong><div>Temporary password for <strong>r.khan</strong>: <code class="mono">Pegasus!8841-Temp</code>. Share it once; they must replace it at next sign-in.</div></div>
              </div>

              <section class="panel" aria-labelledby="acc-tbl-title">
                <div class="panel-head"><h2 id="acc-tbl-title">Accounts</h2></div>
                <div class="table-wrap no-border">
                  <table class="table">
                    <thead><tr><th>Username</th><th>Display name</th><th>Role</th><th>Sign-off</th><th>Glass's</th><th>State</th><th class="right">Actions</th></tr></thead>
                    <tbody>
                      <tr>
                        <td class="mono">alex</td>
                        <td>Alex Jordan</td>
                        <td>Administrator</td>
                        <td>Eligible · MIMI</td>
                        <td><span class="status status--green">Saved</span></td>
                        <td><span class="status status--navy">Active</span></td>
                        <td class="right"><button class="btn btn--small" type="button">Settings</button></td>
                      </tr>
                      <tr>
                        <td class="mono">r.khan</td>
                        <td>Rashid Khan</td>
                        <td>Engineer</td>
                        <td>Eligible · IAEA</td>
                        <td><span class="status status--green">Saved</span></td>
                        <td><span class="status status--navy">Active</span></td>
                        <td class="right"><button class="btn btn--small" type="button">Settings</button></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              <div class="v41-card-pair">
                <section class="dialog dialog--compact v41-inline-dialog" aria-labelledby="glass-cred-title" data-v41-change="f32 (T)">
                  <div class="dialog-head">
                    <h2 id="glass-cred-title">Glass's login · Rashid Khan</h2>
                    <button class="icon-button dialog-close" type="button" aria-label="Close"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button>
                  </div>
                  <div class="dialog-body stack">
                    <dl class="fact-grid">
                      <div class="fact"><dt>State</dt><dd><span class="status status--green">Saved</span></dd></div>
                      <div class="fact"><dt>Glass's username</dt><dd class="mono">rkhan@collisionengineers.co.uk</dd></div>
                      <div class="fact" data-v41-today-only><dt>Generation (Raw int!)</dt><dd class="mono">3</dd></div>
                      <div class="fact" data-v41-today-only><dt>Version (Raw int!)</dt><dd class="mono">7</dd></div>
                      <div class="fact"><dt>Updated</dt><dd>10 Oct 2026 09:12</dd></div>
                    </dl>
                  </div>
                  <div class="dialog-foot">
                    <button class="btn btn--danger" type="button">Remove login</button>
                    <button class="btn" type="button">Close</button>
                    <button class="btn btn--primary" type="button">Save login</button>
                  </div>
                </section>

                <section class="dialog dialog--compact v41-inline-dialog" aria-labelledby="del-acc-title" data-v41-change="f32 (T)">
                  <div class="dialog-head">
                    <h2 id="del-acc-title">Delete account · t.temp</h2>
                    <button class="icon-button dialog-close" type="button" aria-label="Close"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button>
                  </div>
                  <div class="dialog-body stack">
                    <p style="margin:0">Delete <strong>t.temp</strong>? This cannot be undone.</p>
                  </div>
                  <div class="dialog-foot">
                    <button class="btn" type="button">Cancel</button>
                    <button class="btn btn--danger" type="button">Delete account</button>
                  </div>
                </section>
              </div>
            </div>
          </div>

          <section class="panel" data-v41-today-only>
            <div class="panel-head"><h2>Temporary password (rendered outside .admin-layout at bottom of page today)</h2></div>
            <div class="panel-body">Temporary password for r.khan: <code class="mono">Pegasus!8841-Temp</code></div>
          </section>
        </div>
        """)
    ))

    # 16. Administration: Contacts & Principal Edit (/Administration/Contacts)
    states.append((
        "admin-contacts",
        "16. Administration › Contacts: Principal API, Default location & Replace code dialog (/Administration/Contacts/Edit)",
        "admin.css",
        render_app_shell("admin", f"""
        <div class="stack">
          <header class="page-header">
            <div class="page-title">
              <p class="eyebrow">Administration</p>
              <h1>Davison Flynn Duke Solicitors</h1>
            </div>
            <div class="page-actions">
              {render_freshness("Current · 14:32")}
            </div>
          </header>

          <div class="admin-layout" data-v41-change="f33 (U)">
            {render_admin_nav("contacts")}
            <div class="stack">
              <nav class="tabs" aria-label="Davison Flynn Duke Solicitors" data-v41-contact-tabs>
                <a class="tab" href="#contact-tab-details" data-contact-tab="details">Contact</a>
                <a class="tab" href="#contact-tab-gen" data-contact-tab="gen">Report generation</a>
                <a class="tab" href="#contact-tab-send" data-contact-tab="send">Report sending</a>
                <a class="tab" href="#contact-tab-salvage" data-contact-tab="salvage">Salvage matrix</a>
                <a class="tab" href="#contact-tab-loc" data-contact-tab="loc">Default inspection location</a>
                <a class="tab" aria-current="page" href="#contact-tab-api" data-contact-tab="api">Principal API</a>
              </nav>

              <section class="panel" data-contact-panel="details" hidden aria-labelledby="prin-det-title">
                <div class="panel-head">
                  <h2 id="prin-det-title">Contact details</h2>
                  <div class="cluster">
                    <span class="status status--navy">Principal</span>
                    <span class="status status--neutral mono">DFD</span>
                    <button class="btn btn--small" type="button" data-dialog-open="replace-principal">Replace code…</button>
                  </div>
                </div>
                <div class="panel-body stack">
                  <div class="form-grid form-grid--2">
                    <div class="field"><label class="req">Name</label><input value="Davison Flynn Duke Solicitors" /></div>
                    <div class="field"><label>Main e-mail</label><input value="claims@dfd-solicitors.co.uk" /></div>
                    <div class="field"><label>Telephone</label><input value="0161 496 0820" /></div>
                    <div class="field"><label>Inspection mode</label><input value="Physical or Image Based" readonly /></div>
                  </div>
                  <div class="button-row"><button class="btn btn--primary" type="button">Save contact</button></div>
                </div>
              </section>

              <section class="panel" data-contact-panel="gen" hidden aria-labelledby="prin-gen-title">
                <div class="panel-head"><h2 id="prin-gen-title">Report generation</h2></div>
                <div class="panel-body stack">
                  <div class="form-grid form-grid--2">
                    <div class="field"><label>Default labour rate card</label><select><option selected>Standard Mechanical &amp; Body (£48.00/hr)</option><option>Prestige &amp; Specialist (£62.00/hr)</option></select></div>
                    <div class="field"><label>Valuation guide</label><select><option selected>Glass's Guide</option><option>CAP HPI</option></select></div>
                  </div>
                  <div class="field"><label>Notes on every Case</label><textarea rows="3">Ensure total loss figures are confirmed with handler before sending report. Include signed fee note PDF.</textarea></div>
                  <div class="button-row"><button class="btn btn--primary" type="button">Save report generation</button></div>
                </div>
              </section>

              <section class="panel" data-contact-panel="send" hidden aria-labelledby="prin-send-title">
                <div class="panel-head"><h2 id="prin-send-title">Report sending</h2></div>
                <div class="panel-body stack">
                  <div class="form-grid form-grid--2">
                    <div class="field">
                      <label>Default To</label>
                      <input value="claims@dfd-solicitors.co.uk" />
                      <p class="hint">Used when the instruction thread has no reply address.</p>
                    </div>
                    <div class="field">
                      <label>Always Cc</label>
                      <input value="handler@dfd-solicitors.co.uk" />
                      <p class="hint">Added to every report e-mail for this Principal.</p>
                    </div>
                  </div>
                  <div class="button-row"><button class="btn btn--primary" type="button">Save report sending</button></div>
                </div>
              </section>

              <section class="panel" data-contact-panel="salvage" hidden aria-labelledby="prin-salv-title">
                <div class="panel-head"><h2 id="prin-salv-title">Salvage matrix</h2></div>
                <div class="panel-body stack">
                  <table class="table">
                    <thead><tr><th>Category</th><th class="num">Up to 3 yrs (% PAV)</th><th class="num">4–7 yrs (% PAV)</th><th class="num">8+ yrs (% PAV)</th></tr></thead>
                    <tbody>
                      <tr><td>Category S</td><td class="num">28%</td><td class="num">22%</td><td class="num">16%</td></tr>
                      <tr><td>Category N</td><td class="num">35%</td><td class="num">28%</td><td class="num">20%</td></tr>
                    </tbody>
                  </table>
                  <div class="button-row"><button class="btn btn--primary" type="button">Save salvage matrix</button></div>
                </div>
              </section>

              <section class="panel" data-contact-panel="api" aria-labelledby="prin-api-title">
                <div class="panel-head">
                  <h2 id="prin-api-title">Principal API</h2>
                  <span class="status status--navy chip--navy" data-v41-proposal-only>Active</span>
                </div>
                <div class="panel-body stack">
                  <dl class="fact-grid">
                    <div class="fact"><dt>Submission endpoint</dt><dd><code class="mono">/api/principal/v1/submissions</code></dd></div>
                    <div class="fact">
                      <dt>State</dt>
                      <dd data-v41-today-only>Active (raw unstyled <code class="mono">dl.definition-list</code>)</dd>
                      <dd data-v41-proposal-only><span class="status status--navy chip--navy">Active</span></dd>
                    </div>
                  </dl>
                  <div class="button-row">
                    <button class="btn btn--primary" type="button">Reset API key</button>
                    <button class="btn" type="button">Pause</button>
                    <button class="btn btn--danger" type="button">Revoke</button>
                  </div>
                </div>
              </section>

              <section class="panel" data-contact-panel="loc" aria-labelledby="prin-loc-title">
                <div class="panel-head"><h2 id="prin-loc-title">Default inspection location</h2></div>
                <div class="panel-body stack">
                  <label class="choice"><input type="checkbox" /> <span>Default to Image Based Assessment</span></label>
                  <div class="form-grid form-grid--2">
                    <div class="field">
                      <label for="loc-lbl" data-v41-today-only>Location label (optional)</label>
                      <label for="loc-lbl" data-v41-proposal-only>Location label</label>
                      <input id="loc-lbl" value="DFD Manchester Receiving Yard" />
                    </div>
                    <div class="field">
                      <label for="loc-pc" data-v41-today-only>Postcode (optional)</label>
                      <label for="loc-pc" data-v41-proposal-only>Postcode</label>
                      <input id="loc-pc" value="M1 4BT" />
                    </div>
                  </div>
                  <div class="button-row">
                    <button class="btn btn--primary" type="button">Save default location</button>
                  </div>
                </div>
              </section>

              <section class="dialog dialog--compact v41-inline-dialog" id="replace-principal" aria-labelledby="rep-prin-title">
                <div class="dialog-head">
                  <h2 id="rep-prin-title">Replace DFD</h2>
                  <button class="icon-button dialog-close" type="button" aria-label="Close"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button>
                </div>
                <div class="dialog-body stack">
                  <p style="margin:0">42 allocated cases remain with their existing references.</p>
                  <div class="field">
                    <label class="req" for="succ-code">New principal code</label>
                    <input id="succ-code" class="mono" value="DFDL" />
                  </div>
                </div>
                <div class="dialog-foot">
                  <button class="btn" type="button">Cancel</button>
                  <button class="btn btn--danger" type="button">Replace principal code</button>
                </div>
              </section>
            </div>
          </div>
        </div>
        """)
    ))

    # 17. Administration: Workflow Configuration & Mail Settings (/Administration/Configuration, /Administration/Mailboxes)
    states.append((
        "admin-config-mail",
        "17. Administration › Workflow Configuration & Mail Settings (/Administration/Configuration, /Administration/Mailboxes)",
        "admin.css",
        render_app_shell("admin", f"""
        <div class="stack">
          <header class="page-header" data-v41-change="f34 (V)">
            <div class="page-title">
              <p class="eyebrow" data-v41-proposal-only>Administration</p>
              <h1>Workflow configuration &amp; Mail settings</h1>
            </div>
            <div class="page-actions">
              {render_freshness("Current · 14:32")}
            </div>
          </header>

          <div class="admin-layout">
            {render_admin_nav("configuration")}
            <div class="stack">
              <section class="panel" id="admin-sec-configuration" aria-labelledby="wf-cfg-title" data-v41-change="f34 (V)">
                <div class="panel-head"><h2 id="wf-cfg-title">Workflow settings</h2></div>
                <form class="panel-body stack" method="post" action="#">
                  <div class="form-grid form-grid--3">
                    <div class="field">
                      <label for="wf-chase">Chase interval (days)</label>
                      <input id="wf-chase" type="number" min="1" max="30" value="3" />
                      <span class="field-hint muted" data-v41-today-only>1 to 30</span>
                    </div>
                    <div class="field">
                      <label for="wf-due">Report due target (working days)</label>
                      <input id="wf-due" type="number" min="1" max="30" value="5" />
                      <span class="field-hint muted" data-v41-today-only>1 to 30</span>
                    </div>
                    <div class="field">
                      <label for="wf-triage">Triage target (hours)</label>
                      <input id="wf-triage" type="number" min="1" max="168" value="24" />
                      <span class="field-hint muted" data-v41-today-only>1 to 168</span>
                    </div>
                  </div>
                  <div class="button-row">
                    <button class="btn btn--primary" type="button">Save workflow settings</button>
                  </div>
                </form>
              </section>

              <section class="panel" aria-labelledby="lrc-title" data-v41-change="f34 (V)">
                <div class="panel-head"><h2 id="lrc-title">Labour-rate cards</h2></div>
                <div class="table-wrap no-border">
                  <table class="table">
                    <thead><tr><th>Card</th><th class="num">Hourly rate (£)</th><th class="right">Action</th></tr></thead>
                    <tbody>
                      <tr>
                        <td>Standard Mechanical &amp; Body</td>
                        <td class="num"><input type="number" step="0.50" value="48.00" style="max-width:120px;text-align:right" aria-label="Hourly rate" /></td>
                        <td class="right"><button class="btn btn--small btn--primary" type="button">Save</button></td>
                      </tr>
                      <tr>
                        <td>Prestige &amp; Specialist</td>
                        <td class="num"><input type="number" step="0.50" value="62.00" style="max-width:120px;text-align:right" aria-label="Hourly rate" /></td>
                        <td class="right"><button class="btn btn--small btn--primary" type="button">Save</button></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              <section class="panel" id="admin-sec-mailboxes" aria-labelledby="mbx-title" data-v41-change="f35 (W)">
                <div class="panel-head">
                  <h2 id="mbx-title">Approved mailboxes (/Administration/Mailboxes)</h2>
                  <button class="btn btn--primary btn--small" type="button" data-dialog-open="new-mailbox-dialog">Add mailbox</button>
                </div>
                <div class="table-wrap no-border">
                  <table class="table">
                    <thead><tr><th>Address</th><th>Purpose</th><th>Polling</th><th>Last poll</th><th class="right">Actions</th></tr></thead>
                    <tbody>
                      <tr>
                        <td class="mono">instructions@collisionengineers.co.uk</td>
                        <td>Intake &amp; Staff send</td>
                        <td><span class="status status--green">Active</span></td>
                        <td>14 Oct 14:31</td>
                        <td class="right"><button class="btn btn--small" type="button">Test connection</button></td>
                      </tr>
                      <tr>
                        <td class="mono">desk@collisionengineers.co.uk</td>
                        <td>Intake &amp; Triage</td>
                        <td><span class="status status--green">Active</span></td>
                        <td>14 Oct 14:31</td>
                        <td class="right"><button class="btn btn--small" type="button">Test connection</button></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              <section class="panel" data-v41-today-only>
                <div class="panel-head">
                  <h2>Mail categories (Obsolete editable panel — ADR-0069 fixed the closed 11 categories)</h2>
                  <button class="btn btn--dark btn--small" type="button">Add category</button>
                </div>
                <div class="panel-body muted">Editable category rows shown here today despite ADR-0069 / FRD-20 closing the 11 categories.</div>
              </section>

              <section class="panel" id="admin-sec-email-templates" aria-labelledby="emt-title">
                <div class="panel-head"><h2 id="emt-title">E-mail templates (/Administration/EmailTemplates)</h2></div>
                <div class="panel-body stack">
                  <div class="form-grid form-grid--2">
                    <div class="field"><label>Template</label><select><option selected>Standard Report Delivery</option><option>Chaser — Vehicle Availability</option><option>Triage Outcome Reply</option></select></div>
                    <div class="field"><label>Subject pattern</label><input value="Engineering Report — {{CaseReference}} — {{Registration}}" /></div>
                  </div>
                  <div class="field"><label>Body template</label><textarea rows="2">Good afternoon,\n\nPlease find attached our engineering report for {{Registration}} ({{CaseReference}}).</textarea></div>
                  <div class="button-row"><button class="btn btn--primary" type="button">Save template</button></div>
                </div>
              </section>

              <section class="panel" id="admin-sec-valuation-presets" aria-labelledby="vp-title">
                <div class="panel-head"><h2 id="vp-title">Valuation presets (/Administration/ValuationPresets)</h2></div>
                <div class="table-wrap no-border">
                  <table class="table">
                    <thead><tr><th>Preset</th><th>Guides</th><th class="right">Action</th></tr></thead>
                    <tbody>
                      <tr><td>Standard Retail &amp; Trade</td><td>Glass's Retail, Glass's Trade, CAP Clean</td><td class="right"><button class="btn btn--small" type="button">Edit</button></td></tr>
                    </tbody>
                  </table>
                </div>
              </section>
            </div>
          </div>
        </div>
        """)
    ))

    # 18. Administration: Logs, Problem Reports, AI Jobs & Automation
    states.append((
        "admin-logs-ops",
        "18. Administration › Logs, Problem Reports, AI Jobs & Automation (/Administration/Logs, /ProblemReports, /AiJobs)",
        "admin.css,logs.css",
        render_app_shell("admin", f"""
        <div class="stack">
          <header class="page-header">
            <div class="page-title">
              <p class="eyebrow">Administration</p>
              <h1>Logs, Problem reports &amp; AI jobs</h1>
            </div>
            <div class="page-actions">
              {render_freshness("Current · 14:32")}
            </div>
          </header>

          <div class="admin-layout" data-v41-change="f36 (X), f37, f38 (Y)">
            {render_admin_nav("logs")}
            <div class="stack">
              <section class="panel" id="admin-sec-logs" aria-labelledby="act-logs-title" data-v41-change="f36 (X)">
                <div class="panel-head">
                  <h2 id="act-logs-title">Action logs (/Administration/Logs)</h2>
                  <div class="cluster">
                    <input type="search" placeholder="Filter logs…" style="min-height:32px;width:200px" data-v41-log-filter />
                  </div>
                </div>
                <div class="table-wrap no-border">
                  <table class="table" data-v41-log-table>
                    <thead><tr><th>When</th><th>Actor</th><th>Action</th><th>Subject</th><th>Detail</th></tr></thead>
                    <tbody>
                      <tr>
                        <td class="mono">14 Oct 14:28</td>
                        <td>
                          <span class="status-chip status-chip--neutral" data-v41-today-only>AI (unstyled legacy class)</span>
                          <span class="status status--neutral" data-v41-proposal-only>AI</span>
                        </td>
                        <td>Completed AI Proposal</td>
                        <td class="mono"><a href="#engineer-read">QDOS26214</a></td>
                        <td>Candidate repair spec generated</td>
                      </tr>
                      <tr>
                        <td class="mono">14 Oct 14:12</td>
                        <td><span class="status status--navy">System</span></td>
                        <td>Allocated Case reference</td>
                        <td class="mono"><a href="#engineer-read">DFD26031</a></td>
                        <td>Created from instructions@collisionengineers.co.uk</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <details class="panel" open data-v41-today-only style="margin:12px">
                  <summary class="panel-head">Recorded counts and processing times (Internal cache telemetry exposed today!)</summary>
                  <div class="panel-body muted">Cache entries: 42 · Cache bytes: 1,492,012 · Active cache reads: 0 · Cache hits since Web start: 814</div>
                </details>
              </section>

              <section class="panel" id="admin-sec-problem-reports" aria-labelledby="pr-adm-title" data-v41-change="f38 (Y)">
                <div class="panel-head"><h2 id="pr-adm-title">Problem reports (/Administration/ProblemReports)</h2></div>
                <div class="table-wrap no-border">
                  <table class="table">
                    <thead><tr><th>When</th><th>Who</th><th>Page</th><th>Case</th><th>What happened</th><th>Status</th><th class="right">Actions</th></tr></thead>
                    <tbody>
                      <tr data-problem-row>
                        <td>
                          <span>14 Oct 13:40</span>
                          <small class="mono" data-v41-today-only>9f41c820-11b2-4e09-8a71-554433221100</small>
                        </td>
                        <td>R. Khan</td>
                        <td class="mono">/Cases/QDOS26214</td>
                        <td class="mono"><a href="#engineer-read">QDOS26214</a></td>
                        <td>Glass's window closed before import completed</td>
                        <td><span class="status status--amber" data-problem-status>Unknown</span></td>
                        <td class="right">
                          <button class="btn btn--small" type="button" data-v41-proposal-only data-dialog-open="problem-report-dialog">Resolve outcome…</button>
                          <div class="stack" data-v41-today-only style="text-align:left;max-width:220px">
                            <small class="muted">Search the approved GitHub repository for this report ID before choosing an outcome.</small>
                            <input type="number" placeholder="Matching issue #" />
                            <button class="btn btn--small" type="button">Confirm issue</button>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              <section class="panel" id="admin-sec-ai-jobs" aria-labelledby="aij-adm-title" data-v41-change="f38 (Y)">
                <div class="panel-head">
                  <h2 id="aij-adm-title">AI jobs (/Administration/AiJobs)</h2>
                  <span class="meta">1 active · 1 failed · Active</span>
                </div>
                <div class="table-wrap no-border">
                  <table class="table">
                    <thead><tr><th>Job</th><th>Subject</th><th>Created</th><th>State</th><th class="right">Action</th></tr></thead>
                    <tbody>
                      <tr data-ai-job-row>
                        <td><strong>Repair spec</strong><small class="admin-job-detail">Target 55% of PAV</small></td>
                        <td class="mono">
                          <span data-v41-today-only>QDOS26214</span>
                          <a href="#engineer-read" data-v41-proposal-only>QDOS26214</a>
                        </td>
                        <td>14 Oct 14:30</td>
                        <td><span class="status status--blue" data-ai-job-status>Running</span></td>
                        <td class="right">
                          <button class="btn btn--small btn--danger" type="button" data-v41-proposal-only data-dialog-open="stop-ai-job-dialog">Stop…</button>
                          <div class="cluster" data-v41-today-only style="justify-content:flex-end">
                            <input placeholder="Reason" style="width:120px" />
                            <button class="btn btn--small btn--danger" type="button">Stop</button>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              <section class="panel" id="admin-sec-reports" aria-labelledby="adm-rep-title">
                <div class="panel-head"><h2 id="adm-rep-title">Management Reports (/Administration/Reports)</h2></div>
                <div class="panel-body stack">
                  <dl class="fact-grid">
                    <div class="fact"><dt>Instructions received (30 d)</dt><dd class="tabular">184</dd></div>
                    <div class="fact"><dt>Reports dispatched (30 d)</dt><dd class="tabular">169</dd></div>
                    <div class="fact"><dt>Median turnaround</dt><dd class="tabular">3.2 working days</dd></div>
                  </dl>
                </div>
              </section>

              <section class="panel" id="admin-sec-health" aria-labelledby="adm-hlth-title">
                <div class="panel-head"><h2 id="adm-hlth-title">Service health (/Administration/Health)</h2></div>
                <div class="table-wrap no-border">
                  <table class="table">
                    <thead><tr><th>Component</th><th>State</th><th>Detail</th></tr></thead>
                    <tbody>
                      <tr><td>SQL Database</td><td><span class="status status--green">Healthy</span></td><td>14 ms query latency</td></tr>
                      <tr><td>Blob Storage</td><td><span class="status status--green">Healthy</span></td><td>Connected</td></tr>
                      <tr><td>Background Worker</td><td><span class="status status--green">Healthy</span></td><td>Heartbeat 12 s ago</td></tr>
                    </tbody>
                  </table>
                </div>
              </section>

              <section class="panel" id="admin-sec-release-notes" aria-labelledby="adm-rn-title" data-v41-change="f37">
                <div class="panel-head"><h2 id="adm-rn-title">Release notes (/Administration/ReleaseNotes)</h2></div>
                <div class="table-wrap no-border">
                  <table class="table">
                    <thead><tr><th>Version</th><th>Title</th><th>Published</th><th class="right" data-v41-proposal-only>Action</th></tr></thead>
                    <tbody>
                      <tr>
                        <td class="mono">v2026.10</td>
                        <td>One-type Contacts &amp; Report dispatch</td>
                        <td>13 Oct 2026</td>
                        <td class="right" data-v41-proposal-only><button class="btn btn--small" type="button" data-dialog-open="release-note-edit-dialog">Edit</button></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              <section class="panel" id="admin-sec-automation" aria-labelledby="adm-auto-title" data-v41-change="f38 (Y)">
                <div class="panel-head"><h2 id="adm-auto-title">Automation &amp; AI (/Administration/Automation)</h2></div>
                <div class="panel-body stack">
                  <label class="choice"><input type="checkbox" checked /> <span>Automatically extract instruction fields from incoming PDFs</span></label>
                  <label class="choice"><input type="checkbox" checked /> <span>Automatically read vehicle registrations (VRM) on incoming photos</span></label>
                  <label class="choice"><input type="checkbox" checked /> <span>Generate AI repair specification draft when Glass's calculation is saved</span></label>
                  <div class="button-row"><button class="btn btn--primary" type="button">Save automation settings</button></div>
                </div>
              </section>
            </div>
          </div>
        </div>
        """)
    ))

    return states


# ---------------------------------------------------------------------------
# Case Workspace Mockup Builder (pegasus_case_workspace_v41.html)
# ---------------------------------------------------------------------------

def clean_captured_body(html: str) -> str:
    start = html.find("<body")
    end = html.rfind("</body>")
    if start < 0 or end < 0:
        return html
    body = html[html.find(">", start) + 1 : end]
    # Remove embedded sprite sheet (already inlined once at top of body) and scripts
    body = re.sub(r'<svg\b[^>]*class="sprite-sheet"[^>]*>[\s\S]*?</svg>', "", body)
    body = re.sub(r"<script\b[^>]*>[\s\S]*?</script>", "", body)
    body = re.sub(
        r'src="/images/pegasus-mark-refined-128\.[0-9a-z]+\.png"',
        f'src="{MARK_DATA_URI}"',
        body,
    )
    idx = 0

    def repl_dl(_: re.Match[str]) -> str:
        nonlocal idx
        uri = TILE_URIS[idx % len(TILE_URIS)]
        idx += 1
        return f'src="{uri}"'

    body = re.sub(r'src="/Cases/[^"]*Download[^"]*"', repl_dl, body)
    body = re.sub(r'\shref="/[^"]*"', ' href="#"', body)
    body = re.sub(r'\saction="[^"]*"', ' action="#"', body)
    # Add rail-account class to the rail user menu button so interactive checks work on captured frames too
    body = body.replace(
        'data-dialog-open="account-dialog" aria-label="Account menu"',
        'class="icon-button rail-account" data-dialog-open="account-dialog" aria-label="Account menu"',
    )
    return body


def build_case_workspace_states() -> list[tuple[str, str, str, str]]:
    """Returns [(key, label, sheets_csv, html_markup)]."""
    delivery_rules = clean_captured_body(read_text(V39_CAPTURED / "delivery-rules.html"))
    delivery_plain = clean_captured_body(read_text(V39_CAPTURED / "delivery-plain.html"))
    delivery_stop = clean_captured_body(read_text(V39_CAPTURED / "delivery-stop.html"))
    delivery_missing = clean_captured_body(read_text(V39_CAPTURED / "delivery-missing-companion.html"))
    blocker_next = clean_captured_body(read_text(V39_CAPTURED / "blocker-next-action.html"))
    tasks_edit = clean_captured_body(read_text(V39_CAPTURED / "tasks-edit.html"))
    engineer_read = clean_captured_body(read_text(V36_CAPTURED / "frame-engineer-read.html"))
    engineer_edit = clean_captured_body(read_text(V36_CAPTURED / "frame-engineer-edit.html"))

    # Focused showcase state for v41 Case Workspace items (P, Q, R, S + Tier a f26)
    # Uses the exact .case-record / .sticky-block / .ribbon / .section-row / .workspace / .workspace-main / .workspace-aside DOM!
    v41_case_showcase = render_app_shell("cases", f"""
    <article class="record case-record is-editing" id="case-record" data-case-record data-layout="scroll" data-section-current="report" data-case-editing="true">
      <div class="sticky-block" data-sticky-block>
        <div class="ribbon" aria-label="Case identity" data-v41-change="f26 (A1)">
          <div class="ribbon-facts" data-case-ribbon-facts>
            <div class="ribbon-item ribbon-ref">
              <div class="ribbon-label">Case workspace · AB12 CDE</div>
              <h1 class="ribbon-value">QDOS26214</h1>
            </div>
            <div class="ribbon-item">
              <div class="ribbon-label">Claimant</div>
              <div class="ribbon-value"><span>J. Patel</span></div>
            </div>
            <div class="ribbon-item">
              <div class="ribbon-label">Principal</div>
              <div class="ribbon-value"><span>QDOS</span></div>
            </div>
            <div class="ribbon-item">
              <div class="ribbon-label">Engineer</div>
              <div class="ribbon-value"><span>Rashid Khan</span></div>
            </div>
            <div class="ribbon-chips" aria-label="State" data-case-ribbon-chips>
              <span class="status status--navy">With Engineer</span>
              <span class="status status--blue">Repairable</span>
              <span class="status status--green">Roadworthy</span>
            </div>
          </div>
          <div class="ribbon-actions" data-case-ribbon-actions>
            <span class="status status--navy status--plain case-edit-badge">Editing</span>
            <button type="button" class="btn btn--small">
              <svg class="icon" aria-hidden="true"><use href="#icon-save" /></svg>
              <span>Save now</span>
            </button>
            <button type="button" class="btn">
              <svg class="icon" aria-hidden="true"><use href="#icon-check" /></svg>
              <span>Done</span>
            </button>
            <details class="menu" data-menu data-case-actions>
              <summary class="btn"><span>Actions</span><svg class="icon" aria-hidden="true"><use href="#icon-chevron-down" /></svg></summary>
              <div class="menu-body">
                <button type="button" class="btn">
                  <svg class="icon" aria-hidden="true"><use href="#icon-square-check" /></svg>
                  <span>Tasks (2)</span>
                </button>
              </div>
            </details>
          </div>
        </div>

        <div class="section-row">
          <nav class="section-nav" aria-label="Case sections" data-section-nav>
            <a class="section-link" href="#section-overview"><svg class="icon" aria-hidden="true"><use href="#icon-layout-dashboard" /></svg><span>Case details</span></a>
            <a class="section-link" href="#section-vehicle"><svg class="icon" aria-hidden="true"><use href="#icon-car" /></svg><span>Vehicle</span></a>
            <a class="section-link" href="#section-estimate"><svg class="icon" aria-hidden="true"><use href="#icon-list" /></svg><span>Repair Spec</span></a>
            <a class="section-link" href="#section-settlement"><svg class="icon" aria-hidden="true"><use href="#icon-check-circle" /></svg><span>Decisions</span></a>
            <a class="section-link" aria-current="true" href="#section-report"><svg class="icon" aria-hidden="true"><use href="#icon-file" /></svg><span>Report</span></a>
            <a class="section-link" href="#section-files"><svg class="icon" aria-hidden="true"><use href="#icon-folder" /></svg><span>Files</span></a>
            <a class="section-link" href="#section-tasks"><svg class="icon" aria-hidden="true"><use href="#icon-square-check" /></svg><span>Tasks</span></a>
          </nav>
          <div class="section-tools">
            {render_freshness("Current · 14:32")}
          </div>
        </div>
      </div>

      <div class="workspace">
        <div class="workspace-main" id="case-main">
          <section class="record-section panel" id="section-report" data-section="report" aria-labelledby="sec10-title" data-v41-change="f26 (A5), f27 (P, Q)">
            <div class="panel-head">
              <h2 id="sec10-title">Report · Send report</h2>
              <div class="panel-actions">
                <span class="meta">Already sent on 13 Oct 2026 16:40 to claims@qdos.example</span>
              </div>
            </div>
            <div class="panel-body stack" data-send-report>
              <div class="sub-panel">
                <h3>Recipients &amp; file name</h3>
                <div class="fg g2">
                  <div class="fc ro">
                    <span class="lbl">From</span>
                    <div class="fv">From instructions@collisionengineers.co.uk — reply in the instruction's thread</div>
                  </div>
                  <div class="fc">
                    <label for="rep-fn">File name</label>
                    <div class="fv mono">QDOS26214_AB12CDE_Report.pdf</div>
                    <input id="rep-fn" class="fi mono" value="QDOS26214_AB12CDE_Report.pdf" />
                  </div>
                  <div class="fc">
                    <label for="rep-to">To</label>
                    <div class="fv">claims@qdos.example</div>
                    <input id="rep-to" class="fi" type="email" value="claims@qdos.example" />
                  </div>
                  <div class="fc">
                    <label for="rep-cc">Cc</label>
                    <div class="fv">handler@qdos.example</div>
                    <input id="rep-cc" class="fi" type="email" value="handler@qdos.example" />
                    <small class="hint">Added by Principal rule (QDOS); workshop@riverside.example excluded by Never Cc.</small>
                  </div>
                </div>
              </div>

              <div class="sub-panel">
                <h3>Questions for this Principal's sending rules</h3>
                <div class="stack">
                  <div class="cluster--between">
                    <span>Does the instruction mention "Luton"?</span>
                    <div class="cluster" role="radiogroup" aria-label="Luton question">
                      <label class="choice"><input type="radio" name="q_luton" value="yes" /> <span>Yes</span></label>
                      <label class="choice"><input type="radio" name="q_luton" value="no" checked /> <span>No</span></label>
                    </div>
                  </div>
                  <div class="cluster--between">
                    <span>Are the images from Garage?</span>
                    <div class="cluster" role="radiogroup" aria-label="Garage question">
                      <label class="choice"><input type="radio" name="q_garage" value="yes" checked /> <span>Yes</span></label>
                      <label class="choice"><input type="radio" name="q_garage" value="no" /> <span>No</span></label>
                    </div>
                  </div>
                </div>
              </div>

              <div class="sub-panel">
                <h3>Attach</h3>
                <div class="cluster">
                  <label class="choice"><input type="checkbox" checked disabled /> <span>Engineering report (included)</span></label>
                  <label class="choice"><input type="checkbox" checked /> <span>Fee note (separate PDF)</span></label>
                  <label class="choice"><input type="checkbox" checked /> <span>Repairer estimate</span></label>
                  <label class="choice"><input type="checkbox" /> <span>Vehicle images document</span></label>
                </div>
              </div>

              <div class="sub-panel">
                <h3>After sending &amp; hold check</h3>
                <div class="stack">
                  <ul style="margin:0;padding-left:18px">
                    <li>Follow up salvage collection within 48 hours.</li>
                  </ul>
                  <div class="cluster--between" style="border-top:1px solid var(--border);padding-top:8px">
                    <span><strong>Hold check:</strong> Confirm total loss figure with handler before sending.</span>
                    <label class="choice"><input type="checkbox" checked /> <span>Done</span></label>
                  </div>
                </div>
              </div>

              <div class="fc">
                <label for="rep-msg">Message</label>
                <textarea id="rep-msg" class="fi" rows="3">Good afternoon,\n\nPlease find attached our engineering report and fee note for AB12 CDE (QDOS26214).</textarea>
              </div>

              <div class="button-row">
                <button class="btn btn--primary" type="button">Send report</button>
              </div>
            </div>
          </section>

          <div class="v41-dialog-grid">
            <section class="dialog dialog--compact v41-inline-dialog" aria-labelledby="case-tasks-dlg-title" data-v41-change="f26 (A2), f29 (S)">
              <div class="dialog-head">
                <h2 id="case-tasks-dlg-title">Tasks · QDOS26214</h2>
                <button class="icon-button dialog-close" type="button" aria-label="Close"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button>
              </div>
              <div class="dialog-body stack">
                <div class="form-grid form-grid--auto" style="align-items:end">
                  <div class="field"><label for="nt-desc">New task</label><input id="nt-desc" class="fi" placeholder="Task description" /></div>
                  <div class="field">
                    <label for="nt-who">Assignee</label>
                    <select id="nt-who" class="fi"><option value="">Unassigned</option><option selected>Rashid Khan</option><option>Claire Mercer</option></select>
                  </div>
                  <button class="btn btn--primary btn--small" type="button">Add task</button>
                </div>
                <table class="table">
                  <thead><tr><th>Task</th><th>State</th><th class="right">Assignee &amp; actions</th></tr></thead>
                  <tbody>
                    <tr>
                      <td><strong>Confirm salvage collection date</strong></td>
                      <td><span class="status status--amber">Open</span></td>
                      <td class="right">
                        <div class="cluster" style="justify-content:flex-end">
                          <select class="fi" style="width:auto;min-height:32px" aria-label="Assignee"><option value="">Unassigned</option><option selected>Rashid Khan</option></select>
                          <button class="btn btn--small" type="button">Assign</button>
                          <button class="btn btn--small btn--primary" type="button">Complete</button>
                          <button class="btn btn--small btn--danger" type="button">Cancel</button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <p class="empty-line muted" style="margin:0">Empty state uses .empty-line (36px muted sentence, no icon box).</p>
              </div>
            </section>

            <section class="dialog dialog--compact v41-inline-dialog" aria-labelledby="send-ai-dlg-title" data-v41-change="f26 (A4), f29 (S)">
              <div class="dialog-head">
                <h2 id="send-ai-dlg-title">Send to AI &amp; Damage Reset</h2>
                <button class="icon-button dialog-close" type="button" aria-label="Close"><svg class="icon" aria-hidden="true"><use href="#icon-x" /></svg></button>
              </div>
              <div class="dialog-body stack">
                <div class="field">
                  <label for="ai-target-pct">Target Estimate (% of PAV)</label>
                  <div class="cluster">
                    <input id="ai-target-pct" type="range" min="0" max="80" step="1" value="55" style="flex:1" />
                    <input type="number" min="0" max="80" value="55" style="width:72px;text-align:right" aria-label="Target percent number" />
                    <output class="mono"><strong>55%</strong></output>
                  </div>
                </div>
                <div class="cluster--between" style="border-top:1px solid var(--border);padding-top:10px" id="section-damage">
                  <label class="choice"><input type="checkbox" checked /> <span>Record additional damage details</span></label>
                  <button class="btn btn--small" type="button" data-damage-reset style="margin:0 0 0 auto">Reset</button>
                </div>
              </div>
            </section>
          </div>
        </div>

        <aside class="workspace-aside" aria-label="Case context">
          <div class="aside-stack">
            <section class="panel aside-card" aria-label="Figures">
              <div class="panel-head"><h2>Figures</h2></div>
              <div class="panel-body">
                <dl class="figure-list">
                  <div><dt>Repair cost inc VAT</dt><dd class="mono">£3,184.00</dd></div>
                  <div><dt>Engineer's Value</dt><dd class="mono">£5,800.00</dd></div>
                  <div><dt>Repair cost of value</dt><dd class="mono">54.9%</dd></div>
                </dl>
              </div>
            </section>

            <section class="panel aside-card aside-card--action" aria-labelledby="na-tasks-title" data-v41-change="f28 (R)">
              <div class="panel-head">
                <h2 id="na-tasks-title">Next action</h2>
                <span class="status status--amber">2 open tasks</span>
              </div>
              <div class="panel-body stack">
                <div class="stack" data-open-tasks>
                  <button class="row-button cluster--between" type="button" data-v41-proposal-only>
                    <span><strong>Confirm salvage collection date</strong> · R. Khan</span>
                    <span class="meta">Tasks →</span>
                  </button>
                  <button class="row-button cluster--between" type="button" data-v41-proposal-only>
                    <span><strong>Upload signed fee note</strong> · Unassigned</span>
                    <span class="meta">Tasks →</span>
                  </button>
                  <ul class="blocker-list" data-v41-today-only>
                    <li class="blocker"><strong>Confirm salvage collection date</strong> <a class="btn btn--small" href="#">Tasks</a></li>
                    <li class="blocker"><strong>Upload signed fee note</strong> <a class="btn btn--small" href="#">Tasks</a></li>
                  </ul>
                </div>
              </div>
            </section>
          </div>
        </aside>
      </div>
    </article>
    """)

    return [
        ("v41-overview", "1. v41 Case Workspace overview (Delivery, Open Tasks, Tasks & AI dialogs, Damage Reset)", "case-workspace.css", v41_case_showcase),
        ("delivery-rules", "2. Report delivery · Rules, questions, hold & after sending (Items P, Q)", "case-workspace.css", delivery_rules),
        ("delivery-plain", "3. Report delivery · Default rules, nothing asked (Item P)", "case-workspace.css", delivery_plain),
        ("delivery-stop", "4. Report delivery · Stop rule applies, override required (Items P, Q)", "case-workspace.css", delivery_stop),
        ("delivery-missing", "5. Report delivery · Missing required companion (Items P, Q)", "case-workspace.css", delivery_missing),
        ("next-action-tasks", "6. Next action · Post-report open tasks in aside (Item R)", "case-workspace.css", blocker_next),
        ("tasks-dialog", "7. Tasks dialog · Styled inputs & single-line row actions (Item S)", "case-workspace.css", tasks_edit),
        ("engineer-read", "8. Full Case Record · With Engineer (Read mode)", "case-workspace.css", engineer_read),
        ("engineer-edit", "9. Full Case Record · With Engineer (Edit mode)", "case-workspace.css", engineer_edit),
    ]


# ---------------------------------------------------------------------------
# Proposal CSS & Mockup Strip Runtime
# ---------------------------------------------------------------------------

PROPOSAL_CSS = """
/* v41 Proposal refinements, interactive modal/toast layer, and mockup controls strip */
.v41-card-pair { display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 20px; align-items: start; }
.v41-dialog-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 18px; align-items: start; }
.v41-inline-dialog { position: relative !important; inset: auto !important; width: 100% !important; max-width: 100% !important; box-shadow: var(--shadow-sm); background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); }
.cluster--between { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.btn--sm { min-height: 28px; padding: 3px 10px; font-size: var(--text-xs); }

/* Interactive row & link affordances */
.wc-ledger-table tbody tr:not(.wc-group-row):not(.wc-inline-detail),
[data-search-results-table] tbody tr,
[data-row-list] tbody tr,
.inbox-row { cursor: pointer; transition: background-color .1s ease; }

/* Rail collapse interactive mode */
body.rail-collapsed .app-shell { grid-template-columns: 60px minmax(0, 1fr) !important; }
body.rail-collapsed .app-rail .brand-copy,
body.rail-collapsed .app-rail .nav-label,
body.rail-collapsed .app-rail .nav-link span,
body.rail-collapsed .app-rail .rail-collapse span,
body.rail-collapsed .app-rail .rail-health,
body.rail-collapsed .app-rail .rail-user > div { display: none !important; }
body.rail-collapsed .app-rail .nav-link { justify-content: center; padding: 0 !important; }

/* Design toggle: proposal vs today */
html[data-design="proposal"] [data-v41-today-only] { display: none !important; }
html[data-design="today"] [data-v41-proposal-only] { display: none !important; }

/* f05 (Item C): Utility bar duplicate freshness hidden in proposal */
html[data-design="proposal"] [data-v41-dup-freshness] { display: none !important; }

/* f11: Work Centre h1, switch, and table header alignment in proposal */
html[data-design="proposal"] .work-centre .page-header h1 { font-size: 20px; letter-spacing: -.02em; font-weight: 700; }
html[data-design="proposal"] .wc-switch a { height: 32px; border-radius: 4px; display: inline-flex; align-items: center; }
html[data-design="proposal"] .wc-ledger-table th { font-size: 11px; letter-spacing: .04em; height: 34px; padding: 6px 12px; }

/* f15 (Item H) & f16: Inbox 3-column filter bar and 1180px responsive breakpoint */
html[data-design="proposal"] .inbox-filter { grid-template-columns: minmax(0, 1.3fr) minmax(0, 1.1fr) minmax(0, 1.6fr) auto !important; }
@media (max-width: 1180px) {
  html[data-design="proposal"] .inbox-layout.pane-layout--3 { grid-template-columns: minmax(0, 1fr) 380px !important; }
  html[data-design="proposal"] .inbox-layout.pane-layout--3 > aside.pane:first-child { grid-column: 1 / -1; }
}
@media (max-width: 760px) {
  html[data-design="proposal"] .inbox-layout.pane-layout--3 { grid-template-columns: minmax(0, 1fr) !important; }
  .v41-card-pair, .v41-dialog-grid { grid-template-columns: minmax(0, 1fr); }
}

/* f20: Upload review Inspector first in DOM on desktop (>900px), Decision first on narrow screens */
html[data-design="proposal"] .up-workspace .up-inspector { grid-column: 2; grid-row: 1; }
html[data-design="proposal"] .up-workspace .up-decision { grid-column: 1; grid-row: 1; }
@media (max-width: 900px) {
  html[data-design="proposal"] .up-workspace .up-decision { grid-column: 1; grid-row: 1; }
  html[data-design="proposal"] .up-workspace .up-inspector { grid-column: 1; grid-row: 2; }
}

/* f26 (A4): Case Workspace Damage Reset button flush right */
html[data-design="proposal"] #section-damage [data-damage-reset] { margin: 0 0 0 auto !important; }

/* f27 (Item P): Fix .fc input[type="radio"] and label.choice inside #section-report so Yes/No radios are 16px inline choices */
html[data-design="proposal"] .fc input[type="radio"],
html[data-design="proposal"] [data-report-question] input[type="radio"] {
  width: 16px !important;
  min-height: 16px !important;
  height: 16px !important;
  padding: 0 !important;
  flex: 0 0 16px !important;
}
html[data-design="proposal"] [data-report-question] label.choice {
  display: inline-flex !important;
  flex-direction: row !important;
  align-items: center !important;
  gap: 6px !important;
  font-size: var(--text-sm) !important;
  font-weight: 500 !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
  color: var(--ink) !important;
}

/* f33 (Item U) & f34 (Item V): Fieldset reset and .hint styling */
html[data-design="proposal"] fieldset.stack,
html[data-design="proposal"] fieldset.field { border: 0; padding: 0; margin: 0; min-width: 0; }
.hint { font-size: 12px; color: var(--muted); margin: 4px 0 0; }

/* Interactive Modal Overlay & Toast */
#v41-modal-backdrop {
  position: fixed; inset: 0; z-index: 9500;
  background: rgba(15, 20, 26, .52);
  display: grid; place-items: center; padding: 20px;
}
#v41-modal-backdrop[hidden] { display: none !important; }
#v41-modal-box {
  width: 100%; max-width: 540px; max-height: 88vh; overflow: auto;
  background: var(--surface, #fff); color: var(--ink, #1c2226);
  border: 1px solid var(--border, #d0d7de); border-radius: 6px;
  box-shadow: 0 20px 48px rgba(0,0,0,.32);
}
#v41-modal-box .dialog { position: relative !important; inset: auto !important; width: 100% !important; max-width: 100% !important; border: 0 !important; box-shadow: none !important; }
#v41-toast {
  position: fixed; right: 18px; bottom: 18px; z-index: 9998;
  background: #1b2228; color: #fff; padding: 10px 16px; border-radius: 6px;
  border-left: 4px solid var(--red, #c8102e);
  font: 600 13px/1.35 "Inter Variable", Inter, system-ui, sans-serif;
  box-shadow: 0 8px 24px rgba(0,0,0,.3);
  transition: opacity .2s ease, transform .2s ease;
}
#v41-toast[hidden] { display: none !important; }

/* Diff & Ruler widgets */
body.v41-diff [data-v41-change] { outline: 2px dashed var(--red, #c8102e); outline-offset: 3px; position: relative; }
body.v41-diff [data-v41-change]::before {
  content: attr(data-v41-change);
  position: absolute; top: -11px; left: 4px; z-index: 30;
  background: var(--red, #c8102e); color: #fff;
  font: 700 10px/1 "Inter Variable", Inter, sans-serif;
  padding: 3px 6px; border-radius: 3px; pointer-events: none;
}
body.v41-ruler button, body.v41-ruler a.btn, body.v41-ruler input, body.v41-ruler select {
  outline: 2px solid rgba(26, 140, 80, .75); outline-offset: -2px;
}

/* Mockup controls strip */
#mock-strip {
  position: fixed; left: 12px; bottom: 12px; z-index: 9999;
  background: #1d2229; color: #e6e9ee;
  font: 12px/1.4 "Inter Variable", Inter, system-ui, sans-serif;
  border-radius: 8px; box-shadow: 0 8px 28px rgba(0,0,0,.4);
  width: 370px; max-height: 82vh; overflow: auto;
}
#mock-strip summary { cursor: pointer; padding: 9px 12px; font-weight: 700; display: flex; justify-content: space-between; align-items: center; }
#mock-strip .mock-body { padding: 0 12px 12px; display: grid; gap: 8px; }
#mock-strip select, #mock-strip button.mock-btn {
  width: 100%; font: inherit; padding: 5px 8px; border-radius: 4px;
  border: 1px solid #3a424d; background: #2a313a; color: #e6e9ee; cursor: pointer;
}
#mock-strip .mock-seg { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }
#mock-strip .mock-seg--4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; }
#mock-strip .mock-seg button[aria-pressed="true"],
#mock-strip .mock-seg--4 button[aria-pressed="true"] { background: #c8102e; border-color: #c8102e; color: #fff; font-weight: 600; }
#mock-strip small { color: #9aa4b2; display: block; }
body.v41-strip-hidden #mock-strip { display: none !important; }
"""

RUNTIME_JS = r"""
(function () {
  'use strict';
  var STATES = __STATES__;
  var DEFAULT_STATE = __DEFAULT_STATE__;
  var TILE_URIS = __TILE_URIS__;
  var params = new URLSearchParams(location.search);
  var key = params.get('state');
  if (!STATES.some(function (s) { return s.key === key; })) { key = DEFAULT_STATE; }
  var design = params.get('design') === 'today' ? 'today' : 'proposal';
  var diff = params.get('diff') === '1';
  var ruler = params.get('ruler') === '1';
  var stripHidden = params.get('strip') === '0';

  var root = document.getElementById('mock-root');
  var strip = document.getElementById('mock-strip');
  var sel = document.getElementById('mock-state');
  var modalBackdrop = document.getElementById('v41-modal-backdrop');
  var modalBox = document.getElementById('v41-modal-box');
  var toastEl = document.getElementById('v41-toast');
  var toastTimer = null;

  function showToast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.hidden = false;
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.hidden = true; }, 2800);
  }

  function closeModal() {
    if (modalBackdrop) {
      modalBackdrop.hidden = true;
      modalBox.innerHTML = '';
    }
  }

  STATES.forEach(function (s) {
    var o = document.createElement('option');
    o.value = s.key; o.textContent = s.label; o.selected = s.key === key;
    sel.appendChild(o);
  });

  function syncUrl() {
    var p = new URLSearchParams(location.search);
    p.set('state', key);
    p.set('design', design);
    if (diff) p.set('diff', '1'); else p.delete('diff');
    if (ruler) p.set('ruler', '1'); else p.delete('ruler');
    if (stripHidden) p.set('strip', '0'); else p.delete('strip');
    try { history.replaceState(null, '', '?' + p.toString()); } catch (e) {}
  }

  function applyPatches() {
    document.documentElement.setAttribute('data-design', design);
    document.documentElement.setAttribute('data-mock-state', key);
    document.body.classList.toggle('v41-diff', diff);
    document.body.classList.toggle('v41-ruler', ruler);
    document.body.classList.toggle('v41-strip-hidden', stripHidden);

    if (design === 'proposal' && root) {
      root.querySelectorAll('use[href="#icon-check-square"]').forEach(function (u) {
        u.setAttribute('href', '#icon-square-check');
      });
      root.querySelectorAll('[aria-expanded="false"][title="Collapse section"]').forEach(function (btn) {
        btn.setAttribute('title', 'Expand section');
      });
      root.querySelectorAll('[data-send-report] input[type="radio"]').forEach(function (r) {
        var lbl = r.closest('label');
        if (lbl && !lbl.textContent.trim()) {
          var span = document.createElement('span');
          span.textContent = r.value === 'true' || r.value === 'yes' ? ' Yes' : ' No';
          lbl.appendChild(span);
        }
      });
    }

    if (strip) {
      if (sel.value !== key) sel.value = key;
      strip.querySelectorAll('[data-set-design]').forEach(function (btn) {
        btn.setAttribute('aria-pressed', String(btn.getAttribute('data-set-design') === design));
      });
      strip.querySelectorAll('[data-toggle-param]').forEach(function (btn) {
        var param = btn.getAttribute('data-toggle-param');
        var active = (param === 'diff' && diff) || (param === 'ruler' && ruler);
        btn.setAttribute('aria-pressed', String(active));
      });
    }
    if (window.__mock) {
      window.__mock.state = key;
      window.__mock.design = design;
    }
  }

  function renderState(nextKey, scrollSelector) {
    if (!STATES.some(function (s) { return s.key === nextKey; })) return;
    key = nextKey;
    closeModal();
    var tpl = document.getElementById('mock-state-' + key);
    if (tpl && root) {
      // Enable only site.css + this state's @section Styles stylesheet(s)
      var activeSheets = (tpl.getAttribute('data-sheets') || '').split(',').filter(Boolean);
      document.querySelectorAll('style[data-sheet]').forEach(function (st) {
        var name = st.getAttribute('data-sheet');
        var isActive = activeSheets.indexOf(name) !== -1;
        st.media = isActive ? 'all' : 'not all';
        st.disabled = !isActive;
      });
      root.innerHTML = tpl.innerHTML;
      document.title = tpl.getAttribute('data-title') + ' (' + design + ' · v41 mockup)';
    }
    applyPatches();
    wirePageInteractions();
    syncUrl();
    var defaultScroll = scrollSelector;
    if (!defaultScroll) {
      if (key.indexOf('delivery-') === 0) defaultScroll = '#section-report';
      else if (key === 'tasks-dialog') defaultScroll = '#section-tasks';
    }
    if (defaultScroll) {
      var target = root.querySelector(defaultScroll);
      if (target) {
        setTimeout(function () { target.scrollIntoView({ behavior: 'instant', block: 'start' }); }, 10);
        return;
      }
    }
    window.scrollTo(0, 0);
  }

  function openModal(dialogType, triggerEl) {
    if (!modalBackdrop || !modalBox) return;
    var html = '';
    if (dialogType === 'account-dialog') {
      html = '<section class="dialog dialog--compact" aria-labelledby="modal-acc-title">' +
        '<div class="dialog-head"><h2 id="modal-acc-title">Account</h2>' +
        '<button class="icon-button dialog-close" type="button" data-modal-close aria-label="Close"><svg class="icon"><use href="#icon-x"/></svg></button></div>' +
        '<div class="dialog-body stack"><dl class="detail-list">' +
        '<div><dt>Name</dt><dd>Alex Jordan</dd></div>' +
        '<div><dt>Username</dt><dd class="mono">alex</dd></div>' +
        '<div><dt>Role</dt><dd>Administrator</dd></div>' +
        '<div data-v41-proposal-only><dt>Session started</dt><dd class="mono">14 Oct 2026 08:45</dd></div>' +
        '<div><dt>Idle lock</dt><dd>After 15 minutes of inactivity</dd></div></dl>' +
        '<div class="button-row" data-v41-proposal-only style="border-top:1px solid var(--border);padding-top:10px">' +
        '<button class="btn btn--small" type="button" data-go-state="auth-errors" data-scroll="#rn-page-title">Release notes</button>' +
        '<button class="btn btn--small" type="button" data-dialog-open="report-problem-dialog">Report a problem</button>' +
        '<button class="btn btn--small" type="button" data-go-state="auth-signin" data-scroll="#pw-vol-title">Change password</button></div></div>' +
        '<div class="dialog-foot" data-v41-today-only>' +
        '<button class="btn" type="button" data-modal-close>Close</button>' +
        '<button class="btn" type="button" data-go-state="auth-errors">Release notes</button>' +
        '<button class="btn" type="button" data-dialog-open="report-problem-dialog">Report a problem</button>' +
        '<button class="btn" type="button" data-go-state="auth-signin">Change password</button>' +
        '<button class="btn btn--danger" type="button" data-go-state="auth-signin" data-toast="Signed out">Sign out</button></div>' +
        '<div class="dialog-foot" data-v41-proposal-only>' +
        '<button class="btn" type="button" data-modal-close>Close</button>' +
        '<button class="btn btn--danger" type="button" data-go-state="auth-signin" data-toast="Signed out">Sign out</button></div></section>';
    } else if (dialogType === 'notifications-dialog') {
      html = '<section class="dialog dialog--compact" aria-labelledby="modal-notif-title">' +
        '<div class="dialog-head"><h2 id="modal-notif-title">Notifications</h2>' +
        '<div class="cluster"><button class="btn btn--small" type="button" data-v41-proposal-only data-mark-all-read>Mark all read</button>' +
        '<button class="icon-button dialog-close" type="button" data-modal-close aria-label="Close"><svg class="icon"><use href="#icon-x"/></svg></button></div></div>' +
        '<div class="dialog-body stack">' +
        '<button class="row-button notification-item is-unread" type="button" data-go-state="engineer-read" style="text-align:left">' +
        '<div class="row-top"><span class="row-title">AI Proposal ready · QDOS26214</span><span class="row-time">14:28</span></div>' +
        '<div class="row-excerpt">Repair specification candidate completed for AB12 CDE.</div></button>' +
        '<button class="row-button notification-item is-unread" type="button" data-go-state="unidentified-images" style="text-align:left">' +
        '<div class="row-top"><span class="row-title">Images paired · IMG-2026-0019</span><span class="row-time">13:50</span></div>' +
        '<div class="row-excerpt">14 photographs linked for AB12 CDE.</div></button></div>' +
        '<div class="dialog-foot"><button class="btn" type="button" data-v41-today-only data-mark-all-read>Mark all read</button>' +
        '<button class="btn" type="button" data-modal-close>Close</button></div></section>';
    } else if (dialogType === 'cmd-dialog') {
      html = '<section class="dialog dialog--compact" aria-labelledby="modal-cmd-title">' +
        '<div class="dialog-head"><h2 id="modal-cmd-title">Go to</h2>' +
        '<button class="icon-button dialog-close" type="button" data-modal-close aria-label="Close"><svg class="icon"><use href="#icon-x"/></svg></button></div>' +
        '<div class="dialog-body stack">' +
        '<input type="search" id="v41-cmd-input" placeholder="Jump to page or Case (e.g. QDOS26214, Inbox, Contacts)…" autocomplete="off" />' +
        '<div class="stack" id="v41-cmd-list">' +
        '<button class="row-button cluster" type="button" data-go-state="work-centre"><svg class="icon"><use href="#icon-layout-dashboard"/></svg><span>Work Centre</span><small class="muted" style="margin-left:auto">Page</small></button>' +
        '<button class="row-button cluster" type="button" data-go-state="cases-queue"><svg class="icon"><use href="#icon-list-checks"/></svg><span>Cases Queue</span><small class="muted" style="margin-left:auto">Page</small></button>' +
        '<button class="row-button cluster" type="button" data-go-state="search"><svg class="icon"><use href="#icon-search"/></svg><span>Search</span><small class="muted" style="margin-left:auto">Page</small></button>' +
        '<button class="row-button cluster" type="button" data-go-state="inbox"><svg class="icon"><use href="#icon-inbox"/></svg><span>Inbox</span><small class="muted" style="margin-left:auto">Page</small></button>' +
        '<button class="row-button cluster" type="button" data-go-state="upload-review"><svg class="icon"><use href="#icon-upload"/></svg><span>Upload &amp; Review</span><small class="muted" style="margin-left:auto">Page</small></button>' +
        '<button class="row-button cluster" type="button" data-go-state="engineer-read"><svg class="icon"><use href="#icon-file-text"/></svg><span><strong>QDOS26214</strong> · AB12 CDE · BMW 320d (Read)</span><small class="muted" style="margin-left:auto">Case</small></button>' +
        '<button class="row-button cluster" type="button" data-go-state="engineer-edit"><svg class="icon"><use href="#icon-file-text"/></svg><span><strong>QDOS26214</strong> · AB12 CDE · BMW 320d (Edit)</span><small class="muted" style="margin-left:auto">Case</small></button>' +
        '<button class="row-button cluster" type="button" data-go-state="v41-overview"><svg class="icon"><use href="#icon-send"/></svg><span><strong>QDOS26214</strong> · Report Delivery &amp; Tasks</span><small class="muted" style="margin-left:auto">Case</small></button>' +
        '<button class="row-button cluster" type="button" data-go-state="triage-case"><svg class="icon"><use href="#icon-list-checks"/></svg><span><strong>QDOS26210</strong> · KP21 NRO · Triage</span><small class="muted" style="margin-left:auto">Triage</small></button>' +
        '<button class="row-button cluster" type="button" data-go-state="admin-accounts"><svg class="icon"><use href="#icon-settings"/></svg><span>Administration · Staff accounts</span><small class="muted" style="margin-left:auto">Admin</small></button>' +
        '<button class="row-button cluster" type="button" data-go-state="admin-contacts"><svg class="icon"><use href="#icon-building"/></svg><span>Administration · Contacts (DFD)</span><small class="muted" style="margin-left:auto">Admin</small></button>' +
        '<button class="row-button cluster" type="button" data-go-state="admin-config-mail"><svg class="icon"><use href="#icon-sliders"/></svg><span>Administration · Configuration &amp; Mailboxes</span><small class="muted" style="margin-left:auto">Admin</small></button>' +
        '<button class="row-button cluster" type="button" data-go-state="admin-logs-ops"><svg class="icon"><use href="#icon-scroll-text"/></svg><span>Administration · Logs, Reports &amp; AI Jobs</span><small class="muted" style="margin-left:auto">Admin</small></button>' +
        '</div></div></section>';
    } else if (dialogType === 'whats-new-dialog' || dialogType === 'release-note-edit-dialog') {
      html = '<section class="dialog dialog--compact" aria-labelledby="modal-wn-title">' +
        '<div class="dialog-head"><h2 id="modal-wn-title">v2026.10 — Release notes</h2>' +
        '<button class="icon-button dialog-close" type="button" data-modal-close aria-label="Close"><svg class="icon"><use href="#icon-x"/></svg></button></div>' +
        '<div class="dialog-body stack">' +
        '<p class="muted" style="margin:0">Published 13 October 2026</p>' +
        '<ul style="margin:0;padding-left:18px"><li>Contacts directory grouped by Principal, Claim Source, Repairer, Storage and Third Party Engineer.</li>' +
        '<li>Principal report sending rules, salvage matrix and one-step report delivery.</li></ul></div>' +
        '<div class="dialog-foot"><button class="btn" type="button" data-modal-close>Close</button>' +
        '<button class="btn btn--primary" type="button" data-go-state="auth-errors" data-scroll="#rn-page-title">All release notes</button></div></section>';
    } else if (dialogType === 'report-problem-dialog') {
      html = '<section class="dialog dialog--compact" aria-labelledby="modal-rp-title">' +
        '<div class="dialog-head"><h2 id="modal-rp-title">Report a problem</h2>' +
        '<button class="icon-button dialog-close" type="button" data-modal-close aria-label="Close"><svg class="icon"><use href="#icon-x"/></svg></button></div>' +
        '<div class="dialog-body stack">' +
        '<div class="field"><label class="req">What happened?</label><textarea rows="3">Glass\'s window closed before import completed on QDOS26214.</textarea></div></div>' +
        '<div class="dialog-foot"><button class="btn" type="button" data-modal-close>Cancel</button>' +
        '<button class="btn btn--primary" type="button" data-modal-close data-toast="Problem report submitted">Send report</button></div></section>';
    } else if (dialogType === 'wc-assign-dialog') {
      var ref = (triggerEl && triggerEl.getAttribute('data-wc-case-ref')) || 'DFD26031';
      var prin = (triggerEl && triggerEl.getAttribute('data-wc-principal')) || 'Davison Flynn Duke';
      var veh = (triggerEl && triggerEl.getAttribute('data-wc-vehicle')) || 'YK71 XWB · Audi A4 Avant';
      html = '<section class="dialog dialog--compact" aria-labelledby="modal-wca-title">' +
        '<div class="dialog-head"><h2 id="modal-wca-title">Assign Engineer</h2>' +
        '<button class="icon-button dialog-close" type="button" data-modal-close aria-label="Close"><svg class="icon"><use href="#icon-x"/></svg></button></div>' +
        '<div class="dialog-body stack">' +
        (design === 'today' ? '<div class="notice notice--warn"><div><strong>Today bug (f10)</strong><div>Dialog bound to expanded row QDOS26214 instead of clicked row ' + ref + '!</div></div></div>' : '') +
        '<dl class="detail-list">' +
        '<div><dt>Case</dt><dd class="mono">' + (design === 'today' ? 'QDOS26214 (Wrong Case!)' : ref) + '</dd></div>' +
        '<div><dt>Principal</dt><dd>' + (design === 'today' ? 'QDOS' : prin) + '</dd></div>' +
        '<div><dt>Vehicle</dt><dd>' + (design === 'today' ? 'AB12 CDE · BMW 320d' : veh) + '</dd></div></dl>' +
        '<div class="field"><label class="req" for="modal-wc-eng">Engineer</label>' +
        '<select id="modal-wc-eng"><option value="Rashid Khan">Rashid Khan</option><option value="Claire Mercer" selected>Claire Mercer</option><option value="David Hughes">David Hughes</option></select></div></div>' +
        '<div class="dialog-foot"><button class="btn" type="button" data-modal-close>Cancel</button>' +
        '<button class="btn btn--primary" type="button" data-wc-confirm-assign="' + ref + '">Assign</button></div></section>';
    } else if (dialogType === 'unlinkCaseDialog') {
      html = '<section class="dialog dialog--compact" aria-labelledby="modal-unl-title">' +
        '<div class="dialog-head"><h2 id="modal-unl-title">Unlink from Case · DFD26031</h2>' +
        '<button class="icon-button dialog-close" type="button" data-modal-close aria-label="Close"><svg class="icon"><use href="#icon-x"/></svg></button></div>' +
        '<div class="dialog-body stack">' +
        '<p style="margin:0">Unlinking moves this message back to <strong>No Case Found</strong>.</p>' +
        '<div class="field"><label class="req">Reason for unlinking</label><textarea rows="2">Attached to wrong vehicle registration.</textarea></div></div>' +
        '<div class="dialog-foot"><button class="btn" type="button" data-modal-close>Cancel</button>' +
        '<button class="btn btn--danger" type="button" data-modal-close data-toast="Message unlinked from DFD26031">Unlink from Case</button></div></section>';
    } else if (dialogType === 'problem-report-dialog') {
      html = '<section class="dialog dialog--compact" aria-labelledby="modal-prd-title">' +
        '<div class="dialog-head"><h2 id="modal-prd-title">Resolve problem report</h2>' +
        '<button class="icon-button dialog-close" type="button" data-modal-close aria-label="Close"><svg class="icon"><use href="#icon-x"/></svg></button></div>' +
        '<div class="dialog-body stack">' +
        '<p style="margin:0"><strong>R. Khan</strong> on <code class="mono">/Cases/QDOS26214</code>: Glass\'s window closed before import completed.</p>' +
        '<div class="field"><label>Matching GitHub issue # (if confirmed)</label><input type="number" value="1320" /></div></div>' +
        '<div class="dialog-foot"><button class="btn" type="button" data-modal-close>Cancel</button>' +
        '<button class="btn" type="button" data-resolve-problem="Not an issue">Dismiss</button>' +
        '<button class="btn btn--primary" type="button" data-resolve-problem="Confirmed · #1320">Confirm issue</button></div></section>';
    } else if (dialogType === 'stop-ai-job-dialog') {
      html = '<section class="dialog dialog--compact" aria-labelledby="modal-stop-ai">' +
        '<div class="dialog-head"><h2 id="modal-stop-ai">Stop AI job · QDOS26214</h2>' +
        '<button class="icon-button dialog-close" type="button" data-modal-close aria-label="Close"><svg class="icon"><use href="#icon-x"/></svg></button></div>' +
        '<div class="dialog-body stack">' +
        '<div class="field"><label class="req">Reason</label><input value="Updated Glass\'s calculation; restarting with revised PAV." /></div></div>' +
        '<div class="dialog-foot"><button class="btn" type="button" data-modal-close>Cancel</button>' +
        '<button class="btn btn--danger" type="button" data-confirm-stop-ai>Stop job</button></div></section>';
    } else if (dialogType === 'new-mailbox-dialog') {
      html = '<section class="dialog dialog--compact" aria-labelledby="modal-mbx-title">' +
        '<div class="dialog-head"><h2 id="modal-mbx-title">Add approved mailbox</h2>' +
        '<button class="icon-button dialog-close" type="button" data-modal-close aria-label="Close"><svg class="icon"><use href="#icon-x"/></svg></button></div>' +
        '<div class="dialog-body stack">' +
        '<div class="field"><label class="req">E-mail address</label><input class="mono" value="claims@collisionengineers.co.uk" /></div>' +
        '<div class="field"><label>Purpose</label><select><option selected>Intake &amp; Staff send</option><option>Intake only</option></select></div></div>' +
        '<div class="dialog-foot"><button class="btn" type="button" data-modal-close>Cancel</button>' +
        '<button class="btn btn--primary" type="button" data-modal-close data-toast="Mailbox added">Add mailbox</button></div></section>';
    } else if (dialogType === 'replace-principal') {
      var inlineDlg = root && root.querySelector('#replace-principal');
      if (inlineDlg) {
        html = inlineDlg.outerHTML.replace('v41-inline-dialog', '');
      }
    } else if (dialogType === 'preview-media') {
      var title = (triggerEl && triggerEl.getAttribute('data-preview-title')) || 'Document / Image Preview';
      html = '<section class="dialog" aria-labelledby="modal-prev-title">' +
        '<div class="dialog-head"><h2 id="modal-prev-title">' + title + '</h2>' +
        '<button class="icon-button dialog-close" type="button" data-modal-close aria-label="Close"><svg class="icon"><use href="#icon-x"/></svg></button></div>' +
        '<div class="dialog-body stack" style="text-align:center;background:#16202e;padding:20px;border-radius:4px">' +
        '<img src="' + TILE_URIS[0] + '" alt="Preview" style="max-height:360px;margin:0 auto;border-radius:4px" />' +
        '<div class="cluster" style="justify-content:center;color:#e6e9ee">' +
        '<button class="btn btn--small" type="button" data-toast="Rotated 90° (viewer stays open in Proposal · f24)">Rotate 90°</button>' +
        '<button class="btn btn--small" type="button" data-toast="Cropped image saved (viewer stays open · f24)">Save crop</button>' +
        '<button class="btn btn--small" type="button" data-toast="Tag Front Nearside saved (viewer stays open · f24)">Tag: Front Nearside</button>' +
        '</div></div>' +
        '<div class="dialog-foot"><button class="btn" type="button" data-modal-close>Close</button></div></section>';
    }
    if (!html) return;
    modalBox.innerHTML = html;
    modalBackdrop.hidden = false;
    var cmdInput = modalBox.querySelector('#v41-cmd-input');
    if (cmdInput) {
      setTimeout(function () { cmdInput.focus(); }, 20);
      cmdInput.addEventListener('input', function () {
        var q = cmdInput.value.toLowerCase();
        modalBox.querySelectorAll('#v41-cmd-list > button').forEach(function (b) {
          b.hidden = q && b.textContent.toLowerCase().indexOf(q) === -1;
        });
      });
    }
  }

  function wirePageInteractions() {
    if (!root) return;

    var rangeInput = root.querySelector('#ai-target-pct');
    var numInput = root.querySelector('input[aria-label="Target percent number"]');
    var outEl = root.querySelector('#send-ai-dlg-title') && root.querySelector('output.mono');
    if (rangeInput && numInput) {
      rangeInput.addEventListener('input', function () {
        numInput.value = rangeInput.value;
        if (outEl) outEl.innerHTML = '<strong>' + rangeInput.value + '%</strong>';
      });
      numInput.addEventListener('input', function () {
        rangeInput.value = numInput.value;
        if (outEl) outEl.innerHTML = '<strong>' + numInput.value + '%</strong>';
      });
    }

    var wcFind = root.querySelector('.wc-find input[type="search"]');
    if (wcFind) {
      wcFind.addEventListener('input', function () {
        var q = wcFind.value.toLowerCase();
        root.querySelectorAll('.wc-ledger-table tbody tr:not(.wc-group-row):not(.wc-inline-detail)').forEach(function (tr) {
          tr.hidden = !!(q && tr.textContent.toLowerCase().indexOf(q) === -1);
        });
      });
    }

    var cqInput = root.querySelector('#cq-q');
    var cqStage = root.querySelector('#cq-stage');
    var cqPrin = root.querySelector('#cq-prin');
    function filterCasesQueue() {
      var q = cqInput ? cqInput.value.toLowerCase() : '';
      var st = cqStage && cqStage.selectedIndex > 0 ? cqStage.value.toLowerCase() : '';
      var pr = cqPrin && cqPrin.value ? cqPrin.value.toLowerCase() : '';
      root.querySelectorAll('.cases-table tbody tr').forEach(function (tr) {
        var txt = tr.textContent.toLowerCase();
        tr.hidden = !!((q && txt.indexOf(q) === -1) || (st && txt.indexOf(st) === -1) || (pr && txt.indexOf(pr) === -1));
      });
    }
    if (cqInput) cqInput.addEventListener('input', filterCasesQueue);
    if (cqStage) cqStage.addEventListener('change', filterCasesQueue);
    if (cqPrin) cqPrin.addEventListener('change', filterCasesQueue);

    var ibSearch = root.querySelector('#ib-q');
    if (ibSearch) {
      ibSearch.addEventListener('input', function () {
        var q = ibSearch.value.toLowerCase();
        root.querySelectorAll('.inbox-row').forEach(function (row) {
          row.hidden = !!(q && row.textContent.toLowerCase().indexOf(q) === -1);
        });
      });
    }

    var logFilter = root.querySelector('[data-v41-log-filter]');
    if (logFilter) {
      logFilter.addEventListener('input', function () {
        var q = logFilter.value.toLowerCase();
        root.querySelectorAll('[data-v41-log-table] tbody tr').forEach(function (tr) {
          tr.hidden = !!(q && tr.textContent.toLowerCase().indexOf(q) === -1);
        });
      });
    }
  }

  document.addEventListener('keydown', function (ev) {
    if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === 'k') {
      ev.preventDefault();
      openModal('cmd-dialog');
    } else if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === 'b') {
      ev.preventDefault();
      document.body.classList.toggle('rail-collapsed');
    } else if (ev.key === 'Escape' && modalBackdrop && !modalBackdrop.hidden) {
      ev.preventDefault();
      closeModal();
    }
  });

  document.addEventListener('click', function (ev) {
    var t = ev.target;
    if (!t || !t.closest) return;
    if (t.closest('#mock-strip')) return;

    if (t === modalBackdrop || t.closest('[data-modal-close]')) {
      ev.preventDefault();
      closeModal();
      return;
    }

    var goBtn = t.closest('[data-go-state]');
    if (goBtn) {
      ev.preventDefault();
      var nextSt = goBtn.getAttribute('data-go-state');
      var scrollSel = goBtn.getAttribute('data-scroll');
      var toastMsg = goBtn.getAttribute('data-toast');
      closeModal();
      renderState(nextSt, scrollSel);
      if (toastMsg) showToast(toastMsg);
      return;
    }

    var toastBtn = t.closest('[data-toast]');
    if (toastBtn && !toastBtn.hasAttribute('data-go-state')) {
      ev.preventDefault();
      if (toastBtn.hasAttribute('data-modal-close')) closeModal();
      showToast(toastBtn.getAttribute('data-toast'));
      return;
    }

    var markReadBtn = t.closest('[data-mark-all-read]');
    if (markReadBtn) {
      ev.preventDefault();
      document.querySelectorAll('.notification-item.is-unread').forEach(function (el) {
        el.classList.remove('is-unread');
      });
      document.querySelectorAll('.bell-count').forEach(function (el) {
        el.textContent = '0';
      });
      showToast('All notifications marked as read');
      return;
    }

    var confirmAssignBtn = t.closest('[data-wc-confirm-assign]');
    if (confirmAssignBtn) {
      ev.preventDefault();
      var engSel = modalBox.querySelector('#modal-wc-eng');
      var engName = engSel ? engSel.value : 'Claire Mercer';
      var row2 = root && root.querySelector('#wc-row-2');
      if (row2) {
        var cells = row2.querySelectorAll('td');
        if (cells[2]) { cells[2].textContent = engName; cells[2].classList.remove('muted'); }
      }
      closeModal();
      showToast('Assigned DFD26031 to ' + engName);
      return;
    }

    var resolvePrBtn = t.closest('[data-resolve-problem]');
    if (resolvePrBtn) {
      ev.preventDefault();
      var outcome = resolvePrBtn.getAttribute('data-resolve-problem');
      var badge = root && root.querySelector('[data-problem-status]');
      if (badge) {
        badge.textContent = outcome;
        badge.className = 'status status--green';
      }
      closeModal();
      showToast('Problem report marked ' + outcome);
      return;
    }

    var stopAiBtn = t.closest('[data-confirm-stop-ai]');
    if (stopAiBtn) {
      ev.preventDefault();
      var aiBadge = root && root.querySelector('[data-ai-job-status]');
      if (aiBadge) {
        aiBadge.textContent = 'Stopped';
        aiBadge.className = 'status status--neutral';
      }
      closeModal();
      showToast('AI job stopped');
      return;
    }

    var pwBtn = t.closest('[data-password-reveal], .password-toggle');
    if (pwBtn) {
      ev.preventDefault();
      var wrap = pwBtn.closest('.password-input, .password-field');
      var inp = wrap && wrap.querySelector('input');
      if (inp) {
        var isPw = inp.type === 'password';
        inp.type = isPw ? 'text' : 'password';
      }
      return;
    }

    var copyBtn = t.closest('[data-copy]');
    if (copyBtn) {
      ev.preventDefault();
      var val = copyBtn.getAttribute('data-copy');
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(val).catch(function () {});
      }
      copyBtn.textContent = 'Copied ' + val;
      showToast('Copied ' + val + ' to clipboard');
      return;
    }

    if (t.closest('[data-rail-toggle]')) {
      ev.preventDefault();
      document.body.classList.toggle('rail-collapsed');
      return;
    }

    var collapseBtn = t.closest('[data-collapse-toggle]');
    if (collapseBtn) {
      ev.preventDefault();
      var sec = collapseBtn.closest('.record-section, .sub-panel');
      if (sec) {
        var exp = collapseBtn.getAttribute('aria-expanded') !== 'false';
        collapseBtn.setAttribute('aria-expanded', String(!exp));
        sec.classList.toggle('is-collapsed', exp);
        var body = sec.querySelector('.panel-body, .fg');
        if (body) body.hidden = exp;
      }
      return;
    }

    var openAssign = t.closest('[data-wc-open-assign]');
    if (openAssign) {
      ev.preventDefault();
      openModal('wc-assign-dialog', openAssign);
      return;
    }

    var dlgTrigger = t.closest('[data-dialog-open]');
    if (dlgTrigger) {
      ev.preventDefault();
      openModal(dlgTrigger.getAttribute('data-dialog-open'), dlgTrigger);
      return;
    }

    var dlgClose = t.closest('.dialog-close');
    if (dlgClose) {
      var inlineDialog = dlgClose.closest('.v41-inline-dialog');
      if (inlineDialog) {
        ev.preventDefault();
        inlineDialog.hidden = true;
        showToast('Dialog closed');
        return;
      }
    }

    var dismissBtn = t.closest('.wc-dismiss, button[aria-label="Dismiss"]');
    if (dismissBtn) {
      ev.preventDefault();
      var tr = dismissBtn.closest('tr');
      if (tr) {
        var nextTr = tr.nextElementSibling;
        if (nextTr && nextTr.classList.contains('wc-inline-detail')) nextTr.remove();
        tr.remove();
        showToast('Item dismissed from queue');
      }
      return;
    }

    var contactTab = t.closest('[data-contact-tab]');
    if (contactTab && root) {
      ev.preventDefault();
      var tabKey = contactTab.getAttribute('data-contact-tab');
      root.querySelectorAll('[data-contact-tab]').forEach(function (a) {
        if (a === contactTab) a.setAttribute('aria-current', 'page');
        else a.removeAttribute('aria-current');
      });
      root.querySelectorAll('[data-contact-panel]').forEach(function (p) {
        p.hidden = p.getAttribute('data-contact-panel') !== tabKey;
      });
      return;
    }

    var wcSwitch = t.closest('.wc-switch a');
    if (wcSwitch) {
      ev.preventDefault();
      wcSwitch.parentElement.querySelectorAll('a').forEach(function (a) {
        a.setAttribute('aria-current', String(a === wcSwitch));
      });
      showToast('Scope switched to ' + wcSwitch.textContent.trim());
      return;
    }

    var wcChip = t.closest('.wc-filters a.chip');
    if (wcChip) {
      ev.preventDefault();
      wcChip.parentElement.querySelectorAll('a.chip').forEach(function (c) {
        c.setAttribute('aria-current', String(c === wcChip));
      });
      var kind = wcChip.textContent.split(/\d/)[0].trim().toLowerCase();
      root.querySelectorAll('.wc-ledger-table tbody tr:not(.wc-group-row):not(.wc-inline-detail)').forEach(function (tr) {
        if (kind === 'all') tr.hidden = false;
        else tr.hidden = tr.textContent.toLowerCase().indexOf(kind) === -1;
      });
      return;
    }

    var filmBtn = t.closest('.up-film');
    if (filmBtn && root) {
      ev.preventDefault();
      root.querySelectorAll('.up-film').forEach(function (b) { b.setAttribute('aria-pressed', String(b === filmBtn)); });
      var idx = Array.from(filmBtn.parentElement.children).indexOf(filmBtn);
      var counter = root.querySelector('.up-inspect-top span');
      var img = root.querySelector('.up-inspect-photo img');
      if (counter) counter.textContent = (idx + 1) + ' of 3';
      if (img && TILE_URIS[idx % TILE_URIS.length]) img.src = TILE_URIS[idx % TILE_URIS.length];
      return;
    }

    var searchRow = t.closest('[data-search-results-table] tbody tr');
    if (searchRow && !t.closest('a')) {
      ev.preventDefault();
      searchRow.parentElement.querySelectorAll('tr').forEach(function (r) {
        r.classList.toggle('is-selected', r === searchRow);
        r.setAttribute('aria-selected', String(r === searchRow));
      });
      var refLink = searchRow.querySelector('a.mono');
      var ref = refLink ? refLink.textContent.trim() : 'QDOS26214';
      var prevTitle = root.querySelector('#preview-ref');
      var copyB = root.querySelector('#case-search-preview [data-copy]');
      if (prevTitle) prevTitle.textContent = ref;
      if (copyB) { copyB.setAttribute('data-copy', ref); copyB.textContent = 'Copy Case/PO'; }
      return;
    }

    var cqRow = t.closest('.cases-table tbody tr');
    if (cqRow && !t.closest('a')) {
      ev.preventDefault();
      cqRow.parentElement.querySelectorAll('tr').forEach(function (r) {
        r.classList.toggle('is-selected', r === cqRow);
        r.setAttribute('aria-selected', String(r === cqRow));
      });
      var cRef = cqRow.querySelector('td.mono').textContent.trim();
      var detailTitle = root.querySelector('.cases-detail .detail-title');
      if (detailTitle) detailTitle.textContent = cRef;
      return;
    }

    var inboxRow = t.closest('.inbox-row');
    if (inboxRow && !t.closest('a')) {
      ev.preventDefault();
      inboxRow.parentElement.querySelectorAll('.inbox-row').forEach(function (r) {
        r.classList.toggle('is-active', r === inboxRow);
        r.setAttribute('aria-current', String(r === inboxRow));
      });
      var subj = inboxRow.querySelector('a.row-title');
      var prevSubj = root.querySelector('#mail-quick-preview .mail-subject');
      if (subj && prevSubj) prevSubj.textContent = subj.textContent;
      return;
    }

    var scopeBtn = t.closest('.scope-button');
    if (scopeBtn) {
      ev.preventDefault();
      var scopeContainer = scopeBtn.closest('.scope-list');
      if (scopeContainer) {
        scopeContainer.querySelectorAll('.scope-button').forEach(function (b) {
          b.setAttribute('aria-pressed', String(b === scopeBtn));
        });
      }
      showToast('Filtered by ' + scopeBtn.textContent.replace(/\d+/g, '').trim());
      return;
    }

    var btnEl = t.closest('button');
    if (btnEl && !btnEl.hasAttribute('data-dialog-open') && !btnEl.hasAttribute('data-wc-open-assign')) {
      var btnTxt = btnEl.textContent.trim();
      if (btnTxt === 'Add task') {
        ev.preventDefault();
        var descInput = root.querySelector('#nt-desc');
        var whoSel = root.querySelector('#nt-who');
        var tbody = root.querySelector('[aria-labelledby="case-tasks-dlg-title"] tbody');
        if (descInput && descInput.value.trim() && tbody) {
          var trNew = document.createElement('tr');
          trNew.innerHTML = '<td><strong>' + descInput.value.trim() + '</strong></td>' +
            '<td><span class="status status--amber">Open</span></td>' +
            '<td class="right"><div class="cluster" style="justify-content:flex-end">' +
            '<span class="muted">' + (whoSel ? whoSel.value || 'Unassigned' : 'Rashid Khan') + '</span>' +
            '<button class="btn btn--small btn--primary" type="button">Complete</button></div></td>';
          tbody.appendChild(trNew);
          descInput.value = '';
          showToast('Task added');
        } else {
          showToast('Enter a task description first');
        }
        return;
      }
      if (btnTxt === 'Complete' && btnEl.closest('tr')) {
        ev.preventDefault();
        var taskTr = btnEl.closest('tr');
        var chip = taskTr.querySelector('.status');
        if (chip) { chip.textContent = 'Completed'; chip.className = 'status status--green'; }
        btnEl.disabled = true;
        showToast('Task completed');
        return;
      }
      if (btnTxt === 'Done' || btnTxt === 'Done editing') {
        ev.preventDefault();
        renderState('engineer-read');
        showToast('Saved and exited edit mode');
        return;
      }
      if (btnTxt === 'Edit' || btnTxt === 'Edit case') {
        ev.preventDefault();
        renderState('engineer-edit');
        showToast('Entered edit mode (lease acquired)');
        return;
      }
      if (btnTxt === 'Tasks (2)' || btnTxt === 'Tasks' || btnEl.closest('[data-open-tasks]')) {
        ev.preventDefault();
        renderState('v41-overview', '#case-tasks-dlg-title');
        return;
      }
      if (btnTxt === 'Pair' || btnTxt === 'Pair with Case…') {
        ev.preventDefault();
        showToast('Paired IMG-2026-0019 with Case QDOS26214');
        return;
      }
      if (btnTxt === 'Review and add to Case' || btnTxt === 'Confirm and create case' || btnTxt === 'Create case') {
        ev.preventDefault();
        renderState('engineer-read');
        showToast('Case QDOS26214 opened');
        return;
      }
      if (btnTxt === 'Send report' || btnTxt === 'Send' || btnTxt === 'Send outcome reply' || btnTxt === 'Record response') {
        ev.preventDefault();
        showToast(btnTxt + ' completed');
        return;
      }
      if (/^Save/i.test(btnTxt) || btnTxt === 'Assign' || btnTxt === 'Confirm issue' || btnTxt === 'Dismiss reading') {
        ev.preventDefault();
        showToast(btnTxt + ' saved');
        return;
      }
    }

    var a = t.closest('a[href]');
    if (a) {
      var href = a.getAttribute('href') || '';
      var linkTxt = a.textContent.trim();

      var routeMap = {
        '#work-centre': ['work-centre', null],
        '#work-centre-tabs': ['work-centre-tabs', null],
        '#inbox': ['inbox', null],
        '#mail-message': ['mail-message', null],
        '#upload': ['upload-review', null],
        '#upload-review': ['upload-review', null],
        '#cases': ['cases-queue', null],
        '#cases-queue': ['cases-queue', null],
        '#create-case': ['create-case', null],
        '#search': ['search', null],
        '#admin': ['admin-accounts', null],
        '#admin-accounts': ['admin-accounts', null],
        '#admin-contacts': ['admin-contacts', null],
        '#admin-configuration': ['admin-config-mail', '#admin-sec-configuration'],
        '#admin-mailboxes': ['admin-config-mail', '#admin-sec-mailboxes'],
        '#admin-email-templates': ['admin-config-mail', '#admin-sec-email-templates'],
        '#admin-valuation-presets': ['admin-config-mail', '#admin-sec-valuation-presets'],
        '#admin-reports': ['admin-logs-ops', '#admin-sec-reports'],
        '#admin-logs': ['admin-logs-ops', '#admin-sec-logs'],
        '#admin-health': ['admin-logs-ops', '#admin-sec-health'],
        '#admin-problem-reports': ['admin-logs-ops', '#admin-sec-problem-reports'],
        '#admin-release-notes': ['admin-logs-ops', '#admin-sec-release-notes'],
        '#admin-ai-jobs': ['admin-logs-ops', '#admin-sec-ai-jobs'],
        '#admin-automation': ['admin-logs-ops', '#admin-sec-automation'],
        '#engineer-read': ['engineer-read', null],
        '#engineer-edit': ['engineer-edit', null],
        '#v41-overview': ['v41-overview', null],
        '#triage-case': ['triage-case', null],
        '#unidentified-images': ['unidentified-images', null],
        '#auth-signin': ['auth-signin', null]
      };

      if (routeMap[href]) {
        ev.preventDefault();
        renderState(routeMap[href][0], routeMap[href][1]);
        return;
      }

      if (href.startsWith('#') && href.length > 1) {
        var targetState = href.slice(1);
        if (STATES.some(function (s) { return s.key === targetState; })) {
          ev.preventDefault();
          renderState(targetState);
          return;
        }
        var inPage = root && root.querySelector(href);
        if (inPage) {
          ev.preventDefault();
          inPage.scrollIntoView({ behavior: 'smooth', block: 'start' });
          return;
        }
      }

      ev.preventDefault();
      if (/Work Centre|PEGASUS/i.test(linkTxt)) { renderState('work-centre'); return; }
      if (/^Inbox$/i.test(linkTxt) || /Back to Inbox/i.test(linkTxt)) { renderState('inbox'); return; }
      if (/^Upload$/i.test(linkTxt) || /New upload/i.test(linkTxt)) { renderState('upload-review'); return; }
      if (/^Cases$/i.test(linkTxt) || /Back to Cases/i.test(linkTxt)) { renderState('cases-queue'); return; }
      if (/^Search$/i.test(linkTxt)) { renderState('search'); return; }
      if (/^Administration$/i.test(linkTxt)) { renderState('admin-accounts'); return; }
      if (/QDOS26210|Triages/i.test(linkTxt)) { renderState('triage-case'); return; }
      if (/IMG-2026-0019|Unidentified|Unassigned Images/i.test(linkTxt)) { renderState('unidentified-images'); return; }
      if (/QDOS26214|DFD26031|QDOS26198|QDOS26218|AX26340|Open Case|Open case|Open full Case|Complete engineering report|Review AI Proposal/i.test(linkTxt)) {
        renderState('engineer-read');
        return;
      }
      if (/Needs attention/i.test(linkTxt)) { renderState('work-centre'); return; }
      if (/New cases|AI jobs/i.test(linkTxt)) { renderState('work-centre-tabs'); return; }
      if (/Cancel/i.test(linkTxt)) {
        var compose = a.closest('.mail-compose-panel');
        if (compose) { compose.hidden = true; showToast('Draft discarded'); return; }
        renderState('work-centre');
        return;
      }
      if (/Reply|Reply all|Forward/i.test(linkTxt)) {
        var comp = root && root.querySelector('.mail-compose-panel');
        if (comp) {
          comp.hidden = false;
          comp.scrollIntoView({ behavior: 'smooth', block: 'center' });
          var ta = comp.querySelector('textarea');
          if (ta) ta.focus();
          return;
        }
        renderState('mail-message');
        return;
      }
    }
  }, true);

  document.addEventListener('submit', function (ev) {
    ev.preventDefault();
    showToast('Applied');
  }, true);

  sel.addEventListener('change', function () {
    renderState(sel.value);
  });
  strip.querySelectorAll('[data-set-design]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      design = btn.getAttribute('data-set-design');
      applyPatches();
      syncUrl();
      showToast('Mode: ' + (design === 'proposal' ? 'Proposal (v41)' : 'Today (origin/dev)'));
    });
  });
  strip.querySelectorAll('[data-toggle-param]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var param = btn.getAttribute('data-toggle-param');
      if (param === 'diff') diff = !diff;
      if (param === 'ruler') ruler = !ruler;
      applyPatches();
      syncUrl();
    });
  });
  strip.querySelectorAll('[data-quick-modal]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      openModal(btn.getAttribute('data-quick-modal'));
    });
  });

  window.__mock = {
    state: key,
    design: design,
    states: STATES.map(function (s) { return s.key; }),
    go: renderState,
    setDesign: function (d) {
      design = d === 'today' ? 'today' : 'proposal';
      applyPatches();
      syncUrl();
    },
    openModal: openModal
  };
  renderState(key);
  window.__mockReady = true;
})();
"""


def write_mockup_file(
    filename: str,
    title: str,
    states: list[tuple[str, str, str, str]],
    page_css_names: list[str],
    default_state: str,
) -> None:
    site_css = css_with_fonts("site.css")
    style_tags = [f'<style id="sheet-site">{site_css}</style>']
    for name in page_css_names:
        style_tags.append(f'<style data-sheet="{E(name)}" media="not all">{css_with_fonts(name)}</style>')
    style_tags.append(f'<style id="sheet-proposal">{PROPOSAL_CSS}</style>')
    styles_html = "\n".join(style_tags)

    templates = "\n".join(
        f'<template id="mock-state-{k}" data-title="{E(label)}" data-sheets="{E(sheets)}">{markup}</template>'
        for k, label, sheets, markup in states
    )
    states_json = json.dumps([{"key": k, "label": label} for k, label, _, _ in states])
    runtime = (
        RUNTIME_JS.replace("__STATES__", states_json)
        .replace("__DEFAULT_STATE__", json.dumps(default_state))
        .replace("__TILE_URIS__", json.dumps(TILE_URIS))
    )
    strip_html = """
    <details id="mock-strip" open>
      <summary><span>Mockup controls</span><small>v41 Interactive</small></summary>
      <div class="mock-body">
        <small>Full interactive mockup. Click any rail link, table row, tab, filter, or button, or use the controls below.</small>
        <div class="mock-seg" role="group" aria-label="Design mode">
          <button type="button" class="mock-btn" data-set-design="proposal">Proposal (v41)</button>
          <button type="button" class="mock-btn" data-set-design="today">Today (live)</button>
        </div>
        <label>
          <small>Page &amp; state (all 27 surfaces)</small>
          <select id="mock-state" aria-label="Page and state"></select>
        </label>
        <div class="mock-seg--4" role="group" aria-label="Quick modals">
          <button type="button" class="mock-btn" data-quick-modal="cmd-dialog" title="Quick jump (Ctrl+K)">Ctrl+K</button>
          <button type="button" class="mock-btn" data-quick-modal="account-dialog" title="Account dialog">Account</button>
          <button type="button" class="mock-btn" data-quick-modal="notifications-dialog" title="Notifications dialog">Alerts</button>
          <button type="button" class="mock-btn" data-quick-modal="wc-assign-dialog" title="Assign Engineer modal">Assign</button>
        </div>
        <div class="mock-seg" role="group" aria-label="Inspection overlays">
          <button type="button" class="mock-btn" data-toggle-param="diff">Diff badges</button>
          <button type="button" class="mock-btn" data-toggle-param="ruler">Height ruler</button>
        </div>
        <small>Query presets: <code>?state=…</code>, <code>?design=proposal|today</code>, <code>?diff=1</code>, <code>?ruler=1</code>, <code>?strip=0</code></small>
      </div>
    </details>
    <div id="v41-modal-backdrop" hidden><div id="v41-modal-box"></div></div>
    <div id="v41-toast" role="status" aria-live="polite" hidden></div>
    """
    doc = (
        f"<!DOCTYPE html>\n<html lang=\"en-GB\">\n<head>\n<meta charset=\"utf-8\" />\n"
        f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n"
        f"<title>{E(title)}</title>\n"
        f"{styles_html}\n"
        f"</head>\n<body>\n{SPRITE_HTML}\n<div id=\"mock-root\"></div>\n{templates}\n{strip_html}\n"
        f"<script>window.mockupErrors=[];window.addEventListener('error',function(e){{window.mockupErrors.push(e.message);}});</script>\n"
        f"<script>{runtime}</script>\n</body>\n</html>\n"
    )
    out_path = HERE / filename
    out_path.write_text(doc, encoding="utf-8")
    print(f"Wrote {out_path.name}: {len(states)} states, {len(doc) // 1024} KB")


def main() -> None:
    shell_states = build_shell_states()
    case_states = build_case_workspace_states()
    all_states = shell_states + case_states
    page_css = [
        "work-centre.css",
        "inbox.css",
        "upload.css",
        "cases-index.css",
        "triage.css",
        "unidentified.css",
        "image-record.css",
        "pre-case-images.css",
        "admin.css",
        "logs.css",
        "case-workspace.css",
    ]

    write_mockup_file(
        "pegasus_v41.html",
        "Pegasus v41 — Full Interactive Application Proposal Mockup",
        all_states,
        page_css,
        default_state="work-centre",
    )

    write_mockup_file(
        "pegasus_shell_v41.html",
        "Pegasus v41 — Full Application Shell, Queues, Intake & Administration Mockup",
        all_states,
        page_css,
        default_state="auth-signin",
    )

    write_mockup_file(
        "pegasus_case_workspace_v41.html",
        "Pegasus v41 — Case Record Workspace Mockup",
        case_states + shell_states,
        page_css,
        default_state="v41-overview",
    )


if __name__ == "__main__":
    main()
