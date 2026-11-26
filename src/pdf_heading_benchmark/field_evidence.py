"""Validation and text-retention measurements for local OCR field trials."""

import hashlib
import re
import unicodedata
from pathlib import Path

import pymupdf
from bs4 import BeautifulSoup

from pdf_heading_benchmark.io import REPO, read_json


def words(text: str) -> list[str]:
    text = BeautifulSoup(text, "html.parser").get_text(" ")
    text = re.sub(r"!\[[\w+]+\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"(\w)[\-\u2010]\s*\n\s*(\w)", r"\1\2", text)
    return re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", text).casefold())


def grams(text: str) -> set[tuple[str, ...]]:
    tokens = words(text)
    return {tuple(tokens[i : i + 5]) for i in range(len(tokens) - 4)}


def retention(pdf: Path, records: list[dict]) -> dict:
    retained = total = 0
    with pymupdf.open(pdf) as document:
        for record in records:
            paragraphs = [
                block[4]
                for block in document[record["page"] - 1].get_text("blocks")
                if block[6] == 0 and len(words(block[4])) >= 50
            ]
            body = set().union(*(grams(text) for text in paragraphs))
            retained += len(body & grams(record["text"]))
            total += len(body)
    return dict(retained=retained, total=total)


def validate_protocol(protocol: dict, key: str, data: Path) -> None:
    if protocol["smoke"] or protocol["pages"] != read_json(REPO / "configs/audit_pages.json"):
        raise ValueError("Only complete fixed audit runs can be imported")
    pins = read_json(REPO / "configs/field-candidates.json")["models"]
    if protocol["candidate"] != key or protocol["models"] != pins:
        raise ValueError("Candidate or model revisions differ")
    for name, checksum in protocol["source_sha256"].items():
        if hashlib.sha256((REPO / name).read_bytes()).hexdigest() != checksum:
            raise ValueError(f"Runner changed after run started: {name}")
    for item in read_json(REPO / "configs/corpus.json"):
        actual = hashlib.sha256((data / "corpus" / f"{item['id']}.pdf").read_bytes()).hexdigest()
        if actual != item["sha256"] or actual != protocol["input_sha256"][item["id"]]:
            raise ValueError(f"PDF checksum mismatch: {item['id']}")


def import_evidence(run: Path, key: str, data: Path) -> dict:
    protocol = read_json(run / "protocol.json")
    validate_protocol(protocol, key, data)
    predictions = read_json(run / "predictions.json")
    timing = read_json(run / "timing.json")
    if set(predictions) != set(protocol["pages"]) or timing["pages"] != 32 or timing["errors"]:
        raise ValueError("Incomplete run")
    pages, prose = {}, {}
    for document, selected in protocol["pages"].items():
        records = [read_json(run / document / f"{pn}.json") for pn in selected]
        if [r["page"] for r in records] != selected or any(r["error"] for r in records):
            raise ValueError(f"Invalid page records: {document}")
        if [h for record in records for h in record["headings"]] != predictions[document]:
            raise ValueError(f"Page predictions differ: {document}")
        prose[document] = retention(data / "corpus" / f"{document}.pdf", records)
        pages[document] = [{k: v for k, v in r.items() if k not in ("text", "regions")} for r in records]
    measured = sum(r["seconds"] for records in pages.values() for r in records)
    if abs(measured - timing["seconds"]) > 0.001:
        raise ValueError("Timing summary differs from page records")
    return dict(protocol=protocol, predictions=predictions, timing=timing, pages=pages, prose=prose)
