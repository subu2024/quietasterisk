"""End-to-end builds of the fixture site through every theme."""
import json
import re
import xml.etree.ElementTree as ET

import pytest

from conftest import read

THEMES = ["quiet", "bold", "minimal"]
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


# ---- homepage: featured piece, home toggles, menu ---------------------------------------------------

def edit_json(path, change):
    cfg = json.loads(path.read_text(encoding="utf-8"))
    change(cfg)
    path.write_text(json.dumps(cfg), encoding="utf-8")


def feature(content_dir, page, **extra):
    edit_json(content_dir / "site.json",
              lambda c: c["home"].update(featured={"enabled": True, "page": page, **extra}))


@pytest.mark.parametrize("theme", THEMES)
def test_featured_piece_is_shown_in_full_in_every_theme(run_build, content_dir, theme):
    feature(content_dir, "memories-of-another-day.html", heading="Poem of the moment")
    result = run_build(theme=theme, hide_future=True, today=TODAY)
    assert result.ok, result.warnings
    home = read(result, "index.html")
    assert "<p>Poem.</p>" in home and "Memories of Another Day" in home and "Poem of the moment" in home
    assert 'href="memories-of-another-day.html"' in home          # link to its own page
    assert (result.output / "memories-of-another-day.html").exists()   # the page itself is unchanged


@pytest.mark.parametrize("theme", THEMES)
def test_featured_piece_off_by_default_and_when_disabled(run_build, content_dir, theme):
    assert "<p>Poem.</p>" not in read(run_build(theme=theme, hide_future=True, today=TODAY), "index.html")
    feature(content_dir, "memories-of-another-day.html")
    edit_json(content_dir / "site.json", lambda c: c["home"]["featured"].update(enabled=False))
    assert "<p>Poem.</p>" not in read(run_build(theme=theme, hide_future=True, today=TODAY), "index.html")


def test_featured_page_name_is_forgiving(run_build, content_dir):
    for name in ("memories-of-another-day", "  Memories-Of-Another-Day.html "):
        feature(content_dir, name)
        assert "<p>Poem.</p>" in read(run_build(hide_future=True, today=TODAY), "index.html")


def test_featured_essay_is_not_listed_twice(run_build, content_dir):
    feature(content_dir, "who-would-cry.html")
    home = read(run_build(hide_future=True, today=TODAY), "index.html")
    assert home.count("Body one about death and noticing.") == 1                      # shown in full once
    assert home.count('class="qa-essay"') == 1 and 'href="who-would-cry.html" class="qa-essay"' not in home


@pytest.mark.parametrize("page", ["secret-essay.html", "future-essay.html", "no-such-page.html", ""])
def test_featured_locked_future_or_missing_is_never_shown(run_build, content_dir, page):
    feature(content_dir, page)
    strict = run_build(hide_future=True, today=TODAY)
    assert not strict.ok and any("home.featured" in w for w in strict.warnings)     # strict names the problem
    lenient = run_build(strict=False, hide_future=True, today=TODAY)
    assert lenient.ok and (lenient.output / "index.html").exists()                    # normal build still works
    everything = "".join(p.read_text(encoding="utf-8") for p in lenient.output.glob("*.html"))
    assert "Should not publish either." not in everything and 'id="featured"' not in read(lenient, "index.html")


def test_homepage_items_can_be_hidden_but_stay_in_the_menu(run_build, content_dir):
    def hide(cfg):
        for c in cfg["collections"]:
            if c["id"] in ("essays", "sunday_odds", "life_is_happenning"):
                c["show_on_home"] = False
    edit_json(content_dir / "collections.json", hide)
    edit_json(content_dir / "site.json", lambda c: c.update(
        thoughts={"show_on_home": False},
        nav=[{"label": "Essays", "page": "essays"}, {"label": "Sunday Odds", "page": "sunday_odds"},
             {"label": "Daily Thoughts", "page": "thoughts"}]))
    result = run_build(hide_future=True, today=TODAY)
    assert result.ok, result.warnings
    home = read(result, "index.html")
    for gone in ('id="essays"', 'class="qa-essay"', 'id="sunday_odds"', 'id="life_is_happenning"', 'id="daily-thought"'):
        assert gone not in home, gone
    for page in ("essays.html", "series.html", "thoughts.html"):          # pages still built...
        assert (result.output / page).exists()
        assert f'href="{page}" class="nav-link' in home                   # ...and still in the menu


def test_daily_thought_shows_on_home_by_default(run_build):
    assert 'id="daily-thought"' in read(run_build(hide_future=True, today=TODAY), "index.html")


def test_menu_can_list_collections_and_highlights_them(run_build, content_dir):
    edit_json(content_dir / "site.json", lambda c: c.update(
        nav=[{"label": "Sunday Odds", "page": "sunday_odds"}, {"label": "Poems", "page": "pocket_poems"}]))
    result = run_build(hide_future=True, today=TODAY)
    chapter = read(result, "series-01-plan-for-the-bad-month.html")
    assert 'href="series.html" class="nav-link active"' in chapter
    assert 'href="book-pocket-poems.html" class="nav-link"' in chapter
    assert 'href="book-pocket-poems.html" class="nav-link active"' in read(result, "memories-of-another-day.html")
