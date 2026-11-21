"""Download and hash-check the public corpus; initialize external run directories."""

import hashlib
import shutil
from pathlib import Path

import requests

from pdf_heading_benchmark.io import REPO, read_json, write_json


def verify(path: Path, expected: str) -> None:
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(
            f"SHA256 mismatch: {path}; source may have changed. Do not silently update the benchmark."
        )


def prepare(root: Path) -> None:
    manifest = read_json(REPO / "configs/corpus.json")
    for folder in ("corpus", "reference", "results", "models", "logs", "vendor"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    for name in ("gold.json", "audit_pages.json"):
        shutil.copyfile(REPO / "configs" / name, root / "reference" / name)
    for item in manifest:
        path = root / "corpus" / f"{item['id']}.pdf"
        if not path.exists():
            response = requests.get(item["url"], timeout=120)
            response.raise_for_status()
            temporary = path.with_suffix(".download")
            temporary.write_bytes(response.content)
            verify(temporary, item["sha256"])
            temporary.replace(path)
        verify(path, item["sha256"])
        item["path"] = str(path)
        (root / "results" / item["id"]).mkdir(parents=True, exist_ok=True)
    write_json(root / "corpus/manifest.json", manifest)
