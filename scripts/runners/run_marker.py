"""Marker's local no-OCR mode, with JSON provenance and heading tags."""

import argparse
import importlib.metadata
import json
import re
import time
from pathlib import Path

from bs4 import BeautifulSoup
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict, shutdown_models


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    models = create_model_dict(device="cpu", no_server=True)
    converter = PdfConverter(
        artifact_dict=models,
        renderer="marker.renderers.json.JSONRenderer",
        config={
            "mode": "no_ocr",
            "disable_ocr": True,
            "use_llm": False,
            "disable_image_extraction": True,
            "disable_tqdm": True,
        },
    )
    try:
        result = converter(str(args.pdf))
    finally:
        shutdown_models(models)
    elapsed = time.perf_counter() - start
    data = result.model_dump(mode="json")
    (args.output / "marker.document.json").write_text(json.dumps(data, indent=2))
    records = []

    def walk(block, page):
        if block["block_type"] == "SectionHeader":
            soup = BeautifulSoup(block["html"], "html.parser")
            header = soup.find(re.compile(r"^h[1-6]$"))
            records.append(
                {
                    "title": (header or soup).get_text(" ", strip=True),
                    "level": int(header.name[1]) if header else None,
                    "page": page,
                    "bbox": block["bbox"],
                    "ref": block["id"],
                }
            )
        for child in block.get("children") or []:
            walk(child, page)

    for i, page in enumerate(data["children"], 1):
        walk(page, i)
    (args.output / "marker.headings.json").write_text(json.dumps(records, indent=2))
    metadata = {
        "package": "marker-pdf",
        "version": importlib.metadata.version("marker-pdf"),
        "seconds_including_model_load_or_download": elapsed,
        "pages": len(data["children"]),
        "headings": len(records),
        "mode": "no_ocr",
        "use_llm": False,
    }
    (args.output / "marker.run.json").write_text(json.dumps(metadata, indent=2))
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    main()
