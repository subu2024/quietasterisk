"""
Page generators for the blog.
Each function generates a specific page type.
"""

import re
import logging
import markdown
from html import escape
from typing import List, Dict



from config import (
    BLOG_TITLE, TAG_LINE, COPYRIGHT, CONTACT_EMAIL, YOUTUBE_CHANNEL, VIDEOS_FILE_HTML,
    INDEX_FILE, ABOUT_FILE, CATEGORIES_FILE, BOOKS_FILE_HTML, CONTACT_FILE, INSTAGRAM_PROFILE,
    OUTPUT_DIR, POSTS_PER_CATEGORY_PAGE, BOOKS_ON_HOMEPAGE, ARCHIVES_FILE, LOGO_PATH,
    READING_FILE_HTML  # add this
)




from collections import defaultdict
from datetime import datetime

from config import ENABLE_AI_CHAT
from models import Post
from templates import header_html, footer_html, pill_badge
from cards import format_card, format_featured_card, format_book_card, format_reading_note_card
from utils import copy_image, load_books, load_categories, slugify, load_videos, show_logo, load_reading_notes, youtube_embed
from parser import process_youtube_embeds

logger = logging.getLogger("BlogGen")


def get_chat_widget_html() -> str:
    """
    Return the AI chat widget HTML, or an empty string if disabled/unavailable.

    The chat_widget module is optional. Importing it unconditionally at module
    load time meant the entire site generator crashed if that module was
    missing, even when ENABLE_AI_CHAT was False. This guards against that.
    """
    if not ENABLE_AI_CHAT:
        return ""
    try:
        from chat_widget import get_chat_widget_html as _get_chat_widget_html
        return _get_chat_widget_html()
    except ImportError:
        logger.warning("ENABLE_AI_CHAT is True but chat_widget module was not found. Skipping chat widget.")
        return ""

# Global variable for temp content
TEMP_CONTENT = ""



def generate_reading_notes():
    """Generate the running reading-notes / book log page."""
    notes = load_reading_notes()
    if not notes:
        return

    content = header_html("Reading Notes - " + BLOG_TITLE, "reading")
    content += """
<section class="hero" style="padding: 6rem 0 4rem;">
  <div class="container">
    <div class="hero-content">
      <p class="hero-label">Reading Log</p>
      <h1 class="hero-title" style="font-size: clamp(3rem, 5vw, 4rem);">
        Notes on What I've Been Reading
      </h1>
      <p class="hero-description" style="max-width: 48rem;">
        Short, running notes on books that gave me one good idea worth keeping —
        not full essays, just what stuck.
      </p>
      <p>note: As an Amazon Associate I earn from qualifying purchases.Thank you for your support.</p>
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="books-grid">
"""
    for note in notes:
        content += format_reading_note_card(note)
    content += """
    </div>
  </div>
</section>
"""
    content += footer_html()
    with open(OUTPUT_DIR / READING_FILE_HTML, "w", encoding="utf-8") as f:
        f.write(content)

