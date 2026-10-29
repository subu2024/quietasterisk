"""
Content layer: reads everything from content/ into models.

    content/site.json              -> qa.settings
    content/collections.json       -> Collection (+ Entry per markdown file)
    content/<folder>/*.md          -> Entry
    content/pages/*.md             -> PageDoc
    content/data/*.json            -> Book, Note, Thought, Video, category blurbs

No globals and no caching: load_content() returns one Content object, so
builds and tests are independent of each other.
"""

import difflib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import date as date_cls
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

from . import frontmatter
from .models import (
    LAYOUT_CHAPTERS, LAYOUT_ESSAYS, Action, Book, CategoryInfo, Collection, Entry,
    Note, PageDoc, Thought, Video, slugify, title_slug,
)

logger = logging.getLogger("qa")

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

COLLECTION_KEYS = {
    "id", "title", "folder", "layout", "lock", "sort", "show_on_home", "synopsis", "premise",
    "see_all_label", "page_prefix", "linked_book", "eyebrow", "eyebrow_url", "intro",
    "read_note", "disclaimer", "speakers", "start_label", "home_label", "home_heading",
}

_BUILTIN_DEFAULTS = {
    "layout": LAYOUT_CHAPTERS,
    "show_on_home": 0,
    "start_label": "Start with Chapter 1",
    "see_all_label": "See all chapters",
    "home_label": "All chapters",
}


@dataclass
class Content:
    settings: dict
    collections: List[Collection] = field(default_factory=list)
    pages: Dict[str, PageDoc] = field(default_factory=dict)
    books: List[Book] = field(default_factory=list)
    notes: List[Note] = field(default_factory=list)
    thoughts: List[Thought] = field(default_factory=list)     # display order
    videos: List[Video] = field(default_factory=list)
    category_blurbs: Dict[str, str] = field(default_factory=dict)
    essays: List[Entry] = field(default_factory=list)         # pooled, display order
    essays_descending: bool = True

    @property
    def all_entries(self) -> List[Entry]:
        return [e for c in self.collections for e in c.entries]


# ----------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------

def normalize_page_name(raw: str) -> str:
    """Front-matter `slug:` / `aliases:` value -> flat page filename ("" if unusable)."""
    value = (raw or "").strip().strip("/")
    if not value:
        return ""
    if "/" in value or "\\" in value or value.startswith("."):
        return ""
    if re.search(r"\.[A-Za-z0-9]+$", value):
        return value
    return f"{title_slug(value)}.html"


def _natural_key(path: Path):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", path.name)]


def _sort_key(entry: Entry):
    return (entry.date or "", _natural_key(entry.path))


def _read_json(path: Path, expected_type) -> object:
    if not path.exists():
        return expected_type()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Cannot read %s: %s", path.name, e)
        return expected_type()
    if not isinstance(data, expected_type):
        logger.warning("%s should contain a JSON %s; ignoring it.", path.name, expected_type.__name__)
        return expected_type()
    return data


# ----------------------------------------------------------------------
# Entries
# ----------------------------------------------------------------------

def parse_entry_file(md_file: Path, collection_id: str, layout: str, page_prefix: str) -> Optional[Entry]:
    try:
        meta, body = frontmatter.parse(md_file.read_text(encoding="utf-8"))
    except Exception as e:  # unreadable / bad encoding
        logger.warning("Failed to read %s: %s", md_file, e)
        return None

    title = meta.get("title") or ""
    if not title:
        title = md_file.stem.replace("_", " ").replace("-", " ").strip().title() or "Untitled"
        logger.warning("%s has no title in its front matter; using %r.", md_file.name, title)

    lock = frontmatter.as_bool(meta.get("lock", "")) or frontmatter.as_bool(meta.get("archived", ""))

    date = meta.get("date", "")
    if date and not _DATE_RE.match(date):
        logger.warning("%s has date %r; use YYYY-MM-DD so it sorts correctly.", md_file.name, date)
    synopsis = meta.get("synopsis") or meta.get("excerpt") or ""
    if layout == LAYOUT_ESSAYS and not lock:
        if not date:
            logger.warning("Essay %s has no date; it will sort to the end and be left out of the by-year view.", md_file.name)
        if not synopsis:
            logger.warning("Essay %s has no synopsis; its card and search snippet will be empty.", md_file.name)

    raw_slug = meta.get("slug", "")
    custom_slug = normalize_page_name(raw_slug)
    if raw_slug.strip() and not custom_slug:
        logger.warning("%s has an unusable slug %r (no paths or leading dots); using the generated URL.",
                       md_file.name, raw_slug)

    aliases = []
    for raw in frontmatter.as_list(meta.get("aliases", "")):
        alias = normalize_page_name(raw)
        if alias:
            aliases.append(alias)
        else:
            logger.warning("%s has an unusable alias %r; ignored.", md_file.name, raw)

    if not lock and "[CHECK" in body:
        logger.warning("%s is published but still contains a [CHECK ...] marker "
                       "(an unresolved fact-check note) — resolve it before deploying.", md_file.name)

    return Entry(
        path=md_file,
        collection_id=collection_id,
        layout=layout,
        title=title,
        file_slug=slugify(md_file.stem) or "entry",
        date=date,
        category=meta.get("category") or ("Uncategorized" if layout == LAYOUT_ESSAYS else ""),
        synopsis=synopsis,
        keywords=frontmatter.as_list(meta.get("keywords", "")),
        lock=lock,
        body=body,
        asterisk=meta.get("asterisk", ""),
        teaser=meta.get("teaser", ""),
        image=meta.get("image", ""),
        custom_slug=custom_slug,
        aliases=aliases,
        page_prefix=page_prefix,
    )


