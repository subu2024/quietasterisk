"""
Data models for blog posts and content.
"""

import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from sklearn import base


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
        """Generate stable, URL-friendly slug from title + id fallback."""
        base = self.title or self.path.stem or "untitled"

        
        # normalize title into words
        words = re.findall(r'\w+', base)
        slug_text = "_".join(words).lower()

        if not slug_text:
            slug_text = "untitled"

        
        # ensure uniqueness + stability
        #unique_part = getattr(self, "id", None) or self.path.stem

        #print(f"{unique_part}.html")

        #print(f"{slug_text}_{unique_part}.html")

        #return f"{slug_text}_{unique_part}.html"
        return f"{slug_text}.html"
    
#    def slug(self):
#        """Generate URL-friendly slug from filename."""
#        return "_".join(re.findall(r'\w+', self.path.stem)).lower() + ".html"

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
