"""Validation-only search and scoring with the same matching contract as the main league."""

from itertools import product
from pathlib import Path

from pdf_heading_benchmark.evaluation import evaluate
from pdf_heading_benchmark.joint_metrics import scored_counts
from pdf_heading_benchmark.precision_inference import predict_candidates, prepare_candidates
from pdf_heading_benchmark.structure_data import config_hashes, load_model_bundle
from pdf_heading_benchmark.supervised_data import read_json


def decision_grid() -> list[dict]:
    grid = []
    for variant in ("learned_groups", "context_relations"):
        weights = (0.0,) if variant == "learned_groups" else (1.0, 0.0)
        for body, threshold, relation in product((1.0, 2.0, 4.0), (0.0, 0.5, 0.7, 0.85), weights):
            grid.append(
                dict(variant=variant, body_weight=body, min_heading_score=threshold, relation_weight=relation)
            )
    return grid


def choose_candidate(candidates: list[dict]) -> dict | None:
    eligible = [c for c in candidates if c["score"]["precision_gate_pass"]]
    # Stable grid order breaks exact ties; simpler variant and lower thresholds first.
    return max(eligible, key=lambda c: c["score"]["joint_f05"]) if eligible else None


def frozen_models(config: Path, run: Path) -> dict:
    selection = read_json(run / "selection.json")
    if selection["config_hashes"] != config_hashes(config):
        raise ValueError("Changed training configuration")
    grouped, _ = load_model_bundle(run, "learned_groups")
    contextual, _ = load_model_bundle(run, "context_relations")
    return grouped | contextual


def heading_records(groups: list[dict]) -> list[dict]:
    return [{"title": h["text"], "page": h["page"], "level": h["level"]} for h in groups]


def prepare_validation(documents: list[dict], models: dict) -> dict:
    return {
        (doc["record"]["id"], variant): prepare_candidates(doc["lines"], doc["rows"], models, variant)
        for doc in documents
        for variant in ("learned_groups", "context_relations")
    }


def score_documents(documents: list[dict], cached: dict, models: dict, settings: dict) -> tuple[dict, list]:
    counts = dict.fromkeys(("gold", "predicted", "matched", "correct_level"), 0)
    per_document, audits = {}, []
    for doc in documents:
        key = doc["record"]["id"]
        groups = predict_candidates(doc["lines"], cached[key, settings["variant"]], models, settings)
        pages = doc["record"]["review_pages"]
        if not pages:
            raise ValueError("Evaluation requires fully reviewed pages")
        groups = [g for g in groups if g["page"] in pages]
        scored = evaluate(heading_records(doc["groups"]), heading_records(groups), pages)
        found = {k: scored[k] for k in counts}
        per_document[str(key)] = scored_counts(found)
        for k, value in found.items():
            counts[k] += value
        audits.append({"report_id": key, "headings": groups})
    return {**scored_counts(counts), "per_document": per_document}, audits
