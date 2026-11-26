import hashlib
import json

import pymupdf
import pytest

from pdf_heading_benchmark import pipeline_evidence as pipeline


@pytest.fixture
def pipeline_run(tmp_path, monkeypatch):
    data, run, repo = (tmp_path / name for name in ("data", "run", "repo"))
    (data / "corpus").mkdir(parents=True)
    (repo / "configs").mkdir(parents=True)
    run.mkdir()
    pdf = data / "corpus/example.pdf"
    with pymupdf.open() as doc:
        doc.new_page().insert_textbox((50, 50, 500, 600), "word " * 100)
        doc.save(pdf)
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    manifest = [dict(id="example", sha256=digest, pages=1)]
    (repo / "configs/corpus.json").write_text(json.dumps(manifest))
    (repo / "configs/audit_pages.json").write_text(json.dumps({"example": [1]}))
    for path in (
        run / "model-files.json",
        repo / "configs/evidencelab-model-files.json",
        repo / "configs/docling-ocr-model-files.json",
    ):
        path.write_text('{"fixture_model": "recorded_hash"}')
    monkeypatch.setattr(pipeline, "REPO", repo)
    source = b"# archived runner\n"
    (run / "runner.py").write_bytes(source)
    (run / "protocol.json").write_text(json.dumps(dict(source_sha256=hashlib.sha256(source).hexdigest())))
    (run / "timing.json").write_text(
        json.dumps([dict(document="example", pages=1, seconds=2, input_sha256=digest)])
    )
    (run / "initialization.json").write_text('{"seconds": 1}')
    document = dict(
        pages={"1": {}},
        texts=[
            dict(label="section_header", text="Methods", level=3, prov=[dict(page_no=1)]),
            dict(label="text", text="word " * 100, prov=[dict(page_no=1)]),
        ],
    )
    (run / "example.document.json").write_text(json.dumps(document))
    folder = run / "parsed/other/example"
    folder.mkdir(parents=True)
    (folder / "example.json").write_text(json.dumps(document))
    (folder / "toc.txt").write_text("[H2] Methods | page 1\n")
    (run / "example.result.json").write_text('{"success": true}')
    return run, data


def test_native_toc_is_not_repaired():
    title = "Long heading " * 8
    result = pipeline.toc_headings(f"x [H3] {title[:80]} | page 4 (iv) [Front]\n[H?] Unknown | page ?")
    assert result == [
        dict(title=title[:80].strip(), level=3, page=4),
        dict(title="Unknown", level=None, page=None),
    ]
    with pytest.raises(ValueError, match="Unrecognized"):
        pipeline.toc_headings("not a TOC entry")


@pytest.mark.parametrize("method,level", [("evidencelab", 2), ("docling_ocr", 3)])
def test_pipeline_import_preserves_scored_output(pipeline_run, method, level):
    run, data = pipeline_run
    result = pipeline.import_pipeline(run, data, method)
    assert result["predictions"]["example"] == [dict(title="Methods", level=level, page=1)]
    assert result["structured_headings"]["example"][0]["level"] == 3
    assert result["prose"]["example"]["retained"] > 0
    assert result["timing"] == dict(seconds=2, pages=1)


@pytest.mark.parametrize(
    "change,message",
    [
        ("source", "Execution source"),
        ("incomplete", "Incomplete"),
        ("pdf", "Source PDF"),
        ("timing", "Invalid page"),
        ("input", "different PDF"),
        ("document", "Incomplete parsed"),
        ("failed", "Parser reported"),
    ],
)
def test_import_rejects_invalid_evidence(pipeline_run, change, message):
    run, data = pipeline_run
    if change == "source":
        (run / "runner.py").write_text("changed")
    elif change == "pdf":
        (data / "corpus/example.pdf").write_bytes(b"changed")
    elif change == "failed":
        (run / "example.result.json").write_text('{"success": false}')
    elif change == "document":
        path = run / "parsed/other/example/example.json"
        value = json.loads(path.read_text())
        value["pages"] = {}
        path.write_text(json.dumps(value))
    else:
        path = run / "timing.json"
        value = json.loads(path.read_text())
        if change == "incomplete":
            value = []
        elif change == "timing":
            value[0]["seconds"] = 0
        else:
            value[0]["input_sha256"] = "changed"
        path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match=message):
        pipeline.import_pipeline(run, data, "evidencelab")


def test_unknown_method_fails(pipeline_run):
    run, data = pipeline_run
    with pytest.raises(ValueError, match="Unknown"):
        pipeline.import_pipeline(run, data, "unknown")


def test_import_rejects_changed_model_record(pipeline_run):
    run, data = pipeline_run
    (run / "model-files.json").write_text("{}")
    with pytest.raises(ValueError, match="Model file record"):
        pipeline.import_pipeline(run, data, "evidencelab")
