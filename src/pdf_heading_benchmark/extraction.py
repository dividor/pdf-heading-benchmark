"""Initialize an independent run on a reader's own document."""

import hashlib
import shutil
from pathlib import Path

import pymupdf

from pdf_heading_benchmark.io import write_json


def initialize(pdf: Path, output: Path) -> None:
    """Refuse an existing run to avoid mixing page caches from different documents."""
    if output.exists():
        raise FileExistsError(f"Choose a new output directory; {output} already exists.")
    with pymupdf.open(pdf) as document:
        pages = len(document)
    for name in ("corpus", "results/document", "reference", "models", "vendor", "logs"):
        (output / name).mkdir(parents=True)
    destination = output / "corpus/document.pdf"
    shutil.copyfile(pdf, destination)
    write_json(
        output / "corpus/manifest.json",
        [
            dict(
                id="document",
                title=pdf.stem,
                path=str(destination),
                pages=pages,
                sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
            )
        ],
    )
    write_json(output / "reference/audit_pages.json", {"document": list(range(1, pages + 1))})
