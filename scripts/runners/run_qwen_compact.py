"""Run either pinned Qwen model with one image, without loading reference labels.

Requires the optional MLX environment and an installed benchmark package (or
PYTHONPATH=src). Each output directory must be new. Both model variants share the
same prompt and generation settings. Keep model weights and output outside Git.
"""

import argparse
import hashlib
import importlib.metadata
import json
import platform
import time
from datetime import UTC, datetime
from pathlib import Path

import mlx.core as mx
import pymupdf
from decode_qwen import parse
from mlx_vlm import load, stream_generate
from mlx_vlm.prompt_utils import apply_chat_template

from pdf_heading_benchmark.compact_prompt import content

REPO = Path(__file__).resolve().parents[2]
SETTINGS = dict(image_long_edge=1280, max_tokens=4096, temperature=0, seed=42, timeout_seconds=600)


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protocol(args, pages):
    model = read(REPO / "configs/models.json")[args.model]
    source = read(args.model_record)
    if any(source[k] != model[k] for k in ("repo", "revision")):
        raise ValueError("Model record differs from pinned model configuration")
    inputs = {}
    for key in pages:
        paths = [args.input_data / "corpus" / f"{key}.pdf"]
        paths += [
            args.input_data / "results" / key / name
            for name in ("pymupdf4llm.headings.json", "pdf_tags_full_context.json")
        ]
        inputs.update({str(p.relative_to(args.input_data)): digest(p) for p in paths})
    sources = [Path(__file__), REPO / "src/pdf_heading_benchmark/compact_prompt.py"]
    sources += [REPO / "scripts/runners/decode_qwen.py", REPO / "configs/audit_pages.json"]
    return dict(
        created_at=datetime.now(UTC).isoformat(),
        model=model,
        settings=SETTINGS,
        enable_thinking=False,
        pages=pages,
        input_sha256=inputs,
        source_sha256={str(p.relative_to(REPO)): digest(p) for p in sources},
        packages={
            name: importlib.metadata.version(name)
            for name in ("mlx", "mlx-vlm", "transformers", "pymupdf", "huggingface-hub", "pillow")
        },
        python=platform.python_version(),
        platform=platform.platform(),
        scope="32 historical audit pages; regression, not an independent test",
        selection="Two model variants fixed before scoring; report both, no score-driven retries",
        memory="Most recent prediction per level, from earlier sampled pages in this document",
        timing="Generation includes input processing; excludes downloads, loading and candidate extraction",
    )


def generate(model, processor, prompt, image):
    start = time.perf_counter()
    raw, tokens, prompt_tokens, first_token = "", 0, None, None
    timeout = False
    for chunk in stream_generate(
        model, processor, prompt, image=[image], max_tokens=SETTINGS["max_tokens"], temperature=0
    ):
        elapsed = time.perf_counter() - start
        if first_token is None:
            first_token = elapsed
        raw += chunk.text
        tokens = chunk.generation_tokens
        prompt_tokens = getattr(chunk, "prompt_tokens", None)
        if elapsed > SETTINGS["timeout_seconds"]:
            timeout = True
            break
    return dict(
        raw=raw,
        seconds=time.perf_counter() - start,
        first_token_seconds=first_token,
        prompt_tokens=prompt_tokens,
        tokens=tokens,
        timeout=timeout,
        hit_token_limit=tokens >= SETTINGS["max_tokens"],
    )


def page_record(model, processor, doc, pn, memory, outline, tags):
    start = time.perf_counter()
    native = doc[pn - 1].get_text(sort=True)
    image = doc[pn - 1].get_pixmap(matrix=pymupdf.Matrix(2, 2)).pil_image()
    image.thumbnail((SETTINGS["image_long_edge"], SETTINGS["image_long_edge"]))
    text = content(pn, native, outline, tags, json.dumps(list(memory.values()), ensure_ascii=False))
    prompt = apply_chat_template(processor, model.config, text, num_images=1, enable_thinking=False)
    preparation = time.perf_counter() - start
    record = generate(model, processor, prompt, image)
    record.update(
        page=pn,
        prompt=text,
        image_size=list(image.size),
        preparation_seconds=preparation,
        native_text=native,
        error=None,
        peak_mlx_memory_gb=mx.get_peak_memory() / 1e9,
    )
    try:
        record["headings"] = parse(record["raw"], pn)
    except (ValueError, KeyError, TypeError) as exc:
        record.update(headings=[], error=f"{type(exc).__name__}: {exc}")
    mx.clear_cache()
    return record


def document(args, key, pages, model, processor):
    out = args.output / key
    out.mkdir()
    candidates = read(args.input_data / "results" / key / "pymupdf4llm.headings.json")
    outline = "\n".join(f"PDF page {h['page']}: {h['title']}" for h in candidates)
    tags = json.dumps(
        read(args.input_data / "results" / key / "pdf_tags_full_context.json"), ensure_ascii=False
    )
    memory, records = {}, []
    with pymupdf.open(args.input_data / "corpus" / f"{key}.pdf") as doc:
        for pn in sorted(pages):
            print("START", key, pn, flush=True)
            record = page_record(model, processor, doc, pn, memory, outline, tags)
            write(out / f"{pn}.json", record)
            records.append(record)
            for h in record["headings"]:
                memory[h["level"]] = h
            print("DONE", key, pn, round(record["seconds"], 2), len(record["headings"]), flush=True)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-data", type=Path, required=True)
    parser.add_argument("--model", choices=["Qwen3.6-27B-4bit", "Qwen3.6-35B-A3B-4bit"], required=True)
    parser.add_argument("--model-record", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    pages = read(REPO / "configs/audit_pages.json")
    registered = protocol(args, pages)
    args.output.mkdir(parents=True, exist_ok=False)
    write(args.output / "protocol.json", registered)
    start = time.perf_counter()
    model, processor = load(read(args.model_record)["path"])
    load_seconds = time.perf_counter() - start
    mx.random.seed(SETTINGS["seed"])
    results = {key: document(args, key, selected, model, processor) for key, selected in pages.items()}
    write(
        args.output / "predictions.json",
        {k: [h for r in rs for h in r["headings"]] for k, rs in results.items()},
    )
    write(
        args.output / "timing.json",
        dict(
            load_seconds=load_seconds,
            documents={
                key: dict(
                    seconds=sum(r["seconds"] for r in records),
                    preparation_seconds=sum(r["preparation_seconds"] for r in records),
                    pages=len(records),
                    errors=sum(bool(r["error"]) for r in records),
                    timeouts=sum(r["timeout"] for r in records),
                )
                for key, records in results.items()
            },
        ),
    )


if __name__ == "__main__":
    main()
