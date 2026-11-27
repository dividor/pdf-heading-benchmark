"""Optional model dependencies must not inherit an existing developer environment."""

from pdf_heading_benchmark.cli import runner_command


def test_backend_environment_is_isolated():
    command = runner_command({"environment": "docling", "script": "scripts/runners/run_docling.py"})
    assert "--isolated" in command
    assert "--no-project" in command
    assert command[command.index("--with-requirements") + 1].endswith("configs/environments/docling.txt")


def test_project_runner_keeps_locked_environment():
    command = runner_command({"environment": "project", "script": "scripts/runners/run_structure.py"})
    assert command[:4] == ["uv", "run", "--locked", "python"]