def _load_entries(folder: Path, cid: str, layout: str, prefix: str, descending: bool,
                  hide_after: Optional[date_cls]) -> Tuple[List[Entry], int, int]:
    """Return (published entries in display order, locked count, future-hidden count)."""
    parsed = [e for e in (parse_entry_file(f, cid, layout, prefix) for f in sorted(folder.glob("*.md")))
              if e is not None]
    locked = sum(1 for e in parsed if e.lock)
    entries = [e for e in parsed if not e.lock]

    hidden_future = 0
    if hide_after is not None:
        kept = []
        for e in entries:
            d = e.parsed_date
            if d is not None and d.date() > hide_after:
                hidden_future += 1
            else:
                kept.append(e)
        entries = kept

    entries.sort(key=_sort_key)
    for number, entry in enumerate(entries, start=1):
        entry.number = number
    if descending:
        entries.reverse()
    return entries, locked, hidden_future


# ----------------------------------------------------------------------
# Collections
# ----------------------------------------------------------------------

def _parse_show_on_home(value) -> Optional[int]:
    if value is None or value is False:
        return None
    if value is True:
        return 0
    try:
        n = int(value)
    except (TypeError, ValueError):
        logger.warning("show_on_home=%r is not a number; treating it as hidden.", value)
        return None
    return n if n >= 0 else None


def _check_keys(cfg: dict, where: str) -> None:
    for key in cfg:
        if key not in COLLECTION_KEYS:
            hint = difflib.get_close_matches(key, COLLECTION_KEYS, n=1)
            logger.warning("%s: unknown key %r%s", where, key, f" (did you mean {hint[0]!r}?)" if hint else "")


