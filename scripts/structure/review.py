"""Render every recorded annotation, preserving partial-page versus full-page coverage."""

import argparse
import json
import re
from pathlib import Path

import pymupdf

from pdf_heading_benchmark.io import REPO
from pdf_heading_benchmark.structure_data import checksum, config_hashes
from pdf_heading_benchmark.supervised_data import read_json, write_json
from pdf_heading_benchmark.visual_review import render_pages


def source_context(pdf: Path) -> list[int]:
    with pymupdf.open(pdf) as document:
        return [
            i + 1
            for i in range(min(16, len(document)))
            if re.search(
                r"(?im)^\s*(?:table\s+(?:of\s+contents|des\s+mati[eè]res)|contents?|"
                r"sommaire|[ií]ndice|contenido)\s*$",
                document[i].get_text(),
            )
        ]


def prepare_document(record: dict, annotations: list[dict], audits: dict, data: Path, assets: Path) -> dict:
    pdf = data / "pdfs" / f"wfp-{record['id']}.pdf"
    if checksum(pdf) != record["sha256"]:
        raise ValueError("Wrong source PDF")
    groups = [a for a in annotations if a["report_id"] == record["id"]]
    toc = source_context(pdf)
    numbers = set(record["review_pages"] + toc)
    numbers.update(int(re.match(r"p(\d+)", key)[1]) for a in groups for key in a["line_ids"])
    pages = render_pages(pdf, sorted(numbers), assets, record["id"])
    return {
        **record,
        "total_pages": record["pages"],
        "pages": pages,
        "toc_pages": toc,
        "annotations": groups,
        "predictions": audits.get(record["id"], []),
    }


def atlas(documents: list[dict], assets: Path) -> None:
    entries = [(d, p) for d in documents for p in d["pages"] if p["number"] in d["toc_pages"]]
    doc = pymupdf.open()
    page = doc.new_page(width=960, height=((len(entries) + 3) // 4) * 365 + 55)
    page.insert_text((15, 25), f"WFP V2 CONTENTS ATLAS | {len(entries)} SOURCE PAGES", fontsize=15)
    page.insert_text(
        (15, 43),
        "Contents pages are context; assessed headings appear in the interactive viewer.",
        fontsize=10,
    )
    for i, (record, source) in enumerate(entries):
        x, y = i % 4 * 240, i // 4 * 365 + 55
        page.insert_text(
            (x + 8, y + 14), f"{record['id']} | {record['split']} | PDF {source['number']}", fontsize=10
        )
        page.insert_image(
            pymupdf.Rect(x + 7, y + 22, x + 233, y + 359), filename=str(assets.parent / source["image"])
        )
    page.get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3)).save(assets / "toc-atlas.png")


def build(config: Path, data: Path, run: Path, output: Path) -> None:
    selection = read_json(run / "selection.json")
    if selection["config_hashes"] != config_hashes(config):
        raise ValueError("Changed labels or protocol")
    if output.exists():
        raise ValueError("Choose a fresh viewer directory")
    assets = output / "assets"
    assets.mkdir(parents=True)
    audits = {
        a["report_id"]: a["headings"]
        for a in read_json(run / "evaluation" / f"{selection['selected']}-test-audit.json")
    }
    annotations = read_json(config / "annotations.json")
    documents = []
    for record in read_json(config / "corpus.json"):
        documents.append(prepare_document(record, annotations, audits, data, assets))
        print("Rendered", record["id"], flush=True)
    dataset = {"documents": documents, "config_hashes": selection["config_hashes"]}
    write_json(output / "review-data.json", dataset)
    template = REPO / "docs/structure-review"
    html = (template / "index.html").read_text()
    html = html.replace("__STYLE__", (template / "style.css").read_text())
    html = html.replace("__SCRIPT__", (template / "app.js").read_text())
    html = html.replace("__DATA__", json.dumps(dataset, ensure_ascii=False).replace("</", "<\\/"))
    (output / "index.html").write_text(html)
    atlas(documents, assets)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=REPO / "configs/structure-v2")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.config, args.data, args.run, args.output)
