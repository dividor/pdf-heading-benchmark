"""Publish the frozen precision experiment and add its separately measured league row."""

from markdown_it import MarkdownIt

from pdf_heading_benchmark.io import REPO, read_json, write_json
from pdf_heading_benchmark.joint_metrics import scored_counts
from pdf_heading_benchmark.report import table

OUT = REPO / "outputs/structure-precision"
REMOTE = "https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/"
KEY = "structure_precision"


def aggregate(scores: list[dict]) -> dict:
    return scored_counts(
        {k: sum(s[k] for s in scores) for k in ("gold", "predicted", "matched", "correct_level")}
    )


def update_league(historical: dict) -> None:
    counts = aggregate(historical["scores"])
    row = {
        "method": KEY,
        "name": "OUR METHOD — confidence-filtered v2 (F0.5-selected)",
        "source_url": REMOTE + "outputs/structure-precision/report.md",
        "status": "completed",
        "documents_scored": 4,
        **counts,
        "heading_recall": counts["matched"] / counts["gold"],
        "correct_heading_and_level": counts["correct_level"] / counts["gold"],
        "false_headings": counts["predicted"] - counts["matched"],
        "native_prose_retention": None,
        "measured_seconds": sum(t["seconds"] for t in historical["timings"]),
        "processed_pages": 523,
    }
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


def result_row(label: str, score: dict) -> list:
    return [
        label,
        f"{score['joint_f05']:.1%}",
        f"{score['heading_precision']:.1%}",
        "PASS" if score["precision_gate_pass"] else "FAIL",
        f"{score['correct_level']}/{score['gold']}",
        score["predicted"] - score["matched"],
        score["gold"] - score["matched"],
        score["matched"] - score["correct_level"],
    ]


def main() -> None:
    evidence = OUT / "evidence"
    selection = read_json(evidence / "selection.json")
    regression = read_json(evidence / "regression.json")
    historical = read_json(evidence / "historical.json")
    old = next(
        r
        for r in read_json(REPO / "outputs/league_table.json")
        if r["method"] == "structure_context_relations"
    )
    rows = [result_row("Validation / selected", selection["selected"]["score"])]
    rows += [result_row("38-heading regression / " + name, s) for name, s in regression["results"].items()]
    rows += [
        result_row("77-heading historical / baseline", scored_counts(old)),
        result_row("77-heading historical / selected", aggregate(historical["scores"])),
    ]
    results = table(
        [
            "Dataset / configuration",
            "Joint F0.5",
            "Heading precision",
            "95% gate",
            "Correct + level",
            "Extra headings",
            "Missed titles",
            "Wrong levels",
        ],
        rows,
    )
    grid = table(
        ["Variant", "Body weight", "Min heading score", "Relation weight", "F0.5", "Precision", "Gate"],
        [
            [
                r["settings"]["variant"],
                r["settings"]["body_weight"],
                r["settings"]["min_heading_score"],
                r["settings"]["relation_weight"],
                f"{r['score']['joint_f05']:.1%}",
                f"{r['score']['heading_precision']:.1%}",
                "PASS" if r["score"]["precision_gate_pass"] else "FAIL",
            ]
            for r in selection["validation"]
        ],
    )
    markdown = (REPO / "docs/structure-precision.md").read_text()
    markdown = markdown.replace("__RESULTS__", results).replace("__GRID__", grid)
    markdown = markdown.replace("__METRIC__", (REPO / "docs/joint-metric.md").read_text())
    (OUT / "report.md").write_text(markdown)
    css = (REPO / "docs/report.css").read_text()
    html = MarkdownIt("commonmark").enable("table").render(markdown)
    (OUT / "index.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>Precision-constrained heading optimization</title><style>{css}</style></head>"
        f"<body><main>{html}</main></body></html>\n"
    )
    update_league(historical)


if __name__ == "__main__":
    main()
