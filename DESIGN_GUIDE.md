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
