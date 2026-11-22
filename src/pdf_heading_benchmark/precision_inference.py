"""Confidence-filtered inference using frozen v2 trees; no reference labels as inputs."""

import time
from itertools import pairwise
from pathlib import Path

import numpy as np

from pdf_heading_benchmark.structure_features import (
    context_index,
    group_features,
    pair_features,
    with_context,
)
from pdf_heading_benchmark.structure_inference import attach_parents, decode_levels, learned_components
from pdf_heading_benchmark.supervised_features import extract_lines, feature_rows, matrix
from pdf_heading_benchmark.supervised_models import predict_proba


def prepare_candidates(lines: list[dict], rows: list[dict], models: dict, variant: str) -> dict:
    if variant not in {"learned_groups", "context_relations"}:
        raise ValueError("Unsupported precision variant")
    components = learned_components(rows, models["join"])
    context = context_index(lines)
    groups = [group_features(g, lines, rows, context) for g in components]
    inputs = [with_context(g) for g in groups] if variant == "context_relations" else groups
    model = models["context" if variant == "context_relations" else "group"]
    probabilities = predict_proba(model, matrix(inputs, model["features"])) if inputs else np.empty((0, 6))
    return {
        "components": components,
        "inputs": inputs,
        "probabilities": probabilities,
        "classes": model["classes"],
    }


def select_levels(probabilities: np.ndarray, classes: list, settings: dict) -> tuple:
    if settings["body_weight"] <= 0 or not 0 <= settings["min_heading_score"] <= 1:
        raise ValueError("Invalid decision settings")
    decision = probabilities.copy()
    decision[:, classes.index(0)] *= settings["body_weight"]
    levels = np.asarray(classes)[decision.argmax(axis=1)]
    heading_columns = [i for i, label in enumerate(classes) if label > 0]
    confident = probabilities[:, heading_columns].max(axis=1) >= settings["min_heading_score"]
    selected = np.flatnonzero((levels > 0) & confident)
    return levels, selected


def predict_candidates(lines: list[dict], cached: dict, models: dict, settings: dict) -> list[dict]:
    if not cached["inputs"]:
        return []
    probabilities, classes = cached["probabilities"], cached["classes"]
    levels, selected = select_levels(probabilities, classes, settings)
    weight = settings["relation_weight"]
    if weight < 0:
        raise ValueError("Negative relationship weight")
    if settings["variant"] == "context_relations" and weight and len(selected) > 1:
        inputs = cached["inputs"]
        pairs = [pair_features(inputs[a], inputs[b]) for a, b in pairwise(selected)]
        model = models["relation"]
        relations = predict_proba(model, matrix(pairs, model["features"]))
        columns = [i for i, label in enumerate(classes) if label > 0]
        levels[selected] = decode_levels(
            probabilities[selected][:, columns],
            [classes[i] for i in columns],
            relations,
            model["classes"],
            weight,
        )
    groups = []
    for index in selected:
        parts = [lines[i] for i in cached["components"][index]]
        groups.append(
            {
                "id": parts[0]["id"],
                "page": parts[0]["page"],
                "level": int(levels[index]),
                "line_ids": [p["id"] for p in parts],
                "text": " ".join(p["text"] for p in parts),
                "bboxes": [p["bbox"] for p in parts],
            }
        )
    attach_parents(groups)
    return groups


def parse_precision(pdf: Path, models: dict, settings: dict) -> dict:
    start = time.perf_counter()
    lines = extract_lines(pdf)
    rows, _ = feature_rows(lines)
    cached = prepare_candidates(lines, rows, models, settings["variant"])
    headings = predict_candidates(lines, cached, models, settings)
    return {
        "lines": lines,
        "headings": headings,
        "total_seconds": time.perf_counter() - start,
        "parent_status": "inferred from predicted levels; not evaluated",
    }
