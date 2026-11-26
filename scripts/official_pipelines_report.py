"""Import upstream pipeline runs, then regenerate their scores without model inference."""

import argparse
from pathlib import Path

from pdf_heading_benchmark.evaluation import evaluate
from pdf_heading_benchmark.io import REPO, read_json, write_json
from pdf_heading_benchmark.joint_metrics import scored_counts
from pdf_heading_benchmark.official_evidence import import_run

OUT = REPO / "outputs/official-pipelines"
METHODS = {
    "paddleocr_vl16_official": (
        "PaddleOCR-VL-1.6 — official Apple Silicon pipeline",
        "PaddlePaddle/PaddleOCR-VL-1.6",
    ),
    "ovisocr3_official_metal": ("OvisOCR3 — upstream prompt and vLLM Metal", "ATH-MaaS/OvisOCR3"),
    "minicpm_ocr10_official_ollama": (
        "MiniCPM-OCR 1.0 — official package, Ollama Q8 + DSpark",
        "openbmb/MiniCPM-OCR-1.0",
    ),
    "xiaomi_ocr0_official_metal": (
        "Xiaomi-OCR-0 — upstream two-stage pipeline, Metal",
        "xiaomi-research/Xiaomi-OCR-0",
    ),
}


def scored_run(key, evidence):
    gold, pages = read_json(REPO / "configs/gold.json"), read_json(REPO / "configs/audit_pages.json")
    scores = [
        dict(document=doc, method=key, **evaluate(gold[doc], heads, pages[doc]))
        for doc, heads in evidence["predictions"].items()
    ]
    counts = scored_counts(
        {field: sum(s[field] for s in scores) for field in ("gold", "predicted", "matched", "correct_level")}
    )
    prose = evidence["prose"].values()
    row = dict(
        method=key,
        name=METHODS[key][0],
        source_url="https://huggingface.co/" + METHODS[key][1],
        status="completed",
        documents_scored=len(scores),
        **counts,
        heading_recall=counts["matched"] / counts["gold"],
        correct_heading_and_level=counts["correct_level"] / counts["gold"],
        false_headings=counts["predicted"] - counts["matched"],
        native_prose_retention=sum(p["retained"] for p in prose) / sum(p["total"] for p in prose),
        measured_seconds=evidence["timing"]["seconds"],
        processed_pages=evidence["timing"]["pages"],
    )
    return row, scores


def publish():
    keys = [key for key in METHODS if (OUT / f"{key}.json").exists()]
    rows = [r for r in read_json(REPO / "outputs/league_table.json") if r["method"] not in keys]
    details = [r for r in read_json(REPO / "outputs/league_details.json") if r["method"] not in keys]
    predictions = read_json(REPO / "outputs/audit_predictions.json")
    for key in keys:
        evidence = read_json(OUT / f"{key}.json")
        row, scores = scored_run(key, evidence)
        rows.append(row)
        details.extend(scores)
        predictions[key] = evidence["predictions"]
        print(key, row["joint_f05"], row["correct_level"], row["false_headings"])
    rows.sort(key=lambda r: r["correct_heading_and_level"] or -1, reverse=True)
    write_json(REPO / "outputs/league_table.json", rows)
    write_json(REPO / "outputs/league_details.json", details)
    write_json(REPO / "outputs/audit_predictions.json", predictions)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--data", type=Path)
    args = parser.parse_args()
    if args.run:
        if not args.data:
            parser.error("--run requires --data")
        evidence = import_run(args.run, args.data)
        key = evidence["protocol"]["candidate"]
        if key not in METHODS:
            raise ValueError("Unknown official pipeline")
        write_json(OUT / f"{key}.json", evidence)
    publish()


if __name__ == "__main__":
    main()
