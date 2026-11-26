# Checking the official OCR pipelines

The earlier local trials did not all run the upstream document-parsing pipelines. In particular, Paddle used MiniCPM's Markdown assembler, and Xiaomi used whole-page recognition rather than the two-stage pipeline behind its published parsing scores. These reruns keep the earlier configurations visible and add separately named results.

## What stays fixed

- The four public WFP PDFs, their checksums, the 32 physical audit pages and the 77 frozen reference headings remain unchanged. See [the corpus](../configs/corpus.json) and [audit pages](../configs/audit_pages.json).
- Each page is rendered at 200 DPI. Models receive image pixels, not PDF text, tags or the reference labels.
- Only one OCR model performs inference at a time. Recognition requests are sequential. Metal kernels still use parallel GPU execution.
- Smoke tests use the targeting report's cover, which is outside the scored pages. No prompt or level correction is selected using the audit results.
- The same one-to-one title/page matcher and exact-level joint F0.5 scorer evaluate every row. Correcting an offset after seeing these labels would be a new method, not an honest rerun of the existing one.
- References are assistant annotations. They have not all received independent human review. Visual checks of mid-term page 26, Indonesia page 20 and targeting page 24 support the disputed H1/H2 relationships discussed in the audit.

## What “official” means on this Mac

| Run | Upstream components actually used | Hardware/runtime difference |
| --- | --- | --- |
| PaddleOCR-VL-1.6 | `PaddleOCRVL` v1.6 from PaddleOCR 3.7.0; native PaddleX 3.7.2 layout, crops, prompts, merging and Markdown output | The documented Apple Silicon route: PaddlePaddle 3.3.1 CPU layout and MLX-VLM 0.8.0 recognition on Metal. Its client does not apply the optional `min_pixels`/`max_pixels` arguments; the processor uses its own bounds. |
| OvisOCR3 | Original 0.8B BF16 weights; pinned `document_markdown.txt`; upstream chat template, 16,384-token cap, temperature 0, non-thinking mode and Markdown cleanup | Upstream example: vLLM 0.22.1 with Triton. This run: vLLM 0.34.0 with its community-maintained Metal plugin. Pixel bounds remain 448² to 2880²; the current processor `size` API replaces deprecated argument names. Both APIs produced identical cover-page text in the smoke test. |
| MiniCPM-OCR 1.0 | Full `minicpm-ocr` 1.0.5 package, native Paddle layout, orientation handling, crop prompts and Markdown assembly; official Q8_0 main model, F16 vision projector and Q8_0 DSpark draft | Official Ollama deployment route on Metal, with one recognition request at a time. This quantized configuration differs from the earlier original-BF16 MLX adaptation. DSpark proposes token blocks that the main model verifies. |
| Xiaomi-OCR-0 | Pinned upstream two-stage evaluation CLI, region prompts, crop processing, table conversion, repetition-retry policy and Markdown assembly | Native PaddleX layout runs on CPU at the upstream benchmark threshold 0.25. The upstream serializer is reused. vLLM Metal serves the original BF16 recognition model, instead of CUDA vLLM/SGLang. |

Other host workloads were not controlled. Only one OCR model performed inference at a time.

These are comparisons of named local configurations. They are **not** reproductions of the RTX 5090 throughput chart. Running an upstream pipeline on another backend does not prove numerical parity with its CUDA results.

## Measured evidence and limits

The [heading-level audit](level-audit.md) separates correct matches, wrong levels, misses and extras. Each result modal also shows every reference and prediction. [Assembly examples](../outputs/assembly-trace.json) record raw region text and the heading markers produced by MiniCPM 1.0.5; reassembling those saved pages reproduced their Markdown exactly.

