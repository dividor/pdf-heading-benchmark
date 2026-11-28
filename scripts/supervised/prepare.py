"""Prepare frozen annotations from verified public PDFs or a local archive."""

import argparse
import hashlib
import time
from pathlib import Path

from pdf_heading_benchmark.supervised_data import (
    extract_archive,
    label_map,
    read_json,
    read_labels,
    validate_corpus,
    write_json,
)
from pdf_heading_benchmark.supervised_features import extract_lines, feature_rows
from pdf_heading_benchmark.training_download import download_training


def prepare(config: Path, data: Path, archive: Path | None) -> None:
    records = read_json(config / "corpus.json")
    historical = read_json(config.parent / "corpus.json")
    excluded = read_json(config / "excluded.json") + historical
    validate_corpus(records, excluded)
    if archive:
        extract_archive(archive, records, data / "pdfs")
    annotations = read_labels(config / "labels.tsv")
    dataset, expanded, timings = [], [], []
    for record in records:
        path = data / "pdfs" / f"wfp-{record['id']}.pdf"
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError(f"Wrong PDF: {path.name}")
        start = time.perf_counter()
        lines = extract_lines(path)
        rows, names = feature_rows(lines)
        timings.append(
            {
                "report_id": record["id"],
                "pages": record["pages"],
                "lines": len(lines),
                "extract_and_feature_seconds": time.perf_counter() - start,
            }
        )
        labels = label_map(record, lines, annotations)
        dataset.extend(
            {**r, "report_id": record["id"], "split": record["split"], "label": labels[r["id"]]}
            for r in rows
            if r["id"] in labels
        )
        lookup = {line["id"]: line for line in lines}
        for annotation in annotations:
            if annotation["report_id"] == record["id"]:
                parts = [lookup[key] for key in annotation["line_ids"]]
                expanded.append(
                    {
                        **annotation,
                        "page": parts[0]["page"],
                        "text": " ".join(p["text"] for p in parts),
                        "bboxes": [p["bbox"] for p in parts],
                    }
                )
        write_json(data / "extracted" / f"{record['id']}.json", lines)
        write_json(data / "features" / f"{record['id']}.json", rows)
        print(f"{record['id']}: {len(lines)} lines; {len(labels)} reviewed", flush=True)
    hashes = {
        name: hashlib.sha256((config / name).read_bytes()).hexdigest()
        for name in ("labels.tsv", "corpus.json")
    }
    write_json(data / "dataset.json", {"features": names, "rows": dataset, "config_hashes": hashes})
    write_json(data / "annotations-expanded.json", expanded)
    write_json(data / "preparation-timings.json", timings)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/supervised"))
    parser.add_argument("--data", type=Path, required=True)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--archive", type=Path, help="Optional local tar; omit after verified extraction")
    source.add_argument("--download", action="store_true", help="Download the exact public training PDFs")
    args = parser.parse_args()
    if args.download:
        download_training(args.config, args.data)
    prepare(args.config, args.data, args.archive)
