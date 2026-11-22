"""Import complete sequential reruns and render a separate, auditable comparison.

Original league scores and predictions remain frozen. Partial runs are never scored.
Without --run, regeneration uses only the committed compact evidence.
"""

import argparse
import hashlib
import json
import re
import statistics
from pathlib import Path

from pdf_heading_benchmark.evaluation import evaluate
from pdf_heading_benchmark.io import REPO, read_json, write_json
from pdf_heading_benchmark.joint_metrics import scored_counts
from pdf_heading_benchmark.prediction_comparison import LABELS, comparison_rows, heading_text
from pdf_heading_benchmark.report import table

OUT = REPO / "outputs/sequential-repeat"
FIELDS = ("gold", "predicted", "matched", "correct_level")


def page_records(root: Path, method: str, pages: dict) -> dict:
    compact = root / method / "run"
    base = compact if compact.exists() else root / "inputs/results"
    records = {}
    for doc, numbers in pages.items():
        folder = base / doc if compact.exists() else base / doc / method
        records[doc] = [read_json(folder / f"{pn}.json") for pn in sorted(numbers)]
        if [r["page"] for r in records[doc]] != sorted(numbers):
            raise ValueError("Page record identity mismatch")
    return records


def counter(text: str, name: str) -> int:
    found = re.search(rf"^{name}:\s+(\d+)", text, re.MULTILINE)
    if not found:
        raise ValueError(f"Missing VM counter: {name}")
    return int(found[1])


def gpu_summary(samples: list[dict], execution: dict) -> dict:
    values = [d["Device Utilization %"] for r in samples for d in r["gpu"] if "Device Utilization %" in d]
    start, end = execution["before"], execution["after"]
    page_size = re.search(r"page size of (\d+) bytes", start["vm_stat"])
    if not page_size:
        raise ValueError("Missing VM page size")
    return dict(
        samples=len(values),
        median_percent=statistics.median(values) if values else None,
        max_percent=max(values) if values else None,
        swap_start=start["swap"],
        swap_end=end["swap"],
        swap_in_bytes=(counter(end["vm_stat"], "Swapins") - counter(start["vm_stat"], "Swapins"))
        * int(page_size[1]),
        swap_out_bytes=(counter(end["vm_stat"], "Swapouts") - counter(start["vm_stat"], "Swapouts"))
        * int(page_size[1]),
        load_average_start=start["load_average"],
        load_average_end=end["load_average"],
        thermal_end=end["thermal"],
        scope="System-wide samples every approximately 10 seconds, including model loading",
    )


def import_method(root: Path, method: str, protocol: dict) -> None:
    path = root / method
    execution = read_json(path / "execution.json")
    if execution["exit_code"] != 0:
        raise ValueError(f"Cannot import failed method: {method}")
    records = page_records(root, method, protocol["audit_pages"])
    device = read_json(path / "device.json")
    if device["default_device"] != "Device(gpu, 0)":
        raise ValueError("GPU device not verified")
    samples = [json.loads(line) for line in (path / "telemetry.jsonl").read_text().splitlines()]
    fields = (
        "page",
        "seconds",
        "tokens",
        "timeout",
        "hit_token_limit",
        "error",
        "peak_mlx_memory_gb",
        "first_token_seconds",
    )
    write_json(
        OUT / "evidence" / f"{method}.json",
        dict(
            method=method,
            started_at=execution["before"]["at"],
            ended_at=execution["after"]["at"],
            device=device,
            process_wall_seconds=execution["process_wall_seconds"],
            predictions={doc: [h for r in rs for h in r["headings"]] for doc, rs in records.items()},
            pages={
                doc: [{field: r.get(field) for field in fields} for r in rs] for doc, rs in records.items()
            },
            gpu=gpu_summary(samples, execution),
        ),
    )


def import_run(root: Path) -> None:
    protocol = read_json(root / "protocol.json")
    if protocol["audit_pages"] != read_json(REPO / "configs/audit_pages.json"):
        raise ValueError("Audit scope changed")
    for name, value in protocol["source_sha256"].items():
        if hashlib.sha256((REPO / name).read_bytes()).hexdigest() != value:
            raise ValueError(f"Runner changed: {name}")
    for name, value in protocol["input_sha256"].items():
        if hashlib.sha256((root / "inputs" / name).read_bytes()).hexdigest() != value:
            raise ValueError(f"Input changed: {name}")
    for doc in read_json(REPO / "configs/corpus.json"):
        if protocol["pdf_sha256"][doc["id"] + ".pdf"] != doc["sha256"]:
            raise ValueError("Corpus PDF changed")
    write_json(OUT / "protocol.json", protocol)
    for method in protocol["order"]:
        if (root / method / "execution.json").exists():
            import_method(root, method, protocol)


