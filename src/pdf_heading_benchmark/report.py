"""Deterministic HTML and Markdown reports from the frozen run summaries."""

from markdown_it import MarkdownIt

from pdf_heading_benchmark.io import REPO, read_json, write_json
from pdf_heading_benchmark.techniques import enhance_html, markdown_appendix

REMOTE = "https://github.com/dividor/pdf-heading-benchmark/blob/main/"
HEADERS = [
    "Configuration",
    "Method / code",
    "Status",
    "Primary score: correct heading + level",
    "Headings recovered",
    "False headings",
    "Native prose retention",
    "Measured time",
]


def percent(value):
    return "—" if value is None else f"{value:.1%}"


def duration(row):
    seconds = row["measured_seconds"]
    if not seconds:
        return "—"
    label = f"{seconds / 60:.1f} min" if seconds >= 60 else f"{seconds:.1f} s"
    scope = f"{row['processed_pages']} pages" if row["processed_pages"] else "hierarchy stage only"
    return f"{label} / {scope}"


def cells(row, method):
    completed = row["status"] == "completed"
    combined = percent(row["correct_heading_and_level"])
    recall = percent(row["heading_recall"])
    if completed:
        combined += f" ({row['correct_level']}/77)"
        recall += f" ({row['matched']}/77)"
    if row["method"] == "mineru_pro_mlx":
        combined = "Levels not supplied (0/77 complete outputs)"
    configuration = f"[{row['name']}]({row['source_url']})"
    if row["method"] == "supervised_extra_trees":
        configuration = f"[LLM annotations → Extra Trees v1 (CPU)]({row['source_url']})"
    if row["method"] == "structure_context_relations":
        configuration = (
            '<span id="our-trained-model"></span>'
            f"[**OUR METHOD — LLM annotations → grouped context model v2 (CPU)**]({row['source_url']})"
        )
    if row["method"] == "structure_calibrated":
        configuration = (
            '<span id="our-calibrated-model"></span>'
            f"[**OUR METHOD — calibrated decoding (experimental)**]({row['source_url']})"
        )
    return [
        configuration,
        f"[{method['description']}]({method.get('code_url', REMOTE + method['code'])})",
        row["status"],
        f"**{combined}**",
        recall,
        str(row["false_headings"]) if completed else "—",
        percent(row["native_prose_retention"]),
        duration(row),
    ]


def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines += ["| " + " | ".join(str(x).replace("|", "\\|") for x in row) + " |" for row in rows]
    return "\n".join(lines)


def corpus_table():
    corpus = read_json(REPO / "configs/corpus.json")
    audit = read_json(REPO / "configs/audit_pages.json")
    gold = read_json(REPO / "configs/gold.json")
    documents = [
        [
            f"[{r['title']}]({r['url']})",
            {"en": "English", "es": "Spanish"}[r["language"]],
            r["pages"],
            ", ".join(str(page) for page in audit[r["id"]]),
            len(gold[r["id"]]),
        ]
        for r in corpus
    ]
    return table(
        ["WFP report / official PDF", "Language", "PDF pages", "Audited PDF pages", "Reference headings"],
        documents,
    )


def report_rows(filename):
    selected = set(read_json(REPO / "configs/report-methods.json"))
    return [
        {key: value for key, value in row.items() if not key.startswith("api_")}
        for row in read_json(REPO / "outputs" / filename)
        if row["method"] in selected
    ]


def results_table():
    rows = report_rows("league_table.json")
    methods = read_json(REPO / "configs/methods.json")
    return table(HEADERS, [cells(row, methods[row["method"]]) for row in rows])


def build_report():
    methods = read_json(REPO / "configs/methods.json")
    intro = (REPO / "docs/report-introduction.md").read_text()
    notes = (REPO / "docs/report-notes.md").read_text()
    protocol = (REPO / "docs/report-protocol.md").read_text()
    details = report_rows("league_details.json")
    per_report = [
        [
            methods[r["method"]]["code"].split("/")[-1] + " / " + r["method"],
            r["document"],
            f"{r['matched']}/{r['gold']}",
            f"{r['correct_level']}/{r['gold']}",
            r["predicted"] - r["matched"],
        ]
        for r in details
    ]
    markdown = intro + "\n" + corpus_table() + "\n\n" + protocol
    markdown += "\n" + results_table() + "\n\n" + notes
    markdown += "\n\n## Results by report\n\n" + table(
        ["Runner / configuration", "Report", "Recovered", "Correct heading + level", "False headings"],
        per_report,
    )
    markdown += "\n"
    output = REPO / "outputs/report"
    output.mkdir(exist_ok=True)
    write_json(output / "results.json", report_rows("league_table.json"))
    summary_keys = ("method", "document", "gold", "matched", "correct_level", "predicted")
    write_json(output / "details.json", [{key: row[key] for key in summary_keys} for row in details])
    rows = report_rows("league_table.json")
    (output / "league_table.md").write_text(markdown + markdown_appendix(rows, methods))
    rendered = MarkdownIt("commonmark").enable("table").render(markdown)
    rendered = enhance_html(rendered, rows, methods)
    css = (REPO / "docs/report.css").read_text()
    html = (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>On-premises PDF heading benchmark: scores, timings and methods</title><style>"
        + css
        + "</style></head>"
        "<body><main>" + rendered + "</main></body></html>\n"
    )
    (output / "index.html").write_text(html)
