"""Rank unlabelled TRAINING groups for review; never mine validation or test reports."""

import argparse
from pathlib import Path

import numpy as np

from pdf_heading_benchmark.structure_data import load_documents, load_model_bundle
from pdf_heading_benchmark.structure_features import context_index, group_features, with_context
from pdf_heading_benchmark.structure_inference import learned_components
from pdf_heading_benchmark.supervised_data import write_json
from pdf_heading_benchmark.supervised_features import matrix
from pdf_heading_benchmark.supervised_models import predict_proba


def candidates(document: dict, models: dict) -> list[dict]:
    context = context_index(document["lines"])
    groups = learned_components(document["rows"], models["join"])
    inputs = [with_context(group_features(g, document["lines"], document["rows"], context)) for g in groups]
    model = models["context"]
    probabilities = predict_proba(model, matrix(inputs, model["features"]))
    scores = -np.sum(probabilities * np.log(np.maximum(probabilities, 1e-12)), axis=1)
    output = []
    for group, probability, entropy in zip(groups, probabilities, scores, strict=True):
        parts = [document["lines"][i] for i in group]
        if any(p["id"] in document["labels"] for p in parts):
            continue
        output.append(
            {
                "report_id": document["record"]["id"],
                "page": parts[0]["page"],
                "text": " ".join(p["text"] for p in parts),
                "line_ids": [p["id"] for p in parts],
                "suggested_level": model["classes"][int(probability.argmax())],
                "entropy": float(entropy),
                "status": "UNREVIEWED: never a training label",
            }
        )
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/structure-v2"))
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Review queue already exists")
    models, _ = load_model_bundle(args.run, "context_relations")
    queue = []
    for document in load_documents(args.config, args.data, "train"):
        queue.extend(candidates(document, models))
    queue.sort(key=lambda item: item["entropy"], reverse=True)
    write_json(
        args.output,
        {
            "ranking": "Uncalibrated entropy; train reports only; not labels",
            "candidates": queue[: args.limit],
        },
    )