def load_collections(content_dir: Path, hide_after: Optional[date_cls]) -> List[Collection]:
    path = content_dir / "collections.json"
    if not path.exists():
        logger.warning("%s not found — nothing will be published.", path)
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"Cannot read {path}: {e}")

    defaults = {**_BUILTIN_DEFAULTS, **((data.get("defaults") or {}) if isinstance(data, dict) else {})}
    configs = data.get("collections", []) if isinstance(data, dict) else data
    _check_keys(defaults, "collections.json defaults")

    collections: List[Collection] = []
    used_ids, used_prefixes = set(), set()

    for position, cfg in enumerate(configs, start=1):
        title = (cfg.get("title") or "").strip()
        folder_name = (cfg.get("folder") or "").strip()
        where = f"collections.json #{position} ({title or folder_name or '?'})"
        _check_keys(cfg, where)

        def pick(key: str, default=""):
            value = cfg.get(key, defaults.get(key, default))
            return default if value is None else value

        if not title or not folder_name:
            logger.warning("collections.json #%d needs both \"title\" and \"folder\" — skipped.", position)
            continue
        if cfg.get("lock"):
            logger.info("Collection %r is locked; not published.", title)
            continue
        folder = content_dir / folder_name
        if not folder.is_dir():
            logger.warning("%s: folder %s does not exist — skipped.", where, folder)
            continue

        cid = (cfg.get("id") or folder_name).strip()
        if cid in used_ids:
            logger.warning("%s: id %r is used twice — skipped.", where, cid)
            continue
        used_ids.add(cid)

        layout = str(pick("layout", LAYOUT_CHAPTERS)).strip().lower()
        if layout not in (LAYOUT_ESSAYS, LAYOUT_CHAPTERS):
            logger.warning("%s: unknown layout %r; using %r.", where, layout, LAYOUT_CHAPTERS)
            layout = LAYOUT_CHAPTERS
        default_sort = "descending" if layout == LAYOUT_ESSAYS else "ascending"
        sort = str(pick("sort", default_sort)).strip().lower()
        if sort not in ("ascending", "descending"):
            logger.warning("%s: sort=%r (use ascending or descending); using %r.", where, sort, default_sort)
            sort = default_sort

        prefix = ""
        if layout == LAYOUT_CHAPTERS:
            prefix = (cfg.get("page_prefix") or f"book-{slugify(folder_name)}").strip()
            if prefix in used_prefixes:
                logger.warning("%s: page_prefix %r already used — skipped.", where, prefix)
                continue
            used_prefixes.add(prefix)

        entries, locked, future = _load_entries(folder, cid, layout, prefix, sort == "descending", hide_after)
        if not entries:
            logger.warning("%s has no published entries (%d locked, %d future-dated) — skipped.",
                           where, locked, future)
            continue

        coll = Collection(
            id=cid, title=title, folder=folder_name, layout=layout, sort=sort, page_prefix=prefix,
            entries=entries,
            show_on_home=_parse_show_on_home(cfg.get("show_on_home", defaults.get("show_on_home"))),
            synopsis=cfg.get("synopsis") or cfg.get("premise") or "",
            linked_book=(cfg.get("linked_book") or "").strip(),
            eyebrow=pick("eyebrow"), eyebrow_url=pick("eyebrow_url"), intro=pick("intro"),
            read_note=pick("read_note"), disclaimer=pick("disclaimer"),
            speakers=tuple(cfg.get("speakers", defaults.get("speakers", [])) or []),
            start_label=pick("start_label"), see_all_label=pick("see_all_label"),
            home_label=pick("home_label"), home_heading=pick("home_heading") or title,
        )
        collections.append(coll)
        logger.info("Loaded %r: %d published, %d locked, %d future-dated (sort=%s, show_on_home=%s)",
                    title, len(entries), locked, future, sort, coll.show_on_home)
    return collections


# ----------------------------------------------------------------------
# Standalone pages
# ----------------------------------------------------------------------

def load_pages(content_dir: Path) -> Dict[str, PageDoc]:
    pages: Dict[str, PageDoc] = {}
    folder = content_dir / "pages"
    if not folder.is_dir():
        return pages
    for md in sorted(folder.glob("*.md")):
        meta, body = frontmatter.parse(md.read_text(encoding="utf-8"))
        if frontmatter.as_bool(meta.get("lock", "")):
            continue
        key = slugify(md.stem) or md.stem
        url = normalize_page_name(meta.get("slug", "")) or f"{key}.html"
        title = meta.get("title") or md.stem.replace("-", " ").title()
        pages[key] = PageDoc(
            path=md, key=key, title=title, url=url,
            template=meta.get("template", "default") or "default",
            description=meta.get("description", ""),
            section=meta.get("section", key) or key,
            meta=meta, body=body,
        )
    return pages


# ----------------------------------------------------------------------
# JSON data sets
# ----------------------------------------------------------------------

def _build_books(raw: list, collections: List[Collection], images_dir: Path, downloads_dir: Path,
                 note_titles: set) -> List[Book]:
    by_book = {c.linked_book.strip().casefold(): c for c in collections if c.linked_book}
    books: List[Book] = []
    for item in raw:
        if not isinstance(item, dict) or not item.get("title"):
            logger.warning("books.json: an entry without a title was skipped.")
            continue
        title = item["title"].strip()

        image_url = ""
        if item.get("image"):
            if (images_dir / item["image"]).is_file():
                image_url = f"images/{item['image']}"
            else:
                logger.warning("books.json: cover image %r for %r not found in assets/images.", item["image"], title)

        actions: List[Action] = []
        coll = by_book.get(title.casefold())
        if coll:
            actions.append(Action("read", "Read Me", coll.url, False))
        link = (item.get("link") or "").strip()
        if link:
            if link.lower().startswith(("http://", "https://")):
                actions.append(Action("buy", item.get("linkDescription") or "Buy Me", link, True))
            else:
                rel = link[len("downloads/"):] if link.startswith("downloads/") else link
                if not (downloads_dir / rel).is_file():
                    logger.warning("books.json: download %r for %r not found in assets/downloads.", link, title)
                actions.append(Action("download", item.get("linkDescription") or "Download",
                                      quote(link, safe="/"), False))
        slug = slugify(title)
        books.append(Book(
            title=title, description=item.get("description", ""), author=item.get("author", ""),
            year=str(item.get("year", "") or ""), image_url=image_url, video_id=item.get("video_id", "") or "",
            link_label=item.get("linkDescription", ""), actions=actions,
            unavailable_label=(item.get("linkDescription") or "Not available") if not actions else "",
            anchor=f"book-{slug}",
            cross_link=f"#note-{slug}" if title.casefold() in note_titles else "",
        ))
    return books


