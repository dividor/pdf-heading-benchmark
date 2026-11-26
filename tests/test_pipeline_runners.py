import hashlib
import json
import runpy
import sys
from types import SimpleNamespace

import benchmark_evidencelab
import prepare_evidencelab_models
import pytest
import run_docling_ocr
import run_evidencelab

from pdf_heading_benchmark.io import REPO

REPORT = runpy.run_path(str(REPO / "scripts/pipeline_report.py"))


class Options:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def model_dump_json(self):
        return json.dumps(self.__dict__, default=vars)


def test_ocr_configuration_forces_image_recognition(monkeypatch):
    monkeypatch.setitem(
        sys.modules,
        "docling.datamodel.accelerator_options",
        SimpleNamespace(AcceleratorDevice=SimpleNamespace(CPU="cpu"), AcceleratorOptions=Options),
    )
    monkeypatch.setitem(
        sys.modules,
        "docling.datamodel.pipeline_options",
        SimpleNamespace(
            OcrMode=SimpleNamespace(FULL_PAGE="full_page"),
            PdfPipelineOptions=Options,
            RapidOcrOptions=Options,
        ),
    )
    options = run_docling_ocr.make_options()
    assert options.do_ocr and options.generate_parsed_pages and not options.do_table_structure
    assert options.ocr_options.__dict__ == dict(mode="full_page", lang=["latin"], backend="onnxruntime")
    assert options.accelerator_options.__dict__ == dict(device="cpu", num_threads=8)


def test_evidencelab_launcher_pins_image_and_isolates_data(tmp_path, monkeypatch):
    calls = []
    output = tmp_path / "run-001"

    def invoke(command, **kwargs):
        calls.append((command, kwargs))
        if len(calls) == 1:
            (tmp_path / "model-files.json").write_text("{}")
        else:
            output.mkdir()

    monkeypatch.setattr(benchmark_evidencelab.subprocess, "run", invoke)
    benchmark_evidencelab.run(tmp_path, output)
    assert len(calls) == 2
    preparation, parser = [c[0] for c in calls]
    assert "HF_HUB_OFFLINE=0" in preparation and "HF_HUB_OFFLINE=1" in parser
    assert any("@sha256:" in word for word in parser)
    assert f"{tmp_path / 'corpus'}:/corpus:ro" in parser
    assert "12g" in parser and "4" in parser
    assert all(c[1]["check"] for c in calls)
    assert (tmp_path / "runner.py").read_bytes() == (REPO / "scripts/runners/run_evidencelab.py").read_bytes()
    assert (output / "model-files.json").read_text() == "{}"
    with pytest.raises(ValueError, match="fresh"):
        benchmark_evidencelab.run(tmp_path, output)
    monkeypatch.setattr(benchmark_evidencelab, "read_json", lambda path: {"image": "floating:tag"})
    with pytest.raises(ValueError, match="digest"):
        benchmark_evidencelab.docker_command(tmp_path, tmp_path)


def test_model_preparation_records_exact_files(tmp_path):
    revision = "a" * 40
    snapshot = tmp_path / "model/snapshots" / revision
    snapshot.mkdir(parents=True)
    (snapshot / "weights").write_bytes(b"weights")
    calls = []

    def download(**kwargs):
        calls.append(kwargs)
        return snapshot

    config = {"models": [dict(repo="owner/model", ref="main", revision=revision)]}
    result = prepare_evidencelab_models.prepare(config, tmp_path, download)
    assert calls == [dict(repo_id="owner/model", revision=revision, cache_dir=tmp_path)]
    assert result[0]["files"]["weights"] == hashlib.sha256(b"weights").hexdigest()
    assert (snapshot.parent.parent / "refs/main").read_text() == revision
    with pytest.raises(ValueError, match="revision"):
        prepare_evidencelab_models.prepare(config, tmp_path, lambda **kwargs: tmp_path)


@pytest.fixture
def runner_input(tmp_path):
    repo, corpus = tmp_path / "repo", tmp_path / "corpus"
    (repo / "configs").mkdir(parents=True)
    corpus.mkdir()
    (corpus / "example.pdf").write_bytes(b"fixture pdf")
    manifest = [
        dict(id="example", title="Example", pages=1, sha256=hashlib.sha256(b"fixture pdf").hexdigest())
    ]
    (repo / "configs/corpus.json").write_text(json.dumps(manifest))
    (repo / "configs/evidencelab.json").write_text(json.dumps({"parser": {"no_ocr": True}}))
    return repo, corpus, tmp_path / "output"


@pytest.mark.parametrize("success", [True, False])
def test_evidencelab_runner_archives_success_and_failure(runner_input, monkeypatch, success):
    calls = []

    class Parser:
        def __init__(self, **kwargs):
            calls.append(kwargs)

        def setup(self):
            calls.append("setup")

        def teardown(self):
            calls.append("teardown")

        def process_document(self, item):
            calls.append(item)
            return {"success": success}

    monkeypatch.setitem(
        sys.modules, "pipeline.processors.parsing.parser", SimpleNamespace(ParseProcessor=Parser)
    )
    monkeypatch.setattr(run_evidencelab.importlib.metadata, "version", lambda name: "fixture")
    repo, corpus, output = runner_input
    if success:
        run_evidencelab.run(repo, corpus, output)
        assert calls[-1] == "teardown"
        assert json.loads((output / "timing.json").read_text())[0]["pages"] == 1
    else:
        with pytest.raises(RuntimeError, match="EvidenceLab failed"):
            run_evidencelab.run(repo, corpus, output)
        assert not (output / "timing.json").exists()
    assert json.loads((output / "example.result.json").read_text())["success"] == success
    assert (
        json.loads((output / "protocol.json").read_text())["source_sha256"]
        == hashlib.sha256((output / "runner.py").read_bytes()).hexdigest()
    )


