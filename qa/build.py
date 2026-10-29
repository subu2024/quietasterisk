"""
The build pipeline.

    settings + content  ->  plan (PageSpecs)  ->  theme renders  ->  dist/

Safety: the site is built into a temporary folder and swapped into place only
when the whole build succeeds (and, with --strict, produced no warnings), so a
failed build never leaves a half-written or empty dist/.
"""

import json
import logging
import re
import shutil
from dataclasses import dataclass, field
from datetime import date as date_cls
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import List, Optional
from urllib.parse import unquote

import jinja2

from . import __version__
from .assets import copy_static, copy_tree
from .loaders import load_content
from .models import LAYOUT_ESSAYS
from .pages import (
    FEED_FILE, NOT_FOUND_FILE, ROBOTS_FILE, SITEMAP_FILE, PageSpec, plan_site,
)
from .related import build_related_map
from .render_md import Renderer
from .settings import load_settings
from .theme import Theme, ThemeError

logger = logging.getLogger("qa")

_SYSTEM_TEMPLATES = Path(__file__).with_name("system_templates")


@dataclass
class BuildOptions:
    root: Path = Path(".")
    content_dir: Optional[Path] = None
    themes_dir: Optional[Path] = None
    output_dir: Optional[Path] = None
    theme: Optional[str] = None
    strict: bool = False
    hide_future: Optional[bool] = None
    today: Optional[date_cls] = None

    def resolved(self):
        root = Path(self.root)
        return (Path(self.content_dir or root / "content"),
                Path(self.themes_dir or root / "themes"),
                Path(self.output_dir or root / "dist"))


@dataclass
class BuildResult:
    ok: bool
    pages: int = 0
    warnings: List[str] = field(default_factory=list)
    output: Optional[Path] = None


class _WarningCollector(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)   # records WARNING only (not the strict-mode ERROR)
        self.messages: List[str] = []

    def emit(self, record):
        if record.levelno == logging.WARNING:
            self.messages.append(record.getMessage())


def _system_env() -> jinja2.Environment:
    return jinja2.Environment(loader=jinja2.FileSystemLoader(str(_SYSTEM_TEMPLATES)),
                              autoescape=jinja2.select_autoescape(["xml", "html", "j2"], default=True),
                              trim_blocks=True, lstrip_blocks=True)


def _write(root: Path, rel: str, text: str) -> None:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _page_meta(spec: PageSpec, site: dict, images_dir: Path) -> dict:
    base = site["url"]
    canonical = f"{base}/" if spec.url == "index.html" else f"{base}/{spec.url}"
    image_name = spec.image if spec.image and (images_dir / spec.image).is_file() else ""
    image_name = image_name or site.get("og_image_file", "")
    ld = json.dumps(spec.jsonld, ensure_ascii=False).replace("</", "<\\/") if spec.jsonld else ""
    full_title = f"{spec.title} - {site['title']}"
    return {
        "title": full_title, "heading": spec.title, "description": spec.description or site["tagline"],
        "canonical": canonical, "og_type": spec.og_type,
        "image_url": f"{base}/images/{image_name}" if image_name else "",
        "section": spec.section, "noindex": spec.noindex, "jsonld_json": ld, "url": spec.url,
    }


def _check_links(root: Path) -> None:
    """Warn about internal links and assets that point at files that do not exist."""
    ref = re.compile(r"""(?:href|src)=["']([^"']+)["']""", re.IGNORECASE)
    for html_file in sorted(root.rglob("*.html")):
        text = html_file.read_text(encoding="utf-8", errors="ignore")
        seen = set()
        for value in ref.findall(text):
            if re.match(r"^(https?:|//|mailto:|tel:|#|javascript:|data:)", value):
                continue
            path = unquote(re.split(r"[#?]", value, maxsplit=1)[0])
            if not path or path in seen:
                continue
            seen.add(path)
            if not (root / path).exists():
                logger.warning("Broken link in %s: %s", html_file.relative_to(root).as_posix(), value)


