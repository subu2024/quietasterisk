# make_blog.py (Enhanced v3.1)
# Generates a Bootstrap-styled static blog with optional categories page, featured images, callouts, and visual hierarchy.

import os
import shutil
import re
from datetime import datetime
from pathlib import Path
import logging
import markdown
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import textwrap
import argparse

TEMP_CONTENT = ""

# ------------------------------
# Configuration
# ------------------------------
BLOG_TITLE = "Rhyme and Reflection"
TAG_LINE = "Spinning life’s chaos into laughs, stories, and verses — because therapy is expensive"
COPYRIGHT = "© 2025 Subu Sangameswar. All original content. All rights reserved. For permission to reuse or reproduce any part of this work, please contact the <a href='mailto:subusangam@gmail.com?subject=permission to reuse' target='_top'>author</a>."
INPUT_DIR = Path("./blogger_markdown")
OUTPUT_DIR = Path("./output")
IMAGE_DIR = OUTPUT_DIR / "images"
INDEX_FILE = "index.html"
ABOUT_FILE = "about.html"
SHOW_SNIPPET = True
MIN_SNIPPET_LEN = 38
SIMILARITY_THRESHOLD = 0.15
GENERATE_CATEGORIES_PAGE = True  # set False to disable categories page

# ------------------------------
# Logging
# ------------------------------
logger = logging.getLogger("BlogGen")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"))
logger.addHandler(handler)

# ------------------------------
# HTML Templates
# ------------------------------
HEADER = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="Subu Sangameswar">
    <meta name="description" content="Part diary, part stand-up, part overthinking — reflections that resonate (or at least echo loudly)">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Open+Sans&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Open Sans', sans-serif;
            background-color: #f8f9fa;
            color: #212529;
        }}
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Merriweather', serif;
        }}
        nav {{
            position: sticky;
            top: 0;
            z-index: 1000;
            background-color: #fff;
            border-bottom: 1px solid #dee2e6;
            padding: 0.5rem 0;
        }}
        nav a {{
            font-weight: 500;
            margin-right: 0.75rem;
        }}
        .callout {{
            background-color: #e7f3ff;
            border-left: 4px solid #0d6efd;
            padding: 1rem;
            margin: 1.5rem 0;
            border-radius: 0.25rem;
            font-weight: 500;
        }}
        .post-header-img {{
            width: 100%;
            height: auto;
            margin-bottom: 1rem;
            border-radius: 0.5rem;
        }}
        footer {{
            padding: 2rem 0;
            text-align: center;
            font-size: 0.875rem;
            color: #6c757d;
        }}
        .main-title {{
            font-family: 'Merriweather', serif;
            font-size: 2.5rem;
            font-weight: bold;
            color: #b00000;
            margin-top: 1rem;
            margin-bottom: 2rem;
            text-align: center;
        }}
        .latest-post {{
            max-width: 800px;
            margin: 0 auto 3rem auto;
            text-align: left;
        }}
        .year-panel {{
            border-top: 2px solid #ddd;
            padding-top: 2rem;
            margin-top: 2rem;
            text-align: left;
        }}
        .year-title {{
            font-weight: bold;
            font-size: 1.3rem;
            margin-bottom: 0.5rem;
            color: #b00000;
        }}
        .justify-text {{
            text-align: justify;
        }}
        .article-count {{
            color: #6c757d;
            font-weight: normal;
            font-size: 0.9rem;
        }}
         @media (max-width: 768px) {{
            .card-title {{
                font-size: 1.5rem;
            }}
            body {{
                font-size: 1rem;
                line-height: 1.75;
            }}
        }}
    </style>
</head>
<body>
<div class="container mt-3">
    <h1 class="main-title">{blog_title}</h1>
    <h4 class="mb-4">{blog_tag_line}</h4>
    <nav class="mb-4">
        <a href='{home}' class="btn btn-outline-primary btn-sm">Home</a>
        <a href='{about}' class="btn btn-outline-secondary btn-sm">About</a>
        {category_button}
    </nav>
    <div class="row">
"""

FOOTER = """</div>
    <footer class="mt-5">
        <p class="text-muted mb-0">&copy; 2025 {title} v2.6 — Built with Python</p>
    </footer>
</div>
</body>
</html>"""


ABOUT = """

  **Welcome to My Humble Corner of the Internet**

