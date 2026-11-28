"""Import completed Qwen speed trials and regenerate their league evidence.

Use --runs EXTERNAL_ROOT once to import 27b-run-002, 35b-run-001 and 35b-memory-run-001. Without it,
rebuild entirely offline from the compact committed evidence.
"""

import argparse
import hashlib
from pathlib import Path

from markdown_it import MarkdownIt

from pdf_heading_benchmark.evaluation import evaluate
from pdf_heading_benchmark.io import REPO, read_json, write_json
from pdf_heading_benchmark.joint_metrics import scored_counts
from pdf_heading_benchmark.report import table

OUT = REPO / "outputs/qwen-compact"
REMOTE = "https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/"
VARIANTS = {
    "qwen36_27b_compact": ("27b-run-002", "Qwen3.6-27B 4-bit — single image"),
    "qwen36_35b_compact": ("35b-run-001", "Qwen3.6-35B-A3B 4-bit — single image"),
    "qwen36_35b_visual_memory": ("35b-memory-run-001", "Qwen3.6-35B-A3B 4-bit — visual memory"),
}


def import_run(root: Path, variant: str, directory: str) -> None:
    run = root / directory
    protocol = read_json(run / "protocol.json")
    if protocol["pages"] != read_json(REPO / "configs/audit_pages.json"):
        raise ValueError("Incomplete or different audit-page scope")
    for name, expected in protocol["source_sha256"].items():
        if hashlib.sha256((REPO / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Source changed after run started: {name}")
    for item in read_json(REPO / "configs/corpus.json"):
        if protocol["input_sha256"][f"corpus/{item['id']}.pdf"] != item["sha256"]:
            raise ValueError(f"PDF differs from frozen corpus: {item['id']}")
    model_name = "Qwen3.6-27B-4bit" if variant == "qwen36_27b_compact" else "Qwen3.6-35B-A3B-4bit"
    if protocol["model"] != read_json(REPO / "configs/models.json")[model_name]:
        raise ValueError("Model identity differs from the requested league row")
    predictions = read_json(run / "predictions.json")
    timing = read_json(run / "timing.json")
    if set(predictions) != set(protocol["pages"]):
        raise ValueError("Predictions do not cover all four reports")
    pages = {}
    fields = (
        "page",
        "image_size",
        "seconds",
        "preparation_seconds",
        "first_token_seconds",
        "prompt_tokens",
        "tokens",
        "timeout",
        "hit_token_limit",
        "error",
        "peak_mlx_memory_gb",
        "memory_pages",
        "outside_generation_seconds",
    )
    for document, selected in protocol["pages"].items():
        records = [read_json(run / document / f"{pn}.json") for pn in sorted(selected)]
        actual = [h for record in records for h in record["headings"]]
        if actual != predictions[document]:
            raise ValueError(f"Page records and final predictions differ: {document}")
        pages[document] = [{field: r.get(field) for field in fields} for r in records]
    write_json(
        OUT / "evidence" / f"{variant}.json",
        dict(
            protocol=protocol,
            predictions=predictions,
            timing=timing,
            pages=pages,
        ),
    )


def optional_duration(pages: list[dict], field: str, divisor: int = 1) -> str:
    values = [r.get(field) for r in pages]
    if any(value is None for value in values):
        return "—"
    return f"{sum(values) / divisor:.1f}" + (" min" if divisor == 60 else " s")


def telemetry_table() -> str:
    rows = []
    for key, (_, name) in VARIANTS.items():
        evidence = read_json(OUT / "evidence" / f"{key}.json")
        pages = [r for records in evidence["pages"].values() for r in records]
        rows.append(
            [
                name,
                f"{evidence['timing']['load_seconds']:.1f} s",
                optional_duration(pages, "preparation_seconds"),
                optional_duration(pages, "outside_generation_seconds"),
                optional_duration(pages, "first_token_seconds", 60),
                sum(r["tokens"] for r in pages),
                f"{max(r['peak_mlx_memory_gb'] for r in pages):.1f} GB",
                sum(bool(r["error"]) for r in pages),
                sum(r["timeout"] for r in pages),
                sum(r["hit_token_limit"] for r in pages),
            ]
        )
    return table(
        [
            "Configuration",
            "Model loading",
            "Page preparation",
            "Other wrapper time",
            "Summed time to first chunk",
            "Output tokens",
            "Peak MLX allocation",
            "Parse errors",
            "Timeouts",
            "Token caps reached",
        ],
        rows,
    )


def score_variant(key: str, name: str, evidence: dict) -> tuple[dict, list[dict]]:
    gold = read_json(REPO / "configs/gold.json")
    pages = read_json(REPO / "configs/audit_pages.json")
    scores = [
        dict(document=doc, method=key, **evaluate(gold[doc], heads, pages[doc]))
        for doc, heads in evidence["predictions"].items()
    ]
    counts = scored_counts(
        {field: sum(s[field] for s in scores) for field in ("gold", "predicted", "matched", "correct_level")}
    )
    timing = evidence["timing"]["documents"]
    return dict(
        method=key,
        name=name,
        source_url=REMOTE + "outputs/qwen-compact/report.md",
        status="completed",
        documents_scored=len(scores),
        **counts,
        heading_recall=counts["matched"] / counts["gold"],
        correct_heading_and_level=counts["correct_level"] / counts["gold"],
        false_headings=counts["predicted"] - counts["matched"],
        native_prose_retention=None,
        measured_seconds=sum(t["seconds"] for t in timing.values()),
        processed_pages=sum(t["pages"] for t in timing.values()),
    ), scores


def publish() -> list[dict]:
    rows = [r for r in read_json(REPO / "outputs/league_table.json") if r["method"] not in VARIANTS]
    details = [r for r in read_json(REPO / "outputs/league_details.json") if r["method"] not in VARIANTS]
    predictions = read_json(REPO / "outputs/audit_predictions.json")
    added = []
    for key, (_, name) in VARIANTS.items():
        evidence = read_json(OUT / "evidence" / f"{key}.json")
        row, scores = score_variant(key, name, evidence)
        rows.append(row)
        added.append(row)
        details.extend(scores)
        predictions[key] = evidence["predictions"]
    rows.sort(key=lambda r: r["correct_heading_and_level"] or -1, reverse=True)
    write_json(REPO / "outputs/league_table.json", rows)
    write_json(REPO / "outputs/league_details.json", details)
    write_json(REPO / "outputs/audit_predictions.json", predictions)
    baseline = next(r for r in rows if r["method"] == "qwen36_visual_memory")
    return [scored_counts(baseline), *added]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path)
    args = parser.parse_args()
    if args.runs:
        for key, (directory, _) in VARIANTS.items():
            import_run(args.runs, key, directory)
    results = publish()
    rendered = table(
        [
            "Configuration",
            "Joint F0.5",
            "Joint precision",
            "Correct heading + level",
            "Titles found",
            "False headings",
            "Generation / 32 pages",
        ],
        [
            [
                r["name"],
                f"{r['joint_f05']:.1%}",
                f"{r['joint_precision']:.1%}",
                f"{r['correct_level']}/{r['gold']} ({r['joint_recall']:.1%})",
                f"{r['matched']}/{r['gold']}",
                r["false_headings"],
                f"{r['measured_seconds'] / 60:.1f} min",
            ]
            for r in results
        ],
    )
    markdown = (REPO / "docs/qwen-compact.md").read_text().replace("__RESULTS__", rendered)
    markdown = markdown.replace("__TELEMETRY__", telemetry_table())
    (OUT / "report.md").write_text(markdown)
    body = MarkdownIt("commonmark").enable("table").render(markdown)
    css = (REPO / "docs/report.css").read_text()
    (OUT / "index.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>Qwen speed and hierarchy experiments</title><style>{css}</style></head>"
        f"<body><main>{body}</main></body></html>\n"
    )


if __name__ == "__main__":
    main()
