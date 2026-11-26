"""Test full-page RapidOCR in Docling, then its default heading-hierarchy stage."""

import argparse
import hashlib
import importlib.metadata
import json
import logging
import platform
import time
from pathlib import Path


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def make_options():
    from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
    from docling.datamodel.pipeline_options import OcrMode, PdfPipelineOptions, RapidOcrOptions

    options = PdfPipelineOptions()
    options.do_ocr = True
    options.do_table_structure = False
    options.generate_parsed_pages = True
    options.ocr_options = RapidOcrOptions(mode=OcrMode.FULL_PAGE, lang=["latin"], backend="onnxruntime")
    options.accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CPU, num_threads=8)
    return options


def run(repo, corpus, output):
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import HeadingHierarchyOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.models.stages.heading_hierarchy.heading_hierarchy_model import HeadingHierarchyModel

    output.mkdir(parents=True, exist_ok=False)
    options = make_options()
    protocol = dict(
        platform=platform.platform(),
        options=json.loads(options.model_dump_json()),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        packages={
            name: importlib.metadata.version(name)
            for name in ("docling", "docling-core", "rapidocr", "onnxruntime", "torch", "pymupdf")
        },
    )
    write(output / "protocol.json", protocol)
    (output / "runner.py").write_bytes(Path(__file__).read_bytes())
    converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)})
    start = time.perf_counter()
    converter.initialize_pipeline(InputFormat.PDF)
    write(output / "initialization.json", {"seconds": time.perf_counter() - start})
    results = []
    for item in json.loads((repo / "configs/corpus.json").read_text()):
        pdf = corpus / f"{item['id']}.pdf"
        if hashlib.sha256(pdf.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Wrong PDF: {item['id']}")
        start = time.perf_counter()
        result = converter.convert(pdf)
        if str(result.status).split(".")[-1].lower() != "success":
            raise RuntimeError(f"Docling conversion did not complete: {result.status}")
        HeadingHierarchyModel(HeadingHierarchyOptions(enabled=True))(result)
        seconds = time.perf_counter() - start
        result.document.save_as_json(output / f"{item['id']}.document.json")
        (output / f"{item['id']}.md").write_text(result.document.export_to_markdown())
        results.append(
            dict(document=item["id"], pages=len(result.pages), seconds=seconds, input_sha256=item["sha256"])
        )
        write(output / "timing.json", results)
        print(json.dumps(results[-1]), flush=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument("--repo", required=True, type=Path)
    arguments.add_argument("--corpus", required=True, type=Path)
    arguments.add_argument("--output", required=True, type=Path)
    args = arguments.parse_args()
    run(args.repo, args.corpus, args.output)
