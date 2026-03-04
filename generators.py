"""
Page generators for the blog.
Each function generates a specific page type.
"""

import re
import logging
import markdown
from typing import List, Dict

from config import *
from models import Post
from templates import header_html, footer_html
from cards import format_card, format_featured_card, format_book_card
from utils import copy_image, load_books, load_categories, slugify

logger = logging.getLogger("BlogGen")

# Global variable for temp content
TEMP_CONTENT = ""


def generate_post_pages(posts: List[Post], related_map: Dict[str, List[str]]):
    """Generate individual blog post pages."""
    global TEMP_CONTENT
    
    for post in posts:
        # Convert markdown to HTML
        html_body = markdown.markdown(post.body, extensions=['extra', 'codehilite'])
        
        # Handle images
        img_matches = re.findall(r'<img.*?src=[\'"](.*?)[\'"]', html_body)
        for img_src in img_matches:
            copied = copy_image(img_src)
            if copied:
                html_body = html_body.replace(img_src, copied)

        # Related posts HTML
        related_html = ""
        related_slugs = related_map.get(post.slug, [])
        if related_slugs:
            related_html = '<div class="related-posts"><h4 class="related-posts-title">Related Essays</h4><ul class="related-posts-list">'
            for slug in related_slugs:
                related_post = next((p for p in posts if p.slug == slug), None)
                if related_post:
                    related_html += f'<li class="related-posts-item"><a href="{slug}" class="related-posts-link">{related_post.title}</a></li>'
            related_html += '</ul></div>'

        # Build page
        content = header_html(post.title, "")
        content += f"""
<article class="post-content animate-in">
  <header class="post-header">
    <div class="post-meta">
      <span class="post-category">{post.category}</span>
      <span class="post-meta-item">{post.formatted_date}</span>
      <span class="post-meta-item">{post.reading_time}</span>
    </div>
    <h1 class="post-title">{post.title}</h1>
    <div class="decorative-line"></div>
  </header>
  <div class="post-body">
    {html_body}
  </div>
  {related_html}
</article>
"""
        content += footer_html()

        out_path = OUTPUT_DIR / post.slug
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        from utils import clean_text
        TEMP_CONTENT += f"TITLE: {post.title}\nDATE: {post.date}\nCONTENT: {clean_text(post.body)[:500]}\n\n"


