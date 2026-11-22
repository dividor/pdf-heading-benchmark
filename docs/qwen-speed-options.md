# Qwen speed options for this benchmark

Checked against the linked model cards on 21 November 2026. These are candidates for speed/quality experiments, not measured replacements for the current result.

The recorded Qwen result already uses **mlx-community/Qwen3.6-27B-4bit**, on the shared 48 GB M4 Pro, with `enable_thinking=False`, temperature 0 and a 4,096-token output cap. Its 61.8 minutes cover 32 audit pages, not the whole 523-page corpus. [Recorded runner](../scripts/runners/run_qwen_visual_memory.py) · [Pinned model revision](../configs/models.json).

| Option | What is available | What we know for this task |
| --- | --- | --- |
| [Qwen3.6-27B MLX 4-bit](https://huggingface.co/mlx-community/Qwen3.6-27B-4bit) | Quantized Apple Silicon model | Already used in the measured 82.7% joint F0.5 result. Quantization is not an untried fix for its runtime. |
| [Qwen3.6-27B GGUF](https://huggingface.co/unsloth/Qwen3.6-27B-GGUF) | Includes 3-bit and 4-bit variants | Lower-bit weights reduce storage; speed and heading accuracy on this workload must be measured. The vision projector and runtime buffers also consume memory. |
| [Qwen3.6-35B-A3B MLX 4-bit](https://huggingface.co/mlx-community/Qwen3.6-35B-A3B-4bit) | Quantized mixture-of-experts sibling | A promising speed candidate, not the same model as the tested 27B. Its [official card](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) specifies 35B total / 3B activated parameters. That motivates testing; it does not establish speed or heading accuracy on this Mac. |
| [Qwen3.6-27B MTP GGUF](https://huggingface.co/unsloth/Qwen3.6-27B-MTP-GGUF) | Conversion retaining multi-token-prediction support | Requires a compatible inference path. No measured multimodal M4 Pro speedup in this benchmark. |

The runner sends the full candidate outline and author tags again for each target, plus the current page image and selected prior page images. It starts a fresh generation call per target. This repeated input processing is a plausible cost driver, but the saved total timings do not isolate input processing from token generation.

The most useful next controlled experiment is **the same 4-bit model with less repeated input**: cap visual memory, reduce image dimensions, and replace repeated full-document context with a compact document-style summary. Measure each change on validation reports and record both joint precision and recall. Test the 35B-A3B sibling separately with the same inputs. Preserve the existing result, time end-to-end preprocessing as well as generation, and do not assume either change preserves accuracy.

[Qwen's official model card](https://huggingface.co/Qwen/Qwen3.6-27B) documents non-thinking mode and MTP serving options. Non-thinking mode is already enabled in this benchmark; it cannot be counted as a new speed improvement. No additional Qwen model was downloaded or timed for this note.
