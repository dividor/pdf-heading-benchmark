"""Run Xiaomi's upstream two-stage evaluation with PaddleX CPU layout and vLLM Metal.

The upstream GPU layout launcher is replaced only at device selection: the same
PaddleX model, threshold, RGB arrays and upstream region serializer are used.
Recognition, retry policy and assembly execute the pinned upstream CLI unchanged.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pymupdf

from pdf_heading_benchmark.field_output import markdown_headings

REPO = Path(__file__).resolve().parents[2]
UPSTREAM_REVISION = "4abc240285b69a2965cf64762101ddb4ab35f32d"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def run_page(args, detector, serializer, document, key, number):
    started = time.perf_counter()
    folder = args.output / key / f"{number}-upstream"
    folder.mkdir(parents=True)
    image = (
        document[number - 1].get_pixmap(matrix=pymupdf.Matrix(200 / 72, 200 / 72)).pil_image().convert("RGB")
    )
    path = folder / f"{number}.png"
    image.save(path)
    detected = list(detector.predict([np.asarray(image)]))
    if len(detected) != 1:
        raise RuntimeError("Expected one layout result")
    layout = dict(images=[str(path)], layout_result=serializer(detected[0], *image.size))
    (folder / "layout.jsonl").write_text(json.dumps(layout) + "\n")
    command = [
        sys.executable,
        "-m",
        "evaluation_pipeline.twostage_img2md",
        "--input-jsonl",
        str(folder / "layout.jsonl"),
        "--layout-jsonl",
        str(folder / "layout.jsonl"),
        "--output_dir",
        str(folder),
        "--model_path",
        str(args.model),
        "--served_model_name",
        "xiaomi-ocr0",
        "--port",
        "8112",
        "--workers",
        "1",
        "--temperature",
        "0",
        "--top_p",
        "0.8",
        "--presence_penalty",
        "0",
        "--repetition_penalty",
        "1",
        "--max_tokens",
        "16384",
        "--request_timeout",
        "600",
        "--retry-repetitive",
        "--retry-presence-penalty",
        "1.5",
    ]
    environment = dict(os.environ, PYTHONPATH=str(args.upstream))
    with (folder / "command.log").open("w") as handle:
        subprocess.run(
            command, cwd=args.upstream, env=environment, stdout=handle, stderr=subprocess.STDOUT, check=True
        )
    log = (folder / "command.log").read_text()
    summaries = re.findall(r"VLM done: (\d+) success, (\d+) failures", log)
    if len(summaries) != 1 or int(summaries[0][1]) != 0:
        raise RuntimeError("Upstream recognition failed or did not report its completion")
    text = (folder / f"{number}.md").read_text()
    record = dict(
        page=number,
        text=text,
        headings=markdown_headings(text, number),
        seconds=time.perf_counter() - started,
        error=None,
    )
    write(args.output / key / f"{number}.json", record)
    print("DONE", key, number, round(record["seconds"], 2), flush=True)
    return record


def main():
    from paddlex import create_model

    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("model", "layout", "upstream", "input-data", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=args.upstream, text=True).strip()
    if revision != UPSTREAM_REVISION:
        raise ValueError("Unexpected Xiaomi upstream revision")
    sys.path.insert(0, str(args.upstream))
    from evaluation_pipeline.layout_detect_paddlex import serialize_regions

    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "runner.py").write_bytes(Path(__file__).read_bytes())
    pages = {"targeting": [1]} if args.smoke else json.loads((REPO / "configs/audit_pages.json").read_text())
    write(
        args.output / "protocol.json",
        dict(
            created_at=datetime.now(UTC).isoformat(),
            candidate="xiaomi_ocr0_official_metal",
            smoke=args.smoke,
            pages=pages,
            render_dpi=200,
            upstream_revision=revision,
            model=str(args.model),
            layout=str(args.layout),
            layout_device="cpu",
            layout_threshold=0.25,
            source_sha256={
                str(Path(__file__).relative_to(REPO)): hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            },
            input_sha256={
                key: hashlib.sha256((args.input_data / "corpus" / f"{key}.pdf").read_bytes()).hexdigest()
                for key in pages
            },
        ),
    )
    started = time.perf_counter()
    detector = create_model("PP-DocLayoutV3", model_dir=str(args.layout), device="cpu", threshold=0.25)
    load_seconds = time.perf_counter() - started
    records, predictions = [], {}
    for key, selected in pages.items():
        with pymupdf.open(args.input_data / "corpus" / f"{key}.pdf") as doc:
            current = [run_page(args, detector, serialize_regions, doc, key, page) for page in selected]
        records.extend(current)
        predictions[key] = [heading for record in current for heading in record["headings"]]
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
