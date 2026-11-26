# Reproducibility and interpretation

## Corpus and reference

Four born-digital WFP evaluation reports, 523 pages in total; three English reports and one Spanish report. `configs/corpus.json` records source URLs, page counts and SHA256 hashes. Downloads fail if a source changes. `configs/audit_pages.json` identifies eight selected pages per report. `configs/gold.json` contains 77 visually annotated headings (15 targeting, 18 midterm, 21 Indonesia, 23 Colombia).

The annotation was produced by a single assistant, without independent human adjudication or inter-annotator measurement. Page selection was purposive, not randomized. Cover titles do not shift chapter levels; main chapters and individual annexes are H1. The older 2018 resilience evaluation was excluded after document-specific investigation. No special correction for any of these four reports is applied.

The original gold file SHA256 was `6cd638fb840879fd997238c599aa6e1db5ec4063852a8177f2fbf2e811a675db`. Repository JSON formatting adds a trailing newline; the bundled file's hash is in `configs/gold.sha256`. Parsed labels are unchanged. The historical source hashes and new-model package versions are preserved in `outputs/historical_environment.json`.

## Scoring

`src/pdf_heading_benchmark/evaluation.py` preserves the original evaluation contract. Titles are stripped of HTML tags, Unicode NFKC-normalized, case-folded and reduced to alphanumeric characters. Similarities are `SequenceMatcher(..., autojunk=False)` ratios on the same original PDF page. Hungarian assignment maximizes total similarity, then matches below 0.90 are discarded. This assignment-before-threshold detail is intentional historical behavior, not a claim that it is the only reasonable matching algorithm.

A recovered heading counts as a correct pair only if its integer level equals the reference. The primary score is joint F0.5 = 1.25C / (P + 0.25G), where C counts correct pairs, P all predictions and G all 77 reference headings. Wrong levels and extra predictions both reduce this score. Joint recall C/G and joint precision C/P are shown separately. Null levels cannot earn a correct-level point. Missing runs remain unscored. Original records also include exploratory shift/order diagnostics; these are not used for ranking, and no gold-tuned shift is applied.

`outputs/audit_predictions.json` holds every completed configuration's predictions on the audited pages. `score --historical` reproduces the table counts. `outputs/league_details.json` preserves the original per-report matches and errors, including those additional diagnostics. `outputs/text_retention.json` retains page-level text numerator/denominator counts. Published summaries remain frozen when you run new experiments; fresh scores are written to the external data directory instead of overwriting the published evidence.

## Method implementations

`configs/methods.json` is the single mapping from configuration names to descriptions and executable steps. The Method column links each configuration to its final runner. Dependencies (candidate extraction, tag context, model preparation) are included in the same configuration. All inference runners use only document text, page images, candidate outputs and the selected page numbers. They do not read reference titles or levels.

- **Docling 2.151.1:** CPU, eight threads, OCR and table reconstruction disabled, parsed pages retained. Default, built-in hierarchy and fixed `style_size_tolerance=0.15` share the same detected blocks. The last is exploratory, not a learned general calibration.
- **PyMuPDF4LLM 2.1:** full-document page chunks, OCR disabled, Markdown H1–H6 headings with page provenance.
- **Marker 2.2:** full documents, CPU no-OCR/no-LLM, JSON SectionHeader blocks and their HTML levels.
- **MinerU 4.2.3 basic:** full documents, ONNX CPU, automatic parse mode, no external LLM or image analysis, native title-block levels.
- **Embedded tags:** H1–H6 elements and their marked content on the selected pages. No inferred hierarchy.
- **LightOnOCR-3-0.8B:** MLX, author's `grounding` prompt, page render at 400 dpi downscaled to 2048 pixels, greedy decoding, 8192-token limit, 300-second soft timeout. Decode native title blocks and documented `+` continuations.
- **LightOnOCR-3-4B / Chandra OCR 2:** upstream prompt and rendering, MLX batching. LightOn batch size two and 2048-pixel cap; Chandra batch size four, minimum rendering resolution and upstream grid/pixel scaling. 12384-token batch cap. The batch wrapper checks that it preserves the upstream chat template. Historical LightOn 4B retained five earlier single-page outputs (12288-token cap), then used batches. Fresh runs batch all pages. Chandra's pixel budget was 16 million.
- **MinerU Pro:** direct MLX `two_step_extract`, image analysis disabled, 400 dpi downscaled to 2048. The model detects title blocks, but this interface supplied no heading levels. No hierarchy model was added afterward.
- **Qwen3.5 candidate reranking:** 4-bit MLX; full-document candidate IDs with titles and pages, no images. Output must map every ID to an integer level or null. Candidate sources are PyMuPDF, MinerU, or the union of Docling + PyMuPDF (0.90 same-page fuzzy deduplication). Greedy, 4096 tokens, thinking disabled. Invalid output rejects the candidates and remains recorded as an error.
- **Qwen3.6 sampled visual memory:** 27B 4-bit MLX, native page text, full-document PyMuPDF candidate titles without levels, full-document PDF heading tags, current image (1792-pixel cap), and previous sampled-page images (1280 cap) for the latest predicted heading at each H1–H6. Only earlier processed sampled pages can become visual memory. Greedy, 4096-token cap, 600-second soft timeout, seed 42. Generic JSON decoding accepts an array, a `headings` wrapper or one fenced JSON block; no values are repaired. Seven historical formatting deviations were accepted this way. This is not a reproduction of a paper's full-document benchmark. New Markdown output preserves native page text; predicted headings are separate JSON.
- **Qwen3.6 single-image trials:** the pinned 27B and 35B-A3B MLX 4-bit models use the same full text context and a single current-page image capped at 1280 pixels, with previous predictions as text only. Both are newly executed regression trials on the 32 audit pages. [Exact settings, provenance and commands](qwen-compact.md).
- **Popo:** experimental 8-bit affine MLX conversion (group size 64), upstream title filtering/chunking/mosaics and overlap bias alignment, eight-page chunks rather than the upstream larger setting. Starts from Docling candidates, demotes unassigned/negative levels according to the upstream acceptance contract. No gold-label correction. Code and model revisions are pinned in the setup runner.

