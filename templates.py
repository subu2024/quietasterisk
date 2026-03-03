"""
HTML template functions for generating pages.
"""

from config import (
    BLOG_TITLE, TAG_LINE, COPYRIGHT, CONTACT_EMAIL,
    INDEX_FILE, ABOUT_FILE, CATEGORIES_FILE, BOOKS_FILE_HTML, CONTACT_FILE
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
<header class="header">
  <div class="container">
    <div class="header-content">
      <a href="{INDEX_FILE}" class="logo">{BLOG_TITLE}<span class="logo-asterisk">*</span></a>
      <nav class="nav">
        <a href="{INDEX_FILE}" class="nav-link {active_classes['home']}">Essays</a>
        <a href="{BOOKS_FILE_HTML}" class="nav-link {active_classes['books']}">Books</a>
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
          <a href="{CATEGORIES_FILE}" class="footer-link">Categories</a>
          <a href="{ABOUT_FILE}" class="footer-link">About</a>
          <a href="{CONTACT_FILE}" class="footer-link">Contact</a>
        </nav>
      </div>
      <div>
        <h4 class="footer-section-title">Connect</h4>
        <p style="color: var(--color-sand); margin-bottom: 1rem;">Get in touch</p>
        <a href="mailto:{CONTACT_EMAIL}" class="footer-link" style="display: block; margin-bottom: 0.5rem;">{CONTACT_EMAIL}</a>
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
