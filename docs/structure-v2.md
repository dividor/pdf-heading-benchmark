# Training a small local heading model: second experiment

**Current comparison metric:** the league now ranks by joint heading-and-level F0.5 with joint precision and joint recall alongside it; no league-table PASS/FAIL gate. [Definitions and worked example](../../docs/joint-metric.md) · [New precision experiment](../structure-precision/report.md). The F1 results and selection criteria below describe the original frozen experiment; they have not been retroactively changed. Published primary scores use the league's same-page title matching rule.

The selected model improved exact heading-group-and-level F1 from **71.6% to 85.7%** on 32 fully reviewed pages from four fresh WFP reports. It recovered all 38 reference groups, assigned 36 the correct level, and emitted eight extra groups. This is a small pilot using one assistant's labels, without independent human adjudication.

![Training and evaluation pipeline](../../docs/structure-v2-method.svg)

## What changed

The original Extra Trees model had 154 training heading groups from 16 reports. The expanded set has **887 groups from 20 training reports**, including English, French and Spanish. There are 7,039 labelled training lines. These are 859 newly reviewed group decisions (including re-reviewed existing headings) plus retained v1 annotations; they are not 859 additional disjoint headings. Three changes to overlapping v1 annotations are recorded explicitly in `configs/structure-v2/annotation-changes.json`; v1 evidence is unchanged.

Training coverage is deliberately partial. The 112 original fully reviewed training pages supply ordinary-text negatives. Added candidate-guided headings supply positive labels on other pages. Unreviewed lines stay unlabelled. Candidate review used boldness, font size and numbering to propose examples, with extracted text, TOCs and rendered page/snippet inspection to assess them. This can under-sample subtle headings and still contains annotation errors. It is not a complete-document gold corpus.

The four validation reports retain their original 20 reviewed pages and 21 groups. Selection used exact group-and-level F1 on those reports. The final test uses **32 fully reviewed pages and 38 groups from four new reports**: Niger malnutrition interventions (English), anticipatory action in Nepal (English), Chad country strategic plan (French), and Ecuador country strategic plan (Spanish). Each contributes two continuous four-page windows, covering introduction/context and findings. All page numbers are physical PDF pages. Labels and the protocol were frozen before fitting; the test was evaluated after selection. The original four test reports from v1 were excluded entirely.

These are report-disjoint splits, **not template-family-disjoint splits**. For example, the Niger and Chad impact evaluations share a 3ie publishing style. The selection was purposive rather than random and the test has only one H4 and no H5/H6 headings. It does not establish whole-document or cross-publisher accuracy.

## Three controlled variants

1. **Extra annotations only:** retain v1's line features, 200-tree Extra Trees settings and same-block grouping. This isolates the effect of more labels and four extra training reports.
2. **Learned grouping:** a separate tree classifier learns whether adjacent extracted lines belong to one heading, including across PDF block boundaries. Another classifier assigns the resulting group a body/H1–H6 label.
3. **Context and relationships:** add document-wide style/numbering statistics and an exact normalized TOC-title feature. A learned pair model scores whether successive heading levels rise, stay equal or fall; Viterbi decoding combines those scores with group-level probabilities. The relation weight is fixed at 1.0. TOC presence is optional. This is a lightweight context model, not a fine-tuned language model.

All variants use the same training split and seed. Group training uses explicitly annotated groups plus known ordinary-text lines. Pair training only uses pairs whose labels are known. Context features use the input PDF, never reference labels. No report-specific inference corrections were added. The context variant combines extra features and sequence decoding; this experiment does not isolate their individual contributions.

Parent IDs are inferred from the resulting level sequence and remain unevaluated. Native text is retained, but reading order, tables and OCR quality are not solved by this model. Non-adjacent fragments and headings separated by running headers remain possible grouping failures.

## Results and costs

Exact group F1 requires the complete ordered set of source line IDs; matching individual fragments does not count. Exact group-and-level F1 additionally requires the right H level. F1 is `2 × correct / (reference groups + predicted groups)`, so false headings reduce the score. This is stricter than the title-matching metric in the historical league table.

__RESULTS__

**Selection remains the context model**, chosen before looking at the test or historical results. Learned grouping alone scored slightly better on the historical benchmark. That does not justify switching after examining those results. The new context model also regressed slightly on Chad's exact F1 despite getting one more level right: false positives increased. More data is not a substitute for testing individual reports.

__PER_DOCUMENT__