def generate_post_pages(posts: List[Post], related_map: Dict[str, List[str]]):
    """Generate individual blog post pages."""
    global TEMP_CONTENT
    
    for post in posts:
        # Convert markdown to HTML
        html_body = markdown.markdown(post.body, extensions=['extra', 'codehilite'])
        
        html_body = process_youtube_embeds(html_body)

       
        
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
        TEMP_CONTENT += f"TITLE: {post.title}\nDATE: {post.date}\nCONTENT: {clean_text(post.body)}\n\n"





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
    content += f"""
<section class="section">
  <div class="container">
    <article class="post-content" style="max-width: 42rem;">
      
      <h2 style="font-size: 2.5rem; margin-bottom: 2rem; color: var(--color-charcoal);">Dear Curious Internet Stranger,</h2>
      
      <p style="margin-bottom: 2rem; font-size: 1.125rem; line-height: 1.8;">
        First, thank you for clicking "About" instead of immediately leaving. 
        That shows either genuine curiosity or excellent procrastination skills. 
        Either way, I respect it.
      </p>
      
      
      
      <p style="margin-bottom: 2rem; font-size: 1.125rem; line-height: 1.8;">
       I'm fascinated by one question:

How do we live well when certainty isn't an option? <br/><br/>

That's the thread running through everything I write.

Sometimes it looks like essays about love and loss. Sometimes it's money and the stories we tell ourselves about it. Sometimes it's parenting, technology, work, or the quiet assumptions that shape our days. Different subjects, same curiosity.
      </p>
      
      <p style="margin-bottom: 2rem; font-size: 1.125rem; line-height: 1.8;">
        Think of this space as what happens when 
        <a href="https://en.wikipedia.org/wiki/Seinfeld" target="_blank" rel="noopener noreferrer" 
           style="color: var(--color-rust); text-decoration: underline; font-weight: 500;">Seinfeld</a> 
        meets philosophy—observant, self-aware, mildly neurotic, and uncomfortably honest about the small stuff that turns out to be the big stuff: a leaking ceiling, a burnt piece of toast, a stranger on a train platform.
      </p>
      
     
      
      <p style="margin-bottom: 2rem; font-size: 1.125rem; line-height: 1.8;">
        I'm drawn to the space between certainty and probability, noise and meaning, information and wisdom. We spend a surprising amount of our lives trying to eliminate uncertainty, when perhaps the better question is how to live with it well.

Not because I'm particularly brave, but because pretending to have everything figured out is exhausting—and I've never met anyone who actually does.

 </p>

 <blockquote style="border-left: 4px solid var(--color-rust); padding-left: 1.5rem; margin: 2.5rem 0; font-style: italic; color: var(--color-slate); font-size: 1.25rem;">
        In a culture obsessed with certainty, I've made peace with Uncertainty. Mostly.
      </blockquote>

      <p style="margin-bottom: 2rem; font-size: 1.125rem; line-height: 1.8;">
It's less an obstacle than a traveling companion. Occasionally annoying. Often humbling. Best experienced with a sense of humor. And coffee. Definitely coffee.
</P

      
      
      
      <p style="margin-bottom: 2rem; font-size: 1.125rem; line-height: 1.8;">
        You'll find essays here that ramble a bit, the occasional poem when prose won't cut it, and observations about the things we usually ignore until they're suddenly the only things that matter.
      </p>
      
      <p style="margin-bottom: 2rem; font-size: 1.125rem; line-height: 1.8;">
        If you're the kind of person who reads the footnotes, questions the premise, and occasionally pauses mid-sentence to wonder if any of this means anything — well, you're in the right place.
      </p>
      
      <p style="margin-bottom: 3rem; font-size: 1.125rem; line-height: 1.8;">
        Thanks for stopping by. The asterisk is silent, but the questions are loud.
      </p>
      
      <div style="margin-top: 3rem; padding-top: 2rem; border-top: 2px solid var(--color-sand);">
        <p style="margin-bottom: 0.5rem; font-size: 1.125rem;">Warmly,</p>
        <p style="font-style: italic; font-size: 1.25rem; color: var(--color-charcoal); font-weight: 600;">
          Subu
        </p>
      </div>
      
      <div style="margin-top: 4rem; padding: 2.5rem; background: linear-gradient(135deg, white 0%, var(--color-cream) 100%); border: 2px solid var(--color-sand); border-left: 6px solid var(--color-rust); border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
        <h3 style="font-family: var(--font-serif); font-size: 2rem; margin-bottom: 1.5rem; color: var(--color-charcoal);">
          Want to Connect?
        </h3>
        
        <p style="margin-bottom: 2rem; font-size: 1.125rem; line-height: 1.7; color: var(--color-slate);">
          I'd love to hear from you. Questions, thoughts, disagreements, or just to say hello—
          <a href="{CONTACT_FILE}" style="color: var(--color-rust); text-decoration: underline; font-weight: 600; transition: color 0.3s;">drop me a line</a>.
        </p>
        
        <p style="font-size: 1.125rem; line-height: 1.7; color: var(--color-slate);">
          You can also find me sharing thoughts (280 characters at a time) 
          and occasional video essays on 
          <a href="{YOUTUBE_CHANNEL}" target="_blank" rel="noopener noreferrer" 
             style="color: var(--color-rust); text-decoration: underline; font-weight: 600; transition: color 0.3s;">YouTube</a> and 
          <a href="{INSTAGRAM_PROFILE}" target="_blank" rel="noopener noreferrer" 
             style="color: var(--color-rust); text-decoration: underline; font-weight: 600; transition: color 0.3s;">Instagram</a>.
        </p>
      </div>
      
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
      <h2 style="font-family: var(--font-serif); font-size: 2rem; margin-bottom: 1rem;">Email {show_logo(LOGO_PATH, 70)}</h2>
      <p style="color: var(--color-slate); margin-bottom: 2rem;">I typically respond within a 48 hours</p>
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


def generate_videos():
    """Generate videos page showing all videos."""
    videos = load_videos()
    
    if not videos:
        logger.info("No videos found, skipping videos page generation")
        return
    
    content = header_html("Videos - " + BLOG_TITLE, "videos")
    
    # Hero section
    content += """
