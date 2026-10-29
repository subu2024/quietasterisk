"""
Markdown -> HTML for entry and page bodies.

The engine owns the markdown dialect; the theme owns the *markup* of the few
things markdown cannot express by itself. Those are macros in the theme's
macros.html, which the engine calls:

    youtube(video_id, title)             for [youtube:VIDEO_ID] tags
    dialogue(speaker, index, html)       for paragraphs that start **Speaker:**
"""

import logging
import re
from pathlib import Path
from typing import Iterable

import markdown
from markupsafe import Markup

from .theme import Theme

logger = logging.getLogger("qa")

_YOUTUBE_TAG_RE = re.compile(r"\[youtube:([a-zA-Z0-9_-]+)\]")
_IMG_RE = re.compile(r"""(<img\b[^>]*?\bsrc=)(['"])(.*?)\2""", re.IGNORECASE)


class Renderer:
    def __init__(self, theme: Theme, images_dir: Path, used_images: set):
        self.images_dir = Path(images_dir)
        self.used_images = used_images           # filenames to copy into dist/images
        self._youtube = theme.macro("youtube")
        self._dialogue = theme.macro("dialogue")

    def _images(self, html: str, origin: str) -> str:
        def fix(match):
            prefix, quote, src = match.groups()
            if re.match(r"^(https?:|//|data:|/|#)", src):
                return match.group(0)
            name = Path(src).name
            if (self.images_dir / name).is_file():
                self.used_images.add(name)
                return f"{prefix}{quote}images/{name}{quote}"
            logger.warning("%s: image %r not found in assets/images.", origin, src)
            return match.group(0)
        return _IMG_RE.sub(fix, html)

    def render(self, body: str, origin: str = "", speakers: Iterable[str] = ()) -> str:
        html = markdown.markdown(body, extensions=["extra", "codehilite"])

        if self._youtube:
            html = _YOUTUBE_TAG_RE.sub(lambda m: str(self._youtube(m.group(1), "YouTube video player")), html)

        speakers = list(speakers or [])
        if speakers and self._dialogue:
            names = "|".join(re.escape(s) for s in speakers)
            order = [s.lower() for s in speakers]
            pattern = re.compile(rf"<p>\s*<strong>({names}):</strong>\s*(.*?)</p>", re.IGNORECASE | re.DOTALL)
            html = pattern.sub(
                lambda m: str(self._dialogue(m.group(1), order.index(m.group(1).lower()), Markup(m.group(2)))), html)

        return self._images(html, origin)
