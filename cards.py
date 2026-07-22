"""
Card components for displaying posts, books, and categories.

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

from models import Post
from utils import copy_image, category_accent, youtube_embed

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
    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
    </svg>
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


def format_reading_note_card(note: dict) -> str:
    """Generate a compact card for a short reading-log entry."""
    author_html = ""
    if note.get("author"):
        author_html = f'<p class="book-meta-line">by {escape(note.get("author"))}</p>'

    link_html = ""
    if note.get("link"):
        link_html = (
            f'<a href="{escape(note.get("link"))}" target="_blank" '
            f'rel="noopener noreferrer" class="card-link" style="display: inline-flex;">'
            f'More on this book →</a>'
        )

    return f"""
<div class="book-card">
  <h4 class="book-title">{escape(note.get("title", ""))}</h4>
  {author_html}
  <p class="book-description">{escape(note.get("note", ""))}</p>
  {link_html}
</div>
"""


def format_book_card(book: dict, show_full_description: bool = False) -> str:
    """
    Generate book card with cover image and buy button.

    Args:
        book: Book dictionary from books.json
        show_full_description: Whether to show full or truncated description

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

    # Buy button if link exists
    link_html = ""
    link_url = book.get("link", "")
    if link_url:
        link_html = f'''
        <a href="{escape(link_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary"
           style="font-size: 0.875rem; padding: 0.75rem 1.5rem; display: inline-block;">
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

    return f"""
<div class="book-card">
  <div style="display: flex; gap: 1.25rem; align-items: flex-start;">
    {img_html}
    <div style="flex: 1; min-width: 0;">
      <h4 class="book-title">{escape(book.get("title", ""))}</h4>
      {author_html}
      {year_html}
      <p class="book-description">{escape(description)}</p>
      {link_html}
    </div>
  </div>
  {video_html}
</div>
"""
