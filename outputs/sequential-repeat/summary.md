<span id="sequential-gpu-reruns"></span>

## Sequential GPU reruns

These are fresh runs on the same four PDFs and 32 audit pages, using the existing 77 reference headings. Each configuration runs in a separate process, with only one benchmark model loaded at a time. The runner checks that MLX selects the Metal GPU and refuses a CPU fallback. It records model/package versions, source and input hashes, raw page responses, process wall time, GPU activity and virtual-memory counters. The original league results above remain frozen; this table compares the reruns explicitly rather than silently replacing the historical measurements.

**Timing:** all rates below use seconds per page. Earlier and rerun processing rates use the original runners' measurement boundaries, excluding model loading and upstream candidate extraction. Whole-process rates include interpreter imports, model loading, image preparation, generation and output writes; they still exclude previously prepared candidate extraction and downloads. OCR batch time is divided by the number of pages, so it measures average throughput rather than single-page latency. Smaller values are faster. This is one repeat per configuration, not a statistical estimate of typical performance.

**Settings:** Qwen models retain their pinned MLX 4-bit weights, greedy decoding, seed 42, non-thinking prompts and 4,096-token limit. Single-image runs use a 1,280-pixel image; visual-memory runs use a 1,792-pixel current image plus up to six earlier 1,280-pixel images. Chandra retains batch four and a 12,384-token limit. LightOn 4B uses batch two throughout and a 12,384-token limit; its historical run mixed five single-page checkpoints (12,288-token limit) with batching, so that comparison includes a batching and token-limit change. LightOn 0.8B remains one image at a time with an 8,192-token limit. No headings or levels are repaired after generation.

**Hardware and limits:** this Mac has an Apple M4 Pro with a 20-core GPU and 48 GiB unified memory. GPU inference is active, but other applications still share memory and GPU resources. In the initial rerun, loading the sparse Qwen model increased total system swap usage from approximately 15 GB to 20 GB. The reruns therefore must not be described as measurements on an idle or memory-pressure-free machine. Swap-counter differences below show actual activity during each run, rather than treating existing swap allocation as proof of ongoing paging. PDF rendering, tokenization and JSON handling also use the CPU. [MLX's unified-memory and device documentation](https://ml-explore.github.io/mlx/build/html/usage/unified_memory.html) explains how CPU and GPU execution share memory; the recorded device selection and telemetry establish what happened in these runs.

[Sequential runner](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/repeat_models.py) · [Importer and scorer](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/repeat_report.py) · [Rerun predictions versus reference](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/sequential-repeat/report.md) · [Compact evidence](https://github.com/dividor/pdf-heading-benchmark/tree/codex/technique-explorer/outputs/sequential-repeat)


**Completed: 5/7 configurations.**

| Repeated configuration | Earlier s/page | Rerun s/page | Whole-process s/page | Correct heading + level | Joint F0.5: earlier → rerun | Rerun extras | Errors | Timeouts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen3.6-35B-A3B 4-bit — single image | 9.772 | 10.701 | 11.632 | 53/77 → 53/77 | 68.8% → 68.8% | 0 | 0 | 0 |
| Qwen3.6-35B-A3B 4-bit — visual memory | 16.256 | 15.580 | 16.497 | 52/77 → 52/77 | 69.0% → 69.0% | 0 | 0 | 0 |
| Chandra OCR 2 / MLX | 32.258 | 27.701 | 28.198 | 53/77 → 53/77 | 72.6% → 72.6% | 2 | 0 | 0 |
| LightOnOCR-3-4B / MLX grounding | 44.145 | 32.988 | 33.530 | 46/77 → 46/77 | 57.9% → 57.9% | 8 | 0 | 0 |
| LightOnOCR-3-0.8B / MLX | 16.606 | 11.542 | 11.772 | 46/77 → 46/77 | 57.9% → 57.9% | 8 | 0 | 0 |

### GPU and memory observations

| Repeated configuration | Samples | Median GPU % | Maximum GPU % | Swap read GB | Swap written GB |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6-35B-A3B 4-bit — single image | 38 | 99.0 | 100 | 0.492 | 4.719 |
| Qwen3.6-35B-A3B 4-bit — visual memory | 53 | 99 | 100 | 0.098 | 0.029 |
| Chandra OCR 2 / MLX | 90 | 99.0 | 100 | 0.099 | 0.000 |
| LightOnOCR-3-4B / MLX grounding | 107 | 99 | 100 | 0.143 | 0.000 |
| LightOnOCR-3-0.8B / MLX | 38 | 92.0 | 100 | 0.201 | 0.000 |

GPU and swap measurements are system-wide; they include other applications and model loading. A high GPU percentage confirms activity but does not prove optimal inference or identify a bottleneck.
