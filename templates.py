"""
HTML template functions for generating pages.
"""

import logging
import json
from html import escape
from typing import List

from config import (
    BLOG_TITLE, TAG_LINE, COPYRIGHT, CONTACT_EMAIL, YOUTUBE_CHANNEL, LOGO_PATH, INSTAGRAM_PROFILE,
    INDEX_FILE, ABOUT_FILE, CATEGORIES_FILE, BOOKS_FILE_HTML, CONTACT_FILE, VIDEOS_FILE_HTML, ARCHIVES_FILE,
    NEWSLETTER_ENABLED, NEWSLETTER_API_ENDPOINT, NEWSLETTER_HEADING, NEWSLETTER_SUBHEAD
)
from styles import get_modern_styles

from utils import show_logo, slugify

logger = logging.getLogger("BlogGen")


def pill_badge(text: str, accent: str = "rust") -> str:
    """
    Return a small uppercase pill badge, e.g. for section eyebrows.

    Args:
        text: Badge text
        accent: One of "rust", "sage", "gold" (see .pill-badge-* in styles.py)

    Returns:
        HTML string for the badge
    """
    return f'<span class="pill-badge pill-badge-{accent}">{text}</span>'


def newsletter_html() -> str:
    """
    Return the email-signup section shown on the homepage.

    Submits via JS fetch() as JSON, not a plain HTML form POST — Resend's
    Audiences API needs a JSON body and a secret bearer key, so the actual
    Resend call has to happen server-side in your own proxy (see
    newsletter_lambda/handler.py). This section only ever talks to that
    proxy's public URL (NEWSLETTER_API_ENDPOINT), never to Resend directly.

    Gracefully degrades: if NEWSLETTER_API_ENDPOINT isn't configured, the
    section renders with the input/button disabled and a note in place of
    a live form — better than posting to nowhere and giving the visitor a
    silent failure — and the generator logs a warning. Same graceful-degrade
    posture as generators.get_chat_widget_html for a missing dependency.

    Returns:
        HTML string for the newsletter section, or "" if disabled.
    """
    if not NEWSLETTER_ENABLED:
        return ""

    endpoint = NEWSLETTER_API_ENDPOINT
    if not endpoint:
        logger.warning(
            "NEWSLETTER_API_ENDPOINT is not set (env var BLOG_NEWSLETTER_API_ENDPOINT) "
            "— the newsletter section will render in a disabled state until you deploy "
            "the proxy in newsletter_lambda/ and point this at its URL."
        )
        return f"""
<section class="section newsletter-section">
  <div class="container newsletter-grid">
    <div>
      <h2 class="section-title" style="font-size: 2rem; margin-bottom: 0.75rem;">{escape(NEWSLETTER_HEADING)}</h2>
      <p class="section-description">{escape(NEWSLETTER_SUBHEAD)}</p>
    </div>
    <div>
      <form class="newsletter-form">
        <input type="email" class="newsletter-input" placeholder="you@email.com"
               aria-label="Email address" disabled>
        <button type="button" class="btn btn-primary" disabled>Subscribe</button>
      </form>
      <p class="newsletter-fine">Signup is being set up — check back soon.</p>
    </div>
  </div>
</section>
"""

    return f"""
<section class="section newsletter-section">
  <div class="container newsletter-grid">
    <div>
      <h2 class="section-title" style="font-size: 2rem; margin-bottom: 0.75rem;">{escape(NEWSLETTER_HEADING)}</h2>
      <p class="section-description">{escape(NEWSLETTER_SUBHEAD)}</p>
    </div>
    <div>
      <form class="newsletter-form" id="newsletter-form" novalidate>
        <input type="email" name="email" id="newsletter-email" class="newsletter-input"
               placeholder="you@email.com" aria-label="Email address" required>
        <button type="submit" class="btn btn-primary" id="newsletter-submit">Subscribe</button>
      </form>
      <p class="newsletter-fine" id="newsletter-status" aria-live="polite">Unsubscribe any time. I mean it.</p>
    </div>
  </div>
</section>
<script>
(function () {{
  var form = document.getElementById('newsletter-form');
  if (!form) return;
  var endpoint = {json.dumps(endpoint)};
  var input = document.getElementById('newsletter-email');
  var button = document.getElementById('newsletter-submit');
  var status = document.getElementById('newsletter-status');
  var defaultStatus = status.textContent;

  form.addEventListener('submit', function (event) {{
    event.preventDefault();
    var email = input.value.trim();
    if (!email) return;

    button.disabled = true;
    button.textContent = 'Subscribing…';
    status.textContent = defaultStatus;

    fetch(endpoint, {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ email: email }})
    }})
      .then(function (response) {{
        if (!response.ok) throw new Error('Request failed');
        return response.json().catch(function () {{ return {{}}; }});
      }})
      .then(function () {{
        form.reset();
        status.textContent = "You're in — thanks for subscribing.";
        button.textContent = 'Subscribed';
      }})
      .catch(function () {{
        status.textContent = 'Something went wrong — please try again in a moment.';
        button.disabled = false;
        button.textContent = 'Subscribe';
      }});
  }});
}})();
</script>
"""


