## Published comparison

### The OCR field: quality versus speed

Higher means better document parsing; farther right means faster processing. **Four models sit above Chandra OCR 2 on quality. We tested three; Ovis-OCR2 remains a gap.**

[![OpenBMB comparison of fourteen OCR systems: document-parsing quality versus throughput.](../../docs/images/ocr-field-overview.png)](https://github.com/OpenBMB/MiniCPM-OCR/blob/c21a3ca524263ef8166cb6d350864b10c3056b61/docs/minicpm_ocr_1dot0_en.md#evaluation)

*OpenBMB, October 27, 2026. Original figure reproduced unchanged under Apache 2.0. [Source and methodology](https://github.com/OpenBMB/MiniCPM-OCR/blob/c21a3ca524263ef8166cb6d350864b10c3056b61/docs/minicpm_ocr_1dot0_en.md#evaluation) · [Original image](https://raw.githubusercontent.com/OpenBMB/MiniCPM-OCR/c21a3ca524263ef8166cb6d350864b10c3056b61/assets/minicpm-ocr/efficiency-performance-en.png).*

This author-reported chart averages four parsing benchmarks and measures throughput on an RTX 5090, with one page at a time and possible region concurrency. It does **not** measure our WFP heading-level accuracy or Mac speed. Its selected models are not the whole field.

### Which chart models did we test?

| Model in the chart | Quality relative to Chandra in this chart | Our WFP coverage |
| --- | --- | --- |
| MiniCPM-OCR 1.0 | Higher | Tested: MLX + CPU layout, **22.2%** joint F0.5. |
| Xiaomi-OCR-0 | Higher | Tested: whole-page MLX, **39.7%**. The chart’s stronger two-stage pipeline was not reproduced. |
| PaddleOCR-VL-1.6 | Higher | Tested: MLX + CPU layout, **22.2%**. Portable adaptation; not the complete official CUDA pipeline. |
| [Ovis-OCR2](https://huggingface.co/ATH-MaaS/OvisOCR2) | Higher | **Not tested. First remaining candidate above Chandra.** |
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

### Why the gap?

The previous shortlist selected MiniCPM, Xiaomi and Paddle. **It was incomplete.** We have no recorded failed compatibility test or other demonstrated blocker for Ovis-OCR2, so it should not have been silently omitted. Its authors describe a compact **0.8B, Qwen3.5-based** model, making a local trial worth investigating. Compatibility and heading quality still need measurement. [Official model card](https://huggingface.co/ATH-MaaS/OvisOCR2).

The other untested entries are faster than Chandra in this chart but have lower aggregate quality. They remain potential speed/quality alternatives, not demonstrated heading-level winners. Untested configurations receive no score in our results table.

**Why our results differ:** good text recognition does not guarantee the required hierarchy. Xiaomi gets 29/77 heading-level pairs right. MiniCPM and Paddle each get 16/77 and share the same layout and Markdown assembly. We preserved their native levels; we did not adjust them to match the reference. [Local run protocol and evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/field-candidates.md).
