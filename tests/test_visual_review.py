"""Keep review annotations and same-corpus comparisons tied to their frozen evidence."""

import hashlib

from pdf_heading_benchmark.cli import runner_command
from pdf_heading_benchmark.evaluation import evaluate
from pdf_heading_benchmark.io import REPO, read_json
from pdf_heading_benchmark.supervised_data import read_labels


def test_visual_annotations_are_the_frozen_labels():
    config = REPO / "configs/supervised"
    corpus = {r["id"]: r for r in read_json(config / "corpus.json")}
    labels = read_labels(config / "labels.tsv")
    annotations = read_json(REPO / "outputs/supervised/evidence/annotations.json")

    def signature(rows):
        return {(r["report_id"], tuple(r["line_ids"]), r["level"]) for r in rows}

    assert signature(labels) == signature(annotations)
    assert len(annotations) == 202
    for item in annotations:
        assert item["page"] in corpus[item["report_id"]]["review_pages"]
        assert len(item["bboxes"]) == len(item["line_ids"])
        assert all(box[0] < box[2] and box[1] < box[3] for box in item["bboxes"])
    toc = read_json(config / "visual-review.json")["documents"]
    assert len(toc) == 24
    assert sum(bool(r["toc_pages"]) for r in toc) == 22
    assert sum(len(r["toc_pages"]) for r in toc) == 26


def test_new_main_table_row_uses_same_corpus_and_unchanged_model():
    comparison = REPO / "outputs/supervised/comparison"
    predictions = read_json(comparison / "audit-predictions.json")
    gold = read_json(REPO / "configs/gold.json")
    pages = read_json(REPO / "configs/audit_pages.json")
    scores = [evaluate(gold[key], predictions[key], pages[key]) for key in gold]
    assert sum(s["matched"] for s in scores) == 59
    assert sum(s["correct_level"] for s in scores) == 35
    assert sum(s["predicted"] - s["matched"] for s in scores) == 20
    row = next(
        r for r in read_json(REPO / "outputs/report/results.json") if r["method"] == "supervised_extra_trees"
    )
    assert row["correct_heading_and_level"] == 35 / 77
    run = read_json(comparison / "run.json")
    selection = read_json(REPO / "outputs/supervised/evidence/selection.json")
    assert run["selected_model_sha256"] == selection["selected_model_sha256"]
    assert (
        hashlib.sha256((REPO / "configs/supervised/labels.tsv").read_bytes()).hexdigest()
        == selection["label_sha256"]
    )


def test_project_runner_uses_locked_environment():
    command = runner_command({"environment": "project", "script": "scripts/runners/run_supervised.py"})
    assert command[:4] == ["uv", "run", "--locked", "python"]
    assert command[-1].endswith("scripts/runners/run_supervised.py")
