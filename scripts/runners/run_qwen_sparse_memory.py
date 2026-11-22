"""Test the pinned sparse Qwen model with the original multi-image instructions."""

import argparse
import time
from pathlib import Path

import mlx.core as mx
import pymupdf
from mlx_vlm import load
from run_qwen_compact import REPO, digest, protocol, read, write
from run_qwen_visual_memory import generate_page


def document(args, key, pages, model, processor):
    out = args.output / key
    out.mkdir()
    candidates = read(args.input_data / "results" / key / "pymupdf4llm.headings.json")
    outline = "\n".join(f"PDF page {h['page']}: {h['title']}" for h in candidates)
    tags = read(args.input_data / "results" / key / "pdf_tags_full_context.json")
    memory, records = {}, []
    with pymupdf.open(args.input_data / "corpus" / f"{key}.pdf") as doc:
        for pn in sorted(pages):
            start = time.perf_counter()
            record = generate_page(model, processor, doc, pn, memory, outline, tags, key, out / f"{pn}.json")
            record["outside_generation_seconds"] = time.perf_counter() - start - record["seconds"]
            record["native_text"] = doc[pn - 1].get_text(sort=True)
            write(out / f"{pn}.json", record)
            records.append(record)
            for heading in record["headings"]:
                memory[heading["level"]] = heading
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-data", type=Path, required=True)
    parser.add_argument("--model-record", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.model = "Qwen3.6-35B-A3B-4bit"
    pages = read(REPO / "configs/audit_pages.json")
    registered = protocol(args, pages)
    registered["settings"] = dict(
        target_long_edge=1792,
        memory_long_edge=1280,
        max_memory_pages=6,
        max_tokens=4096,
        temperature=0,
        seed=42,
        timeout_seconds=600,
    )
    registered["memory"] = "Original visual memory: latest predicted heading per level; earlier audit images"
    registered["selection"] = (
        "Follow-up after two single-image trials: retain sparse weights and restore original visual memory"
    )
    for name in ("scripts/runners/run_qwen_sparse_memory.py", "scripts/runners/run_qwen_visual_memory.py"):
        registered["source_sha256"][name] = digest(REPO / name)
    args.output.mkdir(parents=True, exist_ok=False)
    write(args.output / "protocol.json", registered)
    start = time.perf_counter()
    model, processor = load(read(args.model_record)["path"])
    load_seconds = time.perf_counter() - start
    mx.random.seed(42)
    results = {key: document(args, key, selected, model, processor) for key, selected in pages.items()}
    write(
        args.output / "predictions.json",
        {key: [h for record in records for h in record["headings"]] for key, records in results.items()},
    )
    write(
        args.output / "timing.json",
        dict(
            load_seconds=load_seconds,
            documents={
                key: dict(
                    seconds=sum(r["seconds"] for r in records),
                    pages=len(records),
                    outside_generation_seconds=sum(r["outside_generation_seconds"] for r in records),
                    errors=sum(bool(r["error"]) for r in records),
                    timeouts=sum(r["timeout"] for r in records),
                )
                for key, records in results.items()
            },
        ),
    )


if __name__ == "__main__":
    main()
