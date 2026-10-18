"""
Card components for displaying posts, books, and categories.
(format_essay_row is the one non-card: a plain list row for the homepage.)

Design notes:
- Every category gets a consistent, distinct accent color (see
  utils.category_accent) instead of everything defaulting to rust, so
  scanning a grid of mixed categories is easier at a glance.
- All user-authored fields (titles, excerpts, notes, book metadata) are
  HTML-escaped since they come from markdown front matter / JSON files
  and may contain characters like & or < that would otherwise break
  the page.
- format_card() previously accepted an `is_small` flag that did nothing;
  it now toggles the .card-compact style defined in styles.py.
"""

from html import escape
from typing import List, Tuple
from urllib.parse import quote

from config import BOOK_READ_LABEL
from models import Post
from chapters import get_publication_for_book
from utils import copy_image, category_accent, youtube_embed, slugify, arrow_icon, format_thought_date

_ACCENT_VARS = {
    "rust": "var(--color-rust)",
    "sage": "var(--color-sage)",
    "gold": "var(--color-gold)",
    "terracotta": "var(--color-terracotta)",
}


def _category_badge(category: str) -> str:
    """Return a colored, escaped category pill consistent across all cards."""
    accent = category_accent(category)
    return f'<span class="card-category card-category-{accent}">{escape(category)}</span>'


def _accent_border(category: str) -> str:
    """Return an inline top-border style matching the category's accent color."""
    accent_var = _ACCENT_VARS[category_accent(category)]
    return f'border-top: 4px solid {accent_var};'


def format_featured_card(post: Post) -> str:
    """
    Generate large featured card for hero section.

    Args:
        post: Post object to display

    Returns:
        HTML string for featured card
    """
    return f"""
<article class="card card-featured" style="{_accent_border(post.category)}">
  <span class="featured-badge">Featured</span>
  <div class="card-meta" style="margin-bottom: 1.5rem;">
    {_category_badge(post.category)}
    <span class="post-meta-item">{escape(post.formatted_date)}</span>
    <span class="post-meta-item">{escape(post.reading_time)}</span>
  </div>
  <h3 class="card-title">{escape(post.title)}</h3>
  <p class="card-excerpt">{escape(post.excerpt)}</p>
  <a href="{post.slug}" class="card-link">
    Read Essay
    {arrow_icon()}
  </a>
</article>
"""


def format_card(post: Post, is_small: bool = False) -> str:
    """
    Generate standard card for post listings.

    Args:
        post: Post object to display
        is_small: Use the compact card style (smaller title/excerpt, tighter
            padding, clamped excerpt) for dense layouts like the featured
            sidebar list.

    Returns:
        HTML string for card
    """
    card_class = "card card-compact" if is_small else "card"
    return f"""
<article class="{card_class}" style="{_accent_border(post.category)}">
  <div class="card-meta">
    {_category_badge(post.category)}
    <span class="post-meta-item">{escape(post.formatted_date)}</span>
  </div>
  <h3 class="card-title">{escape(post.title)}</h3>
  <p class="card-excerpt">{escape(post.excerpt)}</p>
  <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
    <span class="post-meta-item">{escape(post.reading_time)}</span>
    <a href="{post.slug}" class="card-link">
      Read
      <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
      </svg>
    </a>
  </div>
</article>
"""


def format_essay_row(post: Post) -> str:
    """
    Generate a quiet, typographic list row for the homepage "Recent essays".

    Deliberately not a card: no colored pill, no accent border, no button.
    Just a small meta line, the title, and the excerpt, with the whole row
    as one link. Use format_card() for grids (Essays page, category pages);
    use this for short vertical lists where less chrome reads better.

    Styled by .qa-essay* in styles.py (scoped under .quiet-home).
    """
    meta = " · ".join(
        part for part in (post.category, post.formatted_date, post.reading_time) if part
    )
    return f"""
<a class="qa-essay" href="{post.slug}">
  <div class="qa-essay-meta">{escape(meta)}</div>
  <h3>{escape(post.title)}</h3>
  <p>{escape(post.excerpt)}</p>
</a>
"""