def generate_index(posts: List[Post], related_map: Dict):
    """Generate homepage with hero, books, featured and recent posts."""
    books = load_books()
    
    # Generate individual post pages
    generate_post_pages(posts, related_map)

    content = header_html("Home - " + BLOG_TITLE, "home")

    # Hero Section
    content += f"""
<section class="hero">
  <div class="hero-bg-blob hero-bg-blob-1"></div>
  <div class="hero-bg-blob hero-bg-blob-2"></div>
  <div class="container">
    <div class="hero-content">
      <p class="hero-label">Welcome to Quiet Asterisk</p>
      <h1 class="hero-title">
        Essays on <span class="hero-title-accent" style="color: var(--color-rust);">meaning</span>, 
        <span style="color: var(--color-sage);">uncertainty</span>, and the quiet details
      </h1>
      <p class="hero-subtitle">that shape how we think and see the world</p>
      <p class="hero-description">
        A collection of reflections on systems, stories, and the subtle patterns that connect them. 
        Written with care for those who notice the small things.
      </p>
      <div class="hero-cta">
        <a href="#featured" class="btn btn-primary">Explore Essays</a>
        <a href="about.html" class="btn btn-secondary">About the Author</a>
      </div>
      <div class="hero-stats">
        <div class="stat-item">
          <div class="stat-number">{len(posts)}+</div>
          <div class="stat-label">Essays Published</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{len(set(p.category for p in posts))}</div>
          <div class="stat-label">Categories</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{len(books)}</div>
          <div class="stat-label">Books Written</div>
        </div>
      </div>
    </div>
  </div>
</section>
"""

    # Books section
    if books:
        content += """
<section class="section">
  <div class="container">
    <div class="section-header">
      <h2 class="section-title">Books</h2>
      <p class="section-description">Published works and ongoing projects</p>
    </div>
    <div class="books-grid">
"""
        for book in books[:BOOKS_ON_HOMEPAGE]:
            content += format_book_card(book, show_full_description=False)
        content += """
    </div>
    <div style="margin-top: 3rem; text-align: center;">
      <a href="books.html" class="btn btn-secondary">View All Books</a>
    </div>
  </div>
</section>
"""

    # Divider
    content += """
<div class="divider">
  <div class="divider-line" style="background: var(--color-rust);"></div>
  <div class="divider-dot" style="background: var(--color-rust);"></div>
  <div class="divider-line" style="background: var(--color-rust);"></div>
</div>
"""

    # Featured Essays
    featured_posts = [p for p in posts if p.featured][:4]
    if featured_posts:
        content += """
<section class="section" id="featured">
  <div class="container">
    <div class="section-header section-header-centered">
      <h2 class="section-title">Featured Essays</h2>
      <p class="section-description section-description-centered">Recent explorations worth your time</p>
      <div style="display: flex; justify-content: center; margin-top: 2rem;">
        <div style="width: 6rem; height: 2px; background: linear-gradient(90deg, transparent, var(--color-rust), transparent);"></div>
      </div>
    </div>
    <div class="featured-grid">
"""
        content += format_featured_card(featured_posts[0])
        content += '<div style="display: flex; flex-direction: column; gap: 2rem;">'
        for post in featured_posts[1:]:
            content += format_card(post, is_small=True)
        content += '</div></div></div></section>'

    # Recent Posts
    recent_posts = [p for p in posts if not p.featured][:6]
    if recent_posts:
        content += """
<section class="section">
  <div class="container">
    <div class="section-header">
      <h2 class="section-title">Recent Essays</h2>
      <p class="section-description">Latest thoughts and explorations</p>
    </div>
    <div class="card-grid">
"""
        for post in recent_posts:
            content += format_card(post)
        content += """
    </div>
    <div style="margin-top: 4rem; text-align: center;">
      <a href="categories.html" class="btn btn-secondary">View All Essays</a>
    </div>
  </div>
</section>
"""

    content += footer_html()
    with open(OUTPUT_DIR / INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def generate_books():
    """Generate dedicated books page."""
    books = load_books()
    if not books:
        return
    
    content = header_html("Books - " + BLOG_TITLE, "books")
    content += """
<section class="hero" style="padding: 6rem 0 4rem;">
  <div class="container">
    <div class="hero-content">
      <p class="hero-label">Published Works</p>
      <h1 class="hero-title" style="font-size: clamp(3rem, 5vw, 4rem);">
        Published Books and Ongoing Projects
      </h1>
      <p class="hero-description" style="max-width: 48rem;">
        A collection of works exploring life, meaning, technology and the human experience.
      </p>
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="books-grid">
"""
    for book in books:
        content += format_book_card(book, show_full_description=True)
    content += """
    </div>
  </div>
</section>
"""
    content += footer_html()
    with open(OUTPUT_DIR / BOOKS_FILE_HTML, "w", encoding="utf-8") as f:
        f.write(content)


def generate_categories(posts: List[Post]):
    """Generate category landing page and individual category pages."""
    grouped = {}
    for post in posts:
        grouped.setdefault(post.category, []).append(post)
    
    categories_meta = load_categories()

    # Main categories page
    content = header_html("Categories - " + BLOG_TITLE, "categories")
    content += """
<section class="section">
  <div class="container">
    <div class="section-header section-header-centered">
      <h1 class="section-title">Explore by Category</h1>
      <p class="section-description section-description-centered">
        Different lenses for looking at the world
      </p>
    </div>
    <div class="card-grid">
"""

    for category in sorted(grouped.keys()):
        cat_posts = grouped[category]
        category_slug = slugify(category)
        category_file = f"category-{category_slug}.html"
        category_info = categories_meta.get(category, {})
        description = category_info.get("description", f"Essays exploring {category.lower()}")
        
        content += f"""
    <a href="{category_file}" style="text-decoration: none; color: inherit;">
      <article class="card">
        <div class="card-meta">
          <span class="card-category" style="color: var(--color-rust);">{len(cat_posts)} essays</span>
        </div>
        <h3 class="card-title">{category}</h3>
        <p class="card-excerpt">{description}</p>
        <div class="card-link" style="margin-top: 1rem;">
          Explore {category}
          <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
          </svg>
        </div>
      </article>
    </a>
"""

    content += "</div></div></section>"
    content += footer_html()
    with open(OUTPUT_DIR / CATEGORIES_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    # Individual category pages
    for category, cat_posts in grouped.items():
        generate_category_page(category, cat_posts, categories_meta.get(category, {}))


def generate_category_page(category: str, posts: List[Post], category_meta: dict):
    """Generate individual category page with load more."""
    posts.sort(key=lambda p: p.date or "", reverse=True)
    category_slug = slugify(category)
    category_file = f"category-{category_slug}.html"
    description = category_meta.get("description", f"Essays exploring {category.lower()}")
    
    content = header_html(f"{category} - " + BLOG_TITLE, "categories")
    content += """
<script>
function loadMore() {
    const hiddenPosts = document.querySelectorAll('.hidden-post');
    let count = 0;
    hiddenPosts.forEach(post => {
        if (count < 10) {
            post.classList.remove('hidden-post');
            post.style.display = 'block';
            count++;
        }
    });
    const remaining = document.querySelectorAll('.hidden-post');
    const button = document.getElementById('load-more-btn');
    if (remaining.length === 0) {
        button.style.display = 'none';
    } else {
        button.innerHTML = `Load More (${remaining.length} remaining)`;
    }
}
</script>
"""
    
    content += f"""
<section class="hero" style="padding: 6rem 0 4rem;">
  <div class="container">
    <div class="hero-content">
      <p class="hero-label">
        <a href="{CATEGORIES_FILE}" style="color: var(--color-rust); text-decoration: none;">← All Categories</a>
      </p>
      <h1 class="hero-title" style="font-size: clamp(3rem, 5vw, 4rem);">
        {category}
      </h1>
      <p class="hero-description" style="max-width: 48rem;">
        {description}
      </p>
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="card-grid">
"""
    
    for idx, post in enumerate(posts):
        hidden_class = ' hidden-post' if idx >= POSTS_PER_CATEGORY_PAGE else ''
        content += f'<div class="card-wrapper{hidden_class}">'
        content += format_card(post)
        content += '</div>'
    
    content += "</div>"
    
    if len(posts) > POSTS_PER_CATEGORY_PAGE:
        remaining = len(posts) - POSTS_PER_CATEGORY_PAGE
        content += f"""
    <div style="text-align: center; margin-top: 3rem;">
      <button id="load-more-btn" onclick="loadMore()" class="btn btn-secondary" style="cursor: pointer;">
        Load More ({remaining} remaining)
      </button>
    </div>
"""
    
    content += "</div></section>"
    content += footer_html()
    with open(OUTPUT_DIR / category_file, "w", encoding="utf-8") as f:
        f.write(content)


def generate_about():
    """Generate about page."""
    content = header_html("About - " + BLOG_TITLE, "about")
    content += """
<section class="section">
  <div class="container">
    <article class="post-content">
      <h2>About the Author</h2>
      <p>Subu Sangameswar writes about love and loss, parenting chaos,
    uncertainty, systems, and our deeply human habit of demanding clarity
    from a world that offers none.</p><br/>
    <p>Part biography, part fiction, his work moves like an episode of
    <a href="https://en.wikipedia.org/wiki/Seinfeld" target="_blank" rel="noopener noreferrer">Seinfeld</a>
    — observant, self-aware, mildly neurotic, and uncomfortably honest.</p><br/>
    <p>In a culture obsessed with certainty, he lingers in risk, chance, and
    hope — treating uncertainty not as a flaw to eliminate, but as a
    companion to travel with. Preferably with humor. Sometimes with coffee.</p>
    </article>
  </div>
</section>
"""
    content += footer_html()
    with open(OUTPUT_DIR / ABOUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def generate_contact():
    """Generate contact page."""
    content = header_html("Contact - " + BLOG_TITLE, "contact")
    content += f"""
<section class="hero" style="padding: 6rem 0 4rem;">
  <div class="container">
    <div class="hero-content">
      <p class="hero-label">Get in Touch</p>
      <h1 class="hero-title" style="font-size: clamp(3rem, 5vw, 4rem);">
        Let's <span style="color: var(--color-rust); font-style: italic;">Connect</span>
      </h1>
      <p class="hero-description" style="max-width: 48rem;">
        Whether you have thoughts on an essay, questions about a book, or just want to say hello—I'd love to hear from you.
      </p>
    </div>
  </div>
</section>
<section class="section">
  <div class="container" style="max-width: 48rem;">
    <div style="background: white; border: 2px solid var(--color-sand); padding: 3rem; border-radius: 4px; text-align: center;">
      <div style="width: 80px; height: 80px; background: var(--color-rust); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 2rem;">
        <svg width="40" height="40" fill="none" stroke="white" viewBox="0 0 24 24" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
      </div>
      <h2 style="font-family: var(--font-serif); font-size: 2rem; margin-bottom: 1rem;">Email Me</h2>
      <p style="color: var(--color-slate); margin-bottom: 2rem;">I typically respond within a few days</p>
      <a href="mailto:{CONTACT_EMAIL}" class="btn btn-primary" style="font-size: 1.125rem; padding: 1rem 2.5rem;">
        {CONTACT_EMAIL}
      </a>
    </div>
  </div>
</section>
"""
    content += footer_html()
    with open(OUTPUT_DIR / CONTACT_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def get_temp_content():
    """Return temporary content for debugging."""
    return TEMP_CONTENT
