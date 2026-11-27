"""Check pinned Qwen configuration, processor and runner imports without loading weights."""

import argparse
import importlib
import importlib.metadata
import json
from pathlib import Path

import mlx.core as mx
from huggingface_hub import snapshot_download
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import get_model_and_args, load_processor

REPO = Path(__file__).resolve().parents[2]

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--cache", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
pins = json.loads((REPO / "configs/models.json").read_text())
checks = {}
for name in ("qwen_ids", "Qwen3.6-27B-4bit", "Qwen3.6-35B-A3B-4bit"):
    pin = pins[name]
    repo = pin["model"] if name == "qwen_ids" else pin["repo"]
    path = Path(
        snapshot_download(
            repo_id=repo,
            revision=pin["revision"],
            cache_dir=args.cache,
            allow_patterns=["*.json", "*.txt", "*.jinja", "*.model"],
            max_workers=2,
        )
    )
    config = json.loads((path / "config.json").read_text())
    architecture, model_type = get_model_and_args(config, path)
    processor = load_processor(path)
    prompt = apply_chat_template(
        processor,
        config,
        "Return only the current page headings as JSON.",
        num_images=0 if name == "qwen_ids" else 1,
        enable_thinking=False,
    )
    checks[name] = dict(
        repo=repo,
        revision=pin["revision"],
        model_type=model_type,
        implementation=architecture.__name__,
        prompt_characters=len(prompt),
        weights_loaded=False,
    )
imports = [
    "run_qwen_ids",
    "run_qwen_visual_memory",
    "run_qwen_compact",
    "run_qwen_sparse_memory",
    "benchmark_qwen_compact",
    "prepare_model",
]
record = dict(
    models=checks,
    modules={name: bool(importlib.import_module(name)) for name in imports},
    device=str(mx.default_device()),
    metal_available=mx.metal.is_available(),
    versions={name: importlib.metadata.version(name) for name in ("mlx", "mlx-vlm", "transformers")},
    scope="Real pinned configurations, processors, templates and imports. No weight loading or generation.",
)
args.output.parent.mkdir(parents=True, exist_ok=True)
with args.output.open("x") as stream:
    json.dump(record, stream, indent=2)
print(json.dumps(record, indent=2))
