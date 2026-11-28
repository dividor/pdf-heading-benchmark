"""The complete report must stay deterministic and its code links must resolve locally."""

from html import escape

from bs4 import BeautifulSoup

from pdf_heading_benchmark.io import REPO, read_json
from pdf_heading_benchmark.report import build_report, time_for_32_pages


def test_report_is_reproducible_and_has_all_method_links():
    paths = [REPO / "outputs/report" / name for name in ("index.html", "league_table.md")]
    before = [p.read_bytes() for p in paths]
    build_report()
    assert [p.read_bytes() for p in paths] == before
    soup = BeautifulSoup(paths[0].read_text(), "html.parser")
    corpus_rows = soup.select_one("#panel-documents table tbody").find_all("tr")
    corpus = read_json(REPO / "configs/corpus.json")
    assert [row.find("a")["href"] for row in corpus_rows] == [doc["url"] for doc in corpus]
    results = soup.select_one("table.league-table")
    assert [th.contents[0].strip() for th in results.find_all("th")][:3] == [
        "Configuration",
        "Time for 32 pages",
        "Primary score: joint F0.5",
    ]
    scores = read_json(REPO / "outputs/report/results.json")
    combined_scores = [r["joint_f05"] for r in scores]
    assert combined_scores == sorted(combined_scores, reverse=True)
    rows = results.find("tbody").find_all("tr")
    assert len(rows) == len(read_json(REPO / "configs/report-methods.json"))
    for row in rows:
        assert len(row.find_all("td")) == 11
        assert (
            row.find_all("td")[5]
            .find("a")["href"]
            .startswith("https://github.com/dividor/pdf-heading-benchmark/blob/")
        )
    for method in read_json(REPO / "configs/methods.json").values():
        for step in method["steps"]:
            assert (REPO / step["script"]).is_file()


def test_32_page_times_stay_with_their_configuration_before_the_score():
    from markdown_it import MarkdownIt

    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    rows = soup.select("table.league-table tbody tr")
    records = read_json(REPO / "outputs/report/results.json")
    for row, record in zip(rows, records, strict=True):
        expected = BeautifulSoup(MarkdownIt().render(time_for_32_pages(record)), "html.parser")
        assert row.find_all("td")[1].get_text().strip() == expected.get_text().strip()
        assert row.find_all("td")[2].get_text().strip() == f"{record['joint_f05']:.1%}"
    help_button = soup.select_one("table.league-table th:nth-child(2) button")
    assert "Estimated" in soup.find(id=help_button["aria-controls"]).get_text()


def test_measured_table_remains_local_with_requested_cloud_services_queued():
    selected = set(read_json(REPO / "configs/report-methods.json"))
    assert len(selected) >= 21
    for filename in ("results.json", "details.json"):
        rows = read_json(REPO / "outputs/report" / filename)
        assert {row["method"] for row in rows} == selected
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    report = str(soup.select_one(".league-table"))
    for excluded in ("Azure", "Mistral", "azure_layout", "mistral_ocr41", "API USD"):
        assert excluded not in report
    field = soup.select_one("#panel-field").get_text()
    for candidate in (
        "mistral-ocr-2512",
        "prebuilt-layout",
        "pretrained-layout-parser-v3.5-2026-07-09",
        "LlamaParse",
    ):
        assert candidate in field
    assert "Cloud services queued for comparison" in field


def test_every_configuration_has_an_accessible_diagram_and_markdown_sources():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    configs = read_json(REPO / "configs/report-methods.json")
    assert len(soup.select("a[data-technique]")) == len(configs)
    assert len(soup.select('dialog[id^="technique-"]')) == len(configs)
    identifiers = [element["id"] for element in soup.select("[id]")]
    assert len(identifiers) == len(set(identifiers))
    markdown = (REPO / "outputs/report/league_table.md").read_text()
    for key in configs:
        panel = soup.find("dialog", id="technique-" + key)
        assert panel.find(id=panel["aria-labelledby"])
        assert panel.select_one('button[aria-label="Close technique diagram"]')
        assert len(panel.select(".technique-flow li")) >= 3
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
        record = (REPO / "outputs/report/method-records.md").read_text()
        for section in technique["sections"]:
            for paragraph in section["paragraphs"]:
                assert paragraph in record
        assert panel.select_one(".technique-details summary").get_text() == "Exact run settings"
        assert not panel.select_one(".technique-details").has_attr("open")
        diagrams.append(tuple((s["title"], s["detail"]) for s in technique["stages"]))
    assert len(set(diagrams)) == len(diagrams)


def test_information_buttons_resolve_to_named_dialogs():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    table = soup.select_one("table.league-table")
    assert len(table.select("th button.info-button")) == 11
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
    score_help = soup.find("dialog", id="column-help-2")
    assert "1.25C / (P + 0.25G)" in score_help.get_text()
    assert "no separate PASS/FAIL" in score_help.get_text()