Paddle's full pipeline still outputs `1. Introduction` as H3 and `1.1 EVALUATION FEATURES` as H3 on mid-term PDF page 26. It also outputs the ordinary paragraph `3. The MTE's key features are:` as H3. This is an observed limitation of that pipeline's output. It is not evidence that the visual recognition weights themselves predicted an H3 label.

The earlier Xiaomi whole-page result has 65 H2 predictions among 69 matched headings. Those titles cover reference levels H1 through H5. A single global offset would therefore leave many disagreements.

Xiaomi’s upstream two-stage run returns 31 correct title-level pairs, 37 wrong levels, nine missed titles and three extras. Its default `title_profile="v2"` converts paragraph titles to H2. We executed the formatter on H1, H3 and numbered example titles and observed H2 for each; see [the recorded examples](../outputs/xiaomi-assembly-trace.json). The alternative number-based profile was not selected after inspecting the labels. All 32 upstream retry reports recorded zero repetition retries.

The Xiaomi per-region field named `merged` has already passed through Markdown assembly; it is not an untouched recognition response. We do not use it to claim that the weights themselves selected those levels.

Paddle and Xiaomi do not expose every recognition request's finish reason through the pipeline result. Missing token-limit telemetry is labelled unavailable, not zero. Ovis records raw text, finish reasons and token counts. Full raw pages, model weights, logs and execution-source snapshots stay outside Git; compact predictions and run summaries are committed under [outputs/official-pipelines](../outputs/official-pipelines).

## Reproducing the runs

Use a fresh output directory for every invocation. Set `DATA` to an external directory containing the PDFs downloaded by `uv run pdf-headings download`. Set `CACHE` to an external Hugging Face cache. Model revisions are in [official-pipelines.json](../configs/official-pipelines.json) and [field-candidates.json](../configs/field-candidates.json). The [layout file hashes](../configs/official-layout-model.json) identify the native Paddle weights used here.

Install the appropriate requirements in separate Python 3.12 environments. The normal repository environment is sufficient for scoring and report generation; it does not install these optional runtimes.

```bash
uv venv --python 3.12 "$DATA/environments/paddle"
uv pip install --python "$DATA/environments/paddle/bin/python" -r configs/environments/paddle-official.txt
uv venv --python 3.12 "$DATA/environments/ovis"
uv pip install --python "$DATA/environments/ovis/bin/python" -r configs/environments/ovis-metal.txt
```

Use the existing `field-mlx.txt` environment for the Paddle recognition server and model downloads. The download programs use pinned revisions and write download records:

```bash
python scripts/runners/prepare_field_candidates.py --cache "$CACHE" --records "$DATA/downloads"
python scripts/runners/prepare_official_models.py ovisocr3 --cache "$CACHE" --records "$DATA/downloads"
python scripts/runners/prepare_official_models.py minicpm_gguf --cache "$CACHE" --records "$DATA/downloads"
python scripts/runners/prepare_official_models.py minicpm_dspark --cache "$CACHE" --records "$DATA/downloads"
```

`PADDLE_MODEL`, `OVIS_MODEL` and `XIAOMI_MODEL` below are the snapshot paths recorded by those programs. `LAYOUT` is the native PP-DocLayoutV3 directory, not the Transformers `safetensors` conversion. Paddle's first smoke run can download it through its official model manager; supply `--layout` on the scored run. Verify the three `inference.*` file hashes against the committed manifest before reusing it.

### Paddle

Start the recognition server in its MLX environment. This wrapper changes only browser access settings: it binds to loopback and replaces the upstream wildcard browser origin with an explicit local origin. Inference remains in the upstream server.

```bash
python scripts/runners/serve_local_mlx.py --host 127.0.0.1 --port 8111 --model "$PADDLE_MODEL"
```

In another terminal, use the Paddle environment:

```bash
PYTHONPATH=src python scripts/runners/run_official_paddle.py \
  --input-data "$DATA" --model "$PADDLE_MODEL" --layout "$LAYOUT" \
  --output "$DATA/official/paddle"
```

Add `--smoke` with a different output directory to test the cover first. Stop the recognition server before starting another model.

### OvisOCR3

The Ovis environment loads its model directly; no HTTP server is required:

```bash
PYTHONPATH=src python scripts/runners/run_ovis_official.py \
  --input-data "$DATA" --model "$OVIS_MODEL" --output "$DATA/official/ovis"
