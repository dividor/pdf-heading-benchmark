# On-premises PDF heading benchmark: scores, timings and methods

**22 completed local configurations, suitable for on-premises inference.** This experiment asks whether parsers and local models can recover heading titles, PDF pages and levels while retaining the text of long WFP evaluation reports.

**Primary metric: joint heading-and-level F0.5, with a 95% heading-detection precision requirement.** Both incorrect levels and extra headings reduce the joint score. The precision gate separately requires at most 5% spurious headings among predictions on this sample. FAIL rows remain visible but do not qualify. Definitions and a worked example follow the table.

Qwen3.6-27B with sampled visual memory leads at **82.7% joint F0.5**, with **97.5% heading precision**, 65/77 correct heading-level pairs and two extras. Embedded PDF tags score **73.4% F0.5**, with 96.3% heading precision and 43/77 correct pairs. Chandra scores **72.6% F0.5**, 97.2% heading precision and 53/77 correct pairs. These are configuration-specific results from a small, assistant-annotated sample, without independent human validation.

**Our new precision-selected method:** [jump to the highlighted row](#our-trained-model). A validation-selected confidence filter raises historical joint F0.5 from **58.8% to 70.5%** and reduces extra headings from **23 to 2**, reaching **95.1% heading precision**. It emits fewer headings: correct title-and-level pairs fall from **50/77 to 34/77**, with 38 titles missed. This is an explicit precision/recall trade-off. The three small CPU classifiers are unchanged; the LLM supplied training annotations and is not used at inference.

The candidate was selected from a fixed 36-setting grid on four separate validation reports. The original league and the previously inspected 38-heading set were scored only after selection. Both are regression evidence, not new independent tests. The precision gate is an observed sample threshold, not a statistical confidence bound or production guarantee. [Experiment, every setting and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-precision/report.md).

[Repository and runnable instructions](https://github.com/dividor/pdf-heading-benchmark) · [Markdown report](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/report/league_table.md) · [Score exports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/report/results.json)

## Documents and their sources

All four PDFs were obtained from WFP's public document servers. Each title below links directly to its official source PDF. The [corpus manifest](https://github.com/dividor/pdf-heading-benchmark/blob/main/configs/corpus.json) records the download URLs, page counts and SHA-256 hashes; the downloader verifies the files against those hashes.

The corpus contains **523 pages: three English reports and one Spanish report**. All four contain native digital text. None has PDF outline bookmarks, although embedded structure tags provide another possible source of headings. This does not test scanned-document performance. The original 2018 resilience report that prompted the investigation was excluded after document-specific exploratory work.

The audit covers **eight selected pages per report, 32 pages and 77 reference headings in total**. Page numbers below are **one-based physical PDF pages**, including covers and front matter, rather than printed page labels. These are the exact pages scored for every completed configuration.

| WFP report / official PDF | Language | PDF pages | Audited PDF pages | Reference headings |
| --- | --- | --- | --- | --- |
| [Strategic evaluation of WFP’s Approaches to Targeting and Prioritization for Food and Nutrition Assistance](https://api.godocs.wfp.org/api/documents/WFP-0000171594/download/) | English | 172 | 7, 11, 24, 27, 33, 67, 96, 109 | 15 |
| [Mid-Term Evaluation of WFP’s Strategic Plan 2022–2025](https://docs.wfp.org/api/documents/WFP-0000162023/download/) | English | 176 | 8, 10, 26, 27, 36, 61, 87, 98 | 18 |
| [Evaluation of Indonesia WFP country strategic plan 2021–2025 — Volume I](https://docs.wfp.org/api/documents/WFP-0000168942/download/) | English | 76 | 7, 11, 20, 33, 42, 48, 56, 68 | 21 |
| [Evaluación del Plan estratégico para Colombia 2021–2024](https://docs.wfp.org/api/documents/WFP-0000157262/download/) | Spanish | 99 | 7, 13, 28, 42, 56, 72, 73, 93 | 23 |

## What was tested and how

1. **Select and annotate pages.** Pages were deliberately selected across front matter, chapters, subsections and annexes. A single AI assistant visually annotated heading titles and levels. The [page selection](https://github.com/dividor/pdf-heading-benchmark/blob/main/configs/audit_pages.json) and [frozen reference labels](https://github.com/dividor/pdf-heading-benchmark/blob/main/configs/gold.json) are public. They have not been independently reviewed by a human, and the selection is not random.
2. **Run the configured extractor or hierarchy stage.** CPU parsers processed all 523 pages; the later local OCR models processed the 32 audit pages. Hierarchy stages consumed extracted candidates and, for some configurations, PDF tags or page images. No reference titles or reference levels were supplied to inference. The table links to each runner; [method configuration steps](https://github.com/dividor/pdf-heading-benchmark/blob/main/configs/methods.json), [model revisions](https://github.com/dividor/pdf-heading-benchmark/blob/main/configs/models.json) and [reproducibility notes](https://github.com/dividor/pdf-heading-benchmark/blob/main/docs/reproducibility.md) give dependencies, prompts and settings. No per-report heading correction rules are applied.
3. **Score the same audit pages.** The [scorer](https://github.com/dividor/pdf-heading-benchmark/blob/main/src/pdf_heading_benchmark/evaluation.py) matches titles on the same original PDF page, using normalized text similarity of at least 90% after one-to-one Hungarian assignment. A combined success requires the exact reference H level too. Main chapters and annexes are H1; the cover title does not shift the body hierarchy. Missing headings remain in the denominator of 77. Extra predictions are counted separately, so the combined score is not precision or F1 and does not penalize false headings directly.
4. **Check prose and record resources.** Native prose retention measures preserved five-word sequences from native PDF blocks of at least 50 words on the audit pages. It does not measure character accuracy, reading order or table extraction. Processing times were observed on a shared 48 GB Apple M4 Pro and have different scopes. Hardware, electricity, engineering, review and licensing costs were not measured in dollars.

This is **sampled-page heading accuracy**, even when a parser processed the full document. The completed configurations include variants of the same packages and models; they are not independent products. The single annotator, small purposive sample and exploratory configuration choices limit any claim about general robustness.

## Full configuration results

**Ranked by joint heading-and-level F0.5**, with a separate **95% heading-detection precision gate**. Only PASS rows qualify on this sample. The first score column is highlighted; FAIL rows remain visible for comparison. See the definitions and worked example below the table. In HTML, select the **i** beside a configuration, or its **Method / code** for its diagram, parameters and sources. Markdown retains those links and the detailed technique appendix. All configurations ran locally. Missing measurements remain unavailable rather than being assigned zero.

| Configuration | Primary score: joint F0.5 | Heading precision / 95% gate | Method / code | Status | Correct heading + level | Headings recovered | False headings | Native prose retention | Measured time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Qwen3.6-27B / MLX 4-bit / sampled visual memory](https://huggingface.co/Qwen/Qwen3.6-27B) | **82.7%** | 97.5% · PASS | [32 targets; Qwen3.6-27B MLX 4-bit, native text, full-document candidates/tags, prior sampled-page images.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_visual_memory.py) | completed | 84.4% (65/77) | 100.0% (77/77) | 2 | — | 61.8 min / 32 pages |
| [Embedded PDF heading tags](https://www.w3.org/WAI/WCAG22/Techniques/pdf/PDF9) | **73.4%** | 96.3% · PASS | [Read author H1–H6 structure-tree tags on 32 audit pages; no inferred repairs.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_pdf_tags.py) | completed | 55.8% (43/77) | 67.5% (52/77) | 2 | — | 6.4 s / 32 pages |
| [Chandra OCR 2 / MLX](https://huggingface.co/datalab-to/chandra-ocr-2) | **72.6%** | 97.2% · PASS | [32 images; author OCR-layout prompt/rendering; MLX batch 4; read HTML heading levels.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_chandra_batch.py) | completed | 68.8% (53/77) | 90.9% (70/77) | 2 | 98.7% | 17.2 min / 32 pages |
| <span id="our-trained-model"></span>[**OUR METHOD — confidence-filtered v2 (F0.5-selected)**](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-precision/report.md) | **70.5%** | 95.1% · PASS | [OUR METHOD — frozen v2 trees; validation-selected heading score ≥0.70, body weight 1, relation weight 1. Optimize joint F0.5 subject to ≥95% heading precision. CPU; regression evidence.](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/optimize_precision.py) | completed | 44.2% (34/77) | 50.6% (39/77) | 2 | — | 11.7 s / 523 pages |
| <span id="our-calibrated-model"></span>[**OUR METHOD — calibrated decoding (experimental)**](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-calibration/report.md) | **59.2%** | 73.8% · FAIL | [OUR METHOD v2 + validation-selected decoding: body score ×2; relation weight 1. Same frozen trees and annotations. CPU; historical diagnostic, not a fresh test.](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/calibrate.py) | completed | 61.0% (47/77) | 76.6% (59/77) | 21 | — | 14.5 s / 523 pages |
| <span id="our-original-model"></span>[OUR METHOD — grouped context v2 (previous selection)](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md) | **58.8%** | 73.6% · FAIL | [OUR METHOD v2: learned grouping + document style/TOC features + learned level relationships. Selected on separate validation reports; CPU. Historical diagnostic.](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) | completed | 64.9% (50/77) | 83.1% (64/77) | 23 | — | 12.6 s / 523 pages |
| [LightOnOCR-3-0.8B / MLX](https://huggingface.co/lightonai/LightOnOCR-3-0.8B) | **57.9%** | 90.0% · FAIL | [32 page images; 0.8B MLX, grounding prompt, greedy 8192 tokens; decode title/continuation blocks.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_lighton_mlx.py) | completed | 59.7% (46/77) | 93.5% (72/77) | 8 | 99.5% | 8.9 min / 32 pages |
| [LightOnOCR-3-4B / MLX grounding](https://huggingface.co/lightonai/LightOnOCR-3-4B) | **57.9%** | 90.0% · FAIL | [32 images; MLX grounding prompt, 2048-pixel limit; batch 2 after 5 single-page historical checkpoints.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_chandra_batch.py) | completed | 59.7% (46/77) | 93.5% (72/77) | 8 | 99.3% | 23.5 min / 32 pages |
| [v2: learned grouping](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md) | **55.8%** | 77.9% · FAIL | [LLM annotations → learned line joining across PDF blocks → group-level Extra Trees. Same expanded training set; CPU; historical diagnostic.](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) | completed | 66.2% (51/77) | 96.1% (74/77) | 21 | — | 12.0 s / 523 pages |
| [v2: more annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md) | **44.9%** | 72.6% · FAIL | [LLM annotations → Extra Trees v2: 887 heading groups on 20 training reports; original line classifier and grouping. CPU; historical diagnostic.](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) | completed | 53.2% (41/77) | 89.6% (69/77) | 26 | — | 9.3 s / 523 pages |
| [LLM annotations → Extra Trees v1 (CPU)](https://github.com/dividor/pdf-heading-benchmark/blob/main/src/pdf_heading_benchmark/supervised_models.py) | **44.5%** | 74.7% · FAIL | [LLM-assisted visual annotations → 200-tree Extra Trees classifier trained on 16 different WFP reports → local CPU inference using PyMuPDF line features. Full PDFs; no refit on benchmark.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/supervised/compare.py) | completed | 45.5% (35/77) | 76.6% (59/77) | 20 | — | 7.7 s / 523 pages |
| [MinerU 4.2.3 basic CPU](https://github.com/opendatalab/MinerU) | **44.4%** | 97.1% · PASS | [Full PDFs; basic ONNX CPU tier, no external LLM; native title-block levels.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_mineru.py) | completed | 40.3% (31/77) | 85.7% (66/77) | 2 | 99.1% | 11.2 min / 523 pages |
| [Qwen3.5-4B / union candidates](https://huggingface.co/Qwen/Qwen3.5-4B) | **41.0%** | 94.7% · FAIL | [Full-document candidate IDs + Qwen3.5-4B MLX 4-bit; JSON levels/null, no images; source: union.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) | completed | 32.5% (25/77) | 70.1% (54/77) | 3 | — | 1.7 min / hierarchy stage only |
| [Qwen3.5-4B / PyMuPDF candidates](https://huggingface.co/Qwen/Qwen3.5-4B) | **37.5%** | 100.0% · PASS | [Full-document candidate IDs + Qwen3.5-4B MLX 4-bit; JSON levels/null, no images; source: pymupdf4llm.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) | completed | 28.6% (22/77) | 70.1% (54/77) | 0 | — | 1.5 min / hierarchy stage only |
| [PyMuPDF4LLM 2.1](https://github.com/pymupdf/pymupdf4llm) | **37.5%** | 97.3% · PASS | [Full PDFs to page-chunk Markdown; read Markdown heading levels and page provenance.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_pymupdf4llm.py) | completed | 36.4% (28/77) | 93.5% (72/77) | 2 | 98.8% | 51.8 s / 523 pages |
| [Qwen3.5-4B / MinerU candidates](https://huggingface.co/Qwen/Qwen3.5-4B) | **33.3%** | 98.5% · PASS | [Full-document candidate IDs + Qwen3.5-4B MLX 4-bit; JSON levels/null, no images; source: mineru_basic.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) | completed | 29.9% (23/77) | 85.7% (66/77) | 1 | — | 1.3 min / hierarchy stage only |
| [Docling fixed tolerance 0.15](https://github.com/docling-project/docling) | **30.8%** | 97.1% · PASS | [Same blocks, fixed style_size_tolerance=0.15 on every report; exploratory variant.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) | completed | 28.6% (22/77) | 88.3% (68/77) | 2 | 98.4% | 1.7 min / 523 pages |
| [Marker 2.2 no OCR/LLM](https://github.com/datalab-to/marker) | **25.5%** | 87.8% · FAIL | [Full PDFs; CPU no-OCR/no-LLM; decode SectionHeader HTML tags.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_marker.py) | completed | 24.7% (19/77) | 84.4% (65/77) | 9 | 98.8% | 44.0 s / 523 pages |
| [Docling 2.151.1 default](https://github.com/docling-project/docling) | **22.4%** | 97.1% · PASS | [CPU, OCR and tables off; native SectionHeaderItem levels; full PDFs.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) | completed | 20.8% (16/77) | 88.3% (68/77) | 2 | 98.4% | 1.7 min / 523 pages |
| [Docling built-in hierarchy](https://github.com/docling-project/docling) | **22.4%** | 97.1% · PASS | [Same Docling blocks, built-in HeadingHierarchyModel enabled.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) | completed | 20.8% (16/77) | 88.3% (68/77) | 2 | 98.4% | 1.7 min / 523 pages |
| [Popo + Docling / experimental MLX 8-bit](https://github.com/opendatalab/MinerU-Popo) | **21.0%** | 97.1% · PASS | [Docling candidates + Popo MLX 8-bit; 8-page chunks, page mosaics, upstream overlap alignment; experimental port.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_popo_mlx.py) | completed | 19.5% (15/77) | 88.3% (68/77) | 2 | 98.4% | 14.9 min / hierarchy stage only |
| [MinerU2.5-Pro-2605-1.2B / direct MLX interface](https://huggingface.co/opendatalab/MinerU2.5-Pro-2605-1.2B) | **0.0%** | 95.8% · PASS | [32 images; direct MLX two_step_extract; preserve title blocks and absent levels as null.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_mineru_pro.py) | completed | Levels not supplied (0/77 complete outputs) | 89.6% (69/77) | 3 | 99.0% | 9.5 min / 32 pages |

## Primary metric: heading-and-level F0.5

A useful output must identify a real heading, put it on the correct PDF page and assign the correct level. Invented headings also matter. We therefore rank by **joint heading-and-level F0.5**, and require **at least 95% heading-detection precision** for a configuration to qualify on the evaluated sample. A high score with a FAIL label does not qualify.

Let **G** be the number of reference headings, **P** all predicted headings, **M** the one-to-one title/page matches and **C** those matches with the exact reference level. Matching uses the unchanged same-page, normalized-title similarity ≥0.90 contract. Counts are pooled across reports before calculating metrics (micro averaging).

| Measure | Definition | What it tells us |
| --- | --- | --- |
| Joint precision | C / P | Fraction of emitted headings with both title/page and level correct |
| Joint recall | C / G | Fraction of reference headings recovered at the correct level |
| Joint F1 | 2C / (P + G) | Equal precision/recall emphasis |
| **Joint F0.5** | **1.25C / (P + 0.25G)** | Primary score; emphasizes precision more than recall |
| Heading-detection precision | M / P | Fraction of predictions that are real headings, regardless of level |
| **95% precision gate** | **P > 0 and M / P ≥ 0.95** | At most 5% of emitted headings are spurious on this sample |

Joint true positives are **C**, false positives are **P − C**, and false negatives are **G − C**. A wrong-level heading is both a joint false positive and a joint false negative. A missing heading contributes a false negative; an extra heading contributes a false positive. No predictions gives a zero score and fails the gate. Unknown levels earn no joint credit. The gate concerns real-heading detection; it does **not** mean 95% of levels are correct, and it is an observed sample threshold, not a confidence bound or deployment guarantee.

For example, 10 reference headings, 12 predictions, 10 title matches and 9 correct levels give joint precision 75%, recall 90%, F1 81.8% and F0.5 77.6%. Heading precision is only 83.3%, so this configuration fails the gate despite recovering every title.

For optimization, select the highest validation joint F0.5 **among candidates passing the gate**, then freeze the configuration before evaluation elsewhere. If none qualifies, report no qualifying candidate. Do not choose settings using the main league or inspected regression pages. Existing F1-selected runs retain their original provenance; recomputing these metrics does not retrain them.


## How to read the table

**Local resources and cost:** all configurations in this report ran locally on a shared 48 GB Apple M4 Pro. Hardware, electricity, setup, engineering, manual review and commercial licensing costs were not measured in dollars. Observed processing times are reported with their actual scope; local inference is not cost-free.

**Scopes and timing:** earlier CPU parsers processed all 523 pages. New local OCR models processed the complete text on the 32 audit pages. Qwen3.6 read native page text, full-document candidate titles and author PDF tags, and current/previous sampled-page images; it does not OCR the body. Its measured time excludes those candidate-generation stages. Qwen3.5 and Popo timings cover only hierarchy inference. Hardware was a shared 48 GB Apple M4 Pro. New-model times exclude downloads, loading and aborted attempts; some earlier CPU times include setup. These are observations with different scopes, not a controlled throughput benchmark.

**Text:** native prose retention measures five-word sequences preserved from native PDF blocks of at least 50 words, on the audit pages. It is not character accuracy, reading order, semantic accuracy or table correctness. A missing score means not evaluated or not applicable. Hierarchy-only stages reuse extracted text.

**Configuration caveats:** MinerU Pro's direct interface recovered headings but supplied no hierarchy levels; its 0/77 complete outputs must not be described as zero heading detection. The Qwen3.6 implementation uses only previously processed audit pages as visual memory; it is not a reproduction of a full-document memory benchmark. The Popo result is an experimental 8-bit MLX port with 8-page chunks, not an upstream performance claim. LightOn 4B historical timing includes five single-page checkpoints followed by batch-two processing; a clean rerun uses batch two throughout. The 0.15 Docling tolerance was fixed across these reports but remains an exploratory choice, not an untuned general default.

**Reference and uncertainty:** pages were deliberately selected to span front matter, body chapters, subsections and annexes. A single assistant annotated them visually. The original 2018 resilience report was excluded after prior document-specific investigation. No per-report title/level correction rules are applied here. The sample is small, covers born-digital reports only, and has no inter-annotator agreement study. Ranking on it cannot establish robustness on arbitrary documents. No missing run is assigned a zero score.

**Reproducibility:** the repo includes the frozen audit labels, page-restricted predictions and original summary/match records. `uv run pdf-headings score --historical` recomputes the bundled historical predictions, including the local configurations selected for this report, without model downloads or credentials. Raw full-page responses remain in the original local experiment archive; they are not bundled in the public repo. Fresh runners save raw responses outside Git. Seven historical Qwen formatting deviations were accepted by a generic JSON array/wrapper/single-fence reader without changing title or level values. Refactored runners retain prompts and settings; model/GPU runs have not all been repeated after packaging. See [method details](https://github.com/dividor/pdf-heading-benchmark/blob/main/docs/reproducibility.md).

**Licenses:** the repository's MIT license covers its code, not third-party packages, model weights or WFP reports. Chandra weights have commercial-use restrictions; applicable licensing costs are additional. See each linked model/package and [third-party notices](https://github.com/dividor/pdf-heading-benchmark/blob/main/THIRD_PARTY_NOTICES.md).

**Supervised Extra Trees:** the frozen classifier was trained on 16 different WFP reports, selected using four validation reports, and first evaluated on four new test reports. It was then applied without refitting to the original four benchmark PDFs and scored with the same 77-heading matching contract as every row above: **59/77 recovered, 35/77 at the correct level, 20 extra headings**. The 7.7-second measurement covers all 523 pages, including extraction and classification but excluding model loading and output writes. Native prose retention was not evaluated. Its separate 82.0% exact-level line F1 on the new test set uses a different corpus and metric and is not the number ranked here. [Comparison runner and evidence](https://github.com/dividor/pdf-heading-benchmark/tree/main/outputs/supervised/comparison) · [Training protocol](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/supervised/report.md).

**Earlier calibration experiment:** body-weight calibration was selected using validation F1. On the historical table its joint F0.5 is 59.2%, versus 58.8% for the original context model; heading precision is only 73.8%, so it fails the new 95% gate. On the inspected 38-heading set, both configurations still have 36 correct heading-level pairs; higher F1 came from fewer extras. Those original results and selection criteria remain frozen.

**New precision optimization:** the threshold-0.70 candidate was selected on validation joint F0.5 subject to the 95% heading-precision gate. It passes on the historical sample with 39/41 genuine headings (95.1%), including 34 correctly leveled, and two extras. Joint F0.5 is 70.5%; joint recall is 44.2%. On the inspected 38-heading set it emits 28 correctly leveled headings, no extras, and misses ten. Reused small validation and regression sets limit the result; a fresh independent evaluation remains necessary. [Settings, all validation scores and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-precision/report.md).


## Results by report

| Runner / configuration | Report | Recovered | Correct heading + level | False headings |
| --- | --- | --- | --- | --- |
| run_docling.py / docling_default | targeting | 13/15 | 3/15 | 0 |
| run_docling.py / docling_default | midterm | 17/18 | 5/18 | 0 |
| run_docling.py / docling_default | indonesia | 17/21 | 4/21 | 0 |
| run_docling.py / docling_default | colombia | 21/23 | 4/23 | 2 |
| run_docling.py / docling_hierarchy | targeting | 13/15 | 0/15 | 0 |
| run_docling.py / docling_hierarchy | midterm | 17/18 | 1/18 | 0 |
| run_docling.py / docling_hierarchy | indonesia | 17/21 | 7/21 | 0 |
| run_docling.py / docling_hierarchy | colombia | 21/23 | 8/23 | 2 |
| run_docling.py / docling_tuned | targeting | 13/15 | 0/15 | 0 |
| run_docling.py / docling_tuned | midterm | 17/18 | 6/18 | 0 |
| run_docling.py / docling_tuned | indonesia | 17/21 | 4/21 | 0 |
| run_docling.py / docling_tuned | colombia | 21/23 | 12/23 | 2 |
| run_pymupdf4llm.py / pymupdf4llm | targeting | 14/15 | 3/15 | 0 |
| run_pymupdf4llm.py / pymupdf4llm | midterm | 18/18 | 0/18 | 0 |
| run_pymupdf4llm.py / pymupdf4llm | indonesia | 18/21 | 16/21 | 2 |
| run_pymupdf4llm.py / pymupdf4llm | colombia | 22/23 | 9/23 | 0 |
| run_marker.py / marker | targeting | 13/15 | 6/15 | 4 |
| run_marker.py / marker | midterm | 18/18 | 6/18 | 2 |
| run_marker.py / marker | indonesia | 17/21 | 4/21 | 0 |
| run_marker.py / marker | colombia | 17/23 | 3/23 | 3 |
| run_mineru.py / mineru_basic | targeting | 13/15 | 8/15 | 0 |
| run_mineru.py / mineru_basic | midterm | 18/18 | 9/18 | 1 |
| run_mineru.py / mineru_basic | indonesia | 17/21 | 7/21 | 1 |
| run_mineru.py / mineru_basic | colombia | 18/23 | 7/23 | 0 |
| run_lighton_mlx.py / lighton_mlx | targeting | 13/15 | 8/15 | 2 |
| run_lighton_mlx.py / lighton_mlx | midterm | 18/18 | 13/18 | 0 |
| run_lighton_mlx.py / lighton_mlx | indonesia | 19/21 | 13/21 | 2 |
| run_lighton_mlx.py / lighton_mlx | colombia | 22/23 | 12/23 | 4 |
| run_popo_mlx.py / popo_docling | targeting | 13/15 | 0/15 | 0 |
| run_popo_mlx.py / popo_docling | midterm | 17/18 | 5/18 | 0 |
| run_popo_mlx.py / popo_docling | indonesia | 17/21 | 5/21 | 0 |
| run_popo_mlx.py / popo_docling | colombia | 21/23 | 5/23 | 2 |
| run_qwen_ids.py / qwen_ids_union | targeting | 0/15 | 0/15 | 0 |
| run_qwen_ids.py / qwen_ids_union | midterm | 14/18 | 6/18 | 0 |
| run_qwen_ids.py / qwen_ids_union | indonesia | 18/21 | 12/21 | 1 |
| run_qwen_ids.py / qwen_ids_union | colombia | 22/23 | 7/23 | 2 |
| run_qwen_ids.py / qwen_ids_mineru_basic | targeting | 13/15 | 2/15 | 0 |
| run_qwen_ids.py / qwen_ids_mineru_basic | midterm | 18/18 | 10/18 | 1 |
| run_qwen_ids.py / qwen_ids_mineru_basic | indonesia | 17/21 | 8/21 | 0 |
| run_qwen_ids.py / qwen_ids_mineru_basic | colombia | 18/23 | 3/23 | 0 |
| run_qwen_ids.py / qwen_ids_pymupdf4llm | targeting | 14/15 | 4/15 | 0 |
| run_qwen_ids.py / qwen_ids_pymupdf4llm | midterm | 0/18 | 0/18 | 0 |
| run_qwen_ids.py / qwen_ids_pymupdf4llm | indonesia | 18/21 | 6/21 | 0 |
| run_qwen_ids.py / qwen_ids_pymupdf4llm | colombia | 22/23 | 12/23 | 0 |
| run_pdf_tags.py / pdf_tags_audit_only | targeting | 9/15 | 9/15 | 0 |
| run_pdf_tags.py / pdf_tags_audit_only | midterm | 13/18 | 13/18 | 0 |
| run_pdf_tags.py / pdf_tags_audit_only | indonesia | 14/21 | 10/21 | 2 |
| run_pdf_tags.py / pdf_tags_audit_only | colombia | 16/23 | 11/23 | 0 |
| run_mineru_pro.py / mineru_pro_mlx | targeting | 13/15 | 0/15 | 0 |
| run_mineru_pro.py / mineru_pro_mlx | midterm | 18/18 | 0/18 | 1 |
| run_mineru_pro.py / mineru_pro_mlx | indonesia | 19/21 | 0/21 | 0 |
| run_mineru_pro.py / mineru_pro_mlx | colombia | 19/23 | 0/23 | 2 |
| run_chandra_batch.py / lighton4b_mlx | targeting | 13/15 | 9/15 | 3 |
| run_chandra_batch.py / lighton4b_mlx | midterm | 18/18 | 13/18 | 0 |
| run_chandra_batch.py / lighton4b_mlx | indonesia | 19/21 | 13/21 | 1 |
| run_chandra_batch.py / lighton4b_mlx | colombia | 22/23 | 11/23 | 4 |
| run_chandra_batch.py / chandra2_mlx | targeting | 13/15 | 8/15 | 0 |
| run_chandra_batch.py / chandra2_mlx | midterm | 18/18 | 15/18 | 0 |
| run_chandra_batch.py / chandra2_mlx | indonesia | 19/21 | 16/21 | 0 |
| run_chandra_batch.py / chandra2_mlx | colombia | 20/23 | 14/23 | 2 |
| run_qwen_visual_memory.py / qwen36_visual_memory | targeting | 15/15 | 12/15 | 0 |
| run_qwen_visual_memory.py / qwen36_visual_memory | midterm | 18/18 | 18/18 | 0 |
| run_qwen_visual_memory.py / qwen36_visual_memory | indonesia | 21/21 | 19/21 | 0 |
| run_qwen_visual_memory.py / qwen36_visual_memory | colombia | 23/23 | 16/23 | 2 |
| compare.py / supervised_extra_trees | targeting | 10/15 | 4/15 | 10 |
| compare.py / supervised_extra_trees | midterm | 16/18 | 13/18 | 2 |
| compare.py / supervised_extra_trees | indonesia | 14/21 | 9/21 | 6 |
| compare.py / supervised_extra_trees | colombia | 19/23 | 9/23 | 2 |
| train.py / structure_expanded_line | targeting | 12/15 | 7/15 | 11 |
| train.py / structure_expanded_line | midterm | 18/18 | 14/18 | 0 |
| train.py / structure_expanded_line | indonesia | 18/21 | 10/21 | 13 |
| train.py / structure_expanded_line | colombia | 21/23 | 10/23 | 2 |
| train.py / structure_learned_groups | targeting | 15/15 | 12/15 | 7 |
| train.py / structure_learned_groups | midterm | 16/18 | 14/18 | 1 |
| train.py / structure_learned_groups | indonesia | 21/21 | 12/21 | 11 |
| train.py / structure_learned_groups | colombia | 22/23 | 13/23 | 2 |
| train.py / structure_context_relations | targeting | 15/15 | 9/15 | 10 |
| train.py / structure_context_relations | midterm | 16/18 | 15/18 | 2 |
| train.py / structure_context_relations | indonesia | 14/21 | 13/21 | 11 |
| train.py / structure_context_relations | colombia | 19/23 | 13/23 | 0 |
| calibrate.py / structure_calibrated | targeting | 15/15 | 9/15 | 9 |
| calibrate.py / structure_calibrated | midterm | 16/18 | 15/18 | 2 |
| calibrate.py / structure_calibrated | indonesia | 12/21 | 11/21 | 10 |
| calibrate.py / structure_calibrated | colombia | 16/23 | 12/23 | 0 |
| optimize_precision.py / structure_precision | targeting | 7/15 | 6/15 | 1 |
| optimize_precision.py / structure_precision | midterm | 12/18 | 12/18 | 0 |
| optimize_precision.py / structure_precision | indonesia | 7/21 | 7/21 | 1 |
| optimize_precision.py / structure_precision | colombia | 13/23 | 9/23 | 0 |

## Technique diagrams and sources

The HTML report opens these diagrams in a modal.


### Qwen3.6-27B / MLX 4-bit / sampled visual memory

Vision + document context · local MLX

Qwen3.6-27B in 4-bit MLX receives a target page image, its native text, a document-wide candidate outline and author tags, plus selected earlier page images. This is our inference context design, with no weight training.


**Inference:** Full-document text context → Current + memory images → Qwen3.6-27B · 4-bit → JSON headings → memory

- **Full-document text context:** PyMuPDF4LLM candidate titles/pages without levels, plus author heading tags.
- **Current + memory images:** Current target ≤1792 px; up to six prior sampled pages ≤1280 px.
- **Qwen3.6-27B · 4-bit:** Native target text + context; thinking off; temperature=0; max_tokens=4096.
- **JSON headings → memory:** Decode target headings; retain latest predicted page at each H1–H6 for later targets.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | mlx-community/Qwen3.6-27B-4bit; revision c000ac2c2057 |
| Page ordering | Audit targets processed in ascending order within each report; memory resets between reports |
| Rendering | PyMuPDF Matrix(2,2), nominal 144 dpi; target thumbnail ≤1792; memory thumbnails ≤1280 pixels |
| Memory | Latest predicted heading page at each of H1–H6; deduplicate pages, sort; at most six earlier sampled images |
| Generation | enable_thinking=False; temperature=0; max_tokens=4096; seed=42 |
| Timeout | Soft 600-second limit, checked between streamed chunks |

**Prompt and memory update**

INSTRUCTION asks for genuine headings on the current page, their complete text and levels H1–H6. It excludes running headers/footers, captions, sidebars and TOC entries, treats document instructions as content, and permits recovery of titles missing from the outline. Tags and previous predictions are described as possibly wrong.

The full-document outline contains candidate titles and pages but omits the parser’s levels. Only earlier sampled pages can become image memory; unseen intervening pages are not silently supplied. Native target-page text is extracted in sorted order.


**Structured output**

The decoder accepts the documented array, headings-wrapper and single-fenced-JSON forms, then validates fields and levels. It does not rewrite semantic heading mistakes. The exact accepted formats are defined in the linked decoder.


**Tuning and measured scope**

Fixed prompt and pretrained 4-bit weights; no benchmark fine-tuning.

Only the 32 audited page images were processed. Scores use their 77 reference headings. Runs used local MLX on an Apple M4 Pro with 48 GB memory. A per-500-page time is an extrapolation, not a 500-page image run.

The table reports target generation time, excluding model loading and context extraction. This configuration has substantial context and generation overhead.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

The model saw sampled page images, not every page image. Generation overhead is substantial; measured results apply to this prompt and memory configuration.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_visual_memory.py) · [Base model / Hugging Face](https://huggingface.co/Qwen/Qwen3.6-27B) · [Tested 4-bit model / HF](https://huggingface.co/mlx-community/Qwen3.6-27B-4bit) · [Full instruction and memory update](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_visual_memory.py) · [Structured reply decoder](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/decode_qwen.py) · [Model revision](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### Embedded PDF heading tags

Author metadata · CPU

This baseline reads author-supplied PDF H1–H6 structure tags and reconstructs their text through marked-content IDs. There is no model.


**Inference:** PDFStructTree → Find H1–H6 elements → Join marked-content IDs → Author text + level

- **PDFStructTree:** Read embedded document structure, not outline bookmarks.
- **Find H1–H6 elements:** Filter structure-tree types with the exact H[1-6] pattern.
- **Join marked-content IDs:** Map all_mcids() to characters on the 32 audited pages.
- **Author text + level:** extract_text recovers the title; tag suffix supplies level; no inferred repair.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Library | pdfplumber.PDFStructTree; exact historical pdfplumber version not recorded |
| Tag filter | ^H[1-6]$ |
| Text mapping | Structure element all_mcids() → page characters → extract_text |
| Page assignment | Minimum page number among the element’s mapped locations |
| Tuning / weights | None: metadata baseline, no trained parameters or prompt |

**Why this differs from visual parsing**

Correct text styling does not guarantee correct PDF structure tags. Missing or incorrect author tags remain missing or incorrect in this result. The method does not fall back to font-size inference.


**Measured scope and timing**

Structure-tree traversal and character recovery target the 32 audited pages. Timing includes PDF opening, traversal and text reconstruction. Hardware: Apple M4 Pro, 48 GB.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

Works only to the extent that the PDF author supplied correct structural tags.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_pdf_tags.py) · [W3C PDF heading technique](https://www.w3.org/WAI/WCAG22/Techniques/pdf/PDF9) · [Structure tree and MCID recovery](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_pdf_tags.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### Chandra OCR 2 / MLX

Page vision model · local MLX

datalab-to/chandra-ocr-2 uses the author’s OCR_LAYOUT_PROMPT and image preparation, with local bf16 MLX batches of four. Generated HTML tags determine heading levels.


**Inference:** Author image preparation → OCR_LAYOUT_PROMPT → Chandra 2 · bf16 · batch 4 → HTML → H1–H6

- **Author image preparation:** At least 192 dpi / 1024-pixel short side, then upstream scale_to_fit.
- **OCR_LAYOUT_PROMPT:** Use the author prompt; verify chat-template compatibility with thinking off.
- **Chandra 2 · bf16 · batch 4:** 16,000,000-pixel batch budget; temperature=0; max_new_tokens=12384.
- **HTML → H1–H6:** Decode h1–h6; preserve Section-Header blocks without tags as level=null.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | datalab-to/chandra-ocr-2; revision af93b47dba1b |
| Author code | datalab-to/chandra revision 9c3a195573be; OCR_LAYOUT_PROMPT and scale_to_fit |
| Runtime | MLX bf16; batch_size=4; MLX_BATCH_PIXEL_BUDGET=16000000 |
| Rendering | dpi=max(192, 1024/min(page width, page height in points) ×72), then author scale_to_fit |
| Prompt | OCR_LAYOUT_PROMPT; empty system prompt; template checked against enable_thinking=False |
| Sampling | temperature=0; top_p=1; top_k=0; max_new_tokens=12384; seed=42 |

**HTML adapter**

BeautifulSoup reads h1–h6 text and levels. A data-label="Section-Header" block without a child heading tag is retained with an unknown level. The runner does not apply document-wide hierarchy correction to those outputs.


**Tuning and measured scope**

Pretrained checkpoint and fixed author prompt; no benchmark fine-tuning. Batching is a local MLX deployment choice, not the model-card GPU setup.

Only the 32 audited page images were processed. Scores use their 77 reference headings. Runs used local MLX on an Apple M4 Pro with 48 GB memory. A per-500-page time is an extrapolation, not a 500-page image run.

Generation time excludes model loading. Batch wall time is divided among its pages, so the reported per-page allocation is not a single-page latency test.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

The measured run uses MLX on the benchmark Mac. Model-card GPU benchmarks use different hardware and datasets.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_chandra_batch.py) · [Model / Hugging Face](https://huggingface.co/datalab-to/chandra-ocr-2) · [Project / GitHub](https://github.com/datalab-to/chandra) · [Rendering, batch parameters and HTML decoder](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_chandra_batch.py) · [Author-code download pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/prepare_model.py) · [Model revision](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### OUR METHOD — confidence-filtered v2 (F0.5-selected)

Our supervised model · CPU

Our F0.5-selected candidate uses the same three frozen Extra Trees models, with a new heading-confidence filter selected on validation. It reaches 95.1% heading precision and 70.5% joint F0.5 on the historical table, with 2 extras and 34/77 correct title-and-level pairs. The lower recall is deliberate and remains visible.


**Training:** Reuse frozen v2 trees → Search 36 validation settings → Gate then maximize F0.5

- **Reuse frozen v2 trees:** 20 training reports; 887 heading groups; no new fitting or label changes.
- **Search 36 validation settings:** Two grouped variants; body weights 1/2/4; heading score thresholds 0/.5/.7/.85; contextual relation weights 1/0.
- **Gate then maximize F0.5:** Require ≥95% heading precision, then select highest joint F0.5. Chosen: context, threshold .70, body 1, relation 1.



**Inference:** Join model · 200 trees → Context model · 200 trees → Relation model · 200 trees → Viterbi → fewer headings

- **Join model · 200 trees:** 100 adjacent-line features → joined groups. Same frozen model as v2.
- **Context model · 200 trees:** 47 features → body/H1–H5 scores. Require heading argmax and largest heading score ≥0.70.
- **Relation model · 200 trees:** 142 pair features on retained groups → shallower/same/deeper probabilities.
- **Viterbi → fewer headings:** Relation weight 1; preserve native text. Historical: 41 emitted, 39 real, 34 correctly leveled.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Estimator | sklearn.ensemble.ExtraTreesClassifier; scikit-learn 1.9.1; Python 3.12.3 |
| Trees per classifier | n_estimators=200 |
| Tree limits | max_depth=16; min_samples_leaf=2 |
| Feature sampling / weighting | max_features=0.8; class_weight="balanced" |
| Reproducibility / parallelism | random_state=42; n_jobs=4 |
| Other estimator options | Library defaults; no tree hyperparameter search was run |
| Join classifier | ExtraTreesClassifier: 100 features; 6,267 pairs; 200 trees; separate/join |
| Context classifier | ExtraTreesClassifier: 47 features; 6,736 groups; 200 trees; body/H1–H5 |
| Relation classifier | ExtraTreesClassifier: 142 features; 867 heading pairs; 200 trees; shallower/same/deeper |
| Total deployed trees | 3 ×200 =600; join + context + relation |
| Decision filter | body_weight=1.0; min_heading_score=0.70; relation_weight=1.0 |
| Selection objective | Maximum validation joint F0.5 among candidates with heading precision ≥0.95; empty output fails |
| Grid | 36 settings: learned_groups/context_relations × body {1,2,4} × score {0,.5,.7,.85}; contextual relation {1,0} |
| Matching | Same physical page; normalized title similarity ≥0.90; exact H level; pooled counts before scoring |

**Training data and teacher provenance**

A single assistant reviewed source text, layout/page snippets and TOC context and supplied explicit line groups and H levels. The annotation provenance does not record a precise teacher-model checkpoint, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate ground truth. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The training split contains 20 WFP reports, 887 heading groups and 7,039 labeled lines. Line classes: body=5,849; H1=238; H2=391; H3=432; H4=128; H5=1; H6=0. Negative examples come from 112 fully reviewed training pages. Unmarked lines on positive-only annotation pages are not automatically negatives. The H5/H6 coverage is a material limitation.

Validation uses reports 103, 538, 176 and 128: 21 reference groups on 20 reviewed pages. The original v2 test uses reports 321, 844, 560 and 394: 38 groups on 32 reviewed pages. Splits are by report, not random lines; report-template families are not held out. Those test pages have now been inspected and are regression evidence for subsequent changes.


**What each model learns**

The 33 native-line features cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.

The context classifier uses 47 features: the 43 group features plus style_numbered_count, style_mean_depth, style_max_depth and toc_exact_title. Style statistics group lines by rounded font size, bold/italic and color, then summarize numeric-prefix depth. TOC matching normalizes title text, strips its numeric prefix and dot leaders, and checks exact membership among dot-leader lines. This is a learned input feature, not a hard TOC level override.

The relationship classifier uses 142 features: two 47-feature groups, their differences and page delta. Its 867 training pairs are consecutive annotated headings. Target −1 means the next H number is smaller (shallower), 0 means equal and +1 means larger (deeper). It learns direction, not the number of levels skipped.


**Filter and validation selection**

The largest heading-class score must be at least 0.70 and a heading must beat the weighted body score. Scores are not calibrated probabilities. Filtering precedes relationship inference and Viterbi, so rejected groups cannot return.

The fixed 36-setting grid was evaluated only on the four validation reports (21 headings). Twenty-three settings met the 95% detection-precision gate. The selected configuration emitted 14 headings, all correctly leveled, and missed seven: joint F0.5 90.9%. Exact ties retain fixed grid order. No eligible candidate would mean no selection.


**Measured result and lost recall**

On the historical 77-heading benchmark, joint F0.5 rises from 58.8% to 70.5%, extras fall from 23 to 2, and heading precision rises to 95.1%. Correct heading-level pairs fall from 50 to 34. Of 41 predictions, 39 are real headings and five of those have incorrect levels; 38 reference titles are missed.

On the previously inspected 38-heading regression set, the candidate emits 28 headings, all correctly leveled, misses ten and scores 93.3% joint F0.5. These are regression results, not independent new test evidence. The 95.1% historical precision is a narrow sample pass.


**Runtime and reproducibility**

Measured full-PDF runtime is 11.66 seconds across all 523 pages on the shared 48 GB Apple M4 Pro. It includes extraction, features and inference; model loading and writes are excluded. The 600 frozen trees and data-only JSON deployment are unchanged.

Selection caches probabilities for speed and reads no test documents. The protocol freezes the grid and source/model/configuration hashes. Regression checks those hashes. Full text and raw outputs remain external; compact audit predictions and all grid scores are committed.

The precision target is met on these samples by abstaining: historical joint recall is 44.2%. Reused small validation and regression sets do not establish production robustness or a guaranteed 95% precision.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/optimize_precision.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Exact estimator constructor and JSON export](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Native line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [Group/context/pair features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py) · [Training components and variant selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/train.py) · [PDF sources and report splits](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json) · [Reviewable heading annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/annotations.json) · [Inference, grouping and Viterbi](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py) · [Precision filter and sequence inference](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/precision_inference.py) · [Joint metric implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/joint_metrics.py) · [All validation results](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-precision/evidence/selection.json) · [Experiment, trade-offs and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-precision/report.md) · [Run on a new PDF](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_precision.py)


### OUR METHOD v2 + calibrated decoding (CPU)

Our supervised model · CPU

This earlier candidate reuses the v2 models with body weight 2, selected using validation F1. Its historical joint F0.5 is 59.2%, but heading precision is only 73.8%, so it fails the new 95% gate.


**Training:** Reuse v2 labels and weights → Evaluate nine decoding settings → Freeze body=2, relation=1

- **Reuse v2 labels and weights:** 887 training groups; same join/context/relation JSON models and hashes.
- **Evaluate nine decoding settings:** Body weights 1 /1.5 /2 × relation weights 1 /0.5 /0; 4 validation reports.
- **Freeze body=2, relation=1:** 81.1% validation group F1; assess inspected regression set and historical table separately.



**Inference:** Frozen join model → Frozen context model → Frozen relation model → Viterbi with weight 1

- **Frozen join model:** Same 200 trees / 100 features; no changes to labels or predicted joining rules.
- **Frozen context model:** Same 200 trees / 47 features; multiply only the body decision score by 2 before argmax.
- **Frozen relation model:** Same 200 trees / 142 features; predict shallower/same/deeper on retained headings.
- **Viterbi with weight 1:** Selected relationship weight stays 1; stricter heading filtering can also remove true headings.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Estimator | sklearn.ensemble.ExtraTreesClassifier; scikit-learn 1.9.1; Python 3.12.3 |
| Trees per classifier | n_estimators=200 |
| Tree limits | max_depth=16; min_samples_leaf=2 |
| Feature sampling / weighting | max_features=0.8; class_weight="balanced" |
| Reproducibility / parallelism | random_state=42; n_jobs=4 |
| Other estimator options | Library defaults; no tree hyperparameter search was run |
| Join classifier | ExtraTreesClassifier: 100 features; 6,267 pairs; 200 trees; separate/join |
| Context classifier | ExtraTreesClassifier: 47 features; 6,736 groups; 200 trees; body/H1–H5 |
| Relation classifier | ExtraTreesClassifier: 142 features; 867 heading pairs; 200 trees; shallower/same/deeper |
| Total deployed trees | 3 ×200 =600; join + context + relation |
| Grid actually searched | body_weight ∈ {1.0, 1.5, 2.0}; relation_weight ∈ {1.0, 0.5, 0.0}; 9 combinations |
| Selected decoding | body_weight=2.0; relation_weight=1.0 |
| Selection metric / ties | Validation exact group-and-level F1; first grid entry wins ties, with baseline settings ordered first |
| Model integrity | Same JSON model hashes as v2; no refitting or label changes |

**Frozen training data and components**

A single assistant reviewed source text, layout/page snippets and TOC context and supplied explicit line groups and H levels. The annotation provenance does not record a precise teacher-model checkpoint, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate ground truth. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The training split contains 20 WFP reports, 887 heading groups and 7,039 labeled lines. Line classes: body=5,849; H1=238; H2=391; H3=432; H4=128; H5=1; H6=0. Negative examples come from 112 fully reviewed training pages. Unmarked lines on positive-only annotation pages are not automatically negatives. The H5/H6 coverage is a material limitation.

Validation uses reports 103, 538, 176 and 128: 21 reference groups on 20 reviewed pages. The original v2 test uses reports 321, 844, 560 and 394: 38 groups on 32 reviewed pages. Splits are by report, not random lines; report-template families are not held out. Those test pages have now been inspected and are regression evidence for subsequent changes.


**Features and sequence decoding**

The 33 native-line features cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.

The context classifier uses 47 features: the 43 group features plus style_numbered_count, style_mean_depth, style_max_depth and toc_exact_title. Style statistics group lines by rounded font size, bold/italic and color, then summarize numeric-prefix depth. TOC matching normalizes title text, strips its numeric prefix and dot leaders, and checks exact membership among dot-leader lines. This is a learned input feature, not a hard TOC level override.

The relationship classifier uses 142 features: two 47-feature groups, their differences and page delta. Its 867 training pairs are consecutive annotated headings. Target −1 means the next H number is smaller (shallower), 0 means equal and +1 means larger (deeper). It learns direction, not the number of levels skipped.

First, body/heading argmax decides which predicted groups survive. Viterbi then maximizes the sum of log heading-class probabilities and weighted log relationship probabilities for transitions between retained groups. Transition class is sign(next H − previous H); probabilities are clipped below at 1e-12. Default relation weight is 1.0. This decoder is an algorithm, not a fourth trained model, and cannot recover a group already rejected as body.


**What calibration changes**

Only the body column of a copy of the group-probability array is multiplied by body_weight before argmax. Surviving headings still use the original probabilities in Viterbi. This is decision weighting, not statistical probability calibration.

On the four validation reports, body weights 1.0, 1.5 and 2.0 yield group-and-level F1 of 69.8%, 76.9% and 81.1%. All three relationship weights tie at each body weight, so the ordered grid retains relation_weight=1.0. There is no evidence from this grid that a relationship-weight change helped.


**Regression outcome and why this is not promoted**

On the previously inspected 38-heading set, F1 rises from 85.7% to 94.7%: 36 groups remain correctly leveled, false groups fall from 8 to 1, and one genuine group is now missed. This is regression evidence, not a new independent test.

On the historical main-table 77 headings, correct title-plus-level matches fall from 50 to 47; matched titles fall from 64 to 59 and false headings from 23 to 21. The candidate therefore remains a separate historical candidate; the current highlighted method is selected using joint F0.5 and the precision gate.


**Deployment and measured scope**

Models are exported as data-only JSON arrays. Exported predict_proba is checked against scikit-learn with atol=1e-7. Runtime inference uses NumPy and float32 tree traversal; it needs no LLM or scikit-learn model server. Full native text is retained. Parent IDs are derived from the predicted level stack, not separately learned or evaluated.

The main comparison parses all four historical PDFs (523 pages) on an Apple M4 Pro with 48 GB memory, but scores only 77 headings on 32 audited pages. Its fuzzy title matching plus exact level is different from the supervised exact group-and-level F1. Main-table scores are historical diagnostics, not the fresh supervised split. Timing covers extraction, feature construction and prediction; model-file loading occurs before the parser timer.

The runner accepts a separate calibration file and verifies frozen model/configuration provenance. No score or inference output is changed by this documentation update.

The models and labels are unchanged. Validation selects a stricter heading decision. Regression on previously inspected pages improves F1 but misses one genuine heading. It is not new independent test evidence.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/calibrate.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Calibration protocol and regression evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-calibration/report.md) · [Exact estimator constructor and JSON export](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Native line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [Group/context/pair features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py) · [Training components and variant selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/train.py) · [Frozen validation scores and fit metadata](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-v2/evidence/selection.json) · [PDF sources and report splits](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json) · [Reviewable heading annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/annotations.json) · [Inference, grouping and Viterbi](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py) · [Frozen grid scores and selected decoding](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-calibration/evidence/selection.json) · [Calibration runner and artifact input](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_structure.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### v2: context + relationships (selected)

Our supervised model · CPU

Our selected v2 pipeline is three scikit-learn ExtraTreesClassifier models (600 trees total) plus a Viterbi decoder. They learn line joining, contextual heading classification and relative level transitions. Tree settings are fixed; validation selects the pipeline architecture.


**Training:** Assistant → explicit labels → Fit fixed Extra Trees → Select pipeline on validation

- **Assistant → explicit labels:** 20 reports: 887 heading groups; reviewed body negatives; train/validation/test reports separated.
- **Fit fixed Extra Trees:** 200 trees per component; depth ≤16; leaf ≥2; balanced classes; seed 42.
- **Select pipeline on validation:** 21 groups / 4 reports; exact group+level F1: line 55.3%, groups 63.6%, context+relations 69.8%.



**Inference:** Join model · 200 trees → Context model · 200 trees → Relation model · 200 trees → Viterbi level sequence

- **Join model · 200 trees:** 100 pair features → binary continuation → line groups, including across PDF blocks.
- **Context model · 200 trees:** 47 features = group style/text + document numbering/TOC context → body/H1–H5 probabilities.
- **Relation model · 200 trees:** 142 features between retained groups → shallower / same / deeper transition probabilities.
- **Viterbi level sequence:** Relation weight=1; maximize class + transition log probabilities; export source text and parents.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Estimator | sklearn.ensemble.ExtraTreesClassifier; scikit-learn 1.9.1; Python 3.12.3 |
| Trees per classifier | n_estimators=200 |
| Tree limits | max_depth=16; min_samples_leaf=2 |
| Feature sampling / weighting | max_features=0.8; class_weight="balanced" |
| Reproducibility / parallelism | random_state=42; n_jobs=4 |
| Other estimator options | Library defaults; no tree hyperparameter search was run |
| Join classifier | ExtraTreesClassifier: 100 features; 6,267 pairs; 200 trees; separate/join |
| Context classifier | ExtraTreesClassifier: 47 features; 6,736 groups; 200 trees; body/H1–H5 |
| Relation classifier | ExtraTreesClassifier: 142 features; 867 heading pairs; 200 trees; shallower/same/deeper |
| Total deployed trees | 3 ×200 =600; join + context + relation |
| Decoding | body_weight=1.0; relation_weight=1.0; Viterbi over retained H1–H5 candidates |
| Artifacts / fitting | 23.2 MiB combined JSON; ≈2.09 s summed classifier fitting, excluding extraction/export/validation |

**Training data and teacher provenance**

A single assistant reviewed source text, layout/page snippets and TOC context and supplied explicit line groups and H levels. The annotation provenance does not record a precise teacher-model checkpoint, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate ground truth. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The training split contains 20 WFP reports, 887 heading groups and 7,039 labeled lines. Line classes: body=5,849; H1=238; H2=391; H3=432; H4=128; H5=1; H6=0. Negative examples come from 112 fully reviewed training pages. Unmarked lines on positive-only annotation pages are not automatically negatives. The H5/H6 coverage is a material limitation.

Validation uses reports 103, 538, 176 and 128: 21 reference groups on 20 reviewed pages. The original v2 test uses reports 321, 844, 560 and 394: 38 groups on 32 reviewed pages. Splits are by report, not random lines; report-template families are not held out. Those test pages have now been inspected and are regression evidence for subsequent changes.


**What each model learns**

The 33 native-line features cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.

The context classifier uses 47 features: the 43 group features plus style_numbered_count, style_mean_depth, style_max_depth and toc_exact_title. Style statistics group lines by rounded font size, bold/italic and color, then summarize numeric-prefix depth. TOC matching normalizes title text, strips its numeric prefix and dot leaders, and checks exact membership among dot-leader lines. This is a learned input feature, not a hard TOC level override.

The relationship classifier uses 142 features: two 47-feature groups, their differences and page delta. Its 867 training pairs are consecutive annotated headings. Target −1 means the next H number is smaller (shallower), 0 means equal and +1 means larger (deeper). It learns direction, not the number of levels skipped.


**Sequence decoding**

First, body/heading argmax decides which predicted groups survive. Viterbi then maximizes the sum of log heading-class probabilities and weighted log relationship probabilities for transitions between retained groups. Transition class is sign(next H − previous H); probabilities are clipped below at 1e-12. Default relation weight is 1.0. This decoder is an algorithm, not a fourth trained model, and cannot recover a group already rejected as body.


**Selection, not a tree-parameter search**

We compared three pipeline variants, with identical fixed tree settings. Validation exact group-and-level F1 was 55.3% for expanded_line, 63.6% for learned_groups and 69.8% for context_relations. The highest validation F1 selected context_relations before the original v2 test. Selection did not use the historical main-table results. F1 = 2 × exact group-and-level matches / (gold groups + predicted groups); group matching requires identical source-line membership.

The original separate 38-heading v2 test achieved 85.7% exact group-and-level F1: 38 matched groups, 36 correctly leveled and 8 additional false groups. That small test is distinct from the historical 77-heading table.


**Deployment and timing**

Models are exported as data-only JSON arrays. Exported predict_proba is checked against scikit-learn with atol=1e-7. Runtime inference uses NumPy and float32 tree traversal; it needs no LLM or scikit-learn model server. Full native text is retained. Parent IDs are derived from the predicted level stack, not separately learned or evaluated.

The main comparison parses all four historical PDFs (523 pages) on an Apple M4 Pro with 48 GB memory, but scores only 77 headings on 32 audited pages. Its fuzzy title matching plus exact level is different from the supervised exact group-and-level F1. Main-table scores are historical diagnostics, not the fresh supervised split. Timing covers extraction, feature construction and prediction; model-file loading occurs before the parser timer.

No LLM is needed at inference. Labels are assistant-assisted, not independently human-verified. Parent links are inferred, not evaluated. v2 main-table scores are historical diagnostics; the separate 38-heading pilot has a different metric.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Exact estimator constructor and JSON export](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Native line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [Group/context/pair features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py) · [Training components and variant selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/train.py) · [Frozen validation scores and fit metadata](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-v2/evidence/selection.json) · [PDF sources and report splits](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json) · [Reviewable heading annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/annotations.json) · [Inference, grouping and Viterbi](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py) · [Configuration source / evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md)


### LightOnOCR-3-0.8B / MLX

Page vision model · local MLX

LightOnOCR-3-0.8B runs one audited page at a time in MLX. Its grounding response supplies title blocks, their boxes and any Markdown heading levels.


**Inference:** Render 32 pages → 0.8B + “grounding” → Decode grounded titles → Join continuations

- **Render 32 pages:** 400 dpi, then thumbnail to a maximum 2048-pixel side.
- **0.8B + “grounding”:** Single image; thinking off; temperature=0; at most 8192 generated tokens.
- **Decode grounded titles:** Read title / title+ blocks and normalized boxes from model text.
- **Join continuations:** title+ extends a preceding title; # count gives H level, otherwise null.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | lightonai/LightOnOCR-3-0.8B; revision 36d863692532 (pin in runner) |
| Runtime | MLX native checkpoint; no quantization conversion in the runner; one page per call |
| Image | 400 dpi → longest side ≤2048 pixels |
| Prompt | Literal “grounding”; num_images=1; enable_thinking=False |
| Generation | temperature=0; max_tokens=8192; MLX seed=42 |
| Timeout | Soft 300-second limit, checked between streamed chunks; not a hard interrupt |

**Grounding decoder**

Grounded title blocks include bounding boxes on a 0–1000 coordinate scale, normalized by the adapter. A title+ block is appended only when the preceding block is title/title+. Markdown # through ###### supplies level; an unmarked title retains level=null. Raw text, token counts and limit/timeout status are saved.


**Tuning and measured scope**

Pretrained weights and a fixed grounding prompt; no benchmark fine-tuning. The linked 2026 LightOnOCR paper is earlier research, not a claim that this benchmark replicates a LightOnOCR-3 paper.

Only the 32 audited page images were processed. Scores use their 77 reference headings. Runs used local MLX on an Apple M4 Pro with 48 GB memory. A per-500-page time is an extrapolation, not a 500-page image run.

The reported time sums page generation; model loading is excluded. Cached completed pages support resumption.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

Page-local recognition has less document-wide hierarchy context. These are local MLX measurements, not vendor throughput claims.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_lighton_mlx.py) · [Model / Hugging Face](https://huggingface.co/lightonai/LightOnOCR-3-0.8B) · [Project / GitHub](https://github.com/lightonai/LightOnOCR) · [Earlier LightOnOCR research paper](https://arxiv.org/abs/2601.14251) · [Grounding prompt, image sizing and decoder](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_lighton_mlx.py) · [MLX package pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/mlx.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### LightOnOCR-3-4B / MLX grounding

Page vision model · local MLX

LightOnOCR-3-4B uses the same grounding-output idea as the 0.8B model, but runs bf16 MLX batches of two with a larger generation allowance. The published run also retains five earlier single-page checkpoints.


**Inference:** 2048-pixel page images → 4B bf16 · batch 2 → Historical checkpoint merge → Grounded heading decode

- **2048-pixel page images:** Render at 400 dpi, then shrink; each page remains an independent input.
- **4B bf16 · batch 2:** “grounding”; temperature=0; 12,384-token ceiling in the batch runner.
- **Historical checkpoint merge:** Five earlier single-page outputs used a 12,288-token ceiling.
- **Grounded heading decode:** Join title+ continuations; retain # levels and page/box provenance.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | lightonai/LightOnOCR-3-4B; revision b71010f095dc |
| Runtime | MLX bf16; MlxVlmClient; batch_size=2; no quantization conversion |
| Image | 400 dpi → longest side ≤2048 pixels |
| Prompt | Literal “grounding”; empty system prompt; wrapper checked against template with enable_thinking=False |
| Sampling | temperature=0; top_p=1; top_k=0; max_new_tokens=12384; seed=42 |
| Historical exception | Five cached single-page outputs use max_tokens=12288; fresh packaged runs batch all 32 pages |

**Output and provenance**

The grounded title/title+ decoder is shared with the 0.8B path. It retains unknown levels rather than inferring them. The table’s measured result combines the five earlier checkpoints with the subsequent batch outputs; it is not a claim that all 32 historical pages used an identical batching configuration.


**Tuning and measured scope**

No benchmark fine-tuning or parameter search. Batch size and token limits are fixed runtime choices.

Only the 32 audited page images were processed. Scores use their 77 reference headings. Runs used local MLX on an Apple M4 Pro with 48 GB memory. A per-500-page time is an extrapolation, not a 500-page image run.

Timing sums recorded generation, excludes model loading, and allocates a batch’s wall time equally across its pages. Allocated per-page times are not individual-page latency measurements.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

Page-local recognition has less document-wide hierarchy context. These are local MLX measurements, not vendor throughput claims.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_chandra_batch.py) · [Model / Hugging Face](https://huggingface.co/lightonai/LightOnOCR-3-4B) · [Project / GitHub](https://github.com/lightonai/LightOnOCR) · [Earlier LightOnOCR research paper](https://arxiv.org/abs/2601.14251) · [Batch settings and prompt verification](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_chandra_batch.py) · [Grounded title decoder](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_lighton_mlx.py) · [Checkpoint revisions](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### v2: learned grouping

Our supervised model · CPU

This v2 ablation uses two ExtraTreesClassifier models: a binary line-join model and a group-level body/heading classifier, 400 trees total. It tests learned heading spans before adding document context and level relationships.


**Training:** Assistant → explicit labels → Fit fixed Extra Trees → Select pipeline on validation

- **Assistant → explicit labels:** 20 reports: 887 heading groups; reviewed body negatives; train/validation/test reports separated.
- **Fit fixed Extra Trees:** 200 trees per component; depth ≤16; leaf ≥2; balanced classes; seed 42.
- **Select pipeline on validation:** 21 groups / 4 reports; exact group+level F1: line 55.3%, groups 63.6%, context+relations 69.8%.



**Inference:** Adjacent line pairs → join → Connected heading spans → 43-feature group classifier → Independent group levels

- **Adjacent line pairs → join:** 100 features = line A + line B + differences + page delta; binary Extra Trees.
- **Connected heading spans:** Join predicted continuations across PDF block boundaries; retain separate source line IDs.
- **43-feature group classifier:** 200 more trees predict body or H1–H5 from merged text and style summaries.
- **Independent group levels:** Argmax per group; no TOC/style-context features or relation/Viterbi stage.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Estimator | sklearn.ensemble.ExtraTreesClassifier; scikit-learn 1.9.1; Python 3.12.3 |
| Trees per classifier | n_estimators=200 |
| Tree limits | max_depth=16; min_samples_leaf=2 |
| Feature sampling / weighting | max_features=0.8; class_weight="balanced" |
| Reproducibility / parallelism | random_state=42; n_jobs=4 |
| Other estimator options | Library defaults; no tree hyperparameter search was run |
| Join classifier | 100 features; 6,267 labeled adjacent-line pairs; classes 0=separate, 1=join |
| Group classifier | 43 features; 6,736 examples; classes body/H1–H5 |
| Total deployed trees | 2 ×200 =400 |
| Artifact sizes / fit | join.json 1,958,200 bytes / ≈0.816 s; group.json 17,519,049 bytes / ≈0.995 s |

**Training set and annotation source**

A single assistant reviewed source text, layout/page snippets and TOC context and supplied explicit line groups and H levels. The annotation provenance does not record a precise teacher-model checkpoint, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate ground truth. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The training split contains 20 WFP reports, 887 heading groups and 7,039 labeled lines. Line classes: body=5,849; H1=238; H2=391; H3=432; H4=128; H5=1; H6=0. Negative examples come from 112 fully reviewed training pages. Unmarked lines on positive-only annotation pages are not automatically negatives. The H5/H6 coverage is a material limitation.

Validation uses reports 103, 538, 176 and 128: 21 reference groups on 20 reviewed pages. The original v2 test uses reports 321, 844, 560 and 394: 38 groups on 32 reviewed pages. Splits are by report, not random lines; report-template families are not held out. Those test pages have now been inspected and are regression evidence for subsequent changes.


**Join and group targets**

The 33 native-line features cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.

An adjacent pair is positive only if both lines belong to the same explicit annotated heading. Only pairs with known labels on both lines are trained. Pair features concatenate A, B, B−A and page difference: 3×33+1=100.

The group classifier trains on 887 annotated heading groups plus 5,849 reviewed singleton body lines. Its 43 features start from the 33 line features, recompute text indicators on the joined title, use the last line’s following gap, and add group length/page span plus mean/max size, bold, italic and width. Inference uses predicted groups, so join errors can propagate into classification.


**Selection and deployment**

We compared three pipeline variants, with identical fixed tree settings. Validation exact group-and-level F1 was 55.3% for expanded_line, 63.6% for learned_groups and 69.8% for context_relations. The highest validation F1 selected context_relations before the original v2 test. Selection did not use the historical main-table results. F1 = 2 × exact group-and-level matches / (gold groups + predicted groups); group matching requires identical source-line membership.

Models are exported as data-only JSON arrays. Exported predict_proba is checked against scikit-learn with atol=1e-7. Runtime inference uses NumPy and float32 tree traversal; it needs no LLM or scikit-learn model server. Full native text is retained. Parent IDs are derived from the predicted level stack, not separately learned or evaluated.

The main comparison parses all four historical PDFs (523 pages) on an Apple M4 Pro with 48 GB memory, but scores only 77 headings on 32 audited pages. Its fuzzy title matching plus exact level is different from the supervised exact group-and-level F1. Main-table scores are historical diagnostics, not the fresh supervised split. Timing covers extraction, feature construction and prediction; model-file loading occurs before the parser timer.

No LLM is needed at inference. Labels are assistant-assisted, not independently human-verified. Parent links are inferred, not evaluated. v2 main-table scores are historical diagnostics; the separate 38-heading pilot has a different metric.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Exact estimator constructor and JSON export](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Native line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [Group/context/pair features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py) · [Training components and variant selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/train.py) · [Frozen validation scores and fit metadata](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-v2/evidence/selection.json) · [PDF sources and report splits](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json) · [Reviewable heading annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/annotations.json) · [Inference, grouping and Viterbi](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py) · [Configuration source / evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md)


### v2: more annotations

Our supervised model · CPU

The v2 line-only ablation keeps the original one-classifier architecture but expands training to 887 heading groups across 20 reports. It isolates the effect of more labels before introducing learned grouping.


**Training:** Assistant → explicit labels → Fit fixed Extra Trees → Select pipeline on validation

- **Assistant → explicit labels:** 20 reports: 887 heading groups; reviewed body negatives; train/validation/test reports separated.
- **Fit fixed Extra Trees:** 200 trees per component; depth ≤16; leaf ≥2; balanced classes; seed 42.
- **Select pipeline on validation:** 21 groups / 4 reports; exact group+level F1: line 55.3%, groups 63.6%, context+relations 69.8%.



**Inference:** Expanded labels → line model → Full PDF → line probabilities → Original block grouping → Line-only result

- **Expanded labels → line model:** Fit 200 trees on 7,039 labeled lines with 33 features.
- **Full PDF → line probabilities:** Each line gets body/H1–H5 scores; choose argmax.
- **Original block grouping:** Join adjacent equal-level heading lines in the same PDF block; no join classifier.
- **Line-only result:** No TOC context model or relationship decoder; validation group F1 55.3%.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Estimator | sklearn.ensemble.ExtraTreesClassifier; scikit-learn 1.9.1; Python 3.12.3 |
| Trees per classifier | n_estimators=200 |
| Tree limits | max_depth=16; min_samples_leaf=2 |
| Feature sampling / weighting | max_features=0.8; class_weight="balanced" |
| Reproducibility / parallelism | random_state=42; n_jobs=4 |
| Other estimator options | Library defaults; no tree hyperparameter search was run |
| Deployed components | line: 33 features, 7,039 examples, 200 trees |
| Observed target classes | 0=body, 1–5=heading level; no H6 training examples |
| Artifact / fit | line.json: 22,737,104 bytes; fit ≈1.007 s; excludes extraction/export/validation |

**Training set and annotation source**

A single assistant reviewed source text, layout/page snippets and TOC context and supplied explicit line groups and H levels. The annotation provenance does not record a precise teacher-model checkpoint, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate ground truth. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The training split contains 20 WFP reports, 887 heading groups and 7,039 labeled lines. Line classes: body=5,849; H1=238; H2=391; H3=432; H4=128; H5=1; H6=0. Negative examples come from 112 fully reviewed training pages. Unmarked lines on positive-only annotation pages are not automatically negatives. The H5/H6 coverage is a material limitation.

Validation uses reports 103, 538, 176 and 128: 21 reference groups on 20 reviewed pages. The original v2 test uses reports 321, 844, 560 and 394: 38 groups on 32 reviewed pages. Splits are by report, not random lines; report-template families are not held out. Those test pages have now been inspected and are regression evidence for subsequent changes.


**Features and grouping**

The 33 native-line features cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.

Line classification uses the largest class probability. The original grouping combines adjacent heading lines only when their PDF block and predicted level agree. There is no learned line-joining model, group classifier or Viterbi stage in this ablation.


**Selection and deployment**

We compared three pipeline variants, with identical fixed tree settings. Validation exact group-and-level F1 was 55.3% for expanded_line, 63.6% for learned_groups and 69.8% for context_relations. The highest validation F1 selected context_relations before the original v2 test. Selection did not use the historical main-table results. F1 = 2 × exact group-and-level matches / (gold groups + predicted groups); group matching requires identical source-line membership.

Models are exported as data-only JSON arrays. Exported predict_proba is checked against scikit-learn with atol=1e-7. Runtime inference uses NumPy and float32 tree traversal; it needs no LLM or scikit-learn model server. Full native text is retained. Parent IDs are derived from the predicted level stack, not separately learned or evaluated.

The main comparison parses all four historical PDFs (523 pages) on an Apple M4 Pro with 48 GB memory, but scores only 77 headings on 32 audited pages. Its fuzzy title matching plus exact level is different from the supervised exact group-and-level F1. Main-table scores are historical diagnostics, not the fresh supervised split. Timing covers extraction, feature construction and prediction; model-file loading occurs before the parser timer.

No LLM is needed at inference. Labels are assistant-assisted, not independently human-verified. Parent links are inferred, not evaluated. v2 main-table scores are historical diagnostics; the separate 38-heading pilot has a different metric.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Exact estimator constructor and JSON export](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Native line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [Group/context/pair features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py) · [Training components and variant selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/train.py) · [Frozen validation scores and fit metadata](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-v2/evidence/selection.json) · [PDF sources and report splits](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json) · [Reviewable heading annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/annotations.json) · [Inference, grouping and Viterbi](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py) · [Configuration source / evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md)


### Supervised Extra Trees / CPU / assistant labels

Our supervised model · CPU

Our first supervised baseline is one 200-tree ExtraTreesClassifier over native PDF lines. It was selected against scaled logistic regression on separate validation reports; no LLM runs during inference.


**Training:** Assistant annotations → Fit two estimator families → Select Extra Trees

- **Assistant annotations:** 154 heading groups on 16 training reports; report-level validation/test splits.
- **Fit two estimator families:** StandardScaler + LogisticRegression(C=1), versus 200-tree Extra Trees; fixed settings.
- **Select Extra Trees:** Validation exact-level line F1 69.1% versus 47.6%; freeze the winning model.



**Inference:** PyMuPDF → 33 features → One ExtraTreesClassifier → Same-block grouping → Native text + headings

- **PyMuPDF → 33 features:** Extract every native line; fonts, geometry, spacing and generic text indicators.
- **One ExtraTreesClassifier:** 200 trees; depth ≤16; minimum leaf 2; body or H level per line.
- **Same-block grouping:** Merge adjacent same-level heading lines only within a PDF block.
- **Native text + headings:** Keep source lines; export heading groups, levels and inferred parents.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Estimator | sklearn.ensemble.ExtraTreesClassifier; scikit-learn 1.9.1; Python 3.12.3 |
| Trees per classifier | n_estimators=200 |
| Tree limits | max_depth=16; min_samples_leaf=2 |
| Feature sampling / weighting | max_features=0.8; class_weight="balanced" |
| Reproducibility / parallelism | random_state=42; n_jobs=4 |
| Other estimator options | Library defaults; no tree hyperparameter search was run |
| Training set | 154 heading groups / 16 WFP reports |
| Alternative estimator | StandardScaler + LogisticRegression(C=1, class_weight="balanced", max_iter=3000, random_state=42) |
| Selected artifact | 200-tree JSON model, 9.97 MiB; recorded fit time ≈0.455 s, excluding preparation |

**Labels and features**

A single assistant reviewed source text, layout/page snippets and TOC context and supplied explicit line groups and H levels. The annotation provenance does not record a precise teacher-model checkpoint, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate ground truth. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The 33 native-line features cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.


**What was actually tuned**

Two estimator families were compared using validation exact-level LINE F1: logistic regression 47.6%, Extra Trees 69.1%. Tree parameters and logistic C were fixed, not searched. Validation contains 21 heading groups across four reports; the separate v1 test contains 27 groups across four reports.

The v1 test scored 82.0% exact-level line F1 and 22/27 complete heading groups at the right level. This differs from the v2 group-F1 metric. The v1 training set was expanded with additional reviewed training pages before the reported selection/test; it is smaller than the later 887-group v2 set.


**Export and measured scope**

Models are exported as data-only JSON arrays. Exported predict_proba is checked against scikit-learn with atol=1e-7. Runtime inference uses NumPy and float32 tree traversal; it needs no LLM or scikit-learn model server. Full native text is retained. Parent IDs are derived from the predicted level stack, not separately learned or evaluated.

The main comparison parses all four historical PDFs (523 pages) on an Apple M4 Pro with 48 GB memory, but scores only 77 headings on 32 audited pages. Its fuzzy title matching plus exact level is different from the supervised exact group-and-level F1. Main-table scores are historical diagnostics, not the fresh supervised split. Timing covers extraction, feature construction and prediction; model-file loading occurs before the parser timer.

Assistant-produced labels lack independent adjudication. V1 selection uses line F1, not v2 group F1. Same-block grouping can split multi-block headings; parent edges are inferred and unscored.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/supervised/compare.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Estimator definitions](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [V1 training and selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/supervised/train.py) · [V1 validation evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/supervised/evidence/selection.json) · [V1 corpus and source URLs](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/supervised/corpus.json) · [Grouping and parent inference](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_inference.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py) · [Configuration source / evidence](https://github.com/dividor/pdf-heading-benchmark/blob/main/src/pdf_heading_benchmark/supervised_models.py)


### MinerU 4.2.3 basic CPU

Layout parser · CPU

MinerU 4.2.3 uses its basic ONNX CPU parser. This is the native title-block pipeline, separate from the MinerU Pro vision model.


**Inference:** ONNX on CPU → MinerUParser basic tier → Native title blocks → Export parser levels

- **ONNX on CPU:** small_backend="onnx"; onnx_device="cpu".
- **MinerUParser basic tier:** parse_mode="auto"; page_range="all"; image_analysis=False.
- **Native title blocks:** Read ParagraphTitleBlock and DocTitleBlock content, level and box.
- **Export parser levels:** Use inline_plain_text and b.level directly; no secondary hierarchy model.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Package | mineru==4.2.3 |
| Backend | small_backend="onnx"; onnx_device="cpu" |
| Parser | tier="basic"; parse_mode="auto"; image_analysis=False; page_range="all" |
| External assistance | Empty VLM server URL; runner rejects enabled LLM title leveling or cross-page table-cell merging |
| Tuning | No benchmark training; individual parser model revisions are not explicitly pinned by this runner |

**Native extraction**

Heading text, level, box and page are taken from the parser’s title objects. The runner does not add a title hierarchy prompt or rewrite missing levels.


**Measured scope and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

The parse call is timed; parser construction happens before that timer.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

This CPU tier is different from the MinerU Pro vision model below.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_mineru.py) · [Project / GitHub](https://github.com/opendatalab/MinerU) · [ONNX configuration and block extraction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_mineru.py) · [Pinned environment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/mineru.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### Qwen3.5-4B / union candidates

Text-only LLM refinement · local MLX

Qwen3.5-4B in local 4-bit MLX refines Docling + PyMuPDF4LLM candidates. It receives the entire document’s candidate list as text, with no page images and no upstream levels.


**Inference:** Docling + PyMuPDF4LLM candidates → IDs, page and title only → Qwen3.5-4B · 4-bit → Strict ID → level JSON

- **Docling + PyMuPDF4LLM candidates:** Union both full-document candidate streams; same-page fuzzy deduplication ≥0.90.
- **IDs, page and title only:** Assign h0000-style IDs; omit source H levels; send one list per document.
- **Qwen3.5-4B · 4-bit:** temperature=0; max_tokens=4096; seed=42; thinking disabled.
- **Strict ID → level JSON:** Every ID must map to an integer 1–20 or null; rejected output is not repaired.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | mlx-community/Qwen3.5-4B-MLX-4bit; revision 32f3e8ecf654 (full pin in configs/models.json) |
| Input | One full-document text candidate list; num_images=0; enable_thinking=False |
| Generation | temperature=0; max_tokens=4096; prefill_step_size=256; MLX seed=42 |
| Candidate source | Docling + PyMuPDF4LLM |
| Output contract | Exact input-ID key set; integer level 1–20 or null; invalid response produces null levels for that document |
| Tuning | Fixed prompt and pretrained quantized weights; no fine-tuning or recorded prompt search |

**Candidate construction**

The union uses same-page greedy one-to-one matching at normalized title similarity ≥0.90. It strips HTML, normalizes Unicode and alphanumeric text, and uses SequenceMatcher with autojunk=False. Matched source candidates are deduplicated; unmatched candidates are merged while preserving relative order. This operates on parser outputs, not gold labels.


**Prompt and decoding**

The frozen PROMPT asks for logical hierarchy, treats executive summaries/main sections/annexes as top level, rejects captions, table cells, running headers, emphasis and TOC entries, and requires consistent parallel sections. Cover text must not shift body levels; absolute page number must not determine level. The complete prompt is linked in the runner.

The decoder strips a code-fence wrapper, then validates every ID and value. Accepted IDs are joined back to their original titles and pages; null rejects a candidate. A missing source title cannot be created by this method. Invalid responses are recorded as errors and yield no accepted headings for that document.


**Measured scope and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

Reported time covers the hierarchy-generation stage only. Candidate extraction and model loading/download are excluded; end-to-end deployment must also pay for the source parser.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

A missing candidate cannot be recovered by this refinement. JSON is validated; invalid replies are not silently repaired.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) · [Base model / Hugging Face](https://huggingface.co/Qwen/Qwen3.5-4B) · [Tested 4-bit model / HF](https://huggingface.co/mlx-community/Qwen3.5-4B-MLX-4bit) · [Exact PROMPT, sampling and validation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_ids.py) · [Model revision pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Candidate union and order preservation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/build_union.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### Qwen3.5-4B / PyMuPDF candidates

Text-only LLM refinement · local MLX

Qwen3.5-4B in local 4-bit MLX refines PyMuPDF4LLM candidates. It receives the entire document’s candidate list as text, with no page images and no upstream levels.


**Inference:** PyMuPDF4LLM candidates → IDs, page and title only → Qwen3.5-4B · 4-bit → Strict ID → level JSON

- **PyMuPDF4LLM candidates:** Use the full PDF’s Markdown heading candidates and page provenance.
- **IDs, page and title only:** Assign h0000-style IDs; omit source H levels; send one list per document.
- **Qwen3.5-4B · 4-bit:** temperature=0; max_tokens=4096; seed=42; thinking disabled.
- **Strict ID → level JSON:** Every ID must map to an integer 1–20 or null; rejected output is not repaired.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | mlx-community/Qwen3.5-4B-MLX-4bit; revision 32f3e8ecf654 (full pin in configs/models.json) |
| Input | One full-document text candidate list; num_images=0; enable_thinking=False |
| Generation | temperature=0; max_tokens=4096; prefill_step_size=256; MLX seed=42 |
| Candidate source | PyMuPDF4LLM |
| Output contract | Exact input-ID key set; integer level 1–20 or null; invalid response produces null levels for that document |
| Tuning | Fixed prompt and pretrained quantized weights; no fine-tuning or recorded prompt search |

**Candidate construction**

Only PyMuPDF4LLM supplies candidates. This variant changes the candidate source, while keeping the Qwen model, prompt and generation settings the same as the other ID-refinement rows.


**Prompt and decoding**

The frozen PROMPT asks for logical hierarchy, treats executive summaries/main sections/annexes as top level, rejects captions, table cells, running headers, emphasis and TOC entries, and requires consistent parallel sections. Cover text must not shift body levels; absolute page number must not determine level. The complete prompt is linked in the runner.

The decoder strips a code-fence wrapper, then validates every ID and value. Accepted IDs are joined back to their original titles and pages; null rejects a candidate. A missing source title cannot be created by this method. Invalid responses are recorded as errors and yield no accepted headings for that document.


**Measured scope and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

Reported time covers the hierarchy-generation stage only. Candidate extraction and model loading/download are excluded; end-to-end deployment must also pay for the source parser.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

A missing candidate cannot be recovered by this refinement. JSON is validated; invalid replies are not silently repaired.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) · [Base model / Hugging Face](https://huggingface.co/Qwen/Qwen3.5-4B) · [Tested 4-bit model / HF](https://huggingface.co/mlx-community/Qwen3.5-4B-MLX-4bit) · [Exact PROMPT, sampling and validation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_ids.py) · [Model revision pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Candidate parser](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_pymupdf4llm.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### PyMuPDF4LLM 2.1

Native PDF parser · CPU

PyMuPDF4LLM 2.1 converts native PDF text and layout to page-chunk Markdown. We score the heading markers it emits; no generative model is used.


**Inference:** Native PDF text + fonts → to_markdown → Parse # through ###### → Page-tagged headings

- **Native PDF text + fonts:** Use PyMuPDF4LLM 2.1 on the entire PDF.
- **to_markdown:** page_chunks=True; use_ocr=False; no custom font-size threshold.
- **Parse # through ######:** Only Markdown heading lines become headings; count the leading # characters.
- **Page-tagged headings:** Take page_number from each chunk; preserve the extracted title.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Package | pymupdf4llm==2.1 |
| Call | to_markdown(pdf, page_chunks=True, use_ocr=False) |
| Heading parser | Start-of-line #{1,6}, followed by whitespace and nonempty text |
| Tuning / prompt | No benchmark fitting, prompt or manual font-threshold override; other options use package defaults |

**Extraction and decoding**

Markdown determines both heading membership and H level. The adapter does not repair typography-driven mistakes or infer hierarchy from section numbers. Full text is retained in page chunks and Markdown.


**Measured scope and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

Timing covers the conversion call; JSON/Markdown heading decoding is a separate adapter step.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

Typography-driven Markdown can confuse display text with section headings.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_pymupdf4llm.py) · [Project / GitHub](https://github.com/pymupdf/pymupdf4llm) · [Documentation](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/) · [Markdown conversion and heading regex](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_pymupdf4llm.py) · [Pinned environment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/pymupdf.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### Qwen3.5-4B / MinerU candidates

Text-only LLM refinement · local MLX

Qwen3.5-4B in local 4-bit MLX refines MinerU basic candidates. It receives the entire document’s candidate list as text, with no page images and no upstream levels.


**Inference:** MinerU basic candidates → IDs, page and title only → Qwen3.5-4B · 4-bit → Strict ID → level JSON

- **MinerU basic candidates:** Use native ONNX ParagraphTitleBlock / DocTitleBlock candidates from the full PDF.
- **IDs, page and title only:** Assign h0000-style IDs; omit source H levels; send one list per document.
- **Qwen3.5-4B · 4-bit:** temperature=0; max_tokens=4096; seed=42; thinking disabled.
- **Strict ID → level JSON:** Every ID must map to an integer 1–20 or null; rejected output is not repaired.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | mlx-community/Qwen3.5-4B-MLX-4bit; revision 32f3e8ecf654 (full pin in configs/models.json) |
| Input | One full-document text candidate list; num_images=0; enable_thinking=False |
| Generation | temperature=0; max_tokens=4096; prefill_step_size=256; MLX seed=42 |
| Candidate source | MinerU basic |
| Output contract | Exact input-ID key set; integer level 1–20 or null; invalid response produces null levels for that document |
| Tuning | Fixed prompt and pretrained quantized weights; no fine-tuning or recorded prompt search |

**Candidate construction**

Only MinerU basic supplies candidates. This variant changes the candidate source, while keeping the Qwen model, prompt and generation settings the same as the other ID-refinement rows.


**Prompt and decoding**

The frozen PROMPT asks for logical hierarchy, treats executive summaries/main sections/annexes as top level, rejects captions, table cells, running headers, emphasis and TOC entries, and requires consistent parallel sections. Cover text must not shift body levels; absolute page number must not determine level. The complete prompt is linked in the runner.

The decoder strips a code-fence wrapper, then validates every ID and value. Accepted IDs are joined back to their original titles and pages; null rejects a candidate. A missing source title cannot be created by this method. Invalid responses are recorded as errors and yield no accepted headings for that document.


**Measured scope and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

Reported time covers the hierarchy-generation stage only. Candidate extraction and model loading/download are excluded; end-to-end deployment must also pay for the source parser.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

A missing candidate cannot be recovered by this refinement. JSON is validated; invalid replies are not silently repaired.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) · [Base model / Hugging Face](https://huggingface.co/Qwen/Qwen3.5-4B) · [Tested 4-bit model / HF](https://huggingface.co/mlx-community/Qwen3.5-4B-MLX-4bit) · [Exact PROMPT, sampling and validation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_ids.py) · [Model revision pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Candidate parser](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_mineru.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### Docling fixed tolerance 0.15

Layout parser · CPU

The exploratory Docling variant changes one hierarchy setting: style_size_tolerance=0.15. It starts from the same flat document as the other variants, not from the already-refined output.


**Inference:** Native PDF → layout → Retain parsed pages → Style tolerance = 0.15 → Export section headers

- **Native PDF → layout:** Docling 2.151.1; CPU, 8 threads; OCR and table structure disabled.
- **Retain parsed pages:** generate_parsed_pages=True preserves geometry required by the later hierarchy stage.
- **Style tolerance = 0.15:** Reset to a copy of the original blocks, then enable hierarchy with the fixed tolerance.
- **Export section headers:** Keep text, native level, first provenance page, box and item reference.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Package | docling==2.151.1 |
| Device / parallelism | CPU; num_threads=8 |
| Conversion | do_ocr=False; do_table_structure=False; generate_parsed_pages=True |
| Hierarchy | enabled=True; style_size_tolerance=0.15; other settings use library defaults |
| Model provenance | Package-managed layout models; the runner does not explicitly pin individual layout-model revisions. |

**What changed and how it was selected**

The exploratory Docling variant changes one hierarchy setting: style_size_tolerance=0.15. It starts from the same flat document as the other variants, not from the already-refined output.

These are fixed configurations, not a learned WFP-specific correction or a recorded hyperparameter search. The tolerance variant is exploratory; “tuned” in its historical row name should not be read as a validated optimum.


**Output and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

The variants share one base conversion. Its recorded time includes first model load/download. The ordinary hierarchy pass has a separate timer; the tolerance pass was not separately timed. Their table times therefore do not represent three independent end-to-end conversions.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

These variants share detected blocks. A hierarchy stage cannot recover a heading absent from its inputs. The tolerance variant is exploratory.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) · [Project / GitHub](https://github.com/docling-project/docling) · [Docling technical report (2024)](https://arxiv.org/abs/2408.09869) · [Conversion and both hierarchy passes](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_docling.py) · [Pinned environment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/docling.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### Marker 2.2 no OCR/LLM

Layout parser · CPU

Marker 2.2 runs its local CPU document pipeline with both OCR and LLM assistance disabled. The scored hierarchy comes from HTML heading tags inside SectionHeader blocks.


**Inference:** Load Marker models → Full-PDF JSON conversion → Walk SectionHeader blocks → Retain missing levels

- **Load Marker models:** create_model_dict(device="cpu", no_server=True).
- **Full-PDF JSON conversion:** JSONRenderer; no_ocr mode; use_llm=False.
- **Walk SectionHeader blocks:** Recurse through the JSON and read h1–h6 from each block’s HTML.
- **Retain missing levels:** Keep a detected title with level=null if it has no HTML heading tag.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Package | marker-pdf==2.2 |
| Models | create_model_dict(device="cpu", no_server=True); internal checkpoints not explicitly pinned by this runner |
| Renderer | marker.renderers.json.JSONRenderer |
| Configuration | mode="no_ocr"; disable_ocr=True; use_llm=False; disable_image_extraction=True; disable_tqdm=True |
| Tuning | No benchmark fine-tuning or prompt; remaining options use package defaults |

**Output adapter**

The adapter enumerates output pages from 1, visits nested SectionHeader blocks and uses BeautifulSoup to identify h1–h6 tags. A title without such a tag remains a heading candidate with an unknown level.


**Measured scope and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

The timer starts before create_model_dict, so model loading/download and shutdown are included. This timing boundary differs from the vision-model generation-only measurements.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

This benchmark is the local no-OCR/no-LLM configuration, not Marker with generative assistance.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_marker.py) · [Project / GitHub](https://github.com/datalab-to/marker) · [Model construction and JSON decoding](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_marker.py) · [Pinned environment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/marker.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### Docling 2.151.1 default

Layout parser · CPU

Docling 2.151.1 detects section-header blocks; this row scores their native levels without our applying a separate hierarchy stage.


**Inference:** Native PDF → layout → Retain parsed pages → Native SectionHeaderItem.level → Export section headers

- **Native PDF → layout:** Docling 2.151.1; CPU, 8 threads; OCR and table structure disabled.
- **Retain parsed pages:** generate_parsed_pages=True preserves geometry required by the later hierarchy stage.
- **Native SectionHeaderItem.level:** Read the conversion output directly; no explicit post-conversion hierarchy pass.
- **Export section headers:** Keep text, native level, first provenance page, box and item reference.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Package | docling==2.151.1 |
| Device / parallelism | CPU; num_threads=8 |
| Conversion | do_ocr=False; do_table_structure=False; generate_parsed_pages=True |
| Hierarchy | No explicit HeadingHierarchyModel pass |
| Model provenance | Package-managed layout models; the runner does not explicitly pin individual layout-model revisions. |

**What changed and how it was selected**

Docling 2.151.1 detects section-header blocks; this row scores their native levels without our applying a separate hierarchy stage.

These are fixed configurations, not a learned WFP-specific correction or a recorded hyperparameter search. The tolerance variant is exploratory; “tuned” in its historical row name should not be read as a validated optimum.


**Output and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

The variants share one base conversion. Its recorded time includes first model load/download. The ordinary hierarchy pass has a separate timer; the tolerance pass was not separately timed. Their table times therefore do not represent three independent end-to-end conversions.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

These variants share detected blocks. A hierarchy stage cannot recover a heading absent from its inputs. The tolerance variant is exploratory.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) · [Project / GitHub](https://github.com/docling-project/docling) · [Docling technical report (2024)](https://arxiv.org/abs/2408.09869) · [Conversion and both hierarchy passes](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_docling.py) · [Pinned environment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/docling.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### Docling built-in hierarchy

Layout parser · CPU

Docling 2.151.1 plus its built-in HeadingHierarchyModel: the candidates are unchanged, but levels are inferred in an explicit second stage.


**Inference:** Native PDF → layout → Retain parsed pages → HeadingHierarchyModel → Export section headers

- **Native PDF → layout:** Docling 2.151.1; CPU, 8 threads; OCR and table structure disabled.
- **Retain parsed pages:** generate_parsed_pages=True preserves geometry required by the later hierarchy stage.
- **HeadingHierarchyModel:** Apply HeadingHierarchyOptions(enabled=True) to the same detected blocks.
- **Export section headers:** Keep text, native level, first provenance page, box and item reference.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Package | docling==2.151.1 |
| Device / parallelism | CPU; num_threads=8 |
| Conversion | do_ocr=False; do_table_structure=False; generate_parsed_pages=True |
| Hierarchy | HeadingHierarchyOptions(enabled=True); other hierarchy settings use library defaults |
| Model provenance | Package-managed layout models; the runner does not explicitly pin individual layout-model revisions. |

**What changed and how it was selected**

Docling 2.151.1 plus its built-in HeadingHierarchyModel: the candidates are unchanged, but levels are inferred in an explicit second stage.

These are fixed configurations, not a learned WFP-specific correction or a recorded hyperparameter search. The tolerance variant is exploratory; “tuned” in its historical row name should not be read as a validated optimum.


**Output and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

The variants share one base conversion. Its recorded time includes first model load/download. The ordinary hierarchy pass has a separate timer; the tolerance pass was not separately timed. Their table times therefore do not represent three independent end-to-end conversions.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

These variants share detected blocks. A hierarchy stage cannot recover a heading absent from its inputs. The tolerance variant is exploratory.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) · [Project / GitHub](https://github.com/docling-project/docling) · [Docling technical report (2024)](https://arxiv.org/abs/2408.09869) · [Conversion and both hierarchy passes](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_docling.py) · [Pinned environment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/docling.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### Popo + Docling / experimental MLX 8-bit

Visual hierarchy post-processing · local MLX

An experimental adapter combines Docling’s detected section headers with MinerU-Popo’s visual title-level task. We converted the pinned weights to 8-bit MLX, built page mosaics and aligned predictions across overlapping chunks.


**Inference:** Docling title candidates → 8-page visual chunks → MinerU-Popo · 8-bit → Align overlaps → source IDs

- **Docling title candidates:** Traverse section_header nodes; retain text and normalized boxes; skip picture/table subtrees.
- **8-page visual chunks:** Author adaptive_chunk and bordered page mosaics; one-page overlap.
- **MinerU-Popo · 8-bit:** “Title Level Analysis” prompt + IDs, pages, boxes, text; max_tokens=8192.
- **Align overlaps → source IDs:** Author label decoder and overlap level offsets; reject negative labels, preserve accepted values.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | DreamEternal/MinerU-Popo; revision af75342abdc5 |
| Author code | opendatalab/MinerU-Popo revision 8b9a8bd57ef3 |
| Quantization | mlx_vlm.convert; affine 8-bit; group_size=64 |
| Chunking | adaptive_chunk(..., chunk_size=8); recorded one-page overlap; author concatenate_pdf_pages_with_border |
| Prompt | &lt;image&gt; then “Title Level Analysis: ” and candidate ID/page/box/content fields |
| Generation | temperature=0; max_tokens=8192; prefill_step_size=256; seed=42; thinking not explicitly overridden |

**Candidate and overlap processing**

The adapter reads Docling’s default body hierarchy, excludes picture/table subtrees, and converts boxes to normalized page coordinates with the proper origin. Author preprocessing functions prepare title candidates and visual chunks.

extract_label2 decodes the response. Overlap disagreements involving a negative label reject both copies; otherwise the rounded mean level difference supplies an offset for new positive labels. Repeated IDs retain existing assignments. Nonnegative output labels are accepted as emitted, including 0; negative or missing labels are demoted to text. No hidden +1 shift is applied.


**Tuning and measured scope**

No fine-tuning or parameter search; fixed conversion and inference settings. Only the title-level task was run, not summary generation or other Popo tasks.

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

The reported hierarchy-stage time excludes base Docling extraction and model loading. This MLX adapter is experimental and is not an end-to-end replication of the authors’ benchmark.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

This is our experimental Docling + MLX adapter, not the authors’ standard end-to-end deployment. No summary task was run.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_popo_mlx.py) · [Project / GitHub](https://github.com/opendatalab/MinerU-Popo) · [Model / Hugging Face](https://huggingface.co/DreamEternal/MinerU-Popo) · [MinerU-Popo paper](https://arxiv.org/abs/2605.24973) · [Mosaic prompt and overlap alignment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_popo_mlx.py) · [Quantization and author-code preparation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/prepare_model.py) · [Model revision](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### MinerU2.5-Pro-2605-1.2B / direct MLX interface

Page vision model · local MLX

MinerU2.5-Pro-2605-1.2B runs its direct two_step_extract interface in MLX. The tested interface detected title blocks but did not supply their hierarchy levels.


**Inference:** 400 dpi → 2048 pixels → two_step_extract → Layout then content → No supplied H levels

- **400 dpi → 2048 pixels:** Render only the 32 audit pages; one image per call.
- **two_step_extract:** MinerUClient: mlx-engine, batch_size=1, max_concurrency=1.
- **Layout then content:** Convert returned blocks with json2md; accept title/doc_title/paragraph_title.
- **No supplied H levels:** Keep title text and box; absent # hierarchy stays null, with no added classifier.



**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | opendatalab/MinerU2.5-Pro-2605-1.2B; revision 08aaea840498 |
| Runtime | MLX bf16; mineru-vl-utils==2.0.9; backend="mlx-engine" |
| Parallelism | batch_size=1; max_concurrency=1; use_tqdm=False |
| Image / seed | 400 dpi → longest side ≤2048 pixels; MLX seed=42; image_analysis=False |
| Prompt / sampling | Internal two_step_extract library defaults; prompt, temperature and token ceiling are not explicitly overridden or individually recorded by this runner |

**What the score means**

The adapter checks the Markdown rendering of each title block for # through ######. When those markers are absent, level remains null. The historical result recovered 69 of 77 reference titles but no complete title-plus-level matches. Zero complete matches is not zero title detection.


**Tuning and measured scope**

No benchmark training and no additional title-leveling stage. This configuration should not be generalized to every MinerU deployment.

Only the 32 audited page images were processed. Scores use their 77 reference headings. Runs used local MLX on an Apple M4 Pro with 48 GB memory. A per-500-page time is an extrapolation, not a 500-page image run.

Timing surrounds two_step_extract and excludes model/client loading.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

This direct interface did not supply heading levels. Title detection alone is not a complete heading-and-level output.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_mineru_pro.py) · [Model / Hugging Face](https://huggingface.co/opendatalab/MinerU2.5-Pro-2605-1.2B) · [Project / GitHub](https://github.com/opendatalab/MinerU) · [Research paper linked by model card](https://arxiv.org/abs/2604.04771) · [Two-step interface and null-level handling](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_mineru_pro.py) · [Model revision](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Library pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/mlx.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)