<section class="hero" style="padding: 6rem 0 4rem;">
  <div class="container">
    <div class="hero-content">
      <p class="hero-label">Video Library</p>
      <h1 class="hero-title" style="font-size: clamp(3rem, 5vw, 4rem);">
        Watch & <span style="color: var(--color-rust); font-style: italic;">Learn</span>
      </h1>
      <p class="hero-description" style="max-width: 48rem;">
        Video essays, explanations, and explorations on the topics covered in the blog.
      </p>
    </div>
  </div>
</section>
"""
    
    # Videos grid
    content += """
<section class="section">
  <div class="container">
    <div class="card-grid">
"""
    
    for video in videos:
        video_id = video.get("video_id", "")
        title = escape(video.get("title", "Untitled Video"))
        article_link = video.get("article_link", "")

        article_html = ""
        if article_link:
            article_html = f'''
            <div style="margin-top: 1rem;">
              <a href="{escape(article_link)}" class="card-link">
                Read this Essay
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
                </svg>
              </a>
            </div>
            '''

        content += f"""
<article class="card">
  <h3 class="card-title" style="font-size: 1.5rem; margin-bottom: 1rem;">{title}</h3>
  {youtube_embed(video_id, title=title, css_class="youtube-embed")}
  {article_html}
</article>
"""
    
    content += """
    </div>
  </div>
</section>
"""
    
    content += footer_html()
    
    with open(OUTPUT_DIR / VIDEOS_FILE_HTML, "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info(f"Generated videos page with {len(videos)} videos")


def get_temp_content():
    """Return temporary content for debugging."""
    return TEMP_CONTENT

def generate_index(posts: List[Post], related_map: Dict):
    """
    Generate the homepage.

    Uses the same rich hero/glassmorphism visual language (pill badges,
    gradient title, glass stat cards, floating blobs) and the same card
    components (format_featured_card/format_card/format_book_card) as the
    rest of the site, instead of the ad hoc plain-list layout this used
    to have.
    """
    books = load_books(BOOKS_ON_HOMEPAGE)
    videos = load_videos()
    featured_video = next((v for v in videos if v.get("featured")), None)

    logger.info(f"Generating index page with {len(posts)} posts and {len(books)} books")

    # Generate individual post pages
    generate_post_pages(posts, related_map)

    content = header_html("Home - " + BLOG_TITLE, "home")

    # =========================
    # HERO
    # =========================
    num_categories = len(set(p.category for p in posts))
    content += f"""
