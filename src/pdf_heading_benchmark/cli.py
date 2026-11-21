"""Commands separate free offline scoring from explicit model and paid API runs."""

import argparse
import os
import subprocess
from pathlib import Path

from pdf_heading_benchmark.corpus import prepare
from pdf_heading_benchmark.evaluation import evaluate_all
from pdf_heading_benchmark.extraction import initialize
from pdf_heading_benchmark.io import REPO, data_root, read_json, write_json
from pdf_heading_benchmark.report import build_report


def run_method(method: str, root: Path) -> None:
    config = read_json(REPO / "configs/methods.json")[method]
    manifest = read_json(root / "corpus/manifest.json")
    environment = dict(os.environ, PDF_BENCHMARK_DATA=str(root))
    for step in config["steps"]:
        command = [
            "uv",
            "run",
            "--no-project",
            "--python",
            "3.12",
            "--with-requirements",
            str(REPO / "configs/environments" / (step["environment"] + ".txt")),
            "python",
            str(REPO / step["script"]),
        ]
        arguments = step.get("args", [])
        if step.get("per_document"):
            for item in manifest:
                subprocess.run(
                    command + arguments + [item["path"], str(root / "results" / item["id"])],
                    env=environment,
                    check=True,
                    cwd=REPO,
                )
        else:
            subprocess.run(command + arguments, env=environment, check=True, cwd=REPO)


def score(root: Path, historical: bool) -> None:
    gold = read_json(REPO / "configs/gold.json")
    pages = read_json(REPO / "configs/audit_pages.json")
    if historical:
        predictions = read_json(REPO / "outputs/audit_predictions.json")
    else:
        methods = read_json(REPO / "configs/methods.json")
        predictions = {}
        for method in methods:
            paths = {key: root / "results" / key / f"{method}.headings.json" for key in gold}
            if all(p.exists() for p in paths.values()):
                predictions[method] = {key: read_json(p) for key, p in paths.items()}
        if not predictions:
            raise ValueError("No complete method outputs; run a method on the four documents first.")
    results = evaluate_all(gold, predictions, pages)
    target = root / "results" / ("historical_scores.json" if historical else "scores.json")
    write_json(target, results)
    for method in predictions:
        rows = [r for r in results if r["method"] == method]
        print(f"{method}: {sum(r['correct_level'] for r in rows)}/{sum(r['gold'] for r in rows)}")
    print(f"Details: {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("download", help="Download public PDFs and verify frozen hashes")
    commands.add_parser("report", help="Regenerate committed HTML/Markdown from frozen results; no API calls")
    scorer = commands.add_parser("score", help="Score complete local outputs")
    scorer.add_argument(
        "--historical", action="store_true", help="Use bundled audit predictions, no model required"
    )
    runner = commands.add_parser("run", help="Run one configuration; hosted configurations incur charges")
    runner.add_argument("method", choices=read_json(REPO / "configs/methods.json"))
    extractor = commands.add_parser("extract", help="Extract your own PDF; all pages, no reference labels")
    extractor.add_argument("method", choices=read_json(REPO / "configs/methods.json"))
    extractor.add_argument("pdf", type=Path)
    extractor.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = data_root()
    if args.command == "download":
        prepare(root)
    elif args.command == "report":
        build_report()
    elif args.command == "score":
        score(root, args.historical)
    elif args.command == "extract":
        output = args.output.expanduser().resolve()
        initialize(args.pdf.expanduser().resolve(), output)
        run_method(args.method, output)
    elif args.command == "run":
        run_method(args.method, root)
