"""Chandra export retains original pages and levels, and rejects incomplete output."""

import json

import export_chandra_markdown
import pytest


@pytest.fixture
def saved_chandra(tmp_path):
    (tmp_path / "reference").mkdir()
    (tmp_path / "reference/audit_pages.json").write_text('{"document": [1, 2]}')
    output = tmp_path / "results/document/chandra2_mlx"
    output.mkdir(parents=True)
    for page in (1, 2):
        record = dict(text=f"<h{page}>Title {page}</h{page}>", error=None, hit_token_limit=False)
        (output / f"{page}.json").write_text(json.dumps(record))
    return tmp_path


def test_export_retains_pages_levels_and_conversion_options(saved_chandra):
    calls = []

    def convert(text, **kwargs):
        calls.append((text, kwargs))
        return "Converted text"

    export_chandra_markdown.export(saved_chandra, convert)
    output = saved_chandra / "results/document"
    headings = json.loads((output / "chandra2.predicted-headings.json").read_text())
    assert headings == [dict(page=n, level=n, title=f"Title {n}") for n in (1, 2)]
    markdown = (output / "chandra2.markdown.md").read_text()
    assert markdown.count("Converted text") == 2
    assert "Original PDF page 1" in markdown and "Original PDF page 2" in markdown
    assert all(options == dict(include_headers_footers=True, include_images=False) for _, options in calls)


@pytest.mark.parametrize("error,limited", [("failed", False), (None, True)])
def test_export_rejects_incomplete_pages(saved_chandra, error, limited):
    page = saved_chandra / "results/document/chandra2_mlx/1.json"
    record = json.loads(page.read_text())
    page.write_text(json.dumps(dict(record, error=error, hit_token_limit=limited)))
    with pytest.raises(ValueError, match="Incomplete"):
        export_chandra_markdown.export(saved_chandra, lambda *args, **kwargs: "text")


def test_export_rejects_empty_conversion(saved_chandra):
    with pytest.raises(ValueError, match="empty text"):
        export_chandra_markdown.export(saved_chandra, lambda *args, **kwargs: "")
