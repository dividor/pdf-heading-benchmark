"""Run the frozen selected classifier on the original benchmark, then score its audit pages."""

import argparse
import hashlib
from pathlib import Path

from pdf_heading_benchmark.evaluation import evaluate
from pdf_heading_benchmark.io import REPO, read_json, write_json
from pdf_heading_benchmark.supervised_inference import markdown_text, parse_document


def compare(data: Path, model_run: Path, output: Path) -> None:
    if output.exists():
        raise ValueError("Use a new comparison directory")
    selection = read_json(model_run / "selection.json")
    model_path = model_run / f"{selection['selected']}.json"
    checksum = hashlib.sha256(model_path.read_bytes()).hexdigest()
    if checksum != selection["selected_model_sha256"]:
        raise ValueError("Frozen model checksum mismatch")
    model = read_json(model_path)
    predictions, timings = {}, []
    for record in read_json(REPO / "configs/corpus.json"):
        pdf = data / "corpus" / f"{record['id']}.pdf"
        if hashlib.sha256(pdf.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError("Wrong benchmark PDF")
        result = parse_document(pdf, model)
        write_json(output / record["id"] / "document.json", result)
        (output / record["id"] / "document.md").write_text(markdown_text(result))
        predictions[record["id"]] = [
            {"page": h["page"], "level": h["level"], "title": h["text"]} for h in result["headings"]
        ]
        timings.append(
            {"document": record["id"], "pages": record["pages"], "seconds": result["total_seconds"]}
        )
    # Reference headings are read only after all inference has finished.
    gold = read_json(REPO / "configs/gold.json")
    pages = read_json(REPO / "configs/audit_pages.json")
    audit = {key: [h for h in values if h["page"] in pages[key]] for key, values in predictions.items()}
    results = [
        {"document": key, "method": "supervised_extra_trees", **evaluate(gold[key], audit[key], pages[key])}
        for key in gold
    ]
    write_json(output / "audit-predictions.json", audit)
    write_json(output / "scores.json", results)
    write_json(
        output / "run.json",
        {
            "selected_model_sha256": checksum,
            "timings": timings,
            "model_selection": "Frozen supervised-v1/run-003; no refitting or tuning on benchmark reports",
            "timing_scope": "Full PDF extraction, features and classification; excludes load/output writes",
        },
    )
    print(
        {
            "matched": sum(r["matched"] for r in results),
            "correct_level": sum(r["correct_level"] for r in results),
            "false_headings": sum(r["predicted"] - r["matched"] for r in results),
            "seconds": sum(r["seconds"] for r in timings),
        }
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--model-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    compare(args.data, args.model_run, args.output)
