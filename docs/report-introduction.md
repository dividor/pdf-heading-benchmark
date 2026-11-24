# On-premises PDF heading benchmark: scores, timings and methods

**28 completed local configurations, suitable for on-premises inference.** This experiment asks whether parsers and local models can recover heading titles, PDF pages and levels while retaining the text of long WFP evaluation reports.

**Primary metric: joint heading-and-level F0.5**, with joint precision and joint recall alongside it. A correct prediction must match the heading title, PDF page and exact level. Wrong levels and extra headings reduce precision; missed or incorrectly leveled headings reduce recall. There is no separate PASS/FAIL gate. Definitions and worked examples follow the table.

Qwen3.6-27B with sampled visual memory leads at **82.7% joint F0.5**, with **82.3% joint precision**, 65/77 correct heading-level pairs and two extras. Chandra scores **72.6% F0.5**, 73.6% joint precision and 53/77 correct pairs. These are configuration-specific results from a small, assistant-annotated sample, without independent human validation.

**Sequential GPU reruns:** seven selected MLX configurations were repeated one at a time on all 32 audit pages. Every heading title, page and level was reproduced exactly, with no parse errors, timeouts or truncations. The main table uses the new **average time per page** measurements, marked “Latest sequential run”. Chandra and LightOn were faster in these repeats; Qwen timings were mixed. [Original versus repeated timings, GPU observations and protocol](#sequential-gpu-reruns).

**New OCR field trials:** all three new candidates completed the same 32 pages, one model at a time, using pixels only. Xiaomi-OCR-0 whole-page scores **39.7% joint F0.5**; MiniCPM-OCR 1.0 and PaddleOCR-VL-1.6 with CPU layout each score **22.2%**. They retain 98.1–98.8% of measured prose and take 4 min 39 sec to 7 min 50 sec per 32 pages, but none improves on Chandra’s hierarchy score. The region pipelines use the MiniCPM SDK’s native numbering-based Markdown levels. These are Apple Silicon configurations, not replications of the external NVIDIA chart; earlier Qwen configurations also receive extra document context. [Protocol, exact settings and measured evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/field-candidates/report.md).

**Our new precision-selected method:** [jump to the highlighted row](#our-trained-model). A validation-selected confidence filter raises historical joint F0.5 from **58.8% to 70.5%** and reduces extra headings from **23 to 2**, reaching **82.9% joint precision (34/41)** and **44.2% joint recall (34/77)**. It emits fewer headings: correct title-and-level pairs fall from **50/77 to 34/77**, with 38 titles missed. This is an explicit precision/recall trade-off. The three small CPU classifiers are unchanged; the LLM supplied training annotations and is not used at inference.

The candidate was selected from a fixed 36-setting grid on four separate validation reports. The original league and the previously inspected 38-heading set were scored only after selection. Both are regression evidence, not new independent tests. The historical selection rule included a 95% heading-only precision constraint; that rule remains documented in the experiment but is no longer a league-table qualification gate. [Experiment, every setting and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-precision/report.md).

**Coverage retraining trial:** the additional OUR METHOD row refits the trees and restores title recovery to 66/77 (85.7%), but has only 50 correct heading-level pairs and 21 extras. None of the 64 validation configurations met both 80% joint precision and recall. It is a diagnostic fallback, not a recommended replacement. [Experiment and complete evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-recall/report.md).

[Repository and runnable instructions](https://github.com/dividor/pdf-heading-benchmark) · [Markdown report](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/report/league_table.md) · [Score exports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/report/results.json)

[The recent OCR field: quality-versus-speed diagram and sources](#published-comparison). These external scores are separate from our WFP results.

## Documents and their sources

All four PDFs were obtained from WFP's public document servers. Each title below links directly to its official source PDF. The [corpus manifest](https://github.com/dividor/pdf-heading-benchmark/blob/main/configs/corpus.json) records the download URLs, page counts and SHA-256 hashes; the downloader verifies the files against those hashes.

The corpus contains **523 pages: three English reports and one Spanish report**. All four contain native digital text. None has PDF outline bookmarks. The standalone PDF-tag baseline is excluded from this comparison because it relies on structure already supplied by the PDF author. The recorded Qwen3.6 runs still use available author tags as input alongside text and images; their scores do not establish performance on untagged PDFs. This does not test scanned-document performance. The original 2018 resilience report that prompted the investigation was excluded after document-specific exploratory work.

The audit covers **eight selected pages per report, 32 pages and 77 reference headings in total**. Page numbers below are **one-based physical PDF pages**, including covers and front matter, rather than printed page labels. These are the exact pages scored for every completed configuration.

[Sequential GPU reruns: before/after timing, accuracy and GPU activity](#sequential-gpu-reruns). The main table marks verified rerun timings; the historical source evidence remains frozen.
