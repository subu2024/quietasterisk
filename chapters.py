"""
Publications: online-readable series and books, loaded from publications.json.

A "publication" is anything readable chapter by chapter on the site, whether
it is a fiction series like Sunday Odds or a book from books.json. Every
publication is one entry in config.PUBLICATIONS_FILE and has its own folder of
markdown chapters under config.BOOK_CHAPTERS_DIR. Adding another one needs no
code changes: add a folder and add an entry.

publications.json shape:

    {
      "defaults": { ...values used when an entry omits them... },
      "publications": [
        {
          "title": "Sunday Odds",          required, shown on pages
          "folder": "sunday_odds",         required, under BOOK_CHAPTERS_DIR
          "page_prefix": "series",         optional, default "book-<folder-slug>"
          "linked_book": "<title>",        optional, exact title in books.json;
                                           adds Buy/Download buttons and falls
                                           back to that book's description
          "eyebrow": "The Series",         small label above the title
          "eyebrow_url": "books.html",     optional, makes the eyebrow a link
          "premise": "...",                homepage card text
          "intro": "...",                  top of the chapter-list page
          "read_note": "...",              line under the intro
          "disclaimer": "...",             shown on every chapter + chapter list
          "speakers": ["Revathi", ...],    enables **Name:** dialogue styling
          "locked_message": "...",         shown instead of a locked chapter
          "start_label": "...",            first-chapter button label
          "see_all_label": "...",          homepage secondary button label
          "home_label": "...",             chapter-nav "up" button label
          "show_on_home": true             feature on the homepage
        }
      ]
    }

Page naming (flat, in the output root):
    <page_prefix>.html                      chapter list
    <page_prefix>-<chapter-file-slug>.html  one page per chapter

A chapter can override its own page name with a `slug:` line in its front
matter (e.g. `slug: plan-for-the-bad-month`). That is used as the URL instead
of the generated name, with ".html" added if it has no extension. Chapters
without one keep the generated name.

Chapters are ordered by filename (natural sort, so 2-x.md comes before 10-x.md).
"""

import re
import json
import logging
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Dict, Tuple

from config import BOOK_CHAPTERS_DIR, PUBLICATIONS_FILE
from utils import slugify

logger = logging.getLogger("BlogGen")

_FRONT_MATTER_RE = re.compile(r"\A\s*---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)(.*)\Z", re.DOTALL)
_TRUE_VALUES = ("true", "yes", "1")

# Used only if publications.json has no "defaults" block (or omits a key).
_BUILTIN_DEFAULTS = {
    "start_label": "Start with Chapter 1",
    "see_all_label": "See all chapters",
    "home_label": "All chapters",
    "locked_message": "This chapter is locked for now. Check back soon.",
    "show_on_home": True,
}


@dataclass
class Chapter:
    """One chapter of a publication, parsed from a markdown file."""

    path: Path
    slug: str          # file-based slug, unique within the publication
    number: int        # 1-based position
    title: str
    synopsis: str
    keywords: List[str]
    locked: bool
    body: str
    page_prefix: str = ""
    asterisk: str = ""   # optional closing note: the line this chapter leaves you with
    teaser: str = ""     # optional "Next Sunday, ..." line shown after the closing note
    custom_slug: str = ""  # optional `slug:` front-matter line; overrides the generated URL

    @property
    def url(self) -> str:
        """
        The chapter's page filename. A `slug:` in the chapter's front matter is
        used as-is (".html" added if it has no extension); otherwise the URL is
        generated from the publication prefix and the file name.
        """
        if self.custom_slug:
            return self.custom_slug
        return f"{self.page_prefix}-{self.slug}.html"

    @property
    def reading_time(self) -> str:
        words = len(self.body.split())
        return f"{max(1, round(words / 155))} min read"


@dataclass
class Publication:
    """A series or book and all its chapters, in reading order."""

    title: str
    slug: str
    page_prefix: str
    folder: str
    chapters: List[Chapter] = field(default_factory=list)
    linked_book: str = ""
    eyebrow: str = ""
    eyebrow_url: str = ""
    premise: str = ""
    intro: str = ""
    read_note: str = ""
    disclaimer: str = ""
    speakers: Tuple[str, ...] = ()
    locked_message: str = ""
    start_label: str = ""
    see_all_label: str = ""
    home_label: str = ""
    show_on_home: bool = True

    @property
    def toc_url(self) -> str:
        """The chapter-list page (also the target of the up/"All chapters" button)."""
        return f"{self.page_prefix}.html"

    @property
    def first_chapter(self) -> Optional[Chapter]:
        return self.chapters[0] if self.chapters else None


