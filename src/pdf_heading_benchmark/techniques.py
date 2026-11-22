"""Accessible, self-contained technique diagrams and their Markdown source appendix."""

from html import escape

from bs4 import BeautifulSoup

from pdf_heading_benchmark.io import REPO, read_json
from pdf_heading_benchmark.method_terms import explained_terms, linked_text
from pdf_heading_benchmark.prediction_comparison import (
    comparison_html,
    comparison_markdown,
    comparisons,
)
from pdf_heading_benchmark.report_help import column_help, info_button

REMOTE = "https://github.com/dividor/pdf-heading-benchmark/blob/main/"


def resources(row: dict, method: dict, technique: dict) -> list[dict]:
    links = [
        {"label": "Benchmark code", "url": method.get("code_url", REMOTE + method["code"])},
        *technique["sources"],
        {"label": "Configuration source / evidence", "url": row["source_url"]},
    ]
    seen = set()
    unique = []
    for link in links:
        if link["url"] not in seen:
            unique.append(link)
            seen.add(link["url"])
    return unique


def flow(stages: list[dict], label: str, technique: dict) -> str:
    cards = "".join(
        f'<li><span class="step-number" aria-hidden="true">{i:02}</span>'
        f"<strong>{linked_text(s['title'], technique)}</strong>"
        f"<p>{linked_text(s['detail'], technique)}</p></li>"
        for i, s in enumerate(stages, 1)
    )
    return f'<figure class="technique-flow"><figcaption>{escape(label)}</figcaption><ol>{cards}</ol></figure>'


def run_details(technique: dict) -> str:
    """Keep explicit run settings visible, including values that were not recorded."""
    rows = "".join(
        f'<tr><th scope="row">{escape(name)}</th><td>{escape(value)}</td></tr>'
        for name, value in technique["parameters"]
    )
    sections = "".join(
        f"<section><h3>{escape(section['title'])}</h3>"
        + "".join(f"<p>{linked_text(p, technique)}</p>" for p in section["paragraphs"])
        + "</section>"
        for section in technique["sections"]
    )
    return (
        '<div class="technique-details"><h3>Parameters used in this run</h3>'
        "<table><caption>Recorded settings; unrecorded defaults are identified explicitly.</caption>"
        f"<tbody>{rows}</tbody></table>{sections}</div>"
    )


def dialog(row: dict, method: dict, technique: dict, documents: list[dict]) -> str:
    key = escape(row["method"], quote=True)
    training = (
        flow(technique["training"], "01 · Training or setting selection", technique)
        if technique["training"]
        else ""
    )
    label = "02 · Processing a new document" if training else "How the measured run works"
    links = "".join(
        f'<a href="{escape(link["url"], quote=True)}" target="_blank" rel="noopener noreferrer">'
        f'{escape(link["label"])} <span aria-hidden="true">↗</span></a>'
        for link in resources(row, method, technique)
    )
    return (
        f'<dialog id="technique-{key}" aria-labelledby="title-{key}" class="technique-dialog">'
        '<div class="technique-shell"><header class="technique-header">'
        f'<div><p class="technique-family">{escape(technique["family"])}</p>'
        f'<h2 id="title-{key}" tabindex="-1">{escape(row["name"])}</h2></div>'
        '<button type="button" class="technique-close" aria-label="Close technique diagram">'
        'Close <span aria-hidden="true">&times;</span></button></header>'
        f'<p class="technique-description">{linked_text(technique["summary"], technique)}</p>'
        f"{comparison_html(documents)}{training}{flow(technique['stages'], label, technique)}"
        f"{explained_terms(technique)}{run_details(technique)}"
        '<aside class="technique-limit"><strong>Interpretation</strong>'
        f"<p>{escape(technique['limitation'])}</p>"
        '</aside><h3>Code and sources</h3><nav class="technique-links" aria-label="Technique resources">'
        f'{links}</nav><p class="technique-footnote">Diagrams describe this benchmark configuration. '
        "Source papers describe the underlying method, not a replication of this experiment."
        "</p></div></dialog>"
    )


def enhance_html(rendered: str, rows: list[dict], methods: dict) -> str:
    techniques = read_json(REPO / "configs/techniques.json")
    soup = BeautifulSoup(rendered, "html.parser")
    results = next(
        t
        for t in soup.find_all("table")
        if (header := t.find("th")) is not None and header.get_text() == "Configuration"
    )
    body = results.find("tbody")
    if body is None:
        raise ValueError("Missing configuration table body")
    results["class"] = "league-table"
    link_columns = [
        index
        for index, header in enumerate(results.find_all("th"))
        if header.get_text() in {"Configuration", "Method / code"}
    ]
    for tr, row in zip(body.find_all("tr"), rows, strict=True):
        for index in link_columns:
            cell = tr.find_all("td")[index]
            anchor = cell.find("a")
            if anchor is None:
                raise ValueError("Missing configuration or method link")
            if index == 0:
                label = anchor.get_text()
                anchor.unwrap()
                cell.append(" ")
                cell.append(info_button(soup, "technique-" + row["method"], label))
                continue
            anchor["data-technique"] = "technique-" + row["method"]
            anchor["aria-haspopup"] = "dialog"
            anchor["aria-controls"] = "technique-" + row["method"]
            anchor["title"] = "Open technique diagram and source links"
    hint = soup.new_tag("p", attrs={"class": "technique-hint"})
    hint.string = (
        "Select an i button beside a column heading for its definition, or beside a configuration "
        "for predicted versus reference headings, its diagram, exact parameters, tuning, code and sources."
    )
    results.insert_before(hint)
    help_panels = column_help(soup, results)
    audits = comparisons([r["method"] for r in rows])
    panels = "".join(
        dialog(r, methods[r["method"]], techniques[r["method"]], audits[r["method"]]) for r in rows
    )
    script = (REPO / "docs/techniques.js").read_text()
    return str(soup) + help_panels + panels + f"<script>{script}</script>"


def markdown_appendix(rows: list[dict], methods: dict) -> str:
    techniques = read_json(REPO / "configs/techniques.json")
    audits = comparisons([r["method"] for r in rows])
    parts = ["\n## Technique diagrams and sources\n", "The HTML report opens these diagrams in a modal.\n"]
    for row in rows:
        technique = techniques[row["method"]]
        parts += [f"\n### {row['name']}\n", f"{technique['family']}\n"]
        parts.append(technique["summary"] + "\n")
        parts.append(comparison_markdown(audits[row["method"]]))
        for label, stages in [("Training", technique["training"]), ("Inference", technique["stages"])]:
            if stages:
                parts.append(f"\n**{label}:** " + " → ".join(s["title"] for s in stages) + "\n")
                parts += [f"- **{s['title']}:** {s['detail']}" for s in stages]
                parts.append("\n")
        parts.append("\n**Models and terms explained**\n")
        parts += [
            f"- [{term['name']}]({term['url']}): {term['description']}" for term in technique.get("terms", [])
        ]
        parts += ["\n**Parameters used in this run**\n", "| Parameter | Recorded value |", "| --- | --- |"]
        parts += [
            f"| {name} | {escape(value, quote=False).replace('|', '&#124;')} |"
            for name, value in technique["parameters"]
        ]
        for section in technique["sections"]:
            parts.append(f"\n**{section['title']}**\n")
            parts.extend(p + "\n" for p in section["paragraphs"])
        parts.append(technique["limitation"] + "\n")
        parts.append(
            " · ".join(
                f"[{x['label']}]({x['url']})" for x in resources(row, methods[row["method"]], technique)
            )
            + "\n"
        )
    return "\n".join(parts)