<section class="hero">
  <div class="hero-bg-blob hero-bg-blob-1"></div>
  <div class="hero-bg-blob hero-bg-blob-2"></div>

  <div class="container">
    <div class="hero-content" style="text-align: center;">
      <div style="margin-bottom: 2rem;">
        {pill_badge("Welcome to " + BLOG_TITLE, "rust")}
      </div>

      <h1 class="hero-title hero-title-gradient" style="margin: 0 auto 1.5rem; text-align: center;">
        Essays on Life
      </h1>

      <p class="hero-subtitle" style="margin: 0 auto 1rem;">{escape(TAG_LINE)}</p>

      <div class="hero-cta" style="justify-content: center;">
        <a href="#featured" class="btn btn-primary">Explore Essays</a>
        <a href="{ABOUT_FILE}" class="btn btn-secondary">About the Author</a>
      </div>

      <div class="hero-stats" style="margin: 0 auto;">
        <div class="stat-card-glass accent-rust">
          <div class="stat-number">{len(posts)}+</div>
          <div class="stat-label">Essays Published</div>
        </div>
        <div class="stat-card-glass accent-sage">
          <div class="stat-number">{num_categories}</div>
          <div class="stat-label">Categories</div>
        </div>
        <div class="stat-card-glass accent-gold">
          <div class="stat-number">{len(books)}</div>
          <div class="stat-label">Books Written</div>
        </div>
      </div>
    </div>
  </div>
</section>
"""

    # =========================
    # FEATURED VIDEO (optional)
    # =========================
    if featured_video:
        video_title = escape(featured_video.get("title", "Featured Video"))
        article_link = featured_video.get("article_link", "")
        article_html = ""
        if article_link:
            article_html = f'<a href="{escape(article_link)}" class="card-link" style="justify-content: center; margin-top: 1rem;">Read the related article →</a>'

        content += f"""
<div class="divider">
  <div class="divider-line" style="background: var(--color-rust);"></div>
  <div class="divider-dot" style="background: var(--color-rust);"></div>
  <div class="divider-line" style="background: var(--color-rust);"></div>
</div>

<section class="section" style="background: white; padding: 4rem 0;">
  <div class="container" style="max-width: 56rem;">
    <div style="text-align: center; margin-bottom: 2rem;">
      <h2 class="section-title" style="font-size: 2.5rem;">{video_title}</h2>
      {article_html}
    </div>
    {youtube_embed(featured_video.get("video_id", ""), title=video_title)}
  </div>
</section>
"""

    # =========================
    # FEATURED ESSAYS
    # =========================
    featured_posts = [p for p in posts if p.featured][:4]
    if featured_posts:
        content += f"""
<section class="section" id="featured" style="background: linear-gradient(180deg, var(--color-cream) 0%, white 100%);">
  <div class="container">
    <div class="section-header section-header-centered">
      {pill_badge("Curated Reading", "rust")}
      <h2 class="section-title" style="margin-top: 1rem;">Featured Essays</h2>
      <p class="section-description section-description-centered">Recent explorations worth your time</p>
    </div>
    <div class="featured-grid">
"""
        content += format_featured_card(featured_posts[0])
        content += '<div style="display: flex; flex-direction: column; gap: 2rem;">'
        for post in featured_posts[1:]:
            content += format_card(post, is_small=True)
        content += "</div></div></div></section>"

    



    # =========================
    # ARCHIVE TEASER
    # =========================
    content += f"""
<section class="section" style="background: white;">
  <div class="container" style="max-width: 56rem; text-align: center;">
    <h2 class="section-title" style="font-size: 2rem;">Archive</h2>
    <p class="section-description section-description-centered" style="margin: 1rem auto 2rem;">
      A chronological index of essays, organized by year.
    </p>
    <a href="{ARCHIVES_FILE}" class="btn btn-secondary">Browse Index →</a>
  </div>
</section>
"""

    # AI Chat Widget (if enabled)
    content += get_chat_widget_html()

    content += footer_html()

    with open(OUTPUT_DIR / INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def generate_archives(posts: List[Post]):
    """Generate archives page with a magazine-style index, toggleable
    between grouping by year and grouping by category."""

    # Group posts by year
    archive_data = defaultdict(list)
    for post in posts:
        try:
            date_obj = datetime.strptime(post.date, "%Y-%m-%d")
            archive_data[date_obj.year].append(post)
        except:
            continue

    sorted_years = sorted(archive_data.keys(), reverse=True)

    # Group posts by category
    category_data = defaultdict(list)
    for post in posts:
        category_data[post.category].append(post)

    # Alphabetical, matching the order on the existing categories.html
    sorted_categories = sorted(category_data.keys())
    categories_meta = load_categories()

    # Same initial count for every group, year or category, so the page
    # reads consistently no matter which view you're in
    GROUP_PREVIEW_COUNT = POSTS_PER_CATEGORY_PAGE

    content = header_html("Archives - " + BLOG_TITLE, "archives")

    # HERO SECTION
    content += f"""
