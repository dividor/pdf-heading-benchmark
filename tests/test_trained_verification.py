"""The reproducibility driver must use newly prepared data and the new model paths."""

import importlib.util
import os
import sys

from pdf_heading_benchmark.io import REPO, write_json


def test_all_trained_methods_use_fresh_model_outputs(tmp_path, monkeypatch):
    path = REPO / "scripts/verification/check_trained_methods.py"
    spec = importlib.util.spec_from_file_location("trained_verification", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    commands, methods = [], []
    monkeypatch.setattr(module.subprocess, "run", lambda command, **kwargs: commands.append(command))
    monkeypatch.setattr(module, "run_method", lambda method, root: methods.append((method, root)))
    monkeypatch.setattr(module.os, "environ", dict(os.environ))
    write_json(tmp_path / "training-verification/supervised-models/selection.json", {"selected": "trees"})
    monkeypatch.setattr(
        sys, "argv", ["verify", "--data", str(tmp_path), "--rebuild", str(tmp_path / "rebuilt")]
    )
    module.main()
    assert len(methods) == 7
    assert all(root == tmp_path for _, root in methods)
    assert commands[0][1:3] == ["scripts/structure/calibrate.py", "select"]
    assert commands[2][2] == "--download"
    assert module.os.environ["PDF_HEADING_STRUCTURE_RUN"] == str(tmp_path / "rebuilt/models")
    assert module.os.environ["PDF_HEADING_MODEL"] == str(
        tmp_path / "training-verification/supervised-models/trees.json"
    )
