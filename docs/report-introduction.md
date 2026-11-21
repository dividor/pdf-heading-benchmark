# PDF heading benchmark: scores, costs and methods

**17 completed configurations, one prepared but unrun service.** Four WFP evaluation reports contain 523 pages; heading scores cover **77 frozen reference headings on 32 deliberately selected pages**. This is a single-assistant-annotator pilot, not a general accuracy guarantee or an independent human-validated test set.

The strongest completed configuration was Qwen3.6-27B with sampled visual memory: **65/77 (84.4%)** headings recovered at the correct level, all 77 titles recovered, and two false headings. These results describe the tested configurations, not every capability of each product.

**Matching contract:** same original PDF page, at least 90% normalized title similarity, one-to-one Hungarian assignment, and an exact reference level. Missing headings count against the combined score. False headings are displayed separately. This is not a character-perfect title metric. Main chapters and annexes are H1; a cover title does not shift all body levels.

[Repository and runnable instructions](https://github.com/dividor/pdf-heading-benchmark) · [Markdown report](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/report/league_table.md) · [Frozen results](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/league_table.json) · [Every original match and error](https://github.com/dividor/pdf-heading-benchmark/blob/main/outputs/league_details.json)
