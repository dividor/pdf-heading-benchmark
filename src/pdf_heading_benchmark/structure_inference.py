"""Learned grouping and sequence-level hierarchy inference, preserving every source line."""

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
from pdf_heading_benchmark.supervised_features import extract_lines, feature_rows, matrix
from pdf_heading_benchmark.supervised_inference import heading_groups
from pdf_heading_benchmark.supervised_models import predict, predict_proba


def learned_components(rows: list[dict], join_model: dict) -> list[list[int]]:
    if len(rows) < 2:
        return [[0]] if rows else []
    pairs = [pair_features(a, b) for a, b in pairwise(rows)]
    joined = predict(join_model, matrix(pairs, join_model["features"]))
    groups = [[0]]
    for index, join in enumerate(joined, 1):
        if join:
            groups[-1].append(index)
        else:
            groups.append([index])
    return groups


def decode_levels(
    probabilities: np.ndarray,
    classes: list,
    relations: np.ndarray,
    relation_classes: list,
    weight: float = 1.0,
) -> list[int]:
    """Viterbi over levels; relation classes encode lower/same/higher next level."""
    if not len(probabilities):
        return []
    logp = np.log(np.maximum(probabilities, 1e-12))
    score = logp[0]
    back = []
    relation_lookup = {value: i for i, value in enumerate(relation_classes)}
    signs = np.sign(np.asarray(classes)[None, :] - np.asarray(classes)[:, None])
    for index in range(1, len(probabilities)):
        edge = np.asarray([[relations[index - 1, relation_lookup[int(s)]] for s in row] for row in signs])
        combined = score[:, None] + weight * np.log(np.maximum(edge, 1e-12))
        back.append(combined.argmax(axis=0))
        score = combined.max(axis=0) + logp[index]
    path = [int(score.argmax())]
    for pointers in reversed(back):
        path.append(int(pointers[path[-1]]))
    return [int(classes[i]) for i in reversed(path)]


def attach_parents(groups: list[dict]) -> None:
    stack: list[dict] = []
    for group in groups:
        while stack and stack[-1]["level"] >= group["level"]:
            stack.pop()
        group["parent_id"] = stack[-1]["id"] if stack else None
        group["level_jump"] = group["level"] != (stack[-1]["level"] + 1 if stack else 1)
        stack.append(group)


def grouped_predictions(
    lines: list[dict], rows: list[dict], models: dict, variant: str, decoding: dict | None = None
) -> list[dict]:
    decoding = decoding or {}
    components = learned_components(rows, models["join"])
    context = context_index(lines)
    grouped = [group_features(g, lines, rows, context) for g in components]
    contextual = variant == "context_relations"
    inputs = [with_context(r) for r in grouped] if contextual else grouped
    model = models["context" if contextual else "group"]
    probabilities = predict_proba(model, matrix(inputs, model["features"]))
    decision = probabilities.copy()
    decision[:, model["classes"].index(0)] *= decoding.get("body_weight", 1.0)
    levels = np.asarray(model["classes"])[decision.argmax(axis=1)]
    selected = np.flatnonzero(levels > 0)
    if contextual and len(selected) > 1:
        pairs = [pair_features(inputs[a], inputs[b]) for a, b in pairwise(selected)]
        relation_model = models["relation"]
        relations = predict_proba(relation_model, matrix(pairs, relation_model["features"]))
        columns = [i for i, c in enumerate(model["classes"]) if c > 0]
        refined = decode_levels(
            probabilities[selected][:, columns],
            [model["classes"][i] for i in columns],
            relations,
            relation_model["classes"],
            weight=decoding.get("relation_weight", 1.0),
        )
        levels[selected] = refined
    output = []
    for i in selected:
        parts = [lines[j] for j in components[i]]
        output.append(
            {
                "id": parts[0]["id"],
                "page": parts[0]["page"],
                "level": int(levels[i]),
                "line_ids": [p["id"] for p in parts],
                "text": " ".join(p["text"] for p in parts),
                "bboxes": [p["bbox"] for p in parts],
            }
        )
    attach_parents(output)
    return output


def infer_lines(
    lines: list[dict], rows: list[dict], models: dict, variant: str, decoding: dict | None = None
) -> list[dict]:
    if variant == "expanded_line":
        model = models["line"]
        levels = predict(model, matrix(rows, model["features"]))
        return heading_groups(
            [dict(line, level=int(level)) for line, level in zip(lines, levels, strict=True)]
        )
    if variant not in {"learned_groups", "context_relations"}:
        raise ValueError("Unknown structure variant")
    return grouped_predictions(lines, rows, models, variant, decoding)


def parse_structure(pdf: Path, models: dict, variant: str, decoding: dict | None = None) -> dict:
    start = time.perf_counter()
    lines = extract_lines(pdf)
    rows, _ = feature_rows(lines)
    groups = infer_lines(lines, rows, models, variant, decoding)
    return {
        "lines": lines,
        "headings": groups,
        "total_seconds": time.perf_counter() - start,
        "parent_status": "inferred from predicted sequence levels; parent edges not evaluated",
    }
