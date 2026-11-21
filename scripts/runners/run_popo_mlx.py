"""Docling candidates + upstream Popo hierarchy stage, locally with MLX 8-bit.

Uses upstream filtering, 8-page chunking (bounded for Mac memory), page mosaics and overlap alignment.
Only the title task is run; no summaries, external APIs or gold annotations.
"""

import base64
import importlib.metadata
import io
import json
import sys
import time

import mlx.core as mx
from mlx_vlm import load, stream_generate
from mlx_vlm.prompt_utils import apply_chat_template
from PIL import Image
from runtime import ROOT

sys.path.insert(0, str(ROOT / "vendor/MinerU-Popo/post_processing"))
from inference import (
    adaptive_chunk,
    add_title,
    concatenate_pdf_pages_with_border,
    extract_label2,
    filter_title,
    parse_string_notype,
)


def candidates(source):
    blocks = []
    records = []
    # Follow body text/groups in reading order. Table/picture subtrees are excluded;
    # their cell/caption titles are not input candidates in this adapter.
    lookup = {t["self_ref"]: t for t in source["texts"]}
    groups = {t["self_ref"]: t for t in source.get("groups", [])}

    def walk(node):
        for child in node.get("children", []):
            ref = child["$ref"]
            if ref in lookup:
                t = lookup[ref]
                if t["label"] != "section_header" or not t.get("prov"):
                    continue
                p = t["prov"][0]
                pn = p["page_no"]
                box = p["bbox"]
                size = source["pages"][str(pn)]["size"]
                w, h = size["width"], size["height"]
                y1, y2 = (
                    (h - box["t"], h - box["b"])
                    if box.get("coord_origin") == "BOTTOMLEFT"
                    else (box["t"], box["b"])
                )
                bbox = [box["l"] / w, y1 / h, box["r"] / w, y2 / h]
                blocks.append(dict(type="title", content=t["text"], page=pn, bbox=bbox))
                records.append(dict(page=pn, title=t["text"], bbox=bbox, level=None, ref=ref))
            elif ref in groups:
                walk(groups[ref])

    walk(source["body"])
    return blocks, records


def infer_chunk(model, processor, item, ix, rng, chunk, target):
    pages = sorted({b["page"] for b in chunk if rng[0] <= b["page"] <= rng[1]})
    im = Image.open(
        io.BytesIO(base64.b64decode(concatenate_pdf_pages_with_border(item["path"], pages)))
    ).convert("RGB")
    text = "<image>\nTitle Level Analysis: " + "\n".join(
        f"<|id|>{b['id']}<|page|>{b['page']}<|box|>{b['box']}<|content|>{b['content']}" for b in chunk
    )
    prompt = apply_chat_template(processor, model.config, text, num_images=1)
    begin = time.perf_counter()
    answer = ""
    print("START", item["id"], ix, rng, len(pages), im.size, len(chunk), flush=True)
    for gen in stream_generate(
        model,
        processor,
        prompt,
        image=[im],
        temperature=0,
        max_tokens=8192,
        prefill_step_size=256,
    ):
        answer += gen.text
        if gen.generation_tokens % 200 == 0:
            print("TOKENS", item["id"], ix, gen.generation_tokens, flush=True)
    j = dict(
        range=rng,
        pages=pages,
        prompt=text,
        raw_response=answer,
        parsed=extract_label2(answer),
        seconds=time.perf_counter() - begin,
        tokens=gen.generation_tokens,
        prompt_tokens=gen.prompt_tokens,
        peak_memory=gen.peak_memory,
        finish_reason=gen.finish_reason,
    )
    target.write_text(json.dumps(j, ensure_ascii=False, indent=2))
    print("DONE", item["id"], ix, j["seconds"], len(j["parsed"]), flush=True)
    mx.clear_cache()
    return j


def align_overlap(j, all_results):
    # Upstream overlap-based bias synchronization.
    pairs = j["parsed"]
    bias = []
    for pair in pairs:
        for exist in all_results:
            if pair["id"] == exist["id"]:
                if pair["level"] < 0 or exist["level"] < 0:
                    pair["level"] = exist["level"] = -1
                else:
                    bias.append(pair["level"] - exist["level"])
                    pair["level"] = exist["level"]
                break
    avg = round(sum(bias) / len(bias)) if bias else 0
    for pair in pairs:
        if not any(p["id"] == pair["id"] for p in all_results):
            pair["level"] = pair["level"] - avg if pair["level"] > 0 else pair["level"]
            all_results.append(pair)


def main():
    start = time.perf_counter()
    model, processor = load(str(ROOT / "models/popo-8bit"))
    load_seconds = time.perf_counter() - start
    mx.random.seed(42)
    for item in json.loads((ROOT / "corpus/manifest.json").read_text()):
        out = ROOT / "results" / item["id"]
        raw = out / "popo_docling"
        raw.mkdir(exist_ok=True)
        source = json.loads((out / "docling_default.document.json").read_text())
        blocks, records = candidates(source)
        ranges, chunks = adaptive_chunk(parse_string_notype(add_title(filter_title(blocks))), chunk_size=8)
        all_results = []
        timings = []
        for ix, (rng, chunk) in enumerate(zip(ranges, chunks, strict=False)):
            target = raw / f"chunk-{ix}.json"
            if target.exists():
                j = json.loads(target.read_text())
            else:
                j = infer_chunk(model, processor, item, ix, rng, chunk, target)
            timings.append(j["seconds"])
            align_overlap(j, all_results)
        for pair in all_results:
            if 0 <= pair["id"] < len(records):
                records[pair["id"]]["level"] = pair["level"]
        (out / "popo_docling.candidates.json").write_text(json.dumps(records, ensure_ascii=False, indent=2))
        # Upstream tree construction demotes candidates without a nonnegative level to text.
        accepted = [h for h in records if h["level"] is not None and h["level"] >= 0]
        (out / "popo_docling.headings.json").write_text(json.dumps(accepted, ensure_ascii=False, indent=2))
        (out / "popo_docling.run.json").write_text(
            json.dumps(
                dict(
                    model="DreamEternal/MinerU-Popo",
                    revision="af75342abdc5cbd461264521c9ef46719ff74190",
                    quantization="MLX affine 8-bit group64",
                    runtime=importlib.metadata.version("mlx-vlm"),
                    chunk_pages=8,
                    overlap_pages=1,
                    seconds=sum(timings),
                    load_seconds=load_seconds,
                    chunks=len(chunks),
                    headings=len(records),
                    levels_assigned=sum(h["level"] is not None for h in records),
                ),
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
