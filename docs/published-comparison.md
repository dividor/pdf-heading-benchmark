## Published comparison

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

### A newer Ovis model is now included

[OvisOCR3](https://huggingface.co/ATH-MaaS/OvisOCR3), described in its [October 20, 2026 paper](https://arxiv.org/abs/2610.33066), is absent from this chart. Our run uses its official Markdown recipe with vLLM Metal: **65.0% joint F0.5**, **36/77 correct title-level pairs**, one extra heading and **6 min 58 sec for 32 pages**. This does not retrospectively test OvisOCR2.

### Why the published chart does not predict our heading scores

The chart measures broad document parsing. Our score requires the exact heading depth as well as the title and page. We also use different hardware and, in the earlier trials, different assembly pipelines. We cannot attribute score differences to the weights alone.

The Methods & scoring tab now shows a measured level-error audit. New runs preserve the upstream pipeline’s output; they do not apply corrections fitted to WFP labels. [Official pipeline details and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/official-pipelines.md).
