"""Select decoding weights on validation; separately regress on the already inspected v2 test."""

import argparse
from itertools import product
from pathlib import Path

from evaluate import historical

from pdf_heading_benchmark.structure_data import checksum, config_hashes, load_documents, load_model_bundle
from pdf_heading_benchmark.structure_evaluation import evaluate_documents
from pdf_heading_benchmark.supervised_data import read_json, write_json


def select(args: argparse.Namespace) -> None:
    if args.output.exists():
        raise ValueError("Use a fresh output directory")
    models, variant = load_model_bundle(args.run, "context_relations")
    selection = read_json(args.run / "selection.json")
    if selection["config_hashes"] != config_hashes(args.config):
        raise ValueError("Changed labels/protocol")
    documents = load_documents(args.config, args.data, "validation")
    # Baseline first; exact ties retain it. Grid fixed before examining scores.
    grid = [{"body_weight": b, "relation_weight": r} for b, r in product((1.0, 1.5, 2.0), (1.0, 0.5, 0.0))]
    protocol = {
        "grid": grid,
        "selection": "Maximum validation exact group+level F1; ties retain first (baseline first).",
        "config_hashes": config_hashes(args.config),
        "model_hashes": selection["model_hashes"],
        "source_hashes": {
            str(p): checksum(p)
            for p in [
                Path(__file__).relative_to(Path.cwd()),
                Path("src/pdf_heading_benchmark/structure_inference.py"),
                Path("src/pdf_heading_benchmark/structure_evaluation.py"),
                Path("scripts/structure/evaluate.py"),
            ]
        },
        "test_status": "Previously inspected v2 test is a regression set, not fresh evaluation.",
    }
    write_json(args.output / "protocol.json", protocol)
    scores = []
    for decoding in grid:
        result, _ = evaluate_documents(documents, models, variant, decoding)
        scores.append({"decoding": decoding, "score": result})
        print(decoding, result["group_level_f1"], flush=True)
    chosen = max(scores, key=lambda item: item["score"]["group_level_f1"])
    write_json(args.output / "selection.json", {"selected": chosen, "validation": scores})
    print("Selected", chosen["decoding"], flush=True)


def regression(args: argparse.Namespace) -> None:
    if (args.output / "regression.json").exists():
        raise ValueError("Regression already recorded")
    protocol = read_json(args.output / "protocol.json")
    frozen = read_json(args.run / "selection.json")
    if protocol["config_hashes"] != config_hashes(args.config):
        raise ValueError("Changed labels/protocol")
    if protocol["model_hashes"] != frozen["model_hashes"]:
        raise ValueError("Changed model selection")
    if any(checksum(Path(p)) != value for p, value in protocol["source_hashes"].items()):
        raise ValueError("Changed code since calibration")
    selected = read_json(args.output / "selection.json")["selected"]["decoding"]
    models, variant = load_model_bundle(args.run, "context_relations")
    documents = load_documents(args.config, args.data, "test")
    results = {}
    for name, decoding in [("baseline", {}), ("selected", selected)]:
        results[name], audit = evaluate_documents(documents, models, variant, decoding)
        write_json(args.output / f"{name}-regression-audit.json", audit)
        print(name, results[name]["group_level_f1"], flush=True)
    write_json(args.output / "regression.json", {"decoding": selected, "results": results})
    measured = historical(
        args.config, args.data.parent, models, variant, args.output / "historical", selected
    )
    write_json(args.output / "historical.json", measured)
    print("Historical:", sum(s["correct_level"] for s in measured["scores"]), "/77", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["select", "regression"])
    parser.add_argument("--config", type=Path, default=Path("configs/structure-v2"))
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    {"select": select, "regression": regression}[arguments.stage](arguments)
