"""Organize the standalone report into accessible, deep-linkable tabs."""

from bs4 import BeautifulSoup, Tag

from pdf_heading_benchmark.io import REPO

TABS = (
    ("results", "Results"),
    ("field", "The OCR field"),
    ("methods", "Methods & scoring"),
    ("documents", "Documents"),
    ("evidence", "Timing & evidence"),
)
SECTIONS = {
    "Results at a glance": "results",
    "Full configuration results": "results",
    "Published comparison": "field",
    "Documents and their sources": "documents",
    "How the experiment works": "methods",
    "Primary metric: heading-and-level F0.5": "methods",
    "How to read the table": "evidence",
    "Sequential GPU reruns": "evidence",
    "GPU and memory observations": "evidence",
    "Results by report": "evidence",
}


def tab_shell(soup):
    """Leave all sections readable if JavaScript is disabled."""
    nav = soup.new_tag("nav", attrs={"class": "report-tabs", "aria-label": "Report sections"})
    nav["hidden"] = ""
    nav["role"] = "tablist"
    panels = {}
    for key, label in TABS:
        button = soup.new_tag("button", attrs={"type": "button", "role": "tab", "id": f"tab-{key}"})
        button["aria-controls"] = f"panel-{key}"
        button.string = label
        nav.append(button)
        panels[key] = soup.new_tag("section", attrs={"class": "report-panel", "id": f"panel-{key}"})
        panels[key]["aria-labelledby"] = f"tab-{key}"
    return nav, panels


def compact_tables(soup):
    """Keep diagnostics available without letting them dominate the main table."""
    table = soup.find("table")
    if table is None:
        raise ValueError("Report has no results table")
    controls = BeautifulSoup(
        '<div class="table-controls"><label><input type="checkbox" id="show-diagnostics"> '
        "Show diagnostic columns (status, heading detection, prose)</label></div>",
        "html.parser",
    )
    table.insert_before(controls)
    for item in soup.find_all("table"):
        wrapper = soup.new_tag("div", attrs={"class": "report-table-scroll", "tabindex": "0"})
        wrapper["role"] = "region"
        wrapper["aria-label"] = "Scrollable data table"
        item.wrap(wrapper)


def fold_evidence(soup, panel):
    """Make large evidence sections available on demand."""
    anchor = panel.find(id="sequential-gpu-reruns")
    heading = panel.find("h2", string="Sequential GPU reruns")
    if anchor is not None and heading is not None:
        anchor.decompose()
        heading["id"] = "sequential-gpu-reruns"
    current = None
    for node in list(panel.contents):
        if isinstance(node, Tag) and node.name == "h2":
            current = soup.new_tag("details", attrs={"class": "evidence-section"})
            summary = soup.new_tag("summary")
            summary.string = node.get_text()
            if node.get("id"):
                current["id"] = node["id"]
            current.append(summary)
            node.replace_with(current)
        elif current is not None:
            current.append(node.extract())


def tabbed_report(rendered: str) -> str:
    soup = BeautifulSoup(rendered, "html.parser")
    nav, panels = tab_shell(soup)
    current = None
    for node in list(soup.contents):
        if isinstance(node, Tag) and node.name == "h2":
            current = panels[SECTIONS[node.get_text()]]
        if current is not None:
            current.append(node.extract())
    soup.append(nav)
    for panel in panels.values():
        soup.append(panel)
    compact_tables(soup)
    fold_evidence(soup, panels["evidence"])
    script = soup.new_tag("script")
    script.string = (REPO / "docs/report-tabs.js").read_text()
    soup.append(script)
    return str(soup)
