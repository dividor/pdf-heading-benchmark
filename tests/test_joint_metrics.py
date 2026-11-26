"""Joint scoring must penalize extra titles and level mistakes, and reject empty abstention."""

import numpy as np
import pytest

from pdf_heading_benchmark.joint_metrics import joint_metrics
from pdf_heading_benchmark.precision_experiment import choose_candidate
from pdf_heading_benchmark.precision_inference import select_levels


def test_wrong_level_counts_as_joint_false_positive_and_false_negative():
    score = joint_metrics(gold=10, predicted=10, matched=10, correct=9)
    assert score["heading_precision"] == 1
    assert score["joint_false_positives"] == score["joint_false_negatives"] == 1
    assert score["joint_f1"] == score["joint_f05"] == 0.9


def test_extra_headings_reduce_score_and_can_fail_the_precision_gate():
    perfect = joint_metrics(10, 10, 10, 10)
    extra = joint_metrics(10, 12, 10, 10)
    assert extra["joint_f05"] < extra["joint_f1"] < perfect["joint_f05"]
    assert not extra["precision_gate_pass"]
    assert joint_metrics(20, 20, 19, 15)["precision_gate_pass"]
    assert not joint_metrics(77, 0, 0, 0)["precision_gate_pass"]


def test_gate_applies_before_validation_ranking():
    rejected = {"score": joint_metrics(20, 23, 20, 20)}
    eligible = {"score": joint_metrics(20, 10, 10, 10)}
    assert rejected["score"]["joint_f05"] > eligible["score"]["joint_f05"]
    assert choose_candidate([rejected, eligible]) == eligible
    assert choose_candidate([rejected]) is None


def test_confidence_and_body_weight_can_abstain_without_changing_level_scores():
    probabilities = np.array([[0.1, 0.8, 0.1], [0.3, 0.5, 0.2], [0.1, 0.3, 0.6]])
    levels, selected = select_levels(probabilities, [0, 1, 2], {"body_weight": 2, "min_heading_score": 0.7})
    assert selected.tolist() == [0]
    assert levels.tolist() == [1, 0, 2]
    assert probabilities[1, 0] == 0.3
    with pytest.raises(ValueError):
        joint_metrics(10, 10, 8, 9)
