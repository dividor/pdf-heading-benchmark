"""Evaluate frozen variants once on fresh held-out pages and the historical diagnostic benchmark."""

import argparse
from pathlib import Path

from pdf_heading_benchmark.evaluation import evaluate
from pdf_heading_benchmark.structure_data import checksum, config_hashes, load_documents
from pdf_heading_benchmark.structure_evaluation import evaluate_documents
from pdf_heading_benchmark.structure_inference import parse_structure
from pdf_heading_benchmark.supervised_data import read_json, write_json
from pdf_heading_benchmark.supervised_inference import markdown_text

VARIANTS = ("expanded_line", "learned_groups", "context_relations")


def frozen_models(config: Path, run: Path) -> tuple[dict, dict]:
    selection = read_json(run / "selection.json")
    if selection["config_hashes"] != config_hashes(config):
        raise ValueError("Labels or protocol changed after selection")
    models = {}
    for name, digest in selection["model_hashes"].items():
        path = run / f"{name}.json"
        if checksum(path) != digest:
            raise ValueError("Changed model")
        models[name] = read_json(path)
    return models, selection


def historical(config: Path, root: Path, models: dict, variant: str, output: Path) -> dict:
    corpus = read_json(config.parent / "corpus.json")
    all_predictions, timings = {}, []
    for record in corpus:
        pdf = root / "corpus" / f"{record['id']}.pdf"
        if checksum(pdf) != record["sha256"]:
            raise ValueError("Wrong historical PDF")
        result = parse_structure(pdf, models, variant)
        all_predictions[record["id"]] = [
            {"page": h["page"], "level": h["level"], "title": h["text"]} for h in result["headings"]
        ]
        write_json(output / variant / record["id"] / "document.json", result)
        (output / variant / record["id"] / "document.md").write_text(markdown_text(result))
        timings.append(
            {"document": record["id"], "pages": record["pages"], "seconds": result["total_seconds"]}
        )
    pages = read_json(config.parent / "audit_pages.json")
    gold = read_json(config.parent / "gold.json")
    audit = {key: [h for h in values if h["page"] in pages[key]] for key, values in all_predictions.items()}
    scores = [
        {"document": key, "method": "structure_" + variant, **evaluate(gold[key], audit[key], pages[key])}
        for key in gold
    ]
    write_json(output / variant / "audit-predictions.json", audit)
    write_json(output / variant / "scores.json", scores)
    return {
        "scores": scores,
        "timings": timings,
        "scope": "Historical diagnostic; inspected before development",
    }


def run_evaluation(args: argparse.Namespace) -> None:
    output = args.run / "evaluation"
    if output.exists():
        raise ValueError("Frozen evaluation already exists")
    models, selection = frozen_models(args.config, args.run)
    documents = load_documents(args.config, args.data, "test")
    results = {}
    original = read_json(args.original_model)
    variants = {"original_v1": ({"line": original}, "expanded_line")}
    variants.update({v: (models, v) for v in VARIANTS})
    for name, (bundle, variant) in variants.items():
        results[name], audit = evaluate_documents(documents, bundle, variant)
        write_json(output / f"{name}-test-audit.json", audit)
        print(name, results[name]["group_level_f1"], flush=True)
    write_json(
        output / "test.json",
        {
            "selected_before_test": selection["selected"],
            "variants": results,
            "original_model_sha256": checksum(args.original_model),
        },
    )
    diagnostics = {}
    for variant in VARIANTS:
        diagnostics[variant] = historical(
            args.config, args.data.parent, models, variant, output / "historical"
        )
        print(variant, sum(s["correct_level"] for s in diagnostics[variant]["scores"]), "/77", flush=True)
    write_json(output / "historical.json", diagnostics)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/structure-v2"))
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--original-model", type=Path, required=True)
    run_evaluation(parser.parse_args())
