"""The displayed comparison must reconcile with the published scores for every method."""

from bs4 import BeautifulSoup

from pdf_heading_benchmark.evaluation import evaluate
from pdf_heading_benchmark.io import REPO, read_json
from pdf_heading_benchmark.prediction_comparison import comparison_rows


def test_all_modal_comparisons_reconcile_with_the_league():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    for result in read_json(REPO / "outputs/report/results.json"):
        panel = soup.find("dialog", id="technique-" + result["method"])
        comparison = panel.select_one(".prediction-comparison")
        assert len(comparison.select("details.comparison-document")) == 4
        correct = len(comparison.select("tr.comparison-correct"))
        wrong = len(comparison.select("tr.comparison-wrong"))
        missing = len(comparison.select("tr.comparison-missing"))
        extra = len(comparison.select("tr.comparison-extra"))
        assert correct == result["correct_level"]
        assert correct + wrong == result["matched"]
        assert correct + wrong + missing == result["gold"]
        assert correct + wrong + extra == result["predicted"]


def test_comparison_keeps_absent_levels_duplicates_and_unmatched_titles():
    truth = [
        {"page": 1, "title": "Findings", "level": 1},
        {"page": 2, "title": "Recommendations", "level": 1},
    ]
    predictions = [
        {"page": 1, "title": "Findings", "level": None},
        {"page": 1, "title": "Findings", "level": None},
        {"page": 3, "title": "Not an audited page", "level": 1},
    ]
    rows = comparison_rows(evaluate(truth, predictions, [1, 2]))
    assert [r["status"] for r in rows] == ["wrong", "extra", "missing"]
    assert rows[0]["prediction"]["level"] is None
    assert rows[1]["reference"] is None
    assert rows[2]["prediction"] is None
