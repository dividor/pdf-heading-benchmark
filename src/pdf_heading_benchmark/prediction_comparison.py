"""Show every scored prediction beside the frozen reference using the actual scorer."""

from html import escape

from pdf_heading_benchmark.evaluation import evaluate
from pdf_heading_benchmark.io import REPO, read_json

LABELS = {
    "correct": "Correct heading + level",
    "wrong": "Wrong or absent level",
    "missing": "Missed heading",
    "extra": "Extra prediction",
}


def comparisons(methods: list[str]) -> dict:
    gold = read_json(REPO / "configs/gold.json")
    pages = read_json(REPO / "configs/audit_pages.json")
    predictions = read_json(REPO / "outputs/audit_predictions.json")
    corpus = read_json(REPO / "configs/corpus.json")
    return {
        method: [
            dict(
                document=doc,
                audit=evaluate(gold[doc["id"]], predictions[method][doc["id"]], pages[doc["id"]]),
            )
            for doc in corpus
        ]
        for method in methods
    }


def comparison_rows(audit: dict) -> list[dict]:
    rows = [
        dict(
            reference=pair["reference"],
            prediction=pair["prediction"],
            status=("correct" if pair["reference"]["level"] == pair["prediction"]["level"] else "wrong"),
        )
        for pair in audit["matches"]
    ]
    rows += [dict(reference=h, prediction=None, status="missing") for h in audit["missing"]]
    rows += [dict(reference=None, prediction=h, status="extra") for h in audit["extras"]]
    return sorted(rows, key=lambda r: (r["reference"] or r["prediction"])["page"])


def counts(audits: list[dict]) -> str:
    correct = sum(a["correct_level"] for a in audits)
    wrong = sum(a["matched"] - a["correct_level"] for a in audits)
    missing = sum(len(a["missing"]) for a in audits)
    extra = sum(len(a["extras"]) for a in audits)
    return f"{correct} correct · {wrong} wrong/absent level · {missing} missed · {extra} extra"


def heading_text(heading: dict | None) -> str:
    if heading is None:
        return "—"
    level = "Level not supplied" if heading["level"] is None else f"H{heading['level']}"
    return f"{level} — {heading['title']}"


def html_rows(audit: dict) -> str:
    return "".join(
        f'<tr class="comparison-{row["status"]}">'
        f"<td>{(row['reference'] or row['prediction'])['page']}</td>"
        f"<td>{escape(heading_text(row['reference']))}</td>"
        f"<td>{escape(heading_text(row['prediction']))}</td>"
        f"<td>{LABELS[row['status']]}</td></tr>"
        for row in comparison_rows(audit)
    )


def comparison_html(documents: list[dict]) -> str:
    sections = []
    for item in documents:
        doc, audit = item["document"], item["audit"]
        sections.append(
            '<details class="comparison-document"><summary>'
            f"{escape(doc['title'])}<span>{counts([audit])}</span></summary>"
            f'<p><a href="{escape(doc["url"], quote=True)}" target="_blank" '
            'rel="noopener noreferrer">Source PDF</a> · One-based physical PDF pages.</p>'
            '<div class="comparison-scroll"><table><caption>Every reference heading and prediction '
            'on the audit pages; ordered by page.</caption><thead><tr><th scope="col">Page</th>'
            '<th scope="col">Reference heading and level</th>'
            '<th scope="col">Predicted heading and level</th><th scope="col">Result</th>'
            f"</tr></thead><tbody>{html_rows(audit)}</tbody></table></div></details>"
        )
    return (
        '<details class="prediction-comparison"><summary>Predictions versus reference</summary>'
        f'<p class="comparison-counts">{counts([d["audit"] for d in documents])}</p>'
        "<p>Choose a report to inspect every scored heading. Page numbers count from the PDF cover.</p>"
        + "".join(sections)
        + "</details>"
    )


def comparison_markdown(documents: list[dict]) -> str:
    lines = [
        "\n**Predicted headings versus reference (all scored pages)**\n",
        counts([d["audit"] for d in documents]) + "\n",
        "Frozen assistant references; not independently human-verified. Same scorer as the table; "
        "one-to-one same-page title similarity ≥90%, exact H level. Physical PDF pages.\n",
    ]
    for item in documents:
        doc, audit = item["document"], item["audit"]
        lines += [
            f"\n**[{doc['title']}]({doc['url']})**\n",
            counts([audit]) + "\n",
            "| Page | Reference heading and level | Predicted heading and level | Result |",
            "| --- | --- | --- | --- |",
        ]
        for row in comparison_rows(audit):
            page = (row["reference"] or row["prediction"])["page"]
            reference = escape(heading_text(row["reference"])).replace("|", "&#124;").replace("\n", " ")
            prediction = escape(heading_text(row["prediction"])).replace("|", "&#124;").replace("\n", " ")
            lines.append(f"| {page} | {reference} | {prediction} | {LABELS[row['status']]} |")
    return "\n".join(lines) + "\n"