# ----------------------------------------------------------------------
# Chapter files
# ----------------------------------------------------------------------

def _natural_key(path: Path):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", path.name)]


def parse_chapter_file(text: str) -> Tuple[Dict[str, str], str]:
    """
    Split a chapter's markdown into (front-matter dict, body).

    Keys are lowercased; surrounding quotes on values are stripped. A file
    with no front matter returns ({}, whole text).
    """
    text = text.replace("\r\n", "\n")
    match = _FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text.strip()

    meta: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        m = re.match(r"^\s*([A-Za-z_][\w-]*)\s*:\s*(.*?)\s*$", line)
        if not m:
            continue
        value = m.group(2)
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        meta[m.group(1).lower()] = value
    return meta, match.group(2).strip()


def _parse_keywords(raw: str) -> List[str]:
    raw = raw.strip().strip("[]")
    return [k.strip().strip("\"'") for k in raw.split(",") if k.strip().strip("\"'")]


def _normalize_custom_slug(raw: str) -> str:
    """Front-matter `slug:` -> page filename ("" if blank/unusable)."""
    value = (raw or "").strip().strip("/")
    if not value:
        return ""
    if "/" in value or "\\" in value or value.startswith("."):
        return ""  # pages are flat in the output root; reject paths
    return value if re.search(r"\.[A-Za-z0-9]+$", value) else f"{value}.html"


