"""Render frozen review pages and line inventories for independent annotation review."""

import argparse
from pathlib import Path

import pymupdf

from pdf_heading_benchmark.supervised_data import read_json, write_json
from pdf_heading_benchmark.supervised_features import extract_lines


def render_review(config: Path, data: Path, output: Path) -> None:
    if output.exists():
        raise ValueError("Use a new review directory")
    for record in read_json(config / "corpus.json"):
        pdf = data / "pdfs" / f"wfp-{record['id']}.pdf"
        destination = output / str(record["id"])
        lines = [line for line in extract_lines(pdf) if line["page"] in record["review_pages"]]
        write_json(destination / "lines.json", lines)
        with pymupdf.open(pdf) as document:
            for number in record["review_pages"]:
                page = document[number - 1]
                page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).save(destination / f"page-{number:03d}.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/supervised"))
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    render_review(args.config, args.data, args.output)
