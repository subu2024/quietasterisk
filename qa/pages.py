"""
Page planning: turns Content into a list of PageSpec objects.

A PageSpec is pure data (output file, theme template, template context,
SEO fields). It contains no HTML and no theme knowledge beyond the template
names listed in docs/THEME_CONTRACT.md. Adding a page type means adding a
builder here and a template to the theme; nothing else changes.
"""

import copy
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .loaders import Content
from .models import LAYOUT_CHAPTERS, LAYOUT_ESSAYS, CategoryInfo, Collection, Entry, slugify

logger = logging.getLogger("qa")

HOME_FILE = "index.html"
ESSAYS_FILE = "essays.html"
CATEGORIES_FILE = "categories.html"
BOOKS_FILE = "books.html"
THOUGHTS_FILE = "thoughts.html"
VIDEOS_FILE = "videos.html"
FEED_FILE = "feed.xml"
NOT_FOUND_FILE = "404.html"
SITEMAP_FILE = "sitemap.xml"
ROBOTS_FILE = "robots.txt"


@dataclass
class PageSpec:
    url: str                          # output file, relative to the site root
    template: str                     # theme template
    context: dict                     # page-specific template variables
    title: str                        # short page title; "<title> - <site title>" is composed later
    description: str = ""
    section: str = ""                 # which nav item is highlighted
    og_type: str = "website"
    image: str = ""                   # file in assets/images used for social sharing
    jsonld: Optional[dict] = None
    noindex: bool = False
    lastmod: str = ""
    in_sitemap: bool = True


@dataclass
class Redirect:
    url: str
    target: str


@dataclass
class Plan:
    pages: List[PageSpec] = field(default_factory=list)
    redirects: List[Redirect] = field(default_factory=list)
    urls: Dict[str, str] = field(default_factory=dict)
    site: dict = field(default_factory=dict)
    feed_entries: List[Entry] = field(default_factory=list)


def _group_by_category(essays: List[Entry], blurbs: Dict[str, str], default_blurb: str) -> List[CategoryInfo]:
    groups: Dict[str, List[Entry]] = defaultdict(list)
    for e in essays:
        groups[e.category].append(e)
    return [CategoryInfo(name=name, slug=slugify(name),
                         description=blurbs.get(name) or default_blurb.format(name=name.lower()),
                         entries=groups[name])
            for name in sorted(groups)]


def _fmt(copy_block: dict, **values) -> dict:
    """Fill {placeholders} in a copy block's strings; unknown placeholders are left as written."""
    class _Safe(dict):
        def __missing__(self, key):
            return "{" + key + "}"
    out = {}
    for k, v in copy_block.items():
        out[k] = v.format_map(_Safe(values)) if isinstance(v, str) else v
    return out


