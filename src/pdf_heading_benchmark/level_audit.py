"""Summarize level disagreements without changing predictions or reference labels."""

from collections import Counter

from pdf_heading_benchmark.prediction_comparison import comparison_rows


def level_audit(documents: list[dict]) -> dict:
    pairs: Counter = Counter()
    rows = []
    for item in documents:
        for row in comparison_rows(item["audit"]):
            rows.append(dict(document=item["document"]["id"], **row))
            if row["reference"] and row["prediction"]:
                pairs[(row["reference"]["level"], row["prediction"]["level"])] += 1
    counts = Counter(row["status"] for row in rows)
    return dict(
        counts={status: counts[status] for status in ("correct", "wrong", "missing", "extra")},
        level_pairs=[
            dict(reference=reference, prediction=prediction, count=count)
            for (reference, prediction), count in sorted(pairs.items(), key=lambda item: str(item[0]))
        ],
        rows=rows,
    )
