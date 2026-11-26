"""Keep the published field plot distinct from the WFP measurements."""

import json
import runpy
import xml.etree.ElementTree as ET

import pymupdf
from bs4 import BeautifulSoup

from pdf_heading_benchmark.io import REPO


def test_field_plot_renders_published_coordinates(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.argv", ["field_overview.py", "--output-dir", str(tmp_path)])
    namespace = runpy.run_path(str(REPO / "scripts/field_overview.py"), run_name="__main__")
    rows = json.loads((REPO / "configs/field-overview.json").read_text())["rows"]
    svg = (tmp_path / "ocr-text-layout.svg").read_text()
    root = ET.fromstring(svg)
    circles = root.findall("{http://www.w3.org/2000/svg}circle")[2:]
    assert len(circles) == len(rows) == 17
    for point, row in zip(circles, rows, strict=True):
        x, y = namespace["coordinate"](row["text"], row["layout"])
        assert float(point.attrib["cx"]) == x
        assert float(point.attrib["cy"]) == y
    chandra = next(row for row in rows if row["name"] == "Chandra OCR 2")
    assert (chandra["text"], chandra["layout"]) == (87.9, 95.4)
    assert "Layout classification score" in svg
    assert "Table extraction score" not in svg
    assert svg == (REPO / "docs/images/ocr-text-layout.svg").read_text()
    with pymupdf.open(tmp_path / "ocr-text-layout.png") as image:
        assert len(image) == 1
        assert image[0].rect.width > 1000


def test_field_plot_is_packaged_with_report_and_source():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    panel = soup.find(id="panel-field")
    image = panel.find("img", src="ocr-text-layout.png")
    assert image is not None
    assert image.find_parent("a")["href"] == "https://github.com/datalab-to/omni_parse_bench#results"
    assert "It does not test heading levels" in panel.get_text()
    assert (REPO / "outputs/report/ocr-text-layout.png").read_bytes() == (
        REPO / "docs/images/ocr-text-layout.png"
    ).read_bytes()
