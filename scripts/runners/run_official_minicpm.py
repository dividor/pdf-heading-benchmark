"""Run MiniCPM's full SDK with its documented Ollama / DSpark configuration."""

import argparse
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import pymupdf
import requests

from pdf_heading_benchmark.field_output import markdown_headings

REPO = Path(__file__).resolve().parents[2]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def render_inputs(data, pages, output):
    output.mkdir(parents=True, exist_ok=False)
    for key, selected in pages.items():
        with pymupdf.open(data / "corpus" / f"{key}.pdf") as document:
            for page in selected:
                document[page - 1].get_pixmap(matrix=pymupdf.Matrix(200 / 72, 200 / 72)).save(
                    output / f"{key}-{page}.png"
                )


def collect_outputs(output, pages):
    predictions = {}
    for key, selected in pages.items():
        predictions[key] = []
        for page in selected:
            text = (output / "markdown" / f"{key}-{page}.md").read_text()
            headings = markdown_headings(text, page)
            write(output / key / f"{page}.json", dict(page=page, text=text, headings=headings, error=None))
            predictions[key].extend(headings)
    write(output / "predictions.json", predictions)


def validate_summary(summary, expected_pages):
    counts = summary["counts"]
    if counts["planned"] != expected_pages or counts["ok"] != expected_pages:
        raise RuntimeError("MiniCPM did not complete all planned pages")
    if counts["failed"] or counts["failed_blocks"] or counts["pages_with_failed_blocks"]:
        raise RuntimeError("MiniCPM reported failed recognition blocks")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-data", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--layout", required=True, type=Path)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "runner.py").write_bytes(Path(__file__).read_bytes())
    response = requests.post(
        "http://127.0.0.1:18499/api/show", json={"model": "benchmark-minicpm-ocr"}, timeout=10
    )
    response.raise_for_status()
    served = response.json()
    pins = json.loads((REPO / "configs/official-pipelines.json").read_text())["models"]
    expected = [
        digest for key in ("minicpm_gguf", "minicpm_dspark") for digest in pins[key]["files"].values()
    ]
    if "vision" not in served["capabilities"] or any(
        digest not in served["modelfile"] for digest in expected
    ):
        raise ValueError("Ollama model does not contain the pinned main, vision and draft weights")
    pages = {"targeting": [1]} if args.smoke else json.loads((REPO / "configs/audit_pages.json").read_text())
    markdown_dir = args.output / "markdown"
    markdown_dir.mkdir()
    inputs = [(key, page) for key, selected in pages.items() for page in selected]
    target = markdown_dir / f"{inputs[0][0]}-{inputs[0][1]}.md" if len(inputs) == 1 else markdown_dir
    command = [
        sys.executable,
        "-m",
        "minicpmvocr",
        "parse",
        str(args.output / "images"),
        "-o",
        str(target),
        "--json",
        "--split-images",
        "--device",
        "cpu",
        "--layout-model",
        str(args.layout),
        "--backend",
        "ollama",
        "--server-url",
        "http://127.0.0.1:18499",
        "--model",
        "benchmark-minicpm-ocr",
        "--workers",
        "1",
        "--set",
        "pipeline.overlap_layout=false",
        "--set",
        "pipeline.page_workers=1",
        "--set",
        "decode.temperature=0",
        "--run-tag",
        "audit",
    ]
    write(
        args.output / "protocol.json",
        dict(
            created_at=datetime.now(UTC).isoformat(),
            candidate="minicpm_ocr10_official_ollama",
            smoke=args.smoke,
            pages=pages,
            command=command,
            render_dpi=200,
            ollama_model=served,
            packages={
                n: importlib.metadata.version(n)
                for n in ("minicpm-ocr", "paddleocr", "paddlepaddle", "paddlex")
            },
            source_sha256={
                str(Path(__file__).relative_to(REPO)): hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            },
            input_sha256={
                key: hashlib.sha256((args.input_data / "corpus" / f"{key}.pdf").read_bytes()).hexdigest()
                for key in pages
            },
            timing_scope=(
                "Rendering and full SDK, including CPU pipeline initialization; "
                "server load is outside this timer."
            ),
        ),
    )
    started = time.perf_counter()
    render_inputs(args.input_data, pages, args.output / "images")
    environment = dict(
        os.environ,
        OCR_RUN_ROOT=str(args.output / "upstream"),
        OCR_ASSETS_DIR=str(args.input_data / "official-review/minicpm-assets"),
    )
    with (args.output / "upstream.log").open("w") as handle:
        subprocess.run(command, env=environment, stdout=handle, stderr=subprocess.STDOUT, check=True)
    seconds = time.perf_counter() - started
    summary = json.loads((args.output / "upstream/audit/summary.json").read_text())
    validate_summary(summary, len(inputs))
    write(args.output / "upstream-summary.json", summary)
    collect_outputs(args.output, pages)
    write(args.output / "timing.json", dict(seconds=seconds, pages=sum(map(len, pages.values())), errors=0))
    print("DONE", seconds, flush=True)


if __name__ == "__main__":
    main()
