"""Render a two-dimensional field plot from the saved publisher table."""

import argparse
import json
from html import escape
from pathlib import Path

import pymupdf

from pdf_heading_benchmark.io import REPO

SOURCE = "https://github.com/datalab-to/omni_parse_bench#results"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir", type=Path, default=REPO / "docs/images")
args = parser.parse_args()
ROOT = args.output_dir
ROOT.mkdir(parents=True, exist_ok=True)
rows = json.loads((REPO / "configs/field-overview.json").read_text())["rows"]
if not all(60 <= row["text"] <= 100 and 85 <= row["layout"] <= 100 for row in rows):
    raise ValueError("Published scores exceed the displayed chart axes")
svg = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1120" viewBox="0 0 1400 1120">',
    '<rect width="1400" height="1120" fill="#fbfaf7"/>',
]


def text(x, y, content, size=21, extra=""):
    """Place escaped text in the chart."""
    svg.append(
        f'<text x="{x}" y="{y}" font-family="Helvetica" font-size="{size}" '
        f'fill="#243447" {extra}>{escape(content)}</text>'
    )


def coordinate(x, y):
    """Map scores onto the labelled, cropped plotting axes."""
    return 120 + (x - 60) * 29, 850 - (y - 85) * (620 / 15)


assert coordinate(60, 85) == (120, 850)
assert coordinate(100, 100) == (1280, 230)
text(65, 60, "The document parsing field", 42, 'font-weight="bold"')
text(65, 102, "Text extraction vs layout classification • Selected local models and hosted services", 24)
for x, color, label in [
    (65, "#087f8c", "Open models, locally runnable"),
    (490, "#6653c6", "Hosted services / models"),
]:
    svg.append(f'<circle cx="{x + 9}" cy="146" r="8" fill="{color}"/>')
    text(x + 28, 153, label, 21)
text(1035, 153, "Better toward top right ↗", 20)
text(120, 207, "Layout classification score", 21, 'font-weight="bold"')
for tick in range(85, 101, 3):
    _, y = coordinate(60, tick)
    svg.append(f'<line x1="120" y1="{y}" x2="1280" y2="{y}" stroke="#dfe4e8"/>')
    text(102, y + 7, str(tick), 19, 'text-anchor="end"')
for tick in range(60, 101, 5):
    x, _ = coordinate(tick, 85)
    svg.append(f'<line x1="{x}" y1="230" x2="{x}" y2="850" stroke="#dfe4e8"/>')
    text(x, 882, str(tick), 19, 'text-anchor="middle"')
for row in rows:
    x, y = coordinate(row["text"], row["layout"])
    color = "#087f8c" if row["category"] == "local" else "#6653c6"
    lx, ly = x + row["dx"], y + row["dy"]
    svg.append(f'<line x1="{x}" y1="{y}" x2="{lx}" y2="{ly - 5}" stroke="{color}" stroke-opacity="0.45"/>')
    svg.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{color}" stroke="#fbfaf7" stroke-width="2"/>')
    text(lx, ly, row["name"], 19)
text(700, 928, "Text extraction score", 23, 'text-anchor="middle" font-weight="bold"')
text(65, 980, "OmniParseBench 1.7.0 · Scores out of 100 · Axes cropped to show model differences", 20)
text(
    65,
    1012,
    "Source: Datalab\u2019s vendor-run benchmark, retrieved 26 November 2026. "
    "† Gemini includes failed-page retries.",
    19,
)
text(65, 1044, "Layout tests classify blocks as text, heading or table. They do not test heading levels.", 19)
text(
    65,
    1076,
    "github.com/datalab-to/omni_parse_bench · Models without published layout scores are omitted.",
    18,
)
svg.append("</svg>")
(ROOT / "ocr-text-layout.svg").write_text("\n".join(svg) + "\n")
with pymupdf.open(ROOT / "ocr-text-layout.svg") as document:
    document[0].get_pixmap(matrix=pymupdf.Matrix(2, 2)).save(ROOT / "ocr-text-layout.png")
print(ROOT / "ocr-text-layout.png")
