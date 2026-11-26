"""Portable local OCR trials: MLX recognition, optional upstream MiniCPM layout/assembly.

Requires the pinned MLX environment plus minicpm-ocr 1.0.5 for region pipelines.
Gold annotations are never loaded. Each invocation requires a fresh output folder.
"""

import argparse
import hashlib
import importlib.metadata
import json
import time
from datetime import UTC, datetime
from pathlib import Path

import mlx.core as mx
import pymupdf
from mlx_vlm import load, stream_generate
from mlx_vlm.prompt_utils import apply_chat_template
from PIL import Image

from pdf_heading_benchmark.field_output import markdown_headings

REPO = Path(__file__).resolve().parents[2]
DOCUMENT_PROMPT = (
    "Extract all information from the main body of the document image and represent it "
    "in markdown format, ignoring headers and footers. Tables should be expressed in OTSL "
    "format, formulas in the document should be represented using LATEX format, and the "
    "parsing should be organized according to the reading order."
)


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def recognize(model, processor, image, instruction, max_tokens):
    prompt = apply_chat_template(processor, model.config, instruction, num_images=1, enable_thinking=False)
    started = time.perf_counter()
    text, tokens, timeout = "", 0, False
    for chunk in stream_generate(
        model, processor, prompt, image=[image], max_tokens=max_tokens, temperature=0
    ):
        text += chunk.text
        tokens = chunk.generation_tokens
        if time.perf_counter() - started > 600:
            timeout = True
            break
    return dict(
        raw=text,
        tokens=tokens,
        timeout=timeout,
        hit_token_limit=tokens >= max_tokens,
        generation_seconds=time.perf_counter() - started,
    )


def region_page(model, processor, detector, image, candidate):
    from minicpmvocr.postprocess import assemble_markdown, convert_otsl_to_html
    from minicpmvocr.prompts import DEFAULT_PROMPT_MAP, get_element_cfg

    detections = detector.detect([image])[0]
    blocks = detector.crop(image, detections)
    records = []
    for order, block in enumerate(blocks):
        crop = block.pop("image")
        block["order"] = order
        block["content"] = ""
        if crop is not None and not block["skip_vlm"]:
            recipe = get_element_cfg(DEFAULT_PROMPT_MAP, block["label"])
            instruction = recipe["prompt"]
            if candidate == "paddleocr_vl16":
                instruction = {"Text Recognition:": "OCR:", "Chart to Table:": "Chart Recognition:"}.get(
                    instruction, instruction
                )
            record = recognize(model, processor, Image.fromarray(crop), instruction, recipe["max_new_tokens"])
            block.update(record)
            block["content"] = record["raw"]
            if block["label"] == "table" and "<fcel>" in record["raw"]:
                block["content"] = convert_otsl_to_html(record["raw"])
            print("REGION", order, block["label"], record["tokens"], flush=True)
            mx.clear_cache()
        records.append(block)
    return assemble_markdown(records, DEFAULT_PROMPT_MAP), records


def setup(args, pins):
    if not mx.metal.is_available() or mx.default_device() != mx.gpu:
        raise RuntimeError("Metal GPU required; no CPU recognition fallback")
    model_pin = pins[args.candidate]
    record = read(args.downloads / (model_pin["repo"].split("/")[-1] + ".download.json"))
    if any(record[k] != model_pin[k] for k in ("repo", "revision")):
        raise ValueError("Downloaded weights differ from the declared model revision")
    started = time.perf_counter()
    model, processor = load(record["path"])
    detector = None
    if args.candidate != "xiaomi_ocr0":
        import torch
        from minicpmvocr.layouts.ppdoclayout3_torch import PPDocLayoutV3TorchDetector

        torch.set_num_threads(4)
        layout = read(args.downloads / "PP-DocLayoutV3_safetensors.download.json")
        if layout["revision"] != pins["layout"]["revision"]:
            raise ValueError("Layout model revision mismatch")
        detector = PPDocLayoutV3TorchDetector(
            dict(
                model_dir=layout["path"],
                device="cpu",
                threshold=0.3,
                nms=True,
                use_chart_recognition=True,
                use_seal_recognition=True,
                use_ocr_for_image_block=False,
            )
        )
        detector.start()
    mx.random.seed(42)
    return model, processor, detector, time.perf_counter() - started


