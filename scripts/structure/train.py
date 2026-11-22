"""Fit on train only, choose on validation exact group+level F1; never read test predictions."""

import argparse
import platform
from itertools import pairwise
from pathlib import Path

import numpy as np
import sklearn

from pdf_heading_benchmark.structure_data import checksum, config_hashes, load_documents
from pdf_heading_benchmark.structure_evaluation import evaluate_documents
from pdf_heading_benchmark.structure_features import (
    pair_features,
    training_groups,
    training_pairs,
    with_context,
)
from pdf_heading_benchmark.supervised_data import write_json
from pdf_heading_benchmark.supervised_features import matrix
from pdf_heading_benchmark.supervised_models import fit_model

VARIANTS = ("expanded_line", "learned_groups", "context_relations")


def training_inputs(documents: list[dict]) -> dict:
    line_rows, groups, pairs, relations = [], [], [], []
    for doc in documents:
        line_rows.extend(
            dict(r, label=doc["labels"][r["id"]]) for r in doc["rows"] if r["id"] in doc["labels"]
        )
        group_rows = training_groups(doc)
        groups.extend(group_rows)
        pairs.extend(training_pairs(doc))
        headings = [with_context(g) for g in group_rows if g["label"] > 0]
        relations.extend(
            dict(pair_features(a, b), label=int(np.sign(b["label"] - a["label"])))
            for a, b in pairwise(headings)
        )
    return {
        "line": line_rows,
        "join": pairs,
        "group": groups,
        "context": [with_context(g) for g in groups],
        "relation": relations,
    }


def train(config: Path, data: Path, output: Path) -> None:
    if output.exists():
        raise ValueError("Use a fresh run directory")
    documents = load_documents(config, data, "train")
    validation = load_documents(config, data, "validation")
    inputs = training_inputs(documents)
    models, sizes, hashes = {}, {}, {}
    for name, rows in inputs.items():
        names = sorted(rows[0]["features"])
        models[name] = fit_model("trees", matrix(rows, names), np.asarray([r["label"] for r in rows]), names)
        path = output / f"{name}.json"
        write_json(path, models[name])
        sizes[name], hashes[name] = path.stat().st_size, checksum(path)
        print(name, len(rows), models[name]["fit_seconds"], flush=True)
    scores = {}
    for variant in VARIANTS:
        scores[variant], audit = evaluate_documents(validation, models, variant)
        write_json(output / f"{variant}-validation-audit.json", audit)
        print(variant, scores[variant]["group_level_f1"], flush=True)
    selected = max(VARIANTS, key=lambda v: scores[v]["group_level_f1"])
    write_json(
        output / "selection.json",
        {
            "selected": selected,
            "selection_metric": "validation exact group and level F1",
            "validation": scores,
            "config_hashes": config_hashes(config),
            "model_hashes": hashes,
            "model_bytes": sizes,
            "fit_seconds": {k: m["fit_seconds"] for k, m in models.items()},
            "training_examples": {k: len(v) for k, v in inputs.items()},
            "train_reports": [d["record"]["id"] for d in documents],
            "validation_reports": [d["record"]["id"] for d in validation],
            "python": platform.python_version(),
            "sklearn": sklearn.__version__,
            "platform": platform.platform(),
        },
    )
    print("Selected:", selected)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/structure-v2"))
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    train(args.config, args.data, args.output)
