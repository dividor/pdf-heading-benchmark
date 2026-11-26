"""Run the pinned EvidenceLab parser inside its Docker image, without a database."""

import argparse
import hashlib
import importlib.metadata
import json
import logging
import platform
import time
from pathlib import Path


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def run(repo, corpus, output):
    from pipeline.processors.parsing.parser import ParseProcessor

    output.mkdir(parents=True, exist_ok=False)
    config = json.loads((repo / "configs/evidencelab.json").read_text())
    manifest = json.loads((repo / "configs/corpus.json").read_text())
    protocol = dict(
        config=config,
        platform=platform.platform(),
        packages={name: importlib.metadata.version(name) for name in ("docling", "docling-core", "torch")},
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    )
    write(output / "protocol.json", protocol)
    (output / "runner.py").write_bytes(Path(__file__).read_bytes())
    parser = ParseProcessor(output_dir=str(output / "parsed"), **config["parser"])
    start = time.perf_counter()
    parser.setup()
    write(output / "initialization.json", {"seconds": time.perf_counter() - start})
    results = []
    for item in manifest:
        pdf = corpus / f"{item['id']}.pdf"
        if hashlib.sha256(pdf.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Wrong PDF: {item['id']}")
        start = time.perf_counter()
        result = parser.process_document(
            {"id": item["id"], "sys_filepath": str(pdf), "map_title": item["title"]}
        )
        seconds = time.perf_counter() - start
        write(output / f"{item['id']}.result.json", result)
        if not result["success"]:
            raise RuntimeError(f"EvidenceLab failed: {item['id']}; see saved result")
        results.append(
            {
                "document": item["id"],
                "pages": item["pages"],
                "seconds": seconds,
                "input_sha256": item["sha256"],
            }
        )
        write(output / "timing.json", results)
        print(json.dumps(results[-1]), flush=True)
    parser.teardown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument("--repo", required=True, type=Path)
    arguments.add_argument("--corpus", required=True, type=Path)
    arguments.add_argument("--output", required=True, type=Path)
    args = arguments.parse_args()
    run(args.repo, args.corpus, args.output)
