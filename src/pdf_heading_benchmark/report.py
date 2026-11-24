"""Deterministic HTML and Markdown reports from the frozen run summaries."""

from markdown_it import MarkdownIt

from pdf_heading_benchmark.io import REPO, read_json, write_json
from pdf_heading_benchmark.joint_metrics import scored_counts
from pdf_heading_benchmark.techniques import enhance_html, markdown_appendix
from pdf_heading_benchmark.timing_format import readable_time
from pdf_heading_benchmark.timing_updates import latest_timings

REMOTE = "https://github.com/dividor/pdf-heading-benchmark/blob/main/"
HEADERS = [
    "Configuration",
    "Primary score: joint F0.5",
    "Joint precision",
    "Joint recall",
    "Method / code",
    "Status",
    "Headings recovered",
    "False headings",
    "Native prose retention",
    "Time per page",
    "Time for 32 pages",
]


def percent(value):
    return "—" if value is None else f"{value:.1%}"


def duration(row):
    seconds, pages = row["measured_seconds"], row["processed_pages"]
    if seconds is None:
        return "—"
    if not pages:
        return f"Page average unavailable<br>{readable_time(seconds)} for the hierarchy stage"
    source = ""
    if row.get("timing_source"):
        source = (
            "<br>Latest sequential run"
            if row["timing_source"] == "sequential rerun"
            else "<br>Original run; see timing comparison"
        )
    return f"**{readable_time(seconds / pages)}**{source}"


def time_for_32_pages(row):
    seconds, pages = row["measured_seconds"], row["processed_pages"]
    if seconds is None or not pages:
        return "Unavailable"
    if pages == 32:
        return f"**{readable_time(seconds)}**<br>Measured"
    return (
        f"**{readable_time(seconds / pages * 32)}**<br>Estimated from "
        f"{readable_time(seconds)} measured over {pages} pages"
    )


def cells(row, method):
    completed = row["status"] == "completed"
    precision = percent(row.get("joint_precision"))
    recall = percent(row.get("joint_recall"))
    recovered = percent(row["heading_recall"])
    if completed:
        precision += f" ({row['correct_level']}/{row['predicted']})"
        recall += f" ({row['correct_level']}/{row['gold']})"
        recovered += f" ({row['matched']}/{row['gold']})"
    configuration = f"[{row['name']}]({row['source_url']})"
    if row["method"] == "supervised_extra_trees":
        configuration = f"[LLM annotations → Extra Trees v1 (CPU)]({row['source_url']})"
    if row["method"] == "structure_context_relations":
        configuration = (
            '<span id="our-original-model"></span>'
            f"[OUR METHOD — grouped context v2 (previous selection)]({row['source_url']})"
        )
    if row["method"] == "structure_precision":
        configuration = (
            '<span id="our-trained-model"></span>'
            f"[**OUR METHOD — confidence-filtered v2 (F0.5-selected)**]({row['source_url']})"
        )
    if row["method"] == "structure_calibrated":
        configuration = (
            '<span id="our-calibrated-model"></span>'
            f"[**OUR METHOD — calibrated decoding (experimental)**]({row['source_url']})"
        )
    return [
        configuration,
        f"**{percent(row.get('joint_f05'))}**",
        precision,
        recall,
        f"[{method['description']}]({method.get('code_url', REMOTE + method['code'])})",
        row["status"],
        recovered,
        str(row["false_headings"]) if completed else "—",
        percent(row["native_prose_retention"]),
        duration(row),
        time_for_32_pages(row),
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
    rows = [
        {key: value for key, value in row.items() if not key.startswith("api_")}
        for row in read_json(REPO / "outputs" / filename)
        if row["method"] in selected
    ]
    if filename == "league_table.json":
        rows = [scored_counts(row) if row["status"] == "completed" else row for row in rows]
        rows = latest_timings(rows)
        rows.sort(key=lambda row: row.get("joint_f05", -1), reverse=True)
    return rows


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
            percent(r["matched"] / r["predicted"] if r["predicted"] else 0),
        ]
        for r in details
    ]
    markdown = intro + "\n" + corpus_table() + "\n\n" + protocol
    metric = (REPO / "docs/joint-metric.md").read_text()
    markdown += "\n" + results_table() + "\n\n" + metric + "\n\n" + notes
    repeat = REPO / "outputs/sequential-repeat/summary.md"
    if repeat.exists():
        markdown += "\n\n" + repeat.read_text()
    markdown += "\n\n" + (REPO / "docs/published-comparison.md").read_text()
    markdown += "\n\n## Results by report\n\n" + table(
        [
            "Runner / configuration",
            "Report",
            "Recovered",
            "Correct heading + level",
            "False headings",
            "Heading-only precision (diagnostic)",
        ],
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
    diagram = "ocr-field-overview.png"
    (output / diagram).write_bytes((REPO / "docs/images" / diagram).read_bytes())
    rendered = rendered.replace(f"../../docs/images/{diagram}", diagram)
    rendered = rendered.replace(
        "<h2>Published comparison</h2>", '<h2 id="published-comparison">Published comparison</h2>'
    )
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
