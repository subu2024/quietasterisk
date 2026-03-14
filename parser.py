"""
Markdown front matter parser for blog posts.
"""

import re
from pathlib import Path
from typing import List
import logging

#import markdown
#from markdown.extensions import Extension
#from markdown.inlinepatterns import InlineProcessor
#import xml.etree.ElementTree as etree

import re

from models import Post
from config import INPUT_DIR

logger = logging.getLogger("BlogGen")


    
def parse_front_matter(content: str) -> tuple:
    """
    Parse YAML-style front matter from markdown content.
    
    Args:
        content: Raw markdown content with front matter
        
    Returns:
        Tuple of (title, date, category, featured, archived, excerpt, body)
    """
    # Extract front matter between --- delimiters
    front = re.search(r"---\n(.*?)\n---", content, re.DOTALL)
    meta = front.group(1) if front else ""

    def search(pattern):
        """Search for a pattern in the front matter."""
        match = re.search(pattern, meta, re.MULTILINE)
        return match.group(1).strip() if match else ""

    def parse_bool(value):
        """Parse boolean value from string."""
        if not value:
            return False
        return value.lower() in ("true", "yes", "1")

    # Extract metadata fields
    title = search(r'title:\s*"?(.+?)"?$') or "Untitled"
    date = search(r'date:\s*(.+?)$') or ""
    category = search(r'category:\s*(.+?)$') or "Uncategorized"
    excerpt = search(r'excerpt:\s*"?(.+?)"?$') or ""
    featured = parse_bool(search(r'featured:\s*(.+?)$'))
    archived = parse_bool(search(r'archived:\s*(.+?)$'))

    # Extract body content (everything after front matter)
    body = re.sub(r"---\n.*?\n---", '', content, flags=re.DOTALL).strip()

    return title, date, category, featured, archived, excerpt, body

def process_youtube_embeds(html_content: str) -> str:
    """
    Convert [youtube:VIDEO_ID] tags to YouTube iframe embeds.
    
    Args:
        html_content: HTML content with [youtube:ID] tags
        
    Returns:
        HTML with embedded YouTube iframes
    """
    def youtube_replacer(match):
        video_id = match.group(1)
        return f'''
<div class="youtube-embed" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 2rem 0;">
    <iframe 
        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
        src="https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1" 
        title="YouTube video player"
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
        referrerpolicy="strict-origin-when-cross-origin"
        allowfullscreen>
    </iframe>
</div>
'''
    
    # Replace [youtube:VIDEO_ID] with iframe
    pattern = r'\[youtube:([a-zA-Z0-9_-]+)\]'
    return re.sub(pattern, youtube_replacer, html_content)

def read_markdown_files(directory: Path) -> List[Post]:
    """
    Read all markdown files from a directory and parse them into Post objects.
    
    Args:
        directory: Directory containing markdown files
        
    Returns:
        List of Post objects, sorted by date (newest first)
    """
    posts = []
    
    if not directory.exists():
        logger.warning(f"Input directory {directory} does not exist.")
        return posts

    for md_file in directory.glob("*.md"):
        try:
            with open(md_file, encoding="utf-8") as f:
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
            logger.warning(f"Failed to read {md_file}: {e}")
            continue

        # Skip archived posts .. this is useful to keep old posts in the source directory without them being published
        if archived:
            continue

        posts.append(
            Post(
                path=md_file,
                title=title,
                date=date,
                category=category,
                featured=featured,
                archived=archived,
                excerpt=excerpt,
                body=body
            )
        )

    # Sort by date, newest first
    posts.sort(key=lambda p: p.date or "", reverse=True)
    
    return posts
