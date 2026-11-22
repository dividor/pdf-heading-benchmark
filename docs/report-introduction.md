# On-premises PDF heading benchmark: scores, timings and methods

**21 completed local configurations, suitable for on-premises inference.** This experiment asks whether inexpensive parsers and local models can recover heading titles, original PDF page numbers and hierarchy levels while retaining the text of long World Food Programme (WFP) evaluation reports.

**Primary score: correct heading + correct level ÷ all reference headings.** A recovered title with the wrong H level earns no credit; a missed heading also earns no credit. Heading recovery, false headings and processing time are secondary diagnostics.

The strongest completed configuration was Qwen3.6-27B with sampled visual memory: **65/77 (84.4%)** headings recovered at the correct level, all 77 reference titles recovered, and two false headings. These are configuration-specific results from a small pilot with one AI assistant annotator, without independent human validation.

[Repository and runnable instructions](https://github.com/dividor/pdf-heading-benchmark) · [Markdown report](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/report/league_table.md) · [Frozen results](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/report/results.json) · [Per-report local scores](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/report/details.json)

**Our methods on this primary score:** learned grouping **51/77 (66.2%)**; grouped context + relationships **50/77 (64.9%)**; calibrated decoding **47/77 (61.0%)**; v1 **35/77 (45.5%)**. Learned grouping is our highest-scoring variant on this table. Calibration is a regression on this objective, even though its F1 improves on a separate regression set.

[Jump to the highlighted **OUR METHOD** row](#our-trained-model): the context + relationships pipeline was historically selected using exact group-and-level F1 on separate validation reports. Its highlight identifies that selected pipeline; it does not mean it has our highest primary score here. The LLM creates annotations; deployed inference uses small tree models. [Ablation results, sources, costs and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md).

**v2 development status:** errors on these original four reports informed the new approach. Its rows are diagnostic results, not fresh held-out validation. Historical model-selection criteria and frozen results are preserved. Future comparisons should prioritize correct heading plus level on validation reports, with false headings reported separately, before evaluating an untouched test set.

## Documents and their sources

All four PDFs were obtained from WFP's public document servers. Each title below links directly to its official source PDF. The [corpus manifest](https://github.com/dividor/pdf-heading-benchmark/blob/main/configs/corpus.json) records the download URLs, page counts and SHA-256 hashes; the downloader verifies the files against those hashes.

The corpus contains **523 pages: three English reports and one Spanish report**. All four contain native digital text. None has PDF outline bookmarks, although embedded structure tags provide another possible source of headings. This does not test scanned-document performance. The original 2018 resilience report that prompted the investigation was excluded after document-specific exploratory work.

The audit covers **eight selected pages per report, 32 pages and 77 reference headings in total**. Page numbers below are **one-based physical PDF pages**, including covers and front matter, rather than printed page labels. These are the exact pages scored for every completed configuration.