```

### MiniCPM

Install [minicpm-official.txt](../configs/environments/minicpm-official.txt). Follow the [upstream Ollama guide](https://github.com/OpenBMB/MiniCPM-OCR/blob/main/docs/ollama_deploy.md) with the downloaded, pinned GGUF files. Register the model as `benchmark-minicpm-ocr` on `127.0.0.1:18499`. Use the guide's Q8_0 main model, F16 4× vision projector, Q8_0 DSpark model, 8,192-token context, temperature 0 and `draft_num_predict=15`.

Keep `OLLAMA_NUM_PARALLEL=1` and `OLLAMA_MAX_LOADED_MODELS=1`. The runner uses one page worker and one region worker, disables layout/recognition overlap, and selects CPU layout explicitly:

```bash
PYTHONPATH=src python scripts/runners/run_official_minicpm.py \
  --input-data "$DATA" --layout "$LAYOUT" --output "$DATA/official/minicpm"
```

The package downloads its orientation models on first use. Perform this setup and the non-audit smoke test before timing the 32 pages. Confirm the Ollama log reports `draft-dspark`; do not assume merely registering the draft model enabled speculative decoding.

### Xiaomi

Install [xiaomi-official.txt](../configs/environments/xiaomi-official.txt), clone [SeerRay-Lab/Xiaomi-OCR-0](https://github.com/SeerRay-Lab/Xiaomi-OCR-0), and check out revision `4abc240285b69a2965cf64762101ddb4ab35f32d`. The runner refuses a different upstream revision. Set `XIAOMI_UPSTREAM` to that checkout.

Start vLLM in the Metal environment with the pinned original model. Use the served name `xiaomi-ocr0`, loopback port 8112, one concurrent sequence and an explicit CORS origin. Use this command in the vLLM Metal environment:

```bash
vllm serve "$XIAOMI_MODEL" --host 127.0.0.1 --port 8112 \
  --served-model-name xiaomi-ocr0 --allowed-origins '["http://127.0.0.1:8112"]' \
  --max-num-seqs 1 --seed 42 --gpu-memory-utilization 0.8 \
  --limit-mm-per-prompt '{"image":1}'
```

Then run the pipeline in the Xiaomi/Paddle environment:

```bash
PYTHONPATH=src python scripts/runners/run_official_xiaomi.py \
  --input-data "$DATA" --model "$XIAOMI_MODEL" --layout "$LAYOUT" \
  --upstream "$XIAOMI_UPSTREAM" --output "$DATA/official/xiaomi"
```

The runner uses the upstream region serializer after native PaddleX layout on CPU. It invokes the upstream recognition and assembly CLI unchanged, with one worker, temperature 0, top-p 0.8, repetition penalty 1, 16,384 maximum output tokens and the documented repetition retry at presence penalty 1.5. A failed upstream recognition summary aborts the run instead of silently producing a scored row.

### Score only after a complete run

```bash
uv run python scripts/official_pipelines_report.py --run "$DATA/official/paddle" --data "$DATA"
uv run python scripts/level_audit_report.py
uv run pdf-headings report
```

Repeat the import command for each complete run directory. The importer verifies the exact corpus hashes, fixed pages, completion count and native Markdown headings. It rejects smoke runs and changed heading levels. It never fills an untested row with a zero score.

Official source documentation: [Paddle Apple Silicon](https://www.paddleocr.ai/latest/en/version3.x/pipeline_usage/PaddleOCR-VL-Apple-Silicon.html), [OvisOCR3 pinned model card](https://huggingface.co/ATH-MaaS/OvisOCR3/blob/5b252386ba615bd464a5a26597560eaba87dae5c/README.md), [vLLM Metal model support](https://github.com/vllm-project/vllm-metal/blob/v0.34.0/docs/supported_models.md), [MiniCPM Ollama](https://github.com/OpenBMB/MiniCPM-OCR/blob/main/docs/ollama_deploy.md), [Xiaomi evaluation pipeline](https://github.com/SeerRay-Lab/Xiaomi-OCR-0/blob/4abc240285b69a2965cf64762101ddb4ab35f32d/evaluation_pipeline/README.md).
