"""Render Medium-friendly score/time panels from the generated report, preserving every row."""

import textwrap
from html import escape

import pymupdf

from pdf_heading_benchmark.io import REPO, read_json
from pdf_heading_benchmark.timing_format import readable_time

NAMES = {
    "qwen36_35b_visual_memory": "Qwen3.6-35B-A3B + visual memory",
    "qwen36_27b_compact": "Qwen3.6-27B / single image",
    "qwen36_35b_compact": "Qwen3.6-35B-A3B / single image",
    "structure_recall": "OUR METHOD: coverage retraining",
    "structure_precision": "OUR METHOD: confidence filter v2",
    "structure_context_relations": "OUR METHOD: context + relations v2",
    "structure_calibrated": "OUR METHOD: earlier calibration",
    "structure_learned_groups": "OUR METHOD: learned grouping v2",
    "structure_expanded_line": "OUR METHOD: expanded line v2",
    "supervised_extra_trees": "OUR METHOD: Extra Trees v1",
    "qwen36_visual_memory": "Qwen3.6-27B + visual memory",
    "qwen_ids_union": "Qwen3.5-4B / union candidates",
    "qwen_ids_mineru_basic": "Qwen3.5-4B / MinerU candidates",
    "qwen_ids_pymupdf4llm": "Qwen3.5-4B / PyMuPDF candidates",
    "mineru_pro_mlx": "MinerU Pro 1.2B / direct MLX",
}


def text(x: int, y: int, value, size: int = 20, bold: bool = False, color: str = "#183247") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}" fill="{color}" '
        f'font-weight="{700 if bold else 400}">{escape(str(value))}</text>'
    )


def score_cells(row: dict, y: int) -> list[str]:
    return [
        text(490, y + 29, f"{row['joint_f05']:.1%}", 23, True),
        text(660, y + 29, f"{row['joint_precision']:.1%}", 23, True),
        text(660, y + 55, f"{row['correct_level']}/{row['predicted']}", 17),
        text(865, y + 29, f"{row['joint_recall']:.1%}", 22, True),
        text(865, y + 55, f"{row['correct_level']}/{row['gold']}", 17),
        text(1020, y + 29, row["false_headings"], 22, True),
        text(1130, y + 29, row["gold"] - row["matched"], 22, True),
    ]


def time_cells(row: dict, y: int) -> list[str]:
    seconds = row["measured_seconds"]
    duration = readable_time(seconds / row["processed_pages"]) if row["processed_pages"] else "—"
    pages = row["processed_pages"]
    total = readable_time(seconds / pages * 32) if pages else "Unavailable"
    scope = "Measured" if pages == 32 else (f"Estimated from {pages} pages" if pages else "No page count")
    prose = row["native_prose_retention"]
    return [
        text(570, y + 29, duration, 22, True),
        text(790, y + 29, total, 22, True),
        text(790, y + 55, scope, 17),
        text(1130, y + 29, "—" if prose is None else f"{prose:.1%}"),
    ]


def panel(kind: str, rows: list[dict]) -> str:
    height = 300 + 74 * len(rows)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="{height}">',
        f'<rect width="1300" height="{height}" fill="white"/>',
    ]
    title = (
        "Heading + level quality: precision matters"
        if kind == "quality"
        else "Local processing: per page and 32 pages"
    )
    parts += [
        text(30, 48, title, 32, True),
        text(30, 85, f"{len(rows)} local configurations · 77 reference headings · 32 audited pages"),
    ]
    parts.append('<rect x="20" y="110" width="1260" height="70" fill="#e5eff7"/>')
    columns = [
        (30, "Configuration"),
        (490, "Joint F0.5"),
        (660, "Joint precision"),
        (865, "Joint recall"),
        (1020, "Extras"),
        (1130, "Missed titles"),
    ]
    if kind == "timings":
        columns = [
            (30, "Configuration"),
            (570, "Time per page"),
            (790, "Time for 32 pages"),
            (1130, "Prose kept"),
        ]
    parts += [text(x, 150, label, 20, True) for x, label in columns]
    for index, row in enumerate(rows):
        y = 180 + 74 * index
        color = (
            "#fff2bd"
            if row["method"] == "structure_precision"
            else ("#f1f6f9" if index % 2 == 0 else "white")
        )
        parts.append(f'<rect x="20" y="{y}" width="1260" height="74" fill="{color}"/>')
        name = NAMES.get(row["method"], row["name"])
        parts += [
            text(30, y + 28 + 25 * line, content)
            for line, content in enumerate(textwrap.wrap(f"{index + 1}. {name}", 39))
        ]
        parts += score_cells(row, y) if kind == "quality" else time_cells(row, y)
    notes = [
        "Joint F0.5 = 1.25C / (P + 0.25G). Wrong levels and extra headings both reduce the score.",
        "Joint precision = correct pairs / predictions. Joint recall = correct pairs / reference headings.",
        "Frozen sample; single assistant annotator. The new filter trades recall for fewer false headings.",
    ]
    if kind == "timings":
        notes = [
            "Shared 48 GB Apple M4 Pro. Timings have different scopes; not a controlled speed benchmark.",
            "Qwen/Popo exclude upstream extraction. The precision model includes full-PDF extraction.",
            "Local hardware, electricity, setup, review and licensing costs were not measured in dollars.",
        ]
    parts += [text(30, height - 82 + 29 * i, note, 19) for i, note in enumerate(notes)]
    return "\n".join([*parts, "</svg>"]) + "\n"


def main() -> None:
    rows = read_json(REPO / "outputs/report/results.json")
    for kind in ("quality", "timings"):
        path = REPO / "docs/images" / f"on-prem-{kind}.svg"
        path.write_text(panel(kind, rows))
        with pymupdf.open(path) as document:
            document[0].get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3)).save(str(path.with_suffix(".png")))


if __name__ == "__main__":
    main()
