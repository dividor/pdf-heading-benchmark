# Qwen local speed and hierarchy experiments

We tested whether removing earlier page images could make Qwen practical without sacrificing correct heading text and level. Two fixed configurations use the same input construction: **Qwen3.6-27B MLX 4-bit** and **Qwen3.6-35B-A3B MLX 4-bit**. A third follow-up restores the original multi-image memory with the sparse model. None was fine-tuned on WFP labels. The second is a mixture-of-experts model with 35 billion total parameters and approximately 3 billion activated per token; it still stores the full model weights. [Official model card](https://huggingface.co/Qwen/Qwen3.6-35B-A3B).

| Configuration | Joint F0.5 | Joint precision | Correct heading + level | Titles found | False headings | Generation / 32 pages |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen3.6-27B / MLX 4-bit / sampled visual memory | 82.7% | 82.3% | 65/77 (84.4%) | 77/77 | 2 | 61.8 min |
| Qwen3.6-27B 4-bit — single image | 77.1% | 76.9% | 60/77 (77.9%) | 77/77 | 1 | 34.0 min |
| Qwen3.6-35B-A3B 4-bit — single image | 68.8% | 68.8% | 53/77 (68.8%) | 77/77 | 0 | 5.2 min |
| Qwen3.6-35B-A3B 4-bit — visual memory | 69.0% | 69.3% | 52/77 (67.5%) | 75/77 | 0 | 8.7 min |

**Interpretation:** none of the new variants improves the original 27B result’s joint F0.5. The single-image 27B run is about 1.8× faster, but loses five correct levels. The sparse single-image run is about 11.9× faster, but loses twelve correct levels. All 77 titles are still recovered in both single-image runs: their remaining errors are primarily hierarchy mistakes, not a failure to find the text.

Restoring visual memory to the sparse model does not help: 52 correct pairs versus 53 with one image, two missing titles versus none, and 8.7 minutes versus 5.2. Its slightly higher F0.5 (69.0% versus 68.8%) comes from emitting fewer predictions, not recovering more correct headings. This is not a better solution to the requested high-coverage objective. The original 27B visual-memory configuration remains the most accurate of these four measured Qwen configurations.

## Documents and scoring

These are the original four WFP reports: the targeting and prioritization strategic evaluation, the mid-term evaluation of the 2022–2025 Strategic Plan, the Indonesia country strategic plan evaluation and the Colombia country strategic plan evaluation. [Official PDF URLs, titles and checksums](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/corpus.json). Together they contain 523 pages, but this experiment processes only **32 selected page images**, eight per report, with **77 reference headings**. [Exact physical PDF pages](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/audit_pages.json) · [Reference annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/gold.json).

We have already inspected this small benchmark. These are historical regression results, not an independent generalization test. The reference was annotated by the assistant and is available for review; it is not a certified human gold standard. The first two configurations were specified before their results were scored. After seeing the sparse single-image result (53/77 correct levels), we added a third configuration restoring the original visual-memory procedure. That follow-up is explicitly exploratory and was not pre-planned alongside the first two. Neither the reference headings nor their levels enter the inference runner. Report all three variants, including failures, rather than selecting a winner and hiding the others.

The primary score is **joint heading-and-level F0.5 = 1.25C / (P + 0.25G)**. C counts one-to-one matches with the correct title, physical page and exact heading level; P is the number predicted and G the number of reference headings. Title matching uses the frozen normalized similarity threshold of 0.90. Joint precision is C/P; joint recall is C/G. A wrong level contributes both a false positive and a false negative. False headings in the table are unmatched predictions; wrong-level headings are additional errors. The main report has the complete prediction-versus-reference table in each method modal.

## Initial single-image trials

1. Extract native text for the current page. Reuse the full-document PyMuPDF4LLM candidate outline and author-provided PDF heading tags. Candidate levels are omitted; tags may be wrong and are described as fallible evidence.
2. Render the current page at twice its PDF dimensions, then thumbnail to a maximum edge of **1,280 pixels**, preserving aspect ratio. Supply **one image**. The earlier configuration supplied a current image up to 1,792 pixels and up to six earlier images at 1,280 pixels.
3. Supply the most recent predicted heading at each H1–H6 level as **text only**. Memory starts empty for each document and updates after each sampled page in ascending page order. It does not silently process the intervening pages.
4. Generate complete heading text and integer H1–H6 levels locally. Both runs use MLX-VLM 0.8.0, MLX 0.32.4, temperature 0, seed 42, thinking disabled and a 4,096-token cap. A soft 600-second limit is checked between streamed chunks. Save raw replies; validate JSON without semantic title or level repairs.
5. Match the saved predictions against the frozen reference only after inference. Preserve the earlier multi-image result as a separate row.

The full outline and tags are still repeated for each target. This is specifically an image-history/resolution experiment, not a test of compacting all document context. Because both image size and history changed together, it does not identify their separate effects.

[Exact prompt](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/compact_prompt.py) · [Inference runner](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_compact.py) · [Strict response decoder](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/decode_qwen.py) · [Pinned model revisions](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json).

## Sparse-model visual-memory follow-up

The sparse single-image run found all 77 titles with no extras, but made 24 level mistakes. To test whether the missing typography examples mattered, a third run uses the original multi-image instruction and `generate_page` function without modifying them. The current image has a 1,792-pixel cap; memory includes up to six earlier sampled-page images at 1,280 pixels, selected by the most recent predicted heading at each level. The model is the same pinned 35B-A3B 4-bit version as the sparse single-image run. Temperature, seed, output cap and soft timeout remain unchanged.

This restores image history, image size and the associated instruction together. It cannot attribute a change to any one of those components. It is a follow-up prompted by results on this already inspected corpus, not an independent test. [Wrapper calling the original generation function](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_sparse_memory.py).

## Timing and provenance

| Configuration | Model loading | Page preparation | Other wrapper time | Summed time to first chunk | Output tokens | Peak MLX allocation | Parse errors | Timeouts | Token caps reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen3.6-27B 4-bit — single image | 19.9 s | 1.1 s | — | 31.2 min | 2426 | 20.2 GB | 0 | 0 | 0 |
| Qwen3.6-35B-A3B 4-bit — single image | 23.6 s | 1.0 s | — | 4.7 min | 2311 | 22.9 GB | 0 | 0 | 0 |
| Qwen3.6-35B-A3B 4-bit — visual memory | 23.6 s | — | 1.4 s | — | 2327 | 23.3 GB | 0 | 0 | 0 |

In the single-image trials, summed time to the first chunk was 31.2 of 34.0 minutes for the 27B model and 4.7 of 5.2 minutes for the sparse model (about 92% and 90%). This interval includes input processing and the first generated token; it is not an isolated GPU-stage profile. Accelerating only the remaining output-token loop has limited room to improve the total.

Runs use the shared Apple M4 Pro with 48 GB memory. The main-table time sums generation calls, including their image/text processing, to match the earlier runner's timing boundary. It excludes model downloads, loading and the previously performed candidate/tag extraction. Separate records retain model loading, generated token counts, timeouts, parse failures and peak MLX allocation. The single-image runner also records per-page rendering/prompt preparation and time to first streamed chunk. The visual-memory wrapper instead records all work outside generation together (including image/prompt preparation, parsing and writing); its reused generator does not expose first-token timing, which remains unavailable. Peak MLX allocation is not total system memory. These are single runs on a shared machine, not repeated controlled hardware benchmarks; speed ratios are observational.

Native page text is exported with the raw page records. We did not rerun an independent prose-retention evaluation, so that field remains blank in the main table. No paid inference API was used. Local hardware, power and elapsed time still have costs; there is no invented dollar charge per page.

An interrupted 27B attempt (run 001) ended before any page result was written. The completed restart uses a fresh run directory (002) with the same settings. The initial 35B model download was also interrupted and resumed from its partial cache. These partial attempts do not contribute scores or inference timings.

Compact evidence is stored under [outputs/qwen-compact/evidence](https://github.com/dividor/pdf-heading-benchmark/tree/codex/technique-explorer/outputs/qwen-compact/evidence). It includes every audited prediction, per-page telemetry, model revisions, package versions, source/input checksums and the protocol written before model loading. Downloaded weights, PDFs and full raw text remain outside Git.

## Reproduce

Use the repository setup instructions to download the four PDFs and prepare the existing PyMuPDF4LLM candidates and PDF tags in an external data directory. Use an Apple Silicon environment with the pinned [MLX requirements](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/mlx.txt), and set `PYTHONPATH=src` when invoking the standalone runner from the repository root.

```sh
export PDF_BENCHMARK_DATA=/absolute/path/to/external-data
export HF_HOME=/absolute/path/to/external-model-cache
export PYTHONPATH=src
python scripts/runners/prepare_model.py Qwen3.6-27B-4bit
python scripts/runners/prepare_model.py Qwen3.6-35B-A3B-4bit
python scripts/runners/run_qwen_compact.py \
  --input-data "$PDF_BENCHMARK_DATA" \
  --model Qwen3.6-27B-4bit \
  --model-record "$PDF_BENCHMARK_DATA/models/download-Qwen3.6-27B-4bit.json" \
  --output "$PDF_BENCHMARK_DATA/qwen-compact/27b-run-002"
python scripts/runners/run_qwen_compact.py \
  --input-data "$PDF_BENCHMARK_DATA" \
  --model Qwen3.6-35B-A3B-4bit \
  --model-record "$PDF_BENCHMARK_DATA/models/download-Qwen3.6-35B-A3B-4bit.json" \
  --output "$PDF_BENCHMARK_DATA/qwen-compact/35b-run-001"
```

The runner refuses existing output directories. For the follow-up, run:

```sh
python scripts/runners/run_qwen_sparse_memory.py \
  --input-data "$PDF_BENCHMARK_DATA" \
  --model-record "$PDF_BENCHMARK_DATA/models/download-Qwen3.6-35B-A3B-4bit.json" \
  --output "$PDF_BENCHMARK_DATA/qwen-compact/35b-memory-run-001"
```

Run the models sequentially to avoid GPU/memory contention. To regenerate the published report without any models, use `uv run python scripts/qwen_compact_report.py` followed by `uv run pdf-headings report`. Importing a new run requires explicit `--runs /absolute/path/to/external-data/qwen-compact`; the importer checks inference source checksums before copying compact evidence. Keep fresh run directories and distinct published rows when changing settings.
