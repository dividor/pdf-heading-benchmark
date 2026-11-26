import json
import runpy
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pymupdf
import pytest

from pdf_heading_benchmark.cli import run_method
from pdf_heading_benchmark.io import REPO

PADDLE = runpy.run_path(str(REPO / "scripts/runners/run_official_paddle.py"))
MINICPM = runpy.run_path(str(REPO / "scripts/runners/run_official_minicpm.py"))
SERVER = runpy.run_path(str(REPO / "scripts/runners/serve_local_mlx.py"))
REPORT = runpy.run_path(str(REPO / "scripts/official_pipelines_report.py"))
XIAOMI = runpy.run_path(str(REPO / "scripts/runners/run_official_xiaomi.py"))


def test_cli_does_not_silently_complete_a_pipeline_requiring_a_local_server(tmp_path):
    with pytest.raises(ValueError, match="separately started local model server"):
        run_method("paddleocr_vl16_official", tmp_path)


def test_paddle_runner_uses_native_markdown_and_saves_evidence(tmp_path):
    result = SimpleNamespace(markdown={"markdown_texts": "### 1. Introduction"}, save_to_json=Mock())
    pipeline = SimpleNamespace(predict=Mock(return_value=[result]))
    with pymupdf.open() as pdf:
        pdf.new_page()
        record = PADDLE["run_page"](pipeline, pdf, 1, tmp_path)
    assert record["headings"] == [dict(page=1, title="1. Introduction", level=3)]
    assert (tmp_path / "1.png").is_file()
    assert json.loads((tmp_path / "1.json").read_text()) == record
    result.save_to_json.assert_called_once()
    assert pipeline.predict.call_args.kwargs == {"temperature": 0}


def test_paddle_runner_rejects_missing_results(tmp_path):
    pipeline = SimpleNamespace(predict=Mock(return_value=[]))
    with pymupdf.open() as pdf:
        pdf.new_page()
        with pytest.raises(RuntimeError, match="Expected one result"):
            PADDLE["run_page"](pipeline, pdf, 1, tmp_path)


def test_minicpm_images_and_markdown_keep_physical_pages(tmp_path):
    (tmp_path / "corpus").mkdir()
    with pymupdf.open() as pdf:
        pdf.new_page()
        pdf.new_page()
        pdf.save(tmp_path / "corpus/example.pdf")
    MINICPM["render_inputs"](tmp_path, {"example": [2]}, tmp_path / "images")
    assert (tmp_path / "images/example-2.png").is_file()
    (tmp_path / "markdown").mkdir()
    (tmp_path / "markdown/example-2.md").write_text("#### Features")
    MINICPM["collect_outputs"](tmp_path, {"example": [2]})
    assert json.loads((tmp_path / "predictions.json").read_text()) == {
        "example": [dict(page=2, title="Features", level=4)]
    }


def test_minicpm_rejects_block_failures_even_when_all_pages_have_outputs():
    counts = dict(planned=32, ok=32, failed=0, failed_blocks=0, pages_with_failed_blocks=0)
    MINICPM["validate_summary"]({"counts": counts}, 32)
    counts["failed_blocks"] = 1
    with pytest.raises(RuntimeError, match="failed recognition blocks"):
        MINICPM["validate_summary"]({"counts": counts}, 32)


def test_local_server_requires_one_cors_middleware_and_explicit_origin():
    kind = object()
    item = SimpleNamespace(cls=kind, kwargs={})
    SERVER["restrict_origins"](SimpleNamespace(user_middleware=[item]), kind)
    assert item.kwargs["allow_origins"] == ["http://127.0.0.1:8111"]
    with pytest.raises(RuntimeError, match="exactly one"):
        SERVER["restrict_origins"](SimpleNamespace(user_middleware=[]), kind)


def test_official_report_scores_all_wrong_level_predictions():
    evidence = json.loads((REPO / "outputs/official-pipelines/paddleocr_vl16_official.json").read_text())
    row, scores = REPORT["scored_run"]("paddleocr_vl16_official", evidence)
    assert len(scores) == 4
    assert row["correct_level"] == 18
    assert row["predicted"] == 71
    assert row["joint_f05"] == pytest.approx(1.25 * 18 / (71 + 0.25 * 77))


def test_ovis_uses_official_prompt_pixel_bounds_and_native_levels(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "vllm", SimpleNamespace(LLM=Mock(), SamplingParams=SimpleNamespace))
    runner = runpy.run_path(str(REPO / "scripts/runners/run_ovis_official.py"))
    output = SimpleNamespace(text="## Features", token_ids=[1, 2], finish_reason="stop")
    model = SimpleNamespace(generate=Mock(return_value=[SimpleNamespace(outputs=[output])]))
    tokenizer = SimpleNamespace(apply_chat_template=Mock(return_value="rendered prompt"))
    with pymupdf.open() as pdf:
        pdf.new_page()
        record = runner["infer_page"](model, tokenizer, "official prompt", pdf, 1, tmp_path)
    request, sampling = model.generate.call_args.args
    assert sampling.temperature == 0 and sampling.max_tokens == 16384
    assert request[0]["mm_processor_kwargs"]["images_kwargs"]["size"] == {
        "shortest_edge": 448 * 448,
        "longest_edge": 2880 * 2880,
    }
    assert request[0]["multi_modal_data"]["image"][0].mode == "RGB"
    assert record["headings"][0]["level"] == 2
    assert record["tokens"] == 2
    assert tokenizer.apply_chat_template.call_args.kwargs["enable_thinking"] is False


def test_xiaomi_calls_upstream_cli_and_preserves_its_markdown(tmp_path, monkeypatch):
    args = SimpleNamespace(output=tmp_path, model=tmp_path / "model", upstream=tmp_path)
    detector = SimpleNamespace(predict=Mock(return_value=[{"boxes": []}]))
    serializer = Mock(return_value=[])

    def upstream_response(command, **kwargs):
        folder = tmp_path / "example/1-upstream"
        (folder / "1.md").write_text("## Introduction")
        kwargs["stdout"].write("VLM done: 1 success, 0 failures\n")
        assert "--retry-repetitive" in command
        assert command[command.index("--workers") + 1] == "1"
        assert len((folder / "layout.jsonl").read_text().splitlines()) == 1

    monkeypatch.setattr("subprocess.run", upstream_response)
    with pymupdf.open() as pdf:
        pdf.new_page()
        record = XIAOMI["run_page"](args, detector, serializer, pdf, "example", 1)
    assert record["headings"] == [dict(page=1, title="Introduction", level=2)]
    serializer.assert_called_once()