def _load_chapters(folder: Path, page_prefix: str) -> List[Chapter]:
    files = sorted(folder.glob("*.md"), key=_natural_key)
    chapters: List[Chapter] = []
    used_slugs = set()
    used_urls = set()

    for number, md_file in enumerate(files, start=1):
        try:
            meta, body = parse_chapter_file(md_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Failed to read chapter %s: %s", md_file, e)
            continue

        slug = slugify(md_file.stem) or f"chapter-{number}"
        if slug in used_slugs:
            slug = f"{slug}-{number}"
        used_slugs.add(slug)

        locked = meta.get("lock", "").lower() in _TRUE_VALUES
        if not locked and "[CHECK" in body:
            logger.warning(
                "Chapter %s is published but still contains a [CHECK ...] marker "
                "(an unresolved fact-check note) — resolve it before deploying.", md_file.name
            )

        title = meta.get("title") or md_file.stem.replace("_", " ").replace("-", " ").strip().title()
        if not meta.get("title"):
            logger.warning("Chapter %s has no title in its front matter; using %r.", md_file.name, title)

        raw_custom = meta.get("slug", "")
        custom_slug = _normalize_custom_slug(raw_custom)
        if raw_custom.strip() and not custom_slug:
            logger.warning("Chapter %s has an unusable slug %r (no paths or leading dots); "
                           "using the generated URL.", md_file.name, raw_custom)

        chapters.append(Chapter(
            path=md_file,
            slug=slug,
            number=len(chapters) + 1,
            title=title,
            synopsis=meta.get("synopsis", ""),
            keywords=_parse_keywords(meta.get("keywords", "")),
            locked=locked,
            body=body,
            page_prefix=page_prefix,
            asterisk=meta.get("asterisk", ""),
            teaser=meta.get("teaser", ""),
            custom_slug=custom_slug,
        ))
        url = chapters[-1].url
        if url in used_urls:
            logger.warning("Chapter %s resolves to URL %s, already used by another chapter "
                           "in this publication — one page will overwrite the other.",
                           md_file.name, url)
        used_urls.add(url)
    return chapters


# ----------------------------------------------------------------------
# publications.json
# ----------------------------------------------------------------------

def _read_publications_config() -> Tuple[dict, List[dict]]:
    """Return (defaults, entries) from PUBLICATIONS_FILE; ({}, []) if absent."""
    path = Path(PUBLICATIONS_FILE)
    if not path.exists():
        logger.warning("%s not found — no series or book chapters will be published.", path)
        return {}, []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit(f"Cannot read {path}: {e}")

    # Accept a bare list of entries as well as {"defaults": ..., "publications": [...]}.
    if isinstance(data, list):
        return {}, data
    return data.get("defaults", {}) or {}, data.get("publications", []) or []


@lru_cache(maxsize=None)
def get_publications() -> Tuple[Publication, ...]:
    """
    Every publication that has at least one chapter, in the order listed in
    publications.json.

    Cached so the homepage, the Books page and the page generator share one
    read (and each warning is logged only once per build). Entries with a
    missing/invalid folder or no chapters are skipped with a warning.
    """
    defaults, entries = _read_publications_config()
    defaults = {**_BUILTIN_DEFAULTS, **defaults}

    publications: List[Publication] = []
    used_prefixes = set()

    for position, entry in enumerate(entries, start=1):
        title = (entry.get("title") or "").strip()
        folder_name = (entry.get("folder") or "").strip()
        if not title or not folder_name:
            logger.warning("%s entry #%d needs both \"title\" and \"folder\" — skipped.",
                           PUBLICATIONS_FILE, position)
            continue
        if title.startswith("["):
            logger.warning("Publication title %r looks like a placeholder — set the real "
                           "title before publishing.", title)

        folder = Path(BOOK_CHAPTERS_DIR) / folder_name
        if not folder.is_dir():
            logger.warning("%r maps to chapter folder %s, which does not exist — "
                           "no chapters will be published for it.", title, folder)
            continue

        slug = slugify(folder_name) or slugify(title) or "publication"
        page_prefix = (entry.get("page_prefix") or f"book-{slug}").strip()
        if page_prefix in used_prefixes:
            logger.warning("Publication %r reuses page_prefix %r already used above — "
                           "its pages would overwrite the other's. Skipped.", title, page_prefix)
            continue
        used_prefixes.add(page_prefix)

        chapters = _load_chapters(folder, page_prefix)
        if not chapters:
            logger.warning("Chapter folder %s has no readable .md files — skipping %r.", folder, title)
            continue

        def pick(key: str) -> str:
            return entry.get(key, defaults.get(key, "")) or ""

        publications.append(Publication(
            title=title,
            slug=slug,
            page_prefix=page_prefix,
            folder=folder_name,
            chapters=chapters,
            linked_book=(entry.get("linked_book") or "").strip(),
            eyebrow=pick("eyebrow"),
            eyebrow_url=pick("eyebrow_url"),
            premise=pick("premise"),
            intro=pick("intro"),
            read_note=pick("read_note"),
            disclaimer=pick("disclaimer"),
            speakers=tuple(entry.get("speakers", defaults.get("speakers", [])) or []),
            locked_message=pick("locked_message"),
            start_label=pick("start_label"),
            see_all_label=pick("see_all_label"),
            home_label=pick("home_label"),
            show_on_home=bool(entry.get("show_on_home", defaults.get("show_on_home", True))),
        ))

    return tuple(publications)


def get_publication_for_book(book_title: str) -> Optional[Publication]:
    """The publication linked to a books.json title (via "linked_book"), if any."""
    key = (book_title or "").strip().casefold()
    if not key:
        return None
    for pub in get_publications():
        if pub.linked_book and pub.linked_book.strip().casefold() == key:
            return pub
    return None


def warn_about_unmatched_book_links(books: List[dict]) -> None:
    """Warn if a publication's "linked_book" matches no title in books.json."""
    titles = {b.get("title", "").strip().casefold() for b in books}
    _, entries = _read_publications_config()
    for entry in entries:
        link = (entry.get("linked_book") or "").strip()
        if link and link.casefold() not in titles:
            logger.warning(
                "Publication %r has linked_book %r, but no book in books.json has that "
                "title — its Buy/Download buttons and description fallback won't apply.",
                entry.get("title"), link
            )


def lock_icon() -> str:
    """Small padlock SVG used on the chapter list and the locked-chapter notice."""
    return ('<svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24" '
            'aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="1" stroke-width="2"/>'
            '<path stroke-linecap="round" stroke-width="2" d="M8 11V8a4 4 0 018 0v3"/></svg>')
