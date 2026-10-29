"""The boundary between engine and theme."""
import json
import re
import shutil
from pathlib import Path

import pytest

from qa.theme import REQUIRED_TEMPLATES, Theme, ThemeError

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("name", ["quiet", "minimal"])
def test_shipped_themes_satisfy_the_contract(name):
    Theme(ROOT / "themes" / name, strict_undefined=True)


def test_missing_required_template_is_reported(tmp_path):
    broken = tmp_path / "t"
    shutil.copytree(ROOT / "themes" / "minimal", broken)
    (broken / "templates" / "books.html").unlink()
    with pytest.raises(ThemeError, match="books.html"):
        Theme(broken)


def test_wrong_contract_version_is_rejected(tmp_path):
    broken = tmp_path / "t"
    shutil.copytree(ROOT / "themes" / "minimal", broken)
    (broken / "theme.json").write_text(json.dumps({"name": "x", "contract": 1}))
    with pytest.raises(ThemeError, match="contract"):
        Theme(broken)


def test_engine_contains_no_page_markup():
    """The engine may not build page HTML. Markup belongs to the theme."""
    forbidden = re.compile(r"<(div|section|article|header|footer|nav|svg|span|h[1-6]|ul|li|a)[\s>]")
    offenders = []
    for py in (ROOT / "qa").glob("*.py"):
        for number, line in enumerate(py.read_text().splitlines(), 1):
            if forbidden.search(line):
                offenders.append(f"{py.name}:{number}")
    assert not offenders, offenders


def test_required_template_list_matches_docs():
    docs = (ROOT / "docs" / "THEME_CONTRACT.md").read_text()
    for template in REQUIRED_TEMPLATES:
        assert template in docs, f"{template} is required but not documented"
