"""One text/layout chart, with a strict layout threshold and collision-free labels."""

from html import escape
from math import hypot

import pymupdf

from pdf_heading_benchmark.io import REPO, read_json

COLORS = {"study": "#007d79", "local": "#71839b", "hosted": "#8055b4"}


def eligible_rows(data: dict) -> list[dict]:
    return [row for row in data["rows"] if row["layout"] is not None and row["layout"] > 70]


def coordinate(text: float, layout: float) -> tuple[float, float]:
    if not 20 <= text <= 100 or not 70 <= layout <= 100:
        raise ValueError("Published coordinates fall outside the displayed axes")
    return 80 + (text - 20) * 10.75, 655 - (layout - 70) * 18


def category(row: dict, detail: dict) -> str:
    return "study" if detail["study_method"] else row["category"]


def svg_text(x, y, content, size=16, extra="") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="Helvetica,Arial,sans-serif" font-size="{size}" '
        f'fill="#263b4a" {extra}>{escape(content)}</text>'
    )


def axis_label(axis: str, title: str, transform: str, width: int) -> str:
    return (
        f'<g class="field-axis" transform="{transform}" data-open-dialog="field-axis-{axis}" '
        f'role="button" tabindex="0" aria-haspopup="dialog" aria-controls="field-axis-{axis}" '
        f'aria-label="About {title.lower()}">'
        f'<rect x="{-width / 2}" y="-21" width="{width}" height="40" rx="5" '
        'fill="white" fill-opacity="0"/>'
        + svg_text(-12, 5, title, 19, 'text-anchor="middle" font-weight="bold"')
        + f'<circle cx="{width / 2 - 14}" cy="-1" r="8" fill="none" stroke="#526673"/>'
        + svg_text(width / 2 - 14, 4, "i", 13, 'text-anchor="middle"')
        + "</g>"
    )


def grid() -> str:
    parts = [axis_label("layout", "Layout score", "translate(23 385) rotate(-90)", 168)]
    for tick in range(70, 101, 5):
        _, y = coordinate(20, tick)
        parts += [
            f'<line x1="80" y1="{y}" x2="940" y2="{y}" stroke="#e1e7ec"/>',
            svg_text(65, y + 6, str(tick), 16, 'text-anchor="end"'),
        ]
    for tick in range(20, 101, 20):
        x, _ = coordinate(tick, 70)
        parts += [
            f'<line x1="{x}" y1="115" x2="{x}" y2="655" stroke="#e1e7ec"/>',
            svg_text(x, 683, str(tick), 16, 'text-anchor="middle"'),
        ]
    parts.append(axis_label("text", "Text extraction score", "translate(510 724)", 250))
    return "".join(parts)


def overlaps(a: tuple, b: tuple) -> bool:
    return a[0] < b[0] + b[2] and a[0] + a[2] > b[0] and a[1] < b[1] + b[3] and a[1] + a[3] > b[1]


def label_candidates(x: float, y: float, width: float) -> list[tuple]:
    """Try nearby labels first, then available space farther from a crowded point."""
    candidates = []
    for distance in range(12, 109, 24):
        for dx, dy in [(1, 0), (-1, 0), (0, -1), (0, 1), (1, -1), (-1, -1), (1, 1), (-1, 1)]:
            left = x + distance * dx - (width if dx < 0 else width / 2 if dx == 0 else 0)
            top = y + distance * dy - 10
            box = (round(left, 2), round(top, 2), width, 22)
            if left >= 85 and left + width <= 970 and top >= 64 and top + 22 <= 646:
                candidates.append(box)
    return sorted(candidates, key=lambda box: hypot(box[0] + box[2] / 2 - x, box[1] + 11 - y))


def label_positions(rows: list[dict], details: dict) -> dict[int, tuple]:
    """Keep labels clear of every marker and earlier label; prioritize study models."""
    positions: dict[int, tuple] = {}
    markers = [(x - 10, y - 10, 20, 20) for x, y in (coordinate(r["text"], r["layout"]) for r in rows)]
    priority = sorted(
        range(len(rows)),
        key=lambda i: (not details[rows[i]["name"]]["study_method"], rows[i]["category"] != "hosted", i),
    )
    for index in priority:
        row = rows[index]
        width = round(pymupdf.get_text_length(details[row["name"]]["label"], fontsize=15) + 10, 2)
        for box in label_candidates(*coordinate(row["text"], row["layout"]), width):
            if not any(overlaps(box, occupied) for occupied in [*markers, *positions.values()]):
                positions[index] = box
                break
    return positions


