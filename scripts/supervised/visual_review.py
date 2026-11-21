"""Build an HTML annotation review pack with source images, TOCs and editable assessments."""

import argparse
from pathlib import Path

from pdf_heading_benchmark.visual_review import build_review

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build_review(args.data, args.run, args.output)
