# Optimizing heading-and-level quality with few false headings

The new candidate raises joint F0.5 from **58.8% to 70.5%** on the historical four-report benchmark and reduces extra headings from **23 to 2**. Heading-detection precision is **95.1%**, just above the agreed 95% gate. It does so by emitting fewer headings: **34/77 correct title-and-level pairs**, down from 50/77. This is a precision/recall trade-off, not an improvement in every measure.

## What changed

The three frozen v2 `ExtraTreesClassifier` models are unchanged: join (100 features), context (47 features) and relationship (142 features), each with 200 trees, maximum depth 16, minimum leaf size 2, feature fraction 0.8, balanced classes and seed 42. The new filter retains a group only if its largest heading-class score is at least **0.70** and its highest decision score is a heading rather than body. The selected body weight remains **1.0**. Viterbi relationship weight remains **1.0**.

These model scores are not calibrated probabilities. The 0.70 cutoff is a validation-selected operating point, not a claim of 70% real-world correctness. Viterbi runs after filtering; it cannot restore rejected headings. Full native text remains available even when a heading is rejected.

## Selection protocol and documents

The fixed grid contains **36 settings**: learned grouping or contextual classification, body weights {1, 2, 4}, minimum heading scores {0, 0.5, 0.7, 0.85}, and, for the contextual model only, relationship weights {1, 0}. Learned grouping has no relationship decoder. The highest validation joint F0.5 among settings with at least 95% heading precision wins. Exact ties use the first grid entry; an empty output fails the gate. No eligible setting means no selection.

Selection used the existing four validation reports **103, 538, 176 and 128**, with **21 headings on 20 fully reviewed pages**. Twenty-three settings passed the gate; the selected one produced **14 correct predictions, no extras and seven missed titles**, yielding 90.9% joint F0.5. No model weights or annotation labels were changed. Training remains 887 groups across 20 separate WFP reports.

