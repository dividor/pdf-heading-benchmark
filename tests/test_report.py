"""The complete report must stay deterministic and its code links must resolve locally."""

from html import escape

from bs4 import BeautifulSoup

from pdf_heading_benchmark.io import REPO, read_json
from pdf_heading_benchmark.report import build_report


def test_report_is_reproducible_and_has_all_method_links():
    paths = [REPO / "outputs/report" / name for name in ("index.html", "league_table.md")]
    before = [p.read_bytes() for p in paths]
    build_report()
    assert [p.read_bytes() for p in paths] == before
    soup = BeautifulSoup(paths[0].read_text(), "html.parser")
    tables = soup.find_all("table")
    corpus_rows = tables[0].find("tbody").find_all("tr")
    corpus = read_json(REPO / "configs/corpus.json")
    assert [row.find("a")["href"] for row in corpus_rows] == [doc["url"] for doc in corpus]
    results = next(t for t in tables if t.find("th").get_text() == "Configuration")
    rows = results.find("tbody").find_all("tr")
    assert len(rows) == 21
    for row in rows:
        assert len(row.find_all("td")) == 8
        assert (
            row.find_all("td")[1]
            .find("a")["href"]
            .startswith("https://github.com/dividor/pdf-heading-benchmark/blob/")
        )
    for method in read_json(REPO / "configs/methods.json").values():
        for step in method["steps"]:
            assert (REPO / step["script"]).is_file()


def test_report_contains_only_on_premises_methods():
    selected = set(read_json(REPO / "configs/report-methods.json"))
    assert len(selected) == 21
    for filename in ("results.json", "details.json"):
        rows = read_json(REPO / "outputs/report" / filename)
        assert {row["method"] for row in rows} == selected
    report = (REPO / "outputs/report/league_table.md").read_text()
    for excluded in ("Azure", "Mistral", "azure_layout", "mistral_ocr41", "API USD"):
        assert excluded not in report


def test_every_configuration_has_an_accessible_diagram_and_markdown_sources():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    configs = read_json(REPO / "configs/report-methods.json")
    assert len(soup.select("a[data-technique]")) == 2 * len(configs)
    assert len(soup.find_all("dialog")) == len(configs)
    identifiers = [element["id"] for element in soup.select("[id]")]
    assert len(identifiers) == len(set(identifiers))
    markdown = (REPO / "outputs/report/league_table.md").read_text()
    for key in configs:
        panel = soup.find("dialog", id="technique-" + key)
        assert panel.find(id=panel["aria-labelledby"])
        assert panel.select_one('button[aria-label="Close technique diagram"]')
        assert len(panel.select(".technique-flow li")) >= 4
        for link in panel.select(".technique-links a"):
            assert link["href"].startswith("https://")
            assert link["href"] in markdown
            assert "noopener" in link["rel"]
        for link in soup.select(f'a[data-technique="technique-{key}"]'):
            assert link["aria-controls"] == panel["id"]
            assert link["aria-haspopup"] == "dialog"
            assert link["href"].startswith("https://")


def test_every_method_exposes_its_run_settings_in_both_formats():
    techniques = read_json(REPO / "configs/techniques.json")
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    markdown = (REPO / "outputs/report/league_table.md").read_text()
    diagrams = []
    for key in read_json(REPO / "configs/report-methods.json"):
        technique = techniques[key]
        panel = soup.find("dialog", id="technique-" + key)
        settings = panel.select(".technique-details tr")
        assert len(settings) == len(technique["parameters"])
        for row, (name, value) in zip(settings, technique["parameters"], strict=True):
            assert row.find("th", scope="row").get_text() == name
            assert row.find("td").get_text() == value
            assert escape(value, quote=False).replace("|", "&#124;") in markdown
        for section in technique["sections"]:
            for paragraph in section["paragraphs"]:
                assert paragraph in panel.get_text()
                assert paragraph in markdown
        diagrams.append(tuple((s["title"], s["detail"]) for s in technique["stages"]))
    assert len(set(diagrams)) == len(diagrams)
