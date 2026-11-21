"""Regenerate Markdown and HTML from frozen supervised experiment evidence."""

from pathlib import Path

from markdown_it import MarkdownIt

from pdf_heading_benchmark.supervised_data import read_json

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "outputs/supervised/evidence"
GH = "https://github.com/dividor/pdf-heading-benchmark/blob/main/"


def score_row(name: str, scope: str, value: dict, fit: float) -> str:
    scores = [
        f"{100 * value[key]:.1f}%"
        for key in ("detection_precision", "detection_recall", "detection_f1", "exact_level_f1")
    ]
    groups = f"{value['complete_groups_correct_level']}/{value['heading_groups']}"
    return f"| {name} | {scope} | " + " | ".join(scores) + f" | {groups} | {fit:.3f}s |"


def results_section() -> str:
    selection = read_json(EVIDENCE / "selection.json")
    test = read_json(EVIDENCE / "test.json")
    runtime = read_json(EVIDENCE / "runtime.json")
    total = sum(r["total_seconds"] for r in runtime["documents"])
    rows = [
        "| Model | Scored set | Detection precision | Recall | Detection F1 | Exact-level F1 | "
        "Whole headings correct | Fit time |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for key, name in [("linear", "Logistic regression"), ("trees", "Extra Trees, 200 trees")]:
        result = selection["validation"][key]
        rows.append(score_row(name, "Validation", result, result["fit_seconds"]))
    rows.append(
        score_row(
            "Extra Trees, selected", "Held-out test", test, selection["validation"]["trees"]["fit_seconds"]
        )
    )
    rows.extend(
        [
            "",
            "Test evaluation was performed once. The linear model was not scored on test.",
            "",
            f"Actual full-document inference covered **1,524 pages in {total:.2f} seconds** "
            "on an Apple M4 Pro "
            "Mac mini (14 CPU cores, 48 GB RAM), CPU only. This sums extraction, feature calculation, "
            "classification and heading grouping, "
            "excluding interpreter/model loading and output-file writes. "
            f"That is **{total * 500 / 1524:.2f} seconds per 500 pages**, "
            "a throughput normalization, not a separately timed run. "
            f"Peak process RSS was {runtime['peak_rss_platform_units'] / 2**20:.1f} MiB. "
            f"The selected JSON model is {selection['validation']['trees']['model_bytes'] / 2**20:.2f} MiB.",
            "",
            "**Cost:** no metered API inference spend and no GPU. Electricity, hardware amortization and "
            "annotation labour were not measured, so total cost is not reported as zero. "
            "Assistant annotation "
            "was used to create the dataset; the preparation, training and deployed classifier run locally.",
        ]
    )
    return "\n".join(rows)


def corpus_section() -> str:
    records = read_json(ROOT / "configs/supervised/corpus.json")
    rows = [
        "| Split | Catalogue ID / row | Report (source PDF) | Year | Language | "
        "PDF pages | Reviewed PDF pages |",
        "|---|---|---|---:|---|---:|---|",
    ]
    for r in records:
        pages = ", ".join(map(str, r["review_pages"]))
        title = r["title"].replace("|", "\\|")
        rows.append(
            f"| {r['split']} | {r['id']} / {r['sheet_row']} | [{title}]({r['url']}) | "
            f"{r['year']} | {r['language']} | {r['pages']} | {pages} |"
        )
    return "\n".join(rows)


def main() -> None:
    template = (ROOT / "docs/supervised-experiment.md").read_text()
    content = template.replace("{{RESULTS}}", results_section()).replace("{{CORPUS}}", corpus_section())
    target = ROOT / "outputs/supervised"
    (target / "report.md").write_text(content)
    html = MarkdownIt("commonmark").enable("table").render(content)
    (target / "report.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" '
        'content="width=device-width,initial-scale=1"><title>Supervised WFP headings pilot</title>'
        "<style>body{font:17px/1.6 system-ui;max-width:1200px;margin:3rem auto;padding:0 2rem;color:#182838}"
        "table{border-collapse:collapse;font-size:14px;display:block;overflow:auto}"
        "td,th{padding:9px;border:1px solid #ccd5de;text-align:left}th{background:#e8f1fa}"
        "a{color:#0757a0}pre{background:#eef2f6;padding:1rem;overflow:auto}</style><body>"
        + html
        + "</body></html>\n"
    )


if __name__ == "__main__":
    main()
