"""Run the validation-selected recall experiment on a new native-text PDF."""

import argparse
import os
from pathlib import Path

from pdf_heading_benchmark.precision_inference import parse_precision
from pdf_heading_benchmark.recall_inference import load_recall
from pdf_heading_benchmark.supervised_data import write_json
from pdf_heading_benchmark.supervised_inference import markdown_text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--run", type=Path, default=os.environ.get("PDF_HEADING_RECALL_RUN"))
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if not args.run:
        parser.error("Supply --run or PDF_HEADING_RECALL_RUN")
    target = args.output / "structure_recall.document.json"
    if target.exists():
        raise ValueError("Use a new output directory")
    models, settings = load_recall(args.run)
    result = parse_precision(args.pdf, models, settings)
    write_json(target, result)
    write_json(
        args.output / "structure_recall.headings.json",
        [{"page": h["page"], "title": h["text"], "level": h["level"]} for h in result["headings"]],
    )
    (args.output / "structure_recall.md").write_text(markdown_text(result))
    write_json(
        args.output / "structure_recall.run.json",
        dict(
            seconds=result["total_seconds"],
            settings=settings,
            scope="Full PDF extraction/features/inference; excludes model loading and writes",
        ),
    )


if __name__ == "__main__":
    main()
