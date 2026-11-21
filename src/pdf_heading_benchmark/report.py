"""Deterministic HTML and Markdown reports from the frozen run summaries."""

from markdown_it import MarkdownIt

from pdf_heading_benchmark.io import REPO, read_json

REMOTE = "https://github.com/dividor/pdf-heading-benchmark/blob/main/"
HEADERS = [
    "Configuration",
    "Method / code",
    "Status",
    "Headings recovered",
    "Correct heading + level",
    "False headings",
    "Native prose retention",
    "API USD / 1,000 pages",
    "API USD / 523 pages",
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
    estimate = " estimate" if row["method"] == "azure_layout" else ""
    return [
        f"[{row['name']}]({row['source_url']})",
        f"[{method['description']}]({REMOTE}{method['code']})",
        row["status"],
        recall,
        combined,
        str(row["false_headings"]) if completed else "—",
        percent(row["native_prose_retention"]),
        f"${row['api_usd_per_1000_pages']:.2f}{estimate}",
        f"${row['api_usd_for_523_pages']:.2f}",
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


def results_table():
    rows = read_json(REPO / "outputs/league_table.json")
    methods = read_json(REPO / "configs/methods.json")
    return table(HEADERS, [cells(row, methods[row["method"]]) for row in rows])


def build_report():
    methods = read_json(REPO / "configs/methods.json")
    intro = (REPO / "docs/report-introduction.md").read_text()
    notes = (REPO / "docs/report-notes.md").read_text()
    protocol = (REPO / "docs/report-protocol.md").read_text()
    details = read_json(REPO / "outputs/league_details.json")
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
    (output / "league_table.md").write_text(markdown)
    rendered = MarkdownIt("commonmark").enable("table").render(markdown)
    css = (REPO / "docs/report.css").read_text()
    html = (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>PDF heading benchmark: scores, costs and methods</title><style>" + css + "</style></head>"
        "<body><main>" + rendered + "</main></body></html>\n"
    )
    (output / "index.html").write_text(html)
