# PDF heading benchmark: scores, costs and methods

**17 completed configurations, one prepared but unrun service.** Four WFP evaluation reports contain 523 pages; heading scores cover **77 frozen reference headings on 32 deliberately selected pages**. This is a single-assistant-annotator pilot, not a general accuracy guarantee or an independent human-validated test set.

The strongest completed configuration was Qwen3.6-27B with sampled visual memory: **65/77 (84.4%)** headings recovered at the correct level, all 77 titles recovered, and two false headings. These results describe the tested configurations, not every capability of each product.

**Matching contract:** same original PDF page, at least 90% normalized title similarity, one-to-one Hungarian assignment, and an exact reference level. Missing headings count against the combined score. False headings are displayed separately. This is not a character-perfect title metric. Main chapters and annexes are H1; a cover title does not shift all body levels.

[Repository and runnable instructions](https://github.com/dividor/pdf-heading-benchmark) · [Markdown report](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/report/league_table.md) · [Frozen results](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/league_table.json) · [Every original match and error](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/league_details.json)

| Configuration | Method / code | Status | Headings recovered | Correct heading + level | False headings | Native prose retention | API USD / 1,000 pages | API USD / 523 pages | Measured time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Qwen3.6-27B / MLX 4-bit / sampled visual memory](https://huggingface.co/Qwen/Qwen3.6-27B) | [32 targets; Qwen3.6-27B MLX 4-bit, native text, full-document candidates/tags, prior sampled-page images.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_visual_memory.py) | completed | 100.0% (77/77) | 84.4% (65/77) | 2 | — | $0.00 | $0.00 | 61.8 min / 32 pages |
| [Chandra OCR 2 / MLX](https://huggingface.co/datalab-to/chandra-ocr-2) | [32 images; author OCR-layout prompt/rendering; MLX batch 4; read HTML heading levels.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_chandra_batch.py) | completed | 90.9% (70/77) | 68.8% (53/77) | 2 | 98.7% | $0.00 | $0.00 | 17.2 min / 32 pages |
| [LightOnOCR-3-0.8B / MLX](https://huggingface.co/lightonai/LightOnOCR-3-0.8B) | [32 page images; 0.8B MLX, grounding prompt, greedy 8192 tokens; decode title/continuation blocks.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_lighton_mlx.py) | completed | 93.5% (72/77) | 59.7% (46/77) | 8 | 99.5% | $0.00 | $0.00 | 8.9 min / 32 pages |
| [LightOnOCR-3-4B / MLX grounding](https://huggingface.co/lightonai/LightOnOCR-3-4B) | [32 images; MLX grounding prompt, 2048-pixel limit; batch 2 after 5 single-page historical checkpoints.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_chandra_batch.py) | completed | 93.5% (72/77) | 59.7% (46/77) | 8 | 99.3% | $0.00 | $0.00 | 23.5 min / 32 pages |
| [Embedded PDF heading tags](https://www.w3.org/WAI/WCAG22/Techniques/pdf/PDF9) | [Read author H1–H6 structure-tree tags on 32 audit pages; no inferred repairs.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_pdf_tags.py) | completed | 67.5% (52/77) | 55.8% (43/77) | 2 | — | $0.00 | $0.00 | 6.4 s / 32 pages |
| [Azure Document Intelligence Layout](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/layout?view=doc-intel-4.0.0) | [All 523 pages; hosted prebuilt-layout API 2024-11-30; paragraph roles plus Markdown levels.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_hosted_ocr.py) | completed | 84.4% (65/77) | 41.6% (32/77) | 3 | 99.9% | $10.00 estimate | $5.23 | 1.7 min / 523 pages |
| [MinerU 4.2.3 basic CPU](https://github.com/opendatalab/MinerU) | [Full PDFs; basic ONNX CPU tier, no external LLM; native title-block levels.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_mineru.py) | completed | 85.7% (66/77) | 40.3% (31/77) | 2 | 99.1% | $0.00 | $0.00 | 11.2 min / 523 pages |
| [PyMuPDF4LLM 2.1](https://github.com/pymupdf/pymupdf4llm) | [Full PDFs to page-chunk Markdown; read Markdown heading levels and page provenance.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_pymupdf4llm.py) | completed | 93.5% (72/77) | 36.4% (28/77) | 2 | 98.8% | $0.00 | $0.00 | 51.8 s / 523 pages |
| [Qwen3.5-4B / union candidates](https://huggingface.co/Qwen/Qwen3.5-4B) | [Full-document candidate IDs + Qwen3.5-4B MLX 4-bit; JSON levels/null, no images; source: union.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) | completed | 70.1% (54/77) | 32.5% (25/77) | 3 | — | $0.00 | $0.00 | 1.7 min / hierarchy stage only |
| [Qwen3.5-4B / MinerU candidates](https://huggingface.co/Qwen/Qwen3.5-4B) | [Full-document candidate IDs + Qwen3.5-4B MLX 4-bit; JSON levels/null, no images; source: mineru_basic.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) | completed | 85.7% (66/77) | 29.9% (23/77) | 1 | — | $0.00 | $0.00 | 1.3 min / hierarchy stage only |
| [Docling fixed tolerance 0.15](https://github.com/docling-project/docling) | [Same blocks, fixed style_size_tolerance=0.15 on every report; exploratory variant.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) | completed | 88.3% (68/77) | 28.6% (22/77) | 2 | 98.4% | $0.00 | $0.00 | 1.7 min / 523 pages |
| [Qwen3.5-4B / PyMuPDF candidates](https://huggingface.co/Qwen/Qwen3.5-4B) | [Full-document candidate IDs + Qwen3.5-4B MLX 4-bit; JSON levels/null, no images; source: pymupdf4llm.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) | completed | 70.1% (54/77) | 28.6% (22/77) | 0 | — | $0.00 | $0.00 | 1.5 min / hierarchy stage only |
| [Marker 2.2 no OCR/LLM](https://github.com/datalab-to/marker) | [Full PDFs; CPU no-OCR/no-LLM; decode SectionHeader HTML tags.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_marker.py) | completed | 84.4% (65/77) | 24.7% (19/77) | 9 | 98.8% | $0.00 | $0.00 | 44.0 s / 523 pages |
| [Docling 2.151.1 default](https://github.com/docling-project/docling) | [CPU, OCR and tables off; native SectionHeaderItem levels; full PDFs.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) | completed | 88.3% (68/77) | 20.8% (16/77) | 2 | 98.4% | $0.00 | $0.00 | 1.7 min / 523 pages |
| [Docling built-in hierarchy](https://github.com/docling-project/docling) | [Same Docling blocks, built-in HeadingHierarchyModel enabled.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) | completed | 88.3% (68/77) | 20.8% (16/77) | 2 | 98.4% | $0.00 | $0.00 | 1.7 min / 523 pages |
| [Popo + Docling / experimental MLX 8-bit](https://github.com/opendatalab/MinerU-Popo) | [Docling candidates + Popo MLX 8-bit; 8-page chunks, page mosaics, upstream overlap alignment; experimental port.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_popo_mlx.py) | completed | 88.3% (68/77) | 19.5% (15/77) | 2 | 98.4% | $0.00 | $0.00 | 14.9 min / hierarchy stage only |
| [MinerU2.5-Pro-2605-1.2B / direct MLX interface](https://huggingface.co/opendatalab/MinerU2.5-Pro-2605-1.2B) | [32 images; direct MLX two_step_extract; preserve title blocks and absent levels as null.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_mineru_pro.py) | completed | 89.6% (69/77) | Levels not supplied (0/77 complete outputs) | 3 | 99.0% | $0.00 | $0.00 | 9.5 min / 32 pages |
| [Mistral OCR 4.1](https://docs.mistral.ai/studio/document-processing/basic_ocr) | [Prepared full-PDF OCR 4.1 API runner; extract page Markdown headings. NOT RUN: API key unavailable.](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_hosted_ocr.py) | credentials required | — | — | — | — | $4.00 | $2.09 | — |

## How to read the table

**Cost:** USD API fees, excluding hardware, electricity, tax, engineering, manual review and commercial licenses. Local $0 is not an all-in cost. Hosted figures are projected standard charges, not invoices. Azure's $10/1,000 is a provisional regional estimate. Mistral's $4/1,000 was a published standard rate at the time of the experiment; its $2.09 projection was not spent. Check current [Mistral pricing](https://docs.mistral.ai/inference/pricing?currency=usd) and [Azure pricing](https://azure.microsoft.com/en-us/pricing/details/document-intelligence/) before running.

**Scopes and timing:** earlier CPU parsers and Azure processed all 523 pages. New local OCR models processed the complete text on the 32 audit pages. Qwen3.6 read native page text, full-document candidate titles and author PDF tags, and current/previous sampled-page images; it does not OCR the body. Its measured time excludes those candidate-generation stages. Qwen3.5 and Popo timings cover only hierarchy inference. Hardware was a shared 48 GB Apple M4 Pro. New-model times exclude downloads, loading and aborted attempts; some earlier CPU times include setup. These are observations with different scopes, not a controlled throughput benchmark.

**Text:** native prose retention measures five-word sequences preserved from native PDF blocks of at least 50 words, on the audit pages. It is not character accuracy, reading order, semantic accuracy or table correctness. A missing score means not evaluated or not applicable. Hierarchy-only stages reuse extracted text.

**Configuration caveats:** MinerU Pro's direct interface recovered headings but supplied no hierarchy levels; its 0/77 complete outputs must not be described as zero heading detection. The Qwen3.6 implementation uses only previously processed audit pages as visual memory; it is not a reproduction of a full-document memory benchmark. The Popo result is an experimental 8-bit MLX port with 8-page chunks, not an upstream performance claim. LightOn 4B historical timing includes five single-page checkpoints followed by batch-two processing; a clean rerun uses batch two throughout. The 0.15 Docling tolerance was fixed across these reports but remains an exploratory choice, not an untuned general default.

**Reference and uncertainty:** pages were deliberately selected to span front matter, body chapters, subsections and annexes. A single assistant annotated them visually. The original 2018 resilience report was excluded after prior document-specific investigation. No per-report title/level correction rules are applied here. The sample is small, covers born-digital reports only, and has no inter-annotator agreement study. Ranking on it cannot establish robustness on arbitrary documents. No missing run is assigned a zero score.

**Reproducibility:** the repo includes the frozen audit labels, page-restricted predictions and original summary/match records. `uv run pdf-headings score --historical` recomputes all 17 scores without model downloads or credentials. Raw full-page responses remain in the original local experiment archive; they are not bundled in the public repo. Fresh runners save raw responses outside Git. Seven historical Qwen formatting deviations were accepted by a generic JSON array/wrapper/single-fence reader without changing title or level values. Refactored runners retain prompts and settings; model/GPU runs have not all been repeated after packaging. See [method details](https://github.com/dividor/pdf-heading-benchmark/blob/main/docs/reproducibility.md).

**Licenses:** the repository's MIT license covers its code, not third-party packages, model weights or WFP reports. Chandra weights have commercial-use restrictions; applicable licensing costs are additional. See each linked model/package and [third-party notices](https://github.com/dividor/pdf-heading-benchmark/blob/main/THIRD_PARTY_NOTICES.md).

## Documents

| Report | ID | Language | Pages |
| --- | --- | --- | --- |
| [Strategic evaluation of WFP’s Approaches to Targeting and Prioritization for Food and Nutrition Assistance](https://api.godocs.wfp.org/api/documents/WFP-0000171594/download/) | targeting | en | 172 |
| [Mid-Term Evaluation of WFP’s Strategic Plan 2022–2025](https://docs.wfp.org/api/documents/WFP-0000162023/download/) | midterm | en | 176 |
| [Evaluation of Indonesia WFP country strategic plan 2021–2025 — Volume I](https://docs.wfp.org/api/documents/WFP-0000168942/download/) | indonesia | en | 76 |
| [Evaluación del Plan estratégico para Colombia 2021–2024](https://docs.wfp.org/api/documents/WFP-0000157262/download/) | colombia | es | 99 |

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
| run_hosted_ocr.py / azure_layout | targeting | 14/15 | 7/15 | 1 |
| run_hosted_ocr.py / azure_layout | midterm | 18/18 | 8/18 | 1 |
| run_hosted_ocr.py / azure_layout | indonesia | 17/21 | 15/21 | 1 |
| run_hosted_ocr.py / azure_layout | colombia | 16/23 | 2/23 | 0 |