def format_thought_item(thought: dict) -> str:
    """
    One entry in the Daily Thoughts feed: the text, then the date in small
    type below it. The feed's CSS (.thought-item) draws the line between
    entries. Line breaks in the text are kept (white-space: pre-line).
    """
    date = thought.get("date", "")
    date_html = (
        f'<time class="thought-date" datetime="{escape(date)}">{escape(format_thought_date(date))}</time>'
        if date else ""
    )
    return f"""
<article class="thought-item">
  <p class="thought-text">{escape(thought.get("text", ""))}</p>
  {date_html}
</article>
"""


def format_reading_note_card(note: dict, cross_link_html: str = "") -> str:
    """
    Generate a compact card for a short reading-log entry.

    Args:
        note: Reading-note dictionary from reading_notes.json
        cross_link_html: Optional pre-built HTML link, used when this note's
            title matches one of the author's own books (see generate_books
            in generators.py), so a visitor can jump straight to "the real
            book" instead of the two entries sitting disconnected.
    """
    author_html = ""
    if note.get("author"):
        author_html = f'<p class="book-meta-line">by {escape(note.get("author"))}</p>'

    link_html = ""
    if note.get("link"):
        link_html = (
            f'<a href="{escape(note.get("link"))}" target="_blank" '
            f'rel="nofollow sponsored noopener noreferrer" class="card-link" style="display: inline-flex;">'
            f'More on this book →</a>'
        )

    anchor_id = slugify(note.get("title", ""))

    return f"""
<div class="book-card" id="note-{anchor_id}">
  <h4 class="book-title">{escape(note.get("title", ""))}</h4>
  {author_html}
  <p class="book-description">{escape(note.get("note", ""))}</p>
  {link_html}
  {cross_link_html}
</div>
"""


def format_book_card(book: dict, show_full_description: bool = False, cross_link_html: str = "", read_url: str = "") -> str:
    """
    Generate book card with cover image and buy button.

    Args:
        book: Book dictionary from books.json
        show_full_description: Whether to show full or truncated description
        cross_link_html: Optional pre-built HTML link, used when this book
            also has a reading note (see generate_books in generators.py),
            so the two entries point at each other instead of sitting on
            disconnected pages.
        read_url: Optional chapter-list page (chapters.Publication.toc_url).
            When given, a "Read Me" button is shown next to the buy/download
            button.

    Returns:
        HTML string for book card
    """
    # Handle book cover image
    img_html = ""
    if book.get("image"):
        img = copy_image(book.get("image"))
        if img:
            img_html = f'<img src="{img}" class="book-image" alt="{escape(book.get("title", ""))}">'

    # Truncate description if needed
    description = book.get("description", "")
    if not show_full_description and len(description) > 150:
        description = description[:150] + "..."

    # YouTube video embed if video_id exists
    video_html = ""
    if book.get("video_id"):
        video_html = youtube_embed(book.get("video_id"), title=f"Video about {book.get('title', '')}")

    # Read button (chapters on this site) + buy/download button if link exists
    link_html = ""
    link_url = book.get("link", "")
    if read_url:
        link_html += f'''
        <a href="{escape(read_url)}" class="btn btn-secondary"
           style="font-size: 0.875rem; padding: 0.75rem 1.5rem; display: inline-block; margin-right: 0.5rem; margin-bottom: 0.5rem;">
          {escape(BOOK_READ_LABEL)}
        </a>
        '''
    if link_url:
        link_html += f'''
        <a href="{escape(link_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary"
           style="font-size: 0.875rem; padding: 0.75rem 1.5rem; display: inline-block; margin-bottom: 0.5rem;">
          {escape(book.get("linkDescription", "Buy Book"))}
        </a>
        '''

    # Optional metadata
    author_html = ""
    if book.get("author"):
        author_html = f'<p class="book-meta-line">by {escape(book.get("author"))}</p>'

    year_html = ""
    if book.get("year"):
        year_html = f'<p class="book-meta-line" style="margin-bottom: 1rem;">Published {escape(str(book.get("year")))}</p>'

    anchor_id = slugify(book.get("title", ""))

    return f"""
<div class="book-card" id="book-{anchor_id}">
  <div style="display: flex; gap: 1.25rem; align-items: flex-start;">
    {img_html}
    <div style="flex: 1; min-width: 0;">
      <h4 class="book-title">{escape(book.get("title", ""))}</h4>
      {author_html}
      {year_html}
      <p class="book-description">{escape(description)}</p>
      {link_html}
      {cross_link_html}
    </div>
  </div>
  {video_html}
</div>
"""


