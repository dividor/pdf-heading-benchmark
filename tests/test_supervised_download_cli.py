"""Exercise the original model's public-data path through its actual CLI."""

import hashlib
import json
import subprocess
import sys

import pymupdf

from pdf_heading_benchmark.io import REPO, write_json


def test_supervised_prepare_accepts_verified_public_cache(tmp_path):
    config = tmp_path / "config" / "supervised"
    data = tmp_path / "data"
    pdf = data / "pdfs/wfp-1.pdf"
    pdf.parent.mkdir(parents=True)
    with pymupdf.open() as document:
        document.new_page().insert_text((72, 72), "Example body text")
        document.save(pdf)
    write_json(
        config / "corpus.json",
        [
            {
                "id": 1,
                "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
                "url": "https://example.invalid/report",
                "pages": 1,
                "review_pages": [1],
                "split": "train",
            }
        ],
    )
    write_json(config / "excluded.json", [])
    write_json(config.parent / "corpus.json", [])
    (config / "labels.tsv").write_text("report_id\tlevel\tline_ids\tnote\n")
    subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts/supervised/prepare.py"),
            "--download",
            "--config",
            str(config),
            "--data",
            str(data),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    dataset = json.loads((data / "dataset.json").read_text())
    assert len(dataset["rows"]) == 1
    assert dataset["rows"][0]["label"] == 0
    assert dataset["rows"][0]["report_id"] == 1
