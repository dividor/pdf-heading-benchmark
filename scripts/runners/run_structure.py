"""Run a v2 ablation locally; set PDF_HEADING_STRUCTURE_RUN to a frozen training run."""

import argparse
import os
from pathlib import Path

from pdf_heading_benchmark.structure_data import load_model_bundle
from pdf_heading_benchmark.structure_inference import parse_structure
from pdf_heading_benchmark.supervised_data import write_json
from pdf_heading_benchmark.supervised_inference import markdown_text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--variant", required=True, choices=["expanded_line", "learned_groups", "context_relations"]
    )
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    run = os.environ.get("PDF_HEADING_STRUCTURE_RUN")
    if not run:
        parser.error("Set PDF_HEADING_STRUCTURE_RUN; see scripts/structure/train.py")
    name = "structure_" + args.variant
    if (args.output / f"{name}.headings.json").exists():
        raise ValueError("Existing predictions must not be overwritten")
    models, variant = load_model_bundle(Path(run), args.variant)
    result = parse_structure(args.pdf, models, variant)
    write_json(args.output / f"{name}.document.json", result)
    write_json(
        args.output / f"{name}.headings.json",
        [{"page": h["page"], "level": h["level"], "title": h["text"]} for h in result["headings"]],
    )
    (args.output / f"{name}.md").write_text(markdown_text(result))
    write_json(args.output / f"{name}.run.json", {"seconds": result["total_seconds"], "variant": variant})
