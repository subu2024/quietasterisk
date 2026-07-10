#!/usr/bin/env python3
# make_blog_v3.py (v7.0)
# Quiet Asterisk Blog Generator - Modern Design Edition
# Integrated with refined editorial design system

import re
import shutil
import json
import textwrap
import logging
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List

import markdown
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================================
# Config
# ==========================================================
BLOG_TITLE = "quiet asterisk *"
TAG_LINE = "On chance, meaning, and the quiet details."
COPYRIGHT = "© 2026 pathway llc. All rights reserved."

INPUT_DIR = Path("./blogger_markdown")
OUTPUT_DIR = Path("./output")
IMAGE_DIR = OUTPUT_DIR / "images"
BOOKS_FILE = Path("./books.json")

INDEX_FILE = "index.html"
ABOUT_FILE = "about.html"
CATEGORIES_FILE = "categories.html"
BOOKS_FILE_HTML = "books.html"

MIN_SNIPPET_LEN = 38
SIMILARITY_THRESHOLD = 0.15

TEMP_CONTENT = ""

# ==========================================================
# Logging
# ==========================================================
logger = logging.getLogger("BlogGen")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

# ==========================================================
# Dataclass
# ==========================================================
@dataclass
class Post:
    path: Path
    title: str
    date: str
    category: str
    featured: bool
    archived: bool
    excerpt: str
    body: str

    @property
    def slug(self):
        return "_".join(re.findall(r'\w+', self.path.stem)).lower() + ".html"

    @property
    def reading_time(self):
        words = len(self.body.split())
        return f"{max(1, round(words / 155))} min read"

    @property
    def formatted_date(self):
        try:
            return datetime.strptime(self.date, "%Y-%m-%d").strftime("%B %Y")
        except:
            return self.date or ""

# ==========================================================
# Utilities
# ==========================================================
def copy_image(src_path: str) -> str:
    if not src_path:
        return ""
    src = Path(src_path)
    if not src.exists():
        return ""
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    dest = IMAGE_DIR / src.name
    try:
        shutil.copy(src, dest)
    except Exception as e:
        logger.warning(f"Could not copy image {src_path}: {e}")
        return ""
    return f"images/{src.name}"

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ==========================================================
# Front Matter Parsing
# ==========================================================
def parse_front_matter(content):
    front = re.search(r"---\n(.*?)\n---", content, re.DOTALL)
    meta = front.group(1) if front else ""

    def search(pattern):
        match = re.search(pattern, meta, re.MULTILINE)
        return match.group(1).strip() if match else ""

    def parse_bool(value):
        if not value:
            return False
        return value.lower() in ("true", "yes", "1")

    title = search(r'title:\s*"?(.+?)"?$') or "Untitled"
    date = search(r'date:\s*(.+?)$') or ""
    category = search(r'category:\s*(.+?)$') or "Uncategorized"
    excerpt = search(r'excerpt:\s*"?(.+?)"?$') or ""

    featured = parse_bool(search(r'featured:\s*(.+?)$'))
    archived = parse_bool(search(r'archived:\s*(.+?)$'))

    body = re.sub(r"---\n.*?\n---", '', content, flags=re.DOTALL).strip()

    return title, date, category, featured, archived, excerpt, body

def read_markdown_files(directory: Path) -> List[Post]:
    posts = []
    if not directory.exists():
        logger.warning(f"Input directory {directory} does not exist.")
        return posts

    for md in directory.glob("*.md"):
        try:
            with open(md, encoding="utf-8") as f:
                (
                    title,
                    date,
                    category,
                    featured,
                    archived,
                    excerpt,
                    body
                ) = parse_front_matter(f.read())
        except Exception as e:
            logger.warning(f"Failed to read {md}: {e}")
            continue

        if archived:
            continue

        posts.append(
            Post(
                path=md,
                title=title,
                date=date,
                category=category,
                featured=featured,
                archived=archived,
                excerpt=excerpt,
                body=body
            )
        )

    posts.sort(key=lambda p: p.date or "", reverse=True)
    return posts

