"""CLI adapter: give every Qwen speed trial a fresh directory."""

import argparse
import runpy
import sys
from datetime import UTC, datetime
from pathlib import Path

from runtime import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", choices=["Qwen3.6-27B-4bit", "Qwen3.6-35B-A3B-4bit"])
    parser.add_argument("--visual-memory", action="store_true")
    args = parser.parse_args()
    model = args.model
    if args.visual_memory and model != "Qwen3.6-35B-A3B-4bit":
        parser.error("The visual-memory follow-up uses the sparse 35B-A3B model")
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output = ROOT / "qwen-compact" / f"{model}-{stamp}"
    name = "run_qwen_sparse_memory.py" if args.visual_memory else "run_qwen_compact.py"
    script = Path(__file__).with_name(name)
    sys.path.insert(0, str(script.parents[2] / "src"))
    sys.argv = [
        str(script),
        "--input-data",
        str(ROOT),
        "--model-record",
        str(ROOT / "models" / f"download-{model}.json"),
        "--output",
        str(output),
    ]
    if not args.visual_memory:
        sys.argv.extend(["--model", model])
    runpy.run_path(str(script), run_name="__main__")
    print(f"Fresh run saved to {output}. Score/import explicitly; historical rows were not overwritten.")


if __name__ == "__main__":
    main()
