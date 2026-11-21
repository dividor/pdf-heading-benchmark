"""Compare default Docling heading levels with its built-in hierarchy stage.

Run with ../.venv-pdf-headings/bin/python run_docling.py INPUT.pdf OUTPUT_DIR
OCR and table reconstruction are disabled for this born-digital, heading-only test.
The same detected blocks are used in both variants to isolate level inference.
"""

import argparse
import importlib.metadata
import json
import platform
import time
from pathlib import Path

from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import HeadingHierarchyOptions, PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.models.stages.heading_hierarchy.heading_hierarchy_model import HeadingHierarchyModel
from docling_core.types.doc import SectionHeaderItem


def headings(document):
    return [
        {
            "title": item.text,
            "level": item.level,
            "page": item.prov[0].page_no if item.prov else None,
            "bbox": item.prov[0].bbox.model_dump() if item.prov else None,
            "ref": item.self_ref,
        }
        for item, _ in document.iterate_items()
        if isinstance(item, SectionHeaderItem)
    ]


def save(out, name, document):
    records = headings(document)
    (out / f"{name}.headings.json").write_text(json.dumps(records, indent=2))
    (out / f"{name}.md").write_text(document.export_to_markdown())
    document.save_as_json(out / f"{name}.document.json")
    return len(records)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    options = PdfPipelineOptions()
    options.do_ocr = False
    options.do_table_structure = False
    options.generate_parsed_pages = True  # needed when applying hierarchy after conversion
    options.accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CPU, num_threads=8)
    (args.output / "docling.options.json").write_text(options.model_dump_json(indent=2))
    converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)})
    start = time.perf_counter()
    result = converter.convert(args.pdf)
    conversion_seconds = time.perf_counter() - start
    default_count = save(args.output, "docling_default", result.document)
    flat_document = result.document.model_copy(deep=True)
    parsed = sum(p.parsed_page is not None for p in result.pages)
    start = time.perf_counter()
    HeadingHierarchyModel(HeadingHierarchyOptions(enabled=True))(result)
    hierarchy_seconds = time.perf_counter() - start
    hierarchy_count = save(args.output, "docling_hierarchy", result.document)
    result.document = flat_document
    tuned_options = HeadingHierarchyOptions(enabled=True, style_size_tolerance=0.15)
    HeadingHierarchyModel(tuned_options)(result)
    tuned_count = save(args.output, "docling_tuned", result.document)
    metadata = {
        "package": "docling",
        "version": importlib.metadata.version("docling"),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "status": str(result.status),
        "pages": len(result.pages),
        "parsed_pages_retained": parsed,
        "conversion_seconds_including_first_model_load_or_download": conversion_seconds,
        "hierarchy_stage_seconds": hierarchy_seconds,
        "default_headings": default_count,
        "hierarchy_headings": hierarchy_count,
        "tuned_headings": tuned_count,
        "tuned_hierarchy_options": tuned_options.model_dump(),
        "device": "cpu",
        "threads": 8,
        "ocr": False,
        "table_structure": False,
    }
    (args.output / "docling.run.json").write_text(json.dumps(metadata, indent=2))
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    main()
