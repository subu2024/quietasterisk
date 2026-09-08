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
    OUTPUT_DIR, POSTS_PER_CATEGORY_PAGE, BOOKS_ON_HOMEPAGE, ARCHIVES_FILE, SITE_URL,
    READING_FILE_HTML  # add this
)




from collections import defaultdict
from datetime import datetime

from config import ENABLE_AI_CHAT
from models import Post
from templates import header_html, footer_html, newsletter_html, topic_chips_html
from cards import format_card, format_featured_card, format_book_card, format_reading_note_card
from utils import copy_image, load_books, load_categories, slugify, load_videos, load_reading_notes, youtube_embed, arrow_icon
from parser import process_youtube_embeds

logger = logging.getLogger("BlogGen")

# Global variable for temp content
TEMP_CONTENT = ""

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


def generate_reading_notes_redirect():
    """
    Write a small redirect page at the old reading.html URL.

    Reading Notes now lives as a section on the merged Books page
    (see generate_books). This keeps any bookmarks, backlinks, or search
    results pointing at the old standalone URL from turning into a 404.
    """
    target = f"{BOOKS_FILE_HTML}#reading-notes"
    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="https://www.quietasterisk.com/{target}">
<title>Reading Notes - {BLOG_TITLE}</title>
</head>
<body>
<p>Reading Notes has moved to the <a href="{target}">Books page</a>.</p>
</body>
</html>
"""
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
        content = header_html(post.title, "home")
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
    """
    Generate the merged Books page: "Books I've Written" stacked above
    "What I've Been Reading" (the former Reading Notes page).

    Design notes:
    - Both sections are always visible/stacked, not toggled — they're
      different content types (authored vs. curated/affiliate), so hiding
      either behind a click would bury the wrong thing for some visitors.
    - The pill nav at the top borrows its visual language from the
      Archives page's "By year / By category" tabs, but behaves as plain
      anchor jumps rather than a JS show/hide toggle, since nothing here
      needs to be hidden.
    - When a title appears in both books.json and reading_notes.json
      (e.g. "Space Between Knowing"), each card gets a small cross-link
      to the other entry instead of the two sitting as disconnected
      duplicates.
    """
    books = load_books()
    notes = load_reading_notes()

    if not books and not notes:
        return

    book_titles = {b.get("title", "").strip().lower() for b in books}
    note_titles = {n.get("title", "").strip().lower() for n in notes}

    content = header_html("Books - " + BLOG_TITLE, "books")
    content += """
<section class="hero" style="padding: 6rem 0 4rem;">
  <div class="container">
    <div class="hero-content">
      <p class="hero-label">Books</p>
      <h1 class="hero-title" style="font-size: clamp(3rem, 5vw, 4rem);">
        What I've Written, What I've Read
      </h1>
      <p class="hero-description" style="max-width: 48rem;">
        My own published works and ongoing projects, alongside short running notes
        on other books that gave me one good idea worth keeping.
      </p>
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
"""

    if books and notes:
        content += """
    <div class="jump-nav">
      <a href="#my-books" class="jump-pill ">My Books</a>
      <a href="#reading-notes" class="jump-pill jump-pill-filled">What I'm Reading</a>
    </div>
"""

    if notes:
        content += """
    <div id="reading-notes" class="books-section-heading">
      <h2>What I've Been Reading</h2>
      <div class="books-section-rule"></div>
    </div>
    <p class="section-description" style="margin-bottom: 1rem;">
      Short, running notes on books that gave me one good idea worth keeping —
      not full essays, just what stuck.
    </p>
    <p class="affiliate-disclosure">
      As an Amazon Associate I earn from qualifying purchases. Thank you for your support.
    </p>
    <div class="books-grid">
"""
        for note in notes:
            cross_link_html = ""
            title_key = note.get("title", "").strip().lower()
            if title_key in book_titles:
                anchor = slugify(note.get("title", ""))
                cross_link_html = (
                    f'<a href="#book-{anchor}" class="book-cross-link">'
                    f"This one's actually mine — see the full book →</a>"
                )
            content += format_reading_note_card(note, cross_link_html=cross_link_html)
        content += """
    </div>
"""

    if books:
        content += """
    <div id="my-books" class="books-section-heading">
      <h2>Books I've Written</h2>
      <div class="books-section-rule"></div>
    </div>
    <div class="books-grid" style="margin-bottom: 5rem;">
"""
        for book in books:
            cross_link_html = ""
            title_key = book.get("title", "").strip().lower()
            if title_key in note_titles:
                anchor = slugify(book.get("title", ""))
                cross_link_html = (
                    f'<a href="#note-{anchor}" class="book-cross-link">'
                    f"I wrote a reading note on this one too →</a>"
                )
            content += format_book_card(book, show_full_description=True, cross_link_html=cross_link_html)
        content += """
    </div>
"""



    content += """
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
          {arrow_icon()}
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


