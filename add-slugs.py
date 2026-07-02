#!/usr/bin/env python3

import csv
import os
import re
import argparse
from pathlib import Path

TITLE_PATTERN = re.compile(r'^title:\s*(.*)$', re.IGNORECASE)
SLUG_PATTERN = re.compile(r'^slug:\s*(.*)$', re.IGNORECASE)


def load_csv(csv_file):
    """
    Returns:
        dict: {title: slug}
    """
    title_slug = {}
    errors = []

    with open(csv_file, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        headers = [h.lower() for h in reader.fieldnames]

        if "title" not in headers or "slug" not in headers:
            raise ValueError("CSV must contain 'title' and 'slug' columns.")

        # Map original names
        title_col = reader.fieldnames[headers.index("title")]
        slug_col = reader.fieldnames[headers.index("slug")]

        for row_num, row in enumerate(reader, start=2):
            title = row[title_col].strip()
            slug = row[slug_col].strip()

            if not title:
                errors.append(f"CSV row {row_num}: Empty title")
                continue

            if title in title_slug:
                errors.append(f"Duplicate title in CSV: {title}")
                continue

            title_slug[title] = slug

    return title_slug, errors


def process_markdown(md_file, lookup):
    """
    Updates slug in markdown front matter.
    """
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        return f"{md_file}: Missing YAML front matter."

    parts = content.split("---", 2)

    if len(parts) < 3:
        return f"{md_file}: Invalid front matter."

    front = parts[1].strip("\n")
    body = parts[2]

    lines = front.splitlines()

    title = None
    title_index = None
    slug_index = None

    for i, line in enumerate(lines):
        mt = TITLE_PATTERN.match(line)
        if mt:
            title = mt.group(1).strip().strip('"').strip("'")
            title_index = i

        ms = SLUG_PATTERN.match(line)
        if ms:
            slug_index = i

    if title is None:
        return f"{md_file}: No title found."

    if title not in lookup:
        return f"{md_file}: Title not found in CSV -> '{title}'"

    slug = lookup[title]

    slug_line = f"slug: {slug}"

    if slug_index is not None:
        lines[slug_index] = slug_line
    else:
        lines.insert(title_index + 1, slug_line)

    new_front = "\n".join(lines)
    new_content = f"---\n{new_front}\n---{body}"

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(new_content)

    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("markdown_folder", help="Folder containing markdown files")
    parser.add_argument("csv_file", help="CSV containing title and slug columns")

    args = parser.parse_args()

    try:
        lookup, errors = load_csv(args.csv_file)
    except Exception as e:
        print(f"ERROR reading CSV: {e}")
        return

    print(f"Loaded {len(lookup)} title/slug pairs.\n")

    for error in errors:
        print("CSV ERROR:", error)

    md_files = sorted(Path(args.markdown_folder).glob("*.md"))

    if not md_files:
        print("No markdown files found.")
        return

    updated = 0

    for md in md_files:
        err = process_markdown(md, lookup)

        if err:
            print("ERROR:", err)
        else:
            print(f"Updated: {md.name}")
            updated += 1

    print("\nDone.")
    print(f"Updated: {updated}")
    print(f"Markdown files scanned: {len(md_files)}")


if __name__ == "__main__":
    main()