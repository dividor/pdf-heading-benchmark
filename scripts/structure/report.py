"""Regenerate v2 HTML/Markdown and its three diagnostic league rows from frozen evidence."""

from collections import Counter

from markdown_it import MarkdownIt

from pdf_heading_benchmark.io import REPO, read_json, write_json
from pdf_heading_benchmark.report import build_report, table

OUT = REPO / "outputs/structure-v2"
REMOTE = "https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/"
NAMES = {
    "original_v1": "Original model v1",
    "expanded_line": "v2: more annotations",
    "learned_groups": "v2: learned grouping",
    "context_relations": "v2: context + relationships (selected)",
}
COMPONENTS = {
    "expanded_line": ["line"],
    "learned_groups": ["join", "group"],
    "context_relations": ["join", "context", "relation"],
}


def update_league(historical: dict) -> None:
    identifiers = {"structure_" + key for key in historical}
    rows = [r for r in read_json(REPO / "outputs/league_table.json") if r["method"] not in identifiers]
    details = [r for r in read_json(REPO / "outputs/league_details.json") if r["method"] not in identifiers]
    for variant, result in historical.items():
        scores = result["scores"]
        counts = {k: sum(s[k] for s in scores) for k in ["gold", "predicted", "matched", "correct_level"]}
        rows.append(
            {
                "method": "structure_" + variant,
                "name": NAMES[variant],
                "source_url": REMOTE + "outputs/structure-v2/report.md",
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
        )
        details.extend(scores)
    rows.sort(
        key=lambda r: r["correct_heading_and_level"] if r["correct_heading_and_level"] is not None else -1,
        reverse=True,
    )
    write_json(REPO / "outputs/league_table.json", rows)
    write_json(REPO / "outputs/league_details.json", details)


def summary_tables(selection: dict, test: dict, historical: dict) -> dict:
    rows = []
    for variant, result in test["variants"].items():
        val = selection["validation"].get(variant)
        rows.append(
            [
                NAMES[variant],
                f"{val['group_level_f1']:.1%}" if val else "Not used for v2 selection",
                f"{result['group_level_f1']:.1%}",
                f"{result['matched']}/{result['gold']}",
                f"{result['correct']}/{result['gold']}",
                result["predicted"] - result["matched"],
            ]
        )
    result_tables = {
        "RESULTS": table(
            [
                "Variant",
                "Validation exact F1",
                "Fresh test exact F1",
                "Groups recovered",
                "Groups + levels correct",
                "Extra groups",
            ],
            rows,
        )
    }
    per_doc = []
    chosen = test["variants"][selection["selected"]]["per_document"]
    original = test["variants"]["original_v1"]["per_document"]
    for key, result in chosen.items():
        per_doc.append(
            [
                key,
                f"{original[key]['group_level_f1']:.1%}",
                f"{result['group_level_f1']:.1%}",
                f"{result['correct']}/{result['gold']}",
                result["predicted"] - result["matched"],
            ]
        )
    result_tables["PER_DOCUMENT"] = table(
        ["Fresh report ID", "v1 exact F1", "Selected v2 exact F1", "Correct groups + levels", "Extra groups"],
        per_doc,
    )
    diagnostics, costs = [], []
    for variant, result in historical.items():
        scores = result["scores"]
        diagnostics.append(
            [
                NAMES[variant],
                f"{sum(s['matched'] for s in scores)}/77",
                f"{sum(s['correct_level'] for s in scores)}/77",
                sum(s["predicted"] - s["matched"] for s in scores),
            ]
        )
        seconds = sum(t["seconds"] for t in result["timings"])
        components = COMPONENTS[variant]
        costs.append(
            [
                NAMES[variant],
                f"{sum(selection['fit_seconds'][k] for k in components):.2f} s",
                f"{sum(selection['model_bytes'][k] for k in components) / 2**20:.1f} MiB",
                f"{seconds:.2f} s",
                f"{seconds * 500 / 523:.2f} s",
            ]
        )
    result_tables["HISTORICAL"] = table(
        ["Variant", "Titles recovered", "Correct title + level", "Extra headings"], diagnostics
    )
    result_tables["COSTS"] = table(
        [
            "Variant",
            "Component model fits",
            "Deployment JSON",
            "Measured / 523 pages",
            "Normalized / 500 pages",
        ],
        costs,
    )
    return result_tables


def corpus_table() -> str:
    annotations = read_json(REPO / "configs/structure-v2/annotations.json")
    counts = Counter(a["report_id"] for a in annotations)
    rows = [
        [
            r["id"],
            f"[{r['title']}]({r['url']})",
            r["language"],
            r["split"],
            r["pages"],
            ", ".join(map(str, r["review_pages"])) or "None: positive-only additions",
            counts[r["id"]],
        ]
        for r in read_json(REPO / "configs/structure-v2/corpus.json")
    ]
    return table(
        ["ID", "Report / public source", "Language", "Split", "PDF pages", "Full pages", "Groups"], rows
    )


def main() -> None:
    selection = read_json(OUT / "evidence/selection.json")
    test = read_json(OUT / "evidence/test.json")
    historical = read_json(OUT / "evidence/historical.json")
    markdown = (REPO / "docs/structure-v2.md").read_text()
    for key, value in (summary_tables(selection, test, historical) | {"CORPUS": corpus_table()}).items():
        markdown = markdown.replace("__" + key + "__", value)
    (OUT / "report.md").write_text(markdown)
    rendered = MarkdownIt("commonmark").enable("table").render(markdown)
    css = (REPO / "docs/report.css").read_text()
    (OUT / "index.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>Local heading model v2: controlled experiment</title>"
        f"<style>{css}img{{max-width:100%}}</style></head><body><main>" + rendered + "</main></body></html>\n"
    )
    update_league(historical)
    build_report()


if __name__ == "__main__":
    main()
