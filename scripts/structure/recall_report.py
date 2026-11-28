"""Publish the completed coverage retraining trial without replacing earlier evidence."""

from markdown_it import MarkdownIt
from precision_report import aggregate

from pdf_heading_benchmark.io import REPO, read_json, write_json
from pdf_heading_benchmark.report import table

KEY = "structure_recall"
OUT = REPO / "outputs/structure-recall"
REMOTE = "https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/"


def publish_row(historical: dict) -> dict:
    counts = aggregate(historical["scores"])
    row = dict(
        method=KEY,
        name="OUR METHOD — retrained trees (coverage trial; target not met)",
        source_url=REMOTE + "outputs/structure-recall/report.md",
        status="completed",
        documents_scored=4,
        **counts,
        heading_recall=counts["matched"] / counts["gold"],
        correct_heading_and_level=counts["correct_level"] / counts["gold"],
        false_headings=counts["predicted"] - counts["matched"],
        native_prose_retention=None,
        measured_seconds=sum(t["seconds"] for t in historical["timings"]),
        processed_pages=523,
    )
    rows = [r for r in read_json(REPO / "outputs/league_table.json") if r["method"] != KEY] + [row]
    rows.sort(
        key=lambda r: r["correct_heading_and_level"] if r["correct_heading_and_level"] is not None else -1,
        reverse=True,
    )
    write_json(REPO / "outputs/league_table.json", rows)
    details = [r for r in read_json(REPO / "outputs/league_details.json") if r["method"] != KEY]
    write_json(
        REPO / "outputs/league_details.json", details + [dict(s, method=KEY) for s in historical["scores"]]
    )
    predictions = read_json(REPO / "outputs/audit_predictions.json")
    predictions[KEY] = read_json(OUT / "evidence/historical-audit.json")
    write_json(REPO / "outputs/audit_predictions.json", predictions)
    return counts


def main() -> None:
    regression = read_json(OUT / "evidence/regression.json")
    historical = publish_row(read_json(OUT / "evidence/historical.json"))
    datasets = [
        ("Validation (selection)", regression["validation"]),
        ("Inspected 38-heading regression", regression["test"]),
        ("Original 77-heading league (regression)", historical),
    ]
    rows = [
        [
            name,
            f"{s['joint_f05']:.1%}",
            f"{s['joint_precision']:.1%}",
            f"{s['joint_recall']:.1%}",
            f"{s['correct_level']}/{s['gold']}",
            f"{s['matched']}/{s['gold']}",
            s["predicted"] - s["matched"],
            s["matched"] - s["correct_level"],
        ]
        for name, s in datasets
    ]
    results = table(
        [
            "Dataset",
            "Joint F0.5",
            "Joint precision",
            "Joint recall",
            "Correct + level",
            "Titles found",
            "Extras",
            "Wrong levels",
        ],
        rows,
    )
    markdown = (REPO / "docs/structure-recall.md").read_text().replace("__RESULTS__", results)
    (OUT / "report.md").write_text(markdown)
    rendered = MarkdownIt("commonmark").enable("table").render(markdown)
    css = (REPO / "docs/report.css").read_text()
    (OUT / "index.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>Heading coverage retraining experiment</title><style>{css}</style></head>"
        f"<body><main>{rendered}</main></body></html>\n"
    )


if __name__ == "__main__":
    main()
