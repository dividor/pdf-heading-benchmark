"""Run the pinned EvidenceLab image in isolation, with no service credentials or database."""

import argparse
import shutil
import subprocess
from pathlib import Path

from pdf_heading_benchmark.io import REPO, read_json


def docker_command(data: Path, output: Path) -> list[str]:
    config = read_json(REPO / "configs/evidencelab.json")
    if "@sha256:" not in config["image"]:
        raise ValueError("EvidenceLab image must be pinned by digest")
    return [
        "docker",
        "run",
        "--rm",
        "--platform",
        config["platform"],
        "--cpus",
        str(config["cpus"]),
        "--memory",
        "12g",
        "-e",
        "HF_HOME=/cache/huggingface",
        "-e",
        "HF_HUB_OFFLINE=1",
        "-e",
        f"OMP_NUM_THREADS={config['cpus']}",
        "-e",
        "PYTHONPATH=/app",
        "-v",
        f"{REPO}:/benchmark:ro",
        "-v",
        f"{data / 'corpus'}:/corpus:ro",
        "-v",
        f"{output.parent}:/run-output",
        "-v",
        f"{output.parent / 'cache'}:/cache",
        config["image"],
        "python",
        "/run-output/runner.py",
        "--repo",
        "/benchmark",
        "--corpus",
        "/corpus",
        "--output",
        f"/run-output/{output.name}",
    ]


def run(data: Path, output: Path) -> None:
    if output.exists():
        raise ValueError("Choose a fresh output directory")
    (output.parent / "cache").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPO / "scripts/runners/run_evidencelab.py", output.parent / "runner.py")
    command = docker_command(data, output)
    image_index = command.index(read_json(REPO / "configs/evidencelab.json")["image"])
    preparation = [
        *command[: image_index + 1],
        "python",
        "/benchmark/scripts/runners/prepare_evidencelab_models.py",
    ]
    preparation[preparation.index("HF_HUB_OFFLINE=1")] = "HF_HUB_OFFLINE=0"
    subprocess.run(preparation, check=True)
    with output.with_suffix(".log").open("x") as log:
        subprocess.run(docker_command(data, output), stdout=log, stderr=subprocess.STDOUT, check=True)
    shutil.copyfile(output.parent / "model-files.json", output / "model-files.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.data.resolve(), args.output.resolve())