# ==========================================================
# Similarity
# ==========================================================
def compute_similarity(posts: List[Post]):
    content = [clean_text(p.body) for p in posts]
    if not content:
        return []
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
    vec = vectorizer.fit_transform(content)
    return cosine_similarity(vec)

def build_related_map(posts, sim_matrix):
    related = {}
    for i, post in enumerate(posts):
        scores = sorted(
            [(j, sim_matrix[i][j]) for j in range(len(posts))
             if i != j and sim_matrix[i][j] >= SIMILARITY_THRESHOLD],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        related[post.slug] = [posts[j].slug for j, _ in scores]
    return related

# ==========================================================
# Books
# ==========================================================
def load_books():
    if not BOOKS_FILE.exists():
        return []
    try:
        with open(BOOKS_FILE, encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                logger.warning("books.json does not contain a list; ignoring.")
                return []
    except Exception as e:
        logger.warning(f"Failed to load books.json: {e}")
        return []

# ==========================================================
# Modern CSS Styles
# ==========================================================
def get_modern_styles():
    return """
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=Work+Sans:wght@400;500;600&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --color-cream: #FAF8F3;
  --color-sand: #E8E3D8;
  --color-charcoal: #2B2826;
  --color-slate: #5A5450;
  --color-rust: #B8503E;
  --color-terracotta: #D17458;
  --color-sage: #8B9B7E;
  --color-gold: #C9A767;
  --font-serif: 'Crimson Pro', serif;
  --font-sans: 'Work Sans', sans-serif;
}

body {
  font-family: var(--font-serif);
  background: var(--color-cream);
  color: var(--color-charcoal);
  font-size: 18px;
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
}

.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

/* Header */
.header {
  border-bottom: 2px solid var(--color-sand);
  background: var(--color-cream);
  position: sticky;
  top: 0;
  z-index: 50;
  backdrop-filter: blur(8px);
  background: rgba(250, 248, 243, 0.95);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 0;
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  font-family: var(--font-serif);
  color: var(--color-charcoal);
  text-decoration: none;
  transition: color 0.3s;
}

.logo:hover {
  color: var(--color-rust);
}

.logo-asterisk {
  color: var(--color-rust);
  margin-left: 0.25rem;
}

.nav {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.nav-link {
  font-family: var(--font-sans);
  font-size: 0.875rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-slate);
  text-decoration: none;
  transition: color 0.3s;
  position: relative;
}

.nav-link:hover, .nav-link.active {
  color: var(--color-charcoal);
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: -0.25rem;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--color-rust);
}

/* Hero Section */
.hero {
  padding: 8rem 0 6rem;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, var(--color-cream) 0%, var(--color-sand) 100%);
}

.hero-bg-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.05;
}

.hero-bg-blob-1 {
  top: 5rem;
  right: 2.5rem;
  width: 18rem;
  height: 18rem;
  background: var(--color-terracotta);
}

.hero-bg-blob-2 {
  bottom: 2.5rem;
  left: 2.5rem;
  width: 24rem;
  height: 24rem;
  background: var(--color-sage);
}

.hero-content {
  position: relative;
  z-index: 10;
}

.hero-label {
  font-family: var(--font-sans);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--color-rust);
  font-weight: 500;
  margin-bottom: 2rem;
}

.hero-title {
  font-size: clamp(3rem, 6vw, 5rem);
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  max-width: 80rem;
}

.hero-title-accent {
  font-style: italic;
}

.hero-subtitle {
  font-size: clamp(1.5rem, 3vw, 2rem);
  color: var(--color-slate);
  font-weight: 300;
  line-height: 1.5;
  max-width: 48rem;
  margin-bottom: 3rem;
}

.hero-description {
  font-size: 1.25rem;
  color: var(--color-slate);
  line-height: 1.6;
  max-width: 42rem;
  margin-bottom: 3rem;
}

.hero-cta {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-bottom: 4rem;
}

.btn {
  padding: 1.25rem 2.5rem;
  font-family: var(--font-sans);
  font-weight: 500;
  font-size: 1.125rem;
  text-decoration: none;
  border-radius: 2px;
  transition: all 0.3s;
  display: inline-block;
}

.btn-primary {
  background: var(--color-rust);
  color: white;
  border: 2px solid var(--color-rust);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.btn-primary:hover {
  background: #A03D2F;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.btn-secondary {
  background: transparent;
  color: var(--color-charcoal);
  border: 2px solid var(--color-charcoal);
}

.btn-secondary:hover {
  background: var(--color-charcoal);
  color: white;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  max-width: 48rem;
}

.stat-item {
  padding-left: 1.5rem;
  border-left: 4px solid;
}

.stat-item:nth-child(1) { border-color: var(--color-rust); }
.stat-item:nth-child(2) { border-color: var(--color-sage); }
.stat-item:nth-child(3) { border-color: var(--color-gold); }

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  font-family: var(--font-serif);
  margin-bottom: 0.5rem;
}

.stat-label {
  font-family: var(--font-sans);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-slate);
}

/* Section Headers */
.section {
  padding: 6rem 0;
}

.section-header {
  margin-bottom: 4rem;
}

.section-header-centered {
  text-align: center;
}

.section-title {
  font-size: clamp(2.5rem, 5vw, 3.75rem);
  font-weight: 700;
  font-family: var(--font-serif);
  margin-bottom: 1.5rem;
}

.section-description {
  font-size: 1.25rem;
  color: var(--color-slate);
  line-height: 1.6;
  max-width: 48rem;
}

.section-description-centered {
  margin: 0 auto;
}

.divider {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  padding: 3rem 0;
}

.divider-line {
  width: 4rem;
  height: 2px;
}

.divider-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

/* Cards */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.card {
  background: white;
  border: 2px solid var(--color-sand);
  padding: 2.5rem;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.card:hover {
  border-color: var(--color-charcoal);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  transform: translateY(-4px);
}

.card-category {
  font-family: var(--font-sans);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-weight: 500;
  margin-bottom: 1rem;
  display: inline-block;
}

.card-title {
  font-size: 1.875rem;
  font-weight: 700;
  font-family: var(--font-serif);
  margin-bottom: 1rem;
  color: var(--color-charcoal);
  transition: color 0.3s;
}

.card:hover .card-title {
  color: var(--color-rust);
}

.card-excerpt {
  color: var(--color-slate);
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.card-meta {
  font-family: var(--font-sans);
  font-size: 0.875rem;
  color: var(--color-slate);
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.card-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: var(--font-sans);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-rust);
  text-decoration: none;
  transition: transform 0.3s;
}

.card:hover .card-link {
  transform: translateX(0.5rem);
}

/* Featured Card (Large) */
.featured-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.card-featured {
  grid-row: span 2;
  padding: 3rem;
}

.featured-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: var(--color-rust);
  color: white;
  font-family: var(--font-sans);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-weight: 500;
  border-radius: 20px;
  margin-bottom: 1.5rem;
}

.card-featured .card-title {
  font-size: 3rem;
  margin-bottom: 1.5rem;
}

.card-featured .card-excerpt {
  font-size: 1.25rem;
  margin-bottom: 2rem;
}

/* Post Content */
.post-content {
  max-width: 48rem;
  margin: 0 auto;
  padding: 4rem 1.5rem;
}

.post-header {
  margin-bottom: 3rem;
}

.post-title {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 1.5rem;
}

.post-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 2rem;
}

.post-meta-item {
  font-family: var(--font-sans);
  font-size: 0.875rem;
  color: var(--color-slate);
}

.post-category {
  font-family: var(--font-sans);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-weight: 500;
  color: var(--color-rust);
}

.decorative-line {
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, var(--color-rust), var(--color-terracotta));
  margin: 2rem 0;
}

.post-body {
  font-size: 1.125rem;
  line-height: 1.8;
}

.post-body h2, .post-body h3 {
  font-weight: 600;
  margin-top: 2.5rem;
  margin-bottom: 1rem;
}

.post-body p {
  margin-bottom: 1.5rem;
}

.post-body img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 2rem 0;
}

.post-body blockquote {
  border-left: 4px solid var(--color-rust);
  padding-left: 2rem;
  margin: 2rem 0;
  font-style: italic;
  color: var(--color-slate);
}

/* Related Posts */
.related-posts {
  margin-top: 4rem;
  padding-top: 4rem;
  border-top: 2px solid var(--color-sand);
}

.related-posts-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 2rem;
}

.related-posts-list {
  list-style: none;
  padding: 0;
}

.related-posts-item {
  padding: 1rem 0;
  border-bottom: 1px solid var(--color-sand);
}

.related-posts-link {
  color: var(--color-charcoal);
  text-decoration: none;
  font-size: 1.25rem;
  font-weight: 600;
  transition: color 0.3s;
}

.related-posts-link:hover {
  color: var(--color-rust);
}

/* Footer */
.footer {
  background: var(--color-charcoal);
  color: var(--color-cream);
  padding: 4rem 0 2rem;
  margin-top: 6rem;
  border-top: 2px solid var(--color-sand);
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 3rem;
  margin-bottom: 3rem;
}

.footer-section-title {
  font-family: var(--font-sans);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--color-terracotta);
  margin-bottom: 1.5rem;
  font-weight: 500;
}

.footer-nav {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.footer-link {
  color: var(--color-sand);
  text-decoration: none;
  transition: color 0.3s;
}

.footer-link:hover {
  color: white;
}

.footer-bottom {
  padding-top: 2rem;
  border-top: 1px solid var(--color-slate);
  text-align: center;
  font-family: var(--font-sans);
  font-size: 0.875rem;
  color: var(--color-sand);
}

/* Books Section */
.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.book-card {
  background: white;
  border: 2px solid var(--color-sand);
  padding: 2rem;
  transition: all 0.3s;
}

.book-card:hover {
  border-color: var(--color-gold);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.book-image {
  width: 100%;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.book-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.book-description {
  color: var(--color-slate);
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .nav {
    gap: 1rem;
  }
  
  .hero {
    padding: 4rem 0 3rem;
  }
  
  .hero-stats {
    grid-template-columns: 1fr;
  }
  
  .section {
    padding: 3rem 0;
  }
  
  .featured-grid {
    grid-template-columns: 1fr;
  }
  
  .card-featured {
    grid-row: auto;
  }
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-in {
  animation: fadeIn 0.6s ease-out;
}
"""

# ==========================================================
# HTML Layout
# ==========================================================
def header_html(title, active_page="home"):
    active_home = "active" if active_page == "home" else ""
    active_books = "active" if active_page == "books" else ""
    active_categories = "active" if active_page == "categories" else ""
    active_about = "active" if active_page == "about" else ""
    
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
        <a href="{INDEX_FILE}" class="nav-link {active_home}">Essays</a>
        <a href="{BOOKS_FILE_HTML}" class="nav-link {active_books}">Books</a>
        <a href="{CATEGORIES_FILE}" class="nav-link {active_categories}">Categories</a>
        <a href="{ABOUT_FILE}" class="nav-link {active_about}">About</a>
      </nav>
    </div>
  </div>
</header>
<main>
"""

def footer_html():
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
        </nav>
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

# ==========================================================
# Card Formatters
# ==========================================================
def format_featured_card(post: Post):
    """Large featured card for hero section"""
    return f"""
<article class="card card-featured">
  <span class="featured-badge">Featured</span>
  <div class="card-meta" style="margin-bottom: 1.5rem;">
    <span class="card-category" style="color: var(--color-rust);">{post.category}</span>
    <span class="post-meta-item">{post.formatted_date}</span>
    <span class="post-meta-item">{post.reading_time}</span>
  </div>
  <h3 class="card-title">{post.title}</h3>
  <p class="card-excerpt">{post.excerpt}</p>
  <a href="{post.slug}" class="card-link">
    Read Essay
    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
    </svg>
  </a>
</article>
"""

def format_card(post: Post, is_small=False):
    """Standard card for lists"""
    return f"""
<article class="card">
  <div class="card-meta">
    <span class="card-category" style="color: var(--color-rust);">{post.category}</span>
    <span class="post-meta-item">{post.formatted_date}</span>
  </div>
  <h3 class="card-title">{post.title}</h3>
  <p class="card-excerpt">{post.excerpt}</p>
  <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
    <span class="post-meta-item">{post.reading_time}</span>
    <a href="{post.slug}" class="card-link">
      Read
      <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
      </svg>
    </a>
  </div>
</article>
"""

def format_book_card(book, show_full_description=False):
    """Book card for books section"""
    img_html = ""
    if book.get("image"):
        # Handle both relative paths and filenames
        image_path = book.get("image")
        # If it's just a filename, assume it's in current directory or images dir
        if not image_path.startswith('./') and not image_path.startswith('/'):
            # Try multiple possible locations
            possible_paths = [
                Path(image_path),
                Path('./images') / image_path,
                Path('.') / image_path
            ]
            for path in possible_paths:
                if path.exists():
                    image_path = str(path)
                    break
        
        img = copy_image(image_path)
        if img:
            img_html = f'<img src="{img}" class="book-image" alt="{book.get("title", "")}">'
    
    description = book.get("description", "")
    if not show_full_description and len(description) > 150:
        description = description[:150] + "..."
    
    link_html = ""
    link_url = book.get("link", "")
    if link_url:  # Only show button if link exists and is not empty
        link_html = f'''
        <a href="{link_url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" 
           style="font-size: 0.875rem; padding: 0.75rem 1.5rem; display: inline-block;">
          Buy Book
        </a>
        '''
    
    # Optional additional metadata
    author_html = ""
    if book.get("author"):
        author_html = f'<p style="color: var(--color-slate); margin-bottom: 0.5rem; font-family: var(--font-sans); font-size: 0.875rem;">by {book.get("author")}</p>'
    
    year_html = ""
    if book.get("year"):
        year_html = f'<p style="color: var(--color-slate); margin-bottom: 1rem; font-family: var(--font-sans); font-size: 0.875rem;">Published {book.get("year")}</p>'
    
    return f"""
<div class="book-card">
  {img_html}
  <h4 class="book-title">{book.get("title", "")}</h4>
  {author_html}
  {year_html}
  <p class="book-description">{description}</p>
  {link_html}
</div>
"""

# ==========================================================
# Page Generators
# ==========================================================
def generate_post_pages(posts, related_map):
    global TEMP_CONTENT
    for post in posts:
        # Convert markdown to HTML
        html_body = markdown.markdown(post.body, extensions=['extra', 'codehilite'])
        
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

        TEMP_CONTENT += f"TITLE: {post.title}\nDATE: {post.date}\nCONTENT: {clean_text(post.body)[:500]}\n\n"

def generate_index(posts):
    books = load_books()
    sim_matrix = compute_similarity(posts) if len(posts) > 1 else []
    related_map = build_related_map(posts, sim_matrix) if len(posts) > 1 else {}

    # Generate individual post pages
    generate_post_pages(posts, related_map)

    content = header_html("Home - " + BLOG_TITLE, "home")

    # Hero Section
    content += """
<section class="hero">
  <div class="hero-bg-blob hero-bg-blob-1"></div>
  <div class="hero-bg-blob hero-bg-blob-2"></div>
  <div class="container">
    <div class="hero-content">
      <p class="hero-label">Welcome to Quiet Asterisk</p>
      <h1 class="hero-title">
        Essays on <span class="hero-title-accent" style="color: var(--color-rust);">meaning</span>, 
        <span style="color: var(--color-sage);">uncertainty</span>, and the quiet details
      </h1>
      <p class="hero-subtitle">that shape how we think and see the world</p>
      <p class="hero-description">
        A collection of reflections on systems, stories, and the subtle patterns that connect them. 
        Written with care for those who notice the small things.
      </p>
      <div class="hero-cta">
        <a href="#featured" class="btn btn-primary">Explore Essays</a>
        <a href="about.html" class="btn btn-secondary">About the Author</a>
      </div>
"""
    
    # Calculate stats
    total_posts = len(posts)
    total_words = sum(len(p.body.split()) for p in posts)
    
    content += f"""
      <div class="hero-stats">
        <div class="stat-item">
          <div class="stat-number">{total_posts}+</div>
          <div class="stat-label">Essays Published</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{len(set(p.category for p in posts))}</div>
          <div class="stat-label">Categories</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{len(books)}</div>
          <div class="stat-label">Books Written</div>
        </div>
      </div>
    </div>
  </div>
</section>
"""

    # Books section
    if books:
        content += """
<section class="section">
  <div class="container">
    <div class="section-header">
      <h2 class="section-title">Books</h2>
      <p class="section-description">Published works and ongoing projects</p>
    </div>
    <div class="books-grid">
"""
        # Show only first 3 books on homepage
        for book in books[:3]:
            content += format_book_card(book, show_full_description=False)
        content += """
    </div>
    <div style="margin-top: 3rem; text-align: center;">
      <a href="books.html" class="btn btn-secondary">View All Books</a>
    </div>
  </div>
</section>
"""

    # Divider
    content += """
<div class="divider">
  <div class="divider-line" style="background: var(--color-rust);"></div>
  <div class="divider-dot" style="background: var(--color-rust);"></div>
  <div class="divider-line" style="background: var(--color-rust);"></div>
</div>
"""

    # Featured Essays
    featured_posts = [p for p in posts if p.featured][:4]
    if featured_posts:
        content += """
<section class="section" id="featured">
  <div class="container">
    <div class="section-header section-header-centered">
      <h2 class="section-title">Featured Essays</h2>
      <p class="section-description section-description-centered">Recent explorations worth your time</p>
      <div style="display: flex; justify-content: center; margin-top: 2rem;">
        <div style="width: 6rem; height: 2px; background: linear-gradient(90deg, transparent, var(--color-rust), transparent);"></div>
      </div>
    </div>
    <div class="featured-grid">
"""
        # First featured post gets large card
        content += format_featured_card(featured_posts[0])
        
        # Remaining featured posts get standard cards
        content += '<div style="display: flex; flex-direction: column; gap: 2rem;">'
        for post in featured_posts[1:]:
            content += format_card(post, is_small=True)
        content += '</div>'
        
        content += "</div></div></section>"

    # Divider
    content += """
<div class="divider">
  <div class="divider-line" style="background: var(--color-gold);"></div>
  <div class="divider-dot" style="background: var(--color-gold);"></div>
  <div class="divider-line" style="background: var(--color-gold);"></div>
</div>
"""

    # Recent Posts
    recent_posts = [p for p in posts if not p.featured][:6]
    if recent_posts:
        content += """
<section class="section">
  <div class="container">
    <div class="section-header">
      <h2 class="section-title">Recent Essays</h2>
      <p class="section-description">Latest thoughts and explorations</p>
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

    content += footer_html()

    with open(OUTPUT_DIR / INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def generate_about():
    about_text = """
    <h2>About the Author</h2>
    <p>Subu Sangameswar writes about love and loss, parenting chaos,
    uncertainty, systems, and our deeply human habit of demanding clarity
    from a world that offers none.</p>
    <p>Part biography, part fiction, his work moves like an episode of
    <a href="https://en.wikipedia.org/wiki/Seinfeld" target="_blank" rel="noopener noreferrer">Seinfeld</a>
    — observant, self-aware, mildly neurotic, and uncomfortably honest.</p>
    <p>In a culture obsessed with certainty, he lingers in risk, chance, and
    hope — treating uncertainty not as a flaw to eliminate, but as a
    companion to travel with. Preferably with humor. Sometimes with coffee.</p>
    """
    content = header_html("About - " + BLOG_TITLE, "about")
    content += f"""
<section class="section">
  <div class="container">
    <article class="post-content">
{about_text}
    </article>
  </div>
</section>
"""
    content += footer_html()
    with open(OUTPUT_DIR / ABOUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def generate_categories(posts):
    grouped = {}
    for post in posts:
        grouped.setdefault(post.category, []).append(post)

    content = header_html("Categories - " + BLOG_TITLE, "categories")
    content += """
<section class="section">
  <div class="container">
    <div class="section-header section-header-centered">
      <h1 class="section-title">All Categories</h1>
      <p class="section-description section-description-centered">
        Explore essays by topic and theme
      </p>
    </div>
"""

    for category, cat_posts in sorted(grouped.items()):
        cat_posts.sort(key=lambda p: p.date or "", reverse=True)
        
        content += f"""
    <div style="margin-bottom: 4rem;">
      <h2 class="section-title" style="font-size: 2rem; margin-bottom: 2rem;">
        {category} <span style="color: var(--color-slate); font-size: 1.5rem;">({len(cat_posts)})</span>
      </h2>
      <div class="card-grid">
"""
        for post in cat_posts:
            content += format_card(post)
        
        content += "</div></div>"

    content += "</div></section>"
    content += footer_html()

    with open(OUTPUT_DIR / CATEGORIES_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def generate_books():
    """Generate dedicated books page showing all books"""
    books = load_books()
    
    if not books:
        logger.info("No books found, skipping books page generation")
        return
    
    content = header_html("Books - " + BLOG_TITLE, "books")
    
    # Hero section for books page
    content += """
<section class="hero" style="padding: 6rem 0 4rem;">
  <div class="container">
    <div class="hero-content">
      <p class="hero-label">Published Works</p>
      <h1 class="hero-title" style="font-size: clamp(3rem, 5vw, 4rem);">
        Books by <span style="color: var(--color-rust); font-style: italic;">Subu Sangameswar</span>
      </h1>
      <p class="hero-description" style="max-width: 48rem;">
        A collection of published works exploring life, meaning, and the human experience 
        through essays, stories, and poetry.
      </p>
    </div>
  </div>
</section>
"""
    
    # All books section
    content += """
<section class="section">
  <div class="container">
"""
    
    # Check if books have type field for grouping
    has_types = any(book.get("type") for book in books)
    
    if has_types:
        # Group books by type
        grouped_books = {}
        for book in books:
            book_type = book.get("type", "Books")
            grouped_books.setdefault(book_type, []).append(book)
        
        # Show grouped sections
        for book_type, type_books in grouped_books.items():
            content += f"""
    <div style="margin-bottom: 4rem;">
      <h2 class="section-title" style="font-size: 2.5rem; margin-bottom: 2rem;">
        {book_type}
      </h2>
      <div class="books-grid">
"""
            for book in type_books:
                content += format_book_card(book, show_full_description=True)
            content += "</div></div>"
    else:
        # Just show all books in a grid without grouping
        content += '<div class="books-grid">'
        for book in books:
            content += format_book_card(book, show_full_description=True)
        content += "</div>"
    
    content += """
  </div>
</section>
"""
    
    # Call to action
    content += """
<section class="section" style="background: var(--color-sand); padding: 4rem 0;">
  <div class="container" style="text-align: center;">
    <h3 style="font-family: var(--font-serif); font-size: 2rem; margin-bottom: 1rem; color: var(--color-charcoal);">
      Explore More Writing
    </h3>
    <p style="color: var(--color-slate); font-size: 1.125rem; margin-bottom: 2rem; max-width: 36rem; margin-left: auto; margin-right: auto;">
      Dive deeper into essays, stories, and reflections on meaning, uncertainty, and the patterns that connect us.
    </p>
    <a href="index.html" class="btn btn-primary">Read Essays</a>
  </div>
</section>
"""
    
    content += footer_html()
    
    with open(OUTPUT_DIR / BOOKS_FILE_HTML, "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info(f"Generated books page with {len(books)} books")

# ==========================================================
# Main
# ==========================================================
def main(write_temp=False):
    logger.info("Generating blog with modern design...")

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)
    IMAGE_DIR.mkdir(exist_ok=True)

    posts = read_markdown_files(INPUT_DIR)
    
    if not posts:
        logger.warning("No posts found. Creating sample content...")
        # You could add sample post generation here if needed

    generate_index(posts)
    generate_books()
    generate_categories(posts)
    generate_about()

    if write_temp:
        with open("temp_content.txt", "w", encoding="utf-8") as f:
            f.write(TEMP_CONTENT)

    logger.info(f"Generated {len(posts)} posts successfully.")
    logger.info(f"Output directory: {OUTPUT_DIR.absolute()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a modern blog from markdown files")
    parser.add_argument("--write-temp", action="store_true", help="Write temporary content file")
    args = parser.parse_args()
    main(write_temp=args.write_temp)
