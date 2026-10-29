# Content guide

Everything you write or configure lives in `content/`. None of it mentions HTML or a theme.

```
content/
  site.json            site identity, nav, newsletter, page text, redirects
  collections.json     one entry per folder of markdown
  essays/              markdown (a collection)
  sunday_odds/         markdown (a collection)
  pages/               standalone pages: about.md, contact.md
  data/                books.json, reading_notes.json, thoughts.json, videos.json, categories.json
  assets/images/       logo, book covers, images used in markdown
  assets/downloads/    PDFs and other downloads
```

## Front matter (the same for every markdown entry)

Put this at the very top of the file. Only `title` is required.

```
---
title: Who Would Cry?
slug: who-would-cry              optional custom page name (".html" added if missing)
aliases: old-name.html           optional: old page names that redirect here
date: 2026-10-17                 YYYY-MM-DD, drives sorting and display
category: Self-Awareness & EQ    essays
synopsis: One or two lines for cards, lists, search snippets and the RSS feed.
keywords: probability, patience
lock: false                      true / yes / 1 = NOT published anywhere
image: cover.png                 optional social-share image (file in assets/images)
asterisk: optional closing line
teaser: optional "Next Sunday, ..." line
---
```

Old names still work: `excerpt:` is `synopsis:`, `archived:` is `lock:`.

In the body you can use normal markdown plus:

| Syntax | Result |
|---|---|
| `[youtube:VIDEO_ID]` | An embedded video (markup comes from the theme) |
| `**Revathi:** text` | A labelled dialogue line, if the collection lists `"speakers": ["Revathi", ...]` |
| `![alt](cover.png)` | Image from `assets/images/` (copied automatically) |

## collections.json

```json
{
  "defaults": { "layout": "chapters", "show_on_home": 0 },
  "collections": [
    { "id": "essays", "title": "Essays", "folder": "essays", "layout": "essays",
      "sort": "descending", "show_on_home": 3, "home_heading": "Recent essays",
      "synopsis": "...", "see_all_label": "Browse all essays →" },
    { "id": "sunday_odds", "title": "Sunday Odds", "folder": "sunday_odds",
      "layout": "chapters", "page_prefix": "series", "sort": "ascending",
      "show_on_home": 0, "synopsis": "...", "intro": "...", "disclaimer": "...",
      "speakers": ["Revathi", "Anika"] }
  ]
}
```

| Key | Meaning |
|---|---|
| `title`, `folder` | Required. `folder` is under `content/` |
| `id` | Default: the folder name |
| `layout` | `essays` (flat title-based URLs; listed on the Essays and category pages, feed, related) or `chapters` (a list page `<page_prefix>.html` plus `<prefix>-<file>.html` pages) |
| `lock` | `true` unpublishes the whole collection |
| `sort` | `ascending` / `descending` (default: essays descending, chapters ascending). Controls every list, prev/next and the homepage "top N". Chapter numbers always follow reading order |
| `show_on_home` | absent or `false`: not on the homepage. `0`: synopsis and a "read all" link. `N`: synopsis, top N entries, "read all" |
| `synopsis`, `home_heading`, `see_all_label` | Homepage block text |
| `page_prefix` | Chapters only; default `book-<folder>` |
| `linked_book` | Exact title in `books.json`: adds Read Me, Buy and Download buttons |
| `eyebrow`, `eyebrow_url`, `intro`, `read_note`, `disclaimer`, `start_label`, `home_label`, `speakers` | Text on the collection's list page and entry pages |

Unknown keys produce a warning with a "did you mean" suggestion.

## site.json

Layered over `qa/default_site.json`, so you only override what you need. Notable settings:

| Setting | Purpose |
|---|---|
| `title`, `tagline`, `url`, `author`, `email`, `copyright`, `logo`, `analytics_id` | Identity (logo is a file in `assets/images`) |
| `theme` | Folder name under `themes/` |
| `nav`, `footer_nav` | `[{"label": "...", "page": "essays"}]`; a page that does not exist is dropped. Use `"url"` for external links |
| `social` | `[{"label", "icon", "url"}]` |
| `newsletter` | `enabled`, `heading`, `subhead`, `fine_print`, messages. The endpoint comes from env `BLOG_NEWSLETTER_API_ENDPOINT` |
| `home` | `hero_title`, `thought_after` (collection id after which the daily thought appears) |
| `thoughts` | `newest_first` and the daily-thoughts texts |
| `publishing` | `hide_future_dated`, `similarity_threshold`, `related_count`, `group_preview_count`, `feed_items` |
| `redirects` | `{"old.html": "new.html"}` |
| `copy` | Headings and descriptions for the Essays, Categories, Books and Videos pages |

Environment overrides: `BLOG_SITE_URL`, `BLOG_NEWSLETTER_API_ENDPOINT`.

## Data files

| File | Shape |
|---|---|
| `books.json` | `[{"title", "description", "image", "link", "linkDescription", "video_id", "author", "year"}]`. A relative `link` (`downloads/x.pdf`) is a download; `http(s)` is a buy link; empty means "not available" |
| `reading_notes.json` | `[{"title", "author", "date", "note", "link"}]`, newest first on the page |
| `thoughts.json` | `[{"date": "YYYY-MM-DD", "text": "..."}]` |
| `videos.json` | `[{"title", "video_id", "article_link"}]` |
| `categories.json` | `{"Category name": {"description": "..."}}` |

A book and a reading note with the same title are cross-linked automatically.

## Standalone pages

`content/pages/<name>.md`, with front matter `title`, `slug`, `template` (`letter`, `contact`, `default`, or any `page_<name>.html` your theme provides), `section` (which nav item is highlighted), `description`, and any extra keys the template wants (the Contact page uses `eyebrow, heading, accent, intro, card_title, note`).

## Everyday tasks

| Task | Do this |
|---|---|
| Publish an essay | Add `content/essays/<name>.md` with front matter, run `python build.py` |
| Hide something | `lock: true` |
| Schedule an essay | Give it a future `date` and set `publishing.hide_future_dated` to `true` (or build with `--hide-future`); rebuild daily |
| Rename a URL | Change `slug:` and add the old name to `aliases:` |
| Reverse a series | `"sort": "descending"` |
| Feature a series on the home page | `"show_on_home": 0` (card) or `3` (top three) |
| Add a new series | New folder + new entry in `collections.json` |
| Check before deploying | `python build.py --strict` |
