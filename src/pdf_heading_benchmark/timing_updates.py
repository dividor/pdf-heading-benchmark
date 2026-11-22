"""Use rerun timings only when they reproduce the displayed quality evidence."""

from pdf_heading_benchmark.io import REPO, read_json

FIELDS = ("page", "title", "level")
COUNTS = ("gold", "predicted", "matched", "correct_level")


def canonical(documents: dict) -> dict:
    """Bounding boxes and parser metadata do not change the scored predictions."""
    return {
        doc: [{field: heading[field] for field in FIELDS} for heading in heads]
        for doc, heads in documents.items()
    }


def update_timing(row: dict, repeat: dict, historical: dict, predictions: dict) -> dict:
    if any(repeat.get(field, 0) for field in ("errors", "timeouts", "token_caps")):
        return {**row, "timing_source": "historical; rerun has errors or truncation (see comparison)"}
    if canonical(historical) != canonical(predictions):
        return {**row, "timing_source": "historical; rerun predictions differ (see comparison)"}
    if row["processed_pages"] != repeat["processed_pages"]:
        raise ValueError("Rerun timing has a different page scope")
    if any(row[field] != repeat[field] for field in COUNTS):
        raise ValueError("Identical predictions cannot have different heading counts")
    return {
        **row,
        "measured_seconds": repeat["seconds"],
        "processed_pages": repeat["processed_pages"],
        "timing_source": "sequential rerun",
        "timing_evidence": f"outputs/sequential-repeat/evidence/{row['method']}.json",
    }


def latest_timings(rows: list[dict]) -> list[dict]:
    path = REPO / "outputs/sequential-repeat/results.json"
    if not path.exists():
        return rows
    repeats = {row["method"]: row for row in read_json(path)}
    historical = read_json(REPO / "outputs/audit_predictions.json")
    updated = []
    for row in rows:
        method = row["method"]
        if method in repeats:
            evidence = read_json(REPO / "outputs/sequential-repeat/evidence" / f"{method}.json")
            row = update_timing(row, repeats[method], historical[method], evidence["predictions"])
        updated.append(row)
    return updated
