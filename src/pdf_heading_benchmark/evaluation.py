"""Frozen matching contract: same page, normalized title similarity, exact level."""

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any

import numpy as np
from scipy.optimize import linear_sum_assignment


def normalize(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return "".join(c for c in unicodedata.normalize("NFKC", text).casefold() if c.isalnum())


def similarities(truth: list[dict], predictions: list[dict]) -> np.ndarray:
    scores = np.zeros((len(truth), len(predictions)))
    for i, reference in enumerate(truth):
        for j, prediction in enumerate(predictions):
            if reference["page"] == prediction["page"]:
                scores[i, j] = SequenceMatcher(
                    None, normalize(reference["title"]), normalize(prediction["title"]), autojunk=False
                ).ratio()
    return scores


def evaluate(truth: list[dict], predictions: list[dict], pages: list[int]) -> dict[str, Any]:
    """Use the historical Hungarian assignment before the 0.90 threshold."""
    predictions = [h for h in predictions if h["page"] in pages]
    scores = similarities(truth, predictions)
    rows, columns = linear_sum_assignment(-scores)
    pairs = [(i, j) for i, j in zip(rows, columns, strict=True) if scores[i, j] >= 0.90]
    matched_truth = {i for i, _ in pairs}
    matched_predictions = {j for _, j in pairs}
    return {
        "gold": len(truth),
        "predicted": len(predictions),
        "matched": len(pairs),
        "correct_level": sum(truth[i]["level"] == predictions[j]["level"] for i, j in pairs),
        "matches": [
            {"reference": truth[i], "prediction": predictions[j], "similarity": float(scores[i, j])}
            for i, j in pairs
        ],
        "missing": [h for i, h in enumerate(truth) if i not in matched_truth],
        "extras": [h for j, h in enumerate(predictions) if j not in matched_predictions],
    }


def evaluate_all(gold: dict, predictions: dict, pages: dict) -> list[dict]:
    return [
        dict(document=key, method=method, **evaluate(gold[key], documents[key], pages[key]))
        for method, documents in predictions.items()
        for key in gold
    ]
