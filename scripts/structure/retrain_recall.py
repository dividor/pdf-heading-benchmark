"""Fresh fitting experiment; validation selection precedes all regression evaluation."""

import argparse
import platform
from pathlib import Path

import sklearn

from pdf_heading_benchmark.precision_experiment import score_documents
from pdf_heading_benchmark.precision_inference import prepare_candidates
from pdf_heading_benchmark.recall_training import (
    candidate_rank,
    decision_grid,
    fit,
    training_inputs,
    tree_grid,
)
from pdf_heading_benchmark.structure_data import checksum, config_hashes, load_documents
from pdf_heading_benchmark.supervised_data import write_json


def select(args: argparse.Namespace) -> None:
    if args.output.exists():
        raise ValueError("Use a fresh run directory")
    sources = [Path(__file__), *Path("src/pdf_heading_benchmark").glob("*.py")]
    protocol = dict(
        objective="Maximum validation joint F0.5 with joint precision AND joint recall >=0.80. "
        "If none qualifies, diagnostic fallback maximizes min(joint precision, joint recall), "
        "then joint F0.5. Exact ties retain grid order. Floors are pilot targets, not deployment guarantees.",
        tree_grid=tree_grid(),
        decision_grid=decision_grid(),
        fixed_tree_settings=dict(n_estimators=200, class_weight="balanced", random_state=42, n_jobs=4),
        config_hashes=config_hashes(args.config),
        source_hashes={
            str(p.relative_to(Path.cwd()) if p.is_absolute() else p): checksum(p) for p in sources
        },
        python=platform.python_version(),
        sklearn=sklearn.__version__,
        platform=platform.platform(),
        scope="Same 20 training and four validation reports as v2. No new labels. "
        "Original league and inspected v2 test are regression only; never select settings.",
    )
    write_json(args.output / "protocol.json", protocol)
    train = load_documents(args.config, args.data, "train")
    validation = load_documents(args.config, args.data, "validation")
    inputs = training_inputs(train)
    candidates, winner, winner_models = [], None, None
    for index, tree_settings in enumerate(tree_grid()):
        models = {name: fit(rows, tree_settings) for name, rows in inputs.items()}
        cached = {
            (d["record"]["id"], "context_relations"): prepare_candidates(
                d["lines"], d["rows"], models, "context_relations"
            )
            for d in validation
        }
        for settings in decision_grid():
            score, _ = score_documents(validation, cached, models, settings)
            candidate = dict(tree_index=index, trees=tree_settings, settings=settings, score=score)
            candidates.append(candidate)
            if winner is None or candidate_rank(candidate) > candidate_rank(winner):
                winner, winner_models = candidate, models
        write_json(args.output / "search-progress.json", candidates)
        print(
            "FITTED",
            index,
            tree_settings,
            "BEST",
            winner["score"]["joint_precision"],
            winner["score"]["joint_recall"],
            flush=True,
        )
    hashes = {}
    for name, model in winner_models.items():
        path = args.output / f"{name}.json"
        write_json(path, model)
        hashes[name] = checksum(path)
    write_json(
        args.output / "selection.json",
        dict(
            selected=winner,
            validation=candidates,
            eligible=bool(candidate_rank(winner)[0]),
            model_hashes=hashes,
            training_examples={k: len(v) for k, v in inputs.items()},
            train_reports=[d["record"]["id"] for d in train],
            validation_reports=[d["record"]["id"] for d in validation],
        ),
    )
    print("SELECTED", winner, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/structure-v2"))
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    select(parser.parse_args())
