#!/usr/bin/env python3
"""
Copy a v1 project (or the intermediate v1.9 `content/` layout) into the v2 layout.

    python tools/migrate_v1_to_v2.py --from ../old-site --to .            # copy + convert
    python tools/migrate_v1_to_v2.py --from ../old-site --to . --dry-run

What it does (nothing is deleted or overwritten in the OLD project):

    posts/*.md  or content/essays/*.md          -> content/essays/
    book_chapters/<f>/ or content/<f>/          -> content/<f>/
    publications.json or content/collections.json -> content/collections.json
    books.json, reading_notes.json, thoughts.json, videos.json, categories.json
                                                -> content/data/
    images/                                     -> content/assets/images/
    downloads/                                  -> content/assets/downloads/

    front matter:  excerpt -> synopsis,  archived -> lock,  featured removed.

It never touches content/site.json or content/pages/ in the NEW project.
It reports every file with lock/archived = true: in v2 those are not published at all.
"""

import argparse
import json
import re
import shutil
from pathlib import Path

_FM = re.compile(r"\A(\s*---[ \t]*\n)(.*?)(\n---[ \t]*(?:\n|\Z))", re.DOTALL)
_TRUE = ("true", "yes", "1")
DATA_FILES = ["books.json", "reading_notes.json", "thoughts.json", "videos.json", "categories.json"]


def convert_front_matter(text):
    text = text.replace("\r\n", "\n")
    m = _FM.match(text)
    if not m:
        return text, False
    lines, locked, seen = [], False, set()
    for line in m.group(2).splitlines():
        km = re.match(r"^(\s*)([A-Za-z_][\w-]*)(\s*:\s*)(.*)$", line)
        if not km:
            lines.append(line)
            continue
        indent, key, sep, value = km.groups()
        k = key.lower()
        if k == "featured":
            continue
        if k == "excerpt":
            key = k = "synopsis"
        if k == "archived":
            key = k = "lock"
        if k in seen:
            continue
        seen.add(k)
        if k == "lock" and value.strip().strip("\"'").lower() in _TRUE:
            locked = True
        lines.append(f"{indent}{key}{sep}{value}")
    return m.group(1) + "\n".join(lines) + m.group(3) + text[m.end():], locked


class Migrator:
    def __init__(self, old: Path, new: Path, dry: bool):
        self.old, self.new, self.dry = old, new, dry
        self.locked = []

    def log(self, src, dest, note=""):
        print(f"  {src}  ->  {dest}{('  ' + note) if note else ''}")

    def copy_md_folder(self, src: Path, dest: Path):
        if not self.dry:
            dest.mkdir(parents=True, exist_ok=True)
        for f in sorted(src.iterdir()):
            target = dest / f.name
            if f.suffix.lower() == ".md":
                text, locked = convert_front_matter(f.read_text(encoding="utf-8"))
                if locked:
                    self.locked.append(str(target))
                self.log(f, target)
                if not self.dry:
                    target.write_text(text, encoding="utf-8")
            elif f.is_file():
                self.log(f, target, "(as is)")
                if not self.dry:
                    shutil.copy2(f, target)

    def copy_tree(self, src: Path, dest: Path):
        if not src.is_dir():
            return
        count = 0
        for f in src.rglob("*"):
            if f.is_file():
                count += 1
                if not self.dry:
                    t = dest / f.relative_to(src)
                    t.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, t)
        print(f"  {src}  ->  {dest}  ({count} files)")

    def collections_from_publications(self, path: Path):
        data = json.loads(path.read_text(encoding="utf-8"))
        defaults = (data.get("defaults", {}) if isinstance(data, dict) else {}) or {}
        pubs = data.get("publications", []) if isinstance(data, dict) else data
        new_defaults = {k: v for k, v in defaults.items() if k not in ("locked_message", "show_on_home")}
        new_defaults.update({"layout": "chapters", "show_on_home": 0})
        colls = [{"id": "essays", "title": "Essays", "folder": "essays", "layout": "essays",
                  "sort": "descending", "show_on_home": 3, "home_heading": "Recent essays",
                  "synopsis": "", "see_all_label": "Browse all essays →"}]
        for p in pubs:
            c = {k: v for k, v in p.items() if k not in ("locked_message", "show_on_home", "premise")}
            c.update({"layout": "chapters", "sort": "ascending",
                      "show_on_home": 0 if p.get("show_on_home", defaults.get("show_on_home", True)) else False})
            if p.get("premise"):
                c["synopsis"] = p["premise"]
            colls.append(c)
        return {"defaults": new_defaults, "collections": colls}

    def run(self):
        old, new = self.old, self.new
        # ---- markdown ------------------------------------------------------
        essays = next((p for p in (old / "content" / "essays", old / "posts") if p.is_dir()), None)
        if essays:
            print("Essays:")
            self.copy_md_folder(essays, new / "content" / "essays")
        chapter_roots = [old / "content", old / "book_chapters"]
        done = set()
        for root in chapter_roots:
            if not root.is_dir():
                continue
            for folder in sorted(p for p in root.iterdir() if p.is_dir()):
                if folder.name in ("essays", "pages", "data", "assets") or folder.name in done:
                    continue
                done.add(folder.name)
                print(f"{folder.name}:")
                self.copy_md_folder(folder, new / "content" / folder.name)

        # ---- collections.json ---------------------------------------------
        target = new / "content" / "collections.json"
        legacy = old / "content" / "collections.json"
        pubs = old / "publications.json"
        if target.exists():
            print(f"{target} already exists; left alone.")
        elif legacy.exists():
            print(f"collections.json: {legacy} -> {target}")
            if not self.dry:
                shutil.copy2(legacy, target)
        elif pubs.exists():
            print(f"collections.json: converted from {pubs}")
            if not self.dry:
                target.write_text(json.dumps(self.collections_from_publications(pubs), indent=2,
                                             ensure_ascii=False) + "\n", encoding="utf-8")
        else:
            print("No collections.json or publications.json found: write content/collections.json by hand.")

        # ---- data + assets -------------------------------------------------
        print("Data:")
        for name in DATA_FILES:
            src = old / name
            if src.exists():
                self.log(src, new / "content" / "data" / name)
                if not self.dry:
                    (new / "content" / "data").mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, new / "content" / "data" / name)
        print("Assets:")
        self.copy_tree(old / "images", new / "content" / "assets" / "images")
        self.copy_tree(old / "downloads", new / "content" / "assets" / "downloads")

        if self.locked:
            print("\nNOTE: these have lock/archived = true and will NOT be published in v2 "
                  "(v1 showed a locked placeholder page for chapters):")
            for path in self.locked:
                print("  ", path)
        print("\nDone." + (" (dry run, nothing written)" if self.dry else
                           " Next: set the Essays synopsis in content/collections.json, then run  python build.py --strict"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="old", required=True, help="the old project folder")
    ap.add_argument("--to", dest="new", default=".", help="the v2 project folder (default: current)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    Migrator(Path(args.old), Path(args.new), args.dry_run).run()


if __name__ == "__main__":
    main()
