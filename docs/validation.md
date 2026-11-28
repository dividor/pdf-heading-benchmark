# Fresh-checkout validation

Status recorded on November 28, 2026. This checks that a new checkout can reproduce the published experiment. It does not replace the original table or establish accuracy on new documents.

## Completed and incomplete checks

| Configuration | Fresh validation |
| --- | --- |
| `qwen36_visual_memory` | Configuration and adapter checks; no generation rerun |
| `chandra2_mlx` | Not yet rerun |
| `lighton_mlx` | Start blocked by elevated host memory pressure |
| `lighton4b_mlx` | Not yet rerun |
| `supervised_extra_trees` | Exact published audit predictions reproduced |
| `mineru_basic` | Stopped when host memory pressure rose; incomplete |
| `pymupdf4llm` | Exact published audit predictions reproduced |
| `qwen_ids_union` | Configuration and adapter checks; no generation rerun |
| `qwen_ids_mineru_basic` | Configuration and adapter checks; no generation rerun |
| `docling_tuned` | Exact published audit predictions reproduced |
| `qwen_ids_pymupdf4llm` | Configuration and adapter checks; no generation rerun |
| `marker` | Exact published audit predictions reproduced |
| `docling_default` | Exact published audit predictions reproduced |
| `docling_hierarchy` | Exact published audit predictions reproduced |
| `popo_docling` | Not yet rerun |
| `mineru_pro_mlx` | Not yet rerun |
| `structure_expanded_line` | Exact published audit predictions reproduced |
| `structure_learned_groups` | Exact published audit predictions reproduced |
| `structure_context_relations` | Exact published audit predictions reproduced |
| `structure_calibrated` | Exact published audit predictions reproduced |
| `structure_precision` | Exact published audit predictions reproduced |
| `structure_recall` | Exact published audit predictions reproduced |
| `qwen36_27b_compact` | Configuration and adapter checks; no generation rerun |
| `qwen36_35b_compact` | Configuration and adapter checks; no generation rerun |
| `qwen36_35b_visual_memory` | Configuration and adapter checks; no generation rerun |
| `minicpm_ocr10` | Not yet rerun |
| `xiaomi_ocr0` | Not yet rerun |
| `paddleocr_vl16` | Not yet rerun |
| `paddleocr_vl16_official` | Not yet rerun |
| `ovisocr3_official_metal` | Not yet rerun |
| `minicpm_ocr10_official_ollama` | Not yet rerun |
| `xiaomi_ocr0_official_metal` | Not yet rerun |
| `evidencelab` | Not yet rerun |
| `docling_ocr` | Not yet rerun |

The [machine-readable record](../outputs/verification/summary.json) contains counts, comparison hashes and the scope of each check. Paths in that record identify external run evidence; large logs and raw parser outputs are not distributed in Git. The [Qwen check record](../outputs/verification/qwen-runtime-check.json) records actual pinned processors, templates, model implementations and Metal availability. It explicitly records that weights were not loaded.

## What “reproduced” means

The four downloaded benchmark PDFs passed their committed checksums. Each completed method ran against the fresh data directory. The comparison checked every audited heading’s physical page, title and level against the published predictions, not just the aggregate score. All 12 completed configurations matched exactly.

The training notebook downloaded 28 public reports, fitted the classifiers, selected settings on validation reports and predicted the historical corpus. The seven trained variants were rebuilt and checked. The combined method also wrote JSON and Markdown for an example PDF. [Notebook instructions](rebuild-heading-model.md).

## A dependency difference that mattered

The first fresh Marker 2.2 run installed Indra OCR 1.2.0 and produced 29 correct heading–level pairs. The published run used Indra OCR 1.1.2 and had 19. A second full run with 1.1.2 reproduced every published audit prediction, including the 19 correct pairs. The dependency manifest now pins that version.

The package and its selected weight revision changed together. This experiment does not isolate which internal change affected the predictions. Both attempts remain in the external evidence archive; the better score from the different dependency is not substituted into the published row.

## Run and compare a fresh method

Follow [the parser instructions](run-parsers.md). After a guarded run completes successfully, compare its results:

```bash
uv run python -m pdf_heading_benchmark.verification_evidence \
  --data "$PDF_BENCHMARK_DATA" --method lighton_mlx \
  --job "$PDF_BENCHMARK_DATA/jobs/lighton-attempt-1" \
  --output "$PDF_BENCHMARK_DATA/comparisons/lighton_mlx.json"
```

This command rejects an unfinished job and changed PDFs. Dedicated runners can supply a document-keyed prediction file using `--predictions`. Fresh results stay outside the published report until their configuration and differences have been reviewed.

## Remaining work

Continue the pending parsers sequentially when the host has enough memory. MinerU basic needs a completed retry. Qwen generation will not be repeated in this audit, following the requested limited check. Do not read the original table’s completed measurements as a claim that all 34 fresh installations have passed this validation.