## Costs, timing and text

The current report includes local inference configurations only. Hardware, electricity, licensing, engineering and review were not priced in dollars. Model licenses may affect commercial use.

Timings are observational on a shared 48 GB Apple M4 Pro. Earlier CPU inputs span all 523 pages; the new image models span 32 audit pages; hierarchy-only methods omit the upstream candidate-extraction time. New-model measurements exclude loading, downloads and aborted adapter attempts; earlier CPU runs may include setup. Batch wall time was allocated equally to pages. Do not compare these as controlled pages-per-second benchmarks.

Native prose retention is a proxy: five-word sequence recall against native PDF text blocks of at least 50 words, on the 32 audit pages. It does not establish character accuracy, reading order or table fidelity. `scripts/runners/evaluate_text.py` is the original text-retention protocol and expects the baseline document outputs; it can be run after all CPU baselines are available. The compact committed counts allow the published weighted values to be checked without re-OCR.

## What packaging changed and what was verified

The original experiment scripts were reorganized for portable paths, external data, explicit dependencies and small functions. Core dependency versions are locked; heavyweight backend manifests pin principal versions but not every transitive dependency. Upstream prompts, model revisions and inference settings are retained except the disclosed clean-run LightOn batching difference. Error handling no longer silently falls back to a different model path. Model-generated malformed values are retained as failures; runtime setup errors stop the run.

Offline tests recalculate all published heading scores and check decoding, page provenance, missing levels, one-to-one matching, paid-job resumption, missing credentials, and deterministic reports. The PDF download/hash path and complete PDF-tag and PyMuPDF CPU runs are smoke-tested separately. The packaged Qwen, Chandra and LightOn decoders were also replayed against 128 saved raw page responses, and the Azure decoder against four full-document responses; their final heading exports match the historical exports. Refactored model adapters have not all been re-executed through full inference; these are historical measured results accompanied by packaged runners, not a claim of a second complete benchmark.

Use a fresh external run directory when changing prompts, revisions or documents. Resuming assumes unchanged inputs and configuration. A full-document run on your own PDF is useful experimentation, but requires its own reference labels to establish accuracy.

## Repeat the GPU configurations sequentially

Use the pinned MLX environment, with models and original candidate/tag inputs already prepared. The output directory must be new. The queue runs seven configurations in separate processes and stops on a failed process; it never fills missing predictions with historical output. GPU selection is checked inside each inference process.

```bash
PYTHONPATH=src /path/to/mlx-env/bin/python scripts/runners/repeat_models.py \
  --input-data /path/to/prepared-benchmark-data \
  --extra-models /path/to/additional-model-download-records \
  --output /path/to/new-sequential-run
uv run python scripts/repeat_report.py --run /path/to/new-sequential-run
uv run pdf-headings report
```

The import rejects changed source/input hashes and incomplete audit scopes. Only successfully completed configurations are scored. Raw responses and system telemetry stay outside Git; compact predictions, page timings and aggregate telemetry are sufficient to regenerate the public comparison offline using `uv run python scripts/repeat_report.py`. The main league retains the frozen heading predictions and scores; its timing column adopts a completed rerun only after exact equality of page/title/level predictions is verified. Earlier measurements remain in the repeat comparison. [Timing definitions and batching caveat](sequential-repeat.md).

To refresh the local HTML report as each configuration completes, run the importer in a second terminal with `--run /path/to/new-sequential-run --watch`. It stops when the queue finishes or a completed process reports failure. It does not commit or push results.

## New field candidates

See [the field-trial protocol](field-candidates.md) for pinned MiniCPM-OCR 1.0, Xiaomi-OCR-0 and PaddleOCR-VL-1.6 runs. These use pixels only, with no PDF tags or candidate-heading inputs. The portable region pipelines combine a CPU layout detector, MLX recognition and documented Markdown assembly. Their frozen compact evidence is in `outputs/field-candidates/`; `scripts/field_candidates_report.py` independently recomputes their scores offline.

## EvidenceLab and forced OCR

[The full-document pipeline protocol](evidencelab-and-ocr.md) records the pinned EvidenceLab image and post-processor, and Docling’s forced RapidOCR configuration. Both ran on all four complete PDFs, one parser at a time. Model revisions and weight hashes are committed; the runner archives its source, options and input hashes. `scripts/pipeline_report.py` rebuilds their scores from compact published evidence, and CI checks that the report regenerates unchanged.
