import hashlib
import json

import pymupdf
import pytest

from pdf_heading_benchmark import official_evidence


@pytest.fixture
def official_run(tmp_path, monkeypatch):
    data, run = tmp_path / "data", tmp_path / "run"
    (data / "corpus").mkdir(parents=True)
    (run / "example").mkdir(parents=True)
    pdf = data / "corpus/example.pdf"
    with pymupdf.open() as doc:
        for _ in range(32):
            doc.new_page().insert_textbox((50, 50, 500, 600), "word " * 100)
        doc.save(pdf)
    pages = {"example": list(range(1, 33))}
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    corpus = [dict(id="example", sha256=digest)]
    original_read = official_evidence.read_json
    monkeypatch.setattr(
        official_evidence,
        "read_json",
        lambda path: (
            pages
            if path.name == "audit_pages.json"
            else corpus
            if path.name == "corpus.json"
            else original_read(path)
        ),
    )
    source = b"# Fixture execution snapshot\n"
    (run / "runner.py").write_bytes(source)
    protocol = dict(
        smoke=False,
        pages=pages,
        input_sha256={"example": digest},
        source_sha256={"runner.py": hashlib.sha256(source).hexdigest()},
    )
    (run / "protocol.json").write_text(json.dumps(protocol))
    (run / "timing.json").write_text(json.dumps(dict(seconds=32, pages=32, errors=0)))
    predictions = []
    for page in pages["example"]:
        heading = dict(page=page, title="Methods", level=3)
        predictions.append(heading)
        (run / "example" / f"{page}.json").write_text(
            json.dumps(
                dict(
                    page=page,
                    text="### Methods\n\n" + "word " * 100,
                    headings=[heading],
                    error=None,
                )
            )
        )
    (run / "predictions.json").write_text(json.dumps({"example": predictions}))
    return run, data


def test_official_import_preserves_native_levels_and_removes_full_text(official_run):
    run, data = official_run
    evidence = official_evidence.import_run(run, data)
    assert evidence["predictions"]["example"][0]["level"] == 3
    assert "text" not in evidence["pages"]["example"][0]
    assert evidence["prose"]["example"]["retained"] > 0


def test_official_import_rejects_repaired_or_changed_headings(official_run):
    run, data = official_run
    path = run / "predictions.json"
    predictions = json.loads(path.read_text())
    predictions["example"][0]["level"] = 1
    path.write_text(json.dumps(predictions))
    with pytest.raises(ValueError, match="native Markdown"):
        official_evidence.import_run(run, data)


def test_official_import_rejects_smoke_runs(official_run):
    run, data = official_run
    path = run / "protocol.json"
    protocol = json.loads(path.read_text())
    protocol["smoke"] = True
    path.write_text(json.dumps(protocol))
    with pytest.raises(ValueError, match="complete fixed audit"):
        official_evidence.import_run(run, data)


def test_official_import_rejects_changed_execution_source(official_run):
    run, data = official_run
    (run / "runner.py").write_text("# Changed after the run\n")
    with pytest.raises(ValueError, match="execution source differs"):
        official_evidence.import_run(run, data)


def test_public_protocol_removes_local_roots_but_preserves_model_identity(tmp_path):
    protocol = {
        "command": [str(tmp_path / "images")],
        "layout": str(official_evidence.Path.home() / ".paddlex/model"),
        "model": "/Volumes/storage/cache/hub/models--example/snapshots/revision",
        "ollama_model": {"template": "original template", "parameters": "temperature 0"},
    }
    result = official_evidence.public_protocol(protocol, tmp_path)
    assert result["command"] == ["$DATA/images"]
    assert result["layout"] == "$USER_HOME/.paddlex/model"
    assert result["model"] == "$HF_HUB/models--example/snapshots/revision"
    assert result["ollama_model"]["template_sha256"] == hashlib.sha256(b"original template").hexdigest()
    assert "template" not in result["ollama_model"]
    assert protocol["ollama_model"]["template"] == "original template"
