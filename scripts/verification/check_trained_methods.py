"""Run every trained-model table configuration after a fresh notebook rebuild."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from pdf_heading_benchmark.cli import run_method
from pdf_heading_benchmark.io import REPO, read_json


def check(data: Path, rebuild: Path) -> None:
    training = data / "training-verification"
    models = rebuild / "models"
    commands = [
        [
            "scripts/structure/calibrate.py",
            "select",
            "--data",
            str(data / "structure-v2"),
            "--run",
            str(models),
            "--output",
            str(training / "calibration"),
        ],
        [
            "scripts/structure/retrain_recall.py",
            "--data",
            str(data / "structure-v2"),
            "--output",
            str(training / "recall"),
        ],
        ["scripts/supervised/prepare.py", "--download", "--data", str(training / "supervised")],
        [
            "scripts/supervised/train.py",
            "--data",
            str(training / "supervised"),
            "--output",
            str(training / "supervised-models"),
        ],
    ]
    for command in commands:
        subprocess.run([sys.executable, *command], check=True, cwd=REPO)
    selected = read_json(training / "supervised-models/selection.json")["selected"]
    if selected != "trees":
        raise ValueError("The fresh original-model selection differs from the published Extra Trees method")
    os.environ.update(
        {
            "PDF_HEADING_MODEL": str(training / "supervised-models/trees.json"),
            "PDF_HEADING_STRUCTURE_RUN": str(models),
            "PDF_HEADING_PRECISION_RUN": str(rebuild / "precision"),
            "PDF_HEADING_CALIBRATION": str(training / "calibration"),
            "PDF_HEADING_RECALL_RUN": str(training / "recall"),
        }
    )
    methods = [
        "supervised_extra_trees",
        "structure_expanded_line",
        "structure_learned_groups",
        "structure_context_relations",
        "structure_calibrated",
        "structure_precision",
        "structure_recall",
    ]
    for method in methods:
        print("RUN", method, flush=True)
        run_method(method, data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument(
        "--rebuild", required=True, type=Path, help="Completed notebook run with models/ and precision/"
    )
    args = parser.parse_args()
    check(args.data.resolve(), args.rebuild.resolve())


if __name__ == "__main__":
    main()
