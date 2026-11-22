"""Refit Extra Trees with a predeclared validation objective that requires coverage."""

import time
from itertools import pairwise, product

import numpy as np

from pdf_heading_benchmark.structure_features import (
    pair_features,
    training_groups,
    training_pairs,
    with_context,
)
from pdf_heading_benchmark.supervised_features import matrix
from pdf_heading_benchmark.supervised_models import predict_proba


def training_inputs(documents: list[dict]) -> dict:
    groups: list[dict] = []
    joins: list[dict] = []
    relations: list[dict] = []
    for doc in documents:
        current = training_groups(doc)
        groups.extend(with_context(g) for g in current)
        joins.extend(training_pairs(doc))
        headings = [with_context(g) for g in current if g["label"] > 0]
        relations.extend(
            dict(pair_features(a, b), label=int(np.sign(b["label"] - a["label"])))
            for a, b in pairwise(headings)
        )
    return dict(join=joins, context=groups, relation=relations)


def tree_grid() -> list[dict]:
    return [
        dict(max_depth=depth, min_samples_leaf=leaf, max_features=features)
        for depth, leaf, features in product((16, None), (1, 2), (0.8, 1.0))
    ]


def decision_grid() -> list[dict]:
    return [
        dict(variant="context_relations", body_weight=body, min_heading_score=threshold, relation_weight=rel)
        for body, threshold, rel in product((0.75, 1.0), (0.0, 0.5), (0.0, 1.0))
    ]


def fit(rows: list[dict], settings: dict) -> dict:
    from sklearn.ensemble import ExtraTreesClassifier

    names = sorted(rows[0]["features"])
    x, y = matrix(rows, names), np.asarray([r["label"] for r in rows])
    estimator = ExtraTreesClassifier(
        n_estimators=200, class_weight="balanced", random_state=42, n_jobs=4, **settings
    )
    start = time.perf_counter()
    estimator.fit(x, y)
    seconds = time.perf_counter() - start
    trees = [
        dict(
            left=t.tree_.children_left.tolist(),
            right=t.tree_.children_right.tolist(),
            feature=t.tree_.feature.tolist(),
            threshold=t.tree_.threshold.tolist(),
            value=t.tree_.value[:, 0, :].tolist(),
        )
        for t in estimator.estimators_
    ]
    model = dict(
        kind="trees",
        features=names,
        classes=estimator.classes_.tolist(),
        data=dict(trees=trees),
        fit_seconds=seconds,
    )
    if not np.allclose(predict_proba(model, x), estimator.predict_proba(x), atol=1e-7):
        raise ValueError("JSON export differs from sklearn")
    return model


def candidate_rank(candidate: dict) -> tuple:
    score = candidate["score"]
    eligible = score["joint_precision"] >= 0.8 and score["joint_recall"] >= 0.8
    # If no candidate meets both floors, retain only a diagnostic balanced fallback.
    return (
        eligible,
        score["joint_f05"] if eligible else min(score["joint_precision"], score["joint_recall"]),
        score["joint_f05"],
    )
