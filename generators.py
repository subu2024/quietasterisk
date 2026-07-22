"""
Page generators for the blog.
Each function generates a specific page type.
"""

import re
import logging
import markdown
from typing import List, Dict



from config import (
    BLOG_TITLE, TAG_LINE, COPYRIGHT, CONTACT_EMAIL, YOUTUBE_CHANNEL, VIDEOS_FILE_HTML,
    INDEX_FILE, ABOUT_FILE, CATEGORIES_FILE, BOOKS_FILE_HTML, CONTACT_FILE, INSTAGRAM_PROFILE,
    OUTPUT_DIR, POSTS_PER_CATEGORY_PAGE, BOOKS_ON_HOMEPAGE, ARCHIVES_FILE, LOGO_PATH,
    READING_FILE_HTML  # add this
)




from collections import defaultdict
from datetime import datetime

from chat_widget import get_chat_widget_html


from models import Post
from templates import header_html, footer_html
from cards import format_card, format_featured_card, format_book_card, format_reading_note_card
from utils import copy_image, load_books, load_categories, slugify, load_videos, show_logo, load_reading_notes

#from parser import YouTubeExtension
from parser import process_youtube_embeds
logger = logging.getLogger("BlogGen")

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
        title = video.get("title", "Untitled Video")
        article_link = video.get("article_link", "")
        
        article_html = ""
        if article_link:
            article_html = f'''
            <div style="margin-top: 1rem;">
              <a href="{article_link}" class="card-link">
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
  <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 4px; margin-bottom: 1rem;">
    <iframe 
      style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
      src="https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
      title="{title}"
      frameborder="0" 
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
      referrerpolicy="strict-origin-when-cross-origin"
      allowfullscreen>
    </iframe>
  </div>
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


def generate_archives_v2(posts: List[Post]):
    """Generate archives page with magazine-style year index layout."""
    from collections import defaultdict
    from datetime import datetime

    # Group posts by year only
    archive_data = defaultdict(list)

    for post in posts:
        try:
            date_obj = datetime.strptime(post.date, "%Y-%m-%d")
            year = date_obj.year
            archive_data[year].append(post)
        except:
            continue

    # Sort years descending
    sorted_years = sorted(archive_data.keys(), reverse=True)

    

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



    # MAGAZINE INDEX ARCHIVE
    content += """
<section class="section" style="padding: 6rem 0;">
  <div class="container" style="max-width: 64rem;">
    
    <h2 style="font-size: 2rem; margin-bottom: 4rem; text-align: center; color: var(--color-charcoal); letter-spacing: 0.08em;">
      Archive Index
    </h2>
"""

    for year in sorted_years:
        year_posts = archive_data[year]
        year_posts_sorted = sorted(year_posts, key=lambda x: x.date, reverse=True)

        content += f"""
    <div style="margin-bottom: 5rem;">
      
      <!-- YEAR HEADER -->
      <div style="margin-bottom: 2rem; display: flex; align-items: baseline; gap: 1.5rem;">
        
        <h3 style="font-size: 3rem; font-family: var(--font-serif); color: var(--color-rust); margin: 0;">
          {year}
        </h3>

        <div style="flex: 1; height: 1px; background: var(--color-sand);"></div>

        <span style="font-family: var(--font-sans); font-size: 0.9rem; color: var(--color-slate); letter-spacing: 0.1em;">
          {len(year_posts)} ESSAYS
        </span>

      </div>

      <!-- POSTS LIST -->
      <div style="display: flex; flex-direction: column;">
"""

        for post in year_posts_sorted:
            content += f"""
        <div style="display: flex; justify-content: space-between; align-items: baseline; gap: 2rem; padding: 1rem 0; border-bottom: 1px solid rgba(0,0,0,0.06);">

          <!-- TITLE + META -->
          <div style="flex: 1;">
            
            <a href="{post.slug}"
               style="font-size: 1.25rem; font-family: var(--font-serif); color: var(--color-charcoal); text-decoration: none;"
               onmouseover="this.style.color='var(--color-rust)'"
               onmouseout="this.style.color='var(--color-charcoal)'">
              {post.title}
            </a>

            <div style="margin-top: 0.25rem; font-family: var(--font-sans); font-size: 0.8rem; color: var(--color-slate); letter-spacing: 0.08em; text-transform: uppercase;">
              {post.category} · {post.reading_time}
            </div>

          </div>

          <!-- READ LINK -->
          <a href="{post.slug}"
             style="font-family: var(--font-sans); font-size: 0.85rem; color: var(--color-rust); text-decoration: none; white-space: nowrap;"
             onmouseover="this.style.transform='translateX(3px)'"
             onmouseout="this.style.transform='translateX(0)'">
            Read →
          </a>

        </div>
"""

        content += """
      </div>
    </div>
"""

    content += """
  </div>
</section>
"""

    content += footer_html()

    with open(OUTPUT_DIR / ARCHIVES_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Generated magazine-style archive with {len(posts)} posts across {len(sorted_years)} years")
       
# sorts by year and month, descending - not used any more, but kept for reference
def generate_archives_old(posts: List[Post]):
    """Generate archives page with accordion-style year/month navigation."""
    from collections import defaultdict
    from datetime import datetime
    
    # Group posts by year and month
    archive_data = defaultdict(lambda: defaultdict(list))
    
    for post in posts:
        try:
            date_obj = datetime.strptime(post.date, "%Y-%m-%d")
            year = date_obj.year
            month = date_obj.strftime("%B")  # Full month name
            archive_data[year][month].append(post)
        except:
            continue
    
    # Sort years descending
    sorted_years = sorted(archive_data.keys(), reverse=True)
    
    # Get latest post
    latest_post = posts[0] if posts else None
    
    content = header_html("Archives - " + BLOG_TITLE, "archives")
    
    # Hero section
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
    
    # Latest post section
    if latest_post:
        content += f"""
<section class="section" style="padding: 4rem 0; background: white;">
  <div class="container" style="max-width: 48rem;">
    <h2 style="font-size: 1.5rem; margin-bottom: 2rem; color: var(--color-slate); text-align: center; text-transform: uppercase; letter-spacing: 0.1em; font-family: var(--font-sans); font-weight: 500;">
      Latest Essay
    </h2>
    <article style="background: var(--color-cream); border-left: 4px solid var(--color-rust); padding: 2rem; border-radius: 8px;">
      <div style="margin-bottom: 1rem;">
        <span style="font-family: var(--font-sans); font-size: 0.875rem; color: var(--color-rust); text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600;">{latest_post.category}</span>
        <span style="margin: 0 0.5rem; color: var(--color-slate);">•</span>
        <span style="font-family: var(--font-sans); font-size: 0.875rem; color: var(--color-slate);">{latest_post.formatted_date}</span>
      </div>
      <h3 style="font-size: 2rem; margin-bottom: 1rem; color: var(--color-charcoal);">
        <a href="{latest_post.slug}" style="color: inherit; text-decoration: none; transition: color 0.3s;" onmouseover="this.style.color='var(--color-rust)'" onmouseout="this.style.color='var(--color-charcoal)'">{latest_post.title}</a>
      </h3>
      <p style="color: var(--color-slate); margin-bottom: 1.5rem; line-height: 1.7; font-size: 1.125rem;">{latest_post.excerpt}</p>
      <a href="{latest_post.slug}" class="btn btn-primary" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem;">
        Read Essay
        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
        </svg>
      </a>
    </article>
  </div>
</section>
"""
    
    # Archive accordion
    content += """
<section class="section" style="padding: 4rem 0;">
  <div class="container" style="max-width: 56rem;">
    <h2 style="font-size: 2rem; margin-bottom: 3rem; text-align: center; color: var(--color-charcoal);">Browse by Date</h2>
    <div class="archive-timeline">
"""
    
    for year in sorted_years:
        months = archive_data[year]
        # Sort months chronologically
        month_order = ["January", "February", "March", "April", "May", "June", 
                       "July", "August", "September", "October", "November", "December"]
        sorted_months = sorted(months.keys(), key=lambda x: month_order.index(x), reverse=True)
        
        total_posts_year = sum(len(months[m]) for m in months)
        
        content += f"""
      <div class="year-block" style="margin-bottom: 2rem;">
        <button onclick="toggleYear('year-{year}')" style="width: 100%; background: linear-gradient(135deg, var(--color-rust), var(--color-terracotta)); color: white; border: none; padding: 1.5rem 2rem; border-radius: 8px; cursor: pointer; font-size: 1.5rem; font-weight: 700; font-family: var(--font-serif); display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 12px rgba(184, 80, 62, 0.2); transition: transform 0.3s, box-shadow 0.3s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(184, 80, 62, 0.3)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(184, 80, 62, 0.2)'">
          <span>{year}</span>
          <span style="font-family: var(--font-sans); font-size: 1rem; font-weight: 500; opacity: 0.9;">{total_posts_year} essays</span>
        </button>
        <div id="year-{year}" style="display: none; margin-top: 1rem; padding-left: 1rem;">
"""
        
        for month in sorted_months:
            month_posts = months[month]
            content += f"""
          <div class="month-block" style="margin-bottom: 1.5rem;">
            <button onclick="toggleMonth('month-{year}-{month}')" style="width: 100%; background: white; border: 2px solid var(--color-sand); padding: 1rem 1.5rem; border-radius: 6px; cursor: pointer; font-size: 1.125rem; font-weight: 600; font-family: var(--font-sans); display: flex; justify-content: space-between; align-items: center; color: var(--color-charcoal); transition: all 0.3s;" onmouseover="this.style.borderColor='var(--color-rust)'; this.style.background='var(--color-cream)'" onmouseout="this.style.borderColor='var(--color-sand)'; this.style.background='white'">
              <span>{month}</span>
              <span style="font-size: 0.875rem; color: var(--color-slate);">{len(month_posts)} essays</span>
            </button>
            <div id="month-{year}-{month}" style="display: none; margin-top: 1rem; padding-left: 1rem;">
"""
            
            for post in month_posts:
                content += f"""
              <article style="background: var(--color-cream); border-left: 3px solid var(--color-sage); padding: 1.5rem; border-radius: 4px; margin-bottom: 1rem;">
                <div style="margin-bottom: 0.5rem;">
                  <span style="font-family: var(--font-sans); font-size: 0.75rem; color: var(--color-sage); text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600;">{post.category}</span>
                  <span style="margin: 0 0.5rem; color: var(--color-slate);">•</span>
                  <span style="font-family: var(--font-sans); font-size: 0.75rem; color: var(--color-slate);">{post.reading_time}</span>
                </div>
                <h4 style="font-size: 1.25rem; margin-bottom: 0.5rem;">
                  <a href="{post.slug}" style="color: var(--color-charcoal); text-decoration: none; transition: color 0.3s;" onmouseover="this.style.color='var(--color-rust)'" onmouseout="this.style.color='var(--color-charcoal)'">{post.title}</a>
                </h4>
                <p style="color: var(--color-slate); font-size: 0.9375rem; line-height: 1.6; margin-bottom: 1rem;">{post.excerpt}</p>
                <a href="{post.slug}" style="color: var(--color-rust); text-decoration: none; font-family: var(--font-sans); font-size: 0.875rem; font-weight: 600;">Read more →</a>
              </article>
"""
            
            content += """
            </div>
          </div>
"""
        
        content += """
        </div>
      </div>
"""
    
    content += """
    </div>
  </div>
</section>

<script>
function toggleYear(id) {
  const element = document.getElementById(id);
  if (element.style.display === 'none' || element.style.display === '') {
    element.style.display = 'block';
  } else {
    element.style.display = 'none';
  }
}

function toggleMonth(id) {
  const element = document.getElementById(id);
  if (element.style.display === 'none' || element.style.display === '') {
    element.style.display = 'block';
  } else {
    element.style.display = 'none';
  }
}
</script>
"""
    
    content += footer_html()
    
    with open(OUTPUT_DIR / ARCHIVES_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info(f"Generated archives page with {len(posts)} posts across {len(sorted_years)} years")

def get_temp_content():
    """Return temporary content for debugging."""
    return TEMP_CONTENT

def generate_index(posts: List[Post], related_map: Dict):
    """Generate homepage with magazine-style editorial layout."""
    books = load_books(3)

    logger.info(f"Generating index page with {len(posts)} posts and {len(books)} books")

    # Generate individual post pages
    generate_post_pages(posts, related_map)

    content = header_html("Home - " + BLOG_TITLE, "home")

    # =========================
    # HERO
    # =========================
    content += f"""
<section class="hero" style="padding: 10rem 0 6rem; background: var(--color-cream); text-align: center;">
  <div class="container" style="max-width: 52rem;">
    
    <p style="font-family: var(--font-sans); letter-spacing: 0.2em; text-transform: uppercase; font-size: 0.8rem; color: var(--color-slate); margin-bottom: 2rem;">
      {BLOG_TITLE}
    </p>

    <h1 style="font-size: clamp(3rem, 6vw, 5rem); font-family: var(--font-serif); line-height: 1.2; margin-bottom: 2rem; color: var(--color-charcoal);">
      Essays on uncertainty, attention, and what it means to be human
    </h1>

    <p style="font-size: 1.25rem; color: var(--color-slate); line-height: 1.8; max-width: 40rem; margin: 0 auto;">
      {TAG_LINE}
    </p>

  </div>
</section>
"""

    # =========================
    # FEATURED POSTS
    # =========================
    featured_posts = [p for p in posts if p.featured][:3]

    if featured_posts:
        content += """
<section class="section" style="padding: 6rem 0; background: white;">
  <div class="container" style="max-width: 64rem;">

    <div style="margin-bottom: 4rem; text-align: center;">
      <h2 style="font-size: 2.5rem; font-family: var(--font-serif); color: var(--color-charcoal);">
        Current Essays
      </h2>
      <div style="width: 80px; height: 2px; background: var(--color-rust); margin: 0.5rem auto 0;"></div>
    </div>

    <div style="display: flex; flex-direction: column; gap: 2rem;">
"""

        for post in featured_posts:
            content += f"""
      <div style="padding: 1.5rem 0; border-bottom: 1px solid rgba(0,0,0,0.08);">

        <a href="{post.slug}"
           style="font-size: 1.5rem; font-family: var(--font-serif); color: var(--color-charcoal); text-decoration: none;">
          {post.title}
        </a>

        <div style="margin-top: 0.3rem; font-family: var(--font-sans); font-size: 0.8rem; color: var(--color-slate); text-transform: uppercase;">
          {post.category} · {post.reading_time}
        </div>

        <p style="margin-top: 0.75rem; color: var(--color-slate); line-height: 1.7;">
          {post.excerpt}
        </p>

        <a href="{post.slug}"
           style="display: inline-block; margin-top: 0.75rem; font-size: 0.85rem; color: var(--color-rust); text-decoration: none;">
          Read →
        </a>

      </div>
"""

        content += """
    </div>
  </div>
</section>
"""

    # =========================
    # BOOKS
    # =========================
    if books:
        content += """
<section class="section" style="padding: 5rem 0; background: var(--color-cream);">
  <div class="container" style="max-width: 56rem; text-align: center;">

    <h2 style="font-size: 2rem; font-family: var(--font-serif); margin-bottom: 2rem; color: var(--color-charcoal);">
      Books
    </h2>

    <div style="display: flex; flex-direction: column; gap: 1rem;">
"""

        for book in books:
            link_url = book.get("link", "")

            content += f"""
      <div style="padding: 1rem 0; border-bottom: 1px solid rgba(0,0,0,0.08);">
        
        <div style="font-family: var(--font-serif); font-size: 1.25rem; color: var(--color-charcoal);">
          {book.get("title", "")}
        </div>
"""

            if link_url:
                content += f"""
        <div style="margin-top: 0.5rem;">
          <a href="{link_url}" target="_blank" rel="noopener noreferrer"
             style="font-size: 0.875rem; color: var(--color-rust); text-decoration: none;">
            Buy / Download →
          </a>
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

    # =========================
    # ARCHIVE LINK
    # =========================
    content += """
<section class="section" style="padding: 6rem 0; background: white;">
  <div class="container" style="max-width: 56rem; text-align: center;">

    <h2 style="font-size: 2rem; font-family: var(--font-serif); color: var(--color-charcoal);">
      Archive
    </h2>

    <p style="color: var(--color-slate); margin: 1rem auto 2rem; max-width: 40rem;">
      A chronological index of essays, organized by year.
    </p>

    <a href="archives.html"
       style="font-size: 0.9rem; color: var(--color-rust); text-decoration: none; text-transform: uppercase;">
      Browse Index →
    </a>

  </div>
</section>
"""

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



def generate_index_old(posts: List[Post], related_map: Dict):
    """Generate homepage with hero, books, featured and recent posts."""
    books = load_books()
    
    # Generate individual post pages
    generate_post_pages(posts, related_map)

    content = header_html("Home - " + BLOG_TITLE, "home")

    # Hero Section - Modern with gradient and glassmorphism
    content += f"""
<section class="hero" style="background: linear-gradient(135deg, #FAF8F3 0%, #E8E3D8 50%, #F5E6D3 100%); position: relative; overflow: hidden; padding: 8rem 0 6rem;">
  <!-- Animated background blobs -->
  <div style="position: absolute; top: -10%; right: -5%; width: 500px; height: 500px; background: radial-gradient(circle, rgba(184, 80, 62, 0.15), transparent); border-radius: 50%; filter: blur(60px); animation: float 20s infinite ease-in-out;"></div>
  <div style="position: absolute; bottom: -10%; left: -5%; width: 600px; height: 600px; background: radial-gradient(circle, rgba(139, 155, 126, 0.15), transparent); border-radius: 50%; filter: blur(60px); animation: float 25s infinite ease-in-out reverse;"></div>
  <div style="position: absolute; top: 40%; right: 30%; width: 300px; height: 300px; background: radial-gradient(circle, rgba(201, 167, 103, 0.1), transparent); border-radius: 50%; filter: blur(50px); animation: float 15s infinite ease-in-out;"></div>
  
  <div class="container" style="position: relative; z-index: 10;">
    <div class="hero-content" style="text-align: center;">
      <div style="display: inline-block; padding: 0.5rem 1.5rem; background: rgba(184, 80, 62, 0.1); border: 2px solid var(--color-rust); border-radius: 50px; margin-bottom: 2rem; backdrop-filter: blur(10px);">
        <p class="hero-label" style="margin: 0; font-weight: 600;">Welcome to Quiet Asterisk</p>
      </div>
      
      <h1 style="font-size: clamp(3.5rem, 8vw, 7rem); font-weight: 800; line-height: 1.1; margin-bottom: 1.5rem; background: linear-gradient(135deg, var(--color-charcoal) 0%, var(--color-rust) 50%, var(--color-gold) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
        Essays on Life
      </h1>
      
      <p style="font-size: clamp(1.25rem, 2.5vw, 1.75rem); color: var(--color-slate); font-weight: 400; max-width: 42rem; margin: 0 auto 1rem; line-height: 1.6;">
        Explore <span style="color: var(--color-rust); font-weight: 600;">uncertainty</span>. 
        <span style="color: var(--color-sage); font-weight: 600;">Notice</span>  
        <span style="color: var(--color-gold); font-weight: 600;">what others</span> overlook.
      </p>
      
      <p style="font-size: 1.125rem; color: var(--color-slate); max-width: 36rem; margin: 0 auto 3rem; line-height: 1.7;">
       Essays, books, and videos on systems, ideas, and the hidden details shaping how we think and live.
      </p>
      
      <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; margin-bottom: 4rem;">
        <a href="#featured" class="btn btn-primary" style="padding: 1.25rem 2.5rem; font-size: 1.125rem; box-shadow: 0 8px 20px rgba(184, 80, 62, 0.3); transform: translateY(0); transition: all 0.3s;" onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 12px 28px rgba(184, 80, 62, 0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 8px 20px rgba(184, 80, 62, 0.3)'">
          Explore Essays
        </a>
        <a href="{ABOUT_FILE}" class="btn btn-secondary" style="padding: 1.25rem 2.5rem; font-size: 1.125rem; backdrop-filter: blur(10px); background: rgba(255, 255, 255, 0.5);">
          About the Author
        </a>
      </div>
      
      <!-- Stats with modern cards -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; max-width: 56rem; margin: 0 auto;">
        <div style="background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); border: 2px solid rgba(184, 80, 62, 0.2); border-radius: 16px; padding: 2rem; box-shadow: 0 8px 24px rgba(0,0,0,0.08); transition: transform 0.3s, box-shadow 0.3s;" onmouseover="this.style.transform='translateY(-8px)'; this.style.boxShadow='0 12px 32px rgba(0,0,0,0.12)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 8px 24px rgba(0,0,0,0.08)'">
          <div style="font-size: 3rem; font-weight: 800; background: linear-gradient(135deg, var(--color-rust), var(--color-terracotta)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.5rem;">{len(posts)}+</div>
          <div style="font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--color-slate); font-weight: 600;">Essays Published</div>
        </div>
        <div style="background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); border: 2px solid rgba(139, 155, 126, 0.2); border-radius: 16px; padding: 2rem; box-shadow: 0 8px 24px rgba(0,0,0,0.08); transition: transform 0.3s, box-shadow 0.3s;" onmouseover="this.style.transform='translateY(-8px)'; this.style.boxShadow='0 12px 32px rgba(0,0,0,0.12)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 8px 24px rgba(0,0,0,0.08)'">
          <div style="font-size: 3rem; font-weight: 800; background: linear-gradient(135deg, var(--color-sage), #6B8B5E); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.5rem;">{len(set(p.category for p in posts))}</div>
          <div style="font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--color-slate); font-weight: 600;">Categories</div>
        </div>
        <div style="background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); border: 2px solid rgba(201, 167, 103, 0.2); border-radius: 16px; padding: 2rem; box-shadow: 0 8px 24px rgba(0,0,0,0.08); transition: transform 0.3s, box-shadow 0.3s;" onmouseover="this.style.transform='translateY(-8px)'; this.style.boxShadow='0 12px 32px rgba(0,0,0,0.12)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 8px 24px rgba(0,0,0,0.08)'">
          <div style="font-size: 3rem; font-weight: 800; background: linear-gradient(135deg, var(--color-gold), #B8954F); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.5rem;">{len(books)}</div>
          <div style="font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--color-slate); font-weight: 600;">Books Written</div>
        </div>
      </div>
    </div>
  </div>
</section>

<style>
@keyframes float {{
  0%, 100% {{ transform: translate(0, 0) rotate(0deg); }}
  33% {{ transform: translate(30px, -30px) rotate(5deg); }}
  66% {{ transform: translate(-20px, 20px) rotate(-5deg); }}
}}
</style>
"""

    # Featured Video Section
    videos = load_videos()
    featured_video = next((v for v in videos if v.get("featured")), None)
    
    if featured_video:
        video_id = featured_video.get("video_id", "")
        video_title = featured_video.get("title", "Featured Video")
        article_link = featured_video.get("article_link", "")
        
        article_html = ""
        if article_link:
            article_html = f'<a href="{article_link}" style="color: var(--color-rust); text-decoration: underline; font-size: 1rem;">Read the related article →</a>'
        
        content += f"""
<div class="divider">
  <div class="divider-line" style="background: var(--color-rust);"></div>
  <div class="divider-dot" style="background: var(--color-rust);"></div>
  <div class="divider-line" style="background: var(--color-rust);"></div>
</div>

<section class="section" style="background: white; padding: 4rem 0;">
  <div class="container" style="max-width: 56rem;">
    <div style="text-align: center; margin-bottom: 2rem;">
      <h2 style="font-family: var(--font-serif); font-size: 2.5rem; margin-bottom: 1rem; color: var(--color-charcoal);">
        {video_title}
      </h2>
      {article_html}
    </div>
    <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
      <iframe 
        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
        src="https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
        title="{video_title}"
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
        referrerpolicy="strict-origin-when-cross-origin"
        allowfullscreen>
      </iframe>
    </div>
  </div>
</section>
"""
    
    # Featured Essays - Modern section
    featured_posts = [p for p in posts if p.featured][:4]
    if featured_posts:
        content += f"""
<section class="section" id="featured" style="background: linear-gradient(180deg, var(--color-cream) 0%, white 100%); padding: 6rem 0;">
  <div class="container">
    <div style="text-align: center; margin-bottom: 4rem;">
      <div style="display: inline-block; padding: 0.5rem 1.5rem; background: rgba(184, 80, 62, 0.1); border: 2px solid var(--color-rust); border-radius: 50px; margin-bottom: 1rem;">
        <span style="font-family: var(--font-sans); font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.15em; color: var(--color-rust); font-weight: 600;">Curated Reading</span>
      </div>
      <h2 style="font-size: clamp(2.5rem, 5vw, 3.5rem); font-weight: 700; margin-bottom: 1rem; color: var(--color-charcoal);">Featured Essays</h2>
      <p style="font-size: 1.25rem; color: var(--color-slate); max-width: 36rem; margin: 0 auto 2rem;">Recent explorations worth your time</p>
      <div style="width: 80px; height: 4px; background: linear-gradient(90deg, transparent, var(--color-rust), transparent); margin: 0 auto; border-radius: 2px;"></div>
    </div>
    <div class="featured-grid">
"""
        content += format_featured_card(featured_posts[0])
        content += '<div style="display: flex; flex-direction: column; gap: 2rem;">'
        for post in featured_posts[1:]:
            content += format_card(post, is_small=True)
        content += '</div></div></div></section>'

    # Recent Posts - Modern section
    recent_posts = [p for p in posts if not p.featured][:6]
    if recent_posts:
        content += f"""
<section class="section" style="padding: 6rem 0;">
  <div class="container">
    <div style="text-align: center; margin-bottom: 4rem;">
      <div style="display: inline-block; padding: 0.5rem 1.5rem; background: rgba(139, 155, 126, 0.1); border: 2px solid var(--color-sage); border-radius: 50px; margin-bottom: 1rem;">
        <span style="font-family: var(--font-sans); font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.15em; color: var(--color-sage); font-weight: 600;">Latest Thoughts</span>
      </div>
      <h2 style="font-size: clamp(2.5rem, 5vw, 3.5rem); font-weight: 700; margin-bottom: 1rem; color: var(--color-charcoal);">Recent Essays</h2>
      <p style="font-size: 1.25rem; color: var(--color-slate);">Fresh perspectives and explorations</p>
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

    # AI Chat Widget (if enabled)
    content += get_chat_widget_html()
    
    content += footer_html()
    with open(OUTPUT_DIR / INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(content)