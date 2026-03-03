"""
Card components for displaying posts, books, and categories.
"""

from models import Post
from utils import copy_image


def format_featured_card(post: Post) -> str:
    """
    Generate large featured card for hero section.
    
    Args:
        post: Post object to display
        
    Returns:
        HTML string for featured card
    """
    return f"""
<article class="card card-featured">
  <span class="featured-badge">Featured</span>
  <div class="card-meta" style="margin-bottom: 1.5rem;">
    <span class="card-category" style="color: var(--color-rust);">{post.category}</span>
    <span class="post-meta-item">{post.formatted_date}</span>
    <span class="post-meta-item">{post.reading_time}</span>
  </div>
  <h3 class="card-title">{post.title}</h3>
  <p class="card-excerpt">{post.excerpt}</p>
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
        is_small: Whether to use compact styling
        
    Returns:
        HTML string for card
    """
    return f"""
<article class="card">
  <div class="card-meta">
    <span class="card-category" style="color: var(--color-rust);">{post.category}</span>
    <span class="post-meta-item">{post.formatted_date}</span>
  </div>
  <h3 class="card-title">{post.title}</h3>
  <p class="card-excerpt">{post.excerpt}</p>
  <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
    <span class="post-meta-item">{post.reading_time}</span>
    <a href="{post.slug}" class="card-link">
      Read
      <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
      </svg>
    </a>
  </div>
</article>
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
            img_html = f'<img src="{img}" class="book-image" alt="{book.get("title", "")}">'
    
    # Truncate description if needed
    description = book.get("description", "")
    if not show_full_description and len(description) > 150:
        description = description[:150] + "..."
    
    # Buy button if link exists
    link_html = ""
    link_url = book.get("link", "")
    if link_url:
        link_html = f'''
        <a href="{link_url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" 
           style="font-size: 0.875rem; padding: 0.75rem 1.5rem; display: inline-block;">
          Buy Book
        </a>
        '''
    
    # Optional metadata
    author_html = ""
    if book.get("author"):
        author_html = f'<p style="color: var(--color-slate); margin-bottom: 0.5rem; font-family: var(--font-sans); font-size: 0.875rem;">by {book.get("author")}</p>'
    
    year_html = ""
    if book.get("year"):
        year_html = f'<p style="color: var(--color-slate); margin-bottom: 1rem; font-family: var(--font-sans); font-size: 0.875rem;">Published {book.get("year")}</p>'
    
    return f"""
<div class="book-card">
  {img_html}
  <h4 class="book-title">{book.get("title", "")}</h4>
  {author_html}
  {year_html}
  <p class="book-description">{description}</p>
  {link_html}
</div>
"""
