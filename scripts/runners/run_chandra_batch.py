"""Chandra/LightOn OCR with upstream prompts and rendering in independent MLX batches."""

import importlib.metadata
import json
import runpy
import time

import mlx.core as mx
import pymupdf
from decode_chandra import chandra_headings
from mineru_vl_utils.vlm_client.base_client import SamplingParams
from mineru_vl_utils.vlm_client.mlx_client import MlxVlmClient
from mlx_vlm import load
from mlx_vlm.prompt_utils import apply_chat_template
from parse_lighton import decode
from runtime import ROOT

METHOD = "chandra2_mlx"


def render_batch(doc, batch, kind, scale):
    images = []
    for pn in batch:
        if kind == "chandra2":
            dpi = max(192, 1024 / min(doc[pn - 1].rect.width, doc[pn - 1].rect.height) * 72)
            images.append(
                scale(doc[pn - 1].get_pixmap(matrix=pymupdf.Matrix(dpi / 72, dpi / 72)).pil_image())
            )
        else:
            im = doc[pn - 1].get_pixmap(matrix=pymupdf.Matrix(400 / 72, 400 / 72)).pil_image()
            im.thumbnail((2048, 2048))
            images.append(im)
    return images


def main(kind="chandra2"):
    method = "chandra2_mlx" if kind == "chandra2" else "lighton4b_mlx"
    name = "chandra-ocr-2" if kind == "chandra2" else "LightOnOCR-3-4B"
    source = json.loads((ROOT / f"models/download-{name}.json").read_text())
    begin = time.perf_counter()
    model, processor = load(source["path"])
    load_seconds = time.perf_counter() - begin
    scale = runpy.run_path(str(ROOT / "vendor/chandra/chandra/model/util.py"))["scale_to_fit"]
    prompt = (
        (ROOT / "vendor/chandra_ocr_layout_prompt.txt").read_text() if kind == "chandra2" else "grounding"
    )
    batch_size = 4 if kind == "chandra2" else 2
    if kind == "chandra2":
        import mineru_vl_utils.vlm_client.mlx_client as mlx_client_module

        mlx_client_module.MLX_BATCH_PIXEL_BUDGET = 16_000_000
    client = MlxVlmClient(
        model, processor, prompt=prompt, system_prompt="", batch_size=batch_size, use_tqdm=False
    )
    # Verify batching does not silently alter the author's chat template.
    standard = apply_chat_template(processor, model.config, prompt, num_images=1, enable_thinking=False)
    wrapped = processor.apply_chat_template(
        client.build_messages(prompt, True), tokenize=False, add_generation_prompt=True
    )
    if standard != wrapped:
        raise ValueError("Batch wrapper changes the standard prompt")
    params = SamplingParams(temperature=0, top_p=1, top_k=0, max_new_tokens=12384)
    mx.random.seed(42)
    for key, pages in json.loads((ROOT / "reference/audit_pages.json").read_text()).items():
        out = ROOT / "results" / key / method
        out.mkdir(parents=True, exist_ok=True)
        doc = pymupdf.open(ROOT / "corpus" / f"{key}.pdf")
        pending = [n for n in pages if not (out / f"{n}.json").exists()]
        for offset in range(0, len(pending), batch_size):
            batch = pending[offset : offset + batch_size]
            images = []
            images = render_batch(doc, batch, kind, scale)
            print("START", key, batch, flush=True)
            begin = time.perf_counter()
            raw = client.batch_predict(images, prompts=[prompt] * len(batch), sampling_params=params)
            elapsed = time.perf_counter() - begin
            for pn, text in zip(batch, raw, strict=False):
                tokens = len(processor.tokenizer.encode(text, add_special_tokens=False))
                heads = chandra_headings(text, pn) if kind == "chandra2" else decode(text, pn)
                record = dict(
                    page=pn,
                    text=text,
                    headings=heads,
                    error=None,
                    seconds=elapsed / len(batch),
                    batch_seconds=elapsed,
                    batch_pages=batch,
                    time_note="batch wall time allocated equally; not individual page latency",
                    tokens=tokens,
                    hit_token_limit=tokens >= 12384,
                    timeout=False,
                    peak_mlx_memory_gb=mx.get_peak_memory() / 1e9,
                )
                (out / f"{pn}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2))
                print(
                    "DONE", key, pn, round(record["seconds"], 1), tokens, len(record["headings"]), flush=True
                )
            mx.clear_cache()
        records = [json.loads((out / f"{pn}.json").read_text()) for pn in pages]
        (out.parent / f"{method}.headings.json").write_text(
            json.dumps([h for r in records for h in r["headings"]], ensure_ascii=False, indent=2)
        )
        (out.parent / f"{method}.md").write_text(
            "\n\n".join(f"<!-- Original PDF page {r['page']} -->\n" + r["text"] for r in records)
        )
        (out.parent / f"{method}.run.json").write_text(
            json.dumps(
                dict(
                    **source,
                    pages=len(records),
                    seconds=sum(r["seconds"] for r in records),
                    load_seconds=load_seconds,
                    runtime=f"MLX bf16 batch size {batch_size}",
                    api_cost_usd=0,
                    mlx_vlm=importlib.metadata.version("mlx-vlm"),
                    errors=0,
                    scope=(
                        "audit pages; independent image prompts; upstream prompt/rendering; "
                        "any earlier single-page checkpoints retained"
                    ),
                    max_tokens=12384,
                    temperature=0,
                ),
                indent=2,
            )
        )


if __name__ == "__main__":
    import sys

    main(sys.argv[1] if len(sys.argv) > 1 else "chandra2")
