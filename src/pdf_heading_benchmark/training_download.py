"""Download the exact public training PDFs recorded in the frozen manifest."""

from pathlib import Path

import requests

from pdf_heading_benchmark.corpus import verify
from pdf_heading_benchmark.structure_data import validate_records
from pdf_heading_benchmark.supervised_data import read_json


def download_training(config: Path, data: Path) -> None:
    records = read_json(config / "corpus.json")
    validate_records(records, read_json(config / "excluded.json"))
    directory = data / "pdfs"
    directory.mkdir(parents=True, exist_ok=True)
    for record in records:
        path = directory / f"wfp-{record['id']}.pdf"
        if path.exists():
            verify(path, record["sha256"])
            continue
        response = requests.get(record["url"], timeout=120)
        response.raise_for_status()
        temporary = path.with_suffix(".download")
        temporary.write_bytes(response.content)
        verify(temporary, record["sha256"])
        temporary.replace(path)
        print(f"Verified report {record['id']} ({record['split']})", flush=True)
