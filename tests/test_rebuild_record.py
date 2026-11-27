"""Keep the published fresh-checkout acceptance record tied to the code that was run."""

import hashlib

from pdf_heading_benchmark.io import REPO, read_json
from pdf_heading_benchmark.joint_metrics import scored_counts


def test_rebuild_record_matches_executed_code_and_published_predictions():
    record = read_json(REPO / "outputs/rebuild-check/summary.json")
    for name, expected in record["source_hashes"].items():
        assert hashlib.sha256((REPO / name).read_bytes()).hexdigest() == expected
    audit = REPO / "outputs/structure-precision/evidence/historical-audit.json"
    assert hashlib.sha256(audit.read_bytes()).hexdigest() == record["historical_predictions_sha256"]
    assert record["historical_predictions_identical_to_published"]
    assert record["historical"] == scored_counts(
        {"gold": 77, "predicted": 41, "matched": 39, "correct_level": 34}
    )
    assert record["notebook_code_cells_executed"] == 6
    assert record["example_prediction_headings"] > 0