@pytest.mark.parametrize("status", ["success", "partial_success"])
def test_docling_runner_only_accepts_complete_documents(runner_input, monkeypatch, status):
    calls = []

    class Document:
        def save_as_json(self, path):
            path.write_text("{}")

        def export_to_markdown(self):
            return "# Methods"

    result = SimpleNamespace(status=status, pages=[1], document=Document())

    class Converter:
        def __init__(self, **kwargs):
            calls.append(kwargs)

        def initialize_pipeline(self, format):
            calls.append(format)

        def convert(self, path):
            calls.append(path)
            return result

    monkeypatch.setattr(run_docling_ocr, "make_options", lambda: Options(do_ocr=True))
    monkeypatch.setattr(run_docling_ocr.importlib.metadata, "version", lambda name: "fixture")
    monkeypatch.setitem(
        sys.modules, "docling.datamodel.base_models", SimpleNamespace(InputFormat=SimpleNamespace(PDF="pdf"))
    )
    monkeypatch.setitem(
        sys.modules, "docling.datamodel.pipeline_options", SimpleNamespace(HeadingHierarchyOptions=Options)
    )
    monkeypatch.setitem(
        sys.modules,
        "docling.document_converter",
        SimpleNamespace(DocumentConverter=Converter, PdfFormatOption=Options),
    )
    monkeypatch.setitem(
        sys.modules,
        "docling.models.stages.heading_hierarchy.heading_hierarchy_model",
        SimpleNamespace(HeadingHierarchyModel=lambda options: lambda doc: calls.append(options.enabled)),
    )
    repo, corpus, output = runner_input
    if status == "success":
        run_docling_ocr.run(repo, corpus, output)
        assert calls[-1] is True
        assert (output / "example.md").read_text() == "# Methods"
        assert json.loads((output / "timing.json").read_text())[0]["pages"] == 1
    else:
        with pytest.raises(RuntimeError, match="did not complete"):
            run_docling_ocr.run(repo, corpus, output)
        assert not (output / "timing.json").exists()


def test_pipeline_publisher_scores_native_levels(tmp_path, monkeypatch):
    config = tmp_path / "configs"
    config.mkdir()
    (config / "gold.json").write_text(json.dumps({"example": [dict(title="Methods", level=2, page=1)]}))
    (config / "audit_pages.json").write_text(json.dumps({"example": [1]}))
    out = tmp_path / "outputs"
    out.mkdir()
    for name, value in (("league_table", []), ("league_details", []), ("audit_predictions", {})):
        (out / f"{name}.json").write_text(json.dumps(value))
    monkeypatch.setitem(REPORT["score"].__globals__, "REPO", tmp_path)
    evidence = dict(
        predictions={"example": [dict(title="Methods", level=3, page=1)]},
        prose={"example": dict(retained=10, total=10)},
        timing=dict(seconds=2, pages=1),
    )
    row = REPORT["publish"]("docling_ocr", evidence)
    assert row["matched"] == 1 and row["correct_level"] == 0 and row["joint_f05"] == 0
    assert row["native_prose_retention"] == 1
    before = (out / "league_table.json").read_bytes()
    REPORT["rebuild"]()
    assert (out / "league_table.json").read_bytes() == before
    assert json.loads((out / "pipeline-runs/docling_ocr.json").read_text()) == evidence


def test_ocr_preparation_rejects_changed_weights(tmp_path):
    import prepare_docling_ocr_models

    data = b"recorded weights"
    config = dict(
        rapidocr=[
            dict(name="rec.onnx", url="https://example.org/rec.onnx", sha256=hashlib.sha256(data).hexdigest())
        ]
    )
    calls = []

    def download(url):
        calls.append(url)
        return data

    assert prepare_docling_ocr_models.prepare_ocr(config, tmp_path, download) == config["rapidocr"]
    prepare_docling_ocr_models.prepare_ocr(config, tmp_path, download)
    assert calls == ["https://example.org/rec.onnx"]
    (tmp_path / "rec.onnx").write_bytes(b"changed")
    with pytest.raises(ValueError, match="weight hash"):
        prepare_docling_ocr_models.prepare_ocr(config, tmp_path, download)


def test_ocr_download_checks_http_status(monkeypatch):
    import prepare_docling_ocr_models

    calls = []
    response = SimpleNamespace(content=b"weights", raise_for_status=lambda: calls.append("checked"))
    monkeypatch.setattr(prepare_docling_ocr_models.requests, "get", lambda url, timeout: response)
    assert prepare_docling_ocr_models.fetch("https://example.org/weights") == b"weights"
    assert calls == ["checked"]
