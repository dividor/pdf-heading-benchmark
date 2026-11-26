"""Audit the selection boundary and recompute regression results without models or PDFs."""

import pytest

from pdf_heading_benchmark.io import REPO, read_json, write_json
from pdf_heading_benchmark.structure_data import checksum, load_calibration
from pdf_heading_benchmark.structure_evaluation import group_counts, summarize_counts

EVIDENCE = REPO / "outputs/structure-calibration/evidence"


def test_calibration_is_validation_selected_and_source_frozen():
    protocol = read_json(EVIDENCE / "protocol.json")
    selection = read_json(EVIDENCE / "selection.json")
    assert len(selection["validation"]) == 9
    best = max(selection["validation"], key=lambda row: row["score"]["group_level_f1"])
    assert selection["selected"] == best
    for source, expected in protocol["source_hashes"].items():
        assert checksum(REPO / source) == expected
    assert [row["decoding"] for row in selection["validation"]] == protocol["grid"]
    assert set(best["score"]["per_document"]) == {"103", "538", "176", "128"}


def test_regression_scores_recompute_from_published_groups():
    annotations = read_json(REPO / "configs/structure-v2/annotations.json")
    for name, result in read_json(EVIDENCE / "regression.json")["results"].items():
        counts = dict.fromkeys(("gold", "predicted", "matched", "correct"), 0)
        for doc in read_json(EVIDENCE / f"{name}-regression-audit.json"):
            gold = [a for a in annotations if a["report_id"] == doc["report_id"]]
            found = group_counts(gold, doc["headings"])
            for key, value in found.items():
                counts[key] += value
        summary = summarize_counts(counts)
        assert all(result[key] == value for key, value in summary.items())


def test_calibration_rejects_a_different_model_bundle(tmp_path):
    write_json(tmp_path / "selection.json", {"model_hashes": {"context": "different"}})
    with pytest.raises(ValueError, match="different model"):
        load_calibration(EVIDENCE, tmp_path)
    protocol = read_json(EVIDENCE / "protocol.json")
    write_json(tmp_path / "selection.json", {"model_hashes": protocol["model_hashes"]})
    assert load_calibration(EVIDENCE, tmp_path) == {"body_weight": 2.0, "relation_weight": 1.0}
