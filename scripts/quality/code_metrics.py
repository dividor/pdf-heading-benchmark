"""Python quality gate adapted from dividor/tiered-taxonomy-tagging (MIT).

Same ratings: cyclomatic/cognitive <=20, maintainability index >=10.
This Python-only repository needs no JavaScript metric adapters.
"""

import argparse
import ast
import json
from pathlib import Path

import lizard
from cognitive_complexity.api import get_cognitive_complexity
from radon.metrics import mi_visit


def measure(path):
    source = path.read_text()
    functions = [
        n for n in ast.walk(ast.parse(source)) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    analysis = lizard.analyze_file.analyze_source_code(str(path), source)
    cyclomatic = max((f.cyclomatic_complexity for f in analysis.function_list), default=0)
    cognitive = max((get_cognitive_complexity(f) for f in functions), default=0)
    maintainability = mi_visit(source, multi=True)
    return dict(
        path=str(path),
        cyclomatic_max=cyclomatic,
        cognitive_max=cognitive,
        mi=maintainability,
        bad=cyclomatic > 20 or cognitive > 20 or maintainability < 10,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths", nargs="+", default=["src", "tests", "scripts"])
    parser.add_argument("--fail-on-bad", action="store_true")
    parser.add_argument(
        "--skip-js-cognitive", action="store_true", help="Compatibility with the reference repo"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    files = sorted({p for root in args.paths for p in Path(root).rglob("*.py")})
    rows = [measure(path) for path in files]
    bad = [row for row in rows if row["bad"]]
    payload = json.dumps(dict(files=rows, bad_files=bad), indent=2) + "\n"
    if args.output:
        args.output.write_text(payload)
    for row in bad:
        print(row)
    print(f"Checked {len(rows)} files; {len(bad)} fail the gate.")
    return int(bool(bad) and args.fail_on_bad)


if __name__ == "__main__":
    raise SystemExit(main())
