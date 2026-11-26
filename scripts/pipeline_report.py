"""Import complete EvidenceLab or Docling OCR runs into the shared benchmark."""

import argparse
from pathlib import Path

from pdf_heading_benchmark.evaluation import evaluate
from pdf_heading_benchmark.io import REPO, read_json, write_json
from pdf_heading_benchmark.joint_metrics import scored_counts
from pdf_heading_benchmark.pipeline_evidence import import_pipeline

METHODS = {
    "evidencelab": (
        "EvidenceLab — Docling + hierarchical post-processing",
        "https://github.com/dividor/evidencelab",
    ),
    "docling_ocr": (
        "Docling — full-page RapidOCR + heading hierarchy",
        "https://github.com/docling-project/docling",
    ),
}


def score(key, evidence):
    gold, pages = read_json(REPO / "configs/gold.json"), read_json(REPO / "configs/audit_pages.json")
    details = [
        dict(document=doc, method=key, **evaluate(gold[doc], heads, pages[doc]))
        for doc, heads in evidence["predictions"].items()
    ]
    counts = scored_counts(
        {field: sum(d[field] for d in details) for field in ("gold", "predicted", "matched", "correct_level")}
    )
    prose = list(evidence["prose"].values())
    row = dict(
        method=key,
        name=METHODS[key][0],
        source_url=METHODS[key][1],
        status="completed",
        documents_scored=len(details),
        **counts,
        heading_recall=counts["matched"] / counts["gold"],
        correct_heading_and_level=counts["correct_level"] / counts["gold"],
        false_headings=counts["predicted"] - counts["matched"],
        native_prose_retention=sum(p["retained"] for p in prose) / sum(p["total"] for p in prose),
        measured_seconds=evidence["timing"]["seconds"],
        processed_pages=evidence["timing"]["pages"],
    )
    return row, details


def publish(key, evidence):
    row, scores = score(key, evidence)
    rows = [r for r in read_json(REPO / "outputs/league_table.json") if r["method"] != key]
    details = [r for r in read_json(REPO / "outputs/league_details.json") if r["method"] != key]
    predictions = read_json(REPO / "outputs/audit_predictions.json")
    predictions[key] = evidence["predictions"]
    write_json(REPO / f"outputs/pipeline-runs/{key}.json", evidence)
    rows.append(row)
    rows.sort(key=lambda item: item["correct_heading_and_level"] or -1, reverse=True)
    write_json(REPO / "outputs/league_table.json", rows)
    write_json(REPO / "outputs/league_details.json", [*details, *scores])
    write_json(REPO / "outputs/audit_predictions.json", predictions)
    return row


def rebuild():
    for key in METHODS:
        path = REPO / f"outputs/pipeline-runs/{key}.json"
        if path.exists():
            publish(key, read_json(path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("method", choices=METHODS, nargs="?")
    parser.add_argument("--run", type=Path)
    parser.add_argument("--data", type=Path)
    args = parser.parse_args()
    if args.method:
        if not args.run or not args.data:
            parser.error("Import requires --run and --data")
        print(publish(args.method, import_pipeline(args.run, args.data, args.method)))
    elif args.run or args.data:
        parser.error("Import requires a method name")
    rebuild()


if __name__ == "__main__":
    main()
