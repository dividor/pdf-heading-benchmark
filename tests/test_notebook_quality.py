"""Validate useful notebook output and the standalone quality-check command."""

import json
import subprocess
import sys

from pdf_heading_benchmark.io import REPO
from pdf_heading_benchmark.notebook_quality import long_streams


def test_long_streams_accepts_strings_and_serialized_line_lists():
    notebook = {
        "cells": [
            {"outputs": [{"output_type": "stream", "text": "short result\n"}]},
            {"outputs": [{"output_type": "stream", "text": ["line\n"] * 41}]},
            {"outputs": [{"output_type": "stream", "text": "x" * 4001}]},
            {"outputs": [{"output_type": "display_data", "data": {"text/plain": "table"}}]},
        ]
    }
    assert long_streams(notebook) == [1, 2]
    assert long_streams({}) == []


def test_notebook_check_command_rejects_long_output(tmp_path):
    path = tmp_path / "example.ipynb"
    path.write_text(json.dumps({"cells": [{"outputs": [{"output_type": "stream", "text": "x" * 4001}]}]}))
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts/quality/check_notebooks.py"), str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "holds long console output" in result.stdout


def test_rebuild_notebook_keeps_code_in_the_real_pipeline():
    notebook = json.loads((REPO / "notebooks/rebuild_heading_model.ipynb").read_text())
    sources = "\n".join("".join(c["source"]) for c in notebook["cells"] if c["cell_type"] == "code")
    for script in ("prepare.py", "train.py", "optimize_precision.py", "run_precision.py"):
        assert script in sources
    assert "--download" in sources
    assert "ExtraTreesClassifier(" not in sources
    assert not long_streams(notebook)
