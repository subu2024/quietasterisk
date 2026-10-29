# quiet asterisk: site generator, version 2

A static-site generator with a hard line between **content** and **presentation**.

| Layer | Folder | You edit it to... |
|---|---|---|
| Content | `content/` | write essays, books, series, poems; change site text and settings |
| Presentation | `themes/<name>/` | change how the site looks (Jinja2 templates, CSS, JS) |
| Engine | `qa/` | almost never; it turns content into data and hands it to the theme |

Swap the whole look of the site without touching a single essay:

```bash
python build.py --theme minimal        # the same content, a completely different design
```

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python build.py --serve                # build into dist/ and preview at http://localhost:8000
python build.py --strict               # what CI runs: any warning fails the build
python -m pytest                       # tests
```

Set these when building for production (they are not stored in the repo):

```bash
export BLOG_NEWSLETTER_API_ENDPOINT="https://xxxx.lambda-url.us-east-1.on.aws/"   # see handler.py
export BLOG_SITE_URL="https://www.quietasterisk.com"                                # optional, default is in site.json
```

## Moving from version 1

```bash
python tools/migrate_v1_to_v2.py --from ../old-project --to . --dry-run
python tools/migrate_v1_to_v2.py --from ../old-project --to .
```

It copies (never deletes) your essays, chapters, JSON data, images and downloads into `content/`, converts front matter
(`excerpt` to `synopsis`, `archived` to `lock`), and lists anything locked. Then add the Essays synopsis to
`content/collections.json` and run `python build.py --strict`. The newsletter Lambda (`handler.py`) is unchanged.

## What changed from version 1

| Area | v1 | v2 |
|---|---|---|
| HTML | f-strings in 5 Python files | Jinja2 templates in a swappable theme |
| CSS | a 1,100-line Python string inlined in every page | `static/css/style.css`, linked, cache-busted by content hash |
| Site text | constants in `config.py` and strings in generators | `content/site.json` and `content/pages/*.md` (About, Contact are markdown) |
| Inline styles and `onclick` | everywhere | CSS classes and `data-*` attributes |
| Escaping | manual `escape()` (some missed) | automatic |
| Build output | wiped first | built aside, swapped in only on success |
| Warnings | log lines | `--strict` fails the build; includes a broken-link and missing-asset check |
| SEO | title only | description, canonical, Open Graph, JSON-LD, RSS feed, robots.txt, sitemap with lastmod |
| Old URLs | two hard-coded redirects | `aliases:` per entry and `redirects` in `site.json` |
| Scheduling | none | `--hide-future` / `publishing.hide_future_dated` |
| Tests | none | 33 tests, including one that fails if the engine ever emits page markup |

Removed because nothing used them: the AI chat widget stub, `format_featured_card`, `format_book_action_row`,
`topic_chips_html`, the `is_small` card flag and their CSS.

## Where things are documented

* `docs/CONTENT_GUIDE.md`: front matter, `collections.json`, `site.json`, data files, everyday tasks
* `docs/ARCHITECTURE.md`: the build flow, module responsibilities, behavioural rules
* `docs/THEME_CONTRACT.md`: every template and variable, for writing a new theme

## Project layout

```
build.py                 entry point
qa/                      engine (settings, loaders, models, pages, theme, build...)
content/                 site.json, collections.json, essays/, series folders, pages/, data/, assets/
themes/quiet/            the current design        themes/minimal/   the smallest valid theme
tests/                   pytest suite + fixture site
tools/                   migrate_v1_to_v2.py
handler.py               newsletter signup Lambda (deploys separately)
.github/workflows/       CI: tests, strict build, upload dist/
```
