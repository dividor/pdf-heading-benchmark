"""Fetch the recorded OCR weights and layout revision, checking exact file hashes."""

import argparse
import hashlib
import json
from pathlib import Path

import requests
from prepare_evidencelab_models import prepare


def fetch(url):
    response = requests.get(url, timeout=180)
    response.raise_for_status()
    return response.content


def prepare_ocr(config, model_dir, download):
    model_dir.mkdir(parents=True, exist_ok=True)
    for model in config["rapidocr"]:
        path = model_dir / model["name"]
        data = path.read_bytes() if path.exists() else download(model["url"])
        if hashlib.sha256(data).hexdigest() != model["sha256"]:
            raise ValueError(f"OCR weight hash differs: {model['name']}")
        if not path.exists():
            path.write_bytes(data)
    return config["rapidocr"]


def main():
    import rapidocr
    from huggingface_hub import constants, snapshot_download

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads((args.repo / "configs/docling-ocr-models.json").read_text())
    rapid_models = prepare_ocr(config, Path(rapidocr.__file__).parent / "models", fetch)
    layout = prepare(config, Path(constants.HF_HUB_CACHE), snapshot_download)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(dict(layout=layout, rapidocr=rapid_models), indent=2) + "\n")


if __name__ == "__main__":
    main()