def build(opts: BuildOptions) -> BuildResult:
    content_dir, themes_dir, output = opts.resolved()
    collector = _WarningCollector()
    logger.addHandler(collector)
    tmp = output.with_name(output.name + ".building")
    try:
        if tmp.exists():
            shutil.rmtree(tmp)
        tmp.mkdir(parents=True)

        settings = load_settings(content_dir)
        theme_name = opts.theme or settings["theme"]
        theme = Theme(themes_dir / theme_name, strict_undefined=opts.strict)
        logger.info("Engine %s, theme %r", __version__, theme.name)

        content = load_content(content_dir, settings, today=opts.today, hide_future=opts.hide_future)

        # ---- assets -------------------------------------------------------
        images = copy_tree(content_dir / "assets" / "images", tmp / "images")
        downloads = copy_tree(content_dir / "assets" / "downloads", tmp / "downloads")
        theme.set_static_resolver(copy_static(theme.static_dir, tmp / "static"))
        logger.info("Copied %d image(s), %d download(s)", images, downloads)

        # ---- plan + render markdown bodies ---------------------------------
        plan = plan_site(content)
        images_dir = content_dir / "assets" / "images"
        if settings["logo"] and not (images_dir / settings["logo"]).is_file():
            logger.warning("site.json logo %r not found in assets/images; the logo is left out.", settings["logo"])
            plan.site["logo_url"] = ""
        og = settings["og_image"] or settings["logo"]
        plan.site["og_image_file"] = og if og and (images_dir / og).is_file() else ""

        renderer = Renderer(theme, images_dir, set())
        for coll in content.collections:
            for entry in coll.entries:
                entry.body_html = renderer.render(entry.body, entry.path.name, coll.speakers)
        for doc in content.pages.values():
            doc.body_html = renderer.render(doc.body, doc.path.name)

        related = build_related_map(content.essays, float(settings["publishing"]["similarity_threshold"]),
                                    int(settings["publishing"]["related_count"]))
        for spec in plan.pages:
            entry = spec.context.get("entry")
            if entry is not None and entry.layout == LAYOUT_ESSAYS:
                spec.context["related"] = related.get(entry.url, [])

        # ---- 404 (optional theme template) ---------------------------------
        if theme.has_template(NOT_FOUND_FILE):
            plan.pages.append(PageSpec(url=NOT_FOUND_FILE, template=NOT_FOUND_FILE, title="Page not found",
                                       noindex=True, in_sitemap=False, context={}))

        # ---- URL collisions ------------------------------------------------
        owners = {}
        for spec in plan.pages:
            if spec.url in owners:
                logger.warning("URL clash: %r and %r both produce %s; one will overwrite the other.",
                               owners[spec.url], spec.title, spec.url)
            owners[spec.url] = spec.title
        for redirect in plan.redirects:
            if redirect.url in owners:
                logger.warning("Redirect %s collides with the page %r; the redirect wins.", redirect.url, owners[redirect.url])
            if redirect.target.split("#")[0] not in owners:
                logger.warning("Redirect %s points to %s, which is not a page on this site.", redirect.url, redirect.target)

        # ---- render pages --------------------------------------------------
        for spec in plan.pages:
            template = spec.template
            if not theme.has_template(template):
                if template.startswith("page_"):
                    logger.info("Theme %r has no %s; using page_default.html.", theme.name, template)
                    template = "page_default.html"
                else:
                    raise ThemeError(f"Theme {theme.name!r} has no template {template}")
            ctx = {"site": plan.site, "urls": plan.urls, "page": _page_meta(spec, plan.site, images_dir)}
            ctx.update(spec.context)
            _write(tmp, spec.url, theme.render(template, ctx))

        # ---- machine-readable files (engine-owned, theme-independent) -------
        sys_env = _system_env()
        for redirect in plan.redirects:
            _write(tmp, redirect.url, sys_env.get_template("redirect.html.j2").render(site=plan.site, target=redirect.target))

        sitemap_pages = [{"loc": f"{plan.site['url']}/{'' if s.url == 'index.html' else s.url}", "lastmod": s.lastmod}
                         for s in plan.pages if s.in_sitemap and not s.noindex]
        _write(tmp, SITEMAP_FILE, sys_env.get_template("sitemap.xml.j2").render(pages=sitemap_pages))
        _write(tmp, ROBOTS_FILE, sys_env.get_template("robots.txt.j2").render(site=plan.site, sitemap_file=SITEMAP_FILE))
        if plan.feed_entries:
            items = []
            for e in plan.feed_entries:
                d = e.parsed_date
                items.append({"title": e.title, "url": e.url, "synopsis": e.synopsis, "category": e.category,
                              "pub_date": format_datetime(d.replace(tzinfo=timezone.utc)) if d else ""})
            _write(tmp, FEED_FILE, sys_env.get_template("feed.xml.j2").render(
                site=plan.site, items=items, feed_file=FEED_FILE,
                built=format_datetime(datetime.now(timezone.utc))))

        _check_links(tmp)

        # ---- swap into place ----------------------------------------------
        if opts.strict and collector.messages:
            shutil.rmtree(tmp, ignore_errors=True)
            logger.error("Strict mode: %d warning(s); the existing %s was left untouched.", len(collector.messages), output)
            return BuildResult(ok=False, pages=len(plan.pages), warnings=list(collector.messages))

        old = output.with_name(output.name + ".old")
        if old.exists():
            shutil.rmtree(old)
        if output.exists():
            output.rename(old)
        tmp.rename(output)
        shutil.rmtree(old, ignore_errors=True)

        logger.info("✓ %d pages, %d redirects, %d warning(s) → %s",
                    len(plan.pages), len(plan.redirects), len(collector.messages), output)
        return BuildResult(ok=True, pages=len(plan.pages), warnings=list(collector.messages), output=output)
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    finally:
        logger.removeHandler(collector)