Part diary, part stand-up routine, part *“oops, did I really text that at 2 a.m.?”*  Think of it as **[Seinfeld](https://en.wikipedia.org/wiki/Seinfeld) meets therapy**, with guest appearances by failed romances, parenting chaos, philosophical detours, and the many poems no one asked for.  

Taken together, the evolution here is clear: it all starts with the fire of romantic love, slides into the chaos of arguments over social rituals, tumbles headfirst into heartbreak, and somehow—miraculously—climbs back into the sunlight of rediscovering self. And yes, sometimes the only way to get through that journey is to **laugh .. usually at myself**.  

My life is mostly *“nothing”*—commutes, coffee, bills, and me heroically pretending broccoli is delicious. But beneath the surface bubbles a stew of **messy emotions, half-baked philosophies, and stories that refuse to sit quietly in the corner**. So I write. Sometimes funny, sometimes sad, sometimes pure fiction but always at least slightly unhinged (in my own charming way, I hope).  

This blog is my way of turning therapy bills into blog posts. Here, heartbreak gets repackaged as humor, mistakes become punchlines, and fleeting thoughts get a longer shelf life wrapped in sarcasm.  

So grab a coffee, pull up a chair, and join me in laughing at the glorious mess of it all - my life. 

Thanks for reading—and remember: **stay weird, stay curious, and above all, don’t take even heartbreak too seriously**.

---

**Life happens**  
* Many thoughts race into action  
* Some real, some imagination  
* Some dark, some funny, and some with no situation  
* Some random, some with a home and a mansion  
* I imprisoned those thoughts with my pen  
* Grabbing it while I can and making it stay in my den  
* Giving it a shape, molding with a tape, forcing it to wear my apron  
* For you, my reader, to silently watch, discard, or relive the action  

---

So thanks for swinging by and reading. If you're dying to know more about me, [click here](2021_06_23_me.html).

    
"""

# ------------------------------
# Utilities
# ------------------------------

def copy_image(src_path, dest_dir):
    if not src_path:
        return None
    src = Path(src_path)
    if not src.exists():
        return None
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    try:
        shutil.copy(src, dest)
        return f"images/{src.name}"
    except Exception as e:
        logger.error(f"Failed to copy {src}: {e}")
        return None

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_front_matter(content):
    front = re.search(r"---\n(.*?)\n---", content, re.DOTALL)
    meta = front.group(1) if front else ""
    title = re.search(r'title:\s*"?(.*?)"?$', meta, re.MULTILINE).group(1) if re.search(r'title:', meta) else "Untitled"
    date = re.search(r'date:\s*(.*?)$', meta, re.MULTILINE).group(1) if re.search(r'date:', meta) else "0000-00-00"
    status_match = re.search(r'status:\s*(.*?)$', meta, re.MULTILINE)
    status = status_match.group(1).strip() if status_match else "draft"
    image = re.search(r'image:\s*(.*?)$', meta, re.MULTILINE)
    image = image.group(1).strip() if image else ""
    callout = re.search(r'callout:\s*"(.*?)"$', meta, re.MULTILINE)
    callout = callout.group(1).strip() if callout else ""
    category_match = re.search(r'category:\s*(.*?)$', meta, re.MULTILINE)
    category = category_match.group(1).strip() if category_match else "Uncategorized"
    tags = re.findall(r'"(.*?)"', meta) if 'tags' in meta else ['uncategorized']
    tags = [tag.strip() for tag in tags if tag.strip()]
    body = re.sub(r"---\n.*?\n---", '', content, count=1, flags=re.DOTALL).strip()
    return title, date, status, tags, image, callout, body, category

def read_markdown_files(directory):
    articles = {}
    for path in directory.glob("*.md"):
        with open(path, encoding="utf-8") as f:
            raw = f.read()
            title, date, status, tags, image, callout, body, category = parse_front_matter(raw)
            if status.lower() == "draft":
                continue
            articles[path] = (title, date, tags, image, callout, body, category)
    return dict(sorted(articles.items(), key=lambda x: x[1][1], reverse=True))

def estimate_reading_time(text):
    words = len(text.split())
    return f"{max(1, round(words / 155))} minute read"

def convert_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%A, %B %d, %Y')
    except:
        return "Unknown"

def generate_filename(path):
    return "_".join(re.findall(r'\w+', path.stem)).lower() + ".html"

def clean_output(directory):
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True)

# ------------------------------
# Grouping
# ------------------------------

def group_articles_by_year(articles):
    grouped = {}
    for path, (title, date, tags, image, callout, body, category) in articles.items():
        if date == "0000-00-00": continue
        year = datetime.strptime(date, "%Y-%m-%d").strftime("%Y")
        grouped.setdefault(year, []).append((path, title, date))
    return grouped

def group_articles_by_category(articles):
    grouped = {}
    for path, (title, date, tags, image, callout, body, category) in articles.items():
        grouped.setdefault(category, []).append((path, title, date))
    return dict(sorted(grouped.items(), key=lambda x: x[0].lower()))

# ------------------------------
# Similarity
# ------------------------------

def compute_similarity(articles):
    content = [clean_text(val[5]) for val in articles.values()]
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
    vec = vectorizer.fit_transform(content)
    sim_matrix = cosine_similarity(vec, dense_output=False)
    return sim_matrix.toarray()

def get_related_articles(articles, sim_matrix, filenames):
    related = {}
    for i, name in enumerate(filenames):
        scores = sorted(
            [(j, sim_matrix[i][j]) for j in range(len(filenames)) if i != j and sim_matrix[i][j] >= SIMILARITY_THRESHOLD],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        related[name] = [filenames[j] for j, _ in scores]
    return related

# ------------------------------
# Format helpers
# ------------------------------

def format_card(title, date, content, read_time='', related='', file_link='', image_url='', callout=''):
    card = f"""<div class="col-12 mb-4"><div class="card p-3"><div class="card-body">"""
    if image_url:
        card += f'<img src="{image_url}" alt="{title}" class="post-header-img"/>'
    card += f"""<h3 class="card-title">{title}</h3>
                <h6 class="card-subtitle mb-2 text-muted">{convert_date(date)} | {read_time}</h6>"""
    if callout:
        card += f'<div class="callout">{callout}</div>'
    card += f"""<div class="justify-text">{content}</div>"""
    if file_link:
        card += f'<div class="mt-3"><a href="{file_link}" class="card-link">Read More</a></div>'
    if related:
        card += f'<h5 class="justify-text mt-4">Related Articles</h5><ul class="justify-text">{related}</ul>'
    card += "</div></div></div>"
    return card

# ------------------------------
# Generators
# ------------------------------

def generate_blog_pages(articles, related_map):
    global TEMP_CONTENT
    for path, (title, date, tags, image, callout, body, category) in articles.items():
        image_url = copy_image(image, IMAGE_DIR) or (image if image else "")
        html_body = markdown.markdown(body)

        img_matches = re.findall(r'<img.*?src=[\'"](.*?)[\'"]', html_body)
        for img_src in img_matches:
            copied = copy_image(img_src, IMAGE_DIR)
            if copied:
                html_body = html_body.replace(img_src, copied)

        related = "".join(
            f'<li><a href="{generate_filename(r)}">{articles[r][0]}</a></li>'
            for r in related_map.get(path, [])
        )

        category_button = (
            "<a href='categories.html' class='btn btn-outline-success btn-sm'>Categories</a>"
            if GENERATE_CATEGORIES_PAGE else ""
        )

        content = HEADER.format(
            title=title,
            blog_title=BLOG_TITLE,
            blog_tag_line=TAG_LINE,
            home=INDEX_FILE,
            about=ABOUT_FILE,
            category_button=category_button,
        )

        content += format_card(
            title,
            date,
            html_body + f"<br/><i>{COPYRIGHT}</i>",
            estimate_reading_time(body),
            related,
            "",
            image_url,
            callout
        )

        content += FOOTER.format(title=BLOG_TITLE)
        write_html_file(content, generate_filename(path))

        
        lines = [
            f"TITLE: {title}",
            f"PUBLISHED: {date}",
            f"cCONTENT: {clean_text(html_body)[:500]}"  # trimmed to 500 chars
        ]

        # Join all lines with newline characters and add a blank line at the end
        TEMP_CONTENT += "\n".join(lines) + "\n\n"



def generate_index_page(articles):
    grouped = group_articles_by_year(articles)
    latest_path, (latest_title, latest_date, tags, image, callout, latest_body, category) = next(iter(articles.items()))
    snippet_text = markdown.markdown(latest_body)
    snippet_words = snippet_text.split()
    snippet = " ".join(snippet_words[:MIN_SNIPPET_LEN]) + "..." if len(snippet_words) > MIN_SNIPPET_LEN else snippet_text

    content = f"""
    <div class="latest-post">
        {format_card(latest_title, latest_date, snippet, file_link=generate_filename(latest_path), image_url=image, callout=callout)}
    </div>
    <div class="year-panel"><div class="row">"""

    col_count = 0
    for year in sorted(grouped.keys(), reverse=True):
        count = len(grouped[year])
        article_text = "article" if count == 1 else "articles"
        content += f'<div class="col-md-4 year-block"><div class="year-title">{year} <span class="article-count">({count} {article_text})</span></div><ul>'
        for path, title, date in sorted(grouped[year], key=lambda x: x[2], reverse=True):
            content += f'<li><a href="{generate_filename(path)}">{title}</a> <small>({convert_date(date)})</small></li>'
        content += "</ul></div>"
        col_count += 1
        if col_count % 3 == 0:
            content += '</div><div class="row mt-4">'
    content += "</div></div>"

    category_button = "<a href='categories.html' class='btn btn-outline-success btn-sm'>Categories</a>" if GENERATE_CATEGORIES_PAGE else ""
    full_html = HEADER.format(title=f"Home - {BLOG_TITLE}", blog_title=BLOG_TITLE, blog_tag_line=TAG_LINE, home=INDEX_FILE, about=ABOUT_FILE, category_button=category_button)
    full_html += content
    full_html += FOOTER.format(title=BLOG_TITLE)
    write_html_file(full_html, INDEX_FILE)

def generate_about_page():
    category_button = "<a href='categories.html' class='btn btn-outline-success btn-sm'>Categories</a>" if GENERATE_CATEGORIES_PAGE else ""
    content = HEADER.format(title="About", blog_title=BLOG_TITLE, blog_tag_line=TAG_LINE, home=INDEX_FILE, about=ABOUT_FILE, category_button=category_button)
    content += format_card("About", "", f'<div class="markdown-body">{markdown.markdown(textwrap.dedent(ABOUT))}</div>')
    content += FOOTER.format(title=BLOG_TITLE)
    write_html_file(content, ABOUT_FILE)

def generate_categories_page(articles):
    grouped = group_articles_by_category(articles)
    content = "<div class='category-page text-start'>"
    for category, posts in grouped.items():
        count = len(posts)
        article_text = "article" if count == 1 else "articles"
        content += f"<h3 class='mt-4'>{category} <span class='article-count'>({count} {article_text})</span></h3><ul>"
        for path, title, date in sorted(posts, key=lambda x: x[2], reverse=True):
            content += f'<li><a href="{generate_filename(path)}">{title}</a> <small>({convert_date(date)})</small></li>'
        content += "</ul>"
    content += "</div>"

    cat_button = "<a href='categories.html' class='btn btn-outline-success btn-sm'>Categories</a>"
    full_html = HEADER.format(title=f"Categories - {BLOG_TITLE}", blog_title=BLOG_TITLE, blog_tag_line=TAG_LINE, home=INDEX_FILE, about=ABOUT_FILE, category_button=cat_button)
    full_html += content
    full_html += FOOTER.format(title=BLOG_TITLE)
    write_html_file(full_html, "categories.html")

def write_html_file(content, name):
    with open(OUTPUT_DIR / name, 'w', encoding='utf-8') as f:
        f.write(content)

# ------------------------------
# Main
# ------------------------------

def main(write_temp=False):
    logger.info("Starting blog generation...")
    clean_output(OUTPUT_DIR)
    articles = read_markdown_files(INPUT_DIR)
    filenames = list(articles.keys())
    sim_matrix = compute_similarity(articles)
    related_map = get_related_articles(articles, sim_matrix, filenames)
    generate_blog_pages(articles, related_map)
    generate_index_page(articles)
    generate_about_page()
    if GENERATE_CATEGORIES_PAGE:
        generate_categories_page(articles)
    logger.info("Blog generated")
    if write_temp:
        with open("temp_content.txt", "w", encoding="utf-8") as f:
            f.write(TEMP_CONTENT)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate static blog pages.")
    parser.add_argument("--write-temp", action="store_true", help="Write TEMP_CONTENT to temp_content.txt")
    args = parser.parse_args()
    main(write_temp=args.write_temp)

