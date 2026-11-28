"""Native headings stay visible without silently filling missing levels."""

import json

import export_evidencelab

from pdf_heading_benchmark.heading_exports import write_heading_list


def test_heading_preview_preserves_missing_levels_and_indentation(tmp_path):
    path = tmp_path / "headings.md"
    write_heading_list(
        path, [dict(title="Child", level=3, page=2), dict(title="Unknown", level=None, page=None)], "Parser"
    )
    assert "    - H3 · PDF page 2 · Child" in path.read_text()
    assert "- Level not supplied · Page not supplied · Unknown" in path.read_text()


def test_evidencelab_export_uses_final_toc_and_preserves_markdown(tmp_path):
    folder = tmp_path / "parsed/other/document"
    folder.mkdir(parents=True)
    (tmp_path / "document.result.json").write_text('{"success": true}')
    (folder / "document.json").write_text('{"texts": []}')
    (folder / "document.md").write_text("### Introduction\n\nText\n")
    (folder / "toc.txt").write_text("[H1] Introduction | page 3\n")
    output = tmp_path / "exports"
    export_evidencelab.export(tmp_path, "document", output)
    assert (output / "evidencelab.md").read_bytes() == (folder / "document.md").read_bytes()
    assert json.loads((output / "evidencelab-headings.json").read_text()) == [
        dict(title="Introduction", level=1, page=3)
    ]
    assert "H1 · PDF page 3 · Introduction" in (output / "evidencelab-headings.md").read_text()
