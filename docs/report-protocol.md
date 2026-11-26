## How the experiment works

1. **Annotate:** identify heading text, page and level on the same 32 pages. Main chapters and annexes are H1. [Pages](https://github.com/dividor/pdf-heading-benchmark/blob/main/configs/audit_pages.json) · [Reference labels](https://github.com/dividor/pdf-heading-benchmark/blob/main/configs/gold.json).
2. **Extract:** run each local configuration without reference labels. CPU parsers process the complete PDFs; later OCR models process page images. Some Qwen runs also receive native text, tags and document context. These are different input conditions.
3. **Match and score:** match titles one-to-one on the same page, using normalized similarity ≥90%. Award joint credit only when the level also matches. [Scorer](https://github.com/dividor/pdf-heading-benchmark/blob/main/src/pdf_heading_benchmark/evaluation.py).
4. **Measure:** record processing time and, where applicable, retained prose. Run large models one at a time. No per-report heading corrections are applied.

### Three kinds of technique

| Approach | What happens | Examples |
| --- | --- | --- |
| PDF parser | Read PDF text or use OCR; infer heading styles and hierarchy. | Docling, PyMuPDF4LLM, MinerU basic |
| Local vision model | Read page images; generate text and structure. Some configurations add text or document context. | Chandra, Qwen, MiniCPM, Xiaomi, Paddle |
| OUR METHOD | Use assistant-labeled reports to train small Extra Trees classifiers for line grouping, heading levels and neighboring-heading relationships. No LLM runs at inference. | Original, calibrated and confidence-filtered variants |

A row’s **i** opens only that configuration’s flow and settings. Expand its predictions to inspect misses and wrong levels. [Runnable repository](https://github.com/dividor/pdf-heading-benchmark) · [Reproduction guide](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/reproducibility.md).

### What is shared across the runs?

We preserve each pipeline’s output without WFP-specific level repairs. Different inputs are explicit: native-text parsers, image-only OCR, and Qwen with additional document context. Page numbers count from the cover. Predictions and references use the same scorer in the table and dialogs.

OUR METHOD uses Extra Trees: classifiers that combine randomized decision trees. Its variants learn from assistant annotations on separate reports. Each dialog identifies the fitted components and the validation choices for that variant; it links the full training record.
