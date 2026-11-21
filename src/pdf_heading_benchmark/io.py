"""Repository configuration and external run data."""

import json
import os
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def data_root() -> Path:
    return (
        Path(os.environ.get("PDF_BENCHMARK_DATA", str(REPO.parent / "pdf-heading-benchmark-data")))
        .expanduser()
        .resolve()
    )
