"""Large private inputs and weights are ignored; compact audit evidence stays trackable."""

import subprocess

from pdf_heading_benchmark.io import REPO


def test_generated_data_and_weights_are_ignored():
    ignored = [
        "data/example.json",
        "pdf-heading-benchmark-data/prepared/report.json",
        "runs/new/document.json",
        "rebuilds/example/selection.json",
        "corpus/report.pdf",
        "downloaded.pdf",
        "model.safetensors",
        "model.gguf",
        "model.onnx",
        "model.pt",
        "model.joblib",
        "archive.tar",
        "train/join.json",
        "train/context.json",
        "train/relation.json",
        "train/group.json",
        "train/line.json",
        "train/trees.json",
    ]
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--stdin"],
        cwd=REPO,
        input="\n".join(ignored) + "\n",
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout.splitlines() == ignored
    evidence = [
        "configs/gold.json",
        "outputs/structure-precision/evidence/selection.json",
        "notebooks/rebuild_heading_model.ipynb",
    ]
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--stdin"],
        cwd=REPO,
        input="\n".join(evidence) + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert result.stdout == ""
