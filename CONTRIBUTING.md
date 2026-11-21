# Contributing

Use Python 3.12 and `uv sync --locked`. Create a feature branch (`codex/` for Codex changes), install pre-commit, and use Conventional Commits. Never bypass hooks with `--no-verify`.

Run `uv run pre-commit run --all-files` and `uv run pytest -q` before a PR. Hooks cover file hygiene, Ruff formatting/linting, mypy, Bandit, detect-secrets, Gitleaks, notebook output hygiene and complexity. New and changed functions must have cyclomatic and cognitive complexity <=20. Python file maintainability index must be >=10 (>=20 preferred), matching the reference repo's good/okay/bad bands. The gate includes src, tests and scripts. Refactor failures rather than adding suppression comments or excluding code.

Keep tests small, meaningful, offline and free of API credentials. Test model response adapters with synthetic data; never silently repair invalid model replies or substitute a different backend. Preserve raw replies and report failures. Paid-service retries must not blindly resubmit a potentially completed operation.

Run `uv run pdf-headings report` after changing report data or descriptions; commit both generated formats. CI regenerates them and requires byte-for-byte agreement. Published results are frozen evidence: keep new runs separate until their protocol, labels and provenance are reviewed. Do not overwrite scores with a rerun without explaining what changed.

PDFs, model weights, full raw outputs and secrets stay outside Git. The committed 77-label reference and compact audit predictions are a deliberate exception so public scores can be independently recomputed. Do not commit `.env`, provider operation URLs or local resource identifiers. Review any secret-scanner baseline entry before accepting it.

Keep notebooks thin and retain useful outputs without long progress logs. Draft posts belong in ignored `blog/` and are not committed. Model/package/PDF licenses are separate from this repository's MIT license.
