"""Draw a reproducible comparison of published scores, separate from our WFP results."""

from html import escape

import pymupdf

from pdf_heading_benchmark.io import REPO, read_json


def text(x: int, y: int, value: str, size: int, bold: bool = False) -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}" '
        f'fill="#183247" font-weight="{700 if bold else 400}">{escape(value)}</text>'
    )


def chart(data: dict) -> str:
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="930" '
        'role="img" aria-labelledby="title desc">',
        '<title id="title">Do newer models beat Chandra 2?</title>',
        '<desc id="desc">Published OpenBMB comparisons on four benchmarks. MiniCPM, Xiaomi '
        "and Paddle lead Chandra on three; Chandra leads these candidates on olmOCR.</desc>",
        '<rect width="1200" height="930" fill="#f4f7fb"/>',
        text(35, 48, "Do newer models beat Chandra 2?", 32, True),
        text(35, 82, "Published scores · higher is better · compare within each panel", 20),
    ]
    for index, metric in enumerate(data["metrics"]):
        x, y = 30 + index % 2 * 590, 110 + index // 2 * 320
        parts.append(f'<rect x="{x}" y="{y}" width="565" height="300" rx="16" fill="white"/>')
        parts.append(text(x + 18, y + 36, metric, 23, True))
        for row, model in enumerate(data["models"]):
            score = model["scores"][index]
            baseline = row == 0
            color = "#6946a5" if baseline else "#087e88"
            line = y + 70 + row * 39
            parts.append(text(x + 18, line + 18, model["name"], 17, baseline))
            parts.append(
                f'<rect x="{x + 240}" y="{line}" width="{score * 2.5:.2f}" '
                f'height="24" rx="4" fill="{color}"/>'
            )
            parts.append(text(x + 492, line + 18, f"{score:.2f}", 17, True))
        parts.append(text(x + 240, y + 285, "Bar scale: 0 to 100", 14))
    parts += [
        text(
            35, 785, "Published parsing tests → candidate shortlist → our WFP heading + level test", 23, True
        ),
        text(
            35,
            825,
            "These scores are NOT our WFP joint F0.5. They do not establish correct H1/H2/H3 levels.",
            19,
        ),
        text(35, 861, "Source: OpenBMB / MiniCPM-OCR 1.0 comparison table · checked November 23, 2026", 18),
        text(
            35,
            895,
            "Original chart from reported values. Author-reported configurations; no new model runs.",
            18,
        ),
        "</svg>\n",
    ]
    return "\n".join(parts)


def main() -> None:
    data = read_json(REPO / "configs/published-comparison.json")
    path = REPO / "docs/images/published-comparison.svg"
    path.write_text(chart(data))
    with pymupdf.open(path) as document:
        document[0].get_pixmap(matrix=pymupdf.Matrix(1.6, 1.6)).save(str(path.with_suffix(".png")))


if __name__ == "__main__":
    main()
