"""Download the pinned upstream weights and prompts for official-pipeline trials."""

import argparse
import json
from pathlib import Path

from huggingface_hub import snapshot_download

REPO = Path(__file__).resolve().parents[2]
FILES = {
    "ovisocr3": None,
    "minicpm_gguf": ["MiniCPM-OCR-1_0-Q8_0.gguf", "mmproj-model-f16-4x.gguf", "README.md"],
    "minicpm_dspark": ["dspark-MiniCPM-OCR-1_0-Q8_0.gguf", "README.md"],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", choices=FILES)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--records", required=True, type=Path)
    args = parser.parse_args()
    pin = json.loads((REPO / "configs/official-pipelines.json").read_text())["models"][args.model]
    path = snapshot_download(
        repo_id=pin["repo"],
        revision=pin["revision"],
        cache_dir=args.cache,
        allow_patterns=FILES[args.model],
        max_workers=3,
    )
    args.records.mkdir(parents=True, exist_ok=True)
    (args.records / f"{args.model}.download.json").write_text(
        json.dumps(dict(**pin, path=path), indent=2) + "\n"
    )
    print(path, flush=True)


if __name__ == "__main__":
    main()