def _build_notes(raw: list, book_titles: set) -> List[Note]:
    raw = sorted((n for n in raw if isinstance(n, dict) and n.get("title")),
                 key=lambda n: n.get("date", ""), reverse=True)
    notes = []
    for item in raw:
        title = item["title"].strip()
        slug = slugify(title)
        notes.append(Note(
            title=title, note=item.get("note", ""), author=item.get("author", ""),
            date=item.get("date", ""), link=item.get("link", ""), anchor=f"note-{slug}",
            cross_link=f"#book-{slug}" if title.casefold() in book_titles else "",
        ))
    return notes


def _build_thoughts(raw: list, newest_first: bool) -> List[Thought]:
    items = []
    for position, entry in enumerate(raw):
        if not isinstance(entry, dict):
            logger.warning("thoughts.json entry #%d is not an object; skipped.", position + 1)
            continue
        text = str(entry.get("text", "")).strip()
        date = str(entry.get("date", "")).strip()
        if not text:
            logger.warning("thoughts.json entry #%d has no text; skipped.", position + 1)
            continue
        try:
            parsed = datetime.fromisoformat(date) if date else None
        except ValueError:
            parsed = None
        if date and parsed is None:
            logger.warning("thoughts.json entry #%d has an unrecognised date %r (use YYYY-MM-DD).", position + 1, date)
        items.append((parsed or datetime.min, position, date, parsed, text))
    items.sort(key=lambda t: (t[0], t[1]))      # oldest -> newest; ties keep file order
    thoughts = [
        Thought(text=text, date=date, iso_date=date if parsed else "",
                date_display=f"{parsed:%B} {parsed.day}, {parsed.year}" if parsed else date)
        for _, _, date, parsed, text in items
    ]
    if newest_first:
        thoughts.reverse()
    return thoughts


def load_content(content_dir: Path, settings: dict, today: Optional[date_cls] = None,
                 hide_future: Optional[bool] = None) -> Content:
    """Load everything under content_dir. `hide_future` overrides publishing.hide_future_dated."""
    content_dir = Path(content_dir)
    today = today or date_cls.today()
    if hide_future is None:
        hide_future = bool(settings["publishing"]["hide_future_dated"])

    collections = load_collections(content_dir, today if hide_future else None)
    data_dir = content_dir / "data"
    assets = content_dir / "assets"

    raw_books = _read_json(data_dir / "books.json", list)
    raw_notes = _read_json(data_dir / "reading_notes.json", list)
    note_titles = {n.get("title", "").strip().casefold() for n in raw_notes if isinstance(n, dict)}
    book_titles = {b.get("title", "").strip().casefold() for b in raw_books if isinstance(b, dict)}

    books = _build_books(raw_books, collections, assets / "images", assets / "downloads", note_titles)
    notes = _build_notes(raw_notes, book_titles)

    known_titles = {b.title.casefold() for b in books}
    for c in collections:
        if c.linked_book and c.linked_book.casefold() not in known_titles:
            logger.warning("Collection %r has linked_book %r, but no book in books.json has that title.",
                           c.title, c.linked_book)

    videos = []
    for v in _read_json(data_dir / "videos.json", list):
        if isinstance(v, dict) and v.get("video_id"):
            videos.append(Video(title=v.get("title", "Untitled Video"), video_id=v["video_id"],
                                article_link=v.get("article_link", "")))

    blurbs = {name: (info or {}).get("description", "")
              for name, info in _read_json(data_dir / "categories.json", dict).items()
              if isinstance(info, dict)}

    essay_colls = [c for c in collections if c.layout == LAYOUT_ESSAYS]
    descending = essay_colls[0].descending if essay_colls else True
    essays = sorted((e for c in essay_colls for e in c.entries), key=_sort_key, reverse=descending)

    return Content(
        settings=settings, collections=collections, pages=load_pages(content_dir),
        books=books, notes=notes,
        thoughts=_build_thoughts(_read_json(data_dir / "thoughts.json", list),
                                 bool(settings["thoughts"]["newest_first"])),
        videos=videos, category_blurbs=blurbs, essays=essays, essays_descending=descending,
    )
