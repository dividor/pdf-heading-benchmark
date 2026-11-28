## Heading-level audit

A recognized title can still have the wrong depth. The first three counts below add to the 77 references; extra predictions are counted separately. Open a method's details in Results to inspect every prediction beside its reference.

| Configuration | Correct title + level | Title found, wrong level | Missed title | Extra prediction |
| --- | --- | --- | --- | --- |
| Xiaomi: earlier whole-page adaptation | 29 | 40 | 8 | 3 |
| MiniCPM: earlier MLX adaptation | 16 | 52 | 9 | 3 |
| Paddle: earlier MiniCPM assembly adaptation | 16 | 52 | 9 | 3 |
| Chandra OCR 2: existing MLX run | 53 | 17 | 7 | 2 |
| Paddle: official Apple Silicon pipeline | 18 | 50 | 9 | 3 |
| OvisOCR3: upstream prompt, vLLM Metal | 36 | 13 | 28 | 1 |
| MiniCPM: official package, Ollama Q8 + DSpark | 16 | 52 | 9 | 3 |
| Xiaomi: upstream two-stage pipeline, Metal | 31 | 37 | 9 | 3 |

**What we verified:** on the mid-term report's PDF page 26, “1. Introduction” is visually the main section and “1.1 Evaluation features” its subsection. The earlier MiniCPM assembler emits both as H3. It also promotes the ordinary paragraph “3. The MTE's key features are:” to a heading. Paddle's full pipeline reproduces these three outputs on that page.

In the earlier Xiaomi whole-page run, 65 of its 69 matched titles were H2. Those titles span reference levels H1-H5, so changing every level by one cannot fix the result. We have applied no offsets or rules fitted to these reports.

**Xiaomi's upstream default formatter assigns H2 to paragraph titles.** Executing that formatter on H1, H3 and numbered example titles returned H2 each time. On mid-term page 26, both Introduction and its Evaluation features subsection are H2. The upstream two-stage run still has 37 wrong-level matches; no WFP correction was applied.

**OvisOCR3 sometimes transcribes a title without marking it as a heading.** On Indonesia page 7, Executive summary, Introduction and Evaluation features appear as ordinary text. On targeting page 33, 2 Evaluation findings has no heading marker, although its subsections have H2-H4 markers. These are classification misses, not necessarily unreadable or absent text.

[All level disagreements and counts](https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/outputs/level-audit.json) · [Raw region-to-heading assembly examples](https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/outputs/assembly-trace.json) · [Xiaomi formatter measurements](https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/outputs/xiaomi-assembly-trace.json) · [Rerun protocol and runtime differences](https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/docs/official-pipelines.md).
