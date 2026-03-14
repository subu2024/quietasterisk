"""
HTML template functions for generating pages.
"""

from config import (
    BLOG_TITLE, TAG_LINE, COPYRIGHT, CONTACT_EMAIL, YOUTUBE_CHANNEL,
    INDEX_FILE, ABOUT_FILE, CATEGORIES_FILE, BOOKS_FILE_HTML, CONTACT_FILE, VIDEOS_FILE_HTML
)
from styles import get_modern_styles


def header_html(title: str, active_page: str = "home") -> str:
    """
    Generate HTML header with navigation.
    
    Args:
        title: Page title for <title> tag
        active_page: Which nav item is active ("home", "books", "categories", "about", "contact")
        
    Returns:
        HTML string for header
    """
    active_classes = {
        "home": "active" if active_page == "home" else "",
        "books": "active" if active_page == "books" else "",
        "videos": "active" if active_page == "videos" else "",  # Add this
        "categories": "active" if active_page == "categories" else "",
        "about": "active" if active_page == "about" else "",
        "contact": "active" if active_page == "contact" else "",
    }
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{get_modern_styles()}</style>
</head>
<body>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-Z65VG31B7Q"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag() {{ window.dataLayer.push(arguments); }}
  gtag('js', new Date());
  gtag('config', 'G-Z65VG31B7Q', {{ page_path: window.location.pathname }});
</script>

<header class="header">
  <div class="container">
    <div class="header-content">
      <a href="{INDEX_FILE}" class="logo">{BLOG_TITLE}<span class="logo-asterisk">*</span></a>
      <nav class="nav">
        <a href="{INDEX_FILE}" class="nav-link {active_classes['home']}">Essays</a>
        <a href="{BOOKS_FILE_HTML}" class="nav-link {active_classes['books']}">Books</a>
        <a href="{VIDEOS_FILE_HTML}" class="nav-link {active_classes['videos']}">Videos</a>
        <a href="{CATEGORIES_FILE}" class="nav-link {active_classes['categories']}">Categories</a>
        <a href="{ABOUT_FILE}" class="nav-link {active_classes['about']}">About</a>
        <a href="{CONTACT_FILE}" class="nav-link {active_classes['contact']}">Contact</a>
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
        <a href="{INDEX_FILE}" class="logo" style="color: var(--color-cream);">{BLOG_TITLE}<span class="logo-asterisk">*</span></a>
        <p style="margin-top: 1rem; color: var(--color-sand);">{TAG_LINE}</p>
      </div>
      <div>
        <h4 class="footer-section-title">Explore</h4>
        <nav class="footer-nav">
          <a href="{INDEX_FILE}" class="footer-link">Essays</a>
          <a href="{BOOKS_FILE_HTML}" class="footer-link">Books</a>
          <a href="{VIDEOS_FILE_HTML}" class="footer-link">Videos</a>
          <a href="{CATEGORIES_FILE}" class="footer-link">Categories</a>
          <a href="{ABOUT_FILE}" class="footer-link">About</a>
          <a href="{CONTACT_FILE}" class="footer-link">Contact</a>
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