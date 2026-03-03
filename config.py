"""
Configuration module for the Quiet Asterisk blog generator.
Contains all constants and settings used throughout the application.
"""

from pathlib import Path

# ==========================================================
# Site Configuration
# ==========================================================
BLOG_TITLE = "quiet asterisk"
TAG_LINE = "On chance, meaning, and the quiet details"
COPYRIGHT = "© 2026 pathway llc. All rights reserved."
CONTACT_EMAIL = "hello@quietasterisk.com"

# ==========================================================
# File Paths
# ==========================================================
INPUT_DIR = Path("./posts")
OUTPUT_DIR = Path("./dist")
IMAGE_DIR = OUTPUT_DIR / "images"

# Data files
BOOKS_FILE = Path("./books.json")
CATEGORIES_FILE_JSON = Path("./categories.json")

# Output HTML files
INDEX_FILE = "index.html"
ABOUT_FILE = "about.html"
CATEGORIES_FILE = "categories.html"
BOOKS_FILE_HTML = "books.html"
CONTACT_FILE = "contact.html"

# ==========================================================
# Content Settings
# ==========================================================
MIN_SNIPPET_LEN = 38
SIMILARITY_THRESHOLD = 0.15
POSTS_PER_CATEGORY_PAGE = 10  # Number of posts to show before "Load More"
BOOKS_ON_HOMEPAGE = 2  # Number of books to show on homepage

# ==========================================================
# Temporary Files
# ==========================================================
TEMP_CONTENT_FILE = "temp_content.txt"
