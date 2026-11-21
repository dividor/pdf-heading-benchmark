"""Visual review pack: frozen annotations over source pages, with TOC context."""

import hashlib
import json
import shutil
from pathlib import Path

import pymupdf

from pdf_heading_benchmark.io import REPO, read_json, write_json

COLOURS = ["#81919f", "#006ea5", "#00806a", "#8b4bb1", "#bc6405", "#c02d65", "#604f34"]


def render_pages(pdf: Path, numbers: list[int], destination: Path, identifier: int) -> list[dict]:
    pages = []
    with pymupdf.open(pdf) as document:
        for number in numbers:
            page = document[number - 1]
            name = f"{identifier}-{number:03d}.png"
            page.get_pixmap(matrix=pymupdf.Matrix(1.6, 1.6), alpha=False).save(destination / name)
            pages.append(
                {
                    "number": number,
                    "width": page.rect.width,
                    "height": page.rect.height,
                    "image": "assets/" + name,
                }
            )
    return pages


def document_data(
    record: dict, context: dict, annotations: list[dict], data: Path, run: Path, assets: Path
) -> dict:
    identifier = record["id"]
    pdf = data / "pdfs" / f"wfp-{identifier}.pdf"
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != record["sha256"]:
        raise ValueError("Wrong source PDF")
    numbers = sorted(set(record["review_pages"] + context["toc_pages"]))
    pages = render_pages(pdf, numbers, assets, identifier)
    inference = read_json(run / "inference" / f"{identifier}.json")
    if inference["pdf_sha256"] != record["sha256"]:
        raise ValueError("Inference/source mismatch")
    for page in pages:
        page["lines"] = [
            {k: line[k] for k in ("id", "text", "page", "bbox")}
            for line in inference["lines"]
            if line["page"] == page["number"]
        ]
    return {
        **{k: record[k] for k in ("id", "title", "year", "language", "split", "url", "review_pages")},
        "total_pages": record["pages"],
        "toc_pages": context["toc_pages"],
        "toc_note": context["note"],
        "pages": pages,
        "annotations": [a for a in annotations if a["report_id"] == identifier],
        "predictions": [h for h in inference["headings"] if h["page"] in numbers],
    }


def contact_sheet(documents: list[dict], assets: Path) -> None:
    entries = [(d, p) for d in documents for p in d["pages"] if p["number"] in d["toc_pages"]]
    columns, width, height = 4, 240, 365
    doc = pymupdf.open()
    page = doc.new_page(width=columns * width, height=((len(entries) + columns - 1) // columns) * height + 55)
    page.insert_text((18, 25), "WFP CONTENTS ATLAS | 22 REPORTS / 26 PAGES", fontsize=15)
    page.insert_text(
        (18, 43),
        "Context images, not training labels. Open individual pages in the review report.",
        fontsize=10,
    )
    for index, (record, source) in enumerate(entries):
        x, y = (index % columns) * width, (index // columns) * height + 55
        page.insert_text(
            (x + 8, y + 14), f"{record['id']} | {record['split']} | PDF {source['number']}", fontsize=10
        )
        page.insert_image(
            pymupdf.Rect(x + 7, y + 22, x + width - 7, y + height - 6),
            filename=str(assets.parent / source["image"]),
        )
    page.get_pixmap(matrix=pymupdf.Matrix(1.7, 1.7), alpha=False).save(assets / "toc-atlas.png")


def annotation_example(document: dict, assets: Path) -> None:
    source = next(p for p in document["pages"] if p["number"] == 23)
    doc = pymupdf.open()
    page = doc.new_page(width=source["width"] + 280, height=source["height"] + 50)
    page.insert_text((18, 23), "SOURCE PAGE + ASSISTANT ANNOTATIONS", fontsize=15)
    offset = 42
    page.insert_image(
        pymupdf.Rect(0, offset, source["width"], source["height"] + offset),
        filename=str(assets.parent / source["image"]),
    )
    y = 75
    for annotation in (a for a in document["annotations"] if a["page"] == 23):
        colour = tuple(int(COLOURS[annotation["level"]][i : i + 2], 16) / 255 for i in (1, 3, 5))
        for index, box in enumerate(annotation["bboxes"]):
            rect = pymupdf.Rect(box[0], box[1] + offset, box[2], box[3] + offset)
            page.draw_rect(rect, color=colour, fill=colour, fill_opacity=0.12, width=1.2)
            if index == 0:
                page.insert_text(
                    (max(2, rect.x0 - 26), rect.y0 + 10), f"H{annotation['level']}", fontsize=10, color=colour
                )
        page.insert_text(
            (source["width"] + 12, y), f"H{annotation['level']} | PDF 23", fontsize=13, color=colour
        )
        page.insert_textbox(
            pymupdf.Rect(source["width"] + 12, y + 10, page.rect.width - 15, y + 80),
            annotation["text"],
            fontsize=11,
        )
        y += 115
    page.insert_textbox(
        pymupdf.Rect(source["width"] + 12, y + 20, page.rect.width - 15, page.rect.height - 20),
        "Report 611: Madagascar country strategic plan evaluation.\n\n"
        "Coloured boxes show the assistant labels. They are reviewable judgments, not verified truth.\n\n"
        "The H3 geography heading was missed by the trained classifier.\n\n"
        "These labels were frozen before model fitting.",
        fontsize=11,
    )
    page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False).save(assets / "annotation-example.png")


def build_review(data: Path, run: Path, output: Path) -> None:
    config = REPO / "configs/supervised"
    selection = read_json(run / "selection.json")
    label_hash = hashlib.sha256((config / "labels.tsv").read_bytes()).hexdigest()
    if label_hash != selection["label_sha256"]:
        raise ValueError("Labels changed since model selection")
    corpus_hash = hashlib.sha256((config / "corpus.json").read_bytes()).hexdigest()
    if corpus_hash != selection["corpus_sha256"]:
        raise ValueError("Corpus changed since model selection")
    assets = output / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    context = {r["id"]: r for r in read_json(config / "visual-review.json")["documents"]}
    annotations = read_json(REPO / "outputs/supervised/evidence/annotations.json")
    documents = []
    for record in read_json(config / "corpus.json"):
        documents.append(document_data(record, context[record["id"]], annotations, data, run, assets))
        print(f"Rendered report {record['id']}", flush=True)
    dataset = {"label_hash": label_hash, "documents": documents}
    write_json(output / "review-data.json", dataset)
    template = REPO / "docs/annotation-review"
    html = (template / "index.html").read_text().replace("__STYLE__", (template / "style.css").read_text())
    html = html.replace("__SCRIPT__", (template / "app.js").read_text())
    html = html.replace("__DATA__", json.dumps(dataset, ensure_ascii=False).replace("</", "<\\/"))
    (output / "index.html").write_text(html)
    shutil.copy2(REPO / "docs/images/supervised-method.svg", assets / "method.svg")
    contact_sheet(documents, assets)
    annotation_example(next(d for d in documents if d["id"] == 611), assets)
