"""Filter the field chart and open source-backed details for every model."""

from html import escape

from bs4 import BeautifulSoup

from pdf_heading_benchmark.field_charts import category, eligible_rows, plot_svg
from pdf_heading_benchmark.io import REPO, read_json


def model_dialog(row: dict, detail: dict, index: int, data: dict) -> str:
    source_root = f"https://github.com/datalab-to/omni_parse_bench/blob/{data['revision']}"
    links = [
        (
            "Benchmark adapter code",
            f"{source_root}/omni_parse_bench/harness/providers/{detail['provider']}.py",
        ),
        ("Run notes", f"{source_root}/docs/providers.md"),
        ("Published scores", data["source"]),
    ]
    if detail["model_url"]:
        links.insert(0, ("Model on Hugging Face", detail["model_url"]))
    study = "This configuration has not been tested in our WFP study."
    if detail["study_method"]:
        technique = read_json(REPO / "configs/techniques.json")[detail["study_method"]]
        study = "We tested this model or tool on WFP reports with different settings. " + technique["summary"]
        links.extend(
            ("Our study: " + item["label"], item["url"])
            for item in technique["sources"]
            if "/scripts/" in item["url"]
        )
    notes = []
    if row["retry"]:
        notes.append(
            "† This result includes a rerun of failed pages; other systems did not receive that second pass."
        )
    if row["annotation_contributor"]:
        notes.append("* This model helped create or verify benchmark tests.")
    if row["benchmark_vendor"]:
        notes.append("Datalab develops this system and the benchmark.")
    settings = "".join(f"<dt>{escape(k)}</dt><dd>{escape(v)}</dd>" for k, v in detail["settings"].items())
    sources = " · ".join(
        f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener">{escape(label)}</a>'
        for label, url in links
    )
    return (
        f'<dialog class="field-model-dialog" id="field-model-{index}" aria-labelledby="field-title-{index}">'
        '<div class="field-dialog-head"><span>Model details</span>'
        '<button type="button" class="field-dialog-close" '
        'aria-label="Close model details">Close &#215;</button></div>'
        f'<h2 id="field-title-{index}">{escape(row["name"])}</h2>'
        f'<p class="field-scoreline">Text <strong>{row["text"]:.1f}</strong> · '
        f"Layout <strong>{row['layout']:.1f}</strong> / 100</p>"
        f"<p>{escape(detail['description'])}</p>"
        "<h3>Published pipeline and adapter settings</h3>"
        f'<dl>{settings}</dl><p class="field-hint">Settings describe the pinned benchmark adapter '
        "and documented run. "
        "They are not a new run in this study.</p>"
        f"<h3>In our study</h3><p>{escape(study)}</p>"
        f'<p class="field-hint">{escape(" ".join(notes))}</p>'
        f'<div class="field-sources">{sources}</div></dialog>'
    )


def explorer(data: dict) -> str:
    rows = eligible_rows(data)
    details = read_json(REPO / "configs/field-model-details.json")
    options = "".join(
        f'<option value="{i}" data-category="{category(row, details[row["name"]])}">'
        f"{escape(row['name'])}</option>"
        for i, row in sorted(enumerate(rows), key=lambda item: item[1]["name"].casefold())
    )
    counts = {
        key: sum(category(row, details[row["name"]]) == key for row in rows)
        for key in ("study", "local", "hosted")
    }
    data_rows = "".join(
        f'<tr><td><button class="field-table-link" data-open-model="{i}">{escape(row["name"])}</button></td>'
        f"<td>{row['text']:.1f}</td><td>{row['layout']:.1f}</td></tr>"
        for i, row in sorted(enumerate(rows), key=lambda item: -item[1]["text"])
    )
    dialogs = "".join(model_dialog(row, details[row["name"]], i, data) for i, row in enumerate(rows))
    return (
        '<section id="field-explorer" aria-label="Explore the OCR field">'
        '<div class="field-controls"><label>Show <select id="field-filter">'
        f'<option value="all">All {len(rows)} systems</option>'
        f'<option value="study">Tested in our study ({counts["study"]})</option>'
        f'<option value="hosted">Hosted APIs &amp; services ({counts["hosted"]})</option>'
        f'<option value="local">Other open models &amp; tools ({counts["local"]})</option></select></label>'
        f'<label>Find a model <select id="field-system">{options}</select></label>'
        '<button id="field-open-model" type="button">Model details ⓘ</button></div>'
        '<div class="field-legend"><span class="field-study">● Tested in our WFP study</span>'
        '<span class="field-local">● Other open models &amp; tools</span>'
        '<span class="field-hosted">■ Hosted APIs &amp; services</span></div>'
        '<p id="field-count"></p><div class="field-plot-scroll" tabindex="0" '
        'aria-label="Chart; scroll horizontally on a phone">'
        + plot_svg(data)
        + '</div><p class="field-hint">Click a model name or marker for details. '
        "On a phone, scroll the chart or use Find a model. "
        "Colors identify models and tools; benchmark settings differ from our study.</p>"
        '<details class="field-values"><summary>View the plotted scores</summary>'
        '<div class="report-table-scroll" tabindex="0"><table><thead><tr><th>System</th>'
        "<th>Text</th><th>Layout</th></tr></thead>"
        f"<tbody>{data_rows}</tbody></table></div></details>{dialogs}</section>"
    )


def enhance_field(rendered: str, data: dict) -> str:
    soup = BeautifulSoup(rendered, "html.parser")
    image = soup.find("img", src="ocr-text-layout.png")
    if image is None:
        raise ValueError("Field chart paragraph placeholder is missing from the report")
    parent = image.find_parent("p")
    if parent is None:
        raise ValueError("Field chart paragraph placeholder is missing from the report")
    parent.replace_with(BeautifulSoup(explorer(data), "html.parser"))
    style = soup.new_tag("style")
    style.string = (REPO / "docs/field-explorer.css").read_text()
    soup.append(style)
    script = soup.new_tag("script")
    script.string = (REPO / "docs/field-explorer.js").read_text()
    soup.append(script)
    return str(soup)
