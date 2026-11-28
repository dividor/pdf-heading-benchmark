"""Verify field coverage, score filtering, model details and reproducible rendering."""

import itertools
import runpy
import xml.etree.ElementTree as ET

import pymupdf
import pytest
from bs4 import BeautifulSoup

from pdf_heading_benchmark.field_charts import coordinate, eligible_rows, label_positions, overlaps
from pdf_heading_benchmark.field_explorer import enhance_field
from pdf_heading_benchmark.io import REPO, read_json


def test_field_plot_renders_every_eligible_coordinate(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.argv", ["field_overview.py", "--output-dir", str(tmp_path)])
    runpy.run_path(str(REPO / "scripts/field_overview.py"), run_name="__main__")
    data = read_json(REPO / "configs/field-overview.json")
    svg = (tmp_path / "ocr-text-layout.svg").read_text()
    root = ET.fromstring(svg)
    points = root.findall('.//{http://www.w3.org/2000/svg}g[@class="field-point"]')
    assert len(points) == len(eligible_rows(data)) == 39
    rows = eligible_rows(data)
    for point in points:
        row = rows[int(point.attrib["data-index"])]
        hit = point.find('{http://www.w3.org/2000/svg}circle[@class="field-hit"]')
        assert (float(hit.attrib["cx"]), float(hit.attrib["cy"])) == coordinate(row["text"], row["layout"])
        assert point.attrib["data-name"] == row["name"]
    assert {r["name"] for r in data["pending"]}.isdisjoint(p.attrib["data-name"] for p in points)
    assert "Layout not reported" not in svg
    assert "Table extraction score" not in svg
    assert svg == (REPO / "docs/images/ocr-text-layout.svg").read_text()
    with pymupdf.open(tmp_path / "ocr-text-layout.png") as image:
        assert len(image) == 1
        assert image[0].rect.width > 1000


def test_field_explorer_has_one_chart_all_apis_and_accessible_selection():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    panel = soup.find(id="panel-field")
    assert len(panel.select("svg.field-svg")) == 1
    assert not panel.find("img", src="ocr-field-overview.png")
    assert len(panel.select(".field-point")) == len(panel.select("#field-system option")) == 39
    assert len(panel.select('.field-point[data-category="hosted"]')) == 12
    assert len(panel.select('.field-point[data-category="study"]')) == 8
    assert panel.select_one('#field-system option[value="6"]').get_text() == "LlamaParse"
    for name in ("LlamaParse", "Azure", "Mistral OCR", "Reducto"):
        assert panel.select_one(f'.field-point[data-name="{name}"]') is not None
    assert "It does not test heading levels" in panel.get_text()
    assert (REPO / "outputs/report/ocr-text-layout.png").read_bytes() == (
        REPO / "docs/images/ocr-text-layout.png"
    ).read_bytes()


def test_layout_threshold_excludes_missing_and_exactly_seventy():
    rows = [{"name": str(value), "layout": value} for value in [None, 0, 69.9, 70, 70.1, 100]]
    assert [r["layout"] for r in eligible_rows({"rows": rows})] == [70.1, 100]
    assert rows[0]["layout"] is None
    with pytest.raises(ValueError, match="outside"):
        coordinate(20, 0)


def test_labels_avoid_other_labels_and_all_markers():
    rows = eligible_rows(read_json(REPO / "configs/field-overview.json"))
    details = read_json(REPO / "configs/field-model-details.json")
    positions = label_positions(rows, details)
    assert len(positions) >= 30
    assert all(i in positions for i, row in enumerate(rows) if details[row["name"]]["study_method"])
    for a, b in itertools.combinations(positions.values(), 2):
        assert not overlaps(a, b)
    for box in positions.values():
        for row in rows:
            x, y = coordinate(row["text"], row["layout"])
            assert not overlaps(box, (x - 10, y - 10, 20, 20))


def test_each_point_has_specific_model_dialog_and_valid_study_mapping():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    details = read_json(REPO / "configs/field-model-details.json")
    techniques = read_json(REPO / "configs/techniques.json")
    points = soup.select("#field-explorer .field-point")
    assert set(details) == {point["data-name"] for point in points}
    for point in points:
        detail = details[point["data-name"]]
        dialog = soup.find(id=point["aria-controls"])
        assert dialog.name == "dialog"
        assert dialog.find("h2").get_text() == point["data-name"]
        assert detail["description"] in dialog.get_text()
        assert len(dialog.select("dl dt")) >= 2
        assert dialog.select_one(".field-dialog-close")
        assert any(detail["provider"] + ".py" in a["href"] for a in dialog.select("a"))
        if detail["study_method"]:
            assert detail["study_method"] in techniques
            assert point["data-category"] == "study"
    assert details["Docling (formula)"]["study_method"] is None
    assert details["PyMuPDF4LLM (OCR)"]["study_method"] is None
    assert "Content Understanding" in details["Azure"]["description"]
    assert "mistral-ocr-4-1" in details["Mistral OCR"]["settings"]["Model"]


@pytest.mark.parametrize("html", ["<p>No chart</p>", '<img src="ocr-text-layout.png">'])
def test_missing_field_placeholder_fails(html):
    with pytest.raises(ValueError, match="placeholder"):
        enhance_field(html, {})


def test_chart_names_open_their_own_dialog_and_hosted_markers_draw_last():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    for label in soup.select(".field-name"):
        index = label["data-open-model"]
        assert label["data-for"] == index
        assert label["tabindex"] == "0"
        assert label["role"] == "button"
        assert soup.find(id=label["aria-controls"])["id"] == "field-model-" + index
    markers = soup.select(".field-points .field-point")
    assert all(marker["data-category"] == "hosted" for marker in markers[-12:])
    mistral = next(marker for marker in markers if marker["data-name"] == "Mistral OCR")
    assert mistral.find("rect") is not None
    assert mistral["data-text"] == "83.6"
    assert mistral["data-layout"] == "93.8"
    label = soup.select_one(f'.field-name[data-for="{mistral["data-index"]}"]')
    assert label.get_text() == "Mistral OCR"
