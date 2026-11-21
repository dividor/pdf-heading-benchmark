"""MinerU 4.2.3 local basic tier, full-document input, no external LLM."""

import importlib.metadata
import json
import os
import time

from docvortex.content.inline import inline_plain_text
from mineru.config import VlmConfig, get_config
from mineru.parser.mineru_parser import MinerUParser
from mineru.types import DocTitleBlock, ParagraphTitleBlock
from runtime import ROOT


def main():
    os.environ["MINERU_HOME"] = str(ROOT / "mineru_runtime")
    config = get_config()
    config.model.small_backend = "onnx"
    config.model.onnx_device = "cpu"
    if config.llm_aided.features.title_leveling or config.llm_aided.features.cross_page_table_cell_merge:
        raise ValueError("External LLM features must be disabled")
    parser = MinerUParser(
        tier="basic", parse_mode="auto", image_analysis=False, vlm_config=VlmConfig(server_url="")
    )
    for item in json.loads((ROOT / "corpus/manifest.json").read_text()):
        out = ROOT / "results" / item["id"]
        out.mkdir(exist_ok=True)
        if (out / "mineru_basic.document.json").exists():
            continue
        print("START", item["id"], flush=True)
        start = time.perf_counter()
        result = parser.parse(item["path"], page_range="all")
        elapsed = time.perf_counter() - start
        (out / "mineru_basic.document.json").write_text(result.to_json())
        (out / "mineru_basic.md").write_text(result.markdown())
        headers = []
        for i, page in enumerate(result.pages, 1):
            for b in page.blocks:
                if isinstance(b, (ParagraphTitleBlock, DocTitleBlock)):
                    headers.append(
                        dict(
                            page=i,
                            title=inline_plain_text(b.content),
                            level=b.level,
                            bbox=list(b.bbox),
                            type=b.type,
                        )
                    )
        (out / "mineru_basic.headings.json").write_text(json.dumps(headers, ensure_ascii=False, indent=2))
        (out / "mineru_basic.run.json").write_text(
            json.dumps(
                dict(
                    version=importlib.metadata.version("mineru"),
                    seconds=elapsed,
                    pages=len(result.pages),
                    headings=len(headers),
                    tier="basic",
                    device="onnx-cpu",
                    parse_mode="auto",
                    image_analysis=False,
                    external_llm=False,
                ),
                indent=2,
            )
        )
        print("DONE", item["id"], elapsed, len(headers), flush=True)


if __name__ == "__main__":
    main()
