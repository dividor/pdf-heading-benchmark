"""Native headings must not be promoted, repaired, or inferred from code and body text."""

from pdf_heading_benchmark.field_output import markdown_headings


def test_native_levels_and_setext_survive_without_cover_level_adjustment():
    assert markdown_headings("## 1. Findings\n\n### Evidence\n\nAnnex\n=====\n", 9) == [
        {"page": 9, "title": "1. Findings", "level": 2},
        {"page": 9, "title": "Evidence", "level": 3},
        {"page": 9, "title": "Annex", "level": 1},
    ]


def test_code_and_bold_paragraphs_are_not_headings():
    assert markdown_headings("```python\n# A comment\n```\n\n**Findings**\n\nBody", 1) == []
