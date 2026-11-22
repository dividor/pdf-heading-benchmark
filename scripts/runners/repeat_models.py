"""Repeat seven MLX configurations sequentially, preserving all earlier evidence.

Use the pinned MLX environment. Inputs and models must already be available.
The output directory must not exist. Telemetry is system-wide, not per-process.
"""

import argparse
import hashlib
import json
import os
import plistlib
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNNERS = REPO / "scripts/runners"
ORDER = [
    "qwen36_35b_compact",
    "qwen36_35b_visual_memory",
    "chandra2_mlx",
    "lighton4b_mlx",
    "lighton_mlx",
    "qwen36_27b_compact",
    "qwen36_visual_memory",
]


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def read(path):
    return json.loads(path.read_text())


def capture(command):
    result = subprocess.run(command, capture_output=True, check=False)
    return result.stdout.decode(errors="replace")


def telemetry():
    raw = capture(["/usr/sbin/ioreg", "-a", "-r", "-c", "IOAccelerator"])
    devices = plistlib.loads(raw.encode()) if raw else []
    return dict(
        at=datetime.now(UTC).isoformat(),
        load_average=os.getloadavg(),
        gpu=[d.get("PerformanceStatistics", {}) for d in devices],
        swap=capture(["/usr/sbin/sysctl", "-n", "vm.swapusage"]).strip(),
        vm_stat=capture(["/usr/bin/vm_stat"]),
        thermal=capture(["/usr/bin/pmset", "-g", "therm"]).strip(),
    )


def prepare(args):
    args.output.mkdir(parents=True, exist_ok=False)
    root = args.output / "inputs"
    root.mkdir()
    for name in ("corpus", "vendor"):
        (root / name).symlink_to(args.input_data / name, target_is_directory=True)
    (root / "reference").mkdir()
    (root / "reference/audit_pages.json").write_bytes((REPO / "configs/audit_pages.json").read_bytes())
    (root / "models").mkdir()
    for name, pin in read(REPO / "configs/models.json").items():
        if "repo" not in pin:
            continue
        record = args.input_data / "models" / f"download-{name}.json"
        if not record.exists():
            record = args.extra_models / f"download-{name}.json"
        if not record.exists():
            continue
        source = read(record)
        if any(source[k] != pin[k] for k in ("repo", "revision")):
            raise ValueError(f"Model pin mismatch: {name}")
        (root / "models" / record.name).write_bytes(record.read_bytes())
    for key in read(REPO / "configs/audit_pages.json"):
        dest = root / "results" / key
        dest.mkdir(parents=True)
        for name in ("pymupdf4llm.headings.json", "pdf_tags_full_context.json"):
            (dest / name).write_bytes((args.input_data / "results" / key / name).read_bytes())
    return root


def command(method, root, output):
    record = root / "models/download-Qwen3.6-35B-A3B-4bit.json"
    if method.endswith("compact"):
        model = "Qwen3.6-27B-4bit" if "27b" in method else "Qwen3.6-35B-A3B-4bit"
        return [
            "run_qwen_compact.py",
            "--input-data",
            str(root),
            "--model",
            model,
            "--model-record",
            str(root / f"models/download-{model}.json"),
            "--output",
            str(output),
        ]
    if method == "qwen36_35b_visual_memory":
        return [
            "run_qwen_sparse_memory.py",
            "--input-data",
            str(root),
            "--model-record",
            str(record),
            "--output",
            str(output),
        ]
    return {
        "qwen36_visual_memory": ["run_qwen_visual_memory.py"],
        "chandra2_mlx": ["run_chandra_batch.py", "chandra2"],
        "lighton4b_mlx": ["run_chandra_batch.py", "lighton4b"],
        "lighton_mlx": ["run_lighton_mlx.py"],
    }[method]


def worker():
    import importlib.metadata

    import mlx.core as mx

    if mx.default_device() != mx.gpu or not mx.metal.is_available():
        raise RuntimeError("This repeat requires the Metal GPU; refusing CPU fallback")
    path, *arguments = sys.argv[2:]
    write(
        Path(os.environ["REPEAT_DEVICE_RECORD"]),
        dict(
            default_device=str(mx.default_device()),
            device_info=mx.device_info(),
            packages={
                n: importlib.metadata.version(n)
                for n in ("mlx", "mlx-vlm", "transformers", "pymupdf", "pillow", "huggingface-hub")
            },
        ),
    )
    import runpy

    sys.argv = [path, *arguments]
    runpy.run_path(path, run_name="__main__")


def run_one(method, root, args, environment):
    target = args.output / method
    target.mkdir()
    arguments = command(method, root, target / "run")
    argv = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker",
        str(RUNNERS / arguments[0]),
        *arguments[1:],
    ]
    environment["REPEAT_DEVICE_RECORD"] = str(target / "device.json")
    before = telemetry()
    start = time.perf_counter()
    with (target / "run.log").open("w") as log, (target / "telemetry.jsonl").open("w") as samples:
        process = subprocess.Popen(argv, env=environment, stdout=log, stderr=subprocess.STDOUT)
        while process.poll() is None:
            samples.write(json.dumps(telemetry()) + "\n")
            samples.flush()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
    write(
        target / "execution.json",
        dict(
            method=method,
            command=arguments,
            exit_code=process.returncode,
            process_wall_seconds=time.perf_counter() - start,
            before=before,
            after=telemetry(),
        ),
    )
    print("FINISHED", method, process.returncode, round(time.perf_counter() - start, 1), flush=True)
    if process.returncode:
        raise RuntimeError(f"Run failed; queue stopped: {method}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-data", type=Path, required=True)
    parser.add_argument("--extra-models", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = prepare(args)
    sources = [*RUNNERS.glob("*.py"), REPO / "src/pdf_heading_benchmark/compact_prompt.py"]
    write(
        args.output / "protocol.json",
        dict(
            created_at=datetime.now(UTC).isoformat(),
            order=ORDER,
            source_sha256={
                str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources
            },
            audit_pages=read(REPO / "configs/audit_pages.json"),
            input_sha256={
                str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.rglob("*.json")
            },
            pdf_sha256={
                p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (root / "corpus").glob("*.pdf")
            },
            note="One fresh process at a time; same prompts/settings. LightOn 4B uses batch two throughout; "
            "historical result mixed single pages and batches. GPU samples are system-wide. "
            "Process wall time includes loading/preparation/writes; page timers retain original boundaries.",
        ),
    )
    environment = dict(
        os.environ, PDF_BENCHMARK_DATA=str(root), PYTHONPATH=str(REPO / "src"), HF_HUB_OFFLINE="1"
    )
    for method in ORDER:
        print("STARTING", method, flush=True)
        run_one(method, root, args, environment)
    write(args.output / "completed.json", dict(completed_at=datetime.now(UTC).isoformat(), methods=ORDER))


if __name__ == "__main__":
    if sys.argv[1:2] == ["--worker"]:
        worker()
    else:
        main()
