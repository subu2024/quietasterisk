#!/usr/bin/env python3
"""
update_markdown_from_csv.py

Reads a CSV of article metadata (title, category, summary, slug, archive) and
applies it to a folder of markdown blog posts by matching on title.

For each .md file:
  - Reads any existing YAML front matter (the --- ... --- block at the top).
  - If the file's title matches a row in the CSV (case/whitespace-insensitive),
    updates (or adds) the category, summary, slug, and archive fields in the
    front matter.
  - Leaves the rest of the file (the actual article body) completely untouched.
  - Writes the file back in place.

If a file has no front matter yet, one is created using the title pulled from
the first "# Heading" line, and the body is left as-is below it.

Usage:
    python update_markdown_from_csv.py --csv blog_articles_categorized.csv --folder ./posts

    (both flags are optional if you edit the defaults below)
"""

import argparse
import csv
import re
from pathlib import Path

import yaml

# ---- Defaults (edit these if you'd rather not pass CLI flags) -------------
DEFAULT_CSV = "article_synopses.csv"
DEFAULT_FOLDER = "./posts"
# -----------------------------------------------------------------------


def normalize_title(title: str) -> str:
    """Lowercase, collapse whitespace, strip punctuation for fuzzy matching."""
    title = title.strip().lower()
    title = re.sub(r"[^\w\s]", "", title)   # drop punctuation
    title = re.sub(r"\s+", " ", title)      # collapse whitespace
    return title.strip()


def load_csv_lookup(csv_path: Path) -> dict:
    """Return {normalized_title: row_dict} from the CSV."""
    lookup = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = normalize_title(row["title"])
            lookup[key] = row
    return lookup


FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n?", re.DOTALL)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def split_front_matter(text: str):
    """
    Split a markdown file into (front_matter_dict, body_text, had_front_matter).
    If there's no front matter block, front_matter_dict is an empty dict and
    the whole file is treated as body.
    """
    match = FRONT_MATTER_RE.match(text)
    if match:
        raw_fm = match.group(1)
        body = text[match.end():]
        try:
            fm = yaml.safe_load(raw_fm) or {}
        except yaml.YAMLError:
            # Front matter exists but isn't valid YAML -- don't touch the file.
            return None, text, False
        return fm, body, True
    return {}, text, False


def get_title(front_matter: dict, body: str) -> str:
    """Prefer a 'title' key in front matter, otherwise fall back to the first H1."""
    if front_matter and front_matter.get("title"):
        return str(front_matter["title"])
    h1 = H1_RE.search(body)
    if h1:
        return h1.group(1)
    return ""


def build_output(front_matter: dict, body: str) -> str:
    """Re-serialize front matter (preserving key order) + original body."""
    dumped = yaml.dump(
        front_matter,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )
    return f"---\n{dumped}---\n{body}"


def main():
    parser = argparse.ArgumentParser(description="Sync CSV metadata into markdown front matter.")
    parser.add_argument("--csv", default=DEFAULT_CSV, help="Path to the CSV file")
    parser.add_argument("--folder", default=DEFAULT_FOLDER, help="Folder containing .md files")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    folder = Path(args.folder)

    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")
    if not folder.exists():
        raise SystemExit(f"Markdown folder not found: {folder}")

    lookup = load_csv_lookup(csv_path)
    md_files = sorted(folder.rglob("*.md"))

    updated, unchanged, unmatched, unreadable = [], [], [], []
    matched_titles = set()

    for path in md_files:
        text = path.read_text(encoding="utf-8")
        front_matter, body, had_fm = split_front_matter(text)

        if front_matter is None:
            unreadable.append(path.name)
            continue

        title = get_title(front_matter, body)
        if not title:
            unmatched.append(path.name)
            continue

        row = lookup.get(normalize_title(title))
        if not row:
            unmatched.append(path.name)
            continue

        matched_titles.add(normalize_title(title))

        new_fm = dict(front_matter)  # preserve existing keys/order
        new_fm.setdefault("title", title)
        #new_fm["category"] = row["category"]
        new_fm["excerpt"] = row["summary"]
        #new_fm["slug"] = row["slug"]
        #new_fm["archived"] = row["archive"].strip().lower() == "true"

        if new_fm == front_matter:
            unchanged.append(path.name)
            continue

        if not args.dry_run:
            path.write_text(build_output(new_fm, body), encoding="utf-8")
        updated.append(path.name)

    csv_titles_not_found = [
        row["title"] for key, row in lookup.items() if key not in matched_titles
    ]

    # ---- Summary -------------------------------------------------------
    print("=" * 60)
    print("UPDATE SUMMARY")
    print("=" * 60)
    print(f"Markdown files scanned:        {len(md_files)}")
    print(f"Updated:                       {len(updated)}")
    print(f"Already up to date (no change):{len(unchanged)}")
    print(f"No title match found in CSV:   {len(unmatched)}")
    print(f"Skipped (invalid front matter):{len(unreadable)}")
    print(f"CSV rows with no matching file:{len(csv_titles_not_found)}")
    if args.dry_run:
        print("\n(DRY RUN -- no files were actually written)")

    if updated:
        print("\nUpdated files:")
        for name in updated:
            print(f"  - {name}")

    if unmatched:
        print("\nFiles with no matching CSV title (left untouched):")
        for name in unmatched:
            print(f"  - {name}")

    if csv_titles_not_found:
        print("\nCSV titles with no corresponding markdown file:")
        for title in csv_titles_not_found:
            print(f"  - {title}")

    if unreadable:
        print("\nFiles skipped due to unparsable front matter (fix manually):")
        for name in unreadable:
            print(f"  - {name}")


if __name__ == "__main__":
    main()