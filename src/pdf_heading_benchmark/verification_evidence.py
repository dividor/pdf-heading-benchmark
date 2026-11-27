"""Compare fresh predictions with published evidence without changing the report."""

import argparse
from pathlib import Path

from pdf_heading_benchmark.corpus import verify
from pdf_heading_benchmark.evaluation import evaluate
from pdf_heading_benchmark.io import REPO, read_json, write_json
from pdf_heading_benchmark.joint_metrics import scored_counts


def compare_predictions(actual: dict, published: dict, gold: dict, pages: dict) -> dict:
    if set(actual) != set(gold):
        raise ValueError("Fresh predictions must cover exactly the four benchmark documents")
    details = {key: evaluate(gold[key], actual[key], pages[key]) for key in gold}
    counts = scored_counts(
        {
            field: sum(row[field] for row in details.values())
            for field in ("gold", "predicted", "matched", "correct_level")
        }
    )
    changed = []
    for key in gold:
        fresh = [(h["page"], h["title"], h["level"]) for h in actual[key] if h["page"] in pages[key]]
        prior = [(h["page"], h["title"], h["level"]) for h in published[key] if h["page"] in pages[key]]
        if sorted(fresh, key=repr) != sorted(prior, key=repr):
            changed.append(key)
    return {
        "counts": counts,
        "changed_documents": changed,
        "predictions_identical": not changed,
        "details": details,
    }


def record_completed(root: Path, method: str, job: Path, predictions: Path | None, output: Path) -> dict:
    status = read_json(job / "status.json")
    if status["status"] != "completed" or status["returncode"] != 0:
        raise ValueError("Cannot verify an unfinished or failed process")
    if method not in read_json(REPO / "configs/report-methods.json"):
        raise ValueError("Method is not in the local report")
    for item in read_json(REPO / "configs/corpus.json"):
        verify(root / "corpus" / f"{item['id']}.pdf", item["sha256"])
    gold = read_json(REPO / "configs/gold.json")
    actual = (
        read_json(predictions)
        if predictions
        else {key: read_json(root / "results" / key / f"{method}.headings.json") for key in gold}
    )
    comparison = compare_predictions(
        actual,
        read_json(REPO / "outputs/audit_predictions.json")[method],
        gold,
        read_json(REPO / "configs/audit_pages.json"),
    )
    record = {"method": method, "process": status, **comparison}
    write_json(output, record)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--method", required=True)
    parser.add_argument("--job", required=True, type=Path)
    parser.add_argument(
        "--predictions", type=Path, help="Explicit document-keyed output from a dedicated runner"
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    record = record_completed(args.data, args.method, args.job, args.predictions, args.output)
    print(args.method, record["counts"], "Exact published predictions:", record["predictions_identical"])


if __name__ == "__main__":
    main()