def score(evidence: dict) -> tuple[dict, list[dict]]:
    gold, pages = read_json(REPO / "configs/gold.json"), read_json(REPO / "configs/audit_pages.json")
    if set(evidence["predictions"]) != set(gold):
        raise ValueError("Incomplete document coverage")
    details = [
        dict(document=doc, **evaluate(gold[doc], evidence["predictions"][doc], pages[doc])) for doc in gold
    ]
    counts = scored_counts({field: sum(r[field] for r in details) for field in FIELDS})
    records = [r for rs in evidence["pages"].values() for r in rs]
    if len(records) != sum(map(len, pages.values())):
        raise ValueError("Incomplete page coverage")
    counts.update(
        seconds=sum(r["seconds"] for r in records),
        processed_pages=len(records),
        errors=sum(bool(r["error"]) for r in records),
        timeouts=sum(bool(r["timeout"]) for r in records),
        token_caps=sum(bool(r["hit_token_limit"]) for r in records),
    )
    return counts, details


def result_row(name: str, previous: dict, evidence: dict, counts: dict) -> list:
    return [
        name,
        f"{previous['measured_seconds'] / previous['processed_pages']:.3f}",
        f"{counts['seconds'] / counts['processed_pages']:.3f}",
        f"{evidence['process_wall_seconds'] / counts['processed_pages']:.3f}",
        f"{previous['correct_level']}/{previous['gold']} → {counts['correct_level']}/{counts['gold']}",
        f"{scored_counts(previous)['joint_f05']:.1%} → {counts['joint_f05']:.1%}",
        counts["predicted"] - counts["matched"],
        counts["errors"],
        counts["timeouts"],
    ]


def comparison_details(name: str, details: list[dict]) -> str:
    rows = [
        [
            detail["document"],
            (row["reference"] or row["prediction"])["page"],
            heading_text(row["reference"]),
            heading_text(row["prediction"]),
            LABELS[row["status"]],
        ]
        for detail in details
        for row in comparison_rows(detail)
    ]
    return f"\n\n### {name}: rerun predictions versus reference\n\n" + table(
        ["Report", "PDF page", "Reference", "Rerun prediction", "Outcome"], rows
    )


def build() -> None:
    if not (OUT / "protocol.json").exists():
        return
    protocol = read_json(OUT / "protocol.json")
    previous = {r["method"]: r for r in read_json(REPO / "outputs/league_table.json")}
    rows, telemetry, results, appendix = [], [], [], ""
    for method in protocol["order"]:
        path = OUT / "evidence" / f"{method}.json"
        if not path.exists():
            continue
        evidence = read_json(path)
        counts, details = score(evidence)
        name = previous[method]["name"]
        rows.append(result_row(name, previous[method], evidence, counts))
        gpu = evidence["gpu"]
        telemetry.append(
            [
                name,
                gpu["samples"],
                gpu["median_percent"],
                gpu["max_percent"],
                f"{gpu['swap_in_bytes'] / 1e9:.3f}",
                f"{gpu['swap_out_bytes'] / 1e9:.3f}",
            ]
        )
        results.append(dict(method=method, **counts))
        appendix += comparison_details(name, details)
    intro = (REPO / "docs/sequential-repeat.md").read_text()
    summary = intro + f"\n\n**Completed: {len(rows)}/{len(protocol['order'])} configurations.**\n\n"
    summary += table(
        [
            "Repeated configuration",
            "Earlier s/page",
            "Rerun s/page",
            "Whole-process s/page",
            "Correct heading + level",
            "Joint F0.5: earlier → rerun",
            "Rerun extras",
            "Errors",
            "Timeouts",
        ],
        rows,
    )
    summary += "\n\n### GPU and memory observations\n\n" + table(
        [
            "Repeated configuration",
            "Samples",
            "Median GPU %",
            "Maximum GPU %",
            "Swap read GB",
            "Swap written GB",
        ],
        telemetry,
    )
    summary += (
        "\n\nGPU and swap measurements are system-wide; they include other applications and model loading. "
    )
    summary += (
        "A high GPU percentage confirms activity but does not prove optimal inference "
        "or identify a bottleneck.\n"
    )
    (OUT / "summary.md").write_text(summary)
    (OUT / "report.md").write_text(summary + appendix + "\n")
    write_json(OUT / "results.json", results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path)
    args = parser.parse_args()
    if args.run:
        import_run(args.run)
    build()


if __name__ == "__main__":
    main()