def test_methods_explain_terms_and_link_them_in_context():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    techniques = read_json(REPO / "configs/techniques.json")
    for key in read_json(REPO / "configs/report-methods.json"):
        panel = soup.find("dialog", id="technique-" + key)
        assert not panel.select_one(".method-terms")
        shared = soup.select_one("#panel-methods .method-terms")
        assert techniques[key]["terms"]
        for term in techniques[key]["terms"]:
            assert term["name"] in shared.get_text()
            assert term["description"] in (REPO / "outputs/report/method-records.md").read_text()
            assert any(a["href"] == term["url"] for a in shared.select("a"))
        assert panel.select_one(".technique-description a, .technique-flow a")
    chosen = soup.find("dialog", id="technique-structure_precision")
    assert "Reuse frozen v2 trees" not in chosen.get_text()
    assert "No further model training" in chosen.get_text()


def test_league_shows_joint_precision_and_recall_without_detection_gate():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    table = soup.select_one("table.league-table")
    headers = [th.contents[0].strip() for th in table.find_all("th")]
    assert headers[2:5] == ["Primary score: joint F0.5", "Joint precision", "Joint recall"]
    assert "PASS" not in table.get_text() and "FAIL" not in table.get_text()
    rows = {row["method"]: row for row in read_json(REPO / "outputs/report/results.json")}
    for key in ("mineru_basic", "structure_precision"):
        cell = table.select_one(f'button[data-technique="technique-{key}"]').find_parent("tr")
        values = [td.get_text() for td in cell.find_all("td")]
        row = rows[key]
        expected = f"{row['correct_level'] / row['predicted']:.1%}"
        assert values[3].startswith(expected)
        assert values[4].startswith(f"{row['correct_level'] / row['gold']:.1%}")
    assert "Heading-only precision (diagnostic)" in soup.get_text()


def test_timing_is_readable_without_inventing_a_scope():
    from pdf_heading_benchmark.report import duration

    assert duration(dict(measured_seconds=11.662223, processed_pages=523)).startswith("**0.022 sec**")
    assert duration(dict(measured_seconds=3706.6876, processed_pages=32)).startswith("**1 min 56 sec**")
    assert duration(dict(measured_seconds=0, processed_pages=32)).startswith("**0.000 sec**")
    assert duration(dict(measured_seconds=None, processed_pages=32)) == "—"
    unknown = duration(dict(measured_seconds=100.0, processed_pages=None))
    assert unknown == "Page average unavailable<br>1 min 40 sec for the hierarchy stage"


def test_32_page_time_distinguishes_measurements_from_projections():
    from pdf_heading_benchmark.report import time_for_32_pages

    assert time_for_32_pages(dict(measured_seconds=3242.4, processed_pages=32)) == (
        "**54 min 2 sec**<br>Measured"
    )
    estimate = time_for_32_pages(dict(measured_seconds=523.0, processed_pages=523))
    assert estimate == "**32 sec**<br>Estimated from 8 min 43 sec measured over 523 pages"
    assert time_for_32_pages(dict(measured_seconds=100, processed_pages=None)) == "Unavailable"
    assert time_for_32_pages(dict(measured_seconds=None, processed_pages=32)) == "Unavailable"


def test_tabs_preserve_deep_links_and_keep_results_first():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    tabs = soup.select('.report-tabs [role="tab"]')
    assert [tab.get_text() for tab in tabs] == [
        "Results",
        "The OCR field",
        "Methods & scoring",
        "Documents",
        "Timing & evidence",
    ]
    for tab in tabs:
        panel = soup.find(id=tab["aria-controls"])
        assert panel["aria-labelledby"] == tab["id"]
    results = soup.find(id="panel-results")
    assert results.select_one(".league-table")
    assert results.find(id="our-trained-model")
    assert soup.find(id="published-comparison").find_parent(class_="report-panel")["id"] == "panel-field"
    assert soup.find(id="sequential-gpu-reruns").find_parent(class_="report-panel")["id"] == "panel-evidence"
    assert soup.find(id="show-diagnostics")
    assert "OvisOCR3" in soup.find(id="panel-field").get_text()
    assert not soup.select('.report-panel dialog[id^="technique-"]')
    assert len(soup.select('#panel-field dialog[id^="field-model-"]')) == 39

    assert soup.find(id="sequential-gpu-reruns").find("summary").get_text() == "Sequential GPU reruns"


def test_dialogs_prioritize_specific_steps_and_keep_long_records_closed():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    for key in read_json(REPO / "configs/report-methods.json"):
        panel = soup.find("dialog", id="technique-" + key)
        assert panel.select_one("[data-overview]")["href"] == "#panel-methods"
        assert len(panel.select_one(".technique-description").get_text().split()) <= 50
        assert not panel.select("details[open]")
        assert panel.select_one(".prediction-comparison").name == "details"
        assert panel.select_one(".technique-resources").name == "details"
        assert "Source papers describe" not in panel.get_text()
    chosen = soup.find(id="technique-structure_precision")
    visible_flow = chosen.select_one(".technique-flow").get_text()
    assert "0.70" in visible_flow and "200-tree" in visible_flow
    assert "142 measurements" in visible_flow
    assert (
        soup.find("summary", string="Heading-level audit").find_parent(class_="report-panel")["id"]
        == "panel-evidence"
    )