def process_page(args, model, processor, detector, doc, page):
    started = time.perf_counter()
    image = doc[page - 1].get_pixmap(matrix=pymupdf.Matrix(200 / 72, 200 / 72)).pil_image()
    if detector is None:
        record = recognize(model, processor, image, DOCUMENT_PROMPT, 16384)
        text, regions = record["raw"], [record]
    else:
        text, regions = region_page(model, processor, detector, image, args.candidate)
    return dict(
        page=page,
        image_size=list(image.size),
        text=text,
        regions=regions,
        headings=markdown_headings(text, page),
        seconds=time.perf_counter() - started,
        tokens=sum(r.get("tokens", 0) for r in regions),
        timeout=any(r.get("timeout", False) for r in regions),
        hit_token_limit=any(r.get("hit_token_limit", False) for r in regions),
        error=None,
        peak_mlx_memory_gb=mx.get_peak_memory() / 1e9,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", choices=["minicpm_ocr10", "xiaomi_ocr0", "paddleocr_vl16"])
    parser.add_argument("--input-data", type=Path, required=True)
    parser.add_argument("--downloads", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--smoke", action="store_true", help="One non-audit cover page; no score import")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    pins = read(REPO / "configs/field-candidates.json")["models"]
    pages = {"targeting": [1]} if args.smoke else read(REPO / "configs/audit_pages.json")
    write(
        args.output / "protocol.json",
        dict(
            created_at=datetime.now(UTC).isoformat(),
            candidate=args.candidate,
            models=pins,
            pages=pages,
            smoke=args.smoke,
            render_dpi=200,
            temperature=0,
            seed=42,
            page_concurrency=1,
            region_concurrency=1,
            recognition_device=str(mx.default_device()),
            device_info=mx.device_info(),
            layout_device="cpu" if args.candidate != "xiaomi_ocr0" else None,
            source_sha256={
                str(Path(__file__).relative_to(REPO)): hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            },
            input_sha256={
                key: hashlib.sha256((args.input_data / "corpus" / f"{key}.pdf").read_bytes()).hexdigest()
                for key in pages
            },
            packages={
                n: importlib.metadata.version(n) for n in ("mlx", "mlx-vlm", "transformers", "pymupdf")
            },
            scope="Rendering, CPU layout, MLX recognition and assembly; load recorded separately. "
            "Region runs use MiniCPM SDK 1.0.5 layout/crop/Markdown components; Paddle changes task prompts. "
            "Xiaomi uses whole-page Markdown. These are Apple Silicon adaptations, not CUDA replications.",
        ),
    )
    model, processor, detector, load_seconds = setup(args, pins)
    predictions, totals = {}, []
    for key, selected in pages.items():
        predictions[key] = []
        with pymupdf.open(args.input_data / "corpus" / f"{key}.pdf") as doc:
            for page in selected:
                record = process_page(args, model, processor, detector, doc, page)
                write(args.output / key / f"{page}.json", record)
                predictions[key].extend(record["headings"])
                totals.append(record)
                print("DONE", key, page, round(record["seconds"], 2), len(record["headings"]), flush=True)
                mx.clear_cache()
    write(args.output / "predictions.json", predictions)
    write(
        args.output / "timing.json",
        dict(
            load_seconds=load_seconds,
            seconds=sum(r["seconds"] for r in totals),
            pages=len(totals),
            errors=0,
            timeouts=sum(r["timeout"] for r in totals),
            token_limits=sum(r["hit_token_limit"] for r in totals),
        ),
    )


if __name__ == "__main__":
    main()
