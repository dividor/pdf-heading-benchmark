"""Frozen corpus, safe archive extraction and explicit page-level annotations."""

import csv
import hashlib
import json
import re
import tarfile
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def document_key(url: str) -> str:
    match = re.search(r"WFP-\d+", url)
    return match[0] if match else url.split("?")[0]


def validate_corpus(records: list[dict], excluded: list[dict]) -> None:
    """Reject overlap by ID, checksum or WFP document identifier."""
    seen: dict[str, set] = {key: set() for key in ("id", "sha256", "url")}
    forbidden = {key: {document_key(r[key]) if key == "url" else r[key] for r in excluded} for key in seen}
    for record in records:
        if record["split"] not in {"train", "validation", "test"}:
            raise ValueError("Unknown split")
        for key in seen:
            value = document_key(record[key]) if key == "url" else record[key]
            if value in seen[key] or value in forbidden[key]:
                raise ValueError(f"Duplicate or excluded document: {record['id']} ({key})")
            seen[key].add(value)
        pages = record["review_pages"]
        if not pages or len(set(pages)) != len(pages) or not all(1 <= p <= record["pages"] for p in pages):
            raise ValueError("Invalid review pages")


def extract_archive(archive: Path, records: list[dict], destination: Path) -> None:
    """Read exact regular-file members; never unpack archive paths or links."""
    wanted = {r["member"]: r for r in records}
    found = set()
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:*") as source:
        for member in source:
            if member.name not in wanted:
                continue
            record = wanted[member.name]
            if not member.isfile() or member.name in found or member.size != record["size"]:
                raise ValueError(f"Unexpected archive member: {member.name}")
            stream = source.extractfile(member)
            if stream is None:
                raise ValueError(f"Unreadable member: {member.name}")
            data = stream.read()
            if hashlib.sha256(data).hexdigest() != record["sha256"]:
                raise ValueError(f"Checksum mismatch: {member.name}")
            target = destination / f"wfp-{int(record['id'])}.pdf"
            target.write_bytes(data)
            found.add(member.name)
    if found != set(wanted):
        raise ValueError(f"Missing archive members: {set(wanted) - found}")


def read_labels(path: Path) -> list[dict]:
    with path.open(newline="") as stream:
        return [
            {
                "report_id": int(r["report_id"]),
                "level": int(r["level"]),
                "line_ids": r["line_ids"].split("+"),
                "note": r["note"],
            }
            for r in csv.DictReader(stream, delimiter="\t")
        ]


def label_map(record: dict, lines: list[dict], annotations: list[dict]) -> dict[str, int]:
    """Only inspected pages have negatives. Uninspected pages have no labels."""
    selected = {line["id"]: 0 for line in lines if line["page"] in record["review_pages"]}
    assigned = set()
    for annotation in annotations:
        if annotation["report_id"] != record["id"]:
            continue
        if annotation["level"] not in range(1, 7):
            raise ValueError("Invalid heading level")
        for line_id in annotation["line_ids"]:
            if line_id not in selected or line_id in assigned:
                raise ValueError(f"Unknown, unreviewed or duplicate label: {record['id']}/{line_id}")
            selected[line_id] = annotation["level"]
            assigned.add(line_id)
    return selected
