"""Micro-averaged title-and-level metrics with an explicit heading precision gate."""

PRECISION_FLOOR = 0.95


def joint_metrics(gold: int, predicted: int, matched: int, correct: int) -> dict:
    """Wrong levels are joint false positives and joint false negatives."""
    if not 0 <= correct <= matched <= min(gold, predicted):
        raise ValueError("Inconsistent heading counts")
    return {
        "joint_precision": correct / predicted if predicted else 0.0,
        "joint_recall": correct / gold if gold else 0.0,
        "joint_f1": 2 * correct / (predicted + gold) if predicted + gold else 0.0,
        "joint_f05": 1.25 * correct / (predicted + 0.25 * gold) if predicted + gold else 0.0,
        "heading_precision": matched / predicted if predicted else 0.0,
        "precision_gate_pass": predicted > 0 and matched / predicted >= PRECISION_FLOOR,
        "joint_false_positives": predicted - correct,
        "joint_false_negatives": gold - correct,
    }


def scored_counts(counts: dict) -> dict:
    return {
        **counts,
        **joint_metrics(counts["gold"], counts["predicted"], counts["matched"], counts["correct_level"]),
    }