<section class="hero" style="padding: 6rem 0 4rem; background: linear-gradient(135deg, var(--color-cream) 0%, white 100%);">
  <div class="container">
    <div class="hero-content" style="text-align: center;">
      <div style="display: inline-block; padding: 0.5rem 1.5rem; background: rgba(184, 80, 62, 0.1); border: 2px solid var(--color-rust); border-radius: 50px; margin-bottom: 2rem;">
        <p class="hero-label" style="margin: 0; font-weight: 600;">Archive</p>
      </div>

      <h1 class="hero-title" style="font-size: clamp(3rem, 5vw, 4.5rem); margin-bottom: 1rem;">
        Every Essay, <span style="color: var(--color-rust); font-style: italic;">Organized</span>
      </h1>

      <p class="hero-description" style="max-width: 42rem; margin: 0 auto;">
        Explore {len(posts)} essays spanning {len(sorted_years)} years of writing
      </p>
    </div>
  </div>
</section>
"""

    # SECTION HEADER + TOGGLE TABS
    content += """
<section class="section" style="padding: 6rem 0;">
  <div class="container" style="max-width: 64rem;">

    <h2 style="font-size: 2rem; margin-bottom: 2.5rem; text-align: center; color: var(--color-charcoal); letter-spacing: 0.08em;">
      Archive Index
    </h2>

    <div style="display: flex; justify-content: center; gap: 0.75rem; margin-bottom: 4rem;">
      <button id="tab-year" onclick="showArchiveView('year')"
        style="padding: 0.6rem 1.75rem; border-radius: 50px; border: 2px solid var(--color-rust); background: var(--color-rust); color: white; font-family: var(--font-sans); font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase; cursor: pointer;">
        By year
      </button>
      <button id="tab-category" onclick="showArchiveView('category')"
        style="padding: 0.6rem 1.75rem; border-radius: 50px; border: 2px solid var(--color-rust); background: transparent; color: var(--color-rust); font-family: var(--font-sans); font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase; cursor: pointer;">
        By category
      </button>
    </div>
"""

    # BY YEAR VIEW
    content += """
    <div id="view-by-year">
"""

    for year in sorted_years:
        year_posts_sorted = sorted(archive_data[year], key=lambda x: x.date, reverse=True)

        content += f"""
    <div id="year-{year}" style="margin-bottom: 5rem; scroll-margin-top: 2rem;">

      <div style="margin-bottom: 2rem; display: flex; align-items: baseline; gap: 1.5rem;">
        <h3 style="font-size: 2rem; font-family: var(--font-serif); color: var(--color-rust); margin: 0;">
          {year}
        </h3>
        <div style="flex: 1; height: 1px; background: var(--color-sand);"></div>
        <span style="font-family: var(--font-sans); font-size: 0.9rem; color: var(--color-slate); letter-spacing: 0.1em;">
          {len(year_posts_sorted)} ESSAYS
        </span>
      </div>

      <div class="card-grid">
"""

        for idx, post in enumerate(year_posts_sorted):
            hidden_class = " hidden-post" if idx >= GROUP_PREVIEW_COUNT else ""
            content += f'<div class="card-wrapper{hidden_class}">'
            content += format_card(post)
            content += "</div>"

        content += """
      </div>
"""

        if len(year_posts_sorted) > GROUP_PREVIEW_COUNT:
            remaining = len(year_posts_sorted) - GROUP_PREVIEW_COUNT
            content += f"""
      <div style="text-align: center; margin-top: 2rem;">
        <button id="load-more-year-{year}" onclick="loadMoreGroup('year-{year}')" class="btn btn-secondary" style="cursor: pointer;">
          Load more ({remaining} remaining)
        </button>
      </div>
"""

        content += """
    </div>
"""

    content += """
    </div>
