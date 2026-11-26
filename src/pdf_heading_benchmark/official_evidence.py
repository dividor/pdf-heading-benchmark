"""Validate complete upstream-pipeline runs and preserve their measured evidence."""

import hashlib
import json
import re
from pathlib import Path

from pdf_heading_benchmark.field_evidence import retention
from pdf_heading_benchmark.field_output import markdown_headings
from pdf_heading_benchmark.io import REPO, read_json


def validate_run(protocol: dict, timing: dict, data: Path) -> None:
    if protocol["smoke"] or protocol["pages"] != read_json(REPO / "configs/audit_pages.json"):
        raise ValueError("Only a complete fixed audit run can be scored")
    if timing["pages"] != 32 or timing["errors"] != 0 or timing["seconds"] <= 0:
        raise ValueError("Incomplete run or invalid timing")
    for item in read_json(REPO / "configs/corpus.json"):
        digest = hashlib.sha256((data / "corpus" / f"{item['id']}.pdf").read_bytes()).hexdigest()
        if digest != item["sha256"] or digest != protocol["input_sha256"][item["id"]]:
            raise ValueError(f"PDF checksum mismatch: {item['id']}")


def validate_execution_source(run: Path, protocol: dict) -> None:
    hashes = protocol["source_sha256"]
    if len(hashes) != 1:
        raise ValueError("Expected one archived execution source")
    digest = hashlib.sha256((run / "runner.py").read_bytes()).hexdigest()
    if digest != next(iter(hashes.values())):
        raise ValueError("Archived execution source differs from the run protocol")


def public_protocol(protocol: dict, data: Path) -> dict:
    """Keep reproducibility settings while removing machine-specific directory roots."""
    text = json.dumps(protocol).replace(str(data), "$DATA").replace(str(Path.home()), "$USER_HOME")
    text = re.sub(r'/Volumes/[^"\\\s]+/hub(?=/)', "$HF_HUB", text)
    result = json.loads(text)
    if "ollama_model" in result:
        model = result["ollama_model"]
        model["template_sha256"] = hashlib.sha256(model.pop("template").encode()).hexdigest()
    return result


def import_run(run: Path, data: Path) -> dict:
    protocol, timing = read_json(run / "protocol.json"), read_json(run / "timing.json")
    validate_run(protocol, timing, data)
    validate_execution_source(run, protocol)
    predictions = read_json(run / "predictions.json")
    if set(predictions) != set(protocol["pages"]):
        raise ValueError("Prediction documents do not match the protocol")
    pages, prose = {}, {}
    for document, selected in protocol["pages"].items():
        records = [read_json(run / document / f"{pn}.json") for pn in selected]
        if any(r["error"] for r in records) or [r["page"] for r in records] != selected:
            raise ValueError("Page errors or wrong pages")
        extracted = [h for r in records for h in markdown_headings(r["text"], r["page"])]
        if extracted != predictions[document]:
            raise ValueError("Saved headings differ from native Markdown")
        prose[document] = retention(data / "corpus" / f"{document}.pdf", records)
        pages[document] = [
            dict(
                **{k: v for k, v in r.items() if k not in ("text", "raw")},
                text_sha256=hashlib.sha256(r["text"].encode()).hexdigest(),
            )
            for r in records
        ]
    return dict(
        protocol=public_protocol(protocol, data),
        timing=timing,
        predictions=predictions,
        pages=pages,
        prose=prose,
    )
