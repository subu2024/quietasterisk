# Theme contract (version 2)

A **theme** is everything a visitor sees: HTML templates, CSS, JavaScript, fonts, icons.
The **engine** (`qa/`) never writes page markup; it hands each theme template plain data.
To redesign the site, write a new theme folder and run `python build.py --theme <name>`.
Content (`content/`) and engine are untouched.

```
themes/<name>/
  theme.json        {"name": "...", "version": "...", "contract": 2}
  templates/        Jinja2 templates (below)
  static/           copied to dist/static/ (css, js, fonts, images)
```

`theme.json` must declare `"contract": 2`. A theme for another contract version is rejected with a clear error.
`themes/minimal/` is the smallest valid theme (about 60 lines of templates). Copy it to start.

## Rules for themes

1. Templates are Jinja2 with **autoescape on**. Never use `|safe` except on `entry.body_html` and `doc.body_html` (already-rendered markdown).
2. No Python, no network access at build time. Everything a template needs arrives in its context.
3. Pages are **flat files in one folder**. Always link with the values the engine provides (`urls.*`, `entry.url`, `collection.url`, ...), never hard-coded file names.
4. Load assets with `{{ static('css/style.css') }}`. It adds a cache-busting hash.
5. Do not reference variables that are not in this document. The engine's `--strict` mode makes undefined variables an error.
6. Prefer classes over inline `style=""`; prefer `data-*` attributes over inline `onclick=""`.

## Templates

### Required (the engine refuses to build without all of them)

| Template | Page | Written to |
|---|---|---|
| `base.html` | Layout every other template extends (not rendered alone) | n/a |
| `macros.html` | Macros the engine calls (see "Engine hooks") | n/a |
| `home.html` | Homepage | `index.html` |
| `entry.html` | One essay or one chapter/poem | `<entry.url>` |
| `collection.html` | Chapter list of a `chapters` collection | `<collection.url>` |
| `essays.html` | All essays, grouped by year and by category | `essays.html` |
| `categories.html` | List of categories | `categories.html` |
| `category.html` | One category | `category-<slug>.html` |
| `books.html` | Books and reading notes | `books.html` |
| `thoughts.html` | Daily thoughts feed | `thoughts.html` |
| `videos.html` | Video library | `videos.html` |
| `page_default.html` | Fallback for markdown pages | `<doc.url>` |

### Optional

| Template | Used when |
|---|---|
| `page_<name>.html` | A page in `content/pages/` has `template: <name>` (e.g. `page_letter.html`, `page_contact.html`). Falls back to `page_default.html`. |
| `404.html` | If present, written to `404.html` (not indexed, not in the sitemap). |

`books.html`, `thoughts.html`, `videos.html`, `essays.html` and the category pages are only generated when there is something to show.

## Variables available in every template

### `site` (from `content/site.json`)

`title`, `tagline`, `url`, `language`, `author`, `email`, `copyright`, `logo_url` (`""` if none),
`analytics_id` (`""` if none), `social` (list of `{label, icon, url}`),
`nav` and `footer_nav` (lists of `{label, href, page}`; items whose page does not exist are already removed),
`feed_url` (`""` if no feed), `home`, `thoughts`,
`newsletter` (`{active, endpoint, heading, subhead, button_label, fine_print, success_message, error_message}`; render the signup form only if `newsletter.active`).

### `urls`

Map of page key to file name: `home`, `essays`, `categories`, `books`, `thoughts`, `videos`, `feed`
(only keys that exist), plus one key per markdown page (`about`, `contact`, ...) and per collection id (`sunday_odds`, ...).

### `page` (SEO and navigation)

`title` (full `<title>` text), `heading` (short title), `description`, `canonical`, `og_type`,
`image_url` (`""` if none), `section` (compare with `item.page` to highlight the current nav item),
`noindex`, `jsonld_json` (JSON string; print with `|safe` inside `<script type="application/ld+json">`), `url`.

### `static(path)`

Function returning the URL of a file in the theme's `static/` folder.

## Per-template variables

