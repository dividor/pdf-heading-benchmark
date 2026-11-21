"""Apply a trained JSON classifier to any PDF containing embedded text."""

import argparse
from pathlib import Path

from pdf_heading_benchmark.supervised_data import read_json, write_json
from pdf_heading_benchmark.supervised_inference import markdown_text, parse_document

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New output directory")
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Use a new output directory")
    result = parse_document(args.pdf, read_json(args.model))
    write_json(args.output / "document.json", result)
    (args.output / "document.md").write_text(markdown_text(result))
    print(
        {
            "lines": len(result["lines"]),
            "headings": len(result["headings"]),
            "seconds": result["total_seconds"],
        }
    )