def point(row: dict, detail: dict, index: int) -> str:
    x, y = coordinate(row["text"], row["layout"])
    color = COLORS[category(row, detail)]
    label = f"{row['name']}. Text {row['text']:.1f}. Layout {row['layout']:.1f}. Open model details."
    attributes = (
        f'class="field-point" id="field-marker-{index}" data-index="{index}" '
        f'data-category="{category(row, detail)}" '
        f'data-name="{escape(row["name"], quote=True)}" data-text="{row["text"]}" '
        f'data-layout="{row["layout"]}" tabindex="0" role="button" aria-haspopup="dialog" '
        f'aria-controls="field-model-{index}" aria-label="{escape(label, quote=True)}"'
    )
    shape = (
        f'<rect x="{x - 6}" y="{y - 6}" width="12" height="12" rx="1"'
        if row["category"] == "hosted"
        else f'<circle cx="{x}" cy="{y}" r="6"'
    )
    return (
        f"<g {attributes}><title>{escape(label)}</title>"
        f'<circle class="field-hit" cx="{x}" cy="{y}" r="11" fill="white" fill-opacity="0"/>'
        f'{shape} fill="{color}" stroke="white" stroke-width="1.5"/></g>'
    )


def plot_svg(data: dict) -> str:
    rows = eligible_rows(data)
    details = read_json(REPO / "configs/field-model-details.json")
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="750" viewBox="0 0 1000 750" '
        'class="field-svg" role="group" aria-label="Published text and layout scores above 70 layout">',
        '<rect width="1000" height="750" fill="#fff"/>',
        grid(),
    ]
    labels = []
    for index, (left, top, width, height) in label_positions(rows, details).items():
        row = rows[index]
        x, y = coordinate(row["text"], row["layout"])
        end_x, end_y = max(left, min(left + width, x)), max(top, min(top + height, y))
        parts += [
            f'<g class="field-label" data-for="{index}">'
            f'<line x1="{x}" y1="{y}" x2="{end_x}" y2="{end_y}" stroke="#9cabb8" stroke-width="0.8"/></g>',
        ]
        labels += [
            f'<g class="field-label field-name" data-for="{index}" data-open-model="{index}" '
            f'tabindex="0" role="button" aria-haspopup="dialog" aria-controls="field-model-{index}" '
            f'aria-label="Model details for {escape(row["name"], quote=True)}">',
            f'<rect x="{left}" y="{top}" width="{width}" height="{height}" '
            'rx="3" fill="white" fill-opacity="0.94"/>',
            svg_text(left + 5, top + 16, details[row["name"]]["label"], 15),
            "</g>",
        ]
    parts.extend(labels)
    parts.append('<g class="field-points">')
    draw_order = sorted(enumerate(rows), key=lambda item: item[1]["category"] == "hosted")
    parts.extend(point(row, details[row["name"]], i) for i, row in draw_order)
    parts.append("</g>")
    parts.append(
        '<use class="field-active-marker" href="#field-marker-0" display="none" '
        'aria-hidden="true" pointer-events="none" hidden="hidden"/>'
    )
    parts.append(
        '<g class="field-tooltip" pointer-events="none" hidden="hidden">'
        '<rect rx="4" fill="#263b4a"/><text fill="white" font-family="Helvetica,Arial,sans-serif" '
        'font-size="17"></text></g>'
    )
    return "".join([*parts, "</svg>"])


def export_svg(data: dict) -> str:
    plot = (
        '<g transform="translate(10 105)">' + plot_svg(data).split(">", 1)[1].removesuffix("</svg>") + "</g>"
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1020" height="960" viewBox="0 0 1020 960">'
        '<rect width="1020" height="960" fill="white"/>'
        + svg_text(45, 42, "The document parsing field", 28, 'font-weight="bold"')
        + svg_text(
            45, 73, f"{data['benchmark']} · {len(eligible_rows(data))} systems with layout above 70", 18
        )
        + '<circle cx="51" cy="99" r="6" fill="#007d79"/>'
        + svg_text(65, 105, "Tested in our WFP study", 16)
        + '<circle cx="314" cy="99" r="6" fill="#71839b"/>'
        + svg_text(328, 105, "Other open models & tools", 16)
        + '<rect x="610" y="93" width="12" height="12" fill="#8055b4"/>'
        + svg_text(636, 105, "Hosted APIs & services", 16)
        + plot
        + svg_text(
            45, 879, f"Datalab's published scores · {data['retrieved']} · Not our WFP measurements", 16
        )
        + svg_text(
            45,
            908,
            "Layout measures block classification, not heading levels. † Includes failed-page retries.",
            16,
        )
        + svg_text(
            45,
            937,
            "Source: github.com/datalab-to/omni_parse_bench · "
            "Study colors match models/tools, not configurations",
            15,
        )
        + "</svg>"
    )
