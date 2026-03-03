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

    @property
    def slug(self):
        """Generate URL-friendly slug from filename."""
        return "_".join(re.findall(r'\w+', self.path.stem)).lower() + ".html"

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
