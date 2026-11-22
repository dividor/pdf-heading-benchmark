# Qwen speed options for this benchmark

Model availability was checked against the linked cards on 21 November 2026. The single-image 27B and 35B-A3B trials were run on 22 November; see the [measured comparison](../outputs/qwen-compact/report.md). GGUF and MTP remain unmeasured here.

The recorded Qwen result already uses **mlx-community/Qwen3.6-27B-4bit**, on the shared 48 GB M4 Pro, with `enable_thinking=False`, temperature 0 and a 4,096-token output cap. Its 61.8 minutes cover 32 audit pages, not the whole 523-page corpus. [Recorded runner](../scripts/runners/run_qwen_visual_memory.py) · [Pinned model revision](../configs/models.json).

| Option | What is available | What we know for this task |
| --- | --- | --- |
| [Qwen3.6-27B MLX 4-bit](https://huggingface.co/mlx-community/Qwen3.6-27B-4bit) | Quantized Apple Silicon model | Already used in the measured 82.7% joint F0.5 result. Quantization is not an untried fix for its runtime. |
| [Qwen3.6-27B GGUF](https://huggingface.co/unsloth/Qwen3.6-27B-GGUF) | Includes 3-bit and 4-bit variants | Lower-bit weights reduce storage; speed and heading accuracy on this workload must be measured. The vision projector and runtime buffers also consume memory. |
| [Qwen3.6-35B-A3B MLX 4-bit](https://huggingface.co/mlx-community/Qwen3.6-35B-A3B-4bit) | Quantized mixture-of-experts sibling | Now tested separately with the same single-image input construction as the 27B speed trial. Its [official card](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) specifies 35B total / 3B activated parameters. Use the measured regression results linked above for speed and heading accuracy on this Mac. |
| [Qwen3.6-27B MTP GGUF](https://huggingface.co/unsloth/Qwen3.6-27B-MTP-GGUF) | Conversion retaining multi-token-prediction support | Requires a compatible inference path. No measured multimodal M4 Pro speedup in this benchmark. |

The runner sends the full candidate outline and author tags again for each target, plus the current page image and selected prior page images. It starts a fresh generation call per target. This repeated input processing is a plausible cost driver, but the saved total timings do not isolate input processing from token generation.

The completed speed experiment reduces the current image to 1,280 pixels and replaces earlier images with text-only heading memory. It retains the full outline and tags, so it does not test a compact document-style summary. Both model variants were fixed before scoring on the already inspected audit corpus. The older multi-image result remains a separate row. A follow-up restored that multi-image procedure with the sparse model; it did not improve recovery (52/77 correct pairs versus 53/77 with one image). All three fresh trials remain in the report.

[Qwen's official model card](https://huggingface.co/Qwen/Qwen3.6-27B) documents non-thinking mode and MTP serving options. Non-thinking mode is already enabled in this benchmark; it cannot be counted as a new speed improvement. The measured single-image experiment is documented separately; lower-bit GGUF and MTP options have not been timed here.
