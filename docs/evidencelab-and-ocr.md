# EvidenceLab and forced Docling OCR

These two configurations parse the same four complete WFP reports (523 pages). We score only the existing 32 audit pages and 77 reference headings. Input hashes, unmodified predictions and measured times are retained. No report-specific heading repairs are applied.

## EvidenceLab, including its post-processor

The tested source is [`dividor/evidencelab` at `40c4ae4`](https://github.com/dividor/evidencelab/tree/40c4ae48296d68814af8d308a4aa5388c71cdd9e). The image is pinned by digest in [the configuration](../configs/evidencelab.json). We ran an isolated copy of the image used by the local EvidenceLab service; the service and its database were not changed.

```text
Full PDF → Docling 2.58.0 (Heron + TableFormer fast)
         → ResultPostprocessor and EvidenceLab's hierarchy safeguards
         → final contents-list normalization → native toc.txt headings
```

The hierarchy package is [`docling-hierarchical-pdf` 0.1.2](https://github.com/krrome/docling-hierarchical-pdf). Its `ResultPostprocessor` uses PDF hierarchy metadata when available; otherwise it builds a hierarchy from heading geometry and font style.

The public `ParseProcessor.process_document` entry point runs the whole parsing pipeline, including hierarchy processing, superscripts, output creation and final TOC normalization. OCR and chunking are disabled. The container uses Linux ARM64, four CPU cores and a 12 GB memory limit. This is CPU processing inside Docker, not Metal GPU inference.

We score **the final normalized `toc.txt`**, including its native levels, filtering and 80-character title limit. We also retain the structured JSON headings as a diagnostic. They are not substituted for the final TOC. The upstream pipeline's safeguards remain unchanged; the benchmark adds no fallback or repair.

**Observed:** 37/77 correct heading-level pairs; 26 headings matched at an incorrect level; 14 missed; seven extras. Joint F0.5 is **51.8%**. Parsing took **9 min 50 sec** over all 523 pages, averaging **1.13 sec/page**. The 32-page estimate is **36 sec**, not a separately measured run. First-document timing includes lazy model loading and downloads; parser setup is recorded separately.

This uses an older Docling version than the Docling-only rows. The score difference does not isolate the effect of post-processing.

From the repository root, after the standard environment and corpus setup in the README:

```bash
export PDF_BENCHMARK_DATA=/path/to/pdf-heading-benchmark-data
uv run --locked python scripts/runners/benchmark_evidencelab.py \
  --data "$PDF_BENCHMARK_DATA" \
  --output "$PDF_BENCHMARK_DATA/evidencelab/run-002"
uv run --locked python scripts/pipeline_report.py evidencelab \
  --data "$PDF_BENCHMARK_DATA" \
  --run "$PDF_BENCHMARK_DATA/evidencelab/run-002"
uv run --locked pdf-headings report
```

Use a fresh run directory. The launcher first downloads the recorded model revisions, then runs the parser with Hugging Face offline. Docker and model downloads require network access during setup. No inference API, database credentials or running EvidenceLab service are required. [Weight hashes](../configs/evidencelab-model-files.json) · [Saved evidence](../outputs/pipeline-runs/evidencelab.json).

## Docling with forced full-page OCR

The original Docling tests set `do_ocr=False`. This configuration uses **Docling 2.151.1 + RapidOCR 3.10.0**, with full-page OCR forced even when selectable PDF text exists.

```text
Page image at 216 dpi → PP-OCRv5 mobile detection + Latin recognition
                     → Heron layout → Docling HeadingHierarchyModel
                     → native heading text, H level and PDF page
```

RapidOCR uses ONNX Runtime 1.32.0 on CPU with eight threads. Its models are `ch_PP-OCRv5_det_mobile`, `latin_PP-OCRv5_rec_mobile` and `ch_ppocr_mobile_v2.0_cls_mobile`. Latin-script recognition covers the English and Spanish input documents. Settings are `mode=FULL_PAGE`, `scale=3`, `text_score=0.5`, `detect_orientation=False`. Table reconstruction is disabled. The default heading hierarchy pass runs after conversion.

**Observed:** 15/77 correct heading-level pairs, 52 incorrect levels, ten missed headings and two extras. Joint F0.5 is **21.2%**, compared with **22.4%** for the earlier Docling hierarchy configuration without OCR. Native prose retention is **86.6%**. Processing took **9 min 23 sec** for 523 pages, plus **4.12 sec** initialization. The average is **1.08 sec/page**; the estimated 32-page duration is **34.5 sec**. Forced OCR did not improve this benchmark.

OCR recognizes characters; the subsequent layout and hierarchy stages still have to identify headings and assign levels. This experiment tests OCR on selectable-text PDFs. It does not establish quality on scanned documents or compare all OCR engines supported by Docling.

```bash
uv venv --python 3.12 "$PDF_BENCHMARK_DATA/envs/docling-ocr"
uv pip install --python "$PDF_BENCHMARK_DATA/envs/docling-ocr/bin/python" \
  -r configs/environments/docling-ocr.txt
"$PDF_BENCHMARK_DATA/envs/docling-ocr/bin/python" scripts/runners/prepare_docling_ocr_models.py \
  --repo "$PWD" --manifest "$PDF_BENCHMARK_DATA/docling-ocr/model-files.json"
HF_HUB_OFFLINE=1 "$PDF_BENCHMARK_DATA/envs/docling-ocr/bin/python" scripts/runners/run_docling_ocr.py \
  --repo "$PWD" --corpus "$PDF_BENCHMARK_DATA/corpus" \
  --output "$PDF_BENCHMARK_DATA/docling-ocr/run-002"
cp "$PDF_BENCHMARK_DATA/docling-ocr/model-files.json" \
  "$PDF_BENCHMARK_DATA/docling-ocr/run-002/model-files.json"
uv run --locked python scripts/pipeline_report.py docling_ocr \
  --data "$PDF_BENCHMARK_DATA" \
  --run "$PDF_BENCHMARK_DATA/docling-ocr/run-002"
uv run --locked pdf-headings report
```

The setup script downloads the recorded Heron revision and checks the OCR weights against [their SHA-256 hashes](../configs/docling-ocr-models.json). Changed weights cause an error. Pipeline initialization is timed separately; per-document timing includes conversion and heading hierarchy. The full output and runner snapshot stay outside Git; audit predictions, timings and hashes are published.

Run these parsers **one at a time**. The reproducibility scripts preserve package/model identities and settings; wall-clock performance will still depend on hardware, caches and other work on the host. Unit tests cover the configuration, input validation, native-level preservation, failed-run rejection and publishing. The benchmark also exercises the actual packages on all four PDFs.
