"""Search validation joint F0.5 subject to ≥95% heading precision, then freeze and regress."""

import argparse
import platform
from pathlib import Path

from pdf_heading_benchmark.evaluation import evaluate
from pdf_heading_benchmark.precision_experiment import (
    choose_candidate,
    decision_grid,
    frozen_models,
    heading_records,
    prepare_validation,
    score_documents,
)
from pdf_heading_benchmark.precision_inference import parse_precision
from pdf_heading_benchmark.structure_data import checksum, config_hashes, load_documents
from pdf_heading_benchmark.supervised_data import read_json, write_json
from pdf_heading_benchmark.supervised_inference import markdown_text

SOURCES = [
    "scripts/structure/optimize_precision.py",
    "src/pdf_heading_benchmark/precision_experiment.py",
    "src/pdf_heading_benchmark/precision_inference.py",
    "src/pdf_heading_benchmark/joint_metrics.py",
    "src/pdf_heading_benchmark/evaluation.py",
    "src/pdf_heading_benchmark/structure_features.py",
    "src/pdf_heading_benchmark/structure_inference.py",
    "src/pdf_heading_benchmark/supervised_models.py",
    "src/pdf_heading_benchmark/supervised_features.py",
]


def select(args: argparse.Namespace) -> None:
    if args.output.exists():
        raise ValueError("Use a fresh output directory")
    models = frozen_models(args.config, args.run)
    protocol = {
        "objective": (
            "Maximum validation joint heading+level F0.5 among candidates with heading precision >=0.95; "
            "no predictions fails the gate; no eligible candidate means no selection."
        ),
        "matching": (
            "Same physical page, normalized title similarity >=0.90 using frozen Hungarian assignment; "
            "exact level. Same contract as the league table."
        ),
        "tie_break": (
            "Grid order: learned_groups before context_relations, lower body weight and threshold first; "
            "context relation weight 1 before 0."
        ),
        "grid": decision_grid(),
        "config_hashes": config_hashes(args.config),
        "model_hashes": read_json(args.run / "selection.json")["model_hashes"],
        "source_hashes": {name: checksum(Path(name)) for name in SOURCES},
        "test_status": (
            "Both the v2 test and original league PDFs are previously inspected regression sets. "
            "Neither selects this run. No new independent test."
        ),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "training": "No new fitting: frozen v2 Extra Trees. Model scores are not calibrated probabilities.",
    }
    write_json(args.output / "protocol.json", protocol)
    documents = load_documents(args.config, args.data, "validation")
    cached = prepare_validation(documents, models)
    candidates = []
    for settings in protocol["grid"]:
        score, _ = score_documents(documents, cached, models, settings)
        candidates.append({"settings": settings, "score": score})
        print(settings, score["joint_f05"], score["heading_precision"], flush=True)
    selected = choose_candidate(candidates)
    write_json(args.output / "selection.json", {"selected": selected, "validation": candidates})
    if selected:
        _, audit = score_documents(documents, cached, models, selected["settings"])
        write_json(args.output / "selected-validation-audit.json", audit)
    print("SELECTED", selected, flush=True)


def check_frozen(args: argparse.Namespace) -> dict:
    protocol = read_json(args.output / "protocol.json")
    if protocol["config_hashes"] != config_hashes(args.config):
        raise ValueError("Changed labels or protocol")
    if protocol["model_hashes"] != read_json(args.run / "selection.json")["model_hashes"]:
        raise ValueError("Changed model selection")
    if any(checksum(Path(name)) != digest for name, digest in protocol["source_hashes"].items()):
        raise ValueError("Changed code since validation selection")
    selected = read_json(args.output / "selection.json")["selected"]
    if selected is None:
        raise ValueError("No precision-qualified validation candidate")
    return selected["settings"]


def historical(args: argparse.Namespace, models: dict, settings: dict) -> dict:
    pages = read_json(args.config.parent / "audit_pages.json")
    gold = read_json(args.config.parent / "gold.json")
    scores, timings, audit = [], [], {}
    for record in read_json(args.config.parent / "corpus.json"):
        key = record["id"]
        pdf = args.data.parent / "corpus" / f"{key}.pdf"
        if checksum(pdf) != record["sha256"]:
            raise ValueError("Wrong historical PDF")
        result = parse_precision(pdf, models, settings)
        directory = args.output / "historical" / key
        write_json(directory / "document.json", result)
        (directory / "document.md").write_text(markdown_text(result))
        audit[key] = [h for h in heading_records(result["headings"]) if h["page"] in pages[key]]
        scores.append({"document": key, **evaluate(gold[key], audit[key], pages[key])})
        timings.append({"document": key, "pages": record["pages"], "seconds": result["total_seconds"]})
    write_json(args.output / "historical-audit.json", audit)
    return {"scores": scores, "timings": timings, "scope": "Historical diagnostic; not selection data"}


def regression(args: argparse.Namespace) -> None:
    if (args.output / "regression.json").exists():
        raise ValueError("Regression already recorded")
    settings = check_frozen(args)
    models = frozen_models(args.config, args.run)
    documents = load_documents(args.config, args.data, "test")
    cached = prepare_validation(documents, models)
    baseline = dict(variant="context_relations", body_weight=1.0, min_heading_score=0.0, relation_weight=1.0)
    results = {}
    for name, chosen in (("baseline", baseline), ("selected", settings)):
        results[name], audit = score_documents(documents, cached, models, chosen)
        write_json(args.output / f"{name}-regression-audit.json", audit)
    write_json(args.output / "regression.json", {"settings": settings, "results": results})
    write_json(args.output / "historical.json", historical(args, models, settings))
    print(results, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["select", "regression"])
    parser.add_argument("--config", type=Path, default=Path("configs/structure-v2"))
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    {"select": select, "regression": regression}[arguments.stage](arguments)
