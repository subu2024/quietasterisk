"""
Configuration module for the Quiet Asterisk blog generator.
Contains all constants and settings used throughout the application.
"""

import os
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

# The site's public URL, with no trailing slash. Used to build the absolute
# <loc> links in sitemap.xml — search engines need full URLs there, not
# relative paths. Update this (or set BLOG_SITE_URL) before deploying.
SITE_URL = os.environ.get("BLOG_SITE_URL", "https://www.quietasterisk.com").rstrip("/")

# ==========================================================
# Typography
# ==========================================================
# The whole site pulls its fonts from these three values (see
# styles.get_modern_styles), so changing the site's typeface is a matter of
# editing this block only — no need to touch styles.py or hunt for a
# hardcoded @import elsewhere.
#
# GOOGLE_FONTS_URL is loaded via @import at the top of the stylesheet.
# FONT_SERIF / FONT_SANS become the --font-serif / --font-sans CSS custom
# properties used throughout styles.py; keep a generic fallback (serif /
# sans-serif) at the end of each stack in case the Google Fonts request
# fails or is blocked.
GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600"
    "&family=Inter:wght@400;500;600&display=swap"
)
FONT_SERIF = "'Fraunces', Georgia, serif"
FONT_SANS = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"


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
# The old "Archives" page is now the "Essays" page. ESSAYS_FILE is the real
# page; ARCHIVES_FILE is kept only so generators.generate_archives_redirect()
# can leave a redirect at the old URL (bookmarks, backlinks, search results).
ESSAYS_FILE = "essays.html"
ARCHIVES_FILE = "archives.html"
READING_FILE_HTML = "reading.html"
SERIES_FILE = "series.html"  # the series chapter list (see "The Series" below)

# AI Chat Module
# Optional feature: requires a separate `chat_widget.py` module (not part of
# this repo) that exports get_chat_widget_html(). If that module isn't
# present, generators.py falls back to skipping the widget rather than
# crashing, even when this flag is True.
#
# IMPORTANT — architecture: this widget's JS runs in every visitor's
# browser, so anything in that JS is public, view-source data — the same
# constraint documented for the newsletter integration above. That means
# AWS_API_ENDPOINT must NOT require a bearer token/API key to answer a
# request; there is no secret that can survive being shipped to the client.
# If the Lambda behind this endpoint needs protecting (rate limiting, abuse
# prevention), do it server-side — Origin checks, a WAF rule, or API
# Gateway throttling — the same way newsletter_lambda/handler.py keeps its
# Resend key out of the static page entirely 
ENABLE_AI_CHAT = False  # Set to False to disable
AI_CHAT_TITLE = "Ask Devi"
AI_CHAT_PLACEHOLDER = "Ask a question about uncertainty in your life ..."
AWS_API_ENDPOINT = os.environ.get("BLOG_CHAT_API_ENDPOINT", "")

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
SIMILARITY_THRESHOLD = 0.17
POSTS_PER_CATEGORY_PAGE = 3 # Number of posts to show before "Load More"
HOME_ESSAYS_COUNT = 3  # Number of recent essays shown on the homepage

# ==========================================================
# The Series (homepage feature + Series page)
# ==========================================================
# One non-fiction series, read online chapter by chapter. It reuses the
# book-chapter machinery (chapters.py): each chapter is a markdown file with
# front matter, in SERIES_FOLDER under BOOK_CHAPTERS_DIR, ordered by filename.
#
#   book_chapters/
#     sunday_odds/
#       01-plan-for-the-bad-month.md
#       02-how-big-is-big-enough.md
#
# Pages produced: series.html (chapter list) and series-<chapter-slug>.html
# (one per chapter). If the folder is missing or empty, the Series nav link
# and the homepage feature simply don't appear.
#
# The build logs a warning if SERIES_TITLE still starts with "[" (a placeholder).
SERIES_TITLE = "Sunday Odds"
SERIES_FOLDER = "sunday_odds"
SERIES_EYEBROW = "The Series"

# Short premise, shown on the homepage feature block.
SERIES_PREMISE = (
    "A fiction series about money. Each Sunday, in her mother's kitchen in "
    "Fairfax, Virginia, Anika brings a question about her first real "
    "paycheck, and Revathi, who has worked in markets for twenty-six years, "
    "answers in odds instead of certainties."
)
# Longer introduction, shown at the top of the Series page.
SERIES_INTRO = (
    "Every Sunday, Anika drives to her mother's kitchen with a question she "
    "can't get a straight answer to online. Revathi sketches the numbers on a "
    "napkin, disagrees with her, and ends with one Monday Move. Money, here, "
    "is a set of odds, not a set of rules."
)
SERIES_READ_NOTE = "New chapters on Sundays. Best read in order."

# Shown at the foot of every series chapter and under the chapter list.
SERIES_DISCLAIMER = (
    "Sunday Odds is a fiction series about money. Revathi and Anika are "
    "fictional, and the figures are illustrative. This is education, not "
    "personalized financial, tax or legal advice."
)

# Speaker names used in the chapters, mother first. A paragraph that starts
# with **Revathi:** or **Anika:** in the markdown is rendered with the speaker
# name as a small label above the text, and a side rule whose colour depends
# on the speaker's position in this list (see generators._format_dialogue).
SERIES_SPEAKERS = ("Revathi", "Anika")

# Shown instead of the text of a chapter with `lock: true`.
SERIES_LOCKED_MESSAGE = "This chapter is locked for now. Check back soon, or pick up the book to read it in full."

# ==========================================================
# Book Chapters (online reading)
# ==========================================================
# A book listed in books.json can optionally be readable on the site, one
# page per chapter. Each chapter is a markdown file; all chapters of a book
# live together in their own folder under BOOK_CHAPTERS_DIR:
#
#   book_chapters/
#     the_quiet_asterisk/        <- folder name goes in BOOK_CHAPTER_FOLDERS
#       01-the-asterisk.md
#       02-small-numbers.md      <- chapters are ordered by filename
#
# Each chapter file starts with front matter:
#
#   ---
#   title: The Asterisk
#   synopsis: One line describing the chapter.
#   keywords: probability, patience, chance
#   lock: false                 <- true/yes/1 hides the body (see below)
#   ---
#
# BOOK_CHAPTER_FOLDERS maps a book's title, EXACTLY as written in
# books.json, to its folder name inside BOOK_CHAPTERS_DIR. A book with no
# entry here simply doesn't get a "Read Me" button. A mismatched title or a
# missing folder is logged as a warning on every build.
BOOK_CHAPTERS_DIR = Path("./book_chapters")
BOOK_CHAPTER_FOLDERS = {
    "Life is Happenning": "life_is_happenning",
}

BOOK_READ_LABEL = "Read Me"

# Shown in place of the chapter text when a chapter has `lock: true`.
# The locked chapter's body is never written into the generated HTML at
# all (it isn't just hidden with CSS), so it can't be read via view-source.
# Plain text only; it is HTML-escaped when rendered.
BOOK_LOCKED_MESSAGE = (
    "This chapter is locked for now. Check back soon, or pick up the book "
    "to read it in full."
)

# ==========================================================
# Temporary Files
# ==========================================================
TEMP_CONTENT_FILE = "temp_content.txt"
