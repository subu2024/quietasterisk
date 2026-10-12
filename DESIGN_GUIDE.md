# Quiet Asterisk Design Guide

This documents the design system as it's actually implemented in the code,
so it stays trustworthy. Every pattern below maps to a real CSS class in
`styles.py` or a real Python helper — if you add a new visual pattern,
add it here in the same form (class/function name → what it does → where
it's used), not as aspirational description.

---

## Design Philosophy

Modern literary editorial: warm earth tones, premium serif/sans pairing,
generous spacing, restrained glassmorphism for a few key moments (hero
stats, pill badges), content-first hierarchy. Every page — home, category,
book, archive — should feel like the same publication, built from the
same handful of components.

---

## Site Structure

Three items in the main nav, plus the logo (home):

| Nav item | Page | Notes |
| -------- | ---- | ----- |
| Series   | `series.html` | Chapter list of the non-fiction series; chapters are `series-<slug>.html`. Hidden if the series has no chapters. |
| Essays   | `essays.html` | Every essay, toggle **By year / By category**. This is the former Archives page. |
| About    | `about.html` | |

- **Renames/redirects:** `archives.html` is now only a redirect to `essays.html` (it forwards `#fragments`). `reading.html` still redirects to the Books page.
- **Not in the nav, still published:** `books.html`, `videos.html`, `categories.html`, `category-<slug>.html`, `contact.html`. The footer links to Books ("Also by the author"), Contact, Series, Essays and About.
- **Homepage** (`generators.generate_index`): hero → Series feature → 3 recent essays → newsletter. Nothing else. Recent essays are simply the newest `HOME_ESSAYS_COUNT` posts; the `featured` front-matter flag is no longer used there.
- `header_html(title, active_page)` highlights only `"series"`, `"essays"` or `"about"`. Essay posts, the Essays page and category pages all pass `"essays"`.

---

## Color Palette

```css
--color-cream: #faf8f3 /* Main background */ --color-sand: #e8e3d8
  /* Borders, dividers */ --color-charcoal: #2b2826 /* Primary text */
  --color-slate: #5a5450 /* Secondary/muted text */ --color-rust: #b8503e
  /* Primary accent, CTAs, links */ --color-terracotta: #d17458
  /* Rust gradient partner */ --color-sage: #8b9b7e /* Secondary accent */
  --color-gold: #c9a767 /* Tertiary accent, books */;
```

### Category accent system

Every category gets one of four accent colors — **rust, sage, gold,
terracotta** — assigned deterministically by `utils.category_accent(category)`
(a stable hash of the category name). This is what makes card grids with
mixed categories scannable instead of monochrome. Never hardcode a
category's color; always go through this function so the same category
looks the same everywhere.

Used by:

- `cards._category_badge()` → renders `.card-category .card-category-{accent}` pill
- `cards._accent_border()` → renders a matching 4px top border on the card

Don't invent a 5th accent color without also adding its `.card-category-*`
and `.stat-card-glass.accent-*` CSS variants — see below.

---

## Typography

```css
--font-serif:
  "Crimson Pro",
  serif /* Headings, article body, card titles */ --font-sans: "Work Sans",
  sans-serif /* Nav, buttons, labels, metadata, pills */;
```

> **Out of date:** the live fonts are set in `config.py` (`FONT_SERIF` = Fraunces,
> `FONT_SANS` = Inter, with `GOOGLE_FONTS_URL`), and the palette above has been
> replaced by the paper/ink tokens at the top of `styles.py` (`--color-cream:
> #EDE9E1`, `--color-rust: #A5732E`, ...). Treat `styles.py` and `config.py` as
> the source of truth until this section is rewritten.

Both are loaded via the `@import` at the top of `get_modern_styles()` in
`styles.py`. **If you ever change these variables, update the `@import`
URL to match** — they drifted out of sync once already (the import was
loading Merriweather/Lato while every variable pointed to Crimson
Pro/Work Sans, so the whole site silently fell back to system fonts).

### Type scale

| Use                     | Size                                                |
| ----------------------- | --------------------------------------------------- |
| Homepage hero title     | `clamp(3rem, 6vw, 5rem)` (`.hero-title`)            |
| Section title           | `clamp(2.5rem, 5vw, 3.75rem)` (`.section-title`)    |
| Card title              | 1.875rem (`.card-title`), 3rem in `.card-featured`  |
| Body / excerpt          | 1rem–1.125rem                                       |
| Labels, metadata, pills | 0.75–0.875rem, uppercase, letter-spacing 0.1–0.15em |

### Weights

400 body · 500 emphasis/labels · 600 subheadings/pills · 700 headings · 800 hero numbers/gradient titles

---

## Core Components

Reuse these. Don't hand-roll a new card, badge, or embed with inline
styles — every time that happened previously it drifted from the rest
of the site (see git history / prior review notes).

### Cards — `cards.py`

| Function                                              | Used for                                                                                                            |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `format_card(post, is_small=False)`                   | Standard post card. `is_small=True` → `.card-compact` (tighter padding, clamped 2-line excerpt) for dense sidebars. |
| `format_featured_card(post)`                          | Large hero card, spans 2 grid rows (`.card-featured`).                                                              |
| `format_book_card(book, show_full_description=False)` | Book card with cover thumbnail, author/year, optional YouTube embed, buy button.                                    |
| `format_reading_note_card(note)`                      | Compact book-log entry.                                                                                             |
| `format_book_action_row(book)`                        | Compact book row with Read Me / Download / Buy buttons. Not used on the homepage any more; kept for reuse.         |
| `format_essay_row(post)`                              | Plain list row (meta line, title, excerpt, whole row is a link) for the homepage "Recent essays" (`.qa-essay*`). The one non-card. |

All four escape user/JSON-authored text automatically (`html.escape`) — don't
re-escape or bypass them by writing markup manually.

Every card gets:

- A colored category pill (`_category_badge`)
- A matching colored top border (`_accent_border`)

Grid containers: `.card-grid` (uniform cards), `.featured-grid` (1 large +
stacked smalls, see homepage), `.books-grid`.

### Pill badges — `templates.pill_badge(text, accent="rust")`

```python
pill_badge("Curated Reading", "rust")
# -> <span class="pill-badge pill-badge-rust">Curated Reading</span>
```

Accents: `rust`, `sage`, `gold` (`.pill-badge-rust/sage/gold` in styles.py).
Used as the small uppercase eyebrow above section titles and in the hero.

### Glass stat cards — `.stat-card-glass.accent-{rust,sage,gold}`

Real glassmorphism (`backdrop-filter: blur(10px)`, translucent white,
16px radius, lift-on-hover) with a gradient-text `.stat-number`. Used in
the homepage hero (`.hero-stats` grid). This is the _one_ place true
glass panels appear — keep it that way; overusing glassmorphism dilutes it.

```html
<div class="hero-stats">
  <div class="stat-card-glass accent-rust">
    <div class="stat-number">42+</div>
    <div class="stat-label">Essays Published</div>
  </div>
</div>
```

### YouTube embeds — `utils.youtube_embed(video_id, title, css_class="youtube-embed")`

One implementation, used everywhere a video appears (post bodies via
`parser.process_youtube_embeds`, book cards, the videos page, the
homepage featured-video section). Never paste the iframe markup by hand.

### Poems / verse

Default markdown collapses single newlines inside a paragraph — a poem
typed as consecutive lines in the `.md` source renders as one run-on
line, since both markdown and HTML ignore bare line breaks. Two ways to
fix that exist (trailing double-space, or the `nl2br` extension); both
are rejected here — see below.

**Convention: wrap poems in a raw HTML block with an explicit `.poem` class.**

```html
<div class="poem">
  <p>
    Roses are red<br />
    Violets are blue
  </p>

  <p>
    Sugar is sweet<br />
    And so are you
  </p>
</div>
```

Python-Markdown passes block-level raw HTML through untouched, so this
renders exactly as written — one `<p>` per stanza (blank line = stanza
break), `<br>` for a line break within a stanza. Styled by
`.post-body .poem` in `styles.py`: italic, tighter line-height, a
neutral sand rule on the left — deliberately _not_ the rust
`blockquote` style, which is reserved for pull-quotes/attributions, so
a poem never reads as something being quoted from elsewhere.

Why not the alternatives:

- **Trailing double-space for a line break** — technically valid
  markdown, but the whitespace is invisible in an editor, and most
  editors/git hooks strip trailing whitespace on save, silently
  breaking the poem.
- **The `nl2br` extension** — would fix poems, but it changes markdown
  parsing globally: every single newline in every post becomes a
  `<br>`, including ordinary hard-wrapped prose paragraphs. Too blunt
  for a site-wide setting.
- **Fenced code block** — preserves line breaks correctly but renders
  in a monospace/code font, which reads wrong for verse.

### Book chapters — `chapters.py`, `generators.generate_book_chapter_pages()`

A book in `books.json` becomes readable online when `config.BOOK_CHAPTER_FOLDERS`
maps its title (exactly as written in the JSON) to a folder under
`config.BOOK_CHAPTERS_DIR`. One markdown file per chapter, ordered by filename
(natural sort, so `2-x.md` precedes `10-x.md`). Front matter:

```
---
title: Chapter title
synopsis: One line.
keywords: a, b, c
lock: false        # true/yes/1 = locked
---
```

Pages generated (flat, in the output root):

- `book-<folder>.html` — chapter list (`.chapter-list`, `.chapter-item`), each with its synopsis and a `.chapter-lock-badge` if locked. This is the target of the **Home** button.
- `book-<folder>-<file-slug>.html` — one page per chapter, reusing `.post-content` / `.post-header` / `.post-body`, plus `.chapter-lead` (synopsis), `.chapter-keywords`, and `.chapter-nav` (Previous / Home / Next, shown top and bottom; Previous/Next only render when that chapter exists).

**Locked chapters** keep their title, synopsis, keywords and nav buttons, but the body is *never rendered* (not hidden by CSS — it isn't in the HTML at all). `config.BOOK_LOCKED_MESSAGE` is shown in `.chapter-locked` instead.

**Buttons** come from one function, `cards.book_actions(book)`: *Read Me* if the book has chapters, plus *Buy* (absolute `http(s)` link) or *Download* (relative link) using `linkDescription` from `books.json` for the label. The homepage row, the Books page card and the chapter-list hero all use it, so they can't disagree.

### The Series — `config.SERIES_*`, `chapters.get_series()`, `generators.generate_reading_pages()`

One non-fiction series reuses the book-chapter machinery above, with its own page names (`series.html`, `series-<slug>.html`) and a few differences, all in `generators._write_reading_pages()` (shared with books so the two can't drift):

- Chapters live in `book_chapters/<SERIES_FOLDER>/*.md` (currently `sunday_odds/`), same front matter as book chapters plus two optional keys below.
- **Dialogue:** start a paragraph with `**Revathi:**` or `**Anika:**` (names, mother first, in `config.SERIES_SPEAKERS`) and it renders with the speaker as a small label above the text and a coloured side rule per speaker (`.dialogue`, `.dialogue-s0/-s1`, `.dialogue-speaker`). Follow-on paragraphs stay plain.
- **Front-matter keys:** `asterisk: "one line"` renders as a closing note (`.chapter-asterisk`); `teaser: "Next Sunday, ..."` renders after it (`.chapter-teaser`). Neither is rendered for locked chapters. Keep values on one line; wrap them in double quotes.
- **Boxes and tables** are raw HTML blocks with `markdown="1"` so the inside is still markdown: `<div class="napkin" markdown="1">` (dashed worked-numbers box), `<div class="move" markdown="1">` (the Monday Move) and `<div class="tw" markdown="1">` around a pipe table (scrolls sideways on phones). Leave a blank line after the opening tag and before `</div>`.
- **Disclaimer:** `config.SERIES_DISCLAIMER` is added under every chapter and under the chapter list, so don't paste it into chapter files.
- **Fact-check markers:** the build warns about any published chapter that still contains a `[CHECK ...]` note.
- The chapter-nav Home button reads "All chapters"; the list page hero has a "Start with Chapter 1" button instead of buy/download buttons.
- **Homepage feature:** `.qa-series-card` (asterisk mark, eyebrow, title, premise, one primary button). Copy comes from `SERIES_TITLE`, `SERIES_PREMISE`, `SERIES_EYEBROW`.
- The build warns while `SERIES_TITLE` is still the `[Series title]` placeholder.

### Newsletter signup — `templates.newsletter_html()`

Homepage-only email capture, placed right after Recent essays, at the end of the page — the point where a visitor has just read a couple of
titles and decided they like the voice, which is the moment to ask them to
come back.

```python
templates.newsletter_html()
# -> full <section class="newsletter-section">...</section> plus an inline
#    <script>, or a disabled-state version if the proxy isn't configured,
#    or "" if config.NEWSLETTER_ENABLED is False
```

**Backend: Resend, via a proxy — not a direct form POST.** Resend's
Audiences API needs a secret bearer key on every call, which can never sit
in static HTML/JS (anyone can read it from the page source). So the form
submits via `fetch()` as JSON to your own small Lambda proxy
(`newsletter_lambda/handler.py`, deployed separately — see its README),
and that proxy holds the real Resend key and audience ID as Lambda
environment variables, never in this repo. The generator only needs to
know the proxy's public URL:

- `NEWSLETTER_API_ENDPOINT` (env `BLOG_NEWSLETTER_API_ENDPOINT`) — the
  deployed proxy's URL. Safe to expose; it can only add an email to your
  audience, not read your Resend key.
- `NEWSLETTER_HEADING` / `NEWSLETTER_SUBHEAD` — the copy.

If `NEWSLETTER_API_ENDPOINT` is unset, the section is **hidden entirely**
(a visible "being set up" box makes the site look unfinished, and posting to
nowhere would fail silently) and the generator logs a warning. Don't ignore
that warning; it means there is currently no signup on the site.

**Don't** point this at a generic ESP embed form (Mailchimp/ConvertKit/
Buttondown-style `<form action="...">`) without also updating the
JS — those expect a plain form POST, not the JSON-over-fetch flow this
component uses to talk to the Resend proxy.

Styled by `.newsletter-section` / `.newsletter-grid` / `.newsletter-form`
/ `.newsletter-input` in `styles.py`. Deliberately reuses the same
gradient-panel-with-rust-left-border look as the About page's "Want to
Connect?" box rather than inventing a new visual treatment for "here's a
thing to do" — that panel style is now the site's general call-to-action
pattern, not a one-off.

### Topics nav — `templates.topic_chips_html(categories)` (currently unused)

The homepage no longer shows a topic strip; themes live on the Essays page's
"By category" view. The helper is kept in case it returns. When it was in
use it was a row of pill-shaped links on the homepage, placed right after the hero,
letting a visitor jump straight into a theme (Self-Awareness & EQ, Money &
Meaning, etc.) instead of only seeing the site chronologically.

```python
topics_nav_html(sorted(set(p.category for p in posts)))
```

Each chip links to the same `category-<slug>.html` page that
`generators.generate_categories()` already builds — this is a second
entry point into existing pages, not a new page type, so there's nothing
to keep in sync beyond passing in the current category list. A trailing
"All topics →" chip always links to `categories.html`.

Styled by `.topics-nav` / `.topic-chip` in `styles.py`. Uses its own chip
style rather than `pill_badge()` — `pill_badge` is documented above as an
eyebrow label *above* a heading, and overloading it as a clickable nav
element would blur that meaning the next time someone reaches for it.

### Hero section pattern

Every hero (`.hero`) follows the same skeleton:

```html
<section class="hero">
  <div class="hero-bg-blob hero-bg-blob-1"></div>
  <!-- optional, homepage only -->
  <div class="hero-bg-blob hero-bg-blob-2"></div>
  <div class="container">
    <div class="hero-content">
      <!-- pill_badge(...) -->
      <h1 class="hero-title">...</h1>
      <!-- add .hero-title-gradient for the multicolor homepage treatment -->
      <p class="hero-description">...</p>
      <!-- optional .hero-cta buttons, optional .hero-stats -->
    </div>
  </div>
</section>
```

Interior pages (about, contact, categories, archives) use a plainer
version: pill badge + `.hero-title` + `.hero-description`, no blobs/stats —
those are reserved for the homepage so it still feels special.

### Section header pattern

```html
<div class="section-header section-header-centered">
  <!-- pill_badge(...) -->
  <h2 class="section-title">Section Name</h2>
  <p class="section-description section-description-centered">
    One-line description
  </p>
</div>
```

### Buttons

`.btn.btn-primary` (solid rust, for the main action) and `.btn.btn-secondary`
(outlined charcoal, for secondary actions). One primary button per section,
maximum.

### Dividers

```html
<div class="divider">
  <div class="divider-line" style="background: var(--color-rust);"></div>
  <div class="divider-dot" style="background: var(--color-rust);"></div>
  <div class="divider-line" style="background: var(--color-rust);"></div>
</div>
```

---

## Layout

```css
max-width: 1280px  /* .container, page-wide sections */
max-width: 64rem   /* Featured/video sections */
max-width: 56rem   /* Books, archive teaser */
max-width: 48rem   /* Article content, forms */
max-width: 42rem   /* About page */
```

Section padding: `6rem 0` standard (`.section`), `8rem 0 6rem` for hero.
Card grid gaps: `2rem` standard, `1.5rem` for stat cards.

---

## Adding a New Page

1. `header_html(title, active_page)` → `...content...` → `footer_html()`,
   written to `OUTPUT_DIR / <name>.html`. Add the page's key to
   `templates.header_html`'s nav list if it should appear in the header;
   otherwise it's still reachable from the footer nav.
2. Build the hero with the pattern above.
3. For any listing of posts/books, use the existing card functions and
   grid classes — don't write a new card.
4. Any pill/eyebrow label → `pill_badge()`, not inline styles.
5. Any YouTube video → `youtube_embed()`.
6. Escape any text sourced from markdown front matter or `*.json` data
   files with `html.escape` unless it's already going through a helper
   that does it for you (all of `cards.py` does).

---

## Known Constraints / Don'ts

- **Don't** import optional feature modules (like the AI chat widget)
  at the top of a file unconditionally — a missing optional module
  should degrade gracefully, not crash the whole generator. See
  `generators.get_chat_widget_html()` for the pattern (lazy import,
  gated on a config flag, falls back to `""` with a logged warning).
- **Don't** hardcode secrets/tokens in `config.py` — pull from
  environment variables (see `AWS_API_TOKEN`/`AWS_API_ENDPOINT`).
- **Don't** duplicate a component's markup inline "just this once" —
  it will drift. Extend the shared function/class instead.
- Keep true glassmorphism (`.stat-card-glass`) rare and intentional;
  it's a homepage-hero accent, not a default card style.
- **Don't** copy-paste one post's front matter as a starting point for a
  new post without rewriting the `excerpt` — this shipped to production
  once already (two posts sharing one teaser). `generate_blog.py` now
  calls `utils.check_duplicate_excerpts(posts)` on every build and logs a
  warning if any two posts share identical excerpt text; don't ignore
  that warning when it appears in the build log.
