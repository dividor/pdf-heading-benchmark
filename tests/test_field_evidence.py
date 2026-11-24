"""Reject unscorable trials and preserve the native-text metric's meaning."""

import pytest

from pdf_heading_benchmark.field_evidence import grams, validate_protocol, words
from pdf_heading_benchmark.io import REPO, read_json


def test_smoke_or_different_scope_cannot_be_scored(tmp_path):
    with pytest.raises(ValueError, match="complete fixed audit"):
        validate_protocol({"smoke": True}, "minicpm_ocr10", tmp_path)
    with pytest.raises(ValueError, match="complete fixed audit"):
        validate_protocol({"smoke": False, "pages": {"targeting": [1]}}, "minicpm_ocr10", tmp_path)


def test_changed_model_pin_cannot_be_scored(tmp_path):
    protocol = dict(
        smoke=False,
        pages=read_json(REPO / "configs/audit_pages.json"),
        candidate="minicpm_ocr10",
        models={},
    )
    with pytest.raises(ValueError, match="model revisions"):
        validate_protocol(protocol, "minicpm_ocr10", tmp_path)


def test_prose_metric_normalizes_wrapping_and_retains_word_order():
    assert words("<p>The [pro-\ngramme](https://example.org) WORKED.</p>") == ["the", "programme", "worked"]
    assert grams("one two three four five six") == {
        ("one", "two", "three", "four", "five"),
        ("two", "three", "four", "five", "six"),
    }
    assert not grams("five four three two one") & grams("one two three four five")