"""

    # BY CATEGORY VIEW
    content += """
    <div id="view-by-category" style="display: none;">
"""

    for category in sorted_categories:
        cat_posts_sorted = sorted(category_data[category], key=lambda x: x.date, reverse=True)
        cat_slug = slugify(category)
        category_info = categories_meta.get(category, {})
        description = category_info.get("description", f"Essays exploring {category.lower()}")

        content += f"""
    <div id="category-{cat_slug}" style="margin-bottom: 5rem; scroll-margin-top: 2rem;">

      <div style="margin-bottom: 0.75rem; display: flex; align-items: baseline; gap: 1.5rem;">
        <h3 style="font-size: 2rem; font-family: var(--font-serif); color: var(--color-rust); margin: 0;">
          {category}
        </h3>
        <div style="flex: 1; height: 1px; background: var(--color-sand);"></div>
        <span style="font-family: var(--font-sans); font-size: 0.9rem; color: var(--color-slate); letter-spacing: 0.1em;">
          {len(cat_posts_sorted)} ESSAYS
        </span>
      </div>

      <p style="margin: 0 0 2rem; font-family: var(--font-sans); color: var(--color-slate); max-width: 42rem;">
        {description}
      </p>

      <div class="card-grid">
"""

        for idx, post in enumerate(cat_posts_sorted):
            hidden_class = " hidden-post" if idx >= GROUP_PREVIEW_COUNT else ""
            content += f'<div class="card-wrapper{hidden_class}">'
            content += format_card(post)
            content += "</div>"

        content += """
      </div>
"""

        if len(cat_posts_sorted) > GROUP_PREVIEW_COUNT:
            remaining = len(cat_posts_sorted) - GROUP_PREVIEW_COUNT
            content += f"""
      <div style="text-align: center; margin-top: 2rem;">
        <button id="load-more-category-{cat_slug}" onclick="loadMoreGroup('category-{cat_slug}')" class="btn btn-secondary" style="cursor: pointer;">
          Load more ({remaining} remaining)
        </button>
      </div>
"""

        content += """
    </div>
"""

    content += """
    </div>

  </div>
</section>
"""

    # TOGGLE + DEEP-LINK SCRIPT
    content += """
<script>
function showArchiveView(view) {
  var yearView = document.getElementById('view-by-year');
  var catView = document.getElementById('view-by-category');
  var yearTab = document.getElementById('tab-year');
  var catTab = document.getElementById('tab-category');

  if (view === 'category') {
    yearView.style.display = 'none';
    catView.style.display = 'block';
    catTab.style.background = 'var(--color-rust)';
    catTab.style.color = 'white';
    yearTab.style.background = 'transparent';
    yearTab.style.color = 'var(--color-rust)';
  } else {
    catView.style.display = 'none';
    yearView.style.display = 'block';
    yearTab.style.background = 'var(--color-rust)';
    yearTab.style.color = 'white';
    catTab.style.background = 'transparent';
    catTab.style.color = 'var(--color-rust)';
  }
}

function loadMoreGroup(groupId) {
  var container = document.getElementById(groupId);
  var hidden = container.querySelectorAll('.hidden-post');
  var count = 0;
  hidden.forEach(function (post) {
    if (count < 6) {
      post.classList.remove('hidden-post');
      post.style.display = 'block';
      count++;
    }
  });
  var remaining = container.querySelectorAll('.hidden-post').length;
  var button = document.getElementById('load-more-' + groupId);
  if (remaining === 0) {
    button.style.display = 'none';
  } else {
    button.innerHTML = 'Load more (' + remaining + ' remaining)';
  }
}

(function () {
  var hash = window.location.hash;
  if (hash.indexOf('category') !== -1) {
    showArchiveView('category');
    var target = document.getElementById(hash.substring(1));
    if (target) {
      setTimeout(function () { target.scrollIntoView(); }, 0);
    }
  }
})();
</script>
"""

    content += footer_html()

    with open(OUTPUT_DIR / ARCHIVES_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(
        f"Generated archive with {len(posts)} posts across "
        f"{len(sorted_years)} years and {len(sorted_categories)} categories"
    )



