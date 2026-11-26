"""Import full-document parser outputs without repairing their headings or levels."""

import hashlib
import re
from pathlib import Path

from pdf_heading_benchmark.field_evidence import retention
from pdf_heading_benchmark.io import REPO, read_json


def toc_headings(text: str) -> list[dict]:
    pattern = re.compile(
        r"\s*(?:x\s+)?\[H(\d+|\?)\]\s*(.*?)\s*\|\s*page\s*(\d+|\?)(?:\s*\([^)]*\))?(?:\s*\[Front\])?\s*"
    )
    headings = []
    for line in text.splitlines():
        if not line.strip():
            continue
        match = pattern.fullmatch(line)
        if match is None:
            raise ValueError(f"Unrecognized EvidenceLab TOC entry: {line}")
        level, title, page = match.groups()
        headings.append(
            dict(
                title=title,
                level=None if level == "?" else int(level),
                page=None if page == "?" else int(page),
            )
        )
    return headings


def document_headings(document: dict) -> list[dict]:
    return [
        dict(
            title=item["text"], level=item["level"], page=item["prov"][0]["page_no"] if item["prov"] else None
        )
        for item in document["texts"]
        if item["label"] == "section_header"
    ]


def document_pages(document: dict, pages: list[int]) -> list[dict]:
    return [
        dict(
            page=page,
            text="\n".join(
                item["text"]
                for item in document["texts"]
                if item["prov"] and item["prov"][0]["page_no"] == page
            ),
        )
        for page in pages
    ]


def read_document(run: Path, key: str, method: str) -> tuple[dict, list[dict], dict]:
    hashes = {}
    if method == "evidencelab":
        result = read_json(run / f"{key}.result.json")
        if not result["success"]:
            raise ValueError("Parser reported failure")
        folder = run / "parsed/other" / key
        path = folder / f"{key}.json"
        toc = (folder / "toc.txt").read_text()
        predictions = toc_headings(toc)
        hashes[f"{key}.toc"] = hashlib.sha256(toc.encode()).hexdigest()
        document = read_json(path)
    else:
        path = run / f"{key}.document.json"
        document = read_json(path)
        predictions = document_headings(document)
    hashes[f"{key}.json"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return document, predictions, hashes


def import_pipeline(run: Path, data: Path, method: str) -> dict:
    if method not in {"evidencelab", "docling_ocr"}:
        raise ValueError("Unknown full-document pipeline")
    protocol, timings = read_json(run / "protocol.json"), read_json(run / "timing.json")
    digest = hashlib.sha256((run / "runner.py").read_bytes()).hexdigest()
    if protocol["source_sha256"] != digest:
        raise ValueError("Execution source changed")
    models = read_json(run / "model-files.json")
    expected = read_json(REPO / "configs" / f"{method.replace('_', '-')}-model-files.json")
    if models != expected:
        raise ValueError("Model file record differs from pinned configuration")
    corpus = read_json(REPO / "configs/corpus.json")
    if [t["document"] for t in timings] != [r["id"] for r in corpus]:
        raise ValueError("Incomplete or reordered document timings")
    audit = read_json(REPO / "configs/audit_pages.json")
    predictions, prose, files, json_predictions = {}, {}, {}, {}
    for record, timing in zip(corpus, timings, strict=True):
        key = record["id"]
        pdf = data / "corpus" / f"{key}.pdf"
        if hashlib.sha256(pdf.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError(f"Source PDF changed: {key}")
        if timing["pages"] != record["pages"] or timing["seconds"] <= 0:
            raise ValueError("Invalid page count or timing")
        if timing["input_sha256"] != record["sha256"]:
            raise ValueError("Run used a different PDF")
        document, native, hashes = read_document(run, key, method)
        files.update(hashes)
        if len(document["pages"]) != record["pages"]:
            raise ValueError("Incomplete parsed document")
        predictions[key] = native
        json_predictions[key] = document_headings(document)
        predictions[key] = [h for h in predictions[key] if h["page"] in audit[key]]
        prose[key] = retention(pdf, document_pages(document, audit[key]))
    return dict(
        protocol=protocol,
        model_files=models,
        predictions=predictions,
        prose=prose,
        timing=dict(seconds=sum(t["seconds"] for t in timings), pages=sum(t["pages"] for t in timings)),
        documents=timings,
        artifact_sha256=files,
        initialization=read_json(run / "initialization.json"),
        structured_headings={
            k: [h for h in heads if h["page"] in audit[k]] for k, heads in json_predictions.items()
        },
    )
