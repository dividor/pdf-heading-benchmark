"""Fetch exact model revisions and upstream helpers outside the checkout."""

import json
import runpy
import subprocess
import sys
from pathlib import Path

from huggingface_hub import snapshot_download
from runtime import ROOT

REPO = Path(__file__).resolve().parents[2]


def checkout(name, url, revision):
    target = ROOT / "vendor" / name
    if not target.exists():
        subprocess.run(["git", "clone", "--no-checkout", url, str(target)], check=True)
    subprocess.run(["git", "-C", str(target), "checkout", "--detach", revision], check=True)
    return target


def prepare(name):
    info = json.loads((REPO / "configs/models.json").read_text())[name]
    if name == "qwen_ids":
        (ROOT / "models/qwen_revision.json").write_text(json.dumps(info))
        snapshot_download(info["model"], revision=info["revision"])
        return
    path = snapshot_download(info["repo"], revision=info["revision"])
    if name == "popo":
        checkout(
            "MinerU-Popo",
            "https://github.com/opendatalab/MinerU-Popo.git",
            "8b9a8bd57ef3c785b45d7ed696fdadfbe7184992",
        )
        destination = ROOT / "models/popo-8bit"
        if not destination.exists():
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "mlx_vlm.convert",
                    "--hf-path",
                    path,
                    "--mlx-path",
                    str(destination),
                    "-q",
                    "--q-bits",
                    "8",
                    "--q-group-size",
                    "64",
                ],
                check=True,
            )
        return
    (ROOT / "models" / f"download-{name}.json").write_text(json.dumps(dict(**info, path=path)))
    if name in ("chandra-ocr-2", "LightOnOCR-3-4B"):
        chandra = checkout(
            "chandra", "https://github.com/datalab-to/chandra.git", "9c3a195573bec72b6e73cd66be099350ac11a4f5"
        )
        prompt = runpy.run_path(str(chandra / "chandra/prompts.py"))["OCR_LAYOUT_PROMPT"]
        (ROOT / "vendor/chandra_ocr_layout_prompt.txt").write_text(prompt.strip())


if __name__ == "__main__":
    prepare(sys.argv[1])
