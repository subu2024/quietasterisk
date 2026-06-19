"""
HTML template functions for generating pages.
"""

from config import (
    BLOG_TITLE, TAG_LINE, COPYRIGHT, CONTACT_EMAIL, YOUTUBE_CHANNEL, LOGO_PATH, INSTAGRAM_PROFILE,
    INDEX_FILE, ABOUT_FILE, CATEGORIES_FILE, BOOKS_FILE_HTML, CONTACT_FILE, VIDEOS_FILE_HTML, ARCHIVES_FILE
)
from styles import get_modern_styles

from utils import show_logo


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
        "videos": "active" if active_page == "videos" else "", 
        "archives": "active" if active_page == "archives" else "",
        "about": "active" if active_page == "about" else "",
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
        <a href="{INDEX_FILE}" class="nav-link {active_classes['home']}">Essays</a>
        <a href="{BOOKS_FILE_HTML}" class="nav-link {active_classes['books']}">Books</a>
        <a href="{VIDEOS_FILE_HTML}" class="nav-link {active_classes['videos']}">Videos</a>
       
        <a href="{ARCHIVES_FILE}" class="nav-link {active_classes['archives']}">Archives</a>
        <a href="{ABOUT_FILE}" class="nav-link {active_classes['about']}">About</a>
        
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