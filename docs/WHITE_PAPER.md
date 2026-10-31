# Quiet Asterisk: Site Platform White Paper

**Version 2.0**

## Executive summary

Quiet Asterisk is a personal publishing site: essays on love, loss, money, parenting, technology and work, plus a fiction series (*Sunday Odds*), books, poems, daily thoughts, reading notes and video essays. This paper describes the platform that builds it.

Version 2 turns the site into a **static-site generator that keeps three things separate**: what you write (content), how it is assembled (engine) and how it looks (theme). The result is a fast, cheap-to-host site that you can redesign without touching a single essay.

## 1. What it is

| | |
|---|---|
| **The site** | A static website of HTML files, published on GitHub Pages |
| **The platform** | A Python build tool (about 1,600 lines of engine code) that turns markdown and JSON into that site |
| **The idea** | The asterisk, the small mark that says "this comes with conditions", as a metaphor for living well without certainty |
| **Who runs it** | One author, writing in markdown and publishing through Git |

## 2. What it does

1. Reads essays, chapters and poems from markdown files with a standard front matter.
2. Reads books, reading notes, thoughts, videos and settings from JSON.
3. Applies publishing rules: what is locked, what is dated in the future, how each collection is sorted, and what appears on the homepage.
4. Passes the result as plain data to a theme, which renders every page.
5. Produces the site plus a sitemap, RSS feed, `robots.txt` and redirect pages.
6. Checks its own output before publishing, so a broken build never replaces a working site.

## 3. Architecture

```
 content/  ──►  engine (qa/)  ──►  theme (themes/<name>/)  ──►  dist/  ──►  GitHub Pages
 what you       loads, validates,    templates, CSS, JS         the static
 write          plans pages                                     site
```

**The one rule:** the engine knows nothing about HTML, and a theme knows nothing about files or publishing rules. A test fails if the engine ever contains page markup.

| Layer | Folder | Contains |
|---|---|---|
| Content | `content/` | Essays, series, About and Contact (markdown), settings, data, images, downloads |
| Engine | `qa/` | Loaders, publishing rules, page planner, theme renderer, build pipeline |
| Presentation | `themes/` | Jinja2 templates, CSS, JavaScript for each design |

## 4. Key features

### Content and publishing

| Feature | What it gives you |
|---|---|
| **Collections** | Any folder of markdown becomes an essay blog, a book, a series or a poem set. A new one needs a folder and one JSON entry, with no code |
| **Standard front matter** | One format for everything: title, slug, date, category, synopsis, keywords, lock, aliases, image, asterisk note, teaser |
| **Lock** | `lock: true` removes an entry from every page, list, feed and sitemap |
| **Sort** | Ascending or descending per collection; it drives lists, previous/next and the homepage |
| **Show on home** | `0` shows a synopsis card, `N` shows the top N entries, and absent hides it |
| **Scheduling** | Future-dated entries can be held back until their date |
| **URL safety** | Existing page addresses never change; renamed pages get redirects through `aliases` |
| **Books and notes** | Automatic buy, download and read buttons, and cross-links when a book and a reading note share a title |
| **Markdown extras** | Embedded video tags, labelled dialogue for fiction, inline images |

### Presentation

| Feature | What it gives you |
|---|---|
| **Swappable themes** | `python build.py --theme bold` re-renders the same content in a new design |
| **Three themes** | `quiet` (the current paper-and-ink look), `bold` (colourful, heavy type, asterisk motif) and `minimal` (a 60-line reference) |
| **Written contract** | `THEME_CONTRACT.md` lists every template and variable, so a new theme can be built without reading the engine |
| **Automatic escaping** | Jinja2 escapes content by default, which removes a class of broken-markup bugs |
| **No inline styles** | Presentation lives in CSS, with cache-busted stylesheets |

### Reach and discoverability

Page descriptions, canonical URLs, Open Graph tags and JSON-LD structured data; an RSS feed; a sitemap with last-modified dates; `robots.txt`; related essays through text similarity; and a newsletter signup that talks to a separate serverless proxy so no secret key sits in the page.

### Quality and safety

| Safeguard | Effect |
|---|---|
| **Strict mode** | Any warning fails the build and leaves the live site untouched |
| **Link and asset check** | Finds broken internal links, missing covers, PDFs and logos |
| **Atomic publish** | The site is built aside and swapped in only on success |
| **Typo detection** | Misspelled settings produce a "did you mean" hint |
| **URL clash detection** | An essay titled "About" cannot silently overwrite the About page |
| **Tests** | 38 automated tests cover the content rules, full builds through every theme, and the theme boundary |

## 5. How it is operated

1. Write or edit markdown and JSON in `content/`.
2. Preview locally with `python build.py --serve`.
3. Run `python build.py --strict`, which is the same check the automation runs.
4. Push to GitHub. The workflow runs the tests and the strict build, and, on `main`, deploys `dist/` to GitHub Pages.
5. The newsletter proxy (`handler.py`, an AWS Lambda) is deployed separately and does not change with the site.

## 6. Current status and limits

- **Verified:** builds, tests and the visual design were checked locally with sample content, and the `quiet` theme's text and links matched the old generator's output.
- **Not yet verified:** a full run of the GitHub workflow, and the build against your complete real content (images and PDFs need to be moved into `content/assets/`).
- **Known limits:** search, tag pages, image optimisation and a cookie-consent banner are not built; the newsletter has no double opt-in; fonts load from Google Fonts.

## 7. Recommended upgrades for the next version

### Priority 1: finish and harden

| Upgrade | Why |
|---|---|
| **Confirm the deploy pipeline** | Get one green run to production, then add a scheduled build if essays are date-scheduled |
| **Newsletter double opt-in and abuse protection** | Confirmation email, a bot-trap field, and rate limiting on the signup endpoint |
| **Privacy and consent** | Analytics loads on every page; add a consent banner if you have EU readers |
| **Automatic social-share images** | Generate a branded image for each essay so shared links look good |

### Priority 2: reader experience

| Upgrade | Why |
|---|---|
| **Site search** | A client-side index (for example Pagefind) over essays and chapters |
| **Tag pages** | Keywords are already collected for every entry, so tag pages are a small step |
| **Dark mode** | Both main themes already run on colour variables |
| **Print and e-book export** | Turn a chapter collection into a PDF or EPUB, which suits a site that publishes books |
| **"Continue reading" and series email** | Email subscribers the next *Sunday Odds* chapter |

### Priority 3: publishing power

| Upgrade | Why |
|---|---|
| **Teaser mode for locked chapters** | Show the title and synopsis with a "get the book" prompt instead of hiding the chapter entirely |
| **Image optimisation** | Resize and convert to WebP, and require alt text |
| **Smarter related essays** | Blend text similarity with shared categories and keywords |
| **Browser-based editing** | A lightweight editor such as Decap CMS so essays can be written without touching Git |
| **Incremental builds** | Rebuild only what changed as the archive grows |

### Priority 4: longer term

An accessibility audit against WCAG 2.2; multilingual support; webmentions or comments; and a published theme gallery so new designs can be added without touching the engine.

## 8. Conclusion

Version 2 gives Quiet Asterisk a durable foundation: a content model that stays stable, rules that are enforced by tests, and a presentation layer that can change as often as the author likes. The next version should focus on confirming the deployment, protecting readers (consent, newsletter hardening) and deepening the reading experience with search, tags and book formats.