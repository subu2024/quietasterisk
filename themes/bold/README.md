# bold theme

Crisp, colourful and loud. The asterisk is the brand mark, used as the logo, hero art, ticker separator,
panel watermark, section divider in essays (`* * *`) and the "asterisk" note on entries.

Use it: set `"theme": "bold"` in `content/site.json`, or `python build.py --theme bold`.

## Design language

* **Type**: Bricolage Grotesque (heavy display), Newsreader (long-form reading), Inter (UI). Loaded from Google Fonts in `base.html`.
* **Shapes**: 2.5px ink outlines, rounded corners, hard offset shadows that lift on hover.
* **Colour**: five tones (sun, coral, mint, lilac, cobalt). Essays take a tone from their category
  (`entry.category_hash`), so a category is always the same colour; lists and tiles cycle in order.
* **Motion**: spinning asterisk, scrolling ticker, hover lift, reading-progress bar. All switched off by `prefers-reduced-motion`.

## Re-colour or re-type in a minute

Everything is driven by the variables at the top of `static/css/style.css`:

```css
:root { --ink: #15121b; --paper: #fffbf3; --sun: #ffc83d; --coral: #ff5a36;
        --mint: #2ed3a5; --lilac: #c3b2ff; --cobalt: #3b4cff;
        --font-display: 'Bricolage Grotesque', ...; --font-body: 'Newsreader', ...; }
```

To change fonts, edit the Google Fonts `<link>` in `templates/base.html` and the three `--font-*` variables.

## Things this theme styles that come from content

The About page (`content/pages/about.md`) uses the classes `letter-heading`, `letter-callout`, `letter-signoff` and `name`;
chapter collections with `speakers` produce `dialogue` paragraphs. This theme styles all of them.

## Files

`templates/` follows `docs/THEME_CONTRACT.md` exactly (all required templates, plus `page_letter`, `page_contact`, `404`).
`static/js/site.js` is about 90 lines of plain JavaScript (tabs, load more, newsletter, progress bar), wired by `data-*` attributes.
