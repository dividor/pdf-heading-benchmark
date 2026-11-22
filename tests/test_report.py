"""The complete report must stay deterministic and its code links must resolve locally."""

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
    assert len(rows) == 20
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
    assert len(selected) == 20
    for filename in ("results.json", "details.json"):
        rows = read_json(REPO / "outputs/report" / filename)
        assert {row["method"] for row in rows} == selected
    report = (REPO / "outputs/report/league_table.md").read_text()
    for excluded in ("Azure", "Mistral", "azure_layout", "mistral_ocr41", "API USD"):
        assert excluded not in report
