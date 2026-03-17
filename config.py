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
COPYRIGHT = "© 2026 pathway llc. All rights reserved. v1.0.06"
CONTACT_EMAIL = "hello@quietasterisk.com"
YOUTUBE_CHANNEL = "https://www.youtube.com/@quietasterisk"


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

# Output HTML files
INDEX_FILE = "index.html"
ABOUT_FILE = "about.html"
CATEGORIES_FILE = "categories.html"
BOOKS_FILE_HTML = "books.html"
CONTACT_FILE = "contact.html"
VIDEOS_FILE_HTML = "videos.html"  

# AI Chat Module
ENABLE_AI_CHAT = False  # Set to False to disable
AI_CHAT_TITLE = "Ask Devi"
AI_CHAT_PLACEHOLDER = "Ask a question about uncertainity in your life ..."
AWS_API_ENDPOINT = "https://your-api-gateway-url.execute-api.region.amazonaws.com/prod/chat"
AWS_API_TOKEN = "your-secret-token-here"  # Your AWS API secret token

# ==========================================================
# Content Settings
# ==========================================================
MIN_SNIPPET_LEN = 38
SIMILARITY_THRESHOLD = 0.16
POSTS_PER_CATEGORY_PAGE = 10  # Number of posts to show before "Load More"
BOOKS_ON_HOMEPAGE = 2  # Number of books to show on homepage

# ==========================================================
# Temporary Files
# ==========================================================
TEMP_CONTENT_FILE = "temp_content.txt"
