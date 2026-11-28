"""The source importer keeps scoring groups and absent values separate."""

import pytest

from pdf_heading_benchmark.field_data import parse_source, score

SOURCE = """## Leaderboard

| parser | weights | headline | text | tables | layout | USD / 1,000 pages |
| --- | --- | --- | --- | --- | --- | --- |
| LlamaParse | closed | 90.8 | 89.4 | 92.9 | 90.0 | 31.25 |
| Gemini † * (Datalab) | closed | 95 | 94 | 97 | 96 | 49 |

**Scorer:** omni-parse-bench 1.8.0

### Pending regrade

These rows are still graded by omni-parse-bench 1.5.0, so they are not comparable.

| parser | weights | headline | text | tables | layout | USD / 1,000 pages |
| --- | --- | --- | --- | --- | --- | --- |
| Older model | closed | 90 | 88 | 91 | 91 | 30 |

### No layout output (no headline)

| parser | weights | text | tables |
| --- | --- | --- | --- |
| Xiaomi-OCR-0 | open | 73.7 | 90.6 |
"""


def test_parse_actual_markdown_structure_preserves_scores_and_caveats():
    result = parse_source(SOURCE, "a" * 40, "2026-11-28")
    assert result["benchmark"] == "OmniParseBench 1.8.0"
    assert result["pending_benchmark"] == "OmniParseBench 1.5.0"
    assert result["rows"][0]["text"] == 89.4
    assert result["rows"][0]["layout"] == 90.0
    assert result["rows"][0]["category"] == "hosted"
    assert result["text_only"][0]["layout"] is None
    assert result["text_only"][0]["category"] == "local"
    assert result["pending"][0]["name"] == "Older model"
    assert all(result["rows"][1][key] for key in ("retry", "annotation_contributor", "benchmark_vendor"))


@pytest.mark.parametrize(
    "source,revision",
    [
        (SOURCE, "main"),
        (SOURCE.replace("## Leaderboard", "## Renamed"), "a" * 40),
        (SOURCE.replace("closed", "unknown"), "a" * 40),
        (SOURCE.replace("1.8.0", "unknown"), "a" * 40),
    ],
)
def test_changed_source_contract_fails(source, revision):
    with pytest.raises(ValueError):
        parse_source(source, revision, "2026-11-28")


def test_invalid_score_is_not_clamped():
    with pytest.raises(ValueError, match="outside"):
        score("101")
