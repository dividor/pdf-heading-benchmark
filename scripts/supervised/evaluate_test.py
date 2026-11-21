"""One final test evaluation of the model already selected using validation."""

import argparse
import hashlib
from pathlib import Path

from pdf_heading_benchmark.supervised_data import read_json, read_labels, write_json
from pdf_heading_benchmark.supervised_models import evaluate


def evaluate_test(data: Path, run: Path, config: Path) -> None:
    if (run / "test.json").exists():
        raise ValueError("Test result already exists; do not overwrite it")
    selection = read_json(run / "selection.json")
    for name in ("labels.tsv", "corpus.json"):
        key = "label_sha256" if name == "labels.tsv" else "corpus_sha256"
        if hashlib.sha256((config / name).read_bytes()).hexdigest() != selection[key]:
            raise ValueError("Labels or corpus changed since model selection")
    path = run / f"{selection['selected']}.json"
    if hashlib.sha256(path.read_bytes()).hexdigest() != selection["selected_model_sha256"]:
        raise ValueError("Selected model changed")
    dataset = read_json(data / "dataset.json")
    for name in ("labels.tsv", "corpus.json"):
        if dataset["config_hashes"][name] != hashlib.sha256((config / name).read_bytes()).hexdigest():
            raise ValueError("Stale dataset")
    rows = [r for r in dataset["rows"] if r["split"] == "test"]
    result, predictions = evaluate(read_json(path), rows, read_labels(config / "labels.tsv"))
    write_json(run / "test.json", result)
    write_json(run / "test-predictions.json", predictions)
    print({k: v for k, v in result.items() if k not in {"per_document", "confusion"}})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/supervised"))
    args = parser.parse_args()
    evaluate_test(args.data, args.run, args.config)
