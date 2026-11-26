"""OvisOCR3 documented vLLM inference and Markdown prompt on the Metal hardware plugin.

The upstream example uses vLLM 0.22.1 and Triton. This Mac uses vLLM 0.34.0
and its Metal plugin. The prompt, pixel bounds, sampling and cleanup are upstream.
"""

import argparse
import hashlib
import importlib.metadata
import json
import time
from datetime import UTC, datetime
from pathlib import Path

import pymupdf
from vllm import LLM, SamplingParams

from pdf_heading_benchmark.field_output import markdown_headings
from pdf_heading_benchmark.ovis_output import document_markdown

REPO = Path(__file__).resolve().parents[2]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def infer_page(model, tokenizer, prompt, document, number, output):
    started = time.perf_counter()
    image = (
        document[number - 1].get_pixmap(matrix=pymupdf.Matrix(200 / 72, 200 / 72)).pil_image().convert("RGB")
    )
    content = [{"type": "image"}, {"type": "text", "text": prompt}]
    rendered = tokenizer.apply_chat_template(
        [{"role": "user", "content": content}],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    request = dict(
        prompt=rendered,
        multi_modal_data={"image": [image]},
        mm_processor_kwargs={
            "images_kwargs": {"size": {"shortest_edge": 448 * 448, "longest_edge": 2880 * 2880}}
        },
    )
    response = model.generate([request], SamplingParams(max_tokens=16384, temperature=0))[0].outputs[0]
    text = document_markdown(response.text)
    record = dict(
        page=number,
        raw=response.text,
        text=text,
        headings=markdown_headings(text, number),
        finish_reason=response.finish_reason,
        tokens=len(response.token_ids),
        seconds=time.perf_counter() - started,
        error=None,
    )
    write(output / f"{number}.json", record)
    print("DONE", output.name, number, round(record["seconds"], 2), response.finish_reason, flush=True)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--input-data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "runner.py").write_bytes(Path(__file__).read_bytes())
    pages = {"targeting": [1]} if args.smoke else json.loads((REPO / "configs/audit_pages.json").read_text())
    prompt = (args.model / "prompts/document_markdown.txt").read_text()
    options = dict(
        model=str(args.model),
        tensor_parallel_size=1,
        gpu_memory_utilization=0.8,
        limit_mm_per_prompt={"image": 2},
        max_num_seqs=1,
        seed=42,
    )
    write(
        args.output / "protocol.json",
        dict(
            created_at=datetime.now(UTC).isoformat(),
            candidate="ovisocr3_official_metal",
            smoke=args.smoke,
            pages=pages,
            render_dpi=200,
            prompt=prompt,
            model_options=options,
            min_pixels=448 * 448,
            max_pixels=2880 * 2880,
            temperature=0,
            max_tokens=16384,
            packages={
                n: importlib.metadata.version(n)
                for n in ("vllm", "vllm-metal", "mlx", "mlx-vlm", "transformers")
            },
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
    model = LLM(**options)
    tokenizer = model.get_tokenizer()
    load_seconds = time.perf_counter() - started
    records, predictions = [], {}
    for key, selected in pages.items():
        with pymupdf.open(args.input_data / "corpus" / f"{key}.pdf") as doc:
            current = [
                infer_page(model, tokenizer, prompt, doc, page, args.output / key) for page in selected
            ]
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
            token_limits=sum(r["finish_reason"] == "length" for r in records),
        ),
    )


if __name__ == "__main__":
    main()
