"""Test the matching contract and reproduce every published heading count."""

import hashlib

import pytest

from pdf_heading_benchmark.evaluation import evaluate, evaluate_all, normalize
from pdf_heading_benchmark.io import REPO, read_json


def h(title, page=1, level=1):
    return dict(title=title, page=page, level=level)


def test_page_provenance_and_one_to_one():
    result = evaluate(
        [h("Introduction")], [h("Introduction"), h("Introduction"), h("Introduction", 2)], [1, 2]
    )
    assert (result["matched"], result["correct_level"], len(result["extras"])) == (1, 1, 2)


def test_missing_levels_do_not_count_as_correct():
    result = evaluate([h("Introduction")], [h("Introduction", level=None)], [1])
    assert (result["matched"], result["correct_level"]) == (1, 0)


def test_no_predictions_and_page_filter():
    result = evaluate([h("Introduction")], [h("Introduction", 2)], [1])
    assert result["predicted"] == result["matched"] == result["correct_level"] == 0
    assert len(result["missing"]) == 1


def test_unicode_normalization():
    assert normalize("<b>\uff11. INTRODUCTION!</b>") == normalize("1 introduction")


@pytest.mark.parametrize("summary", read_json(REPO / "outputs/league_table.json"))
def test_published_counts(summary):
    if summary["status"] != "completed":
        assert summary["correct_heading_and_level"] is None
        return
    method = summary["method"]
    predictions = read_json(REPO / "outputs/audit_predictions.json")
    results = evaluate_all(
        read_json(REPO / "configs/gold.json"),
        {method: predictions[method]},
        read_json(REPO / "configs/audit_pages.json"),
    )
    for field in ("gold", "predicted", "matched", "correct_level"):
        assert sum(r[field] for r in results) == summary[field]


def test_frozen_reference_hash():
    expected = (REPO / "configs/gold.sha256").read_text().split()[0]
    assert hashlib.sha256((REPO / "configs/gold.json").read_bytes()).hexdigest() == expected
