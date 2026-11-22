# On-premises PDF heading benchmark: scores, timings and methods

**22 completed local configurations, suitable for on-premises inference.** This experiment asks whether parsers and local models can recover heading titles, PDF pages and levels while retaining the text of long WFP evaluation reports.

**Primary metric: joint heading-and-level F0.5**, with joint precision and joint recall alongside it. A correct prediction must match the heading title, PDF page and exact level. Wrong levels and extra headings reduce precision; missed or incorrectly leveled headings reduce recall. There is no separate PASS/FAIL gate. Definitions and worked examples follow the table.

Qwen3.6-27B with sampled visual memory leads at **82.7% joint F0.5**, with **82.3% joint precision**, 65/77 correct heading-level pairs and two extras. Embedded PDF tags score **73.4% F0.5**, with 79.6% joint precision and 43/77 correct pairs. Chandra scores **72.6% F0.5**, 73.6% joint precision and 53/77 correct pairs. These are configuration-specific results from a small, assistant-annotated sample, without independent human validation.

**Our new precision-selected method:** [jump to the highlighted row](#our-trained-model). A validation-selected confidence filter raises historical joint F0.5 from **58.8% to 70.5%** and reduces extra headings from **23 to 2**, reaching **82.9% joint precision (34/41)** and **44.2% joint recall (34/77)**. It emits fewer headings: correct title-and-level pairs fall from **50/77 to 34/77**, with 38 titles missed. This is an explicit precision/recall trade-off. The three small CPU classifiers are unchanged; the LLM supplied training annotations and is not used at inference.

The candidate was selected from a fixed 36-setting grid on four separate validation reports. The original league and the previously inspected 38-heading set were scored only after selection. Both are regression evidence, not new independent tests. The historical selection rule included a 95% heading-only precision constraint; that rule remains documented in the experiment but is no longer a league-table qualification gate. [Experiment, every setting and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-precision/report.md).

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
3. **Score the same audit pages.** The [scorer](https://github.com/dividor/pdf-heading-benchmark/blob/main/src/pdf_heading_benchmark/evaluation.py) matches titles on the same original PDF page, using normalized text similarity of at least 90% after one-to-one Hungarian assignment. A combined success requires the exact reference H level too. Main chapters and annexes are H1; the cover title does not shift the body hierarchy. Joint precision divides correct heading-level pairs by all predictions; joint recall divides them by the 77 references. Joint F0.5 combines these with more emphasis on precision, penalizing extra predictions and wrong levels as well as missed headings.
4. **Check prose and record resources.** Native prose retention measures preserved five-word sequences from native PDF blocks of at least 50 words on the audit pages. It does not measure character accuracy, reading order or table extraction. Processing times were observed on a shared 48 GB Apple M4 Pro and have different scopes. Hardware, electricity, engineering, review and licensing costs were not measured in dollars.

This is **sampled-page heading accuracy**, even when a parser processed the full document. The completed configurations include variants of the same packages and models; they are not independent products. The single annotator, small purposive sample and exploratory configuration choices limit any claim about general robustness.

## Full configuration results

**Ranked by joint heading-and-level F0.5**, with **joint precision and joint recall** next to it. The first score column is highlighted. There are no PASS/FAIL labels; heading-only precision appears in the detailed results as a diagnostic. See the definitions and worked example below the table. In HTML, select the **i** beside a configuration, or its **Method / code** for its diagram, parameters and sources. Markdown retains those links and the detailed technique appendix. All configurations ran locally. Missing measurements remain unavailable rather than being assigned zero.

| Configuration | Primary score: joint F0.5 | Joint precision | Joint recall | Method / code | Status | Headings recovered | False headings | Native prose retention | Measured time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Qwen3.6-27B / MLX 4-bit / sampled visual memory](https://huggingface.co/Qwen/Qwen3.6-27B) | **82.7%** | 82.3% (65/79) | 84.4% (65/77) | [Ask Qwen3.6-27B to identify headings using the current page’s image and text, possible headings from the whole document, author-supplied tags and selected earlier page images.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_visual_memory.py) | completed | 100.0% (77/77) | 2 | — | 61.8 min / 32 pages |
| [Embedded PDF heading tags](https://www.w3.org/WAI/WCAG22/Techniques/pdf/PDF9) | **73.4%** | 79.6% (43/54) | 55.8% (43/77) | [Read PDF heading tags—the heading labels already embedded by the PDF’s author.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_pdf_tags.py) | completed | 67.5% (52/77) | 2 | — | 6.4 s / 32 pages |
| [Chandra OCR 2 / MLX](https://huggingface.co/datalab-to/chandra-ocr-2) | **72.6%** | 73.6% (53/72) | 68.8% (53/77) | [Chandra OCR 2 reads page images using its authors’ layout-reading prompt and image preparation.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_chandra_batch.py) | completed | 90.9% (70/77) | 2 | 98.7% | 17.2 min / 32 pages |
| <span id="our-trained-model"></span>[**OUR METHOD — confidence-filtered v2 (F0.5-selected)**](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-precision/report.md) | **70.5%** | 82.9% (34/41) | 44.2% (34/77) | [Three trained Extra Trees classifiers join text lines, recognize headings and compare levels. Reject headings below score 0.70, selected on separate validation reports to reduce false headings; no additional model training.](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/optimize_precision.py) | completed | 50.6% (39/77) | 2 | — | 11.7 s / 523 pages |
| <span id="our-calibrated-model"></span>[**OUR METHOD — calibrated decoding (experimental)**](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-calibration/report.md) | **59.2%** | 58.8% (47/80) | 61.0% (47/77) | [Make the previously trained three-classifier design less likely to label body text as a heading.](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/calibrate.py) | completed | 76.6% (59/77) | 21 | — | 14.5 s / 523 pages |
| <span id="our-original-model"></span>[OUR METHOD — grouped context v2 (previous selection)](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md) | **58.8%** | 57.5% (50/87) | 64.9% (50/77) | [Use three Extra Trees classifiers to join wrapped titles, recognize headings and levels, and compare the levels of neighboring headings.](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) | completed | 83.1% (64/77) | 23 | — | 12.6 s / 523 pages |
| [LightOnOCR-3-0.8B / MLX](https://huggingface.co/lightonai/LightOnOCR-3-0.8B) | **57.9%** | 57.5% (46/80) | 59.7% (46/77) | [LightOnOCR-3-0.8B reads one page image at a time and returns text with locations on the page.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_lighton_mlx.py) | completed | 93.5% (72/77) | 8 | 99.5% | 8.9 min / 32 pages |
| [LightOnOCR-3-4B / MLX grounding](https://huggingface.co/lightonai/LightOnOCR-3-4B) | **57.9%** | 57.5% (46/80) | 59.7% (46/77) | [LightOnOCR-3-4B reads page images and returns text with page locations, using the same output convention as the 0.8-billion-parameter model.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_chandra_batch.py) | completed | 93.5% (72/77) | 8 | 99.3% | 23.5 min / 32 pages |
| [v2: learned grouping](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md) | **55.8%** | 53.7% (51/95) | 66.2% (51/77) | [Train two Extra Trees classifiers: one decides which neighboring lines belong to the same heading, and one labels the resulting text groups as body text or H1–H5.](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) | completed | 96.1% (74/77) | 21 | — | 12.0 s / 523 pages |
| [v2: more annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md) | **44.9%** | 43.2% (41/95) | 53.2% (41/77) | [Test whether more labeled examples improve the original single-classifier design.](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) | completed | 89.6% (69/77) | 26 | — | 9.3 s / 523 pages |
| [LLM annotations → Extra Trees v1 (CPU)](https://github.com/dividor/pdf-heading-benchmark/blob/main/src/pdf_heading_benchmark/supervised_models.py) | **44.5%** | 44.3% (35/79) | 45.5% (35/77) | [Train one Extra Trees classifier to decide whether each PDF text line is body text or a heading at a particular level.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/supervised/compare.py) | completed | 76.6% (59/77) | 20 | — | 7.7 s / 523 pages |
| [MinerU 4.2.3 basic CPU](https://github.com/opendatalab/MinerU) | **44.4%** | 45.6% (31/68) | 40.3% (31/77) | [MinerU 4.2.3 uses its basic PDF parser on the CPU through ONNX Runtime.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_mineru.py) | completed | 85.7% (66/77) | 2 | 99.1% | 11.2 min / 523 pages |
| [Qwen3.5-4B / union candidates](https://huggingface.co/Qwen/Qwen3.5-4B) | **41.0%** | 43.9% (25/57) | 32.5% (25/77) | [Ask Qwen3.5-4B to assign levels to possible headings extracted by Docling and PyMuPDF4LLM.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) | completed | 70.1% (54/77) | 3 | — | 1.7 min / hierarchy stage only |
| [Qwen3.5-4B / PyMuPDF candidates](https://huggingface.co/Qwen/Qwen3.5-4B) | **37.5%** | 40.7% (22/54) | 28.6% (22/77) | [Ask Qwen3.5-4B to assign levels to possible headings extracted by PyMuPDF4LLM.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) | completed | 70.1% (54/77) | 0 | — | 1.5 min / hierarchy stage only |
| [PyMuPDF4LLM 2.1](https://github.com/pymupdf/pymupdf4llm) | **37.5%** | 37.8% (28/74) | 36.4% (28/77) | [PyMuPDF4LLM 2.1 turns the PDF’s existing text into Markdown.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_pymupdf4llm.py) | completed | 93.5% (72/77) | 2 | 98.8% | 51.8 s / 523 pages |
| [Qwen3.5-4B / MinerU candidates](https://huggingface.co/Qwen/Qwen3.5-4B) | **33.3%** | 34.3% (23/67) | 29.9% (23/77) | [Ask Qwen3.5-4B to assign levels to possible headings extracted by MinerU’s basic parser.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) | completed | 85.7% (66/77) | 1 | — | 1.3 min / hierarchy stage only |
| [Docling fixed tolerance 0.15](https://github.com/docling-project/docling) | **30.8%** | 31.4% (22/70) | 28.6% (22/77) | [Use Docling 2.151.1 with a fixed font-style tolerance of 0.15 in its hierarchy step.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) | completed | 88.3% (68/77) | 2 | 98.4% | 1.7 min / 523 pages |
| [Marker 2.2 no OCR/LLM](https://github.com/datalab-to/marker) | **25.5%** | 25.7% (19/74) | 24.7% (19/77) | [Marker 2.2 parses the complete PDF locally on the CPU.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_marker.py) | completed | 84.4% (65/77) | 9 | 98.8% | 44.0 s / 523 pages |
| [Docling 2.151.1 default](https://github.com/docling-project/docling) | **22.4%** | 22.9% (16/70) | 20.8% (16/77) | [Use the heading levels returned by Docling 2.151.1 when it first reads the PDF.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) | completed | 88.3% (68/77) | 2 | 98.4% | 1.7 min / 523 pages |
| [Docling built-in hierarchy](https://github.com/docling-project/docling) | **22.4%** | 22.9% (16/70) | 20.8% (16/77) | [Use Docling 2.151.1 to find headings, then run its built-in HeadingHierarchyModel to assign their levels.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) | completed | 88.3% (68/77) | 2 | 98.4% | 1.7 min / 523 pages |
| [Popo + Docling / experimental MLX 8-bit](https://github.com/opendatalab/MinerU-Popo) | **21.0%** | 21.4% (15/70) | 19.5% (15/77) | [Use MinerU-Popo to assign levels to headings first detected by Docling.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_popo_mlx.py) | completed | 88.3% (68/77) | 2 | 98.4% | 14.9 min / hierarchy stage only |
| [MinerU2.5-Pro-2605-1.2B / direct MLX interface](https://huggingface.co/opendatalab/MinerU2.5-Pro-2605-1.2B) | **0.0%** | 0.0% (0/72) | 0.0% (0/77) | [MinerU2.5-Pro-2605-1.2B reads the layout and text of page images.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_mineru_pro.py) | completed | 89.6% (69/77) | 3 | 99.0% | 9.5 min / 32 pages |

## Primary metric: heading-and-level F0.5

A useful output must identify a real heading, put it on the correct PDF page and assign the correct level. Invented headings also matter. We therefore rank by **joint heading-and-level F0.5**, supported by **joint precision** and **joint recall**. All three require the heading and its level to be correct. There is no separate PASS/FAIL qualification gate.

Let **G** be the number of reference headings, **P** all predicted headings, **M** the one-to-one title/page matches and **C** those matches with the exact reference level. Matching uses the unchanged same-page, normalized-title similarity ≥0.90 contract. Counts are pooled across reports before calculating metrics (micro averaging).

| Measure | Definition | What it tells us |
| --- | --- | --- |
| Joint precision | C / P | Fraction of emitted headings with both title/page and level correct |
| Joint recall | C / G | Fraction of reference headings recovered at the correct level |
| Joint F1 | 2C / (P + G) | Equal precision/recall emphasis |
| **Joint F0.5** | **1.25C / (P + 0.25G)** | Primary score; emphasizes precision more than recall |
| Heading-detection precision | M / P | Diagnostic only: real headings regardless of level; shown in detailed results |

Joint true positives are **C**, false positives are **P − C**, and false negatives are **G − C**. A wrong-level heading is both a joint false positive and a joint false negative. A missing heading contributes a false negative; an extra heading contributes a false positive. No predictions gives a zero score. Unknown levels earn no joint credit. Heading-only precision ignores wrong levels, so it is a diagnostic rather than a quality requirement.

For example, 10 reference headings, 12 predictions, 10 title matches and 9 correct levels give joint precision 75%, recall 90%, F1 81.8% and F0.5 77.6%. Recovering every title does not imply correct hierarchy.

MinerU basic illustrates why the distinction matters: 66 of its 68 predictions match real titles, but only 31 have the correct level. Its joint precision is **45.6% (31/68)**, joint recall **40.3% (31/77)** and joint F0.5 **44.4%**. The 97.1% heading-only precision ignores 35 wrong levels. OUR METHOD's confidence-filtered configuration has **82.9% joint precision (34/41)** and **44.2% joint recall (34/77)**, yielding **70.5% joint F0.5**. Its two extra headings are separate from its five wrong-level headings.

For future optimization, select using validation joint F0.5, report joint precision and recall alongside it, then freeze the configuration before evaluation elsewhere. Do not choose settings using the main league or inspected regression pages.

**Historical selection remains unchanged:** the published 36-setting confidence-filter experiment selected the highest validation joint F0.5 among candidates with at least 95% heading-only precision. That was its actual selection rule, and its protocol and results remain available. We have removed this gate from the league table because it ignores level errors. Recomputing or presenting joint metrics does not retrain models or retroactively change how any configuration was selected.


## How to read the table

**Local resources and cost:** all configurations in this report ran locally on a shared 48 GB Apple M4 Pro. Hardware, electricity, setup, engineering, manual review and commercial licensing costs were not measured in dollars. Observed processing times are reported with their actual scope; local inference is not cost-free.

**Scopes and timing:** earlier CPU parsers processed all 523 pages. New local OCR models processed the complete text on the 32 audit pages. Qwen3.6 read native page text, full-document candidate titles and author PDF tags, and current/previous sampled-page images; it does not OCR the body. Its measured time excludes those candidate-generation stages. Qwen3.5 and Popo timings cover only hierarchy inference. Hardware was a shared 48 GB Apple M4 Pro. New-model times exclude downloads, loading and aborted attempts; some earlier CPU times include setup. These are observations with different scopes, not a controlled throughput benchmark.

**Text:** native prose retention measures five-word sequences preserved from native PDF blocks of at least 50 words, on the audit pages. It is not character accuracy, reading order, semantic accuracy or table correctness. A missing score means not evaluated or not applicable. Hierarchy-only stages reuse extracted text.

**Configuration caveats:** MinerU Pro's direct interface recovered headings but supplied no hierarchy levels; its 0/77 complete outputs must not be described as zero heading detection. The Qwen3.6 implementation uses only previously processed audit pages as visual memory; it is not a reproduction of a full-document memory benchmark. The Popo result is an experimental 8-bit MLX port with 8-page chunks, not an upstream performance claim. LightOn 4B historical timing includes five single-page checkpoints followed by batch-two processing; a clean rerun uses batch two throughout. The 0.15 Docling tolerance was fixed across these reports but remains an exploratory choice, not an untuned general default.

**Reference and uncertainty:** pages were deliberately selected to span front matter, body chapters, subsections and annexes. A single assistant annotated them visually. The original 2018 resilience report was excluded after prior document-specific investigation. No per-report title/level correction rules are applied here. The sample is small, covers born-digital reports only, and has no inter-annotator agreement study. Ranking on it cannot establish robustness on arbitrary documents. No missing run is assigned a zero score.

**Reproducibility:** the repo includes the frozen audit labels, page-restricted predictions and original summary/match records. `uv run pdf-headings score --historical` recomputes the bundled historical predictions, including the local configurations selected for this report, without model downloads or credentials. Raw full-page responses remain in the original local experiment archive; they are not bundled in the public repo. Fresh runners save raw responses outside Git. Seven historical Qwen formatting deviations were accepted by a generic JSON array/wrapper/single-fence reader without changing title or level values. Refactored runners retain prompts and settings; model/GPU runs have not all been repeated after packaging. See [method details](https://github.com/dividor/pdf-heading-benchmark/blob/main/docs/reproducibility.md).

**Licenses:** the repository's MIT license covers its code, not third-party packages, model weights or WFP reports. Chandra weights have commercial-use restrictions; applicable licensing costs are additional. See each linked model/package and [third-party notices](https://github.com/dividor/pdf-heading-benchmark/blob/main/THIRD_PARTY_NOTICES.md).

**Supervised Extra Trees:** the frozen classifier was trained on 16 different WFP reports, selected using four validation reports, and first evaluated on four new test reports. It was then applied without refitting to the original four benchmark PDFs and scored with the same 77-heading matching contract as every row above: **59/77 recovered, 35/77 at the correct level, 20 extra headings**. The 7.7-second measurement covers all 523 pages, including extraction and classification but excluding model loading and output writes. Native prose retention was not evaluated. Its separate 82.0% exact-level line F1 on the new test set uses a different corpus and metric and is not the number ranked here. [Comparison runner and evidence](https://github.com/dividor/pdf-heading-benchmark/tree/main/outputs/supervised/comparison) · [Training protocol](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/supervised/report.md).

**Earlier calibration experiment:** body-weight calibration was selected using validation F1. On the historical table its joint F0.5 is 59.2%, versus 58.8% for the original context model; joint precision is 58.8% (47/80). On the inspected 38-heading set, both configurations still have 36 correct heading-level pairs; higher F1 came from fewer extras. Those original results and selection criteria remain frozen.

**New precision optimization:** the threshold-0.70 candidate was selected on validation joint F0.5 subject to the 95% heading-precision gate. This was the experiment’s historical selection rule, not a current league-table quality gate. On the historical sample, joint precision is 82.9% (34/41), joint recall is 44.2% (34/77), and joint F0.5 is 70.5%. It has two extra headings and five genuine headings with wrong levels. On the inspected 38-heading set it emits 28 correctly leveled headings, no extras, and misses ten. Reused small validation and regression sets limit the result; a fresh independent evaluation remains necessary. [Settings, all validation scores and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-precision/report.md).


## Results by report

| Runner / configuration | Report | Recovered | Correct heading + level | False headings | Heading-only precision (diagnostic) |
| --- | --- | --- | --- | --- | --- |
| run_docling.py / docling_default | targeting | 13/15 | 3/15 | 0 | 100.0% |
| run_docling.py / docling_default | midterm | 17/18 | 5/18 | 0 | 100.0% |
| run_docling.py / docling_default | indonesia | 17/21 | 4/21 | 0 | 100.0% |
| run_docling.py / docling_default | colombia | 21/23 | 4/23 | 2 | 91.3% |
| run_docling.py / docling_hierarchy | targeting | 13/15 | 0/15 | 0 | 100.0% |
| run_docling.py / docling_hierarchy | midterm | 17/18 | 1/18 | 0 | 100.0% |
| run_docling.py / docling_hierarchy | indonesia | 17/21 | 7/21 | 0 | 100.0% |
| run_docling.py / docling_hierarchy | colombia | 21/23 | 8/23 | 2 | 91.3% |
| run_docling.py / docling_tuned | targeting | 13/15 | 0/15 | 0 | 100.0% |
| run_docling.py / docling_tuned | midterm | 17/18 | 6/18 | 0 | 100.0% |
| run_docling.py / docling_tuned | indonesia | 17/21 | 4/21 | 0 | 100.0% |
| run_docling.py / docling_tuned | colombia | 21/23 | 12/23 | 2 | 91.3% |
| run_pymupdf4llm.py / pymupdf4llm | targeting | 14/15 | 3/15 | 0 | 100.0% |
| run_pymupdf4llm.py / pymupdf4llm | midterm | 18/18 | 0/18 | 0 | 100.0% |
| run_pymupdf4llm.py / pymupdf4llm | indonesia | 18/21 | 16/21 | 2 | 90.0% |
| run_pymupdf4llm.py / pymupdf4llm | colombia | 22/23 | 9/23 | 0 | 100.0% |
| run_marker.py / marker | targeting | 13/15 | 6/15 | 4 | 76.5% |
| run_marker.py / marker | midterm | 18/18 | 6/18 | 2 | 90.0% |
| run_marker.py / marker | indonesia | 17/21 | 4/21 | 0 | 100.0% |
| run_marker.py / marker | colombia | 17/23 | 3/23 | 3 | 85.0% |
| run_mineru.py / mineru_basic | targeting | 13/15 | 8/15 | 0 | 100.0% |
| run_mineru.py / mineru_basic | midterm | 18/18 | 9/18 | 1 | 94.7% |
| run_mineru.py / mineru_basic | indonesia | 17/21 | 7/21 | 1 | 94.4% |
| run_mineru.py / mineru_basic | colombia | 18/23 | 7/23 | 0 | 100.0% |
| run_lighton_mlx.py / lighton_mlx | targeting | 13/15 | 8/15 | 2 | 86.7% |
| run_lighton_mlx.py / lighton_mlx | midterm | 18/18 | 13/18 | 0 | 100.0% |
| run_lighton_mlx.py / lighton_mlx | indonesia | 19/21 | 13/21 | 2 | 90.5% |
| run_lighton_mlx.py / lighton_mlx | colombia | 22/23 | 12/23 | 4 | 84.6% |
| run_popo_mlx.py / popo_docling | targeting | 13/15 | 0/15 | 0 | 100.0% |
| run_popo_mlx.py / popo_docling | midterm | 17/18 | 5/18 | 0 | 100.0% |
| run_popo_mlx.py / popo_docling | indonesia | 17/21 | 5/21 | 0 | 100.0% |
| run_popo_mlx.py / popo_docling | colombia | 21/23 | 5/23 | 2 | 91.3% |
| run_qwen_ids.py / qwen_ids_union | targeting | 0/15 | 0/15 | 0 | 0.0% |
| run_qwen_ids.py / qwen_ids_union | midterm | 14/18 | 6/18 | 0 | 100.0% |
| run_qwen_ids.py / qwen_ids_union | indonesia | 18/21 | 12/21 | 1 | 94.7% |
| run_qwen_ids.py / qwen_ids_union | colombia | 22/23 | 7/23 | 2 | 91.7% |
| run_qwen_ids.py / qwen_ids_mineru_basic | targeting | 13/15 | 2/15 | 0 | 100.0% |
| run_qwen_ids.py / qwen_ids_mineru_basic | midterm | 18/18 | 10/18 | 1 | 94.7% |
| run_qwen_ids.py / qwen_ids_mineru_basic | indonesia | 17/21 | 8/21 | 0 | 100.0% |
| run_qwen_ids.py / qwen_ids_mineru_basic | colombia | 18/23 | 3/23 | 0 | 100.0% |
| run_qwen_ids.py / qwen_ids_pymupdf4llm | targeting | 14/15 | 4/15 | 0 | 100.0% |
| run_qwen_ids.py / qwen_ids_pymupdf4llm | midterm | 0/18 | 0/18 | 0 | 0.0% |
| run_qwen_ids.py / qwen_ids_pymupdf4llm | indonesia | 18/21 | 6/21 | 0 | 100.0% |
| run_qwen_ids.py / qwen_ids_pymupdf4llm | colombia | 22/23 | 12/23 | 0 | 100.0% |
| run_pdf_tags.py / pdf_tags_audit_only | targeting | 9/15 | 9/15 | 0 | 100.0% |
| run_pdf_tags.py / pdf_tags_audit_only | midterm | 13/18 | 13/18 | 0 | 100.0% |
| run_pdf_tags.py / pdf_tags_audit_only | indonesia | 14/21 | 10/21 | 2 | 87.5% |
| run_pdf_tags.py / pdf_tags_audit_only | colombia | 16/23 | 11/23 | 0 | 100.0% |
| run_mineru_pro.py / mineru_pro_mlx | targeting | 13/15 | 0/15 | 0 | 100.0% |
| run_mineru_pro.py / mineru_pro_mlx | midterm | 18/18 | 0/18 | 1 | 94.7% |
| run_mineru_pro.py / mineru_pro_mlx | indonesia | 19/21 | 0/21 | 0 | 100.0% |
| run_mineru_pro.py / mineru_pro_mlx | colombia | 19/23 | 0/23 | 2 | 90.5% |
| run_chandra_batch.py / lighton4b_mlx | targeting | 13/15 | 9/15 | 3 | 81.2% |
| run_chandra_batch.py / lighton4b_mlx | midterm | 18/18 | 13/18 | 0 | 100.0% |
| run_chandra_batch.py / lighton4b_mlx | indonesia | 19/21 | 13/21 | 1 | 95.0% |
| run_chandra_batch.py / lighton4b_mlx | colombia | 22/23 | 11/23 | 4 | 84.6% |
| run_chandra_batch.py / chandra2_mlx | targeting | 13/15 | 8/15 | 0 | 100.0% |
| run_chandra_batch.py / chandra2_mlx | midterm | 18/18 | 15/18 | 0 | 100.0% |
| run_chandra_batch.py / chandra2_mlx | indonesia | 19/21 | 16/21 | 0 | 100.0% |
| run_chandra_batch.py / chandra2_mlx | colombia | 20/23 | 14/23 | 2 | 90.9% |
| run_qwen_visual_memory.py / qwen36_visual_memory | targeting | 15/15 | 12/15 | 0 | 100.0% |
| run_qwen_visual_memory.py / qwen36_visual_memory | midterm | 18/18 | 18/18 | 0 | 100.0% |
| run_qwen_visual_memory.py / qwen36_visual_memory | indonesia | 21/21 | 19/21 | 0 | 100.0% |
| run_qwen_visual_memory.py / qwen36_visual_memory | colombia | 23/23 | 16/23 | 2 | 92.0% |
| compare.py / supervised_extra_trees | targeting | 10/15 | 4/15 | 10 | 50.0% |
| compare.py / supervised_extra_trees | midterm | 16/18 | 13/18 | 2 | 88.9% |
| compare.py / supervised_extra_trees | indonesia | 14/21 | 9/21 | 6 | 70.0% |
| compare.py / supervised_extra_trees | colombia | 19/23 | 9/23 | 2 | 90.5% |
| train.py / structure_expanded_line | targeting | 12/15 | 7/15 | 11 | 52.2% |
| train.py / structure_expanded_line | midterm | 18/18 | 14/18 | 0 | 100.0% |
| train.py / structure_expanded_line | indonesia | 18/21 | 10/21 | 13 | 58.1% |
| train.py / structure_expanded_line | colombia | 21/23 | 10/23 | 2 | 91.3% |
| train.py / structure_learned_groups | targeting | 15/15 | 12/15 | 7 | 68.2% |
| train.py / structure_learned_groups | midterm | 16/18 | 14/18 | 1 | 94.1% |
| train.py / structure_learned_groups | indonesia | 21/21 | 12/21 | 11 | 65.6% |
| train.py / structure_learned_groups | colombia | 22/23 | 13/23 | 2 | 91.7% |
| train.py / structure_context_relations | targeting | 15/15 | 9/15 | 10 | 60.0% |
| train.py / structure_context_relations | midterm | 16/18 | 15/18 | 2 | 88.9% |
| train.py / structure_context_relations | indonesia | 14/21 | 13/21 | 11 | 56.0% |
| train.py / structure_context_relations | colombia | 19/23 | 13/23 | 0 | 100.0% |
| calibrate.py / structure_calibrated | targeting | 15/15 | 9/15 | 9 | 62.5% |
| calibrate.py / structure_calibrated | midterm | 16/18 | 15/18 | 2 | 88.9% |
| calibrate.py / structure_calibrated | indonesia | 12/21 | 11/21 | 10 | 54.5% |
| calibrate.py / structure_calibrated | colombia | 16/23 | 12/23 | 0 | 100.0% |
| optimize_precision.py / structure_precision | targeting | 7/15 | 6/15 | 1 | 87.5% |
| optimize_precision.py / structure_precision | midterm | 12/18 | 12/18 | 0 | 100.0% |
| optimize_precision.py / structure_precision | indonesia | 7/21 | 7/21 | 1 | 87.5% |
| optimize_precision.py / structure_precision | colombia | 13/23 | 9/23 | 0 | 100.0% |

## Technique diagrams and sources

The HTML report opens these diagrams in a modal.


### Qwen3.6-27B / MLX 4-bit / sampled visual memory

Vision + document context · local MLX

Ask Qwen3.6-27B to identify headings using the current page’s image and text, possible headings from the whole document, author-supplied tags and selected earlier page images. This supplies more context to an already trained model; we did not train it on WFP labels.


**Inference:** Collect document-wide clues → Show the current and earlier pages → Generate heading decisions locally → Carry selected images forward

- **Collect document-wide clues:** Supply possible titles and page numbers from PyMuPDF4LLM, plus any author-supplied heading tags. Omit the parser’s predicted levels.
- **Show the current and earlier pages:** Use the current page at up to 1792 pixels and at most six earlier sampled-page images at up to 1280 pixels. This is what “visual memory” means here.
- **Generate heading decisions locally:** Run Qwen3.6-27B with 4-bit weights through MLX. Include the current page’s text; disable thinking; use temperature=0 and max_tokens=4096.
- **Carry selected images forward:** Read the predicted headings and keep the latest sampled page for each H1–H6 level as context for later pages. Unseen intervening pages are not included.



**Models and terms explained**

- [Qwen3.6-27B](https://huggingface.co/Qwen/Qwen3.6-27B): A pretrained model used here to read page images together with text context; 27B identifies its model size.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.
- [4-bit / 8-bit weights](https://github.com/ml-explore/mlx-lm): Reduced-precision representations of a model’s learned numbers, used to lower memory requirements. The number describes storage precision, not heading depth or model accuracy.

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

Read PDF heading tags—the heading labels already embedded by the PDF’s author. This baseline uses no trained model: an H2 structure tag is taken to mean H2, even when the author’s tagging is incomplete or wrong.


**Inference:** Read accessibility structure → Find heading tags → Recover the associated text → Export the author’s labels

- **Read accessibility structure:** Inspect the PDF structure tree, which describes tagged content. This is different from the outline bookmarks shown in a PDF reader’s navigation panel.
- **Find heading tags:** Select structure elements named H1 through H6.
- **Recover the associated text:** Use marked-content IDs—the PDF’s internal references connecting a tag to page content—to find characters on the 32 audit pages.
- **Export the author’s labels:** Join those characters into titles and use each tag’s number as its level. Do not infer missing tags or repair levels.



**Models and terms explained**

- [PDF heading tags](https://www.w3.org/WAI/WCAG22/Techniques/pdf/PDF9): H1–H6 labels embedded in the PDF’s accessibility structure by its author. They can be absent, incomplete or incorrect.

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

Chandra OCR 2 reads page images using its authors’ layout-reading prompt and image preparation. We derive heading levels from the HTML it generates. The local MLX run processes four independent pages together with bf16 weights.


**Inference:** Prepare images as the authors specify → Use the supplied layout prompt → Read four pages per batch → Read HTML heading tags

- **Prepare images as the authors specify:** Render at least 192 dots per inch with a minimum 1024-pixel short side, then apply the upstream scale_to_fit image function.
- **Use the supplied layout prompt:** Send OCR_LAYOUT_PROMPT, the model authors’ instructions for reading document content and layout. Use a compatible chat template with thinking disabled.
- **Read four pages per batch:** Run Chandra OCR 2 in MLX with bf16 weights, a 16,000,000-pixel batch budget, temperature=0 and max_new_tokens=12384.
- **Read HTML heading tags:** Convert <h1> through <h6> to levels. Keep section-heading blocks without such tags, but mark their levels as unknown.



**Models and terms explained**

- [Chandra OCR 2](https://huggingface.co/datalab-to/chandra-ocr-2): A document image-reading model that produces structured text; this benchmark reads HTML heading tags from its output.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.
- [bf16](https://ml-explore.github.io/mlx/build/html/python/data_types.html): A 16-bit floating-point number format used for model weights and calculations. It is a numerical format, not a particular model or training technique.

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

Learned classifiers · local CPU

OUR METHOD uses three previously trained Extra Trees classifiers and adds a rule that rejects uncertain heading predictions. Extra Trees is a machine-learning algorithm that combines many decision trees; “previously trained” means their learned rules were kept unchanged while we tested rejection settings. This reduced invented headings from 23 to two, but correct title-and-level answers also fell from 50/77 to 34/77.


**Training:** Start with three trained classifiers → Try 36 ways to reject uncertain headings → Choose the best qualifying setting

- **Start with three trained classifiers:** Use the Extra Trees models that learned line joining, heading recognition and level relationships from 887 annotated heading groups in 20 WFP reports. No further model training is done in this experiment.
- **Try 36 ways to reject uncertain headings:** Use four separate validation reports to compare two text-group classifiers, body-score multipliers 1/2/4, heading-score cutoffs 0/0.5/0.7/0.85 and relationship weights 1/0 where applicable.
- **Choose the best qualifying setting:** First require at least 95% of emitted titles to be genuine headings, regardless of level. Among qualifying settings, choose the highest joint F0.5. The selected design uses document context, a 0.70 cutoff, body multiplier 1 and relationship weight 1.



**Inference:** Join lines that belong to one title → Reject uncertain heading predictions → Compare consecutive headings → Assign levels to the accepted headings

- **Join lines that belong to one title:** A 200-tree Extra Trees classifier uses 100 measurements of adjacent lines to decide whether to join them, including across PDF block boundaries.
- **Reject uncertain heading predictions:** The 47-measurement heading classifier must prefer a heading over body text, and its highest heading score must be at least 0.70. This score is not a verified 70% chance of being correct.
- **Compare consecutive headings:** A third 200-tree Extra Trees classifier uses 142 measurements to predict whether the next heading is at a higher, equal or deeper level.
- **Assign levels to the accepted headings:** Run Viterbi decoding with relationship weight 1. Keep the full extracted text, including rejected groups. On the original benchmark: 41 predictions, 39 genuine headings, 34 with the correct level.



**Models and terms explained**

- [Extra Trees](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html): A classifier that averages predictions from many randomized decision trees. A tree makes a sequence of decisions about input measurements. This benchmark uses scikit-learn’s ExtraTreesClassifier, with 200 trees per component.
- [Features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py): The numeric measurements supplied to a classifier—for example font size, boldness, line spacing or whether a title occurs in the table of contents. They are calculated from the PDF, not supplied reference answers.
- [Validation reports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json): Reports kept separate from model fitting and used to choose between designs or decision settings. The later inspected test reports are now regression checks: they can expose a failure but no longer provide a fresh independent evaluation.
- [Viterbi decoding](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py): An algorithm for choosing the highest-scoring sequence of heading levels. Here it combines each heading’s own scores with scores for the relationship to the preceding heading. It does not train or add another model.

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

**Training data and annotation source**

A single assistant reviewed source text, layout/page snippets and table-of-contents context and supplied explicit line groups and H levels. The annotation provenance does not record a precise model version used by the annotating assistant, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate reference labels. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The training split contains 20 WFP reports, 887 heading groups and 7,039 labeled lines. Line classes: body=5,849; H1=238; H2=391; H3=432; H4=128; H5=1; H6=0. Negative examples come from 112 fully reviewed training pages. Unmarked lines on positive-only annotation pages are not automatically negatives. The H5/H6 coverage is a material limitation.

Validation uses reports 103, 538, 176 and 128: 21 reference groups on 20 reviewed pages. The test from the second training experiment uses reports 321, 844, 560 and 394: 38 groups on 32 reviewed pages. Splits are by report, not random lines; report-template families are not held out. Those test pages have now been inspected and are results on previously inspected test documents for subsequent changes.


**What each model learns**

The 33 measurements of selectable PDF text lines cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.

The context classifier uses 47 features: the 43 group features plus style_numbered_count, style_mean_depth, style_max_depth and toc_exact_title. Style statistics group lines by rounded font size, bold/italic and color, then summarize numeric-prefix depth. table-of-contents matching normalizes title text, strips its numeric prefix and dot leaders, and checks exact membership among dot-leader lines. This is a learned input feature, not a hard TOC level override.

The relationship classifier uses 142 features: two 47-feature groups, their differences and page delta. Its 867 training pairs are consecutive annotated headings. Target −1 means the next H number is smaller (shallower), 0 means equal and +1 means larger (deeper). It learns direction, not the number of levels skipped.


**Filter and validation selection**

The largest heading-class score must be at least 0.70 and a heading must beat the weighted body score. Scores are not calibrated probabilities. Filtering precedes relationship inference and Viterbi, so rejected groups cannot return.

The fixed 36-setting grid was evaluated only on the four validation reports (21 headings). Twenty-three settings met the 95% detection-precision gate. The selected configuration emitted 14 headings, all correctly leveled, and missed seven: joint F0.5 90.9%. Exact ties retain fixed grid order. No eligible candidate would mean no selection.


**Measured result and lost recall**

On the historical 77-heading benchmark, joint F0.5 rises from 58.8% to 70.5%, extras fall from 23 to 2, and heading precision rises to 95.1%. Correct heading-level pairs fall from 50 to 34. Of 41 predictions, 39 are real headings and five of those have incorrect levels; 38 reference titles are missed.

On the previously inspected 38-heading regression set, the candidate emits 28 headings, all correctly leveled, misses ten and scores 93.3% joint F0.5. These are regression results, not independent new test evidence. The 95.1% historical precision is a narrow sample pass.


**Runtime and reproducibility**

Measured full-PDF runtime is 11.66 seconds across all 523 pages on the shared 48 GB Apple M4 Pro. It includes extraction, features and inference; model loading and writes are excluded. The 600 previously trained decision trees and data-only JSON deployment are unchanged.

Selection saves model scores for reuse for speed and reads no test documents. The protocol records the search settings before selection and source/model/configuration hashes. Regression checks those hashes. Full text and raw outputs remain external; compact audit predictions and all grid scores are committed.

The 95% gate checks whether predicted titles are real headings; it does not check their levels. Here 39/41 titles are real (95.1%), but only 34/41 have correct levels (82.9%), and 38 reference titles are missed. These small, previously inspected datasets do not establish production robustness.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/optimize_precision.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Exact estimator constructor and JSON export](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Native line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [Group/context/pair features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py) · [Training components and variant selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/train.py) · [PDF sources and report splits](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json) · [Reviewable heading annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/annotations.json) · [Inference, grouping and Viterbi](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py) · [Precision filter and sequence inference](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/precision_inference.py) · [Joint metric implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/joint_metrics.py) · [All validation results](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-precision/evidence/selection.json) · [Experiment, trade-offs and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-precision/report.md) · [Run on a new PDF](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_precision.py)


### OUR METHOD v2 + calibrated decoding (CPU)

Learned classifiers · local CPU

Make the previously trained three-classifier design less likely to label body text as a heading. Multiply its body-text score by two before choosing a class. The models themselves are unchanged; only this decision rule was selected on validation reports.


**Training:** Start with the trained models → Try nine decision settings → Keep the validation choice

- **Start with the trained models:** Use the line-joining, heading-classification and relationship classifiers trained on 887 heading groups in 20 WFP reports. Do not train them again or change the labels.
- **Try nine decision settings:** On four validation reports, combine body-score multipliers 1, 1.5 and 2 with relationship weights 1, 0.5 and 0.
- **Keep the validation choice:** Body multiplier 2 and relationship weight 1 scored 81.1% exact group-and-level F1. The original benchmark was evaluated afterwards; it did not choose these settings.



**Inference:** Join lines that belong to one title → Favor ordinary body text → Compare consecutive headings → Choose levels for the remaining headings

- **Join lines that belong to one title:** A 200-tree Extra Trees classifier uses 100 measurements of adjacent lines to decide whether to join them, including across PDF block boundaries.
- **Favor ordinary body text:** Use the same 200-tree heading classifier with 47 measurements. Double its body-text score, then choose the highest-scoring class; this can reject real headings too.
- **Compare consecutive headings:** A third 200-tree Extra Trees classifier uses 142 measurements to predict whether the next heading is at a higher, equal or deeper level.
- **Choose levels for the remaining headings:** Run Viterbi decoding with relationship weight 1. Rejected text groups cannot be recovered by this step.



**Models and terms explained**

- [Extra Trees](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html): A classifier that averages predictions from many randomized decision trees. A tree makes a sequence of decisions about input measurements. This benchmark uses scikit-learn’s ExtraTreesClassifier, with 200 trees per component.
- [Features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py): The numeric measurements supplied to a classifier—for example font size, boldness, line spacing or whether a title occurs in the table of contents. They are calculated from the PDF, not supplied reference answers.
- [Validation reports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json): Reports kept separate from model fitting and used to choose between designs or decision settings. The later inspected test reports are now regression checks: they can expose a failure but no longer provide a fresh independent evaluation.
- [Viterbi decoding](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py): An algorithm for choosing the highest-scoring sequence of heading levels. Here it combines each heading’s own scores with scores for the relationship to the preceding heading. It does not train or add another model.

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

**Previously trained models and their examples**

A single assistant reviewed source text, layout/page snippets and table-of-contents context and supplied explicit line groups and H levels. The annotation provenance does not record a precise model version used by the annotating assistant, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate reference labels. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The training split contains 20 WFP reports, 887 heading groups and 7,039 labeled lines. Line classes: body=5,849; H1=238; H2=391; H3=432; H4=128; H5=1; H6=0. Negative examples come from 112 fully reviewed training pages. Unmarked lines on positive-only annotation pages are not automatically negatives. The H5/H6 coverage is a material limitation.

Validation uses reports 103, 538, 176 and 128: 21 reference groups on 20 reviewed pages. The test from the second training experiment uses reports 321, 844, 560 and 394: 38 groups on 32 reviewed pages. Splits are by report, not random lines; report-template families are not held out. Those test pages have now been inspected and are results on previously inspected test documents for subsequent changes.


**Features and sequence decoding**

The 33 measurements of selectable PDF text lines cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.

The context classifier uses 47 features: the 43 group features plus style_numbered_count, style_mean_depth, style_max_depth and toc_exact_title. Style statistics group lines by rounded font size, bold/italic and color, then summarize numeric-prefix depth. table-of-contents matching normalizes title text, strips its numeric prefix and dot leaders, and checks exact membership among dot-leader lines. This is a learned input feature, not a hard TOC level override.

The relationship classifier uses 142 features: two 47-feature groups, their differences and page delta. Its 867 training pairs are consecutive annotated headings. Target −1 means the next H number is smaller (shallower), 0 means equal and +1 means larger (deeper). It learns direction, not the number of levels skipped.

First, choosing the highest body-or-heading score decides which predicted groups survive. Viterbi then maximizes the sum of log heading-class probabilities and weighted log relationship probabilities for transitions between retained groups. Transition class is sign(next H − previous H); probabilities are clipped below at 1e-12. Default relation weight is 1.0. This decoder is an algorithm, not a fourth trained model, and cannot recover a group already rejected as body.


**What calibration changes**

Only the body column of a copy of the group-probability array is multiplied by body_weight before choosing the highest-scoring class. Surviving headings still use the original probabilities in Viterbi. This is decision weighting, not statistical probability calibration.

On the four validation reports, body weights 1.0, 1.5 and 2.0 yield group-and-level F1 of 69.8%, 76.9% and 81.1%. All three relationship weights tie at each body weight, so the ordered grid retains relation_weight=1.0. There is no evidence from this grid that a relationship-weight change helped.


**Regression outcome and why this is not promoted**

On the previously inspected 38-heading set, F1 rises from 85.7% to 94.7%: 36 groups remain correctly leveled, false groups fall from 8 to 1, and one genuine group is now missed. This is results on previously inspected test documents, not a new independent test.

On the historical main-table 77 headings, correct title-plus-level matches fall from 50 to 47; matched titles fall from 64 to 59 and false headings from 23 to 21. The candidate therefore remains a separate historical candidate; the current highlighted method is selected using joint F0.5 and the precision gate.


**Deployment and measured scope**

Models are exported as data-only JSON arrays. Exported predict_proba is checked against scikit-learn with atol=1e-7. Runtime inference uses NumPy and float32 tree traversal; it needs no LLM or scikit-learn model server. Full selectable PDF text is retained. Parent IDs are derived from the predicted level stack, not separately learned or evaluated.

The main comparison parses all four historical PDFs (523 pages) on an Apple M4 Pro with 48 GB memory, but scores only 77 headings on 32 audited pages. Its fuzzy title matching plus exact level is different from the supervised exact group-and-level F1. Main-table scores are historical diagnostics, not the fresh supervised split. Timing covers extraction, feature construction and prediction; model-file loading occurs before the parser timer.

The runner accepts a separate calibration file and verifies the recorded model and configuration checksums. No score or inference output is changed by this documentation update.

The models and labels are unchanged. Validation selects a stricter heading decision. Regression on previously inspected pages improves F1 but misses one genuine heading. It is not new independent test evidence.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/calibrate.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Calibration protocol and regression evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-calibration/report.md) · [Exact estimator constructor and JSON export](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Native line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [Group/context/pair features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py) · [Training components and variant selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/train.py) · [Recorded validation scores and training settings](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-v2/evidence/selection.json) · [PDF sources and report splits](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json) · [Reviewable heading annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/annotations.json) · [Inference, grouping and Viterbi](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py) · [Recorded search results and selected decision settings](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-calibration/evidence/selection.json) · [Calibration runner and artifact input](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_structure.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### v2: context + relationships (selected)

Learned classifiers · local CPU

Use three Extra Trees classifiers to join wrapped titles, recognize headings and levels, and compare the levels of neighboring headings. A Viterbi search then chooses a consistent sequence. This was the second experiment’s selected design, with 600 trees in total.


**Training:** Annotate examples in other WFP reports → Train Extra Trees classifiers → Compare designs on validation reports

- **Annotate examples in other WFP reports:** An assistant labels heading text, levels and ordinary body text. The expanded training set contains 887 heading groups in 20 reports; validation and test reports are separate.
- **Train Extra Trees classifiers:** An Extra Trees classifier combines many randomized decision trees. Each tree uses measurements such as font size and spacing to vote for a class. Each component here has 200 trees, maximum depth 16, minimum leaf size 2, balanced classes and seed 42.
- **Compare designs on validation reports:** Use 21 headings in four separate reports to compare the line-only, joined-text and document-context designs. Their original exact group-and-level F1 scores were 55.3%, 63.6% and 69.8%; that earlier selection predates the new F0.5 objective.



**Inference:** Join lines that belong to one title → Recognize headings and propose levels → Compare consecutive headings → Choose levels that work together

- **Join lines that belong to one title:** A 200-tree Extra Trees classifier uses 100 measurements of adjacent lines to decide whether to join them, including across PDF block boundaries.
- **Recognize headings and propose levels:** A second 200-tree Extra Trees classifier uses 47 measurements of each text group and the document’s numbering, styles and table of contents. It scores body text and levels H1–H5.
- **Compare consecutive headings:** A third 200-tree Extra Trees classifier uses 142 measurements to predict whether the next heading is at a higher, equal or deeper level.
- **Choose levels that work together:** Viterbi decoding is a search algorithm that selects the best-scoring sequence of levels using both heading scores and relationship scores. Relationship weight is 1. It is not another trained model.



**Models and terms explained**

- [Extra Trees](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html): A classifier that averages predictions from many randomized decision trees. A tree makes a sequence of decisions about input measurements. This benchmark uses scikit-learn’s ExtraTreesClassifier, with 200 trees per component.
- [Features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py): The numeric measurements supplied to a classifier—for example font size, boldness, line spacing or whether a title occurs in the table of contents. They are calculated from the PDF, not supplied reference answers.
- [Validation reports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json): Reports kept separate from model fitting and used to choose between designs or decision settings. The later inspected test reports are now regression checks: they can expose a failure but no longer provide a fresh independent evaluation.
- [Viterbi decoding](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py): An algorithm for choosing the highest-scoring sequence of heading levels. Here it combines each heading’s own scores with scores for the relationship to the preceding heading. It does not train or add another model.

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

**Training data and annotation source**

A single assistant reviewed source text, layout/page snippets and table-of-contents context and supplied explicit line groups and H levels. The annotation provenance does not record a precise model version used by the annotating assistant, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate reference labels. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The training split contains 20 WFP reports, 887 heading groups and 7,039 labeled lines. Line classes: body=5,849; H1=238; H2=391; H3=432; H4=128; H5=1; H6=0. Negative examples come from 112 fully reviewed training pages. Unmarked lines on positive-only annotation pages are not automatically negatives. The H5/H6 coverage is a material limitation.

Validation uses reports 103, 538, 176 and 128: 21 reference groups on 20 reviewed pages. The test from the second training experiment uses reports 321, 844, 560 and 394: 38 groups on 32 reviewed pages. Splits are by report, not random lines; report-template families are not held out. Those test pages have now been inspected and are results on previously inspected test documents for subsequent changes.


**What each model learns**

The 33 measurements of selectable PDF text lines cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.

The context classifier uses 47 features: the 43 group features plus style_numbered_count, style_mean_depth, style_max_depth and toc_exact_title. Style statistics group lines by rounded font size, bold/italic and color, then summarize numeric-prefix depth. table-of-contents matching normalizes title text, strips its numeric prefix and dot leaders, and checks exact membership among dot-leader lines. This is a learned input feature, not a hard TOC level override.

The relationship classifier uses 142 features: two 47-feature groups, their differences and page delta. Its 867 training pairs are consecutive annotated headings. Target −1 means the next H number is smaller (shallower), 0 means equal and +1 means larger (deeper). It learns direction, not the number of levels skipped.


**Sequence decoding**

First, choosing the highest body-or-heading score decides which predicted groups survive. Viterbi then maximizes the sum of log heading-class probabilities and weighted log relationship probabilities for transitions between retained groups. Transition class is sign(next H − previous H); probabilities are clipped below at 1e-12. Default relation weight is 1.0. This decoder is an algorithm, not a fourth trained model, and cannot recover a group already rejected as body.


**Selection, not a tree-parameter search**

We compared three pipeline variants, with identical fixed tree settings. Validation exact group-and-level F1 was 55.3% for expanded_line, 63.6% for learned_groups and 69.8% for context_relations. The highest validation F1 selected context_relations before the test from the second training experiment. Selection did not use the historical main-table results. F1 = 2 × exact group-and-level matches / (gold groups + predicted groups); group matching requires identical source-line membership.

The original separate 38-heading v2 test achieved 85.7% exact group-and-level F1: 38 matched groups, 36 correctly leveled and 8 additional false groups. That small test is distinct from the historical 77-heading table.


**Deployment and timing**

Models are exported as data-only JSON arrays. Exported predict_proba is checked against scikit-learn with atol=1e-7. Runtime inference uses NumPy and float32 tree traversal; it needs no LLM or scikit-learn model server. Full selectable PDF text is retained. Parent IDs are derived from the predicted level stack, not separately learned or evaluated.

The main comparison parses all four historical PDFs (523 pages) on an Apple M4 Pro with 48 GB memory, but scores only 77 headings on 32 audited pages. Its fuzzy title matching plus exact level is different from the supervised exact group-and-level F1. Main-table scores are historical diagnostics, not the fresh supervised split. Timing covers extraction, feature construction and prediction; model-file loading occurs before the parser timer.

No LLM is needed at inference. Labels are assistant-assisted, not independently human-verified. Parent links are inferred, not evaluated. v2 main-table scores are historical diagnostics; the separate 38-heading pilot has a different metric.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Exact estimator constructor and JSON export](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Native line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [Group/context/pair features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py) · [Training components and variant selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/train.py) · [Recorded validation scores and training settings](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-v2/evidence/selection.json) · [PDF sources and report splits](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json) · [Reviewable heading annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/annotations.json) · [Inference, grouping and Viterbi](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py) · [Configuration source / evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md)


### LightOnOCR-3-0.8B / MLX

Page vision model · local MLX

LightOnOCR-3-0.8B reads one page image at a time and returns text with locations on the page. We extract its title blocks and use any Markdown heading markers to determine the level.


**Inference:** Make images of the 32 audit pages → Request text with locations → Read the reported title blocks → Join wrapped titles and read levels

- **Make images of the 32 audit pages:** Render at 400 dots per inch, then shrink each image so its longest side is at most 2048 pixels.
- **Request text with locations:** Run LightOnOCR-3-0.8B through MLX using the “grounding” prompt, which asks the model to associate content with page regions. Disable thinking; use temperature=0 and at most 8192 output tokens.
- **Read the reported title blocks:** The model marks titles and supplies bounding boxes—the rectangles locating them on the page.
- **Join wrapped titles and read levels:** A title+ block continues the previous title. Count any leading # characters to obtain its level; retain an unknown level when none is supplied.



**Models and terms explained**

- [LightOnOCR-3-0.8B](https://huggingface.co/lightonai/LightOnOCR-3-0.8B): A document image-reading model with approximately 0.8 billion parameters. Its output includes text and page regions.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.
- [Grounding](https://huggingface.co/lightonai/LightOnOCR-3-0.8B): Returning text together with the page regions it refers to. In these OCR runs, the response locates title blocks; a location alone does not establish a heading’s level.

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

LightOnOCR-3-4B reads page images and returns text with page locations, using the same output convention as the 0.8-billion-parameter model. This run processes two independent pages together using bf16 weights, with five saved outputs from an earlier single-page run.


**Inference:** Render each audit page → Process two pages together → Include five earlier outputs → Extract titles and their levels

- **Render each audit page:** Render at 400 dots per inch and shrink to a maximum 2048-pixel side. Each page is a separate input; batching does not share context.
- **Process two pages together:** Run LightOnOCR-3-4B through MLX with bf16 weights, the “grounding” prompt, temperature=0 and a 12,384-token output limit.
- **Include five earlier outputs:** The published run retained five already completed single-page results. Those used a 12,288-token limit; it was not a clean rerun of all pages with one batch setting.
- **Extract titles and their levels:** Join title+ continuation blocks, read Markdown # levels where supplied, and retain page numbers and bounding boxes.



**Models and terms explained**

- [LightOnOCR-3-4B](https://huggingface.co/lightonai/LightOnOCR-3-4B): The four-billion-parameter document image-reading model used in this run.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.
- [bf16](https://ml-explore.github.io/mlx/build/html/python/data_types.html): A 16-bit floating-point number format used for model weights and calculations. It is a numerical format, not a particular model or training technique.
- [Grounding](https://huggingface.co/lightonai/LightOnOCR-3-0.8B): Returning text together with the page regions it refers to. In these OCR runs, the response locates title blocks; a location alone does not establish a heading’s level.

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

Learned classifiers · local CPU

Train two Extra Trees classifiers: one decides which neighboring lines belong to the same heading, and one labels the resulting text groups as body text or H1–H5. This tests whether learning how to join wrapped titles helps; it uses 400 trees in total.


**Training:** Annotate examples in other WFP reports → Train Extra Trees classifiers → Compare designs on validation reports

- **Annotate examples in other WFP reports:** An assistant labels heading text, levels and ordinary body text. The expanded training set contains 887 heading groups in 20 reports; validation and test reports are separate.
- **Train Extra Trees classifiers:** An Extra Trees classifier combines many randomized decision trees. Each tree uses measurements such as font size and spacing to vote for a class. Each component here has 200 trees, maximum depth 16, minimum leaf size 2, balanced classes and seed 42.
- **Compare designs on validation reports:** Use 21 headings in four separate reports to compare the line-only, joined-text and document-context designs. Their original exact group-and-level F1 scores were 55.3%, 63.6% and 69.8%; that earlier selection predates the new F0.5 objective.



**Inference:** Decide whether neighboring lines belong together → Build complete title groups → Classify the joined text → Choose each group’s level independently

- **Decide whether neighboring lines belong together:** A 200-tree Extra Trees classifier uses 100 measurements of the two lines, their differences and their page separation to predict join or separate.
- **Build complete title groups:** Join predicted continuations even across PDF block boundaries. Keep the IDs of the original lines so every group can be traced to the PDF.
- **Classify the joined text:** A second 200-tree Extra Trees classifier uses 43 text-and-style measurements to choose body text or H1–H5.
- **Choose each group’s level independently:** Take the highest-scoring class. This variant does not use table-of-contents clues or the predicted relationships between headings.



**Models and terms explained**

- [Extra Trees](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html): A classifier that averages predictions from many randomized decision trees. A tree makes a sequence of decisions about input measurements. This benchmark uses scikit-learn’s ExtraTreesClassifier, with 200 trees per component.
- [Features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py): The numeric measurements supplied to a classifier—for example font size, boldness, line spacing or whether a title occurs in the table of contents. They are calculated from the PDF, not supplied reference answers.
- [Validation reports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json): Reports kept separate from model fitting and used to choose between designs or decision settings. The later inspected test reports are now regression checks: they can expose a failure but no longer provide a fresh independent evaluation.

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

A single assistant reviewed source text, layout/page snippets and table-of-contents context and supplied explicit line groups and H levels. The annotation provenance does not record a precise model version used by the annotating assistant, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate reference labels. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The training split contains 20 WFP reports, 887 heading groups and 7,039 labeled lines. Line classes: body=5,849; H1=238; H2=391; H3=432; H4=128; H5=1; H6=0. Negative examples come from 112 fully reviewed training pages. Unmarked lines on positive-only annotation pages are not automatically negatives. The H5/H6 coverage is a material limitation.

Validation uses reports 103, 538, 176 and 128: 21 reference groups on 20 reviewed pages. The test from the second training experiment uses reports 321, 844, 560 and 394: 38 groups on 32 reviewed pages. Splits are by report, not random lines; report-template families are not held out. Those test pages have now been inspected and are results on previously inspected test documents for subsequent changes.


**Join and group targets**

The 33 measurements of selectable PDF text lines cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.

An adjacent pair is positive only if both lines belong to the same explicit annotated heading. Only pairs with known labels on both lines are trained. Pair features concatenate A, B, B−A and page difference: 3×33+1=100.

The group classifier trains on 887 annotated heading groups plus 5,849 reviewed singleton body lines. Its 43 features start from the 33 line features, recompute text indicators on the joined title, use the last line’s following gap, and add group length/page span plus mean/max size, bold, italic and width. Inference uses predicted groups, so join errors can propagate into classification.


**Selection and deployment**

We compared three pipeline variants, with identical fixed tree settings. Validation exact group-and-level F1 was 55.3% for expanded_line, 63.6% for learned_groups and 69.8% for context_relations. The highest validation F1 selected context_relations before the test from the second training experiment. Selection did not use the historical main-table results. F1 = 2 × exact group-and-level matches / (gold groups + predicted groups); group matching requires identical source-line membership.

Models are exported as data-only JSON arrays. Exported predict_proba is checked against scikit-learn with atol=1e-7. Runtime inference uses NumPy and float32 tree traversal; it needs no LLM or scikit-learn model server. Full selectable PDF text is retained. Parent IDs are derived from the predicted level stack, not separately learned or evaluated.

The main comparison parses all four historical PDFs (523 pages) on an Apple M4 Pro with 48 GB memory, but scores only 77 headings on 32 audited pages. Its fuzzy title matching plus exact level is different from the supervised exact group-and-level F1. Main-table scores are historical diagnostics, not the fresh supervised split. Timing covers extraction, feature construction and prediction; model-file loading occurs before the parser timer.

No LLM is needed at inference. Labels are assistant-assisted, not independently human-verified. Parent links are inferred, not evaluated. v2 main-table scores are historical diagnostics; the separate 38-heading pilot has a different metric.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Exact estimator constructor and JSON export](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Native line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [Group/context/pair features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py) · [Training components and variant selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/train.py) · [Recorded validation scores and training settings](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-v2/evidence/selection.json) · [PDF sources and report splits](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json) · [Reviewable heading annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/annotations.json) · [Inference, grouping and Viterbi](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py) · [Configuration source / evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md)


### v2: more annotations

Learned classifiers · local CPU

Test whether more labeled examples improve the original single-classifier design. The same Extra Trees approach now learns from 887 heading groups in 20 reports; heading lines are still joined using their PDF text blocks.


**Training:** Annotate examples in other WFP reports → Train Extra Trees classifiers → Compare designs on validation reports

- **Annotate examples in other WFP reports:** An assistant labels heading text, levels and ordinary body text. The expanded training set contains 887 heading groups in 20 reports; validation and test reports are separate.
- **Train Extra Trees classifiers:** An Extra Trees classifier combines many randomized decision trees. Each tree uses measurements such as font size and spacing to vote for a class. Each component here has 200 trees, maximum depth 16, minimum leaf size 2, balanced classes and seed 42.
- **Compare designs on validation reports:** Use 21 headings in four separate reports to compare the line-only, joined-text and document-context designs. Their original exact group-and-level F1 scores were 55.3%, 63.6% and 69.8%; that earlier selection predates the new F0.5 objective.



**Inference:** Train on the expanded examples → Classify each new line → Join lines using PDF blocks → Keep the simpler design

- **Train on the expanded examples:** Fit a 200-tree Extra Trees classifier on 7,039 labeled lines, using 33 measurements per line.
- **Classify each new line:** Predict scores for ordinary body text and H1–H5. Choose the class with the highest score.
- **Join lines using PDF blocks:** Merge adjacent same-level heading lines only inside the same source PDF block. No model learns how to join lines in this variant.
- **Keep the simpler design:** Do not add table-of-contents context or a model for relationships between headings. Validation group-and-level F1 was 55.3%.



**Models and terms explained**

- [Extra Trees](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html): A classifier that averages predictions from many randomized decision trees. A tree makes a sequence of decisions about input measurements. This benchmark uses scikit-learn’s ExtraTreesClassifier, with 200 trees per component.
- [Features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py): The numeric measurements supplied to a classifier—for example font size, boldness, line spacing or whether a title occurs in the table of contents. They are calculated from the PDF, not supplied reference answers.
- [Validation reports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json): Reports kept separate from model fitting and used to choose between designs or decision settings. The later inspected test reports are now regression checks: they can expose a failure but no longer provide a fresh independent evaluation.

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

A single assistant reviewed source text, layout/page snippets and table-of-contents context and supplied explicit line groups and H levels. The annotation provenance does not record a precise model version used by the annotating assistant, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate reference labels. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The training split contains 20 WFP reports, 887 heading groups and 7,039 labeled lines. Line classes: body=5,849; H1=238; H2=391; H3=432; H4=128; H5=1; H6=0. Negative examples come from 112 fully reviewed training pages. Unmarked lines on positive-only annotation pages are not automatically negatives. The H5/H6 coverage is a material limitation.

Validation uses reports 103, 538, 176 and 128: 21 reference groups on 20 reviewed pages. The test from the second training experiment uses reports 321, 844, 560 and 394: 38 groups on 32 reviewed pages. Splits are by report, not random lines; report-template families are not held out. Those test pages have now been inspected and are results on previously inspected test documents for subsequent changes.


**Features and grouping**

The 33 measurements of selectable PDF text lines cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.

Line classification uses the largest class probability. The original grouping combines adjacent heading lines only when their PDF block and predicted level agree. There is no learned line-joining model, group classifier or Viterbi stage in this comparison.


**Selection and deployment**

We compared three pipeline variants, with identical fixed tree settings. Validation exact group-and-level F1 was 55.3% for expanded_line, 63.6% for learned_groups and 69.8% for context_relations. The highest validation F1 selected context_relations before the test from the second training experiment. Selection did not use the historical main-table results. F1 = 2 × exact group-and-level matches / (gold groups + predicted groups); group matching requires identical source-line membership.

Models are exported as data-only JSON arrays. Exported predict_proba is checked against scikit-learn with atol=1e-7. Runtime inference uses NumPy and float32 tree traversal; it needs no LLM or scikit-learn model server. Full selectable PDF text is retained. Parent IDs are derived from the predicted level stack, not separately learned or evaluated.

The main comparison parses all four historical PDFs (523 pages) on an Apple M4 Pro with 48 GB memory, but scores only 77 headings on 32 audited pages. Its fuzzy title matching plus exact level is different from the supervised exact group-and-level F1. Main-table scores are historical diagnostics, not the fresh supervised split. Timing covers extraction, feature construction and prediction; model-file loading occurs before the parser timer.

No LLM is needed at inference. Labels are assistant-assisted, not independently human-verified. Parent links are inferred, not evaluated. v2 main-table scores are historical diagnostics; the separate 38-heading pilot has a different metric.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Exact estimator constructor and JSON export](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Native line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [Group/context/pair features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py) · [Training components and variant selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/train.py) · [Recorded validation scores and training settings](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-v2/evidence/selection.json) · [PDF sources and report splits](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json) · [Reviewable heading annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/annotations.json) · [Inference, grouping and Viterbi](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py) · [Configuration source / evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md)


### Supervised Extra Trees / CPU / assistant labels

Learned classifiers · local CPU

Train one Extra Trees classifier to decide whether each PDF text line is body text or a heading at a particular level. Extra Trees combines votes from many randomized decision trees. An assistant supplied training labels; no language model runs when a new PDF is parsed.


**Training:** Label training examples → Compare two classifiers → Choose the validation winner

- **Label training examples:** An assistant annotated 154 heading groups from 16 training reports. Separate reports were reserved for validation and testing.
- **Compare two classifiers:** Fit scaled LogisticRegression(C=1), a linear classifier, and a 200-tree Extra Trees classifier using fixed settings.
- **Choose the validation winner:** Extra Trees scored 69.1% exact-level line F1 versus 47.6% for logistic regression. Save the winning trained classifier without fitting it on the benchmark PDFs.



**Inference:** Measure each text line → Classify the line → Join wrapped heading lines → Export text and the outline

- **Measure each text line:** PyMuPDF reads the selectable text and 33 measurements, including font size, position, spacing and text patterns.
- **Classify the line:** A scikit-learn ExtraTreesClassifier with 200 trees predicts body text or a heading level. Each tree is limited to depth 16 and at least two training examples per leaf.
- **Join wrapped heading lines:** Merge adjacent heading lines with the same predicted level only when they are in the same PDF text block.
- **Export text and the outline:** Keep source lines and page numbers. Record each heading’s level and infer its parent from the preceding heading levels.



**Models and terms explained**

- [Extra Trees](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html): A classifier that averages predictions from many randomized decision trees. A tree makes a sequence of decisions about input measurements. This benchmark uses scikit-learn’s ExtraTreesClassifier, with 200 trees per component.
- [Features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py): The numeric measurements supplied to a classifier—for example font size, boldness, line spacing or whether a title occurs in the table of contents. They are calculated from the PDF, not supplied reference answers.
- [Validation reports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json): Reports kept separate from model fitting and used to choose between designs or decision settings. The later inspected test reports are now regression checks: they can expose a failure but no longer provide a fresh independent evaluation.

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

A single assistant reviewed source text, layout/page snippets and table-of-contents context and supplied explicit line groups and H levels. The annotation provenance does not record a precise model version used by the annotating assistant, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate reference labels. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The 33 measurements of selectable PDF text lines cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.


**What was actually tuned**

Two estimator families were compared using validation exact-level LINE F1: logistic regression 47.6%, Extra Trees 69.1%. Tree parameters and logistic C were fixed, not searched. Validation contains 21 heading groups across four reports; the separate v1 test contains 27 groups across four reports.

The v1 test scored 82.0% exact-level line F1 and 22/27 complete heading groups at the right level. This differs from the v2 group-F1 metric. The v1 training set was expanded with additional reviewed training pages before the reported selection/test; it is smaller than the later 887-group v2 set.


**Export and measured scope**

Models are exported as data-only JSON arrays. Exported predict_proba is checked against scikit-learn with atol=1e-7. Runtime inference uses NumPy and float32 tree traversal; it needs no LLM or scikit-learn model server. Full selectable PDF text is retained. Parent IDs are derived from the predicted level stack, not separately learned or evaluated.

The main comparison parses all four historical PDFs (523 pages) on an Apple M4 Pro with 48 GB memory, but scores only 77 headings on 32 audited pages. Its fuzzy title matching plus exact level is different from the supervised exact group-and-level F1. Main-table scores are historical diagnostics, not the fresh supervised split. Timing covers extraction, feature construction and prediction; model-file loading occurs before the parser timer.

Assistant-produced labels lack independent adjudication. V1 selection uses line F1, not v2 group F1. Same-block grouping can split multi-block headings; parent edges are inferred and unscored.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/supervised/compare.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Estimator definitions](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [V1 training and selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/supervised/train.py) · [V1 validation evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/supervised/evidence/selection.json) · [V1 corpus and source URLs](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/supervised/corpus.json) · [Grouping and parent inference](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_inference.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py) · [Configuration source / evidence](https://github.com/dividor/pdf-heading-benchmark/blob/main/src/pdf_heading_benchmark/supervised_models.py)


### MinerU 4.2.3 basic CPU

Layout parser · CPU

MinerU 4.2.3 uses its basic PDF parser on the CPU through ONNX Runtime. We keep the titles and levels it returns without asking another model to repair them. This is a different implementation from the MinerU Pro image model.


**Inference:** Run the basic CPU parser → Process every PDF page → Collect detected titles → Keep the supplied hierarchy

- **Run the basic CPU parser:** Set small_backend="onnx" and onnx_device="cpu". ONNX Runtime executes the parser’s model on the CPU.
- **Process every PDF page:** Use MinerUParser with parse_mode="auto", page_range="all" and image_analysis=False.
- **Collect detected titles:** Read the parser’s document-title and paragraph-title blocks: DocTitleBlock and ParagraphTitleBlock.
- **Keep the supplied hierarchy:** Export the block’s text, level and bounding box. No extra level classifier or document-specific repair is applied.



**Models and terms explained**

- [MinerU](https://github.com/opendatalab/MinerU): Document parsing software; this row uses its basic CPU parser, not the separate Pro image model.
- [ONNX Runtime](https://onnxruntime.ai/docs/): Software that executes a model saved in the ONNX format. The basic MinerU run uses it on the CPU.

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

Ask Qwen3.5-4B to assign levels to possible headings extracted by Docling and PyMuPDF4LLM. The model receives titles and page numbers for the whole document, but no page images or parser-supplied levels. It runs locally through MLX using 4-bit weights.


**Inference:** Collect possible headings → Give each title a reference ID → Ask Qwen to assign levels → Validate the reply

- **Collect possible headings:** Combine headings proposed by both parsers. Merge same-page titles with normalized similarity of at least 0.90.
- **Give each title a reference ID:** Send one list per document containing IDs such as h0000, title text and page number. An ID lets the reply refer unambiguously to an input title.
- **Ask Qwen to assign levels:** Use Qwen3.5-4B with temperature=0, max_tokens=4096, seed=42 and thinking disabled. These are fixed generation settings, not training.
- **Validate the reply:** Require a JSON mapping from every supplied ID to a level 1–20 or null. Null means rejected as a heading. Invalid replies are rejected rather than silently repaired.



**Models and terms explained**

- [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B): A pretrained language model with approximately four billion parameters. Here it reads lists of possible headings and assigns levels.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.
- [4-bit / 8-bit weights](https://github.com/ml-explore/mlx-lm): Reduced-precision representations of a model’s learned numbers, used to lower memory requirements. The number describes storage precision, not heading depth or model accuracy.

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

The same PROMPT is used for each report. It asks for logical hierarchy, treats executive summaries/main sections/annexes as top level, rejects captions, table cells, running headers, emphasis and TOC entries, and requires consistent parallel sections. Cover text must not shift body levels; absolute page number must not determine level. The complete prompt is linked in the runner.

The decoder strips a code-fence wrapper, then validates every ID and value. Accepted IDs are joined back to their original titles and pages; null rejects a candidate. A missing source title cannot be created by this method. Invalid responses are recorded as errors and yield no accepted headings for that document.


**Measured scope and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

Reported time covers the hierarchy-generation stage only. Candidate extraction and model loading/download are excluded; end-to-end deployment must also pay for the source parser.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

A missing candidate cannot be recovered by this refinement. JSON is validated; invalid replies are not silently repaired.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) · [Base model / Hugging Face](https://huggingface.co/Qwen/Qwen3.5-4B) · [Tested 4-bit model / HF](https://huggingface.co/mlx-community/Qwen3.5-4B-MLX-4bit) · [Exact PROMPT, sampling and validation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_ids.py) · [Model revision pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Candidate union and order preservation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/build_union.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### Qwen3.5-4B / PyMuPDF candidates

Text-only LLM refinement · local MLX

Ask Qwen3.5-4B to assign levels to possible headings extracted by PyMuPDF4LLM. The model receives titles and page numbers for the whole document, but no page images or parser-supplied levels. It runs locally through MLX using 4-bit weights.


**Inference:** Collect possible headings → Give each title a reference ID → Ask Qwen to assign levels → Validate the reply

- **Collect possible headings:** Use the headings marked in PyMuPDF4LLM’s Markdown for the full PDF.
- **Give each title a reference ID:** Send one list per document containing IDs such as h0000, title text and page number. An ID lets the reply refer unambiguously to an input title.
- **Ask Qwen to assign levels:** Use Qwen3.5-4B with temperature=0, max_tokens=4096, seed=42 and thinking disabled. These are fixed generation settings, not training.
- **Validate the reply:** Require a JSON mapping from every supplied ID to a level 1–20 or null. Null means rejected as a heading. Invalid replies are rejected rather than silently repaired.



**Models and terms explained**

- [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B): A pretrained language model with approximately four billion parameters. Here it reads lists of possible headings and assigns levels.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.
- [4-bit / 8-bit weights](https://github.com/ml-explore/mlx-lm): Reduced-precision representations of a model’s learned numbers, used to lower memory requirements. The number describes storage precision, not heading depth or model accuracy.

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

The same PROMPT is used for each report. It asks for logical hierarchy, treats executive summaries/main sections/annexes as top level, rejects captions, table cells, running headers, emphasis and TOC entries, and requires consistent parallel sections. Cover text must not shift body levels; absolute page number must not determine level. The complete prompt is linked in the runner.

The decoder strips a code-fence wrapper, then validates every ID and value. Accepted IDs are joined back to their original titles and pages; null rejects a candidate. A missing source title cannot be created by this method. Invalid responses are recorded as errors and yield no accepted headings for that document.


**Measured scope and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

Reported time covers the hierarchy-generation stage only. Candidate extraction and model loading/download are excluded; end-to-end deployment must also pay for the source parser.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

A missing candidate cannot be recovered by this refinement. JSON is validated; invalid replies are not silently repaired.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) · [Base model / Hugging Face](https://huggingface.co/Qwen/Qwen3.5-4B) · [Tested 4-bit model / HF](https://huggingface.co/mlx-community/Qwen3.5-4B-MLX-4bit) · [Exact PROMPT, sampling and validation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_ids.py) · [Model revision pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Candidate parser](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_pymupdf4llm.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### PyMuPDF4LLM 2.1

Native PDF parser · CPU

PyMuPDF4LLM 2.1 turns the PDF’s existing text into Markdown. We treat its #, ## and subsequent heading markers as H1, H2 and deeper levels; no language model makes a second decision.


**Inference:** Read the complete PDF → Convert one page at a time → Read Markdown headings → Keep text and page numbers

- **Read the complete PDF:** Use the PDF’s selectable text, fonts and layout rather than recognizing text from images.
- **Convert one page at a time:** Run to_markdown with page_chunks=True and use_ocr=False. Each output keeps its original PDF page number.
- **Read Markdown headings:** A line starting with # is H1; ## is H2, and so on through H6. We do not add a custom font-size threshold.
- **Keep text and page numbers:** Export heading titles and levels together with the Markdown text and the original page numbers.



**Models and terms explained**

- [PyMuPDF4LLM](https://github.com/pymupdf/pymupdf4llm): A library that converts PDF text and layout into Markdown, including heading markers.

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

Ask Qwen3.5-4B to assign levels to possible headings extracted by MinerU’s basic parser. The model receives titles and page numbers for the whole document, but no page images or parser-supplied levels. It runs locally through MLX using 4-bit weights.


**Inference:** Collect possible headings → Give each title a reference ID → Ask Qwen to assign levels → Validate the reply

- **Collect possible headings:** Use the document-title and paragraph-title blocks proposed by MinerU across the full PDF.
- **Give each title a reference ID:** Send one list per document containing IDs such as h0000, title text and page number. An ID lets the reply refer unambiguously to an input title.
- **Ask Qwen to assign levels:** Use Qwen3.5-4B with temperature=0, max_tokens=4096, seed=42 and thinking disabled. These are fixed generation settings, not training.
- **Validate the reply:** Require a JSON mapping from every supplied ID to a level 1–20 or null. Null means rejected as a heading. Invalid replies are rejected rather than silently repaired.



**Models and terms explained**

- [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B): A pretrained language model with approximately four billion parameters. Here it reads lists of possible headings and assigns levels.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.
- [4-bit / 8-bit weights](https://github.com/ml-explore/mlx-lm): Reduced-precision representations of a model’s learned numbers, used to lower memory requirements. The number describes storage precision, not heading depth or model accuracy.

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

The same PROMPT is used for each report. It asks for logical hierarchy, treats executive summaries/main sections/annexes as top level, rejects captions, table cells, running headers, emphasis and TOC entries, and requires consistent parallel sections. Cover text must not shift body levels; absolute page number must not determine level. The complete prompt is linked in the runner.

The decoder strips a code-fence wrapper, then validates every ID and value. Accepted IDs are joined back to their original titles and pages; null rejects a candidate. A missing source title cannot be created by this method. Invalid responses are recorded as errors and yield no accepted headings for that document.


**Measured scope and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

Reported time covers the hierarchy-generation stage only. Candidate extraction and model loading/download are excluded; end-to-end deployment must also pay for the source parser.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

A missing candidate cannot be recovered by this refinement. JSON is validated; invalid replies are not silently repaired.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) · [Base model / Hugging Face](https://huggingface.co/Qwen/Qwen3.5-4B) · [Tested 4-bit model / HF](https://huggingface.co/mlx-community/Qwen3.5-4B-MLX-4bit) · [Exact PROMPT, sampling and validation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_ids.py) · [Model revision pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Candidate parser](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_mineru.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### Docling fixed tolerance 0.15

Layout parser · CPU

Use Docling 2.151.1 with a fixed font-style tolerance of 0.15 in its hierarchy step. This setting was applied to every report; it was an exploratory choice, not a demonstrated best setting.


**Inference:** Read the text and page layout → Keep each item’s location → Change the style tolerance → Export headings and levels

- **Read the text and page layout:** Process the full PDF on the CPU with eight threads. Optical character recognition (OCR) and table reconstruction are disabled because these PDFs already contain selectable text.
- **Keep each item’s location:** Save parsed page information, including text positions, so the hierarchy step can inspect layout. The code option is generate_parsed_pages=True.
- **Change the style tolerance:** Set style_size_tolerance=0.15 in HeadingHierarchyModel. Start from the original conversion so this is not a second refinement of the default hierarchy result.
- **Export headings and levels:** Save each heading’s text, supplied H level, PDF page and bounding box—the rectangle around its text.



**Models and terms explained**

- [Docling](https://github.com/docling-project/docling): PDF conversion software used here to identify section headings and read or infer their levels.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Package | docling==2.151.1 |
| Device / parallelism | CPU; num_threads=8 |
| Conversion | do_ocr=False; do_table_structure=False; generate_parsed_pages=True |
| Hierarchy | enabled=True; style_size_tolerance=0.15; other settings use library defaults |
| Model provenance | Package-managed layout models; the runner does not explicitly pin individual layout-model revisions. |

**What changed and how it was selected**

Use Docling 2.151.1 with a fixed font-style tolerance of 0.15 in its hierarchy step. This setting was applied to every report; it was an exploratory choice, not a demonstrated best setting.

These are fixed configurations, not a learned WFP-specific correction or a recorded hyperparameter search. The tolerance variant is exploratory; “tuned” in its historical row name should not be read as a validated optimum.


**Output and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

The variants share one base conversion. Its recorded time includes first model load/download. The ordinary hierarchy pass has a separate timer; the tolerance pass was not separately timed. Their table times therefore do not represent three independent end-to-end conversions.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

These variants share detected blocks. A hierarchy stage cannot recover a heading absent from its inputs. The tolerance variant is exploratory.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) · [Project / GitHub](https://github.com/docling-project/docling) · [Docling technical report (2024)](https://arxiv.org/abs/2408.09869) · [Conversion and both hierarchy passes](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_docling.py) · [Pinned environment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/docling.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### Marker 2.2 no OCR/LLM

Layout parser · CPU

Marker 2.2 parses the complete PDF locally on the CPU. We read the levels from HTML heading tags in the blocks Marker identifies as section headings; OCR and language-model assistance are disabled.


**Inference:** Load Marker’s local models → Read the PDF’s existing text → Find section-heading blocks → Preserve unknown levels

- **Load Marker’s local models:** Use create_model_dict(device="cpu", no_server=True). Model inference runs on this machine.
- **Read the PDF’s existing text:** Convert the full document with JSONRenderer, no_ocr mode and use_llm=False.
- **Find section-heading blocks:** Inspect each SectionHeader block. HTML tags such as <h1> and <h2> specify its heading level.
- **Preserve unknown levels:** If Marker identifies a title but supplies no heading tag, keep its text with an unknown level. Do not guess a replacement.



**Models and terms explained**

- [Marker](https://github.com/datalab-to/marker): Document conversion software. This run uses its local models on the CPU and reads heading tags from the output.

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

Use the heading levels returned by Docling 2.151.1 when it first reads the PDF. No additional step changes the hierarchy.


**Inference:** Read the text and page layout → Keep each item’s location → Keep Docling’s original levels → Export headings and levels

- **Read the text and page layout:** Process the full PDF on the CPU with eight threads. Optical character recognition (OCR) and table reconstruction are disabled because these PDFs already contain selectable text.
- **Keep each item’s location:** Save parsed page information, including text positions, so the hierarchy step can inspect layout. The code option is generate_parsed_pages=True.
- **Keep Docling’s original levels:** Read the level attached to each detected section heading directly from Docling’s conversion output.
- **Export headings and levels:** Save each heading’s text, supplied H level, PDF page and bounding box—the rectangle around its text.



**Models and terms explained**

- [Docling](https://github.com/docling-project/docling): PDF conversion software used here to identify section headings and read or infer their levels.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Package | docling==2.151.1 |
| Device / parallelism | CPU; num_threads=8 |
| Conversion | do_ocr=False; do_table_structure=False; generate_parsed_pages=True |
| Hierarchy | No explicit HeadingHierarchyModel pass |
| Model provenance | Package-managed layout models; the runner does not explicitly pin individual layout-model revisions. |

**What changed and how it was selected**

Use the heading levels returned by Docling 2.151.1 when it first reads the PDF. No additional step changes the hierarchy.

These are fixed configurations, not a learned WFP-specific correction or a recorded hyperparameter search. The tolerance variant is exploratory; “tuned” in its historical row name should not be read as a validated optimum.


**Output and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

The variants share one base conversion. Its recorded time includes first model load/download. The ordinary hierarchy pass has a separate timer; the tolerance pass was not separately timed. Their table times therefore do not represent three independent end-to-end conversions.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

These variants share detected blocks. A hierarchy stage cannot recover a heading absent from its inputs. The tolerance variant is exploratory.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) · [Project / GitHub](https://github.com/docling-project/docling) · [Docling technical report (2024)](https://arxiv.org/abs/2408.09869) · [Conversion and both hierarchy passes](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_docling.py) · [Pinned environment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/docling.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### Docling built-in hierarchy

Layout parser · CPU

Use Docling 2.151.1 to find headings, then run its built-in HeadingHierarchyModel to assign their levels. This tests whether Docling’s extra hierarchy step improves the same detected headings.


**Inference:** Read the text and page layout → Keep each item’s location → Assign levels in a second pass → Export headings and levels

- **Read the text and page layout:** Process the full PDF on the CPU with eight threads. Optical character recognition (OCR) and table reconstruction are disabled because these PDFs already contain selectable text.
- **Keep each item’s location:** Save parsed page information, including text positions, so the hierarchy step can inspect layout. The code option is generate_parsed_pages=True.
- **Assign levels in a second pass:** Run Docling’s HeadingHierarchyModel on the detected headings, using its default enabled options.
- **Export headings and levels:** Save each heading’s text, supplied H level, PDF page and bounding box—the rectangle around its text.



**Models and terms explained**

- [Docling](https://github.com/docling-project/docling): PDF conversion software used here to identify section headings and read or infer their levels.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Package | docling==2.151.1 |
| Device / parallelism | CPU; num_threads=8 |
| Conversion | do_ocr=False; do_table_structure=False; generate_parsed_pages=True |
| Hierarchy | HeadingHierarchyOptions(enabled=True); other hierarchy settings use library defaults |
| Model provenance | Package-managed layout models; the runner does not explicitly pin individual layout-model revisions. |

**What changed and how it was selected**

Use Docling 2.151.1 to find headings, then run its built-in HeadingHierarchyModel to assign their levels. This tests whether Docling’s extra hierarchy step improves the same detected headings.

These are fixed configurations, not a learned WFP-specific correction or a recorded hyperparameter search. The tolerance variant is exploratory; “tuned” in its historical row name should not be read as a validated optimum.


**Output and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

The variants share one base conversion. Its recorded time includes first model load/download. The ordinary hierarchy pass has a separate timer; the tolerance pass was not separately timed. Their table times therefore do not represent three independent end-to-end conversions.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

These variants share detected blocks. A hierarchy stage cannot recover a heading absent from its inputs. The tolerance variant is exploratory.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) · [Project / GitHub](https://github.com/docling-project/docling) · [Docling technical report (2024)](https://arxiv.org/abs/2408.09869) · [Conversion and both hierarchy passes](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_docling.py) · [Pinned environment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/docling.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


### Popo + Docling / experimental MLX 8-bit

Visual hierarchy post-processing · local MLX

Use MinerU-Popo to assign levels to headings first detected by Docling. This is an experimental local adaptation: model weights were converted to 8-bit MLX, and predictions from overlapping groups of page images were reconciled.


**Inference:** Find possible titles with Docling → Arrange eight pages for the model → Ask MinerU-Popo for heading levels → Reconcile the repeated page

- **Find possible titles with Docling:** Collect section-header text and its page rectangle. Skip content inside picture and table blocks.
- **Arrange eight pages for the model:** Use the author’s adaptive_chunk routine and bordered image mosaics—several page images arranged together—with one page repeated between consecutive groups.
- **Ask MinerU-Popo for heading levels:** Run the “Title Level Analysis” prompt with title IDs, pages, boxes and text. Use 8-bit weights through MLX and max_tokens=8192.
- **Reconcile the repeated page:** Apply the author’s output-reading and overlap-alignment code to make levels agree across page groups. Map answers back to source title IDs; reject negative level labels.



**Models and terms explained**

- [MinerU-Popo](https://github.com/opendatalab/MinerU-Popo): A model and supporting code for assigning levels to document titles. This benchmark uses an experimental MLX adaptation.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.
- [4-bit / 8-bit weights](https://github.com/ml-explore/mlx-lm): Reduced-precision representations of a model’s learned numbers, used to lower memory requirements. The number describes storage precision, not heading depth or model accuracy.

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

MinerU2.5-Pro-2605-1.2B reads the layout and text of page images. Its tested two_step_extract interface found title blocks but supplied no heading levels, so it earns no credit for complete title-and-level answers.


**Inference:** Render the 32 audit pages → Process one image at a time → Read layout, then content → Record the missing hierarchy

- **Render the 32 audit pages:** Render at 400 dots per inch and shrink to at most 2048 pixels on the longest side.
- **Process one image at a time:** Call MinerUClient.two_step_extract with mlx-engine, batch_size=1 and max_concurrency=1.
- **Read layout, then content:** The two steps locate page blocks and read their content. Convert the returned blocks with json2md and retain recognized title types.
- **Record the missing hierarchy:** Save detected title text and bounding boxes. With no supplied # heading levels, leave the level unknown; do not add another classifier.



**Models and terms explained**

- [MinerU2.5-Pro-2605-1.2B](https://huggingface.co/opendatalab/MinerU2.5-Pro-2605-1.2B): The 1.2-billion-parameter document image model tested through its direct two-step interface. It supplied title blocks but no levels in this run.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.

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
