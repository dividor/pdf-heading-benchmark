"""Load the selected refitted models with artifact identity checks."""

from pathlib import Path

from pdf_heading_benchmark.structure_data import checksum
from pdf_heading_benchmark.supervised_data import read_json


def load_recall(run: Path) -> tuple[dict, dict]:
    selection = read_json(run / "selection.json")
    models = {}
    for name, digest in selection["model_hashes"].items():
        path = run / f"{name}.json"
        if checksum(path) != digest:
            raise ValueError("Changed selected model")
        models[name] = read_json(path)
    return models, selection["selected"]["settings"]
