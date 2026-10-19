"""Proposal patches for the v41 redesign.

Each patch edits a captured live page (a BeautifulSoup <body>) and records what it
changed. Every change carries one ID (for example I3 or A7); the ID is also its
sign-off item in v41-notes.md. Patches live in one module per area:

    proposals_shell.py   S  shell, sign-in, consent, errors, release notes
    proposals_work.py    W  Work Centre and Search
    proposals_inbox.py   I  Inbox and the message dialog
    proposals_intake.py  U  Upload, Cases, Create case, Triage, Unidentified, Vehicle images
    proposals_case.py    K  Case workspace
    proposals_admin.py   A  Administration

Rules every patch follows: no new operator sentence (labels, values and button text
only); no new rule, validation or default; Today stays the capture untouched.
"""
from __future__ import annotations

import importlib
from typing import Callable

from bs4 import BeautifulSoup, Tag

Patch = Callable[["Ctx"], None]
REGISTRY: dict[str, list[Patch]] = {}
EVERY_APP_PAGE = "*app"


def patch(*keys: str) -> Callable[[Patch], Patch]:
    """Register a patch for the given state keys ("*app" = every page with the app shell)."""
    def register(fn: Patch) -> Patch:
        for key in keys:
            REGISTRY.setdefault(key, []).append(fn)
        return fn
    return register


class Ctx:
    def __init__(self, body: Tag, state: dict, changes: list[dict]):
        self.body, self.state, self.changes = body, state, changes
        self.key = state["key"]

    # -- recording ---------------------------------------------------------
    def record(self, change_id: str, summary: str) -> None:
        if not any(c["id"] == change_id for c in self.changes):
            self.changes.append({"id": change_id, "summary": summary})

    def mark(self, element: Tag | None, change_id: str, summary: str) -> Tag | None:
        if element is None:
            return None
        existing = element.get("data-v41-change")
        element["data-v41-change"] = change_id if not existing else f"{existing} {change_id}"
        self.record(change_id, summary)
        return element

    def remove(self, element: Tag | None, change_id: str, summary: str) -> bool:
        if element is None:
            return False
        element.decompose()
        self.record(change_id, summary)
        return True

    # -- finding -----------------------------------------------------------
    def one(self, css: str) -> Tag | None:
        return self.body.select_one(css)

    def all(self, css: str) -> list[Tag]:
        return self.body.select(css)

    def by_text(self, css: str, text: str, exact: bool = True) -> Tag | None:
        for element in self.body.select(css):
            value = element.get_text(" ", strip=True)
            if (value == text) if exact else (text in value):
                return element
        return None

    # -- building ----------------------------------------------------------
    @staticmethod
    def html(markup: str) -> Tag:
        fragment = BeautifulSoup(f"<div>{markup}</div>", "lxml").div
        nodes = [n for n in fragment.contents if isinstance(n, Tag)]
        return nodes[0] if len(nodes) == 1 else fragment

    def style(self, css: str, change_id: str, summary: str) -> None:
        """A proposed stylesheet rule, injected into the page body."""
        tag = self.html(f'<style data-v41-css="{change_id}">{css}</style>')
        self.body.append(tag)
        self.record(change_id, summary)


def apply(key: str, body: Tag, state: dict) -> list[dict]:
    changes: list[dict] = []
    ctx = Ctx(body, state, changes)
    patches = list(REGISTRY.get(key, []))
    if body.select_one(".app-shell") is not None:
        patches = REGISTRY.get(EVERY_APP_PAGE, []) + patches
    for fn in patches:
        fn(ctx)
    return changes


for _module in ("proposals_shell", "proposals_work", "proposals_inbox",
                "proposals_intake", "proposals_case", "proposals_admin",
                "proposals_records"):
    try:
        importlib.import_module(_module)
    except ModuleNotFoundError as error:
        if error.name != _module:
            raise
