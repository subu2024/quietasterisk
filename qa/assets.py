"""Asset handling: content images and downloads, and the theme's static files."""

import hashlib
import shutil
from pathlib import Path
from typing import Callable


def copy_tree(src: Path, dest: Path) -> int:
    """Copy every file under src into dest (keeping sub-folders). Returns the file count."""
    if not src.is_dir():
        return 0
    count = 0
    for item in src.rglob("*"):
        if item.is_file() and not item.name.startswith("."):
            target = dest / item.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            count += 1
    return count


def copy_static(theme_static: Path, dest: Path) -> Callable[[str], str]:
    """
    Copy the theme's static folder to dest and return a resolver for templates:
    static('css/style.css') -> 'static/css/style.css?v=<content hash>', so a
    changed stylesheet is never served from a stale browser cache.
    """
    copy_tree(theme_static, dest)
    hashes = {}
    for f in dest.rglob("*"):
        if f.is_file():
            hashes[f.relative_to(dest).as_posix()] = hashlib.sha1(f.read_bytes()).hexdigest()[:8]

    def resolve(path: str) -> str:
        path = path.lstrip("/")
        version = hashes.get(path)
        return f"static/{path}" + (f"?v={version}" if version else "")
    return resolve
