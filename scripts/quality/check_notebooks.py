#!/usr/bin/env python3
"""Reject long console output while retaining compact notebook results."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pdf_heading_benchmark.notebook_quality import long_streams


def main() -> int:
    """Check each notebook named on the command line and return 1 if any needs trimming."""
    untrimmed = [
        name for name in sys.argv[1:] if long_streams(json.loads(Path(name).read_text(encoding="utf-8")))
    ]
    for name in untrimmed:
        print(f"{name} holds long console output: write full logs outside Git and retain a compact summary")
    return 1 if untrimmed else 0


if __name__ == "__main__":
    sys.exit(main())
