"""Fresh-run comparisons must detect changed levels and incomplete coverage."""

import sys

import pytest

from pdf_heading_benchmark import verification_evidence as evidence
from pdf_heading_benchmark.io import write_json


def test_compare_detects_changed_levels_and_ignores_unscored_pages():
    truth = {"a": [{"page": 1, "title": "Summary", "level": 1}]}
    pages = {"a": [1]}
    assert evidence.compare_predictions(truth, truth, truth, pages)["predictions_identical"]
    actual = {"a": [{"page": 1, "title": "Summary", "level": 2}, {"page": 2, "title": "X", "level": 1}]}
    result = evidence.compare_predictions(actual, truth, truth, pages)
    assert result["changed_documents"] == ["a"]
    assert result["counts"]["matched"] == 1
    assert result["counts"]["joint_f05"] == 0
    with pytest.raises(ValueError, match="exactly"):
        evidence.compare_predictions({}, truth, truth, pages)


def test_failed_process_cannot_be_verified(tmp_path):
    write_json(tmp_path / "job/status.json", {"status": "resource_abort", "returncode": -15})
    with pytest.raises(ValueError, match="unfinished"):
        evidence.record_completed(tmp_path, "example", tmp_path / "job", None, tmp_path / "result.json")


def test_cli_records_actual_completed_predictions(tmp_path, monkeypatch):
    root = tmp_path / "data"
    truth = {"a": [{"page": 1, "title": "Summary", "level": 1}]}
    repo = tmp_path / "repo"
    write_json(repo / "configs/report-methods.json", ["example"])
    write_json(repo / "configs/corpus.json", [])
    write_json(repo / "configs/gold.json", truth)
    write_json(repo / "configs/audit_pages.json", {"a": [1]})
    write_json(repo / "outputs/audit_predictions.json", {"example": truth})
    write_json(root / "results/a/example.headings.json", truth["a"])
    write_json(root / "job/status.json", {"status": "completed", "returncode": 0})
    monkeypatch.setattr(evidence, "REPO", repo)
    output = root / "comparison.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "compare",
            "--data",
            str(root),
            "--method",
            "example",
            "--job",
            str(root / "job"),
            "--output",
            str(output),
        ],
    )
    evidence.main()
    assert evidence.read_json(output)["predictions_identical"]
