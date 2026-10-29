import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from qa.build import BuildOptions, build  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "site"


@pytest.fixture(autouse=True)
def _endpoint(monkeypatch):
    """A newsletter endpoint, so strict builds have nothing to warn about."""
    monkeypatch.setenv("BLOG_NEWSLETTER_API_ENDPOINT", "https://example.test/subscribe")


@pytest.fixture
def content_dir(tmp_path):
    """A private, editable copy of the fixture content."""
    target = tmp_path / "content"
    shutil.copytree(FIXTURE, target)
    return target


@pytest.fixture
def run_build(tmp_path, content_dir):
    def _run(theme="quiet", **kwargs):
        opts = dict(root=ROOT, content_dir=content_dir, themes_dir=ROOT / "themes",
                    output_dir=tmp_path / "dist", theme=theme, strict=True)
        opts.update(kwargs)
        return build(BuildOptions(**opts))
    return _run


def read(result, name):
    return (result.output / name).read_text(encoding="utf-8")
