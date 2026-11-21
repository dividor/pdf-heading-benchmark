"""Small CPU classifiers exported as data-only JSON, never executable pickles."""

import time

import numpy as np
from scipy.special import softmax


def fit_model(kind: str, x: np.ndarray, y: np.ndarray, names: list[str]) -> dict:
    from sklearn.ensemble import ExtraTreesClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    start = time.perf_counter()
    if kind == "linear":
        scaler = StandardScaler().fit(x)
        estimator = LogisticRegression(C=1, class_weight="balanced", max_iter=3000, random_state=42)
        estimator.fit(scaler.transform(x), y)
        data = {
            "mean": scaler.mean_.tolist(),
            "scale": scaler.scale_.tolist(),
            "coef": estimator.coef_.tolist(),
            "intercept": estimator.intercept_.tolist(),
        }
    elif kind == "trees":
        estimator = ExtraTreesClassifier(
            n_estimators=200,
            max_depth=16,
            min_samples_leaf=2,
            class_weight="balanced",
            max_features=0.8,
            random_state=42,
            n_jobs=4,
        )
        estimator.fit(x, y)
        data = {
            "trees": [
                {
                    "left": t.tree_.children_left.tolist(),
                    "right": t.tree_.children_right.tolist(),
                    "feature": t.tree_.feature.tolist(),
                    "threshold": t.tree_.threshold.tolist(),
                    "value": t.tree_.value[:, 0, :].tolist(),
                }
                for t in estimator.estimators_
            ]
        }
    else:
        raise ValueError(f"Unknown model: {kind}")
    model = {
        "kind": kind,
        "features": names,
        "classes": estimator.classes_.tolist(),
        "data": data,
        "fit_seconds": time.perf_counter() - start,
    }
    expected = estimator.predict_proba(scaler.transform(x) if kind == "linear" else x)
    if not np.allclose(predict_proba(model, x), expected, atol=1e-7):
        raise ValueError("Exported JSON model disagrees with sklearn")
    return model


def tree_probabilities(tree: dict, x: np.ndarray) -> np.ndarray:
    x = x.astype(np.float32)  # Match sklearn tree traversal precision.
    nodes = np.zeros(len(x), dtype=int)
    left, right = np.asarray(tree["left"]), np.asarray(tree["right"])
    features, thresholds = np.asarray(tree["feature"]), np.asarray(tree["threshold"])
    while np.any(left[nodes] >= 0):
        active = np.flatnonzero(left[nodes] >= 0)
        current = nodes[active]
        go_left = x[active, features[current]] <= thresholds[current]
        nodes[active] = np.where(go_left, left[current], right[current])
    values = np.asarray(tree["value"])[nodes]
    return values / values.sum(axis=1, keepdims=True)


def predict_proba(model: dict, x: np.ndarray) -> np.ndarray:
    data = model["data"]
    if model["kind"] == "linear":
        scaled = (x - np.asarray(data["mean"])) / np.asarray(data["scale"])
        scores = scaled @ np.asarray(data["coef"]).T + np.asarray(data["intercept"])
        if len(model["classes"]) == 2:
            scores = np.column_stack((np.zeros(len(scores)), scores[:, 0]))
        return softmax(scores, axis=1)
    if model["kind"] != "trees":
        raise ValueError("Unknown JSON model kind")
    return np.mean([tree_probabilities(tree, x) for tree in data["trees"]], axis=0)


def predict(model: dict, x: np.ndarray) -> np.ndarray:
    return np.asarray(model["classes"])[predict_proba(model, x).argmax(axis=1)]


def metrics(y: np.ndarray, predicted: np.ndarray) -> dict:
    tp = int(np.sum((y > 0) & (predicted > 0)))
    positive, detected = int(np.sum(y > 0)), int(np.sum(predicted > 0))
    correct = int(np.sum((y > 0) & (predicted == y)))
    precision, recall = tp / max(1, detected), tp / max(1, positive)
    exact_p, exact_r = correct / max(1, detected), correct / max(1, positive)
    return {
        "lines": len(y),
        "heading_lines": positive,
        "predicted_heading_lines": detected,
        "detected_heading_lines": tp,
        "correct_level_lines": correct,
        "detection_precision": precision,
        "detection_recall": recall,
        "detection_f1": 2 * precision * recall / max(1e-12, precision + recall),
        "exact_level_precision": exact_p,
        "exact_level_recall": exact_r,
        "exact_level_f1": 2 * exact_p * exact_r / max(1e-12, exact_p + exact_r),
        "level_accuracy_given_detected": correct / max(1, tp),
        "confusion_labels": [0, 1, 2, 3, 4, 5, 6],
        "confusion": [[int(np.sum((y == a) & (predicted == b))) for b in range(7)] for a in range(7)],
    }


def evaluate(model: dict, rows: list[dict], annotations: list[dict]) -> tuple[dict, list[dict]]:
    from pdf_heading_benchmark.supervised_features import matrix

    start = time.perf_counter()
    predicted = predict(model, matrix(rows, model["features"]))
    seconds = time.perf_counter() - start
    y = np.asarray([r["label"] for r in rows])
    result = metrics(y, predicted)
    result["predict_seconds"] = seconds
    predictions = [
        {
            "report_id": r["report_id"],
            "id": r["id"],
            "page": r["page"],
            "gold": int(label),
            "predicted": int(p),
        }
        for r, label, p in zip(rows, y, predicted, strict=True)
    ]
    result["per_document"] = {}
    for identifier in sorted({r["report_id"] for r in rows}):
        mask = np.asarray([r["report_id"] == identifier for r in rows])
        result["per_document"][str(identifier)] = metrics(y[mask], predicted[mask])
    lookup = {(r["report_id"], r["id"]): r["predicted"] for r in predictions}
    groups = [a for a in annotations if (a["report_id"], a["line_ids"][0]) in lookup]
    result["heading_groups"] = len(groups)
    result["complete_groups_detected"] = sum(
        all(lookup[a["report_id"], line] > 0 for line in a["line_ids"]) for a in groups
    )
    result["complete_groups_correct_level"] = sum(
        all(lookup[a["report_id"], line] == a["level"] for line in a["line_ids"]) for a in groups
    )
    return result, predictions
