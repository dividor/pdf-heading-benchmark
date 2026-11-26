"""Publish calibrated decoding as a separate diagnostic row; never replace frozen v2 scores."""

from markdown_it import MarkdownIt

from pdf_heading_benchmark.io import REPO, read_json, write_json
from pdf_heading_benchmark.report import build_report, table

OUT = REPO / "outputs/structure-calibration"
REMOTE = "https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/"
KEY = "structure_calibrated"


def update_league(result: dict) -> None:
    scores = [dict(s, method=KEY) for s in result["scores"]]
    counts = {k: sum(s[k] for s in scores) for k in ["gold", "predicted", "matched", "correct_level"]}
    row = {
        "method": KEY,
        "name": "OUR METHOD v2 + calibrated decoding (CPU)",
        "source_url": REMOTE + "outputs/structure-calibration/report.md",
        "status": "completed",
        "documents_scored": 4,
        **counts,
        "heading_recall": counts["matched"] / counts["gold"],
        "correct_heading_and_level": counts["correct_level"] / counts["gold"],
        "false_headings": counts["predicted"] - counts["matched"],
        "native_prose_retention": None,
        "measured_seconds": sum(t["seconds"] for t in result["timings"]),
        "processed_pages": 523,
    }
    rows = [r for r in read_json(REPO / "outputs/league_table.json") if r["method"] != KEY] + [row]
    rows.sort(key=lambda r: r["correct_heading_and_level"] or -1, reverse=True)
    write_json(REPO / "outputs/league_table.json", rows)
    details = [r for r in read_json(REPO / "outputs/league_details.json") if r["method"] != KEY]
    write_json(REPO / "outputs/league_details.json", details + scores)
    predictions = read_json(REPO / "outputs/audit_predictions.json")
    predictions[KEY] = read_json(OUT / "evidence/historical-audit.json")
    write_json(REPO / "outputs/audit_predictions.json", predictions)


def result_tables(selection: dict, regression: dict, historical: dict) -> dict:
    validations = selection["validation"]
    rows = []
    for name, val in [("baseline", validations[0]), ("selected", selection["selected"])]:
        r = regression["results"][name]
        rows.append(
            [
                name,
                f"{val['score']['group_level_f1']:.1%}",
                f"{r['group_level_f1']:.1%}",
                f"{r['matched']}/38",
                f"{r['correct']}/38",
                r["predicted"] - r["matched"],
            ]
        )
    per_doc = regression["results"]["selected"]["per_document"]
    seconds = sum(t["seconds"] for t in historical["timings"])
    return {
        "RESULTS": table(
            ["Setting", "Validation F1", "Regression F1", "Recovered", "Correct + level", "False"], rows
        ),
        "PER_DOCUMENT": table(
            ["Report ID", "Exact F1", "Recovered", "Correct + level", "False"],
            [
                [
                    key,
                    f"{r['group_level_f1']:.1%}",
                    f"{r['matched']}/{r['gold']}",
                    f"{r['correct']}/{r['gold']}",
                    r["predicted"] - r["matched"],
                ]
                for key, r in per_doc.items()
            ],
        ),
        "HISTORICAL": table(
            ["Report", "Recovered", "Correct + level", "False"],
            [
                [
                    r["document"],
                    f"{r['matched']}/{r['gold']}",
                    f"{r['correct_level']}/{r['gold']}",
                    r["predicted"] - r["matched"],
                ]
                for r in historical["scores"]
            ],
        ),
        "TIMING": (
            f"{seconds:.2f} seconds / actual 523 pages; "
            f"{seconds * 500 / 523:.2f} seconds normalized to 500 pages."
        ),
        "GRID": table(
            ["Body weight", "Relationship weight", "Validation exact F1"],
            [
                [
                    r["decoding"]["body_weight"],
                    r["decoding"]["relation_weight"],
                    f"{r['score']['group_level_f1']:.1%}",
                ]
                for r in validations
            ],
        ),
    }


def main() -> None:
    evidence = OUT / "evidence"
    selection = read_json(evidence / "selection.json")
    regression = read_json(evidence / "regression.json")
    historical = read_json(evidence / "historical.json")
    markdown = (REPO / "docs/structure-calibration.md").read_text()
    for key, value in result_tables(selection, regression, historical).items():
        markdown = markdown.replace("__" + key + "__", value)
    (OUT / "report.md").write_text(markdown)
    rendered = MarkdownIt("commonmark").enable("table").render(markdown)
    css = (REPO / "docs/report.css").read_text()
    (OUT / "index.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>Heading decision calibration</title><style>{css}</style></head>"
        f"<body><main>{rendered}</main></body></html>\n"
    )
    update_league(historical)
    build_report()


if __name__ == "__main__":
    main()
