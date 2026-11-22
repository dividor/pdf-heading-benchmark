"""A partial run or source drift must not become a completed league result."""

import runpy

import pytest

from pdf_heading_benchmark.io import REPO, read_json, write_json

REPORT = runpy.run_path(str(REPO / "scripts/qwen_compact_report.py"))
IMPORT_RUN = REPORT["import_run"]


def test_import_rejects_partial_audit_scope(tmp_path):
    write_json(tmp_path / "run/protocol.json", {"pages": {"targeting": [7]}})
    with pytest.raises(ValueError, match="audit-page scope"):
        IMPORT_RUN(tmp_path, "qwen36_27b_compact", "run")


def test_import_rejects_changed_inference_source(tmp_path):
    write_json(
        tmp_path / "run/protocol.json",
        {
            "pages": read_json(REPO / "configs/audit_pages.json"),
            "source_sha256": {"src/pdf_heading_benchmark/compact_prompt.py": "0" * 64},
        },
    )
    with pytest.raises(ValueError, match="Source changed"):
        IMPORT_RUN(tmp_path, "qwen36_27b_compact", "run")


def test_unmeasured_timing_is_not_reported_as_zero():
    duration = REPORT["optional_duration"]
    assert duration([{"first_token_seconds": None}], "first_token_seconds", 60) == "—"
    assert duration([{"preparation_seconds": 0.0}], "preparation_seconds") == "0.0 s"
