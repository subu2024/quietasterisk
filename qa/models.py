"""Plain data classes: everything the engine knows about the content.

These objects are also what themes receive in their template context
(see docs/THEME_CONTRACT.md), so every attribute here is part of the contract.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

LAYOUT_ESSAYS = "essays"
LAYOUT_CHAPTERS = "chapters"


def slugify(text: str) -> str:
    """'Self-Awareness & EQ' -> 'self-awareness-eq'."""
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")


def title_slug(text: str) -> str:
    """Legacy essay URL rule (kept so existing URLs never change)."""
    words = re.findall(r"\w+", text)
    return "-".join(words).lower() or "untitled"


@dataclass
class Entry:
    """One published markdown file: an essay, a chapter, a poem..."""

    path: Path
    collection_id: str
    layout: str
    title: str
    file_slug: str
    date: str = ""
    category: str = ""
    synopsis: str = ""
    keywords: List[str] = field(default_factory=list)
    lock: bool = False
    body: str = ""                 # markdown source
    asterisk: str = ""
    teaser: str = ""
    image: str = ""                # optional social-share image (file in assets/images)
    custom_slug: str = ""
    aliases: List[str] = field(default_factory=list)   # old page names that redirect here
    page_prefix: str = ""
    number: int = 0                # 1-based reading position
    body_html: str = ""            # filled in by the build

    @property
    def url(self) -> str:
        if self.custom_slug:
            return self.custom_slug
        if self.page_prefix:
            return f"{self.page_prefix}-{self.file_slug}.html"
        return f"{title_slug(self.title or self.path.stem)}.html"

    @property
    def reading_minutes(self) -> int:
        return max(1, round(len(self.body.split()) / 155))

    @property
    def parsed_date(self) -> Optional[datetime]:
        try:
            return datetime.strptime(self.date, "%Y-%m-%d")
        except (ValueError, TypeError):
            return None

    @property
    def iso_date(self) -> str:
        return self.date if self.parsed_date else ""

    @property
    def year(self) -> Optional[int]:
        d = self.parsed_date
        return d.year if d else None

    @property
    def date_display(self) -> str:
        d = self.parsed_date
        return d.strftime("%B %Y") if d else (self.date or "")

    @property
    def category_slug(self) -> str:
        return slugify(self.category)

    @property
    def category_hash(self) -> int:
        """Stable integer per category, so a theme can cycle accent colours."""
        return sum(ord(ch) for ch in self.category) if self.category else 0


@dataclass
class Collection:
    """A folder of entries plus its settings from collections.json."""

    id: str
    title: str
    folder: str
    layout: str
    sort: str
    page_prefix: str
    entries: List[Entry] = field(default_factory=list)
    show_on_home: Optional[int] = None    # None hidden / 0 synopsis only / N top N
    synopsis: str = ""
    linked_book: str = ""
    eyebrow: str = ""
    eyebrow_url: str = ""
    intro: str = ""
    read_note: str = ""
    disclaimer: str = ""
    speakers: tuple = ()
    start_label: str = ""
    see_all_label: str = ""
    home_label: str = ""
    home_heading: str = ""

    @property
    def descending(self) -> bool:
        return self.sort == "descending"

    @property
    def url(self) -> str:
        """The page that lists the whole collection."""
        return "essays.html" if self.layout == LAYOUT_ESSAYS else f"{self.page_prefix}.html"

    @property
    def start_entry(self) -> Optional[Entry]:
        return min(self.entries, key=lambda e: e.number) if self.entries else None

    @property
    def home_entries(self) -> List[Entry]:
        return self.entries[: self.show_on_home] if self.show_on_home else []


@dataclass
class PageDoc:
    """A standalone markdown page (About, Contact...) from content/pages/."""

    path: Path
    key: str                       # file stem, e.g. "about"; the name used in nav and `urls`
    title: str
    url: str
    template: str = "default"      # theme template: page_<template>.html
    description: str = ""
    section: str = ""
    meta: Dict[str, str] = field(default_factory=dict)   # every front-matter key, for the theme
    body: str = ""
    body_html: str = ""


@dataclass
class Action:
    kind: str       # "read" | "buy" | "download"
    label: str
    href: str
    external: bool


@dataclass
class Book:
    title: str
    description: str = ""
    author: str = ""
    year: str = ""
    image_url: str = ""
    video_id: str = ""
    link_label: str = ""
    actions: List[Action] = field(default_factory=list)
    unavailable_label: str = ""
    anchor: str = ""               # element id, "book-<slug>"
    cross_link: str = ""           # "#note-<slug>" when a reading note has the same title


@dataclass
class Note:
    title: str
    note: str = ""
    author: str = ""
    date: str = ""
    link: str = ""
    anchor: str = ""               # "note-<slug>"
    cross_link: str = ""           # "#book-<slug>" when one of the author's books has the same title


@dataclass
class Thought:
    text: str
    date: str = ""
    iso_date: str = ""
    date_display: str = ""         # "October 17, 2026"


@dataclass
class Video:
    title: str
    video_id: str
    article_link: str = ""


@dataclass
class CategoryInfo:
    name: str
    slug: str
    description: str
    entries: List[Entry] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.entries)

    @property
    def url(self) -> str:
        return f"category-{self.slug}.html"
