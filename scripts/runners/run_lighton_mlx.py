"""Native Apple Silicon runtime; same model, prompt and greedy decoding."""

import importlib.metadata
import json
import time

import mlx.core as mx
import pymupdf
from mlx_vlm import load, stream_generate
from mlx_vlm.prompt_utils import apply_chat_template
from parse_lighton import decode
from runtime import ROOT

MODEL = "lightonai/LightOnOCR-3-0.8B"
REVISION = "36d8636925327c671bd8e479c517a004f7566bd9"
start = time.perf_counter()
model, processor = load(MODEL, revision=REVISION)
load_seconds = time.perf_counter() - start
mx.random.seed(42)
prompt = apply_chat_template(processor, model.config, "grounding", num_images=1, enable_thinking=False)
for key, pages in json.loads((ROOT / "reference/audit_pages.json").read_text()).items():
    doc = pymupdf.open(ROOT / "corpus" / f"{key}.pdf")
    out = ROOT / "results" / key / "lighton_mlx"
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for pn in pages:
        target = out / f"{pn}.json"
        if target.exists():
            record = json.loads(target.read_text())
            record["headings"] = decode(record["text"], pn)
            records.append(record)
            continue
        im = doc[pn - 1].get_pixmap(matrix=pymupdf.Matrix(400 / 72, 400 / 72)).pil_image()
        im.thumbnail((2048, 2048))
        begin = time.perf_counter()
        text = ""
        truncated = False
        for chunk in stream_generate(model, processor, prompt, image=[im], max_tokens=8192, temperature=0):
            text += chunk.text
            if chunk.generation_tokens % 500 == 0:
                print(key, pn, "tokens", chunk.generation_tokens, flush=True)
            if time.perf_counter() - begin > 300:
                truncated = True
                break
        headings = decode(text, pn)
        record = dict(
            page=pn,
            seconds=time.perf_counter() - begin,
            tokens=chunk.generation_tokens,
            hit_token_limit=chunk.generation_tokens >= 8192,
            timeout=truncated,
            headings=headings,
            text=text,
        )
        target.write_text(json.dumps(record, ensure_ascii=False, indent=2))
        records.append(record)
        print("DONE", key, pn, record["seconds"], record["tokens"], len(headings), flush=True)
        mx.clear_cache()
    (out.parent / "lighton_mlx.headings.json").write_text(
        json.dumps([h for r in records for h in r["headings"]], ensure_ascii=False, indent=2)
    )
    (out.parent / "lighton_mlx.run.json").write_text(
        json.dumps(
            dict(
                model=MODEL,
                revision=REVISION,
                runtime="mlx",
                load_seconds=load_seconds,
                pages=len(records),
                seconds=sum(r["seconds"] for r in records),
                generation="greedy",
                max_tokens=8192,
                timeout_per_page=300,
                mlx_vlm=importlib.metadata.version("mlx-vlm"),
            ),
            indent=2,
        )
    )
