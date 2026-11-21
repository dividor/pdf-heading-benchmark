"""Guard against leakage, unsafe extraction and misleading heading metrics."""

import hashlib
import io
import tarfile
from pathlib import Path

import numpy as np
import pytest

from pdf_heading_benchmark.supervised_data import extract_archive, label_map, validate_corpus
from pdf_heading_benchmark.supervised_inference import heading_groups, markdown_text
from pdf_heading_benchmark.supervised_models import fit_model, metrics, predict_proba


def record(**changes):
    return {
        "id": 1,
        "sha256": "a",
        "url": "https://docs.wfp.org/WFP-123/download",
        "split": "train",
        "pages": 4,
        "review_pages": [2],
        **changes,
    }


@pytest.mark.parametrize(
    "changes", [{"id": 1}, {"sha256": "a"}, {"url": "https://other/WFP-123/download?different=1"}]
)
def test_prior_documents_excluded_even_when_file_changed(changes):
    other = record(id=2, sha256="b", url="https://docs/WFP-456", **{})
    other.update(changes)
    with pytest.raises(ValueError, match="excluded"):
        validate_corpus([other], [record()])


def test_unreviewed_pages_never_become_negative_examples():
    lines = [{"id": "a", "page": 1}, {"id": "b", "page": 2}, {"id": "c", "page": 2}]
    labels = [{"report_id": 1, "level": 2, "line_ids": ["b"]}]
    assert label_map(record(), lines, labels) == {"b": 2, "c": 0}
    labels[0]["line_ids"] = ["a"]
    with pytest.raises(ValueError, match="unreviewed"):
        label_map(record(), lines, labels)


def test_archive_uses_canonical_target_and_checks_content(tmp_path: Path):
    payload = b"test PDF data"
    archive = tmp_path / "source.tar"
    member = tarfile.TarInfo("../../escape.pdf")
    member.size = len(payload)
    with tarfile.open(archive, "w") as stream:
        stream.addfile(member, io.BytesIO(payload))
    r = record(member=member.name, size=len(payload), sha256=hashlib.sha256(payload).hexdigest())
    extract_archive(archive, [r], tmp_path / "pdfs")
    assert (tmp_path / "pdfs/wfp-1.pdf").read_bytes() == payload
    assert not (tmp_path / "escape.pdf").exists()
    r["sha256"] = "wrong"
    with pytest.raises(ValueError, match="Checksum"):
        extract_archive(archive, [r], tmp_path / "pdfs")


def test_wrong_levels_and_false_headings_reduce_f1():
    result = metrics(np.array([0, 0, 1, 2, 3]), np.array([0, 1, 1, 3, 0]))
    assert result["detection_f1"] == pytest.approx(2 / 3)
    assert result["exact_level_f1"] == pytest.approx(1 / 3)
    assert result["correct_level_lines"] == 1


@pytest.mark.parametrize("kind", ["linear", "trees"])
@pytest.mark.parametrize("classes", [2, 4])
def test_data_only_export_matches_sklearn(kind, classes):
    pytest.importorskip("sklearn")
    rng = np.random.default_rng(42)
    x = rng.normal(size=(80, 3))
    y = np.arange(80) % classes
    model = fit_model(kind, x, y, ["a", "b", "c"])
    probabilities = predict_proba(model, x)
    assert probabilities.shape == (80, classes)
    assert np.allclose(probabilities.sum(axis=1), 1)


def test_wrapped_headings_preserve_text_and_flag_level_jumps():
    values = [
        ("p001b001l00", 1, "Summary"),
        ("p001b002l00", 0, "Body"),
        ("p001b003l00", 3, "A wrapped"),
        ("p001b003l01", 3, "heading"),
    ]
    lines = [
        {"id": key, "level": level, "text": text, "page": 1, "bbox": [0, 0, 1, 1]}
        for key, level, text in values
    ]
    groups = heading_groups(lines)
    assert len(groups) == 2
    assert groups[1]["parent_id"] == groups[0]["id"]
    assert groups[1]["level_jump"]
    rendered = markdown_text({"lines": lines, "headings": groups})
    assert "### A wrapped heading" in rendered
    assert "Body" in rendered


def test_frozen_scores_recompute_from_committed_predictions():
    from pdf_heading_benchmark.io import REPO
    from pdf_heading_benchmark.supervised_data import read_json

    directory = REPO / "outputs/supervised/evidence"
    selection = read_json(directory / "selection.json")
    for name, expected in [
        ("linear-validation", selection["validation"]["linear"]),
        ("trees-validation", selection["validation"]["trees"]),
        ("test", read_json(directory / "test.json")),
    ]:
        predictions = read_json(directory / f"{name}-predictions.json")
        actual = metrics(
            np.array([r["gold"] for r in predictions]), np.array([r["predicted"] for r in predictions])
        )
        assert actual["exact_level_f1"] == expected["exact_level_f1"]
        assert actual["confusion"] == expected["confusion"]


def test_committed_corpus_excludes_historical_documents():
    from pdf_heading_benchmark.io import REPO
    from pdf_heading_benchmark.supervised_data import read_json

    config = REPO / "configs"
    records = read_json(config / "supervised/corpus.json")
    validate_corpus(
        records, read_json(config / "corpus.json") + read_json(config / "supervised/excluded.json")
    )
    assert len(records) == 24
    assert sum(len(r["review_pages"]) for r in records) == 152
