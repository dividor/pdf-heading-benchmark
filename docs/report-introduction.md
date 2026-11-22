# On-premises PDF heading benchmark: scores, timings and methods

**22 completed local configurations, suitable for on-premises inference.** This experiment asks whether parsers and local models can recover heading titles, PDF pages and levels while retaining the text of long WFP evaluation reports.

**Primary metric: joint heading-and-level F0.5, with a 95% heading-detection precision requirement.** Both incorrect levels and extra headings reduce the joint score. The precision gate separately requires at most 5% spurious headings among predictions on this sample. FAIL rows remain visible but do not qualify. Definitions and a worked example follow the table.

Qwen3.6-27B with sampled visual memory leads at **82.7% joint F0.5**, with **97.5% heading precision**, 65/77 correct heading-level pairs and two extras. Embedded PDF tags score **73.4% F0.5**, with 96.3% heading precision and 43/77 correct pairs. Chandra scores **72.6% F0.5**, 97.2% heading precision and 53/77 correct pairs. These are configuration-specific results from a small, assistant-annotated sample, without independent human validation.

**Our new precision-selected method:** [jump to the highlighted row](#our-trained-model). A validation-selected confidence filter raises historical joint F0.5 from **58.8% to 70.5%** and reduces extra headings from **23 to 2**, reaching **95.1% heading precision**. It emits fewer headings: correct title-and-level pairs fall from **50/77 to 34/77**, with 38 titles missed. This is an explicit precision/recall trade-off. The three small CPU classifiers are unchanged; the LLM supplied training annotations and is not used at inference.

The candidate was selected from a fixed 36-setting grid on four separate validation reports. The original league and the previously inspected 38-heading set were scored only after selection. Both are regression evidence, not new independent tests. The precision gate is an observed sample threshold, not a statistical confidence bound or production guarantee. [Experiment, every setting and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-precision/report.md).

[Repository and runnable instructions](https://github.com/dividor/pdf-heading-benchmark) · [Markdown report](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/report/league_table.md) · [Score exports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/report/results.json)

## Documents and their sources

All four PDFs were obtained from WFP's public document servers. Each title below links directly to its official source PDF. The [corpus manifest](https://github.com/dividor/pdf-heading-benchmark/blob/main/configs/corpus.json) records the download URLs, page counts and SHA-256 hashes; the downloader verifies the files against those hashes.

The corpus contains **523 pages: three English reports and one Spanish report**. All four contain native digital text. None has PDF outline bookmarks, although embedded structure tags provide another possible source of headings. This does not test scanned-document performance. The original 2018 resilience report that prompted the investigation was excluded after document-specific exploratory work.

The audit covers **eight selected pages per report, 32 pages and 77 reference headings in total**. Page numbers below are **one-based physical PDF pages**, including covers and front matter, rather than printed page labels. These are the exact pages scored for every completed configuration.
