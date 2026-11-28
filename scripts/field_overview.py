"""Render the complete saved field snapshot as an SVG and a blog-ready PNG."""

import argparse
from pathlib import Path

import pymupdf

from pdf_heading_benchmark.field_charts import export_svg
from pdf_heading_benchmark.io import REPO, read_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=REPO / "docs/images")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    svg = export_svg(read_json(REPO / "configs/field-overview.json"))
    target = args.output_dir / "ocr-text-layout.svg"
    target.write_text(svg + "\n")
    with pymupdf.open(target) as document:
        document[0].get_pixmap(matrix=pymupdf.Matrix(2, 2)).save(args.output_dir / "ocr-text-layout.png")
    print(target)


if __name__ == "__main__":
    main()
