"""Run the validation-selected precision candidate on a new PDF, using local frozen models."""

import argparse
import os
from pathlib import Path

from pdf_heading_benchmark.precision_inference import parse_precision
from pdf_heading_benchmark.structure_data import load_model_bundle
from pdf_heading_benchmark.supervised_data import read_json, write_json
from pdf_heading_benchmark.supervised_inference import markdown_text


def load_settings(experiment: Path, run: Path) -> dict:
    protocol = read_json(experiment / "protocol.json")
    if protocol["model_hashes"] != read_json(run / "selection.json")["model_hashes"]:
        raise ValueError("Precision settings belong to different models")
    selected = read_json(experiment / "selection.json")["selected"]
    if not selected or not selected["score"]["precision_gate_pass"]:
        raise ValueError("No qualifying validation candidate")
    if selected["settings"] not in protocol["grid"]:
        raise ValueError("Selected settings outside frozen grid")
    return selected["settings"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--run", type=Path, default=os.environ.get("PDF_HEADING_STRUCTURE_RUN"))
    parser.add_argument("--selection", type=Path, default=os.environ.get("PDF_HEADING_PRECISION_RUN"))
    args = parser.parse_args()
    if not args.run or not args.selection:
        parser.error("Supply --run and --selection, or PDF_HEADING_STRUCTURE_RUN/PDF_HEADING_PRECISION_RUN")
    if (args.output / "structure_precision.headings.json").exists():
        raise ValueError("Existing predictions must not be overwritten")
    settings = load_settings(args.selection, args.run)
    models, _ = load_model_bundle(args.run, settings["variant"])
    result = parse_precision(args.pdf, models, settings)
    write_json(args.output / "structure_precision.document.json", result)
    write_json(
        args.output / "structure_precision.headings.json",
        [{"page": h["page"], "level": h["level"], "title": h["text"]} for h in result["headings"]],
    )
    (args.output / "structure_precision.md").write_text(markdown_text(result))
    write_json(
        args.output / "structure_precision.run.json",
        {
            "seconds": result["total_seconds"],
            "settings": settings,
            "scope": "Full PDF extraction/features/inference; excludes model loading and output writes",
        },
    )


if __name__ == "__main__":
    main()
