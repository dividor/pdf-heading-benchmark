"""Standard CLI entry point for pinned local OCR trials; download then run one model."""

import argparse
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", choices=["minicpm_ocr10", "xiaomi_ocr0", "paddleocr_vl16"])
    parser.add_argument("--cache", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(os.environ.get("PDF_BENCHMARK_DATA", str(REPO.parent / "pdf-heading-benchmark-data")))
    environment = dict(
        os.environ, PYTHONPATH=str(REPO / "src") + os.pathsep + os.environ.get("PYTHONPATH", "")
    )
    records = root / "field-downloads"
    output = (
        args.output or root / "field-trials" / datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") / args.candidate
    )
    subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts/runners/prepare_field_candidates.py"),
            "--cache",
            str(args.cache or root / "models/hub"),
            "--records",
            str(records),
        ],
        check=True,
        env=environment,
    )
    subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts/runners/run_field_candidate.py"),
            args.candidate,
            "--input-data",
            str(root),
            "--downloads",
            str(records),
            "--output",
            str(output),
        ],
        check=True,
        env=environment,
    )
    print(f"Completed external run: {output}")


if __name__ == "__main__":
    main()
