"""Rebuild the field snapshot from the exact publisher commit recorded in its manifest."""

import argparse
from pathlib import Path

import requests

from pdf_heading_benchmark.field_data import parse_source
from pdf_heading_benchmark.io import REPO, read_json, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Use a saved README instead of downloading it")
    parser.add_argument("--output", type=Path, default=REPO / "configs/field-overview.json")
    args = parser.parse_args()
    pin = read_json(REPO / "configs/field-overview-source.json")
    if args.source:
        source = args.source.read_text()
    else:
        url = f"https://raw.githubusercontent.com/datalab-to/omni_parse_bench/{pin['revision']}/README.md"
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        source = response.text
    data = parse_source(source, pin["revision"], pin["retrieved"])
    if data["source_sha256"] != pin["sha256"]:
        raise ValueError("Publisher source checksum does not match the recorded snapshot")
    write_json(args.output, data)
    print(
        f"{len(data['rows'])} with layout; {len(data['text_only'])} without; {len(data['pending'])} pending"
    )


if __name__ == "__main__":
    main()
