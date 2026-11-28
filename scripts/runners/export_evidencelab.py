"""Copy native EvidenceLab Markdown and final TOC into a reviewable output folder."""

import argparse
import json
import shutil
from pathlib import Path

from pdf_heading_benchmark.heading_exports import write_heading_list
from pdf_heading_benchmark.pipeline_evidence import read_document


def export(run: Path, document: str, output: Path) -> None:
    _, headings, hashes = read_document(run, document, "evidencelab")
    output.mkdir(parents=True, exist_ok=True)
    folder = run / "parsed/other" / document
    shutil.copyfile(folder / f"{document}.md", output / "evidencelab.md")
    shutil.copyfile(folder / "toc.txt", output / "evidencelab-headings.txt")
    (output / "evidencelab-headings.json").write_text(
        json.dumps(headings, ensure_ascii=False, indent=2) + "\n"
    )
    (output / "evidencelab-source-hashes.json").write_text(json.dumps(hashes, indent=2) + "\n")
    write_heading_list(output / "evidencelab-headings.md", headings, "EvidenceLab")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--document", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    export(args.run, args.document, args.output)
