"""Exercise production Qwen file and image paths with a controlled generation boundary."""

import importlib
import json
import runpy
import sys
from types import ModuleType, SimpleNamespace

import pymupdf
import pytest

from pdf_heading_benchmark.io import REPO, write_json


@pytest.fixture
def qwen_runtime(tmp_path, monkeypatch):
    calls = []
    core = ModuleType("mlx.core")
    core.random = SimpleNamespace(seed=lambda value: None)
    core.clear_cache = lambda: None
    core.get_peak_memory = lambda: 0
    mlx = ModuleType("mlx")
    mlx.core = core
    vlm = ModuleType("mlx_vlm")
    vlm.load = lambda *args, **kwargs: (SimpleNamespace(config={}), object())
    prompt = ModuleType("mlx_vlm.prompt_utils")

    def template(processor, config, content, **kwargs):
        calls.append({"content": content, **kwargs})
        return content

    prompt.apply_chat_template = template
    for name, module in (
        ("mlx", mlx),
        ("mlx.core", core),
        ("mlx_vlm", vlm),
        ("mlx_vlm.prompt_utils", prompt),
    ):
        monkeypatch.setitem(sys.modules, name, module)
    for name in ("run_qwen_ids", "run_qwen_visual_memory", "run_qwen_compact", "run_qwen_sparse_memory"):
        monkeypatch.delitem(sys.modules, name, raising=False)
    monkeypatch.setattr(importlib.metadata, "version", lambda name: "test-boundary")
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    with pymupdf.open() as doc:
        for title in ("Cover", "Summary", "Findings"):
            doc.new_page().insert_text((72, 72), title)
        doc.save(corpus / "example.pdf")
    out = tmp_path / "results/example"
    out.mkdir(parents=True)
    heads = [{"page": 2, "title": "Summary", "level": 6}, {"page": 3, "title": "Findings", "level": 6}]
    write_json(out / "pymupdf4llm.headings.json", heads)
    write_json(out / "pdf_tags_full_context.json", [])
    write_json(corpus / "manifest.json", [{"id": "example", "path": str(corpus / "example.pdf")}])
    write_json(tmp_path / "reference/audit_pages.json", {"example": [2, 3]})
    yield tmp_path, vlm, calls
    for name in ("run_qwen_ids", "run_qwen_visual_memory", "run_qwen_compact", "run_qwen_sparse_memory"):
        sys.modules.pop(name, None)


def generation(raw):
    return iter(
        [
            SimpleNamespace(
                text=raw, generation_tokens=10, prompt_tokens=20, peak_memory=0, finish_reason="stop"
            )
        ]
    )


def test_candidate_ids_preserve_titles_and_reject_one_candidate(qwen_runtime, monkeypatch):
    root, vlm, calls = qwen_runtime
    vlm.stream_generate = lambda *a, **kw: generation('{"h0000":1,"h0001":null}')
    module = importlib.import_module("run_qwen_ids")
    monkeypatch.setattr(module, "ROOT", root)
    write_json(root / "models/qwen_revision.json", {"model": "boundary", "revision": "pinned"})
    monkeypatch.setattr(sys, "argv", ["runner", "pymupdf4llm"])
    module.main()
    result = json.loads((root / "results/example/qwen_ids_pymupdf4llm.headings.json").read_text())
    assert result == [{"page": 2, "title": "Summary", "level": 1}]
    assert calls[0]["num_images"] == 0
    assert calls[0]["enable_thinking"] is False
    assert '"level":6' not in calls[0]["content"]


@pytest.mark.parametrize("runner", ["run_qwen_compact", "run_qwen_sparse_memory"])
def test_visual_runners_read_fresh_paths_and_keep_memory_behind_target(qwen_runtime, runner):
    root, vlm, calls = qwen_runtime
    vlm.stream_generate = lambda *a, **kw: generation('[{"title":"Summary","level":1}]')
    module = importlib.import_module(runner)
    output = root / "trial"
    output.mkdir()
    args = SimpleNamespace(input_data=root, output=output)
    records = module.document(args, "example", [2, 3], SimpleNamespace(config={}), object())
    assert [r["page"] for r in records] == [2, 3]
    assert records[0]["headings"][0]["page"] == 2
    assert records[1]["headings"][0]["page"] == 3
    assert (output / "example/3.json").exists()
    if runner == "run_qwen_sparse_memory":
        assert records[0]["memory_pages"] == []
        assert records[1]["memory_pages"] == [2]
        assert [c["num_images"] for c in calls] == [1, 2]
    else:
        assert [c["num_images"] for c in calls] == [1, 1]
        assert '"page": 2' in calls[1]["content"]


def test_visual_memory_main_writes_document_exports(qwen_runtime, monkeypatch):
    root, vlm, calls = qwen_runtime
    vlm.stream_generate = lambda *a, **kw: generation('[{"title":"Summary","level":1}]')
    module = importlib.import_module("run_qwen_visual_memory")
    monkeypatch.setattr(module, "ROOT", root)
    write_json(root / "models/download-Qwen3.6-27B-4bit.json", {"path": "boundary"})
    module.main()
    result = root / "results/example/qwen36_visual_memory"
    assert len(json.loads(result.with_suffix(".headings.json").read_text())) == 2
    assert "Findings" in result.with_suffix(".md").read_text()
    assert [c["num_images"] for c in calls] == [1, 2]


def test_compact_runner_rejects_wrong_model_pin(qwen_runtime):
    root, vlm, _ = qwen_runtime
    vlm.stream_generate = lambda *a, **kw: generation("[]")
    module = importlib.import_module("run_qwen_compact")
    record = root / "wrong.json"
    write_json(record, {"repo": "wrong", "revision": "wrong"})
    with pytest.raises(ValueError, match="pinned"):
        module.protocol(SimpleNamespace(model="Qwen3.6-27B-4bit", model_record=record), {})


def test_runtime_check_requests_configs_without_weights(qwen_runtime, monkeypatch):
    root, vlm, _ = qwen_runtime
    vlm.stream_generate = lambda *a, **kw: generation("[]")
    core = sys.modules["mlx.core"]
    core.default_device = lambda: "test-device"
    core.metal = SimpleNamespace(is_available=lambda: False)
    hub, utils = ModuleType("huggingface_hub"), ModuleType("mlx_vlm.utils")
    downloads = []

    def download(**kwargs):
        downloads.append(kwargs)
        return str(root / "snapshot")

    hub.snapshot_download = download
    utils.get_model_and_args = lambda config, path: (SimpleNamespace(__name__="fixture"), "fixture")
    utils.load_processor = lambda path: object()
    monkeypatch.setitem(sys.modules, "huggingface_hub", hub)
    monkeypatch.setitem(sys.modules, "mlx_vlm.utils", utils)
    write_json(root / "snapshot/config.json", {"model_type": "fixture"})
    output = root / "check.json"
    monkeypatch.setattr(sys, "argv", ["check", "--cache", str(root), "--output", str(output)])
    runpy.run_path(str(REPO / "scripts/runners/check_qwen_runtime.py"), run_name="__main__")
    result = json.loads(output.read_text())
    assert len(result["models"]) == 3
    assert all(not m["weights_loaded"] for m in result["models"].values())
    assert all("*.safetensors" not in d["allow_patterns"] for d in downloads)
