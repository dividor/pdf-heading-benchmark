"""Import complete external OCR trials; rebuild published scores offline thereafter."""

import argparse
from pathlib import Path

from pdf_heading_benchmark.evaluation import evaluate
from pdf_heading_benchmark.field_evidence import import_evidence
from pdf_heading_benchmark.io import REPO, read_json, write_json
from pdf_heading_benchmark.joint_metrics import scored_counts
from pdf_heading_benchmark.report import table
from pdf_heading_benchmark.timing_format import readable_time

OUT = REPO / "outputs/field-candidates"
VARIANTS = {
    "minicpm_ocr10": "MiniCPM-OCR 1.0 — MLX + CPU layout",
    "xiaomi_ocr0": "Xiaomi-OCR-0 — MLX whole page",
    "paddleocr_vl16": "PaddleOCR-VL-1.6 — MLX + CPU layout",
}


def score(key: str, evidence: dict) -> tuple[dict, list[dict]]:
    gold = read_json(REPO / "configs/gold.json")
    pages = read_json(REPO / "configs/audit_pages.json")
    scores = [
        dict(document=doc, method=key, **evaluate(gold[doc], heads, pages[doc]))
        for doc, heads in evidence["predictions"].items()
    ]
    counts = scored_counts(
        {field: sum(s[field] for s in scores) for field in ("gold", "predicted", "matched", "correct_level")}
    )
    prose = evidence["prose"].values()
    return dict(
        method=key,
        name=VARIANTS[key],
        source_url="https://huggingface.co/" + evidence["protocol"]["models"][key]["repo"],
        status="completed",
        documents_scored=len(scores),
        **counts,
        heading_recall=counts["matched"] / counts["gold"],
        correct_heading_and_level=counts["correct_level"] / counts["gold"],
        false_headings=counts["predicted"] - counts["matched"],
        native_prose_retention=sum(p["retained"] for p in prose) / sum(p["total"] for p in prose),
        measured_seconds=evidence["timing"]["seconds"],
        processed_pages=evidence["timing"]["pages"],
    ), scores


def publish() -> None:
    keys = [key for key in VARIANTS if (OUT / f"{key}.json").exists()]
    rows = [r for r in read_json(REPO / "outputs/league_table.json") if r["method"] not in keys]
    details = [r for r in read_json(REPO / "outputs/league_details.json") if r["method"] not in keys]
    predictions = read_json(REPO / "outputs/audit_predictions.json")
    for key in keys:
        evidence = read_json(OUT / f"{key}.json")
        row, scores = score(key, evidence)
        rows.append(row)
        details.extend(scores)
        predictions[key] = evidence["predictions"]
    rows.sort(key=lambda r: r["correct_heading_and_level"] or -1, reverse=True)
    write_json(REPO / "outputs/league_table.json", rows)
    write_json(REPO / "outputs/league_details.json", details)
    write_json(REPO / "outputs/audit_predictions.json", predictions)
    write_summary([r for r in rows if r["method"] in keys])


def write_summary(rows: list[dict]) -> None:
    rendered = []
    for row in rows:
        key = row["method"]
        evidence = read_json(OUT / f"{key}.json")
        timing = evidence["timing"]
        rendered.append(
            [
                f"[{row['name']}]({key}.json)",
                f"{row['joint_f05']:.1%}",
                f"{row['correct_level']}/{row['gold']}",
                f"{row['matched']}/{row['gold']}",
                row["false_headings"],
                f"{row['native_prose_retention']:.1%}",
                readable_time(timing["seconds"] / timing["pages"]),
                readable_time(timing["seconds"]),
                readable_time(timing["load_seconds"]),
                timing["errors"],
                timing["timeouts"],
                timing["token_limits"],
            ]
        )
    content = "# New local OCR trials on the WFP sample\n\n"
    content += "Same four public PDFs, 32 audit pages and 77 references. "
    content += "[Protocol, model revisions and reproduction](../../docs/field-candidates.md). "
    content += "Each model ran separately; recognition uses Metal and regional layout uses CPU. "
    content += "These are portable configurations, not replications of the external NVIDIA leaderboard. "
    content += "No PDF tags, text inputs, previous-page memory or gold-tuned level corrections.\n\n"
    content += table(
        [
            "Configuration / evidence",
            "Joint F0.5",
            "Correct title + level",
            "Titles found",
            "Extra headings",
            "Prose retention",
            "Time per page",
            "Measured time / 32 pages",
            "Loading (separate)",
            "Errors",
            "Pages with timeout",
            "Pages hitting token cap",
        ],
        rendered,
    )
    content += "\n\nJoint F0.5 = 1.25C / (P + 0.25G). The main report includes joint precision, "
    content += "recall and every predicted-versus-reference heading. Prose retention is five-word-sequence "
    content += (
        "recall from native paragraphs of at least 50 words; it is not table or reading-order accuracy.\n"
    )
    (OUT / "report.md").write_text(content)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path)
    parser.add_argument("--data", type=Path)
    parser.add_argument("--candidate", choices=VARIANTS)
    args = parser.parse_args()
    if args.runs:
        if not args.data or not args.candidate:
            parser.error("--runs requires --data and --candidate")
        evidence = import_evidence(args.runs / args.candidate, args.candidate, args.data)
        write_json(OUT / f"{args.candidate}.json", evidence)
    publish()


if __name__ == "__main__":
    main()
