"""Materialize the explicit review decisions; never infer labels from typography."""

import argparse
from pathlib import Path

from pdf_heading_benchmark.structure_data import checksum
from pdf_heading_benchmark.supervised_data import read_json, write_json
from pdf_heading_benchmark.supervised_features import extract_lines


def merge_legacy(added: list[dict], legacy: list[dict], identifier: int) -> list[dict]:
    changes = []
    replaced = {key for a in added for key in a["line_ids"]}
    for old in legacy:
        if old["report_id"] != identifier:
            continue
        overlap = set(old["line_ids"]) & replaced
        if overlap:
            differences = [
                a
                for a in added
                if set(a["line_ids"]) & overlap
                and (a["level"] != old["level"] or a["line_ids"] != old["line_ids"])
            ]
            if differences:
                changes.append({"before": old, "after": differences})
        else:
            added.append(old)
    return changes


def compile_annotations(config: Path, data: Path) -> None:
    records = read_json(config / "corpus.json")
    legacy = read_json(config.parent.parent / "outputs/supervised/evidence/annotations.json")
    decisions = read_json(config / "decisions.json") | read_json(config / "test-decisions.json")
    output, changes = [], []
    for record in records:
        pdf = data / "pdfs" / f"wfp-{record['id']}.pdf"
        if checksum(pdf) != record["sha256"]:
            raise ValueError("Wrong source PDF")
        lines = extract_lines(pdf)
        added = []
        for level, tokens in decisions.get(str(record["id"]), {}).items():
            for token in tokens.split():
                parts = [lines[int(index)] for index in token.split("+")]
                added.append(
                    {
                        "report_id": record["id"],
                        "level": int(level),
                        "line_ids": [line["id"] for line in parts],
                        "page": parts[0]["page"],
                        "text": " ".join(line["text"] for line in parts),
                        "bboxes": [line["bbox"] for line in parts],
                        "note": "Explicit LLM review v2; source text and rendered layout",
                    }
                )
        changes.extend(merge_legacy(added, legacy, record["id"]))
        output.extend(sorted(added, key=lambda a: a["line_ids"][0]))
    write_json(config / "annotations.json", output)
    write_json(config / "annotation-changes.json", changes)
    print(f"{len(output)} total annotations, {len(changes)} explicit changes to v1 labels")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/structure-v2"))
    args = parser.parse_args()
    compile_annotations(args.config, args.data)
