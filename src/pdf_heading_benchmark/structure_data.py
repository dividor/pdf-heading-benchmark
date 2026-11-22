"""Partial positive annotations plus explicit fully reviewed pages; no implicit negatives."""

import hashlib
from pathlib import Path

from pdf_heading_benchmark.supervised_data import document_key, read_json, write_json
from pdf_heading_benchmark.supervised_features import extract_lines, feature_rows


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def config_hashes(config: Path) -> dict:
    return {p.name: checksum(p) for p in sorted(config.glob("*.json"))}


def validate_records(records: list[dict], excluded: list[dict]) -> None:
    for key in ("id", "sha256", "url"):
        values = [document_key(r[key]) if key == "url" else r[key] for r in records]
        forbidden = {document_key(r[key]) if key == "url" else r[key] for r in excluded}
        if len(set(values)) != len(values) or set(values) & forbidden:
            raise ValueError(f"Duplicate or excluded document: {key}")
    for record in records:
        if record["split"] not in {"train", "validation", "test"}:
            raise ValueError("Unknown split")
        pages = record["review_pages"]
        if len(set(pages)) != len(pages) or any(p < 1 or p > record["pages"] for p in pages):
            raise ValueError("Invalid reviewed pages")
        if record["split"] != "train" and not pages:
            raise ValueError("Evaluation requires fully reviewed pages")


def known_labels(record: dict, lines: list[dict], groups: list[dict]) -> dict:
    labels = {line["id"]: 0 for line in lines if line["page"] in record["review_pages"]}
    available = {line["id"]: line for line in lines}
    assigned = set()
    for group in groups:
        if group["level"] not in range(1, 7):
            raise ValueError("Invalid level")
        parts = [available[key] for key in group["line_ids"]]
        if " ".join(p["text"] for p in parts) != group["text"]:
            raise ValueError("Annotation text differs from PDF extraction")
        for key in group["line_ids"]:
            if key in assigned:
                raise ValueError("Overlapping annotations")
            if record["split"] != "train" and key not in labels:
                raise ValueError("Evaluation annotation outside reviewed pages")
            assigned.add(key)
            labels[key] = group["level"]
    return labels


def prepare(config: Path, data: Path) -> None:
    records = read_json(config / "corpus.json")
    validate_records(records, read_json(config / "excluded.json"))
    annotations = read_json(config / "annotations.json")
    summaries = []
    for record in records:
        pdf = data / "pdfs" / f"wfp-{record['id']}.pdf"
        if checksum(pdf) != record["sha256"]:
            raise ValueError(f"Wrong PDF: {record['id']}")
        lines = extract_lines(pdf)
        rows, names = feature_rows(lines)
        groups = [a for a in annotations if a["report_id"] == record["id"]]
        labels = known_labels(record, lines, groups)
        write_json(
            data / "prepared" / f"{record['id']}.json",
            {
                "record": record,
                "lines": lines,
                "rows": rows,
                "features": names,
                "labels": labels,
                "groups": groups,
            },
        )
        summaries.append(
            {
                "id": record["id"],
                "split": record["split"],
                "groups": len(groups),
                "labelled_lines": len(labels),
                "reviewed_pages": len(record["review_pages"]),
            }
        )
    write_json(data / "dataset.json", {"config_hashes": config_hashes(config), "documents": summaries})


def load_documents(config: Path, data: Path, split: str) -> list[dict]:
    dataset = read_json(data / "dataset.json")
    if dataset["config_hashes"] != config_hashes(config):
        raise ValueError("Stale prepared dataset")
    return [
        read_json(data / "prepared" / f"{r['id']}.json") for r in dataset["documents"] if r["split"] == split
    ]


def load_model_bundle(run: Path, variant: str | None = None) -> tuple[dict, str]:
    selection = read_json(run / "selection.json")
    chosen = variant or selection["selected"]
    names = {
        "expanded_line": ["line"],
        "learned_groups": ["join", "group"],
        "context_relations": ["join", "context", "relation"],
    }[chosen]
    models = {}
    for name in names:
        path = run / f"{name}.json"
        if checksum(path) != selection["model_hashes"][name]:
            raise ValueError("Changed model")
        models[name] = read_json(path)
    return models, chosen
