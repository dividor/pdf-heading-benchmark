# On-premises PDF heading benchmark: scores, timings and methods

**21 completed local configurations, suitable for on-premises inference.** This experiment asks whether inexpensive parsers and local models can recover heading titles, original PDF page numbers and hierarchy levels while retaining the text of long World Food Programme (WFP) evaluation reports.

The strongest completed configuration was Qwen3.6-27B with sampled visual memory: **65/77 (84.4%)** headings recovered at the correct level, all 77 reference titles recovered, and two false headings. These are configuration-specific results from a small pilot with one AI assistant annotator, without independent human validation.

[Repository and runnable instructions](https://github.com/dividor/pdf-heading-benchmark) · [Markdown report](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/report/league_table.md) · [Frozen results](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/report/results.json) · [Per-report local scores](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/report/details.json)

**Looking for our trained model?** [Jump to the highlighted **OUR METHOD** row](#our-trained-model): LLM-assisted visual annotations → learned line grouping, heading levels and document context → local CPU inference. The LLM creates labels; deployed inference uses small tree models. **v2: 50/77 correct on this historical diagnostic, up from 35/77 for v1.** On 32 pages from four fresh reports, exact group-and-level F1 improved from **71.6% to 85.7%**. The denominators and matching rules differ: do not compare these two percentages directly. [Ablation results, sources, costs and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md).

**v2 development status:** errors on these original four reports informed the new approach. Its rows are diagnostic results, not fresh held-out validation. All three v2 ablations are shown, including learned grouping, which scored 51/77 here; the context model was selected using separate validation reports before the fresh test.

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

Sorted by correct heading plus level. In HTML, select a **Configuration** or **Method / code** to open its technique diagram and source links. The Markdown version retains direct links and includes a technique appendix. Both heading percentages use the same 77-reference denominator. A dash means unavailable or not applicable. All configurations ran locally; no hosted inference service is included. See the notes immediately below the table for scope and licensing qualifications.

| Configuration | Method / code | Status | Headings recovered | Correct heading + level | False headings | Native prose retention | Measured time |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [Qwen3.6-27B / MLX 4-bit / sampled visual memory](https://huggingface.co/Qwen/Qwen3.6-27B) | [32 targets; Qwen3.6-27B MLX 4-bit, native text, full-document candidates/tags, prior sampled-page images.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_visual_memory.py) | completed | 100.0% (77/77) | 84.4% (65/77) | 2 | — | 61.8 min / 32 pages |
| [Chandra OCR 2 / MLX](https://huggingface.co/datalab-to/chandra-ocr-2) | [32 images; author OCR-layout prompt/rendering; MLX batch 4; read HTML heading levels.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_chandra_batch.py) | completed | 90.9% (70/77) | 68.8% (53/77) | 2 | 98.7% | 17.2 min / 32 pages |
| [v2: learned grouping](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md) | [LLM annotations → learned line joining across PDF blocks → group-level Extra Trees. Same expanded training set; CPU; historical diagnostic.](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) | completed | 96.1% (74/77) | 66.2% (51/77) | 21 | — | 12.0 s / 523 pages |
| <span id="our-trained-model"></span>[**OUR METHOD — LLM annotations → grouped context model v2 (CPU)**](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md) | [OUR TRAINED MODEL v2: learned grouping + document style/TOC features + learned level relationships. Selected on separate validation reports; CPU. Historical diagnostic.](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) | completed | 83.1% (64/77) | 64.9% (50/77) | 23 | — | 12.6 s / 523 pages |
| <span id="our-calibrated-model"></span>[**OUR MODEL — calibrated decoding (experimental)**](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-calibration/report.md) | [OUR MODEL v2 + validation-selected decoding: body score ×2; relation weight 1. Same frozen trees and annotations. CPU; historical diagnostic, not a fresh test.](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/calibrate.py) | completed | 76.6% (59/77) | 61.0% (47/77) | 21 | — | 14.5 s / 523 pages |
| [LightOnOCR-3-0.8B / MLX](https://huggingface.co/lightonai/LightOnOCR-3-0.8B) | [32 page images; 0.8B MLX, grounding prompt, greedy 8192 tokens; decode title/continuation blocks.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_lighton_mlx.py) | completed | 93.5% (72/77) | 59.7% (46/77) | 8 | 99.5% | 8.9 min / 32 pages |
| [LightOnOCR-3-4B / MLX grounding](https://huggingface.co/lightonai/LightOnOCR-3-4B) | [32 images; MLX grounding prompt, 2048-pixel limit; batch 2 after 5 single-page historical checkpoints.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_chandra_batch.py) | completed | 93.5% (72/77) | 59.7% (46/77) | 8 | 99.3% | 23.5 min / 32 pages |
| [Embedded PDF heading tags](https://www.w3.org/WAI/WCAG22/Techniques/pdf/PDF9) | [Read author H1–H6 structure-tree tags on 32 audit pages; no inferred repairs.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_pdf_tags.py) | completed | 67.5% (52/77) | 55.8% (43/77) | 2 | — | 6.4 s / 32 pages |
| [v2: more annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md) | [LLM annotations → Extra Trees v2: 887 heading groups on 20 training reports; original line classifier and grouping. CPU; historical diagnostic.](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) | completed | 89.6% (69/77) | 53.2% (41/77) | 26 | — | 9.3 s / 523 pages |
| [LLM annotations → Extra Trees v1 (CPU)](https://github.com/dividor/pdf-heading-benchmark/blob/main/src/pdf_heading_benchmark/supervised_models.py) | [LLM-assisted visual annotations → 200-tree Extra Trees classifier trained on 16 different WFP reports → local CPU inference using PyMuPDF line features. Full PDFs; no refit on benchmark.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/supervised/compare.py) | completed | 76.6% (59/77) | 45.5% (35/77) | 20 | — | 7.7 s / 523 pages |
| [MinerU 4.2.3 basic CPU](https://github.com/opendatalab/MinerU) | [Full PDFs; basic ONNX CPU tier, no external LLM; native title-block levels.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_mineru.py) | completed | 85.7% (66/77) | 40.3% (31/77) | 2 | 99.1% | 11.2 min / 523 pages |
| [PyMuPDF4LLM 2.1](https://github.com/pymupdf/pymupdf4llm) | [Full PDFs to page-chunk Markdown; read Markdown heading levels and page provenance.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_pymupdf4llm.py) | completed | 93.5% (72/77) | 36.4% (28/77) | 2 | 98.8% | 51.8 s / 523 pages |
| [Qwen3.5-4B / union candidates](https://huggingface.co/Qwen/Qwen3.5-4B) | [Full-document candidate IDs + Qwen3.5-4B MLX 4-bit; JSON levels/null, no images; source: union.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) | completed | 70.1% (54/77) | 32.5% (25/77) | 3 | — | 1.7 min / hierarchy stage only |
| [Qwen3.5-4B / MinerU candidates](https://huggingface.co/Qwen/Qwen3.5-4B) | [Full-document candidate IDs + Qwen3.5-4B MLX 4-bit; JSON levels/null, no images; source: mineru_basic.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) | completed | 85.7% (66/77) | 29.9% (23/77) | 1 | — | 1.3 min / hierarchy stage only |
| [Docling fixed tolerance 0.15](https://github.com/docling-project/docling) | [Same blocks, fixed style_size_tolerance=0.15 on every report; exploratory variant.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) | completed | 88.3% (68/77) | 28.6% (22/77) | 2 | 98.4% | 1.7 min / 523 pages |
| [Qwen3.5-4B / PyMuPDF candidates](https://huggingface.co/Qwen/Qwen3.5-4B) | [Full-document candidate IDs + Qwen3.5-4B MLX 4-bit; JSON levels/null, no images; source: pymupdf4llm.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) | completed | 70.1% (54/77) | 28.6% (22/77) | 0 | — | 1.5 min / hierarchy stage only |
| [Marker 2.2 no OCR/LLM](https://github.com/datalab-to/marker) | [Full PDFs; CPU no-OCR/no-LLM; decode SectionHeader HTML tags.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_marker.py) | completed | 84.4% (65/77) | 24.7% (19/77) | 9 | 98.8% | 44.0 s / 523 pages |
| [Docling 2.151.1 default](https://github.com/docling-project/docling) | [CPU, OCR and tables off; native SectionHeaderItem levels; full PDFs.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) | completed | 88.3% (68/77) | 20.8% (16/77) | 2 | 98.4% | 1.7 min / 523 pages |
| [Docling built-in hierarchy](https://github.com/docling-project/docling) | [Same Docling blocks, built-in HeadingHierarchyModel enabled.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) | completed | 88.3% (68/77) | 20.8% (16/77) | 2 | 98.4% | 1.7 min / 523 pages |
| [Popo + Docling / experimental MLX 8-bit](https://github.com/opendatalab/MinerU-Popo) | [Docling candidates + Popo MLX 8-bit; 8-page chunks, page mosaics, upstream overlap alignment; experimental port.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_popo_mlx.py) | completed | 88.3% (68/77) | 19.5% (15/77) | 2 | 98.4% | 14.9 min / hierarchy stage only |
| [MinerU2.5-Pro-2605-1.2B / direct MLX interface](https://huggingface.co/opendatalab/MinerU2.5-Pro-2605-1.2B) | [32 images; direct MLX two_step_extract; preserve title blocks and absent levels as null.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_mineru_pro.py) | completed | 89.6% (69/77) | Levels not supplied (0/77 complete outputs) | 3 | 99.0% | 9.5 min / 32 pages |

## How to read the table

**Local resources and cost:** all configurations in this report ran locally on a shared 48 GB Apple M4 Pro. Hardware, electricity, setup, engineering, manual review and commercial licensing costs were not measured in dollars. Observed processing times are reported with their actual scope; local inference is not cost-free.

**Scopes and timing:** earlier CPU parsers processed all 523 pages. New local OCR models processed the complete text on the 32 audit pages. Qwen3.6 read native page text, full-document candidate titles and author PDF tags, and current/previous sampled-page images; it does not OCR the body. Its measured time excludes those candidate-generation stages. Qwen3.5 and Popo timings cover only hierarchy inference. Hardware was a shared 48 GB Apple M4 Pro. New-model times exclude downloads, loading and aborted attempts; some earlier CPU times include setup. These are observations with different scopes, not a controlled throughput benchmark.

**Text:** native prose retention measures five-word sequences preserved from native PDF blocks of at least 50 words, on the audit pages. It is not character accuracy, reading order, semantic accuracy or table correctness. A missing score means not evaluated or not applicable. Hierarchy-only stages reuse extracted text.

**Configuration caveats:** MinerU Pro's direct interface recovered headings but supplied no hierarchy levels; its 0/77 complete outputs must not be described as zero heading detection. The Qwen3.6 implementation uses only previously processed audit pages as visual memory; it is not a reproduction of a full-document memory benchmark. The Popo result is an experimental 8-bit MLX port with 8-page chunks, not an upstream performance claim. LightOn 4B historical timing includes five single-page checkpoints followed by batch-two processing; a clean rerun uses batch two throughout. The 0.15 Docling tolerance was fixed across these reports but remains an exploratory choice, not an untuned general default.

**Reference and uncertainty:** pages were deliberately selected to span front matter, body chapters, subsections and annexes. A single assistant annotated them visually. The original 2018 resilience report was excluded after prior document-specific investigation. No per-report title/level correction rules are applied here. The sample is small, covers born-digital reports only, and has no inter-annotator agreement study. Ranking on it cannot establish robustness on arbitrary documents. No missing run is assigned a zero score.

**Reproducibility:** the repo includes the frozen audit labels, page-restricted predictions and original summary/match records. `uv run pdf-headings score --historical` recomputes the bundled historical predictions, including the local configurations selected for this report, without model downloads or credentials. Raw full-page responses remain in the original local experiment archive; they are not bundled in the public repo. Fresh runners save raw responses outside Git. Seven historical Qwen formatting deviations were accepted by a generic JSON array/wrapper/single-fence reader without changing title or level values. Refactored runners retain prompts and settings; model/GPU runs have not all been repeated after packaging. See [method details](https://github.com/dividor/pdf-heading-benchmark/blob/main/docs/reproducibility.md).

**Licenses:** the repository's MIT license covers its code, not third-party packages, model weights or WFP reports. Chandra weights have commercial-use restrictions; applicable licensing costs are additional. See each linked model/package and [third-party notices](https://github.com/dividor/pdf-heading-benchmark/blob/main/THIRD_PARTY_NOTICES.md).

**Supervised Extra Trees:** the frozen classifier was trained on 16 different WFP reports, selected using four validation reports, and first evaluated on four new test reports. It was then applied without refitting to the original four benchmark PDFs and scored with the same 77-heading matching contract as every row above: **59/77 recovered, 35/77 at the correct level, 20 extra headings**. The 7.7-second measurement covers all 523 pages, including extraction and classification but excluding model loading and output writes. Native prose retention was not evaluated. Its separate 82.0% exact-level line F1 on the new test set uses a different corpus and metric and is not the number ranked here. [Comparison runner and evidence](https://github.com/dividor/pdf-heading-benchmark/tree/main/outputs/supervised/comparison) · [Training protocol](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/supervised/report.md).

**Calibration follow-up:** a validation-selected stricter decision raises exact group-and-level F1 from 85.7% to 94.7% on the previously inspected 38-heading regression set (eight false headings reduced to one; 36 correct remains unchanged; one genuine heading now missed). It regresses on this historical table: 47/77 correct, versus 50/77 for selected v2. The separate calibrated row is experimental and does not replace the highlighted model. [Protocol, all grid scores, report sources and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-calibration/report.md).


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

## Technique diagrams and sources

The HTML report opens these diagrams in a modal.


### Qwen3.6-27B / MLX 4-bit / sampled visual memory

Vision + document context · local MLX


**Inference:** Document context → 32 target pages → Qwen3.6-27B · 4-bit → Validated records

- **Document context:** Extract native text, full-document candidates and PDF tags.
- **32 target pages:** Render audited page images with earlier sampled-page images as memory.
- **Qwen3.6-27B · 4-bit:** Infer headings and levels using visual and document context.
- **Validated records:** Decode structured output with original page provenance.


The model saw sampled page images, not every page image. Generation overhead is substantial; measured results apply to this prompt and memory configuration.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_visual_memory.py) · [Base model / Hugging Face](https://huggingface.co/Qwen/Qwen3.6-27B) · [Tested 4-bit model / HF](https://huggingface.co/mlx-community/Qwen3.6-27B-4bit)


### Chandra OCR 2 / MLX

Page vision model · local MLX


**Inference:** 32 page images → Chandra OCR 2 → Structured HTML → Heading records

- **32 page images:** Use the author rendering and OCR-layout prompt.
- **Chandra OCR 2:** Run locally through MLX in batches of four.
- **Structured HTML:** Read generated heading tags from the response.
- **Heading records:** Convert HTML headings to levels with page provenance.


The measured run uses MLX on the benchmark Mac. Model-card GPU benchmarks use different hardware and datasets.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_chandra_batch.py) · [Model / Hugging Face](https://huggingface.co/datalab-to/chandra-ocr-2) · [Project / GitHub](https://github.com/datalab-to/chandra)


### v2: learned grouping

Our supervised model · CPU


**Training:** Visual source review → Training data → Small learned models

- **Visual source review:** Assistant labels headings and levels on separate WFP reports.
- **Training data:** 887 heading groups / 20 reports; reviewed negatives retained.
- **Small learned models:** Fit Extra Trees on training reports; select on separate validation reports.



**Inference:** New PDF → lines → Learned line joining → Group classification → Text + hierarchy

- **New PDF → lines:** PyMuPDF extracts text, font, position and spacing features.
- **Learned line joining:** Predict which adjacent lines belong to one heading, across PDF blocks.
- **Group classification:** Classify each joined group as body or a heading level.
- **Text + hierarchy:** Retain all native text; attach heading groups, levels and inferred parents.


No LLM is needed at inference. Labels are assistant-assisted, not independently human-verified. Parent links are inferred, not evaluated. v2 main-table scores are historical diagnostics; the separate 38-heading pilot has a different metric.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Configuration source / evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md)


### v2: context + relationships (selected)

Our supervised model · CPU


**Training:** Visual source review → Training data → Small learned models

- **Visual source review:** Assistant labels headings and levels on separate WFP reports.
- **Training data:** 887 heading groups / 20 reports; reviewed negatives retained.
- **Small learned models:** Fit Extra Trees on training reports; select on separate validation reports.



**Inference:** New PDF → lines → Learned line joining → Context + relationships → Text + hierarchy

- **New PDF → lines:** PyMuPDF extracts text, font, position and spacing features.
- **Learned line joining:** Predict heading spans across PDF blocks.
- **Context + relationships:** Use style / TOC features and learned level transitions; decode the sequence.
- **Text + hierarchy:** Retain all native text; attach heading groups, levels and inferred parents.


No LLM is needed at inference. Labels are assistant-assisted, not independently human-verified. Parent links are inferred, not evaluated. v2 main-table scores are historical diagnostics; the separate 38-heading pilot has a different metric.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Configuration source / evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md)


### OUR MODEL v2 + calibrated decoding (CPU)

Our supervised model · CPU


**Training:** Visual source review → Training data → Small learned models → Validation selection

- **Visual source review:** Assistant labels headings and levels on separate WFP reports.
- **Training data:** 887 heading groups / 20 reports; reviewed negatives retained.
- **Small learned models:** Fit Extra Trees on training reports; select on separate validation reports.
- **Validation selection:** Test nine fixed decoding settings on four validation reports; freeze the best exact F1.



**Inference:** New PDF → lines → Learned line joining → Context + relationships → Text + hierarchy

- **New PDF → lines:** PyMuPDF extracts text, font, position and spacing features.
- **Learned line joining:** Predict heading spans across PDF blocks.
- **Context + relationships:** Double the body decision score before retaining headings, then decode level relationships with weight 1.
- **Text + hierarchy:** Retain all native text; attach heading groups, levels and inferred parents.


The models and labels are unchanged. Validation selects a stricter heading decision. Regression on previously inspected pages improves F1 but misses one genuine heading. It is not new independent test evidence.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/calibrate.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Calibration protocol and regression evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-calibration/report.md)


### LightOnOCR-3-0.8B / MLX

Page vision model · local MLX


**Inference:** 32 page images → LightOnOCR-3-0.8B → Grounded blocks → Heading records

- **32 page images:** Render only the audited pages.
- **LightOnOCR-3-0.8B:** Use the grounding prompt. Greedy generation; up to 8192 tokens.
- **Grounded blocks:** Decode title and continuation blocks from the model response.
- **Heading records:** Export inferred titles, levels and page positions.


Page-local recognition has less document-wide hierarchy context. These are local MLX measurements, not vendor throughput claims.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_lighton_mlx.py) · [Model / Hugging Face](https://huggingface.co/lightonai/LightOnOCR-3-0.8B) · [Project / GitHub](https://github.com/lightonai/LightOnOCR) · [Earlier LightOnOCR research paper](https://arxiv.org/abs/2601.14251)


### LightOnOCR-3-4B / MLX grounding

Page vision model · local MLX


**Inference:** 32 page images → LightOnOCR-3-4B → Grounded blocks → Heading records

- **32 page images:** Render only the audited pages.
- **LightOnOCR-3-4B:** Use the grounding prompt. 2048-pixel limit; batch 2 after five single-page checkpoints.
- **Grounded blocks:** Decode title and continuation blocks from the model response.
- **Heading records:** Export inferred titles, levels and page positions.


Page-local recognition has less document-wide hierarchy context. These are local MLX measurements, not vendor throughput claims.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_chandra_batch.py) · [Model / Hugging Face](https://huggingface.co/lightonai/LightOnOCR-3-4B) · [Project / GitHub](https://github.com/lightonai/LightOnOCR) · [Earlier LightOnOCR research paper](https://arxiv.org/abs/2601.14251)


### Embedded PDF heading tags

Author metadata · CPU


**Inference:** Tagged PDF → H1–H6 tags → Page mapping → Heading records

- **Tagged PDF:** Read the document structure tree.
- **H1–H6 tags:** Collect author-supplied heading elements.
- **Page mapping:** Associate elements with the 32 audited pages.
- **Heading records:** Keep the original levels without inferred repairs.


Works only to the extent that the PDF author supplied correct structural tags.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_pdf_tags.py) · [W3C PDF heading technique](https://www.w3.org/WAI/WCAG22/Techniques/pdf/PDF9)


### v2: more annotations

Our supervised model · CPU


**Training:** Visual source review → Training data → Small learned models

- **Visual source review:** Assistant labels headings and levels on separate WFP reports.
- **Training data:** 887 heading groups / 20 reports; reviewed negatives retained.
- **Small learned models:** Fit Extra Trees on training reports; select on separate validation reports.



**Inference:** New PDF → lines → Line classification → Same-block grouping → Text + hierarchy

- **New PDF → lines:** PyMuPDF extracts text, font, position and spacing features.
- **Line classification:** 200-tree classifier predicts body or heading level per line.
- **Same-block grouping:** Combine adjacent predicted heading lines within PDF blocks.
- **Text + hierarchy:** Retain all native text; attach heading groups, levels and inferred parents.


No LLM is needed at inference. Labels are assistant-assisted, not independently human-verified. Parent links are inferred, not evaluated. v2 main-table scores are historical diagnostics; the separate 38-heading pilot has a different metric.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Configuration source / evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md)


### Supervised Extra Trees / CPU / assistant labels

Our supervised model · CPU


**Training:** Visual source review → Training data → Small learned models

- **Visual source review:** Assistant labels headings and levels on separate WFP reports.
- **Training data:** 154 headings / 16 reports.
- **Small learned models:** Fit Extra Trees on training reports; select on separate validation reports.



**Inference:** New PDF → lines → Line classification → Same-block grouping → Text + hierarchy

- **New PDF → lines:** PyMuPDF extracts text, font, position and spacing features.
- **Line classification:** 200-tree classifier predicts body or heading level per line.
- **Same-block grouping:** Combine adjacent predicted heading lines within PDF blocks.
- **Text + hierarchy:** Retain all native text; attach heading groups, levels and inferred parents.


No LLM is needed at inference. Labels are assistant-assisted, not independently human-verified. Parent links are inferred, not evaluated. v2 main-table scores are historical diagnostics; the separate 38-heading pilot has a different metric.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/supervised/compare.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Configuration source / evidence](https://github.com/dividor/pdf-heading-benchmark/blob/main/src/pdf_heading_benchmark/supervised_models.py)


### MinerU 4.2.3 basic CPU

Layout parser · CPU


**Inference:** Full PDFs → MinerU basic → Title blocks → Heading records

- **Full PDFs:** Process all four complete reports.
- **MinerU basic:** Use the ONNX CPU pipeline without an external LLM.
- **Title blocks:** Read native title blocks and their supplied levels.
- **Heading records:** Preserve native titles and levels for the audit.


This CPU tier is different from the MinerU Pro vision model below.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_mineru.py) · [Project / GitHub](https://github.com/opendatalab/MinerU)


### PyMuPDF4LLM 2.1

Native PDF parser · CPU


**Inference:** Full PDFs → PyMuPDF4LLM → Markdown headings → Heading records

- **Full PDFs:** Read text, fonts and page layout.
- **PyMuPDF4LLM:** Convert every page to Markdown chunks.
- **Markdown headings:** Read # through ###### as levels and retain page provenance.
- **Heading records:** Score extracted titles and their Markdown levels.


Typography-driven Markdown can confuse display text with section headings.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_pymupdf4llm.py) · [Project / GitHub](https://github.com/pymupdf/pymupdf4llm) · [Documentation](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/)


### Qwen3.5-4B / union candidates

Text-only LLM refinement · local MLX


**Inference:** Candidate extraction → Document-wide IDs → Qwen3.5-4B · 4-bit → Join by ID

- **Candidate extraction:** Docling + PyMuPDF4LLM union supplies page-tagged title candidates.
- **Document-wide IDs:** Give each candidate an ID; send the full list without page images.
- **Qwen3.5-4B · 4-bit:** Ask for a JSON level or null for each candidate ID.
- **Join by ID:** Map accepted IDs back to source titles and pages.


A missing candidate cannot be recovered by this refinement. JSON is validated; invalid replies are not silently repaired.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) · [Base model / Hugging Face](https://huggingface.co/Qwen/Qwen3.5-4B) · [Tested 4-bit model / HF](https://huggingface.co/mlx-community/Qwen3.5-4B-MLX-4bit)


### Qwen3.5-4B / MinerU candidates

Text-only LLM refinement · local MLX


**Inference:** Candidate extraction → Document-wide IDs → Qwen3.5-4B · 4-bit → Join by ID

- **Candidate extraction:** MinerU basic supplies page-tagged title candidates.
- **Document-wide IDs:** Give each candidate an ID; send the full list without page images.
- **Qwen3.5-4B · 4-bit:** Ask for a JSON level or null for each candidate ID.
- **Join by ID:** Map accepted IDs back to source titles and pages.


A missing candidate cannot be recovered by this refinement. JSON is validated; invalid replies are not silently repaired.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) · [Base model / Hugging Face](https://huggingface.co/Qwen/Qwen3.5-4B) · [Tested 4-bit model / HF](https://huggingface.co/mlx-community/Qwen3.5-4B-MLX-4bit)


### Docling fixed tolerance 0.15

Layout parser · CPU


**Inference:** Full PDFs → Docling layout → Fixed style tolerance → Heading records

- **Full PDFs:** Read native PDF text and page geometry.
- **Docling layout:** Detect document blocks; OCR and table extraction disabled.
- **Fixed style tolerance:** HeadingHierarchyModel with style_size_tolerance=0.15 across all four reports.
- **Heading records:** Export title, page and supplied level for scoring.


These variants share detected blocks. A hierarchy stage cannot recover a heading absent from its inputs. The tolerance variant is exploratory.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) · [Project / GitHub](https://github.com/docling-project/docling) · [Docling technical report (2024)](https://arxiv.org/abs/2408.09869)


### Qwen3.5-4B / PyMuPDF candidates

Text-only LLM refinement · local MLX


**Inference:** Candidate extraction → Document-wide IDs → Qwen3.5-4B · 4-bit → Join by ID

- **Candidate extraction:** PyMuPDF4LLM supplies page-tagged title candidates.
- **Document-wide IDs:** Give each candidate an ID; send the full list without page images.
- **Qwen3.5-4B · 4-bit:** Ask for a JSON level or null for each candidate ID.
- **Join by ID:** Map accepted IDs back to source titles and pages.


A missing candidate cannot be recovered by this refinement. JSON is validated; invalid replies are not silently repaired.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) · [Base model / Hugging Face](https://huggingface.co/Qwen/Qwen3.5-4B) · [Tested 4-bit model / HF](https://huggingface.co/mlx-community/Qwen3.5-4B-MLX-4bit)


### Marker 2.2 no OCR/LLM

Layout parser · CPU


**Inference:** Full PDFs → Marker conversion → SectionHeader HTML → Heading records

- **Full PDFs:** Read the native text layer.
- **Marker conversion:** Run with OCR and LLM assistance disabled.
- **SectionHeader HTML:** Decode the header tag supplied for each detected section.
- **Heading records:** Map tags to levels and retain page provenance.


This benchmark is the local no-OCR/no-LLM configuration, not Marker with generative assistance.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_marker.py) · [Project / GitHub](https://github.com/datalab-to/marker)


### Docling 2.151.1 default

Layout parser · CPU


**Inference:** Full PDFs → Docling layout → Native section headers → Heading records

- **Full PDFs:** Read native PDF text and page geometry.
- **Docling layout:** Detect document blocks; OCR and table extraction disabled.
- **Native section headers:** Keep SectionHeaderItem levels supplied by the parser.
- **Heading records:** Export title, page and supplied level for scoring.


These variants share detected blocks. A hierarchy stage cannot recover a heading absent from its inputs. The tolerance variant is exploratory.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) · [Project / GitHub](https://github.com/docling-project/docling) · [Docling technical report (2024)](https://arxiv.org/abs/2408.09869)


### Docling built-in hierarchy

Layout parser · CPU


**Inference:** Full PDFs → Docling layout → Built-in hierarchy → Heading records

- **Full PDFs:** Read native PDF text and page geometry.
- **Docling layout:** Detect document blocks; OCR and table extraction disabled.
- **Built-in hierarchy:** Run Docling HeadingHierarchyModel on its detected headers.
- **Heading records:** Export title, page and supplied level for scoring.


These variants share detected blocks. A hierarchy stage cannot recover a heading absent from its inputs. The tolerance variant is exploratory.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) · [Project / GitHub](https://github.com/docling-project/docling) · [Docling technical report (2024)](https://arxiv.org/abs/2408.09869)


### Popo + Docling / experimental MLX 8-bit

Visual hierarchy post-processing · local MLX


**Inference:** Docling candidates → 8-page chunks → Popo · 8-bit → Overlap alignment

- **Docling candidates:** Extract section headers and their page boxes.
- **8-page chunks:** Build page mosaics with candidate text and overlapping chunks.
- **Popo · 8-bit:** Run the title task in an experimental MLX port.
- **Overlap alignment:** Use upstream alignment and map results to source candidates.


This is our experimental Docling + MLX adapter, not the authors’ standard end-to-end deployment. No summary task was run.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_popo_mlx.py) · [Project / GitHub](https://github.com/opendatalab/MinerU-Popo) · [Model / Hugging Face](https://huggingface.co/DreamEternal/MinerU-Popo) · [MinerU-Popo paper](https://arxiv.org/abs/2605.24973)


### MinerU2.5-Pro-2605-1.2B / direct MLX interface

Page vision model · local MLX


**Inference:** 32 page images → MinerU2.5 Pro · 1.2B → Layout → content → Titles; null levels

- **32 page images:** Render the audited pages.
- **MinerU2.5 Pro · 1.2B:** Call the direct MLX two_step_extract interface.
- **Layout → content:** Extract title blocks from the returned content.
- **Titles; null levels:** Keep absent hierarchy levels as null; do not invent them.


This direct interface did not supply heading levels. Title detection alone is not a complete heading-and-level output.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_mineru_pro.py) · [Model / Hugging Face](https://huggingface.co/opendatalab/MinerU2.5-Pro-2605-1.2B) · [Project / GitHub](https://github.com/opendatalab/MinerU) · [Research paper linked by model card](https://arxiv.org/abs/2604.04771)
