"""Custom documents need original page numbers and independent resume directories."""

import pymupdf
import pytest

from pdf_heading_benchmark.extraction import initialize
from pdf_heading_benchmark.io import read_json


def test_custom_document_initialization(tmp_path):
    source = tmp_path / "source.pdf"
    with pymupdf.open() as doc:
        doc.new_page().insert_text((72, 72), "One")
        doc.new_page().insert_text((72, 72), "Two")
        doc.save(source)
    output = tmp_path / "run"
    initialize(source, output)
    assert read_json(output / "reference/audit_pages.json") == {"document": [1, 2]}
    manifest = read_json(output / "corpus/manifest.json")
    assert manifest[0]["pages"] == 2
    assert manifest[0]["title"] == "source"
    assert (output / "corpus/document.pdf").read_bytes() == source.read_bytes()
    assert not (output / "reference/gold.json").exists()
    with pytest.raises(FileExistsError):
        initialize(source, output)