def generate_sitemap(posts: List[Post], categories: List[str]):
    """
    Generate sitemap.xml listing every public page on the site.

    Search engines discover pages by crawling links, but category pages
    (category-<slug>.html) aren't in the main nav — they're only reachable
    via the homepage's topic pills or a direct link — so listing them
    explicitly here is the difference between them getting indexed
    promptly and not at all. Same idea for the reading-notes redirect,
    which is deliberately excluded since it isn't a real destination page.

    Args:
        posts: List of Post objects (used for post URLs + lastmod dates)
        categories: Distinct category names present in the published posts
    """
    static_pages = [
        INDEX_FILE, ABOUT_FILE, CONTACT_FILE, BOOKS_FILE_HTML,
        VIDEOS_FILE_HTML, ARCHIVES_FILE, CATEGORIES_FILE,
    ]

    # (relative URL, lastmod-or-None) pairs
    urls = [(page, None) for page in static_pages]
    urls += [(f"category-{slugify(category)}.html", None) for category in sorted(categories)]

    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for post in posts:
        lastmod = post.date if date_pattern.match(post.date or "") else None
        urls.append((post.slug, lastmod))

    entries = []
    for path, lastmod in urls:
        loc = escape(f"{SITE_URL}/{path}")
        lastmod_xml = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
        entries.append(f"  <url><loc>{loc}</loc>{lastmod_xml}</url>")

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries) +
        "\n</urlset>\n"
    )

    with open(OUTPUT_DIR / "sitemap.xml", "w", encoding="utf-8") as f:
        f.write(xml)

    logger.info(f"Generated sitemap.xml with {len(urls)} URLs")


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
    <article class="post-content letter">

      <h2 class="letter-heading">Dear Curious Internet Stranger,</h2>

      <p>
        First, thank you for clicking "About" instead of immediately leaving.
        That shows either genuine curiosity or excellent procrastination skills.
        Either way, I respect it.
      </p>

      <p>
        I'm fascinated by one question: how do we live well when certainty isn't an option?
      </p>

      <p>
        That's the thread running through everything I write. Sometimes it looks like
        essays about love and loss. Sometimes it's money and the stories we tell ourselves
        about it. Sometimes it's parenting, technology, work, or the quiet assumptions that
        shape our days. Different subjects, same curiosity.
      </p>

      <p>
        Think of this space as what happens when
        <a href="https://en.wikipedia.org/wiki/Seinfeld" target="_blank" rel="noopener noreferrer" class="text-link">Seinfeld</a>
        meets philosophy—observant, self-aware, mildly neurotic, and uncomfortably honest
        about the small stuff that turns out to be the big stuff: a leaking ceiling, a
        burnt piece of toast, a stranger on a train platform.
      </p>

      <p>
        I'm drawn to the space between certainty and probability, noise and meaning,
        information and wisdom. We spend a surprising amount of our lives trying to
        eliminate uncertainty, when perhaps the better question is how to live with it well.
      </p>

      <p>
        Not because I'm particularly brave, but because pretending to have everything
        figured out is exhausting—and I've never met anyone who actually does.
      </p>

      <blockquote>
        In a culture obsessed with certainty, I've made peace with Uncertainty. Mostly.
      </blockquote>

      <p>
        It's less an obstacle than a traveling companion. Occasionally annoying. Often
        humbling. Best experienced with a sense of humor. And coffee. Definitely coffee.
      </p>

      <p>
        You'll find essays here that ramble a bit, the occasional poem when prose won't
        cut it, and observations about the things we usually ignore until they're
        suddenly the only things that matter.
      </p>

      <p>
        If you're the kind of person who reads the footnotes, questions the premise, and
        occasionally pauses mid-sentence to wonder if any of this means anything — well,
        you're in the right place.
      </p>

      <p>
        Thanks for stopping by. The asterisk is silent, but the questions are loud.
      </p>

      <div class="letter-signoff">
        <p style="margin-bottom: 0.5rem;">Warmly,</p>
        <p class="name">Subu</p>
      </div>

      <div class="letter-callout">
        <h3>Want to Connect?</h3>
        <p>
          I'd love to hear from you. Questions, thoughts, disagreements, or just to say
          hello—<a href="{CONTACT_FILE}" class="text-link">drop me a line</a>.
        </p>
        <p>
          You can also find me sharing thoughts (280 characters at a time) and occasional
          video essays on
          <a href="{YOUTUBE_CHANNEL}" target="_blank" rel="noopener noreferrer" class="text-link">YouTube</a> and
          <a href="{INSTAGRAM_PROFILE}" target="_blank" rel="noopener noreferrer" class="text-link">Instagram</a>.
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
        Let's <span class="hero-title-accent">Connect</span>
      </h1>
      <p class="hero-description" style="max-width: 48rem;">
        Whether you have thoughts on an essay, questions about a book, or just want to say hello—I'd love to hear from you.
      </p>
    </div>
  </div>
