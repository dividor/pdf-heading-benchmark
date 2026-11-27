"""Prepare frozen labels from verified public PDFs or a local WFP archive."""

import argparse
from pathlib import Path

from pdf_heading_benchmark.structure_data import prepare
from pdf_heading_benchmark.supervised_data import extract_archive, read_json
from pdf_heading_benchmark.training_download import download_training

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/structure-v2"))
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--archive", type=Path)
    source.add_argument("--download", action="store_true", help="Download exact manifest PDFs publicly")
    args = parser.parse_args()
    if args.archive:
        extract_archive(args.archive, read_json(args.config / "corpus.json"), args.data / "pdfs")
    if args.download:
        download_training(args.config, args.data)
    prepare(args.config, args.data)
