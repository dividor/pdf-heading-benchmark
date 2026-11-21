"""MinerU Pro's direct two-step interface; absent levels remain null."""

import importlib.metadata
import json
import re
import time

import mlx.core as mx
import pymupdf
from mineru_vl_utils import MinerUClient
from mineru_vl_utils.post_process import json2md
from runtime import ROOT


def headings(blocks, page):
    result = []
    for block in blocks:
        if block["type"] in ("title", "doc_title", "paragraph_title"):
            match = re.match(r"^(#{1,6})\s+(.+)", str(json2md([block])).strip(), re.S)
            result.append(
                dict(
                    page=page,
                    title=match[2].strip() if match else block.get("content", ""),
                    level=len(match[1]) if match else None,
                    bbox=block["bbox"],
                )
            )
    return result


def process_page(client, doc, page):
    image = doc[page - 1].get_pixmap(matrix=pymupdf.Matrix(400 / 72, 400 / 72)).pil_image()
    image.thumbnail((2048, 2048))
    start = time.perf_counter()
    blocks = client.two_step_extract(image)
    return dict(
        page=page,
        blocks=blocks,
        text=str(json2md(blocks)),
        headings=headings(blocks, page),
        error=None,
        seconds=time.perf_counter() - start,
        peak_mlx_memory_gb=mx.get_peak_memory() / 1e9,
    )


def main():
    source = json.loads((ROOT / "models/download-MinerU2.5-Pro-2605-1.2B.json").read_text())
    start = time.perf_counter()
    client = MinerUClient(
        backend="mlx-engine",
        model_path=source["path"],
        batch_size=1,
        max_concurrency=1,
        use_tqdm=False,
        image_analysis=False,
    )
    load_seconds = time.perf_counter() - start
    mx.random.seed(42)
    for key, pages in json.loads((ROOT / "reference/audit_pages.json").read_text()).items():
        out = ROOT / "results" / key / "mineru_pro_mlx"
        out.mkdir(parents=True, exist_ok=True)
        with pymupdf.open(ROOT / "corpus" / f"{key}.pdf") as doc:
            for page in pages:
                target = out / f"{page}.json"
                if not target.exists():
                    record = process_page(client, doc, page)
                    target.write_text(json.dumps(record, ensure_ascii=False, indent=2))
                    mx.clear_cache()
        records = [json.loads((out / f"{page}.json").read_text()) for page in pages]
        (out.parent / "mineru_pro_mlx.headings.json").write_text(
            json.dumps([h for r in records for h in r["headings"]])
        )
        (out.parent / "mineru_pro_mlx.md").write_text("\n\n".join(r["text"] for r in records))
        (out.parent / "mineru_pro_mlx.run.json").write_text(
            json.dumps(
                dict(
                    **source,
                    pages=len(records),
                    seconds=sum(r["seconds"] for r in records),
                    load_seconds=load_seconds,
                    mlx_vlm=importlib.metadata.version("mlx-vlm"),
                    errors=0,
                    runtime="MLX bf16",
                )
            )
        )


if __name__ == "__main__":
    main()
