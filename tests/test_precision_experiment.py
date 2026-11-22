"""Audit precision selection and independently recompute published scores from predictions."""

from pdf_heading_benchmark.evaluation import evaluate
from pdf_heading_benchmark.io import REPO, read_json
from pdf_heading_benchmark.joint_metrics import scored_counts
from pdf_heading_benchmark.precision_experiment import choose_candidate, decision_grid, heading_records
from pdf_heading_benchmark.structure_data import checksum

EVIDENCE = REPO / "outputs/structure-precision/evidence"


def test_precision_selection_is_frozen_and_validation_only():
    protocol = read_json(EVIDENCE / "protocol.json")
    selection = read_json(EVIDENCE / "selection.json")
    assert protocol["grid"] == decision_grid()
    assert len(selection["validation"]) == 36
    assert [row["settings"] for row in selection["validation"]] == protocol["grid"]
    assert selection["selected"] == choose_candidate(selection["validation"])
    assert set(selection["selected"]["score"]["per_document"]) == {"103", "538", "176", "128"}
    for path, digest in protocol["source_hashes"].items():
        assert checksum(REPO / path) == digest


def test_regression_recomputes_from_annotations_and_predictions():
    annotations = read_json(REPO / "configs/structure-v2/annotations.json")
    corpus = {r["id"]: r for r in read_json(REPO / "configs/structure-v2/corpus.json")}
    regression = read_json(EVIDENCE / "regression.json")
    for name, expected in regression["results"].items():
        total = dict.fromkeys(("gold", "predicted", "matched", "correct_level"), 0)
        for doc in read_json(EVIDENCE / f"{name}-regression-audit.json"):
            key = doc["report_id"]
            truth = [a for a in annotations if a["report_id"] == key]
            result = evaluate(
                heading_records(truth), heading_records(doc["headings"]), corpus[key]["review_pages"]
            )
            for field in total:
                total[field] += result[field]
        assert all(expected[k] == value for k, value in scored_counts(total).items())
    assert regression["results"]["selected"]["precision_gate_pass"]


def test_historical_precision_metrics_use_all_predictions():
    gold = read_json(REPO / "configs/gold.json")
    pages = read_json(REPO / "configs/audit_pages.json")
    predictions = read_json(EVIDENCE / "historical-audit.json")
    total = dict.fromkeys(("gold", "predicted", "matched", "correct_level"), 0)
    for key, truth in gold.items():
        result = evaluate(truth, predictions[key], pages[key])
        for field in total:
            total[field] += result[field]
    published = next(
        r for r in read_json(REPO / "outputs/report/results.json") if r["method"] == "structure_precision"
    )
    assert all(published[k] == value for k, value in scored_counts(total).items())
    assert total == {"gold": 77, "predicted": 41, "matched": 39, "correct_level": 34}
