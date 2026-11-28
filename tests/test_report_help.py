"""Worked scoring examples use the actual published metric."""

from bs4 import BeautifulSoup

from pdf_heading_benchmark.io import REPO
from pdf_heading_benchmark.joint_metrics import joint_metrics


def test_score_modal_contains_the_document_example_and_correct_calculation():
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    example = soup.select_one("#column-help-2 .score-example")
    reference, predicted = example.find_all("pre")
    assert len(reference.get_text().splitlines()) == 4
    assert len(predicted.get_text().splitlines()) == 4
    assert "    H2  School attendance" in reference.get_text()
    assert "H1  School attendance" in predicted.get_text()
    assert "Recommendations" not in predicted.get_text()
    assert "Attendance rose 12%" in predicted.get_text()
    assert [item.strong.get_text() for item in example.find_all("li")] == [
        "Correct:",
        "Wrong level:",
        "Extra heading:",
        "Missing:",
    ]
    score = joint_metrics(gold=4, predicted=4, matched=3, correct=2)["joint_f05"]
    assert example.select_one(".score-example-result").get_text() == (
        f"Joint F0.5 = (1.25 \N{MULTIPLICATION SIGN} 2) / (4 + 0.25 \N{MULTIPLICATION SIGN} 4) = {score:.0%}."
    )
    assert len(soup.select(".score-example")) == 1