The original 77-heading benchmark was already inspected during development and is now a **diagnostic**. Each new variant ran over all 523 pages, then used the unchanged reference, audit pages and title matcher. Fresh-test F1 and historical correct-heading recall have different denominators and should not be compared directly.

__HISTORICAL__

Runs were local on an Apple M4 Pro with 48 GB RAM. There were no inference API calls or per-page service charges. Dollar costs for electricity, hardware ownership and annotation work were not measured. Model fit time excludes feature preparation, JSON export and validation; inference time includes PDF extraction, features and model inference, but excludes model loading and output writes. The 500-page number below is a linear normalization of an actual 523-page run, not another measured run.

__COSTS__

The selected deployment needs the join, context and relation JSON models. Models, original PDFs, rendered pages and complete extracted text remain outside Git. Published annotations, compact predictions, scores and model/configuration hashes are committed for audit. PyMuPDF's licensing must be considered separately from this repository's MIT code license.

## Source documents and exact coverage

Reports came from the supplied **Evaluation list – Phase 1.xlsx** catalogue and its `20261121T043910Z` local archive snapshot. The reproducible preparation script extracts exact manifest members, verifies their SHA-256 hashes and checks document overlap. It does not require a public download service. Official public source links are listed below; archive filesystem locations are not published. Catalogue entry 962 (GAFSP) was excluded before fitting because it was not a WFP evaluation and was replaced by Niger report 321.

“Full pages” below means every extracted line on those pages has an annotation decision. Extra positive headings can appear elsewhere on training reports. The annotation viewer includes **all 946 groups**, full reviewed pages including zero-heading pages, and pages containing additional positive groups; it distinguishes those coverage types.

__CORPUS__

## Reproduce and run on your own PDF

For a fresh checkout, follow the [complete public-download guide](https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/docs/rebuild-heading-model.md) or [run the notebook](https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/notebooks/rebuild_heading_model.ipynb). That path rebuilds the confidence-filtered method without the private archive or the old v1 model. The commands below reproduce the older comparison when those additional local inputs are available.

Use Python 3.12 and the committed uv lockfile. From a checkout:

```bash
uv sync --locked --extra training
export STRUCTURE_DATA=/path/outside/the/repository/structure-v2
uv run python scripts/structure/prepare.py --data "$STRUCTURE_DATA" --archive /path/to/wfp-20261121T043910Z.tar
uv run python scripts/structure/train.py --data "$STRUCTURE_DATA" --output "$STRUCTURE_DATA/run-001"
uv run python scripts/structure/evaluate.py --data "$STRUCTURE_DATA" --run "$STRUCTURE_DATA/run-001" --original-model /path/to/v1/trees.json
uv run python scripts/structure/predict.py --pdf /path/to/report.pdf --run "$STRUCTURE_DATA/run-001" --output /path/to/new-output.json
uv run python scripts/structure/review.py --data "$STRUCTURE_DATA" --run "$STRUCTURE_DATA/run-001" --output "$STRUCTURE_DATA/viewer"
uv run python scripts/structure/active_review.py --data "$STRUCTURE_DATA" --run "$STRUCTURE_DATA/run-001" --output "$STRUCTURE_DATA/next-review-queue.json"
```

Preparation uses the committed materialized annotations. `compile_annotations.py` can rebuild them from the explicit index decisions and v1 labels; it never generates labels using typography rules. Training/evaluation reject stale configuration hashes and existing run directories. Evaluation additionally needs the four historical PDFs in the sibling `corpus` directory, prepared by the original benchmark instructions, and the frozen v1 model for the before/after comparison. Output JSON contains every native text line, headings and tentative parent IDs; Markdown retains those lines with heading markers.

The package runner is also available through `pdf-headings run structure_context_relations` with `PDF_HEADING_STRUCTURE_RUN` pointing at the trained run. Native digital PDFs are required; scanned documents need a text/OCR stage first.

## Next improvement target

The remaining problem is primarily false positives and transfer across document styles. Review the eight fresh-test false headings as diagnostic examples, but reserve another untouched test set before further tuning. Expand fully reviewed sections, especially caption/table-heavy pages and unnumbered H3–H5 headings; independently check ambiguous labels; and hold out entire template families. The current 887-group training set is the completed first expansion, short of the proposed 1,000–2,000-group target. `active_review.py` ranks up to 200 unlabelled groups from training reports by uncalibrated predictive entropy. It never samples validation or test reports and never turns its suggestions into labels automatically. A queue for the next annotation round has been generated outside Git. A calibrated reject/review option is also a useful next experiment. No confidence calibration or human review guarantee is claimed here.
