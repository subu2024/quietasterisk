"""
Theme loading: the boundary between the engine and the presentation layer.

A theme is a folder:

    themes/<name>/
      theme.json        {"name": ..., "version": ..., "contract": 2}
      templates/        Jinja2 templates (the required set is REQUIRED_TEMPLATES)
      static/           css / js / fonts / images, copied to dist/static/

The engine only ever talks to a theme through render() and macro(); see
docs/THEME_CONTRACT.md for every template and the variables it receives.
"""

import json
import logging
from pathlib import Path
from typing import Callable, Dict, List

import jinja2

from . import THEME_CONTRACT_VERSION

logger = logging.getLogger("qa")

REQUIRED_TEMPLATES = [
    "base.html", "macros.html",
    "home.html", "entry.html", "collection.html",
    "essays.html", "categories.html", "category.html",
    "books.html", "thoughts.html", "videos.html",
    "page_default.html",
]


class ThemeError(Exception):
    pass


class Theme:
    def __init__(self, path: Path, strict_undefined: bool = False):
        self.path = Path(path)
        manifest_file = self.path / "theme.json"
        if not manifest_file.is_file():
            raise ThemeError(f"{self.path} is not a theme: theme.json is missing.")
        try:
            self.manifest: Dict = json.loads(manifest_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ThemeError(f"{manifest_file}: {e}")
        self.name = self.manifest.get("name", self.path.name)

        contract = self.manifest.get("contract")
        if contract != THEME_CONTRACT_VERSION:
            raise ThemeError(
                f"Theme {self.name!r} targets contract {contract!r}, but this engine provides "
                f"contract {THEME_CONTRACT_VERSION}. See docs/THEME_CONTRACT.md.")

        self.templates_dir = self.path / "templates"
        self.static_dir = self.path / "static"
        missing = [t for t in REQUIRED_TEMPLATES if not (self.templates_dir / t).is_file()]
        if missing:
            raise ThemeError(f"Theme {self.name!r} is missing required templates: {', '.join(missing)}")

        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_dir)),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
            undefined=jinja2.StrictUndefined if strict_undefined else jinja2.Undefined,
            trim_blocks=True, lstrip_blocks=True,
        )
        self.env.globals["static"] = lambda p: f"static/{p}"   # replaced by the build (adds a cache-busting hash)

    def has_template(self, name: str) -> bool:
        return (self.templates_dir / name).is_file()

    def set_static_resolver(self, fn: Callable[[str], str]) -> None:
        self.env.globals["static"] = fn

    def render(self, template: str, context: dict) -> str:
        try:
            return self.env.get_template(template).render(**context)
        except jinja2.TemplateError as e:
            raise ThemeError(f"Theme {self.name!r}, template {template}: {e}") from e

    def macro(self, name: str, template: str = "macros.html"):
        """A macro from the theme (for the few snippets the engine inserts into markdown)."""
        module = self.env.get_template(template).make_module({})
        return getattr(module, name, None)
