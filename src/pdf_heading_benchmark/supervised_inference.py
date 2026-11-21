"""Preserve extracted text and attach predicted headings and tentative parents."""

import hashlib
import time
from pathlib import Path

import numpy as np

from pdf_heading_benchmark.supervised_features import extract_lines, feature_rows, matrix
from pdf_heading_benchmark.supervised_models import predict_proba


def heading_groups(lines: list[dict]) -> list[dict]:
    groups: list[dict] = []
    previous = None
    for line in lines:
        if line["level"] == 0:
            previous = None
            continue
        same_block = previous and previous["id"].split("l")[0] == line["id"].split("l")[0]
        if same_block and groups[-1]["level"] == line["level"]:
            groups[-1]["text"] += " " + line["text"]
            groups[-1]["line_ids"].append(line["id"])
            groups[-1]["bboxes"].append(line["bbox"])
        else:
            groups.append(
                {
                    "id": line["id"],
                    "page": line["page"],
                    "text": line["text"],
                    "level": line["level"],
                    "line_ids": [line["id"]],
                    "bboxes": [line["bbox"]],
                }
            )
        previous = line
    stack: list[dict] = []
    for group in groups:
        while stack and stack[-1]["level"] >= group["level"]:
            stack.pop()
        group["parent_id"] = stack[-1]["id"] if stack else None
        group["level_jump"] = group["level"] != (stack[-1]["level"] + 1 if stack else 1)
        stack.append(group)
    return groups


def parse_document(pdf: Path, model: dict) -> dict:
    start = time.perf_counter()
    lines = extract_lines(pdf)
    rows, names = feature_rows(lines)
    if names != model["features"]:
        raise ValueError("Model feature schema does not match this extractor")
    prepared = time.perf_counter()
    probabilities = predict_proba(model, matrix(rows, names))
    predicted = np.asarray(model["classes"])[probabilities.argmax(axis=1)]
    classified = time.perf_counter()
    for line, level, confidence in zip(lines, predicted, probabilities.max(axis=1), strict=True):
        line.update(level=int(level), confidence=float(confidence))
    return {
        "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "lines": lines,
        "headings": heading_groups(lines),
        "parent_status": "inferred from predicted levels; not evaluated",
        "confidence_status": "uncalibrated classifier score",
        "extract_and_feature_seconds": prepared - start,
        "predict_seconds": classified - prepared,
        "total_seconds": time.perf_counter() - start,
    }


def markdown_text(result: dict) -> str:
    """A readable line-preserving view; not a table or reading-order reconstruction."""
    headings = {g["line_ids"][0]: g for g in result["headings"]}
    continuation = {key for g in result["headings"] for key in g["line_ids"][1:]}
    output = []
    page = 0
    for line in result["lines"]:
        if line["page"] != page:
            page = line["page"]
            output.append(f"\n<!-- PDF page {page} -->\n")
        if line["id"] in headings:
            group = headings[line["id"]]
            output.append(f"\n{'#' * group['level']} {group['text']}\n")
        elif line["id"] not in continuation:
            output.append(line["text"])
    return "\n".join(output) + "\n"
