"""The safety wrapper must stop its own process when resource limits are crossed."""

import argparse
import io
import json
import subprocess
import sys

import pytest

from pdf_heading_benchmark import run_guard


def options(tmp_path, command):
    return argparse.Namespace(
        output=tmp_path / "run",
        lock=tmp_path / "lock",
        command=command,
        reserve_gib=6,
        required_gib=1,
        swap_growth_gib=0.5,
        interval_seconds=0.01,
        timeout_seconds=2,
    )


def test_parse_memory():
    vm = "page size of 16384 bytes\nPages free: 65536.\nPages inactive: 131072.\nPages speculative: 65536.\n"
    sample = run_guard.parse_memory(vm, "used = 1024.00M", "1\n")
    assert sample == {"reclaimable_gib": 4, "swap_used_gib": 1, "pressure": 1}
    with pytest.raises(ValueError, match="Cannot read"):
        run_guard.parse_memory("bad", "bad", "1")


def test_memory_sample_reads_each_source(monkeypatch):
    replies = iter(
        [
            "page size of 16384 bytes\nPages free: 1.\nPages inactive: 2.\nPages speculative: 3.\n",
            "used = 512.00M",
            "1",
        ]
    )
    monkeypatch.setattr(subprocess, "check_output", lambda *args, **kwargs: next(replies))
    assert run_guard.memory_sample()["swap_used_gib"] == 0.5


def test_pressure_reserve_and_swap_gates():
    baseline = {"pressure": 1, "reclaimable_gib": 10, "swap_used_gib": 1}
    assert run_guard.unsafe_reason(baseline, baseline, 6, 0.5) is None
    for changed in ({"pressure": 2}, {"reclaimable_gib": 5}, {"swap_used_gib": 1.6}):
        assert run_guard.unsafe_reason(baseline | changed, baseline, 6, 0.5)


def test_success_failure_and_preflight(tmp_path, monkeypatch):
    healthy = {"pressure": 1, "reclaimable_gib": 10, "swap_used_gib": 1}
    monkeypatch.setattr(run_guard, "memory_sample", lambda: healthy)
    for index, exit_code in enumerate((0, 3)):
        args = options(tmp_path / str(index), [sys.executable, "-c", f"raise SystemExit({exit_code})"])
        assert run_guard.run_guarded(args) == (0 if exit_code == 0 else 1)
        record = json.loads((args.output / "status.json").read_text())
        assert record["returncode"] == exit_code
    args = options(tmp_path / "blocked", ["command-that-must-not-start"])
    args.required_gib = 20
    assert run_guard.run_guarded(args) == 75
    assert json.loads((args.output / "status.json").read_text())["status"] == "resource_blocked"


def test_abort_stops_real_child(tmp_path, monkeypatch):
    samples = iter(
        [
            {"pressure": 1, "reclaimable_gib": 10, "swap_used_gib": 1},
            {"pressure": 2, "reclaimable_gib": 10, "swap_used_gib": 1},
        ]
    )
    monkeypatch.setattr(run_guard, "memory_sample", lambda: next(samples))
    args = options(tmp_path, [sys.executable, "-c", "import time; time.sleep(30)"])
    assert run_guard.run_guarded(args) == 1
    assert json.loads((args.output / "status.json").read_text())["status"] == "resource_abort"


def test_timeout_stops_real_child(tmp_path, monkeypatch):
    sample = {"pressure": 1, "reclaimable_gib": 10, "swap_used_gib": 1}
    monkeypatch.setattr(run_guard, "memory_sample", lambda: sample)
    args = options(tmp_path, [])
    args.timeout_seconds = 0.01
    process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"], start_new_session=True)
    try:
        assert run_guard.monitor(process, io.StringIO(), sample, args)[0] == "timeout"
    finally:
        run_guard.terminate_group(process)
    assert process.poll() is not None


def test_cli_uses_shared_exclusive_lock(tmp_path, monkeypatch):
    lock = tmp_path / "lock"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "guard",
            "--output",
            str(tmp_path / "run"),
            "--lock",
            str(lock),
            "--required-gib",
            "1",
            "--",
            "example",
        ],
    )

    def check(args):
        assert args.command == ["example"]
        with lock.open("a") as second:
            with pytest.raises(BlockingIOError):
                run_guard.fcntl.flock(second, run_guard.fcntl.LOCK_EX | run_guard.fcntl.LOCK_NB)
        return 0

    monkeypatch.setattr(run_guard, "run_guarded", check)
    with pytest.raises(SystemExit) as stopped:
        run_guard.main()
    assert stopped.value.code == 0


def test_failed_monitor_is_not_recorded_as_running(tmp_path, monkeypatch):
    sample = {"pressure": 1, "reclaimable_gib": 10, "swap_used_gib": 1}
    monkeypatch.setattr(run_guard, "memory_sample", lambda: sample)

    def broken(*args):
        raise RuntimeError("Cannot monitor memory")

    monkeypatch.setattr(run_guard, "monitor", broken)
    args = options(tmp_path, [sys.executable, "-c", "import time; time.sleep(30)"])
    with pytest.raises(RuntimeError, match="Cannot monitor"):
        run_guard.run_guarded(args)
    assert json.loads((args.output / "status.json").read_text())["status"] == "interrupted_or_monitor_failed"
