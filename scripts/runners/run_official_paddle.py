"""Run PaddleOCR's complete Apple Silicon pipeline, preserving its native Markdown."""

import argparse
import hashlib
import importlib.metadata
import json
import time
from datetime import UTC, datetime
from pathlib import Path

import pymupdf

from pdf_heading_benchmark.field_output import markdown_headings

REPO = Path(__file__).resolve().parents[2]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def run_page(pipeline, document, number, output):
    started = time.perf_counter()
    image = output / f"{number}.png"
    image.parent.mkdir(parents=True, exist_ok=True)
    document[number - 1].get_pixmap(matrix=pymupdf.Matrix(200 / 72, 200 / 72)).save(image)
    results = list(pipeline.predict(str(image), temperature=0))
    if len(results) != 1:
        raise RuntimeError(f"Expected one result, received {len(results)}")
    result = results[0]
    text = result.markdown["markdown_texts"]
    result.save_to_json(str(output / f"{number}.upstream.json"))
    record = dict(
        page=number,
        text=text,
        headings=markdown_headings(text, number),
        seconds=time.perf_counter() - started,
        error=None,
    )
    write(output / f"{number}.json", record)
    print("DONE", output.name, number, round(record["seconds"], 2), flush=True)
    return record


def main():
    from paddleocr import PaddleOCRVL

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-data", required=True, type=Path)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--layout", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "runner.py").write_bytes(Path(__file__).read_bytes())
    pages = {"targeting": [1]} if args.smoke else json.loads((REPO / "configs/audit_pages.json").read_text())
    options = dict(
        pipeline_version="v1.6",
        device="cpu",
        vl_rec_backend="mlx-vlm-server",
        vl_rec_server_url="http://127.0.0.1:8111/",
        vl_rec_api_model_name=str(args.model),
        vl_rec_max_concurrency=1,
        use_queues=False,
    )
    if args.layout:
        options["layout_detection_model_dir"] = str(args.layout)
    protocol = dict(
        created_at=datetime.now(UTC).isoformat(),
        candidate="paddleocr_vl16_official",
        pages=pages,
        smoke=args.smoke,
        render_dpi=200,
        temperature=0,
        page_concurrency=1,
        region_concurrency=1,
        options=options,
        packages={n: importlib.metadata.version(n) for n in ("paddlepaddle", "paddleocr", "paddlex")},
        source_sha256={
            str(Path(__file__).relative_to(REPO)): hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        },
        input_sha256={
            key: hashlib.sha256((args.input_data / "corpus" / f"{key}.pdf").read_bytes()).hexdigest()
            for key in pages
        },
        telemetry=(
            "Paddle does not expose per-request finish reasons; token caps and retries are not measured."
        ),
    )
    write(args.output / "protocol.json", protocol)
    started = time.perf_counter()
    pipeline = PaddleOCRVL(**options)
    load_seconds = time.perf_counter() - started
    pipeline.export_paddlex_config_to_yaml(str(args.output / "pipeline.yaml"))
    predictions, records = {}, []
    for key, selected in pages.items():
        with pymupdf.open(args.input_data / "corpus" / f"{key}.pdf") as document:
            current = [run_page(pipeline, document, number, args.output / key) for number in selected]
        predictions[key] = [heading for record in current for heading in record["headings"]]
        records.extend(current)
    write(args.output / "predictions.json", predictions)
    write(
        args.output / "timing.json",
        dict(
            load_seconds=load_seconds,
            seconds=sum(r["seconds"] for r in records),
            pages=len(records),
            errors=0,
        ),
    )


if __name__ == "__main__":
    main()
