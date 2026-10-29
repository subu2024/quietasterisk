"""End-to-end builds of the fixture site through every theme."""
import json
import re
import xml.etree.ElementTree as ET

import pytest

from conftest import read

THEMES = ["quiet", "minimal"]
BUILD = dict(hide_future=True)
from datetime import date
TODAY = date(2026, 12, 31)


@pytest.mark.parametrize("theme", THEMES)
def test_strict_build_is_clean_for_every_theme(run_build, theme):
    result = run_build(theme=theme, hide_future=True, today=TODAY)
    assert result.ok, result.warnings
    assert result.warnings == []


def test_locked_future_and_archived_never_published(run_build):
    result = run_build(hide_future=True, today=TODAY)
    files = {p.name for p in result.output.iterdir()}
    assert not files & {"secret-essay.html", "old-draft.html", "series-10-later.html", "future-essay.html"}
    assert "LOCKED BODY" not in "".join(p.read_text() for p in result.output.glob("*.html"))
    assert "secret-essay" not in read(result, "sitemap.xml")


def test_homepage_blocks(run_build):
    result = run_build(hide_future=True, today=TODAY)
    home = read(result, "index.html")
    assert home.count('class="qa-essay"') == 2                                   # essays: top 2
    assert 'id="sunday_odds"' in home and "qa-series-card" in home               # show_on_home 0 -> card
    assert 'id="pocket_poems"' not in home                                       # hidden
    assert home.index('id="sunday_odds"') < home.index('id="daily-thought"') < home.index('id="life_is_happenning"')
    assert "Subscribe" in home                                                   # newsletter configured


def test_sort_flip_changes_homepage_and_year_order(run_build, content_dir):
    first = lambda html: re.findall(r'class="qa-essay" href="([^"]+)"', html)[0]
    newest = first(read(run_build(hide_future=True, today=TODAY), "index.html"))
    cfg = json.loads((content_dir / "collections.json").read_text())
    cfg["collections"][0]["sort"] = "ascending"
    (content_dir / "collections.json").write_text(json.dumps(cfg))
    result = run_build(hide_future=True, today=TODAY)
    assert first(read(result, "index.html")) != newest
    years = re.findall(r'id="year-(\d{4})"', read(result, "essays.html"))
    assert years == sorted(years)


def test_machine_files_are_valid(run_build):
    result = run_build(hide_future=True, today=TODAY)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [e.text for e in ET.fromstring(read(result, "sitemap.xml")).findall("s:url/s:loc", ns)]
    assert "https://www.quietasterisk.com/" in locs and "https://www.quietasterisk.com/who-would-cry.html" in locs
    assert not any("archives" in l or "reading.html" in l or "404" in l for l in locs)
    items = ET.fromstring(read(result, "feed.xml")).findall("channel/item")
    assert items and items[0].find("link").text.endswith(".html")
    assert "Sitemap: https://www.quietasterisk.com/sitemap.xml" in read(result, "robots.txt")


def test_redirects_and_aliases(run_build):
    result = run_build(hide_future=True, today=TODAY)
    assert 'url=your-gut-is-witness.html' in read(result, "old-gut.html")
    assert 'url=essays.html' in read(result, "archives.html")
    assert 'url=books.html#reading-notes' in read(result, "reading.html")


def test_seo_metadata(run_build):
    page = read(run_build(hide_future=True, today=TODAY), "your-gut-is-witness.html")
    assert 'rel="canonical" href="https://www.quietasterisk.com/your-gut-is-witness.html"' in page
    assert 'property="og:type" content="article"' in page and 'og:image' in page
    ld = json.loads(re.search(r'application/ld\+json">(.*?)</script>', page, re.S).group(1))
    assert ld["@type"] == "BlogPosting" and ld["datePublished"] == "2026-10-10"


def test_html_is_escaped_automatically(run_build):
    result = run_build(hide_future=True, today=TODAY)
    assert "&lt;b&gt;" in read(result, "books.html") and "<b>." not in read(result, "books.html")
    assert "Self-Awareness &amp; EQ" in read(result, "essays.html")


def test_markdown_extras(run_build):
    result = run_build(hide_future=True, today=TODAY)
    gut = read(result, "your-gut-is-witness.html")
    assert 'src="images/inline.png"' in gut and "youtube.com" in gut
    chapter = read(result, "series-01-plan-for-the-bad-month.html")
    assert "dialogue" in chapter or "Revathi:" in chapter
    about = read(result, "about.html")
    assert 'class="letter-heading"' in about and 'class="letter-signoff"' in about


def test_chapter_navigation_follows_sort(run_build, content_dir):
    cfg = json.loads((content_dir / "collections.json").read_text())
    cfg["collections"][1]["sort"] = "descending"
    (content_dir / "collections.json").write_text(json.dumps(cfg))
    result = run_build(hide_future=True, today=TODAY)
    page = read(result, "series-02-how-big.html")
    assert re.search(r'href="series-03-third.html"[^>]*rel="prev"', page)
    assert re.search(r'href="series-01-plan-for-the-bad-month.html"[^>]*rel="next"', page)
    assert "Chapter 2 of 3" in page
    assert 'href="series-01-plan-for-the-bad-month.html" class="btn btn-primary">Start' in read(result, "series.html")


def test_theme_templates_have_no_inline_styles(run_build):
    result = run_build(hide_future=True, today=TODAY)
    for name in ("index.html", "essays.html", "books.html", "categories.html", "contact.html", "series.html"):
        assert ' style="' not in read(result, name), name


def test_broken_link_fails_strict_and_keeps_old_output(run_build, content_dir):
    good = run_build(hide_future=True, today=TODAY)
    assert good.ok
    marker = good.output / "marker.txt"
    marker.write_text("previous build")
    (content_dir / "pages" / "about.md").write_text("---\ntitle: About\ntemplate: letter\n---\n[x](nowhere.html)\n")
    bad = run_build(hide_future=True, today=TODAY)
    assert not bad.ok and any("nowhere.html" in w for w in bad.warnings)
    assert marker.exists(), "a failed strict build must not touch the existing output"


def test_non_strict_build_reports_but_publishes(run_build, content_dir):
    (content_dir / "pages" / "about.md").write_text("---\ntitle: About\ntemplate: letter\n---\n[x](nowhere.html)\n")
    result = run_build(strict=False, hide_future=True, today=TODAY)
    assert result.ok and result.warnings and (result.output / "about.html").exists()