def plan_site(content: Content) -> Plan:
    s = content.settings
    plan = Plan()
    copy_all = s["copy"]

    # ---- which pages exist -> the `urls` map every template uses -------------
    urls: Dict[str, str] = {"home": HOME_FILE}
    if content.essays:
        urls["essays"] = ESSAYS_FILE
        urls["categories"] = CATEGORIES_FILE
        urls["feed"] = FEED_FILE
    if content.books or content.notes:
        urls["books"] = BOOKS_FILE
    if content.thoughts:
        urls["thoughts"] = THOUGHTS_FILE
    if content.videos:
        urls["videos"] = VIDEOS_FILE
    for key, doc in content.pages.items():
        urls[key] = doc.url
    for coll in content.collections:
        urls[coll.id] = coll.url
    plan.urls = urls

    # ---- site-wide context ---------------------------------------------------
    def resolve(items):
        out = []
        for item in items:
            href = item.get("url") or urls.get(item.get("page", ""))
            if href:
                out.append({"label": item["label"], "href": href, "page": item.get("page", "")})
        return out

    newsletter = dict(s["newsletter"])
    newsletter["active"] = bool(newsletter.get("enabled") and newsletter.get("endpoint"))
    if newsletter.get("enabled") and not newsletter.get("endpoint"):
        logger.warning("newsletter.enabled is true but no endpoint is set (site.json newsletter.endpoint or env "
                       "BLOG_NEWSLETTER_API_ENDPOINT); the signup box is hidden.")

    site = {
        "title": s["title"], "tagline": s["tagline"], "url": s["url"], "language": s["language"],
        "author": s["author"], "email": s["email"], "copyright": s["copyright"],
        "logo_url": f"images/{s['logo']}" if s["logo"] else "",
        "analytics_id": s["analytics_id"], "social": s["social"],
        "nav": resolve(s["nav"]), "footer_nav": resolve(s["footer_nav"]),
        "newsletter": newsletter, "feed_url": urls.get("feed", ""),
        "home": s["home"], "thoughts": s["thoughts"],
    }
    plan.site = site

    def add(spec: PageSpec) -> PageSpec:
        plan.pages.append(spec)
        return spec

    # ---- home ----------------------------------------------------------------
    latest = None
    if content.thoughts:
        latest = content.thoughts[0] if s["thoughts"]["newest_first"] else content.thoughts[-1]
    thought_block = None
    if latest and "thoughts" in urls:
        thought_block = {"kind": "thought", "id": "daily-thought", "heading": s["thoughts"]["home_heading"],
                         "thought": latest, "link_label": s["thoughts"]["home_link_label"],
                         "link_url": urls["thoughts"]}
    blocks, placed = [], False
    for coll in content.collections:
        if coll.show_on_home is None:
            continue
        blocks.append({
            "kind": "card" if coll.show_on_home == 0 else "list",
            "id": coll.id, "collection": coll, "title": coll.title, "heading": coll.home_heading,
            "synopsis": coll.synopsis, "eyebrow": coll.eyebrow, "entries": coll.home_entries,
            "see_all_label": coll.see_all_label or "See all", "see_all_url": coll.url,
        })
        if thought_block and coll.id == s["home"]["thought_after"]:
            blocks.append(thought_block)
            placed = True
    if thought_block and not placed:
        blocks.append(thought_block)

    add(PageSpec(
        url=HOME_FILE, template="home.html", title="Home", description=s["tagline"], section="home",
        jsonld={"@context": "https://schema.org", "@type": "WebSite", "name": s["title"],
                "url": s["url"] + "/", "description": s["tagline"]},
        context={"hero": {"title": s["home"]["hero_title"], "subtitle": s["tagline"]}, "blocks": blocks},
    ))

    # ---- entry pages and chapter lists ---------------------------------------
    books_by_title = {b.title.casefold(): b for b in content.books}
    for coll in content.collections:
        if coll.layout == LAYOUT_CHAPTERS:
            book = books_by_title.get(coll.linked_book.casefold()) if coll.linked_book else None
            description = coll.intro or coll.synopsis or (book.description if book else "")
            add(PageSpec(
                url=coll.url, template="collection.html", title=coll.title, description=description,
                section=coll.id, lastmod=max((e.date for e in coll.entries if e.iso_date), default=""),
                context={"collection": coll, "entries": coll.entries, "start_entry": coll.start_entry,
                         "description": description, "book": book,
                         "book_actions": [a for a in book.actions if a.kind != "read"] if book else []},
            ))
        for index, entry in enumerate(coll.entries):
            is_essay = coll.layout == LAYOUT_ESSAYS
            ld = {"@context": "https://schema.org", "@type": "BlogPosting" if is_essay else "Article",
                  "headline": entry.title, "description": entry.synopsis,
                  "author": {"@type": "Person", "name": s["author"]} if s["author"] else None,
                  "datePublished": entry.iso_date or None,
                  "mainEntityOfPage": f"{s['url']}/{entry.url}",
                  "isPartOf": None if is_essay else {"@type": "Book", "name": coll.title, "url": f"{s['url']}/{coll.url}"}}
            ld = {k: v for k, v in ld.items() if v not in (None, "")}
            add(PageSpec(
                url=entry.url, template="entry.html",
                title=entry.title if is_essay else f"{entry.title} - {coll.title}",
                description=entry.synopsis, section="essays" if is_essay else "reading",
                og_type="article", image=entry.image, jsonld=ld, lastmod=entry.iso_date,
                context={"entry": entry, "collection": coll,
                         "prev": coll.entries[index - 1] if index > 0 else None,
                         "next": coll.entries[index + 1] if index < len(coll.entries) - 1 else None,
                         "related": [],   # replaced by the build for essays
                         "position": {"number": entry.number, "total": len(coll.entries)}},
            ))
            for alias in entry.aliases:
                plan.redirects.append(Redirect(alias, entry.url))

    # ---- essays, categories, feed -------------------------------------------
    if content.essays:
        years: Dict[int, List[Entry]] = defaultdict(list)
        for e in content.essays:
            if e.year:
                years[e.year].append(e)
        year_list = [{"year": y, "entries": years[y], "count": len(years[y])}
                     for y in sorted(years, reverse=content.essays_descending)]
        cats = _group_by_category(content.essays, content.category_blurbs,
                                  copy_all["category"]["default_description"])
        stats = {"count": len(content.essays), "years": len(year_list), "categories": len(cats)}
        preview = int(s["publishing"]["group_preview_count"])

        add(PageSpec(
            url=ESSAYS_FILE, template="essays.html", title="Essays", section="essays",
            description=_fmt(copy_all["essays"], **stats)["description"],
            context={"years": year_list, "categories": cats, "stats": stats, "preview_count": preview,
                     "copy": _fmt(copy_all["essays"], **stats)},
        ))
        add(PageSpec(
            url=CATEGORIES_FILE, template="categories.html", title="Categories", section="essays",
            description=copy_all["categories"]["description"],
            context={"categories": cats, "copy": copy_all["categories"]},
        ))
        for cat in cats:
            add(PageSpec(
                url=cat.url, template="category.html", title=cat.name, section="essays",
                description=cat.description,
                context={"category": cat, "preview_count": preview, "copy": copy_all["category"]},
            ))
        plan.feed_entries = content.essays[: int(s["publishing"]["feed_items"])]
        if not content.essays_descending:      # a feed is always newest first
            plan.feed_entries = sorted(content.essays, key=lambda e: e.date, reverse=True)[: int(s["publishing"]["feed_items"])]

    # ---- books, thoughts, videos ---------------------------------------------
    if "books" in urls:
        add(PageSpec(url=BOOKS_FILE, template="books.html", title="Books", section="books",
                     description=copy_all["books"]["description"],
                     context={"books": content.books, "notes": content.notes, "copy": copy_all["books"]}))
    if "thoughts" in urls:
        add(PageSpec(url=THOUGHTS_FILE, template="thoughts.html", title=s["thoughts"]["page_label"],
                     section="thoughts", description=s["thoughts"]["page_intro"],
                     context={"thoughts": content.thoughts, "copy": s["thoughts"]}))
    if "videos" in urls:
        add(PageSpec(url=VIDEOS_FILE, template="videos.html", title="Videos", section="videos",
                     description=copy_all["videos"]["description"],
                     context={"videos": content.videos, "copy": copy_all["videos"]}))

    # ---- standalone markdown pages -------------------------------------------
    for key, doc in content.pages.items():
        add(PageSpec(url=doc.url, template=f"page_{doc.template}.html", title=doc.title,
                     description=doc.description, section=doc.section,
                     context={"doc": doc, "copy": copy_all.get(key, {})}))

    # ---- redirects from site.json --------------------------------------------
    for old, new in s["redirects"].items():
        plan.redirects.append(Redirect(old, new))

    return plan
