## How to read the table

- **Timing:** large models ran one at a time on a shared 48 GB M4 Pro. Other workloads were not controlled. Setup exclusions vary by configuration; each method records its timing scope.
- **Scope:** Full-document parsers, including Docling OCR and EvidenceLab, read all 523 pages. Vision-to-text models read 32 audit pages. Qwen3.6 timing excludes candidate extraction; Qwen3.5 and Popo time only the hierarchy stage.
- **Measured versus estimated:** a 32-page run is measured. Scaling a longer run’s average to 32 pages is estimated. Neither is a promise of individual-page latency.
- **Prose retention:** the share of five-word sequences retained from native PDF blocks with at least 50 words. This does not measure reading order, table accuracy or meaning.
- **Cost:** hardware, electricity, setup and review were not priced. Local execution is not zero-cost. Model licenses are separate from the repository’s MIT license.
- **Reproduction:** frozen labels and predictions reproduce scores without downloading models. Full raw responses remain external. [Commands and limits](https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/docs/reproducibility.md) · [Licenses](https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/THIRD_PARTY_NOTICES.md).

Configuration-specific exceptions and training records are linked from each method’s details.
