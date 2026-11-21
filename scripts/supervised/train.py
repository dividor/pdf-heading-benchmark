"""Fit on train reports, select on validation reports. Does not evaluate test reports."""

import argparse
import hashlib
import platform
from pathlib import Path

import numpy as np
import sklearn

from pdf_heading_benchmark.supervised_data import read_json, read_labels, write_json
from pdf_heading_benchmark.supervised_features import matrix
from pdf_heading_benchmark.supervised_models import evaluate, fit_model


def train(data: Path, output: Path, config: Path) -> None:
    if output.exists():
        raise ValueError("Use a fresh run directory; existing evidence must not be overwritten")
    dataset = read_json(data / "dataset.json")
    for name in ("labels.tsv", "corpus.json"):
        if dataset["config_hashes"][name] != hashlib.sha256((config / name).read_bytes()).hexdigest():
            raise ValueError("Stale dataset: rerun prepare after changing annotations or corpus")
    training = [r for r in dataset["rows"] if r["split"] == "train"]
    validation = [r for r in dataset["rows"] if r["split"] == "validation"]
    annotations = read_labels(config / "labels.tsv")
    results = {}
    for kind in ("linear", "trees"):
        model = fit_model(
            kind,
            matrix(training, dataset["features"]),
            np.asarray([r["label"] for r in training]),
            dataset["features"],
        )
        result, predictions = evaluate(model, validation, annotations)
        result["fit_seconds"] = model["fit_seconds"]
        write_json(output / f"{kind}.json", model)
        result["model_bytes"] = (output / f"{kind}.json").stat().st_size
        write_json(output / f"{kind}-validation-predictions.json", predictions)
        results[kind] = result
    chosen = max(results, key=lambda kind: results[kind]["exact_level_f1"])
    run = {
        "selected": chosen,
        "selection_metric": "validation exact-level line F1",
        "validation": results,
        "sklearn": sklearn.__version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "train_reports": sorted({r["report_id"] for r in training}),
        "validation_reports": sorted({r["report_id"] for r in validation}),
        "label_sha256": hashlib.sha256((config / "labels.tsv").read_bytes()).hexdigest(),
        "corpus_sha256": hashlib.sha256((config / "corpus.json").read_bytes()).hexdigest(),
        "selected_model_sha256": hashlib.sha256((output / f"{chosen}.json").read_bytes()).hexdigest(),
    }
    write_json(output / "selection.json", run)
    print({"selected": chosen, "validation": {k: v["exact_level_f1"] for k, v in results.items()}})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/supervised"))
    args = parser.parse_args()
    train(args.data, args.output, args.config)
