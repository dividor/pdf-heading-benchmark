"""Reject partial reruns and distinguish accumulated swap from activity in a run."""

import runpy

import pytest

from pdf_heading_benchmark.io import REPO, read_json, write_json

REPORT = runpy.run_path(str(REPO / "scripts/repeat_report.py"))


def test_repeat_rejects_failed_process(tmp_path):
    write_json(tmp_path / "example/execution.json", {"exit_code": 1})
    with pytest.raises(ValueError, match="failed method"):
        REPORT["import_method"](tmp_path, "example", {})


def test_repeat_rejects_incomplete_document_scope():
    with pytest.raises(ValueError, match="Incomplete document"):
        REPORT["score"]({"predictions": {}})


def test_repeat_rejects_incomplete_page_scope():
    gold = read_json(REPO / "configs/gold.json")
    with pytest.raises(ValueError, match="Incomplete page"):
        REPORT["score"]({"predictions": gold, "pages": {doc: [] for doc in gold}})


def test_swap_activity_uses_counter_difference_and_reported_page_size():
    before = dict(
        vm_stat="page size of 16384 bytes\nSwapins: 100.\nSwapouts: 200.\n",
        swap="used = 15G",
        load_average=[1, 2, 3],
        thermal="none",
    )
    after = dict(before, vm_stat="page size of 16384 bytes\nSwapins: 104.\nSwapouts: 202.\n")
    result = REPORT["gpu_summary"](
        [{"gpu": [{"Device Utilization %": 98}]}], dict(before=before, after=after)
    )
    assert result["swap_in_bytes"] == 4 * 16384
    assert result["swap_out_bytes"] == 2 * 16384
    assert result["median_percent"] == 98


def test_repeat_rejects_wrong_page_identity(tmp_path):
    write_json(tmp_path / "example/run/doc/7.json", {"page": 8})
    with pytest.raises(ValueError, match="identity mismatch"):
        REPORT["page_records"](tmp_path, "example", {"doc": [7]})
