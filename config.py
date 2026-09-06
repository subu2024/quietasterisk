"""
Configuration module for the Quiet Asterisk blog generator.
Contains all constants and settings used throughout the application.
"""

from pathlib import Path

# ==========================================================
# Site Configuration
# ==========================================================

BLOG_TITLE = "quiet asterisk"
TAG_LINE = "Writing that slows thinking just enough to notice what uncertainty is trying to teach us"
COPYRIGHT = "© 2026 pathway llc. All rights reserved."
CONTACT_EMAIL = "hello@quietasterisk.com"
YOUTUBE_CHANNEL = "https://www.youtube.com/@quietasterisk"
INSTAGRAM_PROFILE = "https://www.instagram.com/quiet.asterisk/"
LOGO_PATH = "./images/logo.png"  # Relative path to logo in output


# ==========================================================
# File Paths
# ==========================================================
INPUT_DIR = Path("./posts")
OUTPUT_DIR = Path("./dist")
IMAGE_DIR = OUTPUT_DIR / "images"
DOWNLOADS_DIR = Path("./downloads")  # Source directory for downloadable files
OUTPUT_DOWNLOADS_DIR = OUTPUT_DIR / "downloads"  # Destination in output

# Data files
BOOKS_FILE = Path("./books.json")
CATEGORIES_FILE_JSON = Path("./categories.json")
VIDEOS_FILE = Path("./videos.json")  
READING_NOTES_FILE = Path("./reading_notes.json")

# Output HTML files
INDEX_FILE = "index.html"
ABOUT_FILE = "about.html"
CATEGORIES_FILE = "categories.html"
BOOKS_FILE_HTML = "books.html"
CONTACT_FILE = "contact.html"
VIDEOS_FILE_HTML = "videos.html"  
ARCHIVES_FILE = "archives.html" 
READING_FILE_HTML = "reading.html"

# AI Chat Module
# Optional feature: requires a separate `chat_widget.py` module (not part of
# this repo) that exports get_chat_widget_html(). If that module isn't
# present, generators.py falls back to skipping the widget rather than
# crashing, even when this flag is True.
import os

ENABLE_AI_CHAT = False  # Set to False to disable
AI_CHAT_TITLE = "Ask Devi"
AI_CHAT_PLACEHOLDER = "Ask a question about uncertainty in your life ..."
AWS_API_ENDPOINT = os.environ.get("BLOG_CHAT_API_ENDPOINT", "")
AWS_API_TOKEN = os.environ.get("BLOG_CHAT_API_TOKEN", "")  # never hardcode secrets here

# ==========================================================
# Newsletter Signup (Resend)
# ==========================================================
# Renders an email-capture section on the homepage (templates.newsletter_html).
#
# IMPORTANT — architecture: Resend's Audiences API requires a secret API key
# (`Authorization: Bearer re_xxx`), which can never be embedded in a static
# page — anyone could read it from view-source and use it to send mail or
# dump your subscriber list. So the homepage form does NOT call Resend
# directly. Instead it POSTs {"email": "..."} as JSON to your own small
# serverless proxy (see newsletter_lambda/handler.py in this project), and
# that proxy — which holds RESEND_API_KEY and RESEND_AUDIENCE_ID in its own
# environment, not here — calls Resend on the visitor's behalf.
#
# NEWSLETTER_API_ENDPOINT is the PUBLIC URL of that proxy (an AWS Lambda
# Function URL / API Gateway route, matching the AWS_API_ENDPOINT pattern
# above). It is safe to expose; it does no harm if someone finds it, since
# it can only add an email to your audience, not read your Resend key.
NEWSLETTER_ENABLED = True
NEWSLETTER_API_ENDPOINT = os.environ.get("BLOG_NEWSLETTER_API_ENDPOINT", "")
NEWSLETTER_HEADING = "New essays land here first"
NEWSLETTER_SUBHEAD = (
    "One email, roughly once a week. No noise, no growth-hacking — "
    "just the next thing I'm working through."
)

# ==========================================================
# Content Settings
# ==========================================================
MIN_SNIPPET_LEN = 38
SIMILARITY_THRESHOLD = 0.17
POSTS_PER_CATEGORY_PAGE = 3 # Number of posts to show before "Load More"
BOOKS_ON_HOMEPAGE = 2  # Number of books to show on homepage

# ==========================================================
# Temporary Files
# ==========================================================
TEMP_CONTENT_FILE = "temp_content.txt"
