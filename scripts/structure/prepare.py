"""Extract checksum-verified members from a local WFP archive and prepare partial labels."""

import argparse
from pathlib import Path

from pdf_heading_benchmark.structure_data import prepare
from pdf_heading_benchmark.supervised_data import extract_archive, read_json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/structure-v2"))
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    if args.archive:
        extract_archive(args.archive, read_json(args.config / "corpus.json"), args.data / "pdfs")
    prepare(args.config, args.data)