def topic_chips_html(categories: List[str], css_class: str = "topic-chip") -> str:
    """Return category links for use in a topic-navigation layout.

    The shared helper keeps category URL construction in one place while
    allowing the homepage and the standalone topic strip to use their own
    visual treatment.
    """
    if not categories:
        return ""

    chips = "".join(
        f'<a href="category-{slugify(category)}.html" class="{css_class}">{escape(category)}</a>'
        for category in sorted(categories)
    )
    return chips + f'<a href="{CATEGORIES_FILE}" class="{css_class}">All topics →</a>'


def topics_nav_html(categories: List[str]) -> str:
    """Return the standalone row of topic chips used on legacy layouts.

    Gives the homepage a way to browse by theme instead of only by recency.
    This is a second entry point into the same category-<slug>.html pages
    that generators.generate_categories() already builds — not a new page
    type, so there's nothing else to keep in sync.

    Args:
        categories: Distinct category names present in the published posts.

    Returns:
        HTML string for the topics strip, or "" if there are no categories.
    """
    if not categories:
        return ""

    return f"""
<section class="topics-nav">
  <div class="container topics-nav-inner">
    <span class="topics-nav-label">Browse by theme</span>
    {topic_chips_html(categories)}
  </div>
</section>
"""


def header_html(title: str, active_page: str = "home") -> str:
    """
    Generate HTML header with navigation.
    
    Args:
        title: Page title for <title> tag
        active_page: Which nav item is active ("home", "books", "categories", "about", "contact")
        
    Returns:
        HTML string for header
    """
    def active(page: str) -> str:
        return "active" if active_page == page else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{get_modern_styles()}</style>
</head>
<body>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-H4FF5RJXE7"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag() {{ window.dataLayer.push(arguments); }}
  gtag('js', new Date());
  gtag('config', 'G-H4FF5RJXE7', {{ page_path: window.location.pathname }});
</script>

<header class="header">
  <div class="container">
    <div class="header-content">
      <a href="{INDEX_FILE}" class="logo">{BLOG_TITLE}{show_logo(LOGO_PATH, 70)}</a>
      <nav class="nav">
        <a href="{INDEX_FILE}" class="nav-link {active('home')}">Essays</a>
        <a href="{BOOKS_FILE_HTML}" class="nav-link {active('books')}">Books</a>
        <a href="{VIDEOS_FILE_HTML}" class="nav-link {active('videos')}">Videos</a>
        <a href="{ARCHIVES_FILE}" class="nav-link {active('archives')}">Archives</a>
        <a href="{ABOUT_FILE}" class="nav-link {active('about')}">About</a>
      </nav>
    </div>
  </div>
</header>

<main>
"""


def footer_html() -> str:
    """Generate HTML footer with navigation and contact info."""
    return f"""
</main>
<footer class="footer">
  <div class="container">
    <div class="footer-content">
      <div>
        <a href="{INDEX_FILE}" class="logo" style="color: var(--color-cream);">{BLOG_TITLE}{show_logo(LOGO_PATH, 20)}</a>
        <p style="margin-top: 1rem; color: var(--color-sand);">{TAG_LINE}</p>
      </div>
      <div>
        <h4 class="footer-section-title">Explore</h4>
        <nav class="footer-nav">
          <a href="{INDEX_FILE}" class="footer-link">Essays</a>
          <a href="{BOOKS_FILE_HTML}" class="footer-link">Books</a>
          <a href="{VIDEOS_FILE_HTML}" class="footer-link">Videos</a>
          <a href="{BOOKS_FILE_HTML}#reading-notes" class="footer-link">Reading Notes</a>
          <a href="{ARCHIVES_FILE}" class="footer-link">Archives</a>
          <a href="{ABOUT_FILE}" class="footer-link">About</a>
        </nav>
      </div>
      <div>
        <h4 class="footer-section-title">Connect</h4>
        <p style="color: var(--color-sand); margin-bottom: 1rem;">Get in touch</p>
        <a href="mailto:{CONTACT_EMAIL}" class="footer-link" style="display: block; margin-bottom: 0.5rem;">{CONTACT_EMAIL}</a>
        <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
          <a href="{YOUTUBE_CHANNEL}" target="_blank" rel="noopener noreferrer" class="footer-link" aria-label="YouTube Channel" title="YouTube Channel">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
              <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
            </svg>{YOUTUBE_CHANNEL}
          </a>
        </div>
        <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
  <a href="{INSTAGRAM_PROFILE}" target="_blank" rel="noopener noreferrer" class="footer-link" aria-label="Instagram Profile" title="Instagram Profile">
    <svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
      <path d="M7.75 2C4.574 2 2 4.574 2 7.75v8.5C2 19.426 4.574 22 7.75 22h8.5C19.426 22 22 19.426 22 16.25v-8.5C22 4.574 19.426 2 16.25 2h-8.5zm0 2h8.5C18.455 4 20 5.545 20 7.75v8.5c0 2.205-1.545 3.75-3.75 3.75h-8.5C5.545 20 4 18.455 4 16.25v-8.5C4 5.545 5.545 4 7.75 4zm8.75 1.5a1.25 1.25 0 1 0 0 2.5 1.25 1.25 0 0 0 0-2.5zM12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10zm0 2a3 3 0 1 1 0 6 3 3 0 0 1 0-6z"/>
    </svg>{INSTAGRAM_PROFILE}
  </a>
</div>
      </div>
    </div>
    <div class="footer-bottom">
      <p>{COPYRIGHT}</p>
    </div>
  </div>
</footer>
</body>
</html>
"""
