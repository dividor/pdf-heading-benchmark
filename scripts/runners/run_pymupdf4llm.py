"""Local CPU baseline, retaining PDF page numbers via page_chunks."""

import argparse
import importlib.metadata
import json
import re
import time
from pathlib import Path

import pymupdf4llm

parser = argparse.ArgumentParser()
parser.add_argument("pdf", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
start = time.perf_counter()
chunks = pymupdf4llm.to_markdown(str(args.pdf), page_chunks=True, use_ocr=False)
elapsed = time.perf_counter() - start
records = []
for chunk in chunks:
    for match in re.finditer(r"^(#{1,6})\s+(.+)$", chunk["text"], re.MULTILINE):
        records.append(
            {"page": chunk["metadata"]["page_number"], "level": len(match[1]), "title": match[2].strip()}
        )
(args.output / "pymupdf4llm.headings.json").write_text(json.dumps(records, indent=2))
(args.output / "pymupdf4llm.chunks.json").write_text(json.dumps(chunks, indent=2, default=str))
(args.output / "pymupdf4llm.md").write_text("\n\n".join(c["text"] for c in chunks))
metadata = {
    "package": "pymupdf4llm",
    "version": importlib.metadata.version("pymupdf4llm"),
    "seconds": elapsed,
    "pages": len(chunks),
    "headings": len(records),
    "ocr": False,
    "layout": True,
}
(args.output / "pymupdf4llm.run.json").write_text(json.dumps(metadata, indent=2))
print(json.dumps(metadata, indent=2), flush=True)
