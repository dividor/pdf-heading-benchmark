from pdf_heading_benchmark.evaluation import evaluate
from pdf_heading_benchmark.level_audit import level_audit


def test_level_audit_keeps_wrong_levels_separate_from_missing_and_extra():
    gold = [dict(page=1, title="Introduction", level=1), dict(page=1, title="Methods", level=2)]
    predicted = [dict(page=1, title="Introduction", level=3), dict(page=1, title="Unrelated", level=2)]
    audit = level_audit([dict(document=dict(id="example"), audit=evaluate(gold, predicted, [1]))])
    assert audit["counts"] == dict(correct=0, wrong=1, missing=1, extra=1)
    assert audit["level_pairs"] == [dict(reference=1, prediction=3, count=1)]
    assert audit["rows"][0]["reference"]["level"] == 1
    assert audit["rows"][0]["prediction"]["level"] == 3