| Template | Variables |
|---|---|
| `home.html` | `hero` (`{title, subtitle}`), `blocks` (ordered list, see below) |
| `entry.html` | `entry`, `collection`, `prev`, `next` (entries or `None`, in the collection's display order), `related` (essays only; list of entries), `position` (`{number, total}`) |
| `collection.html` | `collection`, `entries`, `start_entry`, `description`, `book` (`Book` or `None`), `book_actions` (list of `Action`, excluding "read") |
| `essays.html` | `years` (list of `{year, entries, count}`), `categories` (list of `CategoryInfo`), `stats` (`{count, years, categories}`), `preview_count`, `copy` |
| `categories.html` | `categories`, `copy` |
| `category.html` | `category` (`CategoryInfo`), `preview_count`, `copy` |
| `books.html` | `books` (list of `Book`), `notes` (list of `Note`), `copy` |
| `thoughts.html` | `thoughts` (list of `Thought`, display order), `copy` |
| `videos.html` | `videos` (list of `Video`), `copy` |
| `page_*.html` | `doc` (`PageDoc`), `copy` (settings `copy.<page key>`, or `{}`) |
| `404.html` | none |

`copy` holds the page's text from `site.json` (never hard-code wording in a theme):

| Page | Keys |
|---|---|
| essays | `eyebrow, title, accent, description, tab_year, tab_category` |
| categories | `title, description` |
| category | `back_label, default_description` |
| books | `eyebrow, title, description, my_books_heading, my_books_pill, notes_heading, notes_pill, notes_intro, affiliate_disclosure, cross_link_to_book, cross_link_to_note` |
| videos | `eyebrow, title, accent, description` |
| thoughts | `page_label, page_title, page_intro, home_heading, home_link_label, newest_first` |

### Homepage `blocks`

Each block is a dict with a `kind`:

| kind | Fields |
|---|---|
| `card` (collection with `show_on_home: 0`) | `id, collection, title, synopsis, eyebrow, see_all_label, see_all_url` |
| `list` (collection with `show_on_home: N`) | the same, plus `heading` and `entries` (the top N) |
| `thought` | `id, heading, thought, link_label, link_url` |

Render them in order; the engine already placed the daily thought where `site.json` asks.

## Objects

**Entry**: `title, url, layout ("essays"|"chapters"), collection_id, date, iso_date, date_display ("October 2026"), year, category, category_slug, category_hash, synopsis, keywords, body_html, asterisk, teaser, reading_minutes, number, image, aliases`.
`category_hash` is a stable integer, so a theme can cycle accent colours (`colors[entry.category_hash % 4]`).

**Collection**: `id, title, layout, sort, descending, url, synopsis, eyebrow, eyebrow_url, intro, read_note, disclaimer, speakers, start_label, see_all_label, home_label, home_heading, show_on_home, linked_book, entries, start_entry, home_entries`.

**CategoryInfo**: `name, slug, description, entries, count, url`.
**PageDoc**: `key, title, url, template, description, section, meta (every front-matter key), body_html`.
**Book**: `title, description, author, year, image_url, video_id, link_label, actions, unavailable_label, anchor, cross_link`.
**Action**: `kind ("read"|"buy"|"download"), label, href, external`.
**Note**: `title, note, author, date, link, anchor, cross_link`.
**Thought**: `text, date, iso_date, date_display`.
**Video**: `title, video_id, article_link`.

## Engine hooks (macros in `macros.html`)

The engine calls these while rendering markdown, because markdown cannot express them. Both are required.

| Macro | Called for |
|---|---|
| `youtube(video_id, title)` | A `[youtube:VIDEO_ID]` tag in markdown |
| `dialogue(speaker, index, html)` | A paragraph starting `**Name:**` in a collection that lists `speakers`; `index` is the speaker's position (0, 1, ...) |

## Creating a new theme

1. `cp -r themes/minimal themes/mytheme` and edit `theme.json`'s `name`.
2. Restyle the templates and `static/`.
3. `python build.py --theme mytheme --strict --serve`.
4. Set `"theme": "mytheme"` in `content/site.json` when you are happy.
