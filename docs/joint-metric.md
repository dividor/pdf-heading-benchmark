## Primary metric: heading-and-level F0.5

A correct prediction must match **title, page and exact level**. Let **C** be correct predictions, **P** all predictions and **G** reference headings. Counts are pooled across the four reports before scoring.

| Measure | Formula | Meaning |
| --- | --- | --- |
| **Joint F0.5** | **1.25C / (P + 0.25G)** | Primary score; weights precision more than recall. |
| Joint precision | C / P | How much of the output is correct, including level? |
| Joint recall | C / G | How much of the reference was recovered correctly? |
| Joint F1 | 2C / (P + G) | Equal emphasis on precision and recall. |

**Wrong level = both a false positive and a false negative.** An invented heading is a false positive; a missed heading is a false negative. Unknown levels receive no joint credit. No predictions scores zero. Heading-only detection ignores level mistakes and is available as a diagnostic; there is no separate PASS/FAIL gate.

**Example:** 10 reference headings, 12 predictions and 9 correct heading-level pairs give precision **75%**, recall **90%**, and F0.5 **77.6%**. Recovering every title is not enough if the levels are wrong.

**Selection history:** OUR METHOD’s confidence filter was selected on separate validation reports using joint F0.5 with a heading-only precision constraint. The published training procedure has not been changed retrospectively. Its full selection rule, thresholds and provenance are in the method modal and [experiment record](https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/outputs/structure-precision/report.md).
