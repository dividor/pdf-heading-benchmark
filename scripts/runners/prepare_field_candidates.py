"""Download the declared model revisions outside Git; no inference or cloud parsing."""

import argparse
import json
from pathlib import Path

from huggingface_hub import snapshot_download

REPO = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--records", type=Path, required=True)
    args = parser.parse_args()
    args.records.mkdir(parents=True, exist_ok=True)
    pins = json.loads((REPO / "configs/field-candidates.json").read_text())["models"]
    for pin in pins.values():
        path = snapshot_download(
            repo_id=pin["repo"],
            revision=pin["revision"],
            cache_dir=args.cache,
            ignore_patterns=["*.md", "*.png", "*.jpg", "*.pdf", "*.bin", "*.gguf"],
            max_workers=3,
        )
        record = args.records / (pin["repo"].split("/")[-1] + ".download.json")
        record.write_text(json.dumps(dict(**pin, path=path), indent=2) + "\n")
        print(pin["repo"], pin["revision"], flush=True)


if __name__ == "__main__":
    main()