def book_actions(book: dict) -> List[Tuple[str, str, str, bool]]:
    """
    Work out which action buttons a book gets.

    Returns a list of (kind, label, href, is_external) tuples, in display
    order, where kind is "read", "buy" or "download":

    - "read": the book has chapters on this site (a publications.json entry whose "linked_book" is this title).
    - "buy": books.json `link` is an absolute http(s) URL (e.g. Amazon).
    - "download": books.json `link` is a relative path (e.g. downloads/x.pdf).

    The buy/download label comes from books.json `linkDescription`
    ("Buy on Amazon", "Download Free PDF") with a plain default.
    A book with an empty `link` (the "Not Available" entries) gets no
    buy/download action.
    """
    actions: List[Tuple[str, str, str, bool]] = []

    publication = get_publication_for_book(book.get("title", ""))
    if publication:
        actions.append(("read", BOOK_READ_LABEL, publication.toc_url, False))

    link = (book.get("link") or "").strip()
    if link:
        if link.lower().startswith(("http://", "https://")):
            actions.append(("buy", book.get("linkDescription") or "Buy Me", link, True))
        else:
            actions.append(("download", book.get("linkDescription") or "Download",
                            quote(link, safe="/"), False))
    return actions


def book_action_buttons(book: dict, include_read: bool = True) -> str:
    """
    Render book_actions() as anchor buttons using the shared .btn classes
    (the first one is primary). Pass include_read=False on the book's own
    chapter-list page, where a "Read Me" button would just link to itself.
    """
    html = []
    actions = [a for a in book_actions(book) if include_read or a[0] != "read"]
    for index, (kind, label, href, external) in enumerate(actions):
        variant = "btn-primary" if index == 0 else "btn-secondary"
        attrs = ' target="_blank" rel="noopener noreferrer"' if external else ""
        if kind == "download":
            attrs += " download"
        html.append(f'<a href="{escape(href)}" class="btn {variant}"{attrs}>{escape(label)}</a>')
    return "".join(html)


def format_book_action_row(book: dict) -> str:
    """
    Compact homepage row for one book: cover, title, description, and its
    Read Me / Download / Buy buttons (see book_actions).

    Styled by .qa-book* in styles.py (scoped under .quiet-home).
    """
    title = book.get("title", "")

    img_html = ""
    if book.get("image"):
        img = copy_image(book.get("image"))
        if img:
            img_html = f'<div class="qa-book-cover"><img src="{img}" alt="Cover of {escape(title)}" loading="lazy"></div>'

    buttons = []
    for kind, label, href, external in book_actions(book):
        variant = "qa-book-btn--outline" if buttons else "qa-book-btn--solid"
        attrs = ' target="_blank" rel="noopener noreferrer"' if external else ""
        if kind == "download":
            attrs += " download"
        buttons.append(f'<a class="qa-book-btn {variant}" href="{escape(href)}"{attrs}>{escape(label)}</a>')

    if not buttons:
        buttons.append(f'<span class="qa-book-unavailable">{escape(book.get("linkDescription") or "Not available")}</span>')

    modifier = "" if img_html else " qa-book--no-cover"
    return f"""
<article class="qa-book{modifier}" id="book-{slugify(title)}">
  {img_html}
  <div class="qa-book-body">
    <h3>{escape(title)}</h3>
    <p>{escape(book.get("description", ""))}</p>
  </div>
  <div class="qa-book-actions">{"".join(buttons)}</div>
</article>
"""
