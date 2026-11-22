# On-premises PDF heading benchmark: scores, timings and methods

**21 completed local configurations, suitable for on-premises inference.** This experiment asks whether inexpensive parsers and local models can recover heading titles, original PDF page numbers and hierarchy levels while retaining the text of long World Food Programme (WFP) evaluation reports.

The strongest completed configuration was Qwen3.6-27B with sampled visual memory: **65/77 (84.4%)** headings recovered at the correct level, all 77 reference titles recovered, and two false headings. These are configuration-specific results from a small pilot with one AI assistant annotator, without independent human validation.

[Repository and runnable instructions](https://github.com/dividor/pdf-heading-benchmark) · [Markdown report](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/report/league_table.md) · [Frozen results](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/report/results.json) · [Per-report local scores](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/report/details.json)

**Looking for our trained model?** [Jump to the highlighted **OUR METHOD** row](#our-trained-model): LLM-assisted visual annotations → learned line grouping, heading levels and document context → local CPU inference. The LLM creates labels; deployed inference uses small tree models. **v2: 50/77 correct on this historical diagnostic, up from 35/77 for v1.** On 32 pages from four fresh reports, exact group-and-level F1 improved from **71.6% to 85.7%**. The denominators and matching rules differ: do not compare these two percentages directly. [Ablation results, sources, costs and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md).

**v2 development status:** errors on these original four reports informed the new approach. Its rows are diagnostic results, not fresh held-out validation. All three v2 ablations are shown, including learned grouping, which scored 51/77 here; the context model was selected using separate validation reports before the fresh test.

## Documents and their sources

All four PDFs were obtained from WFP's public document servers. Each title below links directly to its official source PDF. The [corpus manifest](https://github.com/dividor/pdf-heading-benchmark/blob/main/configs/corpus.json) records the download URLs, page counts and SHA-256 hashes; the downloader verifies the files against those hashes.

The corpus contains **523 pages: three English reports and one Spanish report**. All four contain native digital text. None has PDF outline bookmarks, although embedded structure tags provide another possible source of headings. This does not test scanned-document performance. The original 2018 resilience report that prompted the investigation was excluded after document-specific exploratory work.

The audit covers **eight selected pages per report, 32 pages and 77 reference headings in total**. Page numbers below are **one-based physical PDF pages**, including covers and front matter, rather than printed page labels. These are the exact pages scored for every completed configuration.
