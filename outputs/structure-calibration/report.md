# Can stricter heading decisions improve the model?

**Yes on one regression set, but not consistently across report styles. This candidate does not replace the selected v2 model.** The existing models, training labels and native text extraction are unchanged. This experiment tunes two global decoding weights using only the four validation reports, then measures the chosen setting on previously inspected reports.

## Experiment and documents

The original v2 corpus has 20 training reports (887 heading groups), four validation reports (21 groups on 20 fully reviewed pages) and four test reports (38 groups on 32 fully reviewed pages). The four test reports were already inspected during v2 analysis, so they are now a **regression set**, not a fresh test. There is no template-family holdout or independent human annotation audit.

The regression reports are WFP malnutrition interventions in Niger (321, English), anticipatory action in Nepal (844, English), the Chad country strategic plan (560, French) and the Ecuador strategic plan (394, Spanish). The [corpus manifest with public source URLs and exact physical PDF pages](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/configs/structure-v2/corpus.json) records all training, validation and regression documents. These are separate from the four historical PDFs in the main league table.

Each candidate multiplies the classifier's **body-class decision score** by 1, 1.5 or 2 before choosing body versus a heading level. This is decision-weight tuning, not a claim that tree probabilities are calibrated. The level relationship decoder has weight 1, 0.5 or 0. All nine combinations were specified before the validation search. Exact group-and-level F1 selects the winner; ties retain the first setting, with the original baseline first. Selection chose **body weight 2, relationship weight 1**. No title strings, report IDs or language-specific correction rules are used at inference.

A preliminary run confirmed the same grid result. The recorded second run repeats that fixed grid and includes the full historical comparison. No fresh-test claim is made for either run. Frozen model/config/code hashes and all nine validation scores are in [the evidence directory](https://github.com/dividor/pdf-heading-benchmark/tree/codex/technique-explorer/outputs/structure-calibration/evidence).

## Results on the previously inspected 38-heading set

| Setting | Validation F1 | Regression F1 | Recovered | Correct + level | False |
| --- | --- | --- | --- | --- | --- |
| baseline | 69.8% | 85.7% | 38/38 | 36/38 | 8 |
| selected | 81.1% | 94.7% | 37/38 | 36/38 | 1 |

Exact group-and-level F1 is `2 × correct groups with levels / (reference groups + predicted groups)`. A match requires identical source-line membership and the correct level. It rewards removing false headings and penalizes missed headings. **36/38 correct remains unchanged:** seven false headings disappear, one real heading is missed, and one previously wrong level becomes correct. The stricter heading selection also changes which headings are adjacent for the sequence decoder.

| Report ID | Exact F1 | Recovered | Correct + level | False |
| --- | --- | --- | --- | --- |
| 321 | 100.0% | 10/10 | 10/10 | 0 |
| 844 | 100.0% | 8/8 | 8/8 | 0 |
| 560 | 85.7% | 10/10 | 9/10 | 1 |
| 394 | 94.7% | 9/10 | 9/10 | 0 |

## Historical four-report comparison

The main table uses a different contract: 77 reference headings, same-page normalized title matching, then an exact level check. It reports recall and false headings separately, not F1. Both configurations processed all 523 pages; only the same 32 historical audit pages were scored.

**Original v2: 64/77 recovered, 50/77 correct with levels, 23 false headings. Calibrated candidate: 59/77 recovered, 47/77 correct with levels, 21 false headings.** Correct-level recall falls from 64.9% to 61.0%. This is why the candidate is not promoted as a general improvement.

| Report | Recovered | Correct + level | False |
| --- | --- | --- | --- |
| targeting | 15/15 | 9/15 | 9 |
| midterm | 16/18 | 15/18 | 2 |
| indonesia | 12/21 | 11/21 | 10 |
| colombia | 16/23 | 12/23 | 0 |

Measured calibrated CPU time: **14.47 seconds / actual 523 pages; 13.83 seconds normalized to 500 pages.** This includes PDF extraction, features, grouping and decoding; excludes model loading and output writes. Hardware: shared Apple M4 Pro, 48 GB. The same 23.2 MiB of deployed JSON model components are reused. No additional model training or paid inference was performed. Hardware ownership, electricity and annotation work are not priced here.

## Validation search

| Body weight | Relationship weight | Validation exact F1 |
| --- | --- | --- |
| 1.0 | 1.0 | 69.8% |
| 1.0 | 0.5 | 69.8% |
| 1.0 | 0.0 | 69.8% |
| 1.5 | 1.0 | 76.9% |
| 1.5 | 0.5 | 76.9% |
| 1.5 | 0.0 | 76.9% |
| 2.0 | 1.0 | 81.1% |
| 2.0 | 0.5 | 81.1% |
| 2.0 | 0.0 | 81.1% |

Only 21 validation headings support this choice, and relationship weight makes no difference to this sample's F1. More representative validation pages are needed before choosing a production threshold.

## Reproduce and use

Run from the repository root after preparing and training v2 as described in [the v2 instructions](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md). Keep PDF data and model files outside Git. Choose a new calibration directory for each search.

```bash
uv run python scripts/structure/calibrate.py select \
  --data "$PDF_HEADING_DATA/structure-v2" \
  --run "$PDF_HEADING_DATA/structure-v2/run-001" \
  --output "$PDF_HEADING_DATA/structure-calibration/my-run"

uv run python scripts/structure/calibrate.py regression \
  --data "$PDF_HEADING_DATA/structure-v2" \
  --run "$PDF_HEADING_DATA/structure-v2/run-001" \
  --output "$PDF_HEADING_DATA/structure-calibration/my-run"

uv run python scripts/structure/predict.py \
  --pdf /path/to/new-report.pdf \
  --run "$PDF_HEADING_DATA/structure-v2/run-001" \
  --variant context_relations \
  --calibration "$PDF_HEADING_DATA/structure-calibration/my-run" \
  --output /path/to/new-output.json
```

Omit `--calibration` to retain the original v2 behavior. The optional calibrated runner rejects settings from a different model bundle. These parameters change heading decisions only; full native text remains available in JSON and Markdown.

## What would improve reliability next?

1. Add fully reviewed training pages with boxed findings, captions, table headings and emphasized prose. Label all non-headings on those pages, so the model learns their distinction from headings.
2. Expand complete heading sequences across languages and report templates, including rare deeper levels. More positive-only headings will not address the false-positive problem by themselves.
3. Reserve untouched report families before further tuning; keep this regression set and the original league corpus for diagnostics. Choose global settings on larger validation samples.
4. Review uncertain predictions rather than automatically accepting classifier scores as calibrated confidence. Audit the source annotations independently.

These steps are proposed follow-up work; this experiment measures decoding calibration only.
