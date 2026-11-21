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
    rows = soup.find("table").find("tbody").find_all("tr")
    assert len(rows) == 18
    for row in rows:
        assert len(row.find_all("td")) == 10
        assert (
            row.find_all("td")[1]
            .find("a")["href"]
            .startswith("https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/")
        )
    for method in read_json(REPO / "configs/methods.json").values():
        for step in method["steps"]:
            assert (REPO / step["script"]).is_file()
