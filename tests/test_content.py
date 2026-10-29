"""Content layer: parsing, lock, sort, numbering, URLs, show_on_home."""
import json
import logging
from datetime import date

from qa import frontmatter
from qa.loaders import load_content, normalize_page_name
from qa.models import title_slug
from qa.settings import load_settings


def load(content_dir, **kw):
    return load_content(content_dir, load_settings(content_dir), **kw)


def coll(content, cid):
    return next(c for c in content.collections if c.id == cid)


def test_front_matter_keeps_horizontal_rules_in_body():
    meta, body = frontmatter.parse("---\ntitle: \"Hi\"\nlock: yes\n---\nOne\n\n---\n\nTwo")
    assert meta == {"title": "Hi", "lock": "yes"}
    assert "---" in body and body.endswith("Two")


def test_lock_and_archived_are_not_published(content_dir):
    titles = {e.title for e in load(content_dir).all_entries}
    assert "Secret Essay" not in titles and "Old Draft" not in titles and "Later" not in titles


def test_numbers_skip_locked_chapters(content_dir):
    nums = [(e.number, e.title) for e in sorted(coll(load(content_dir), "sunday_odds").entries, key=lambda e: e.number)]
    assert nums == [(1, "Plan for the Bad Month"), (2, "How Big Is Big Enough"), (3, "Third")]


def test_descending_reverses_order_but_not_numbers(content_dir):
    cfg = json.loads((content_dir / "collections.json").read_text())
    cfg["collections"][1]["sort"] = "descending"
    (content_dir / "collections.json").write_text(json.dumps(cfg))
    c = coll(load(content_dir), "sunday_odds")
    assert [e.number for e in c.entries] == [3, 2, 1]
    assert c.start_entry.number == 1


def test_essays_default_to_newest_first(content_dir):
    dates = [e.date for e in coll(load(content_dir), "essays").entries]
    assert dates == sorted(dates, reverse=True)


def test_url_rules(content_dir):
    content = load(content_dir)
    urls = {e.title: e.url for e in content.all_entries}
    assert urls["Who Would Cry?"] == "who-would-cry.html"                       # from title
    assert urls["Your Gut Is a Witness, Not a Judge"] == "your-gut-is-witness.html"  # slug:
    assert urls["Plan for the Bad Month"] == "series-01-plan-for-the-bad-month.html"  # prefix + file
    assert urls["Memories of Another Day"] == "memories-of-another-day.html"


def test_page_name_normalizing():
    assert normalize_page_name("my slug") == "my-slug.html"
    assert normalize_page_name("page.html") == "page.html"
    assert normalize_page_name("../evil") == "" and normalize_page_name(".hidden") == ""
    assert title_slug("Don't Panic") == "don-t-panic"


def test_aliases_are_parsed(content_dir):
    gut = next(e for e in load(content_dir).all_entries if e.title.startswith("Your Gut"))
    assert gut.aliases == ["old-gut.html"]


def test_future_dated_hidden_only_when_asked(content_dir):
    assert "Future Essay" in {e.title for e in load(content_dir, hide_future=False).all_entries}
    hidden = load(content_dir, hide_future=True, today=date(2026, 12, 31))
    assert "Future Essay" not in {e.title for e in hidden.all_entries}
    assert "Who Would Cry?" in {e.title for e in hidden.all_entries}   # dated 2026-11-01


def test_show_on_home_values(content_dir):
    content = load(content_dir)
    assert coll(content, "essays").show_on_home == 2 and len(coll(content, "essays").home_entries) == 2
    assert coll(content, "sunday_odds").show_on_home == 0 and coll(content, "sunday_odds").home_entries == []
    assert coll(content, "pocket_poems").show_on_home is None


def test_unknown_keys_warn_with_suggestion(content_dir, caplog):
    cfg = json.loads((content_dir / "collections.json").read_text())
    cfg["collections"][0]["show_on_hom"] = 3
    (content_dir / "collections.json").write_text(json.dumps(cfg))
    with caplog.at_level(logging.WARNING, logger="qa"):
        load(content_dir)
    assert any("show_on_hom" in r.message and "show_on_home" in r.message for r in caplog.records)


def test_books_notes_cross_link_and_actions(content_dir):
    content = load(content_dir)
    books = {b.title: b for b in content.books}
    assert [a.kind for a in books["Life is Happenning"].actions] == ["read", "download"]
    assert books["Space Between Knowing"].cross_link == "#note-space-between-knowing"
    assert books["Tableau - An Introduction"].actions == [] and books["Tableau - An Introduction"].unavailable_label
    notes = {n.title: n for n in content.notes}
    assert notes["Space Between Knowing"].cross_link == "#book-space-between-knowing"
    assert [n.title for n in content.notes] == ["Inside the Box", "Space Between Knowing"]   # newest first


def test_thoughts_newest_first_by_default(content_dir):
    assert [t.date for t in load(content_dir).thoughts] == ["2026-10-25", "2026-06-01"]
