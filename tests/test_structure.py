"""Protect partial-label semantics, grouping boundaries, sequence decoding and frozen splits."""

from pathlib import Path

import numpy as np
import pytest

from pdf_heading_benchmark.structure_data import known_labels, validate_records
from pdf_heading_benchmark.structure_evaluation import group_counts, summarize_counts
from pdf_heading_benchmark.structure_features import training_pairs
from pdf_heading_benchmark.structure_inference import decode_levels, learned_components
from pdf_heading_benchmark.supervised_data import read_json


def test_added_positive_does_not_label_rest_of_page_negative():
    lines = [
        {"id": "a", "page": 1, "text": "Title"},
        {"id": "b", "page": 1, "text": "Unknown"},
        {"id": "c", "page": 2, "text": "Reviewed body"},
    ]
    group = {"line_ids": ["a"], "level": 1, "text": "Title"}
    record = {"review_pages": [2], "split": "train"}
    assert known_labels(record, lines, [group]) == {"a": 1, "c": 0}
    record["split"] = "test"
    with pytest.raises(ValueError, match="outside reviewed"):
        known_labels(record, lines, [group])


def test_unreviewed_pairs_are_not_negative_training_examples():
    rows = [{"id": str(i), "page": 1, "features": {"x": float(i)}} for i in range(4)]
    doc = {"rows": rows, "labels": {"0": 2, "1": 2, "3": 0}, "groups": [{"line_ids": ["0", "1"]}]}
    pairs = training_pairs(doc)
    assert len(pairs) == 1
    assert pairs[0]["label"] == 1


def test_learned_join_can_cross_pdf_block_boundaries(monkeypatch):
    monkeypatch.setattr(
        "pdf_heading_benchmark.structure_inference.predict", lambda model, matrix: np.array([1, 0])
    )
    rows = [
        {"id": key, "page": 1, "features": {"x": 0.0}}
        for key in ["p001b001l00", "p001b002l00", "p001b003l00"]
    ]
    assert learned_components(rows, {"features": ["page_delta"]}) == [[0, 1], [2]]


def test_fragmented_heading_is_not_a_correct_group():
    gold = [{"line_ids": ["a", "b"], "level": 2}]
    fragmented = [{"line_ids": ["a"], "level": 2}, {"line_ids": ["b"], "level": 2}]
    score = summarize_counts(group_counts(gold, fragmented))
    assert score["group_level_f1"] == 0
    assert score["predicted"] == 2


def test_sequence_relation_can_resolve_ambiguous_level():
    unary = np.array([[0.99, 0.01], [0.45, 0.55]])
    relations = np.array([[0.01, 0.98, 0.01]])
    assert decode_levels(unary, [1, 2], relations, [-1, 0, 1]) == [1, 1]


def test_frozen_v2_has_no_prior_test_or_benchmark_documents():
    config = Path(__file__).parents[1] / "configs/structure-v2"
    records = read_json(config / "corpus.json")
    validate_records(records, read_json(config / "excluded.json"))
    assert len([r for r in records if r["split"] == "test"]) == 4
    assert sum(len(r["review_pages"]) for r in records if r["split"] == "test") == 32


def test_published_fresh_scores_recompute_from_frozen_annotations():
    from pdf_heading_benchmark.structure_data import config_hashes

    root = Path(__file__).parents[1]
    config = root / "configs/structure-v2"
    evidence = root / "outputs/structure-v2/evidence"
    selection = read_json(evidence / "selection.json")
    assert selection["config_hashes"] == config_hashes(config)
    annotations = read_json(config / "annotations.json")
    results = read_json(evidence / "test.json")
    for variant, expected in results["variants"].items():
        counts = dict.fromkeys(("gold", "predicted", "matched", "correct"), 0)
        for audit in read_json(evidence / f"{variant}-test-audit.json"):
            gold = [a for a in annotations if a["report_id"] == audit["report_id"]]
            found = group_counts(gold, audit["headings"])
            for key, value in found.items():
                counts[key] += value
        assert summarize_counts(counts)["group_level_f1"] == expected["group_level_f1"]
