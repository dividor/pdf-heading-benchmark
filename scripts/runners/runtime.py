"""External run directory, shared by the standalone backend scripts."""

import os
from pathlib import Path

ROOT = Path(os.environ.get("PDF_BENCHMARK_DATA", "../pdf-heading-benchmark-data")).expanduser().resolve()
