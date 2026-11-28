# Run a parser

Start with the installation and external-data settings in the [README](../README.md). Check [validation status](validation.md) before treating a fresh run as a reproduction of the published table.

## Benchmark PDFs

```bash
uv run pdf-headings download
uv run pdf-headings run pymupdf4llm
uv run pdf-headings score
```

Downloads are checked against the committed SHA-256 hashes. Run one parser at a time. Replace `pymupdf4llm` with `docling_default` or `marker` to try another CPU baseline. Docling writes default, hierarchy and tolerance-0.15 outputs from one conversion.

`uv run pdf-headings run --help` lists CLI configurations. Some newer pipelines use [dedicated commands](official-pipelines.md); EvidenceLab and forced OCR have [their own guide](evidencelab-and-ocr.md). The [method manifest](../configs/methods.json) maps each configuration to its scripts and dependencies.

Backend environments are isolated from the core environment. Their manifests pin principal package versions, but are not complete transitive locks. Installation and weight loading can take longer than the processing time shown in the report. Marker pins Indra OCR 1.1.2 because a controlled fresh run with that version reproduced the published predictions.

## Your own PDF

```bash
uv run pdf-headings extract pymupdf4llm /path/to/report.pdf --output /path/to/new-run
```

Use a new output directory. Look in `results/document/` for heading JSON and extracted text. Headings retain physical PDF page numbers. Output formats vary: Marker keeps body text in structured HTML JSON; Docling also writes its hierarchy variants.

For our combined trained method, use the [rebuild and prediction guide](rebuild-heading-model.md). Its exported JSON trees need only the core dependencies for prediction.

## Apple Silicon models

MLX configurations require macOS on Apple Silicon. The experiment used a shared 48 GB M4 Pro. These commands do not silently select CPU or CUDA instead:

```bash
uv run pdf-headings run lighton_mlx
uv run pdf-headings score
```

Other examples are `chandra2_mlx` and `qwen36_visual_memory`. Qwen's command prepares its candidate headings and PDF-tag context before inference. Model revisions are pinned in [the model manifest](../configs/models.json) and model-preparation scripts.

For a custom PDF, image methods process every page. The published results cover only 32 selected benchmark pages; they do not validate full-document accuracy. Keep prompts and inputs unchanged when resuming a run. Use a new external directory for a changed configuration.

For a full-document Chandra OCR 2 and EvidenceLab comparison, including Markdown export,
see [the worked example](unseen-document.md).

## Protect a shared Mac

The optional guard records memory use, allows only one guarded experiment at a time and stops its own process group if memory pressure rises. Set `--required-gib` to the method's expected additional memory, beyond the default 6 GiB reserve. The following 4 GiB value is an example for a small model, not a limit suitable for every model:

```bash
uv run python -m pdf_heading_benchmark.run_guard \
  --output "$PDF_BENCHMARK_DATA/jobs/lighton-attempt-1" \
  --lock "$PDF_BENCHMARK_DATA/experiment.lock" \
  --required-gib 4 -- uv run pdf-headings run lighton_mlx
```

A blocked or aborted run has no valid fresh score. Inspect `status.json`, `memory.jsonl` and `console.log` in the job directory before retrying. The guard does not stop unrelated applications or manage detached Docker containers.
