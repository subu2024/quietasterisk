"""
Book chapters: model, loading, ordering, and URL helpers.

A book in books.json becomes "readable" when config.BOOK_CHAPTER_FOLDERS
maps its title to a folder of markdown files under config.BOOK_CHAPTERS_DIR.
Each file is one chapter; chapters are ordered by filename (natural sort, so
2-x.md comes before 10-x.md).

Page naming (all flat, in the output root like every other page):
    book-<folder-slug>.html                     chapter list ("Home" button)
    book-<folder-slug>-<chapter-file-slug>.html one page per chapter
"""

import re
import logging
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Dict, Tuple

from config import BOOK_CHAPTERS_DIR, BOOK_CHAPTER_FOLDERS
from utils import slugify

logger = logging.getLogger("BlogGen")

_FRONT_MATTER_RE = re.compile(r"\A\s*---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)(.*)\Z", re.DOTALL)
_TRUE_VALUES = ("true", "yes", "1")


@dataclass
class Chapter:
    """One chapter of a book, parsed from a markdown file."""

    path: Path
    slug: str          # file-based slug, unique within the book
    number: int        # 1-based position in the book
    title: str
    synopsis: str
    keywords: List[str]
    locked: bool
    body: str
    book_slug: str = ""

    @property
    def url(self) -> str:
        return f"book-{self.book_slug}-{self.slug}.html"

    @property
    def reading_time(self) -> str:
        words = len(self.body.split())
        return f"{max(1, round(words / 155))} min read"


@dataclass
class BookChapters:
    """All chapters of one book, in reading order."""

    book_title: str
    slug: str
    chapters: List[Chapter] = field(default_factory=list)

    @property
    def toc_url(self) -> str:
        """The book's chapter-list page (also the target of the Home button)."""
        return f"book-{self.slug}.html"


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


@lru_cache(maxsize=None)
def get_book_chapters(book_title: str) -> Optional[BookChapters]:
    """
    Load a book's chapters, or None if the book has no chapter folder
    configured / the folder is missing or empty.

    Cached per title so the homepage, the Books page and the chapter
    generator all share one read (and each warning is logged only once).
    """
    folder_name = BOOK_CHAPTER_FOLDERS.get(book_title)
    if not folder_name:
        return None

    folder = BOOK_CHAPTERS_DIR / folder_name
    if not folder.is_dir():
        logger.warning(
            "Book %r maps to chapter folder %s, which does not exist — "
            "no 'Read Me' button will be shown for it.", book_title, folder
        )
        return None

    files = sorted(folder.glob("*.md"), key=_natural_key)
    if not files:
        logger.warning("Chapter folder %s has no .md files — skipping book %r.", folder, book_title)
        return None

    book_slug = slugify(folder_name) or slugify(book_title) or "book"
    chapters: List[Chapter] = []
    used_slugs = set()

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

        title = meta.get("title") or md_file.stem.replace("_", " ").replace("-", " ").strip().title()
        if not meta.get("title"):
            logger.warning("Chapter %s has no title in its front matter; using %r.", md_file.name, title)

        chapters.append(Chapter(
            path=md_file,
            slug=slug,
            number=len(chapters) + 1,
            title=title,
            synopsis=meta.get("synopsis", ""),
            keywords=_parse_keywords(meta.get("keywords", "")),
            locked=meta.get("lock", "").lower() in _TRUE_VALUES,
            body=body,
            book_slug=book_slug,
        ))

    if not chapters:
        return None
    return BookChapters(book_title=book_title, slug=book_slug, chapters=chapters)


def warn_about_unmatched_folder_config(books: List[dict]) -> None:
    """Warn if BOOK_CHAPTER_FOLDERS has a key that matches no book in books.json."""
    titles = {b.get("title", "") for b in books}
    for key in BOOK_CHAPTER_FOLDERS:
        if key not in titles:
            logger.warning(
                "BOOK_CHAPTER_FOLDERS has an entry for %r, but no book in books.json "
                "has that exact title — its chapters will not be published.", key
            )


def lock_icon() -> str:
    """Small padlock SVG used on the chapter list and the locked-chapter notice."""
    return ('<svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24" '
            'aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="1" stroke-width="2"/>'
            '<path stroke-linecap="round" stroke-width="2" d="M8 11V8a4 4 0 018 0v3"/></svg>')
