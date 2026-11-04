"""Proposal patches for the v48 round: the Send report dialog and the Original report card.

Each patch edits a captured live page (a BeautifulSoup <body>) and records what it
changed. Every change carries one ID, its sign-off letter in notes/v48-notes.md §6.
The patches are in proposals_send.py (the dialog) and proposals_card.py (the card).

A patch asserts the live markup it moves is there: a missing anchor is a build error,
never a silent skip (the v47 patches returned silently).

Rules every patch follows: no new operator sentence (labels are the live strings from
CaseWorkspaceLabels, or the composer's own field labels); Today stays the capture.
"""
from __future__ import annotations

import importlib
import json
import pathlib
from typing import Callable

from bs4 import BeautifulSoup, Tag

CAPTURED = pathlib.Path(__file__).resolve().parent.parent / "captured-live"

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


Preset = Callable[[Tag, dict], None]
PRESETS: dict[str, list[Preset]] = {}


def presets(*keys: str) -> Callable[[Preset], Preset]:
    def register(fn: Preset) -> Preset:
        for key in keys:
            PRESETS.setdefault(key, []).append(fn)
        return fn
    return register


def preset(key: str, body: Tag, state: dict) -> None:
    for fn in PRESETS.get(key, []):
        fn(body, state)


def facts_for(state: dict) -> dict:
    """The fixture facts the capture wrote beside itself ({name}.facts.json)."""
    path = CAPTURED / state["lane"] / f'{state["capture"]}.facts.json'
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


class Anchor(Exception):
    """A live element a patch needs is not in the capture."""


class Ctx:
    def __init__(self, body: Tag, state: dict, changes: list[dict]):
        self.body, self.state, self.changes = body, state, changes
        self.key = state["key"]
        self.facts = state.get("facts") or facts_for(state)

    # -- recording ---------------------------------------------------------
    def record(self, change_id: str, summary: str) -> None:
        if not any(c["id"] == change_id for c in self.changes):
            self.changes.append({"id": change_id, "summary": summary})

    def mark(self, element: Tag | None, change_id: str, summary: str) -> Tag | None:
        if element is None:
            raise Anchor(f"{self.key}: nothing to mark for {change_id}")
        existing = element.get("data-v48-change")
        element["data-v48-change"] = change_id if not existing else f"{existing} {change_id}"
        self.record(change_id, summary)
        return element

    def remove(self, element: Tag | None, change_id: str, summary: str) -> bool:
        if element is None:
            raise Anchor(f"{self.key}: nothing to remove for {change_id}")
        element.decompose()
        self.record(change_id, summary)
        return True

    # -- finding -----------------------------------------------------------
    def one(self, css: str) -> Tag | None:
        return self.body.select_one(css)

    def need(self, css: str, within: Tag | None = None) -> Tag:
        found = (within or self.body).select_one(css)
        if found is None:
            raise Anchor(f"{self.key}: live anchor not found: {css}")
        return found

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

    def style(self, css: str, change_id: str, summary: str | None = None) -> None:
        """A proposed stylesheet rule, injected into the page body."""
        tag = self.html(f'<style data-v48-css="{change_id}">{css}</style>')
        self.body.append(tag)
        if summary:
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


for _module in ("proposals_send", "proposals_card"):
    importlib.import_module(_module)