</section>
<section class="section">
  <div class="container" style="max-width: 48rem;">
    <div class="contact-card">
      <div class="contact-icon">
        <svg width="40" height="40" fill="none" stroke="white" viewBox="0 0 24 24" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
      </div>
      <h2 style="font-family: var(--font-serif); font-size: 2rem; margin-bottom: 1rem;">Email</h2>
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
        Watch & <span class="hero-title-accent">Learn</span>
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
                {arrow_icon()}
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
    """Generate the editorial, quiet-asterisk-inspired homepage."""
    books = load_books(BOOKS_ON_HOMEPAGE)
    videos = load_videos()
    featured_video = next((v for v in videos if v.get("featured")), None)
    categories_present = sorted(set(p.category for p in posts))

    logger.info(f"Generating index page with {len(posts)} posts and {len(books)} books")

    content = header_html("Home - " + BLOG_TITLE, "home")
    content += """
<div class="quiet-home">
  <section class="qa-hero">
    <div class="wrap">
      <div>
        <h1>Essays on life, written from inside the uncertainty.</h1>
        <p class="qa-sub">{tagline}</p>
        <div class="qa-actions">
          <a class="qa-button" href="#featured">Start reading</a>
          <a class="qa-ghost" href="{about_file}">About the author →</a>
        </div>
      </div>
      <div class="qa-asterisk" aria-hidden="true">
        <svg viewBox="0 0 200 200" fill="none"><g stroke="#211F1D" stroke-width="2.5" stroke-linecap="round"><line x1="100" y1="20" x2="100" y2="180"/><line x1="30" y1="60" x2="170" y2="140"/><line x1="170" y1="60" x2="30" y2="140"/></g><circle cx="100" cy="100" r="6" fill="#A5732E"/></svg>
      </div>
    </div>
  </section>
  <div class="qa-strip"><div class="wrap"><span><strong>{post_count} {post_word}.</strong> {book_count} {book_word}. One long argument with certainty.</span><span>Writing from the uncertainty</span></div></div>
  <section class="qa-topics"><div class="wrap"><span class="qa-topic-label">Browse by theme</span>{topics}</div></section>
""".format(
        tagline=escape(TAG_LINE),
        about_file=ABOUT_FILE,
        post_count=len(posts),
        post_word="essay" if len(posts) == 1 else "essays",
        book_count=len(books),
        book_word="book" if len(books) == 1 else "books",
        topics=topic_chips_html(categories_present, "qa-topic"),
    )

    featured_posts = [post for post in posts if post.featured][:4]
    if featured_posts:
        content += """
  <section class="qa-featured" id="featured"><div class="wrap">
    <div class="qa-section-head"><h2>Recent essays</h2><a class="qa-see-all" href="{archive}">Browse the archive →</a></div>
    <div class="qa-featured-grid"><div class="qa-lead">{lead}</div><div class="qa-list">{rest}</div></div>
  </div></section>
""".format(
            archive=ARCHIVES_FILE,
            lead=format_featured_card(featured_posts[0]),
            rest="".join(format_card(post, is_small=True) for post in featured_posts[1:]),
        )

    if featured_video:
        video_title = escape(featured_video.get("title", "Featured video"))
        content += f'''<section class="qa-featured"><div class="wrap"><div class="qa-section-head"><h2>{video_title}</h2></div>{youtube_embed(featured_video.get("video_id", ""), title=video_title)}</div></section>'''

    # Keep the project's live signup integration instead of replacing it with
    # a decorative form from the reference file.
    content += '<div class="qa-newsletter">' + newsletter_html() + '</div>'
    content += f'''<section class="qa-about"><div class="wrap"><div class="qa-avatar" aria-hidden="true"></div><p>Written by {escape(BLOG_TITLE)} — fascinated by one question: how do we live well when certainty isn't an option?</p><a class="qa-about-link" href="{ABOUT_FILE}">Meet the author →</a></div></section>
  <section class="qa-archive"><div class="wrap"><h2>Archive</h2><p>A chronological index of essays, organized by year.</p><a class="qa-button" href="{ARCHIVES_FILE}">Browse the archive →</a></div></section>
</div>'''

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
<section class="hero" style="padding: 6rem 0 4rem;">
  <div class="container">
    <div class="hero-content" style="text-align: center;">
      <div style="display: inline-block; padding: 0.5rem 1.5rem; background: rgba(165, 115, 46, 0.1); border: 1px solid var(--color-rust); border-radius: var(--radius); margin-bottom: 2rem;">
        <p class="hero-label" style="margin: 0; font-weight: 600;">Archive</p>
      </div>

      <h1 class="hero-title" style="font-size: clamp(3rem, 5vw, 4.5rem); margin-bottom: 1rem;">
        Every Essay, <span class="hero-title-accent">Organized</span>
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
        style="padding: 0.6rem 1.75rem; border-radius: var(--radius); border: 1px solid var(--color-rust); background: var(--color-rust); color: white; font-family: var(--font-sans); font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase; cursor: pointer;">
        By year
      </button>
      <button id="tab-category" onclick="showArchiveView('category')"
        style="padding: 0.6rem 1.75rem; border-radius: var(--radius); border: 1px solid var(--color-rust); background: transparent; color: var(--color-rust); font-family: var(--font-sans); font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase; cursor: pointer;">
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

