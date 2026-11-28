"""Export saved Chandra HTML with the pinned author's Markdown converter."""

import argparse
import json
import sys
from pathlib import Path

from decode_chandra import chandra_headings

from pdf_heading_benchmark.heading_exports import write_heading_list


def export(root, convert):
    pages = json.loads((root / "reference/audit_pages.json").read_text())
    for document, numbers in pages.items():
        output = root / "results" / document
        markdown, headings = [], []
        for number in numbers:
            record = json.loads((output / "chandra2_mlx" / f"{number}.json").read_text())
            if record["error"] or record["hit_token_limit"]:
                raise ValueError(f"Incomplete Chandra output on page {number}")
            text = convert(record["text"], include_headers_footers=True, include_images=False)
            if record["text"].strip() and not text.strip():
                raise ValueError(f"Markdown conversion returned empty text on page {number}")
            markdown.append(f"<!-- Original PDF page {number} -->\n\n{text}")
            headings.extend(chandra_headings(record["text"], number))
        write_heading_list(output / "chandra2.predicted-headings.md", headings, "Chandra OCR 2")
        (output / "chandra2.markdown.md").write_text("\n\n".join(markdown) + "\n")
        (output / "chandra2.predicted-headings.json").write_text(
            json.dumps(headings, ensure_ascii=False, indent=2) + "\n"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.data / "vendor/chandra"))
    from chandra.output import parse_markdown

    export(args.data, parse_markdown)
