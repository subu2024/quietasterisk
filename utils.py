"""
Utility functions for file operations and text processing.
"""

import re
import json
import shutil
import logging
from pathlib import Path
from typing import List, Dict

from config import IMAGE_DIR, BOOKS_FILE, CATEGORIES_FILE_JSON, DOWNLOADS_DIR, OUTPUT_DOWNLOADS_DIR
from models import Post

logger = logging.getLogger("BlogGen")


# ==========================================================
# File Operations
# ==========================================================

def copy_downloads() -> int:
    """
    Copy all files from DOWNLOADS_DIR to OUTPUT_DOWNLOADS_DIR.
    
    This allows you to include downloadable files (PDFs, ebooks, etc.) 
    in your blog that will be copied to the output directory.
    
    Returns:
        Number of files copied
    """
    if not DOWNLOADS_DIR.exists():
        logger.info(f"Downloads directory {DOWNLOADS_DIR} does not exist. Skipping.")
        return 0
    
    # Create output downloads directory
    OUTPUT_DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Copy all files
    files_copied = 0
    
    for item in DOWNLOADS_DIR.rglob('*'):
        if item.is_file():
            # Calculate relative path from DOWNLOADS_DIR
            rel_path = item.relative_to(DOWNLOADS_DIR)
            dest_path = OUTPUT_DOWNLOADS_DIR / rel_path
            
            # Create parent directories if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                shutil.copy2(item, dest_path)  # copy2 preserves metadata
                files_copied += 1
                logger.debug(f"Copied: {rel_path}")
            except Exception as e:
                logger.warning(f"Failed to copy {item}: {e}")
    
    if files_copied > 0:
        logger.info(f"Copied {files_copied} file(s) from downloads directory")
    
    return files_copied

def copy_image(src_path: str) -> str:
    """
    Copy an image file to the output directory.
    
    Args:
        src_path: Source path to the image file
        
    Returns:
        Relative path to copied image, or empty string if copy failed
    """
    if not src_path:
        return ""
    
    # Handle both relative paths and filenames
    image_path = src_path
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
    
    src = Path(image_path)
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


def load_json_file(filepath: Path, expected_type=None) -> any:
    """
    Load and parse a JSON file.
    
    Args:
        filepath: Path to JSON file
        expected_type: Expected type (list, dict, etc.)
        
    Returns:
        Parsed JSON data or default value based on expected_type
    """
    if not filepath.exists():
        return [] if expected_type == list else {}
    
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
            
            # Validate type if specified
            if expected_type and not isinstance(data, expected_type):
                logger.warning(f"{filepath.name} does not contain expected type {expected_type}; ignoring.")
                return [] if expected_type == list else {}
            
            return data
    except Exception as e:
        logger.warning(f"Failed to load {filepath.name}: {e}")
        return [] if expected_type == list else {}


def load_books() -> List[Dict]:
    """Load book data from books.json."""
    return load_json_file(BOOKS_FILE, expected_type=list)


def load_categories() -> Dict[str, Dict]:
    """Load category metadata from categories.json."""
    return load_json_file(CATEGORIES_FILE_JSON, expected_type=dict)


# ==========================================================
# Text Processing
# ==========================================================

def clean_text(text: str) -> str:
    """
    Clean and normalize text for similarity comparison.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned lowercase text with only alphanumeric characters
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.
    
    Args:
        text: Text to slugify
        
    Returns:
        Lowercase slug with hyphens
    """
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
