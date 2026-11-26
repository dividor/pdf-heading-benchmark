"""Run a v2 ablation locally; set PDF_HEADING_STRUCTURE_RUN to a frozen training run."""

import argparse
import os
from pathlib import Path

from pdf_heading_benchmark.structure_data import load_calibration, load_model_bundle
from pdf_heading_benchmark.structure_inference import parse_structure
from pdf_heading_benchmark.supervised_data import write_json
from pdf_heading_benchmark.supervised_inference import markdown_text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--variant", required=True, choices=["expanded_line", "learned_groups", "context_relations"]
    )
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--calibration", type=Path, help="Frozen calibration run directory (optional)")
    parser.add_argument("--calibrated", action="store_true", help="Require PDF_HEADING_CALIBRATION or a path")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.calibrated and not args.calibration:
        directory = os.environ.get("PDF_HEADING_CALIBRATION")
        if not directory:
            parser.error("Set PDF_HEADING_CALIBRATION to your calibration run, or pass --calibration")
        args.calibration = Path(directory)
    run = os.environ.get("PDF_HEADING_STRUCTURE_RUN")
    if not run:
        parser.error("Set PDF_HEADING_STRUCTURE_RUN; see scripts/structure/train.py")
    name = "structure_calibrated" if args.calibration else "structure_" + args.variant
    if (args.output / f"{name}.headings.json").exists():
        raise ValueError("Existing predictions must not be overwritten")
    models, variant = load_model_bundle(Path(run), args.variant)
    decoding = load_calibration(args.calibration, Path(run)) if args.calibration else None
    if decoding and variant != "context_relations":
        parser.error("Calibration requires context_relations")
    result = parse_structure(args.pdf, models, variant, decoding)
    write_json(args.output / f"{name}.document.json", result)
    write_json(
        args.output / f"{name}.headings.json",
        [{"page": h["page"], "level": h["level"], "title": h["text"]} for h in result["headings"]],
    )
    (args.output / f"{name}.md").write_text(markdown_text(result))
    write_json(
        args.output / f"{name}.run.json",
        {"seconds": result["total_seconds"], "variant": variant, "decoding": decoding},
    )
