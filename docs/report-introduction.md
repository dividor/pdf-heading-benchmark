# On-premises PDF heading benchmark: scores, timings and methods

**23 completed local configurations, suitable for on-premises inference.** This experiment asks whether parsers and local models can recover heading titles, PDF pages and levels while retaining the text of long WFP evaluation reports.

**Primary metric: joint heading-and-level F0.5**, with joint precision and joint recall alongside it. A correct prediction must match the heading title, PDF page and exact level. Wrong levels and extra headings reduce precision; missed or incorrectly leveled headings reduce recall. There is no separate PASS/FAIL gate. Definitions and worked examples follow the table.

Qwen3.6-27B with sampled visual memory leads at **82.7% joint F0.5**, with **82.3% joint precision**, 65/77 correct heading-level pairs and two extras. Embedded PDF tags score **73.4% F0.5**, with 79.6% joint precision and 43/77 correct pairs. Chandra scores **72.6% F0.5**, 73.6% joint precision and 53/77 correct pairs. These are configuration-specific results from a small, assistant-annotated sample, without independent human validation.

**Our new precision-selected method:** [jump to the highlighted row](#our-trained-model). A validation-selected confidence filter raises historical joint F0.5 from **58.8% to 70.5%** and reduces extra headings from **23 to 2**, reaching **82.9% joint precision (34/41)** and **44.2% joint recall (34/77)**. It emits fewer headings: correct title-and-level pairs fall from **50/77 to 34/77**, with 38 titles missed. This is an explicit precision/recall trade-off. The three small CPU classifiers are unchanged; the LLM supplied training annotations and is not used at inference.

The candidate was selected from a fixed 36-setting grid on four separate validation reports. The original league and the previously inspected 38-heading set were scored only after selection. Both are regression evidence, not new independent tests. The historical selection rule included a 95% heading-only precision constraint; that rule remains documented in the experiment but is no longer a league-table qualification gate. [Experiment, every setting and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-precision/report.md).

**Coverage retraining trial:** the additional OUR METHOD row refits the trees and restores title recovery to 66/77 (85.7%), but has only 50 correct heading-level pairs and 21 extras. None of the 64 validation configurations met both 80% joint precision and recall. It is a diagnostic fallback, not a recommended replacement. [Experiment and complete evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-recall/report.md).

[Repository and runnable instructions](https://github.com/dividor/pdf-heading-benchmark) · [Markdown report](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/report/league_table.md) · [Score exports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/report/results.json)

## Documents and their sources

All four PDFs were obtained from WFP's public document servers. Each title below links directly to its official source PDF. The [corpus manifest](https://github.com/dividor/pdf-heading-benchmark/blob/main/configs/corpus.json) records the download URLs, page counts and SHA-256 hashes; the downloader verifies the files against those hashes.

The corpus contains **523 pages: three English reports and one Spanish report**. All four contain native digital text. None has PDF outline bookmarks, although embedded structure tags provide another possible source of headings. This does not test scanned-document performance. The original 2018 resilience report that prompted the investigation was excluded after document-specific exploratory work.

The audit covers **eight selected pages per report, 32 pages and 77 reference headings in total**. Page numbers below are **one-based physical PDF pages**, including covers and front matter, rather than printed page labels. These are the exact pages scored for every completed configuration.
