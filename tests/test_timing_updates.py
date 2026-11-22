"""Never pair new latency with unrelated historical quality measurements."""

import pytest

from pdf_heading_benchmark.timing_updates import update_timing


def fixture():
    row = dict(
        method="example",
        gold=1,
        predicted=1,
        matched=1,
        correct_level=1,
        measured_seconds=10,
        processed_pages=1,
    )
    repeat = dict(row, seconds=5)
    heads = {"doc": [{"page": 1, "title": "Introduction", "level": 1}]}
    return row, repeat, heads


def test_accept_same_headings_with_extra_parser_metadata():
    row, repeat, heads = fixture()
    fresh = {"doc": [dict(heads["doc"][0], bbox=[0, 0, 1, 1])]}
    result = update_timing(row, repeat, heads, fresh)
    assert result["measured_seconds"] == 5
    assert result["timing_source"] == "sequential rerun"
    assert row["measured_seconds"] == 10


def test_changed_level_cannot_replace_historical_timing():
    row, repeat, heads = fixture()
    fresh = {"doc": [dict(heads["doc"][0], level=2)]}
    result = update_timing(row, repeat, heads, fresh)
    assert result["measured_seconds"] == 10
    assert "predictions differ" in result["timing_source"]


def test_inconsistent_counts_are_rejected():
    row, repeat, heads = fixture()
    with pytest.raises(ValueError, match="different heading counts"):
        update_timing(row, dict(repeat, correct_level=0), heads, heads)


def test_different_processed_page_scope_is_rejected():
    row, repeat, heads = fixture()
    with pytest.raises(ValueError, match="different page scope"):
        update_timing(row, dict(repeat, processed_pages=2), heads, heads)


def test_timeout_cannot_replace_historical_timing_even_if_headings_match():
    row, repeat, heads = fixture()
    result = update_timing(row, dict(repeat, timeouts=1), heads, heads)
    assert result["measured_seconds"] == 10
    assert "truncation" in result["timing_source"]
