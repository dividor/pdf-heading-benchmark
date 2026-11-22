"""Exact line-membership heading metrics on fully reviewed pages, never positive-only samples."""

import time

import numpy as np

from pdf_heading_benchmark.structure_inference import infer_lines
from pdf_heading_benchmark.supervised_models import metrics


def group_counts(gold: list[dict], predicted: list[dict]) -> dict:
    expected = {tuple(a["line_ids"]): a["level"] for a in gold}
    proposed = {tuple(a["line_ids"]): a["level"] for a in predicted}
    matched = expected.keys() & proposed.keys()
    correct = sum(expected[k] == proposed[k] for k in matched)
    return {"gold": len(expected), "predicted": len(proposed), "matched": len(matched), "correct": correct}


def summarize_counts(counts: dict) -> dict:
    denominator = counts["gold"] + counts["predicted"]
    return {
        **counts,
        "group_detection_f1": 2 * counts["matched"] / max(1, denominator),
        "group_level_f1": 2 * counts["correct"] / max(1, denominator),
        "correct_group_recall": counts["correct"] / max(1, counts["gold"]),
    }


def evaluate_documents(documents: list[dict], models: dict, variant: str) -> tuple[dict, list]:
    counts = dict.fromkeys(("gold", "predicted", "matched", "correct"), 0)
    all_gold, all_predicted, audits, per_document = [], [], [], {}
    start = time.perf_counter()
    for doc in documents:
        if not doc["record"]["review_pages"]:
            raise ValueError("Cannot score positive-only annotations as a complete reference")
        groups = infer_lines(doc["lines"], doc["rows"], models, variant)
        pages = set(doc["record"]["review_pages"])
        groups = [g for g in groups if g["page"] in pages]
        found = group_counts(doc["groups"], groups)
        per_document[str(doc["record"]["id"])] = summarize_counts(found)
        for key in counts:
            counts[key] += found[key]
        predicted = {key: a["level"] for a in groups for key in a["line_ids"]}
        for key, level in doc["labels"].items():
            all_gold.append(level)
            all_predicted.append(predicted.get(key, 0))
        audits.append({"report_id": doc["record"]["id"], "headings": groups})
    return {
        **summarize_counts(counts),
        "line_metrics": metrics(np.asarray(all_gold), np.asarray(all_predicted)),
        "per_document": per_document,
        "predict_seconds": time.perf_counter() - start,
        "timing_scope": "Full-document inference on cached extracted lines/features; excludes extraction",
    }, audits
