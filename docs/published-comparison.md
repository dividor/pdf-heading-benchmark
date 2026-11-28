## Published comparison

### OmniParseBench 1.8.0 · 39 systems

[![39 systems with layout scores above 70. Teal marks models or tools also tested in our WFP study.](../../docs/images/ocr-text-layout.png)](https://github.com/datalab-to/omni_parse_bench#leaderboard)

Published scores from Datalab, retrieved November 28, 2026. The chart includes **12 hosted APIs and services**, including LlamaParse, Mistral OCR, Azure and Reducto. These are external benchmark results, not our WFP measurements. Our trained model has not been evaluated here.

Text score runs left to right; layout runs bottom to top. Only layout scores above 70 are shown. Teal marks eight models or tools also tested in our study, with different configurations. Layout tests classify blocks as text, heading or table. **It does not test heading levels.**

<details><summary>Benchmark caveats and excluded rows</summary>

† Gemini 4 includes retries other systems did not receive. * Starred models helped create or verify tests. Datalab builds the benchmark and several listed systems. Rows without a layout score or scoring 70 or less are omitted. Two rows still scored with version 1.5—GPT-6.1 Sol and Claude Opus 5.5—are excluded. Small score differences should not be overinterpreted.

Direct Gemini, Claude and GPT calls are separate configurations from managed document parsers. Google Document AI has no row here. OmniParseBench is also separate from OpenDataLab’s OmniDocBench; their scores are not combined.

</details>

[Pinned source and run notes](https://github.com/datalab-to/omni_parse_bench/blob/65cc5b63f7f7f7e126416558b03bd107a417ac64/README.md#leaderboard) · [Chart data](https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/configs/field-overview.json) · [Reproduce the chart](https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/docs/field-overview.md).

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
