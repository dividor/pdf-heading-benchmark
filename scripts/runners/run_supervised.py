"""Apply a previously trained local classifier; set PDF_HEADING_MODEL to its JSON file."""

import argparse
import os
from pathlib import Path

from pdf_heading_benchmark.io import read_json, write_json
from pdf_heading_benchmark.supervised_inference import markdown_text, parse_document

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    model = os.environ.get("PDF_HEADING_MODEL")
    if not model:
        parser.error("Set PDF_HEADING_MODEL to a trained JSON model; see scripts/supervised/train.py")
    target = args.output / "supervised_extra_trees.headings.json"
    if target.exists():
        raise ValueError("Existing predictions must not be overwritten")
    result = parse_document(args.pdf, read_json(Path(model)))
    write_json(args.output / "supervised_extra_trees.document.json", result)
    write_json(
        target, [{"page": h["page"], "level": h["level"], "title": h["text"]} for h in result["headings"]]
    )
    (args.output / "supervised_extra_trees.md").write_text(markdown_text(result))
    write_json(
        args.output / "supervised_extra_trees.run.json",
        {
            "seconds": result["total_seconds"],
            "model": Path(model).name,
            "pages_with_text": len({r["page"] for r in result["lines"]}),
        },
    )
