# On-premises PDF heading benchmark: scores, timings and methods

**16 completed local configurations, suitable for on-premises inference.** This experiment asks whether inexpensive parsers and local models can recover heading titles, original PDF page numbers and hierarchy levels while retaining the text of long World Food Programme (WFP) evaluation reports.

The strongest completed configuration was Qwen3.6-27B with sampled visual memory: **65/77 (84.4%)** headings recovered at the correct level, all 77 reference titles recovered, and two false headings. These are configuration-specific results from a small pilot with one AI assistant annotator, without independent human validation.

[Repository and runnable instructions](https://github.com/dividor/pdf-heading-benchmark) · [Markdown report](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/report/league_table.md) · [Frozen results](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/report/results.json) · [Per-report local scores](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/report/details.json)

## Documents and their sources

All four PDFs were obtained from WFP's public document servers. Each title below links directly to its official source PDF. The [corpus manifest](https://github.com/dividor/pdf-heading-benchmark/blob/main/configs/corpus.json) records the download URLs, page counts and SHA-256 hashes; the downloader verifies the files against those hashes.

The corpus contains **523 pages: three English reports and one Spanish report**. All four contain native digital text. None has PDF outline bookmarks, although embedded structure tags provide another possible source of headings. This does not test scanned-document performance. The original 2018 resilience report that prompted the investigation was excluded after document-specific exploratory work.

The audit covers **eight selected pages per report, 32 pages and 77 reference headings in total**. Page numbers below are **one-based physical PDF pages**, including covers and front matter, rather than printed page labels. These are the exact pages scored for every completed configuration.