The four 38-heading reports **321, 844, 560 and 394** and the original four league reports were evaluated only after selection was frozen. They have already been inspected in earlier work and are regression sets, not new independent tests. Report URLs, page coverage and split assignments are in the [v2 corpus manifest](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json); the original league reports are in the [main manifest](https://github.com/dividor/pdf-heading-benchmark/blob/main/configs/corpus.json). Source URLs and published annotations enable review; local archive locations are not needed to interpret the results.

This experiment uses the **same title/page matching rule as the main league**, including ≥90% normalized text similarity and exact level. Earlier v2 group F1 used exact source-line membership; its original records remain unchanged. The unchanged baseline was rescored under the new contract for the comparison below.

## Results and trade-offs

| Dataset / configuration | Joint F0.5 | Heading precision | 95% gate | Correct + level | Extra headings | Missed titles | Wrong levels |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Validation / selected | 90.9% | 100.0% | PASS | 14/21 | 0 | 7 | 0 |
| 38-heading regression / baseline | 81.1% | 82.6% | FAIL | 36/38 | 8 | 0 | 2 |
| 38-heading regression / selected | 93.3% | 100.0% | PASS | 28/38 | 0 | 10 | 0 |
| 77-heading historical / baseline | 58.8% | 73.6% | FAIL | 50/77 | 23 | 13 | 14 |
| 77-heading historical / selected | 70.5% | 95.1% | PASS | 34/77 | 2 | 38 | 5 |

On the 38-heading regression set, the selected model emits 28 headings, all correctly leveled, and misses ten. On the historical benchmark it emits 41: 39 genuine headings, five of those at the incorrect level, plus two extras. Thus it misses 38 titles and has 43 joint false negatives. A 95.1% heading precision result from 41 predictions is a narrow sample pass, not evidence of a reliable 95% production guarantee. Labels were produced by one assistant without independent human adjudication. Reusing four validation reports for successive experiments also creates overfitting risk.

The measured historical parse time is **11.66 seconds for all 523 pages**, including native extraction, features, grouping, filtering and sequence inference. Model loading and file writes are excluded. The validation grid reused cached feature/probability calculations; those selection timings are not deployment speed measurements. Runs were local on the shared 48 GB Apple M4 Pro.

The next improvement should recover more genuine headings while preserving this precision floor. That needs more fully reviewed training/validation reports and a new untouched test set, rather than choosing a different cutoff from errors on these inspected pages.

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

**Selection history:** OUR METHOD’s confidence filter was selected on separate validation reports using joint F0.5 with a heading-only precision constraint. The published training procedure has not been changed retrospectively. Its full selection rule, thresholds and provenance are in the method modal and [experiment record](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-precision/report.md).


## Every validation setting

| Variant | Body weight | Min heading score | Relation weight | F0.5 | Precision | Gate |
| --- | --- | --- | --- | --- | --- | --- |
| learned_groups | 1.0 | 0.0 | 0.0 | 66.4% | 82.6% | FAIL |
| learned_groups | 1.0 | 0.5 | 0.0 | 74.3% | 95.0% | PASS |
| learned_groups | 1.0 | 0.7 | 0.0 | 78.7% | 100.0% | PASS |
| learned_groups | 1.0 | 0.85 | 0.0 | 78.7% | 100.0% | PASS |
| learned_groups | 2.0 | 0.0 | 0.0 | 77.3% | 100.0% | PASS |
| learned_groups | 2.0 | 0.5 | 0.0 | 77.3% | 100.0% | PASS |
| learned_groups | 2.0 | 0.7 | 0.0 | 78.7% | 100.0% | PASS |
| learned_groups | 2.0 | 0.85 | 0.0 | 78.7% | 100.0% | PASS |
| learned_groups | 4.0 | 0.0 | 0.0 | 75.3% | 100.0% | PASS |
| learned_groups | 4.0 | 0.5 | 0.0 | 75.3% | 100.0% | PASS |
| learned_groups | 4.0 | 0.7 | 0.0 | 78.7% | 100.0% | PASS |
| learned_groups | 4.0 | 0.85 | 0.0 | 78.7% | 100.0% | PASS |
| context_relations | 1.0 | 0.0 | 1.0 | 73.4% | 86.4% | FAIL |
| context_relations | 1.0 | 0.0 | 0.0 | 73.4% | 86.4% | FAIL |
| context_relations | 1.0 | 0.5 | 1.0 | 82.4% | 87.5% | FAIL |
| context_relations | 1.0 | 0.5 | 0.0 | 82.4% | 87.5% | FAIL |
| context_relations | 1.0 | 0.7 | 1.0 | 90.9% | 100.0% | PASS |
| context_relations | 1.0 | 0.7 | 0.0 | 90.9% | 100.0% | PASS |
| context_relations | 1.0 | 0.85 | 1.0 | 90.9% | 100.0% | PASS |
| context_relations | 1.0 | 0.85 | 0.0 | 90.9% | 100.0% | PASS |
| context_relations | 2.0 | 0.0 | 1.0 | 88.2% | 93.8% | FAIL |
| context_relations | 2.0 | 0.0 | 0.0 | 88.2% | 93.8% | FAIL |
| context_relations | 2.0 | 0.5 | 1.0 | 86.4% | 93.3% | FAIL |
| context_relations | 2.0 | 0.5 | 0.0 | 86.4% | 93.3% | FAIL |
| context_relations | 2.0 | 0.7 | 1.0 | 90.9% | 100.0% | PASS |
| context_relations | 2.0 | 0.7 | 0.0 | 90.9% | 100.0% | PASS |
| context_relations | 2.0 | 0.85 | 1.0 | 90.9% | 100.0% | PASS |
| context_relations | 2.0 | 0.85 | 0.0 | 90.9% | 100.0% | PASS |
| context_relations | 4.0 | 0.0 | 1.0 | 88.2% | 93.8% | FAIL |
| context_relations | 4.0 | 0.0 | 0.0 | 88.2% | 93.8% | FAIL |
| context_relations | 4.0 | 0.5 | 1.0 | 86.4% | 93.3% | FAIL |
| context_relations | 4.0 | 0.5 | 0.0 | 86.4% | 93.3% | FAIL |
| context_relations | 4.0 | 0.7 | 1.0 | 90.9% | 100.0% | PASS |
| context_relations | 4.0 | 0.7 | 0.0 | 90.9% | 100.0% | PASS |
| context_relations | 4.0 | 0.85 | 1.0 | 90.9% | 100.0% | PASS |
| context_relations | 4.0 | 0.85 | 0.0 | 90.9% | 100.0% | PASS |

## Reproduce the experiment

Use the existing [v2 data preparation and training instructions](../structure-v2/report.md). Keep PDFs, cached text and models outside Git. From the repository root, set `DATA` to the external `structure-v2` directory and `MODELS` to its frozen `run-001` directory. `RUN` must be a fresh external output directory.

```bash
uv run python scripts/structure/optimize_precision.py select --data "$DATA" --run "$MODELS" --output "$RUN"
uv run python scripts/structure/optimize_precision.py regression --data "$DATA" --run "$MODELS" --output "$RUN"
uv run python scripts/runners/run_precision.py input.pdf output-dir --run "$MODELS" --selection "$RUN"
```

The selection stage reads only validation documents. It writes its grid and source/model/configuration hashes before evaluating candidates. Regression refuses changed code, weights or labels. Both stages require fresh outputs and preserve raw full-document predictions externally. This published evidence came from run-002; run-001 was superseded after source formatting before regression, with the same grid and no selection based on its outcomes.

The compact [protocol](evidence/protocol.json), [all validation scores](evidence/selection.json), [regression scores](evidence/regression.json) and [historical predictions](evidence/historical-audit.json) are committed. The [inference code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/precision_inference.py) and [optimization runner](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/optimize_precision.py) show the exact implementation.
