# Architecture and build flow

## The one rule

> **Content and engine know nothing about HTML. Themes know nothing about files, sorting or publishing rules.**

```
 content/ (what you write)          qa/ (engine)                       themes/<name>/ (what visitors see)
 ─────────────────────────          ───────────────────────────        ─────────────────────────────────
 site.json                          settings.py                         theme.json
 collections.json         ──►       loaders.py  ──►  models.py          templates/*.html
 essays/*.md, series/*.md           pages.py    (plan: PageSpec data)   static/css, js
 pages/*.md                         render_md.py ──── calls ──────►     macros.html  (youtube, dialogue)
 data/*.json                        theme.py     ──── renders ─────►    every template
 assets/images, downloads           build.py → dist/
```

`tests/test_theme_contract.py` enforces the rule: it fails if `qa/*.py` ever contains page markup.

## Modules

| Module | Job |
|---|---|
| `build.py` (root) / `qa/cli.py` | Command line: flags, `--serve`, exit codes |
| `qa/settings.py` | `content/site.json` over `qa/default_site.json`, environment overrides, typo warnings |
| `qa/frontmatter.py` | The single front-matter parser |
| `qa/models.py` | Data classes (`Entry`, `Collection`, `Book`...): also the theme's data contract |
| `qa/loaders.py` | Reads `content/` into models: collections, entries, pages, books, notes, thoughts, videos |
| `qa/pages.py` | Plans the site: which pages exist, their template and context (`PageSpec`), URL map, redirects |
| `qa/render_md.py` | Markdown to HTML; calls the theme's `youtube` and `dialogue` macros |
| `qa/related.py` | TF-IDF related essays |
| `qa/theme.py` | Loads a theme, validates it against the contract, renders templates |
| `qa/assets.py` | Copies images, downloads and theme static files (with cache-busting hashes) |
| `qa/system_templates/` | Engine-owned machine formats: sitemap, RSS feed, robots.txt, redirect pages |
| `qa/build.py` | Orchestrates everything; atomic swap; strict mode; link check |

## Build flow

```
python build.py [--theme X] [--strict] [--hide-future] [--serve]
 │
 1. load_settings()            site.json + defaults + env (BLOG_SITE_URL, BLOG_NEWSLETTER_API_ENDPOINT)
 2. Theme(themes/<name>)       validate theme.json contract and required templates
 3. load_content()
 │    ├─ collections.json → for each collection: read *.md → parse front matter
 │    │     drop lock:true (and archived:true)           ← never published anywhere
 │    │     drop future-dated if hide_future_dated
 │    │     sort by (date, natural filename); number 1..N; reverse if sort = descending
 │    │     skip a collection with nothing left to publish
 │    ├─ pages/*.md, data/*.json → models (books get actions + cross-links; thoughts sorted)
 │    └─ pool essay-layout entries for the Essays page, categories, related, feed
 4. copy assets                images → dist/images, downloads → dist/downloads, theme static → dist/static
 5. plan_site()                PageSpec list + urls map + redirects (pure data, no HTML)
 6. render markdown bodies     entry.body_html / doc.body_html (theme macros for youtube, dialogue)
 7. related essays             TF-IDF over essay bodies
 8. render every PageSpec      theme template + {site, urls, page, **page context}
 9. system files               sitemap.xml, feed.xml, robots.txt, redirect pages (aliases + site.json redirects)
10. checks                     URL clashes, redirect targets, broken internal links and assets
11. swap                       dist.building → dist (skipped if --strict and any warning)
```

Everything is built into `dist.building/` first. If anything raises, or `--strict` finds a warning, the existing `dist/` is left untouched.

## Pages produced

| Output | Template | When |
|---|---|---|
| `index.html` | `home.html` | always |
| `<entry.url>` | `entry.html` | one per published entry |
| `<prefix>.html` | `collection.html` | one per `chapters` collection |
| `essays.html`, `categories.html`, `category-<slug>.html` | `essays`, `categories`, `category` | when essays exist |
| `books.html` | `books.html` | when books or reading notes exist |
| `thoughts.html`, `videos.html` | `thoughts`, `videos` | when data exists |
| `about.html`, `contact.html`, ... | `page_<template>.html` | one per `content/pages/*.md` |
| `404.html` | `404.html` | if the theme provides it |
| `sitemap.xml`, `feed.xml`, `robots.txt` | engine | always (feed only with essays) |
| redirect pages | engine | `aliases:` in front matter and `redirects` in `site.json` |

## Behavioural rules

- **lock** hides an entry everywhere: page, lists, home, sitemap, feed, related.
- **Numbers** are assigned after locking, in ascending reading order, and never change when a list is displayed descending.
- **sort** drives every list of that collection and prev/next. Essays default to descending, chapters to ascending.
- **show_on_home**: absent/`false` hidden; `0` synopsis and "read all"; `N` synopsis, top N, "read all".
- **URLs** never change for existing content: `slug:` wins, then `<prefix>-<file>.html` for chapters, then the title for essays.
- **Future-dated** entries publish unless `publishing.hide_future_dated` or `--hide-future` is set.
- **Warnings** are collected; `--strict` turns them into a failed build (use it in CI).

## Extension points

| I want to... | Change |
|---|---|
| Redesign the site | Add a theme folder (see `THEME_CONTRACT.md`) |
| Add a series, book or blog | Add a folder under `content/` and an entry in `collections.json` |
| Add a standalone page | Add `content/pages/<name>.md` (and `page_<template>.html` in the theme if it needs a special layout) |
| Add a new kind of page | Add a builder in `qa/pages.py` and a template to every theme (add it to `REQUIRED_TEMPLATES`) |
| Change site text | `content/site.json` |
