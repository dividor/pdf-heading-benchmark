# New OCR candidates: local WFP protocol

The [OpenBMB field diagram](published-comparison.md) motivated three additional candidates: MiniCPM-OCR 1.0 (1.3B), Xiaomi-OCR-0 (0.8B), and PaddleOCR-VL-1.6 (0.9B). The published chart reports broad document parsing and NVIDIA throughput. Our experiment measures native heading titles and hierarchy on Apple Silicon. These are different tests.

[Completed local results and timing details](../outputs/field-candidates/report.md) · [Full comparison with earlier methods](../outputs/report/league_table.md)

## Documents and measurements

Use the unchanged [four public WFP PDFs](../configs/corpus.json), [32 sampled physical PDF pages](../configs/audit_pages.json), and [77 reference headings](../configs/gold.json). The corpus manifest links the original WFP downloads and records their checksums. This is the existing exploratory audit set, not an independent new holdout. Reference annotations were prepared by an assistant and have not received independent human adjudication.

Rank by joint heading-and-level F0.5: **1.25C / (P + 0.25G)**. C counts one-to-one matches with the correct title, page and exact level; P is every prediction; G is every reference heading. Wrong levels count as both a joint false positive and false negative. The same existing title matcher is used for every method. Show joint precision C/P and joint recall C/G alongside the score.

The input is a 200 DPI image of each selected page. These new trials receive no native PDF text, PDF structure tags, TOC, reference labels or previous-page memory. This is a stricter input condition than the earlier Qwen experiments, which received additional document context. Scores therefore compare configurations, not isolated model capability.

Run one candidate at a time on an Apple M4 Pro with 48 GB unified memory. Recognition uses MLX Metal GPU kernels. Region layout uses four CPU threads; page and region concurrency are both one. Timings include rendering, layout when present, recognition and Markdown assembly. Loading is recorded separately. These runs are not GPU-only timing measurements and do not replicate the external RTX 5090 throughput experiment.

## Exactly what each pipeline does

**MiniCPM-OCR 1.0:** the pinned PP-DocLayoutV3 detector identifies regions on CPU (threshold 0.3, non-maximum suppression enabled). MiniCPM SDK 1.0.5 supplies ordered crops and class-specific prompts; MLX runs the original BF16 recognition weights. Use the SDK's native Markdown assembly: document titles become H1; paragraph titles use its numbered formatter (“2” → H2, “2.1” → H3, unnumbered → H2). Do not correct this offset to suit the WFP reference. Tables use the SDK's OTSL conversion.

**Xiaomi-OCR-0:** run the documented whole-page `e2e_img2md.py` prompt with original BF16 weights through MLX's Qwen3.5 implementation. Request the main body in reading order, Markdown, OTSL tables and LaTeX formulas, omitting headers and footers. Preserve its own Markdown heading levels. This is **not** the two-stage configuration behind Xiaomi's strongest published results.

**PaddleOCR-VL-1.6:** use the same pinned layout detector and MiniCPM SDK assembly, replacing region recognition with Paddle's original BF16 model through MLX. Use Paddle task prompts: `OCR:`, `Table Recognition:`, `Formula Recognition:`, `Chart Recognition:` and `Seal Recognition:`. This is an explicitly documented portable adaptation, **not** the full official PaddleOCR CUDA pipeline. Its hierarchy logic comes from the assembly component.

All trials use temperature 0, seed 42 and thinking disabled. Xiaomi has a 16,384-token page limit; regional trials use SDK class budgets (titles 512, text 4096, tables 8192, display formulas 2048, charts 4096, seals 256). A soft 600-second timeout is checked between streamed chunks for each recognition request. Timeouts and token caps are retained in the evidence. No weights are fine-tuned. A cover page outside the audit set is used only to verify runtime compatibility.

The Markdown parser reads actual heading tokens, including setext headings. It does not turn bold paragraphs or code comments into headings. Native prose retention is the fraction of five-word sequences recovered from native PDF paragraphs of at least 50 words, pooled across pages; it does not measure tables or reading order.

## Reproduce

Install the pinned [field-trial environment](../configs/environments/field-mlx.txt), which extends the existing MLX environment with Torch 2.15.0 and MiniCPM SDK 1.0.5. On the test host the SDK was installed with `--no-deps` into a separate directory, leaving the existing MLX environment unchanged. Set `PYTHONPATH` to that directory and this repository's `src` directory if following that arrangement. The SDK provides components used directly by our adapter; this is not its packaged CUDA serving workflow.

The standard CLI wrapper, `uv run pdf-headings run minicpm_ocr10`, installs this optional environment, downloads the pinned weights outside Git, and creates a fresh timestamped trial directory. The explicit commands below allow reuse of a prepared MLX environment and model cache.

Download the WFP corpus with `PDF_BENCHMARK_DATA=/path/to/data uv run pdf-headings download`; the downloader checks the manifest hashes. Download model revisions with:

```bash
python scripts/runners/prepare_field_candidates.py --cache /path/to/hf-cache --records /path/to/trial
```

The [model manifest](../configs/field-candidates.json) pins all four repositories to exact revisions. Then run each candidate in sequence, using a fresh output directory:

```bash
python scripts/runners/run_field_candidate.py minicpm_ocr10 \
  --input-data /path/to/data --downloads /path/to/trial \
  --output /path/to/trial/minicpm_ocr10
# After it exits, repeat for xiaomi_ocr0, then paddleocr_vl16.
```

The external data folder contains `corpus/targeting.pdf`, `midterm.pdf`, `indonesia.pdf` and `colombia.pdf`. `--smoke` processes only the targeting report cover and cannot be imported as a score. Complete runs save raw page text and region responses, predictions, timing, exact model revisions, source/PDF checksums and runtime versions. Large files stay outside Git.

Import each completed run and rebuild the main report:

```bash
uv run python scripts/field_candidates_report.py --runs /path/to/trial \
  --data /path/to/data --candidate minicpm_ocr10
uv run pdf-headings report
```

The importer verifies model pins, page coverage, source and PDF checksums, prediction consistency and timing totals. Compact evidence under `outputs/field-candidates/` is committed for offline verification. Thereafter `uv run python scripts/field_candidates_report.py` recomputes the scores without weights, PDFs or network access. The interactive report exposes each method's exact parameters, source links and predicted-versus-reference headings.

## Run interruptions

The [attempt record](../outputs/field-candidates/attempts.json) identifies which runs contributed scores.

The first Xiaomi audit attempt was interrupted when the external USB data drive disconnected. It is excluded from scores and timing. After the drive remounted, the complete 32-page trial was restarted in a fresh directory; no page results or timings were spliced across attempts. MiniCPM completed before the interruption.
