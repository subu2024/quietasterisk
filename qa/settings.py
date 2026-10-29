"""
Site settings: content/site.json layered over qa/default_site.json.

Everything about the site's identity and text lives in site.json (title,
tagline, nav, social links, newsletter, page copy, redirects...), never in
code and never in a theme. Environment overrides, for deploy-time values:

    BLOG_SITE_URL                 site.url
    BLOG_NEWSLETTER_API_ENDPOINT  site.newsletter.endpoint
"""

import copy
import difflib
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger("qa")

_DEFAULTS_FILE = Path(__file__).with_name("default_site.json")

# Sections whose keys are free-form (not checked for typos).
_FREE_FORM = {"copy", "redirects"}


def _merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in over.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def _warn_unknown(defaults: dict, user: dict, where: str = "site.json") -> None:
    for key, value in user.items():
        if key not in defaults:
            hint = difflib.get_close_matches(key, defaults.keys(), n=1)
            logger.warning("%s: unknown setting %r%s", where, key,
                           f" (did you mean {hint[0]!r}?)" if hint else "")
        elif isinstance(value, dict) and isinstance(defaults[key], dict) and key not in _FREE_FORM:
            _warn_unknown(defaults[key], value, f"{where}.{key}")


def load_settings(content_dir: Path) -> dict:
    """Return the merged settings dict (defaults < site.json < environment)."""
    defaults = json.loads(_DEFAULTS_FILE.read_text(encoding="utf-8"))
    user: dict = {}
    path = Path(content_dir) / "site.json"
    if path.exists():
        try:
            user = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise SystemExit(f"Cannot read {path}: {e}")
        _warn_unknown(defaults, user)
    else:
        logger.warning("%s not found; using built-in defaults.", path)

    settings = _merge(defaults, user)
    if os.environ.get("BLOG_SITE_URL"):
        settings["url"] = os.environ["BLOG_SITE_URL"]
    if os.environ.get("BLOG_NEWSLETTER_API_ENDPOINT"):
        settings["newsletter"]["endpoint"] = os.environ["BLOG_NEWSLETTER_API_ENDPOINT"]
    settings["url"] = settings["url"].rstrip("/")
    return settings
