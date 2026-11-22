"""Coverage selection must not reward low-recall candidates just for high precision."""

import json

import pytest

from pdf_heading_benchmark.recall_inference import load_recall
from pdf_heading_benchmark.recall_training import candidate_rank, decision_grid, tree_grid
from pdf_heading_benchmark.structure_data import checksum


def candidate(precision, recall, f05):
    return dict(score=dict(joint_precision=precision, joint_recall=recall, joint_f05=f05))


def test_both_joint_targets_are_required_and_fallback_is_balanced():
    selective = candidate(1.0, 0.5, 0.83)
    balanced = candidate(0.81, 0.81, 0.81)
    assert candidate_rank(balanced) > candidate_rank(selective)
    assert not candidate_rank(selective)[0]
    assert candidate_rank(candidate(0.84, 0.76, 0.82)) > candidate_rank(candidate(1.0, 0.67, 0.91))
    assert len(tree_grid()) * len(decision_grid()) == 64


def test_saved_model_identity_is_checked(tmp_path):
    model = tmp_path / "context.json"
    model.write_text('{"kind": "trees"}')
    (tmp_path / "selection.json").write_text(
        json.dumps(
            {"model_hashes": {"context": checksum(model)}, "selected": {"settings": {"relation_weight": 0}}}
        )
    )
    models, settings = load_recall(tmp_path)
    assert models["context"]["kind"] == "trees"
    assert settings["relation_weight"] == 0
    model.write_text('{"kind": "changed"}')
    with pytest.raises(ValueError, match="Changed selected model"):
        load_recall(tmp_path)


def test_published_selection_matches_the_predeclared_validation_rule():
    from pdf_heading_benchmark.io import REPO, read_json

    record = read_json(REPO / "outputs/structure-recall/evidence/selection.json")
    assert len(record["validation"]) == 64
    assert record["selected"] == max(record["validation"], key=candidate_rank)
    assert record["eligible"] == bool(candidate_rank(record["selected"])[0])
    assert set(record["train_reports"]).isdisjoint(record["validation_reports"])
