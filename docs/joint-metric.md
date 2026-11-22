## Primary metric: heading-and-level F0.5

A useful output must identify a real heading, put it on the correct PDF page and assign the correct level. Invented headings also matter. We therefore rank by **joint heading-and-level F0.5**, supported by **joint precision** and **joint recall**. All three require the heading and its level to be correct. There is no separate PASS/FAIL qualification gate.

Let **G** be the number of reference headings, **P** all predicted headings, **M** the one-to-one title/page matches and **C** those matches with the exact reference level. Matching uses the unchanged same-page, normalized-title similarity ≥0.90 contract. Counts are pooled across reports before calculating metrics (micro averaging).

| Measure | Definition | What it tells us |
| --- | --- | --- |
| Joint precision | C / P | Fraction of emitted headings with both title/page and level correct |
| Joint recall | C / G | Fraction of reference headings recovered at the correct level |
| Joint F1 | 2C / (P + G) | Equal precision/recall emphasis |
| **Joint F0.5** | **1.25C / (P + 0.25G)** | Primary score; emphasizes precision more than recall |
| Heading-detection precision | M / P | Diagnostic only: real headings regardless of level; shown in detailed results |

Joint true positives are **C**, false positives are **P − C**, and false negatives are **G − C**. A wrong-level heading is both a joint false positive and a joint false negative. A missing heading contributes a false negative; an extra heading contributes a false positive. No predictions gives a zero score. Unknown levels earn no joint credit. Heading-only precision ignores wrong levels, so it is a diagnostic rather than a quality requirement.

For example, 10 reference headings, 12 predictions, 10 title matches and 9 correct levels give joint precision 75%, recall 90%, F1 81.8% and F0.5 77.6%. Recovering every title does not imply correct hierarchy.

MinerU basic illustrates why the distinction matters: 66 of its 68 predictions match real titles, but only 31 have the correct level. Its joint precision is **45.6% (31/68)**, joint recall **40.3% (31/77)** and joint F0.5 **44.4%**. The 97.1% heading-only precision ignores 35 wrong levels. OUR METHOD's confidence-filtered configuration has **82.9% joint precision (34/41)** and **44.2% joint recall (34/77)**, yielding **70.5% joint F0.5**. Its two extra headings are separate from its five wrong-level headings.

For future optimization, select using validation joint F0.5, report joint precision and recall alongside it, then freeze the configuration before evaluation elsewhere. Do not choose settings using the main league or inspected regression pages.

**Historical selection remains unchanged:** the published 36-setting confidence-filter experiment selected the highest validation joint F0.5 among candidates with at least 95% heading-only precision. That was its actual selection rule, and its protocol and results remain available. We have removed this gate from the league table because it ignores level errors. Recomputing or presenting joint metrics does not retrain models or retroactively change how any configuration was selected.
