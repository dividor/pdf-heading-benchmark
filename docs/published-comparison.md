## Published comparison

### Text and layout across the field

[![Published text extraction scores on X and layout classification scores on Y for 17 local models and hosted systems. Higher and farther right is better.](../../docs/images/ocr-text-layout.png)](https://github.com/datalab-to/omni_parse_bench#results)

*Figure by the author from [Datalab’s OmniParseBench results](https://github.com/datalab-to/omni_parse_bench#results), retrieved November 26, 2026. Both axes use published scores out of 100. This is a selected field overview, not our WFP experiment.*

The [layout score](https://github.com/datalab-to/omni_parse_bench/blob/main/docs/scoring/layout_kind.md) tests whether blocks are labeled as text, heading or table at the expected location. It does not test heading levels. Models without a published layout score, including Xiaomi-OCR-0, are omitted. Our trained model has not been evaluated on this benchmark.

Text and layout scores cover both local and hosted systems. Published timings do not cover the local models, so this plot does not use speed. The planned service runs will compare heading-and-level quality and seconds per page on our WFP sample. [Chart data](https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/configs/field-overview.json) · [Reproduce the plot](https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/scripts/field_overview.py).

### Cloud services queued for comparison

These requested API configurations are the next comparison group. They are not included in the 34 local result rows. Use the same WFP reference headings and joint F0.5; record service version, request settings, elapsed time and billed usage separately.

| Service | Configuration to test | Status |
| --- | --- | --- |
| [Mistral OCR 3](https://docs.mistral.ai/models/ocr-3-25-12) | `mistral-ocr-2512`; native Markdown, without custom annotations | Queued. The older runner targets OCR 4.1, so it is not this configuration. |
| [Azure Document Intelligence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/layout?view=doc-intel-4.0.0) | `prebuilt-layout`, API `2024-11-30`, Markdown and section hierarchy | Earlier API evidence is archived outside the local table; verify its configuration before reuse. |
| [Google Document AI Layout Parser](https://docs.cloud.google.com/document-ai/docs/layout-parse-chunk) | Gemini Layout Parser `pretrained-layout-parser-v3.5-2026-07-09`, listed as stable November 18, 2026 | Queued. Score its document hierarchy, rather than basic text-only OCR. |
| [LlamaParse](https://www.llamaindex.ai/pricing) | Cost Effective, Agentic and Agentic Plus as separate configurations; record the resolved model version | Queued. Compare price against heading-level quality. |

**Published league tables and diagrams (checked November 26, 2026):** [ParseBench-2 interactive charts](https://www.llamaindex.ai/blog/introducing-parsebench-v2) and [leaderboard](https://www.parsebench.ai/) cover current LlamaParse, Azure and Mistral OCR 4.1. [Mistral's OCR 3 comparison chart](https://mistral.ai/news/mistral-ocr-3/) covers the requested OCR 3 alongside Azure and Google, but dates from December 2025 and omits LlamaParse. [OmniParseBench](https://github.com/datalab-to/omni_parse_bench) provides another open leaderboard.

These are vendor-produced benchmarks of broader parsing quality, not our heading-and-level score. The sources do not establish a common ranking of all four exact requested configurations. In particular, OCR 4.1 results are not OCR 3 results, and direct Gemini results are not Document AI Layout Parser results.

### The OCR field: quality versus speed

Higher means better document parsing; farther right means faster processing. **This is OpenBMB’s October 27, 2026 snapshot, not a live ranking.** It omits OvisOCR3, which we now test separately.

[![OpenBMB comparison of fourteen OCR systems: document-parsing quality versus throughput.](../../docs/images/ocr-field-overview.png)](https://github.com/OpenBMB/MiniCPM-OCR/blob/c21a3ca524263ef8166cb6d350864b10c3056b61/docs/minicpm_ocr_1dot0_en.md#evaluation)

*OpenBMB, October 27, 2026. Original figure reproduced unchanged under Apache 2.0. [Source and methodology](https://github.com/OpenBMB/MiniCPM-OCR/blob/c21a3ca524263ef8166cb6d350864b10c3056b61/docs/minicpm_ocr_1dot0_en.md#evaluation) · [Original image](https://raw.githubusercontent.com/OpenBMB/MiniCPM-OCR/c21a3ca524263ef8166cb6d350864b10c3056b61/assets/minicpm-ocr/efficiency-performance-en.png).*

This author-reported chart averages four parsing benchmarks and measures throughput on an RTX 5090, with one page at a time and possible region concurrency. It does **not** measure our WFP heading-level accuracy or Mac speed. Its selected models are not the whole field.

### Which chart models did we test?

| Model in the chart | Quality relative to Chandra in this chart | Our WFP coverage |
| --- | --- | --- |
| MiniCPM-OCR 1.0 | Higher | Official package with Ollama Q8 + DSpark: **22.2%** joint F0.5. Earlier MLX adaptation: also **22.2%**. |
| Xiaomi-OCR-0 | Higher | Upstream two-stage pipeline on Metal: **42.9%**. Earlier whole-page MLX: **39.7%**. |
| PaddleOCR-VL-1.6 | Higher | Official Apple Silicon pipeline: **24.9%**. Earlier MiniCPM-assembly adaptation: **22.2%**. |
| [Ovis-OCR2](https://huggingface.co/ATH-MaaS/OvisOCR2) | Higher | Not tested. The newer OvisOCR3 is tested separately below. |
| Chandra OCR 2 | Reference | Tested: MLX, **72.6%**. |
| TeleOCR | Lower | Not tested. |
| MinerU2.5-Pro | Lower | Tested through the direct MLX interface; no heading levels returned. |
| Unlimited-OCR-2 | Lower | Not tested. |
| GLM-OCR | Lower | Not tested. |
| HunyuanOCR-1.5 | Lower | Not tested. |
| Surya OCR 2 | Lower | No standalone run of this chart configuration. |
| dots.ocr | Lower | Not tested. |
| LightOnOCR-3-1B | Lower | Exact chart variant not tested; our rows use 0.8B and 4B variants. |
| Unlimited-OCR | Lower | Not tested. |

**OvisOCR3 is not in this chart.** Our separate Metal run scores **65.0% joint F0.5**, with **36/77** heading-level pairs correct. Ovis-OCR2 remains untested.

Broad OCR quality does not establish heading-level accuracy. Our WFP measurements use different hardware and input conditions. [Pipeline reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/docs/official-pipelines.md).
