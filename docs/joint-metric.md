## Primary metric: heading-and-level F0.5

A useful output must identify a real heading, put it on the correct PDF page and assign the correct level. Invented headings also matter. We therefore rank by **joint heading-and-level F0.5**, and require **at least 95% heading-detection precision** for a configuration to qualify on the evaluated sample. A high score with a FAIL label does not qualify.

Let **G** be the number of reference headings, **P** all predicted headings, **M** the one-to-one title/page matches and **C** those matches with the exact reference level. Matching uses the unchanged same-page, normalized-title similarity ≥0.90 contract. Counts are pooled across reports before calculating metrics (micro averaging).

| Measure | Definition | What it tells us |
| --- | --- | --- |
| Joint precision | C / P | Fraction of emitted headings with both title/page and level correct |
| Joint recall | C / G | Fraction of reference headings recovered at the correct level |
| Joint F1 | 2C / (P + G) | Equal precision/recall emphasis |
| **Joint F0.5** | **1.25C / (P + 0.25G)** | Primary score; emphasizes precision more than recall |
| Heading-detection precision | M / P | Fraction of predictions that are real headings, regardless of level |
| **95% precision gate** | **P > 0 and M / P ≥ 0.95** | At most 5% of emitted headings are spurious on this sample |

Joint true positives are **C**, false positives are **P − C**, and false negatives are **G − C**. A wrong-level heading is both a joint false positive and a joint false negative. A missing heading contributes a false negative; an extra heading contributes a false positive. No predictions gives a zero score and fails the gate. Unknown levels earn no joint credit. The gate concerns real-heading detection; it does **not** mean 95% of levels are correct, and it is an observed sample threshold, not a confidence bound or deployment guarantee.

For example, 10 reference headings, 12 predictions, 10 title matches and 9 correct levels give joint precision 75%, recall 90%, F1 81.8% and F0.5 77.6%. Heading precision is only 83.3%, so this configuration fails the gate despite recovering every title.

For optimization, select the highest validation joint F0.5 **among candidates passing the gate**, then freeze the configuration before evaluation elsewhere. If none qualifies, report no qualifying candidate. Do not choose settings using the main league or inspected regression pages. Existing F1-selected runs retain their original provenance; recomputing these metrics does not retrain them.
