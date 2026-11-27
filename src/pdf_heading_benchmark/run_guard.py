"""Run one macOS experiment with recorded memory checks and process-group cleanup."""

import argparse
import fcntl
import json
import os
import re
import signal
import subprocess
import time
from pathlib import Path

GIB = 1024**3


def parse_memory(vm: str, swap: str, pressure: str) -> dict:
    page_match = re.search(r"page size of (\d+) bytes", vm)
    swap_match = re.search(r"used = ([\d.]+)M", swap)
    if page_match is None or swap_match is None:
        raise ValueError("Cannot read macOS memory statistics")
    page_size = int(page_match[1])
    pages = dict(re.findall(r"^(Pages [\w ]+):\s+(\d+)\.", vm, re.MULTILINE))
    reclaimable = sum(int(pages[key]) for key in ("Pages free", "Pages inactive", "Pages speculative"))
    return {
        "reclaimable_gib": reclaimable * page_size / GIB,
        "swap_used_gib": float(swap_match[1]) / 1024,
        "pressure": int(pressure.strip()),
    }


def memory_sample() -> dict:
    vm = subprocess.check_output(["/usr/bin/vm_stat"], text=True)
    swap = subprocess.check_output(["/usr/sbin/sysctl", "-n", "vm.swapusage"], text=True)
    pressure = subprocess.check_output(
        ["/usr/sbin/sysctl", "-n", "kern.memorystatus_vm_pressure_level"], text=True
    )
    return parse_memory(vm, swap, pressure)


def unsafe_reason(sample: dict, baseline: dict, reserve: float, swap_growth: float) -> str | None:
    if sample["pressure"] != 1:
        return "macOS memory pressure is not normal"
    if sample["reclaimable_gib"] < reserve:
        return "Free, inactive and speculative memory fell below the reserve"
    if sample["swap_used_gib"] - baseline["swap_used_gib"] > swap_growth:
        return "Host swap use grew beyond the allowed amount"
    return None


def terminate_group(process: subprocess.Popen) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=10)


def monitor(process: subprocess.Popen, telemetry, baseline: dict, args) -> tuple[str, str | None]:
    started = time.monotonic()
    while process.poll() is None:
        sample = memory_sample()
        sample["elapsed_seconds"] = time.monotonic() - started
        telemetry.write(json.dumps(sample) + "\n")
        telemetry.flush()
        reason = unsafe_reason(sample, baseline, args.reserve_gib, args.swap_growth_gib)
        if reason:
            return "resource_abort", reason
        if sample["elapsed_seconds"] > args.timeout_seconds:
            return "timeout", "The configured wall-clock limit was reached"
        time.sleep(args.interval_seconds)
    return ("completed" if process.returncode == 0 else "failed"), None


def run_guarded(args) -> int:
    args.output.mkdir(parents=True, exist_ok=False)
    baseline = memory_sample()
    record = {"command": args.command, "cwd": str(Path.cwd()), "baseline": baseline, "status": "preflight"}
    record["environment"] = {
        key: os.environ[key]
        for key in (
            "PDF_BENCHMARK_DATA",
            "PDF_HEADING_MODEL",
            "PDF_HEADING_STRUCTURE_RUN",
            "PDF_HEADING_PRECISION_RUN",
            "PDF_HEADING_CALIBRATION",
            "PDF_HEADING_RECALL_RUN",
            "UV_CACHE_DIR",
            "UV_PROJECT_ENVIRONMENT",
            "HF_HOME",
            "XDG_CACHE_HOME",
            "PATH",
        )
        if key in os.environ
    }
    record["limits"] = {key: value for key, value in vars(args).items() if key not in {"command", "output"}}
    record["limits"]["lock"] = str(args.lock)
    status_file = args.output / "status.json"
    started = time.monotonic()
    try:
        reason = unsafe_reason(baseline, baseline, args.reserve_gib + args.required_gib, args.swap_growth_gib)
        if reason:
            record.update(status="resource_blocked", reason=reason)
            return 75
        with (
            (args.output / "console.log").open("w") as console,
            (args.output / "memory.jsonl").open("w") as log,
        ):
            process = subprocess.Popen(
                args.command, stdout=console, stderr=subprocess.STDOUT, start_new_session=True
            )
            record.update(status="running", pid=process.pid)
            status_file.write_text(json.dumps(record, indent=2) + "\n")
            try:
                status, reason = monitor(process, log, baseline, args)
                record.update(status=status, reason=reason, returncode=process.returncode)
            finally:
                terminate_group(process)
                record["returncode"] = process.returncode
        return 0 if record["status"] == "completed" else 1
    except BaseException:
        record["status"] = "interrupted_or_monitor_failed"
        raise
    finally:
        record["elapsed_seconds"] = time.monotonic() - started
        status_file.write_text(json.dumps(record, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True, help="One shared lock for all experiment runs")
    parser.add_argument(
        "--required-gib", type=float, required=True, help="Preflight headroom beyond the reserve"
    )
    parser.add_argument("--reserve-gib", type=float, default=6)
    parser.add_argument("--swap-growth-gib", type=float, default=0.5)
    parser.add_argument("--interval-seconds", type=float, default=2)
    parser.add_argument("--timeout-seconds", type=float, default=21600)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.command[:1] == ["--"]:
        args.command = args.command[1:]
    if not args.command or min(args.interval_seconds, args.timeout_seconds) <= 0:
        parser.error("Supply a command and positive interval and timeout")
    if min(args.required_gib, args.reserve_gib, args.swap_growth_gib) < 0:
        parser.error("Memory limits cannot be negative")
    args.lock.parent.mkdir(parents=True, exist_ok=True)
    with args.lock.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        raise SystemExit(run_guarded(args))


if __name__ == "__main__":
    main()
