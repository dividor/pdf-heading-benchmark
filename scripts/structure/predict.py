"""Extract complete native PDF text plus learned headings with a frozen local model."""

import argparse
from pathlib import Path

from pdf_heading_benchmark.structure_data import load_calibration, load_model_bundle
from pdf_heading_benchmark.structure_inference import parse_structure
from pdf_heading_benchmark.supervised_data import write_json
from pdf_heading_benchmark.supervised_inference import markdown_text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--variant", choices=["expanded_line", "learned_groups", "context_relations"])
    parser.add_argument("--calibration", type=Path, help="Frozen calibration run directory (optional)")
    args = parser.parse_args()
    if args.output.exists() or args.output.with_suffix(".md").exists():
        raise ValueError("Choose a fresh output filename")
    models, variant = load_model_bundle(args.run, args.variant)
    decoding = load_calibration(args.calibration, args.run) if args.calibration else None
    if decoding and variant != "context_relations":
        parser.error("Calibration requires context_relations")
    result = parse_structure(args.pdf, models, variant, decoding)
    result["decoding"] = decoding
    write_json(args.output, result)
    args.output.with_suffix(".md").write_text(markdown_text(result))
    print(f"{len(result['headings'])} headings; {result['total_seconds']:.2f}s")
