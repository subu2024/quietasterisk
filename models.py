"""
Data models for blog posts and content.
"""

import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Post:
    """Represents a blog post with all its metadata and content."""
    
    path: Path
    title: str
    date: str
    category: str
    featured: bool
    archived: bool
    excerpt: str
    body: str
    _slug: str = ""

    @property
    def slug(self):
        """Generate stable, URL-friendly slug from title + id fallback."""
        base = self._slug or self.title or self.path.stem or "untitled"

        # normalize title into words
        words = re.findall(r'\w+', base)
        slug_text = "-".join(words).lower() or "untitled"

        return f"{slug_text}.html"

    @property
    def reading_time(self):
        """Calculate estimated reading time based on word count."""
        words = len(self.body.split())
        minutes = max(1, round(words / 155))  # Average reading speed: 155 words/min
        return f"{minutes} min read"

    @property
    def formatted_date(self):
        """Format date as 'Month Year' (e.g., 'January 2025')."""
        try:
            return datetime.strptime(self.date, "%Y-%m-%d").strftime("%B %Y")
        except:
            return self.date or ""
