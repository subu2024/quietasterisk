#!/usr/bin/env python3
"""
Quiet Asterisk Blog Generator (Refactored v8.0)
Main entry point for generating the static blog site.

Usage:
    python generate_blog.py
    python generate_blog.py --write-temp
"""

import shutil
import logging
import argparse

from config import OUTPUT_DIR, IMAGE_DIR, INPUT_DIR, TEMP_CONTENT_FILE
from parser import read_markdown_files
from similarity import compute_similarity, build_related_map
from utils import copy_downloads
from generators import (
    generate_index,
    generate_books,
    generate_videos,
    generate_categories,
    generate_about,
    generate_contact,
    get_temp_content
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BlogGen")


def main(write_temp: bool = False):
    """
    Main function to generate the entire blog site.
    
    Args:
        write_temp: Whether to write temporary content file for debugging
    """
    logger.info("Generating blog with modern design...")

    # Clean and create output directory
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)
    IMAGE_DIR.mkdir(exist_ok=True)
    

    # Copy downloadable files
    logger.info("Copying downloadable files...")
    files_copied = copy_downloads()


    # Read all markdown posts
    posts = read_markdown_files(INPUT_DIR)
    
    if not posts:
        logger.warning("No posts found. Check your markdown files in the input directory.")
    
    # Compute similarity matrix for related posts
    sim_matrix = compute_similarity(posts) if len(posts) > 1 else []
    related_map = build_related_map(posts, sim_matrix) if len(posts) > 1 else {}

    # Generate all pages
    logger.info("Generating index page...")
    generate_index(posts, related_map)
    
    logger.info("Generating books page...")
    generate_books()

    logger.info("Generating videos page...")  # Add this
    generate_videos()   
    
    logger.info("Generating categories pages...")
    generate_categories(posts)
    
    logger.info("Generating about page...")
    generate_about()
    
    logger.info("Generating contact page...")
    generate_contact()

    # Write temporary content if requested
    if write_temp:
        with open(TEMP_CONTENT_FILE, "w", encoding="utf-8") as f:
            f.write(get_temp_content())
        logger.info(f"Wrote temporary content to {TEMP_CONTENT_FILE}")

    # Summary
    logger.info(f"✓ Generated {len(posts)} blog posts successfully")
    logger.info(f"✓ Output directory: {OUTPUT_DIR.absolute()}")
    logger.info("✓ Blog generation complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate the Quiet Asterisk blog from markdown files"
    )
    parser.add_argument(
        "--write-temp",
        action="store_true",
        help="Write temporary content file for debugging"
    )
    args = parser.parse_args()
    
    main(write_temp=args.write_temp)
