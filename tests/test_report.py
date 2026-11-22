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
    results = soup.select_one("table.league-table")
    assert results.find_all("th")[1].contents[0].strip() == "Primary score: joint F0.5"
    scores = read_json(REPO / "outputs/report/results.json")
    combined_scores = [r["joint_f05"] for r in scores]
    assert combined_scores == sorted(combined_scores, reverse=True)
    rows = results.find("tbody").find_all("tr")
    assert len(rows) == len(read_json(REPO / "configs/report-methods.json"))
    for row in rows:
        assert len(row.find_all("td")) == 10
        assert (
            row.find_all("td")[3]
            .find("a")["href"]
            .startswith("https://github.com/dividor/pdf-heading-benchmark/blob/")
        )
    for method in read_json(REPO / "configs/methods.json").values():
        for step in method["steps"]:
            assert (REPO / step["script"]).is_file()


def test_report_contains_only_on_premises_methods():
    selected = set(read_json(REPO / "configs/report-methods.json"))
    assert len(selected) >= 21
    for filename in ("results.json", "details.json"):
        rows = read_json(REPO / "outputs/report" / filename)
        assert {row["method"] for row in rows} == selected
    report = (REPO / "outputs/report/league_table.md").read_text()
    for excluded in ("Azure", "Mistral", "azure_layout", "mistral_ocr41", "API USD"):
        assert excluded not in report


def test_every_configuration_has_an_accessible_diagram_and_markdown_sources():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    configs = read_json(REPO / "configs/report-methods.json")
    assert len(soup.select("a[data-technique]")) == len(configs)
    assert len(soup.select("dialog:not(.column-dialog)")) == len(configs)
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


def test_information_buttons_resolve_to_named_dialogs():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    table = soup.select_one("table.league-table")
    assert len(table.select("th button.info-button")) == 10
    for row in table.select("tbody tr"):
        name_cell = row.find("td")
        assert name_cell.find("a") is None
        assert name_cell.select_one("button.info-button")
    for button in table.select("button.info-button"):
        panel = soup.find("dialog", id=button["aria-controls"])
        assert panel is not None
        assert panel.find(id=panel["aria-labelledby"])
        assert button["type"] == "button"
        assert button["aria-haspopup"] == "dialog"
        assert button["aria-label"].startswith("About ")
    score_help = soup.find("dialog", id="column-help-1")
    assert "1.25C / (P + 0.25G)" in score_help.get_text()
    assert "95%" in score_help.get_text()


def test_methods_explain_terms_and_link_them_in_context():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    techniques = read_json(REPO / "configs/techniques.json")
    markdown = (REPO / "outputs/report/league_table.md").read_text()
    for key in read_json(REPO / "configs/report-methods.json"):
        panel = soup.find("dialog", id="technique-" + key)
        assert panel.select_one(".method-terms")
        assert techniques[key]["terms"]
        for term in techniques[key]["terms"]:
            assert term["description"] in panel.get_text()
            assert term["description"] in markdown
            assert any(a["href"] == term["url"] for a in panel.select(".method-terms a"))
        assert panel.select_one(".technique-description a, .technique-flow a")
    chosen = soup.find("dialog", id="technique-structure_precision")
    assert "Reuse frozen v2 trees" not in chosen.get_text()
    assert "No further model training" in chosen.get_text()
