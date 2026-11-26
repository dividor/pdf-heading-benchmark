"""Evaluate a previously selected recall experiment; never select on regression reports."""

import argparse
from pathlib import Path

from optimize_precision import historical

from pdf_heading_benchmark.precision_experiment import score_documents
from pdf_heading_benchmark.precision_inference import prepare_candidates
from pdf_heading_benchmark.recall_inference import load_recall
from pdf_heading_benchmark.structure_data import checksum, config_hashes, load_documents
from pdf_heading_benchmark.supervised_data import read_json, write_json

DEPENDENCIES = [
    "scripts/structure/retrain_recall.py",
    "src/pdf_heading_benchmark/recall_training.py",
    "src/pdf_heading_benchmark/precision_experiment.py",
    "src/pdf_heading_benchmark/precision_inference.py",
    "src/pdf_heading_benchmark/structure_data.py",
    "src/pdf_heading_benchmark/structure_features.py",
    "src/pdf_heading_benchmark/structure_inference.py",
    "src/pdf_heading_benchmark/supervised_features.py",
    "src/pdf_heading_benchmark/supervised_models.py",
    "src/pdf_heading_benchmark/evaluation.py",
    "src/pdf_heading_benchmark/joint_metrics.py",
]


def main(args: argparse.Namespace) -> None:
    if (args.output / "historical.json").exists():
        raise ValueError("Already evaluated; use recorded results")
    protocol = read_json(args.output / "protocol.json")
    if config_hashes(args.config) != protocol["config_hashes"]:
        raise ValueError("Changed annotations or split")
    if any(checksum(Path(p)) != protocol["source_hashes"][p] for p in DEPENDENCIES):
        raise ValueError("Changed fitting or inference source")
    models, settings = load_recall(args.output)
    results = {}
    for split in ("validation", "test"):
        documents = load_documents(args.config, args.data, split)
        cached = {
            (d["record"]["id"], "context_relations"): prepare_candidates(
                d["lines"], d["rows"], models, "context_relations"
            )
            for d in documents
        }
        score, audit = score_documents(documents, cached, models, settings)
        results[split] = score
        write_json(args.output / f"{split}-audit.json", audit)
    write_json(args.output / "regression.json", results)
    write_json(args.output / "historical.json", historical(args, models, settings))
    print(results, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/structure-v2"))
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    main(parser.parse_args())
