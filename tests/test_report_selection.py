"""Published selections and display names agree across report formats."""

from bs4 import BeautifulSoup

from pdf_heading_benchmark.io import REPO, read_json


def test_our_method_names_and_removed_calibration_are_consistent():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    selected = read_json(REPO / "configs/report-methods.json")
    assert "structure_calibrated" not in selected
    assert soup.find(id="technique-structure_calibrated") is None
    for method, anchor in (
        ("structure_context_relations", "our-original-model"),
        ("structure_precision", "our-trained-model"),
    ):
        label = soup.find(id=anchor).parent.get_text(" ", strip=True)
        dialog = soup.find(id="title-" + method).get_text()
        assert "OUR METHOD" in label
        assert "v2" not in label
        assert dialog in label
        assert dialog in (REPO / "outputs/report/league_table.md").read_text()
    for filename in ("results.json", "details.json"):
        assert all(
            row["method"] != "structure_calibrated" for row in read_json(REPO / "outputs/report" / filename)
        )
