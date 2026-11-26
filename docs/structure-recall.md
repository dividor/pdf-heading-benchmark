# OUR METHOD: retraining for greater coverage

**Outcome: coverage improved over the confidence-filtered model, but the practical quality problem remains.** On the original 77-heading benchmark, this experiment recovers 66 titles (85.7%), with 50 at the right level (64.9%) and 21 extras. The confidence-filtered model recovered 39 titles, with 34 at the right level and two extras. The older unfiltered context model already had 50 correct heading-level pairs and 23 extras. This is not a breakthrough or a production-ready result.

Published run: **structure-recall/run-002**. It repeats the initial trial after adding explicit Python type annotations; the selected settings and heading predictions are unchanged. Run directories are kept separate.

## Predeclared experiment

We refitted three Extra Trees classifiers from scratch on the unchanged 20-report training set: 6,267 line-join pairs, 6,736 heading/body groups and 867 heading-relation pairs. Data, annotations and feature construction are unchanged from [the documented training provenance](../../docs/model-provenance.md). No original league-table labels were used for fitting or selection.

Eight tree configurations crossed maximum depth {16, unlimited}, minimum samples per leaf {1, 2}, and feature sampling {0.8, 1.0}. Each classifier had 200 trees, balanced class weighting, random seed 42 and four CPU workers. Each bundle was evaluated with eight decision configurations: body multiplier {0.75, 1}, heading-score cutoff {0, 0.5}, and relationship weight {0, 1}. This is **64 validation configurations**.

The predeclared objective was highest validation joint F0.5 among configurations reaching **at least 80% joint precision and 80% joint recall**. If none met both, the protocol specified a diagnostic fallback maximizing the smaller of joint precision and recall, then F0.5; exact ties retain grid order. These were pilot targets, not claims of acceptable production quality.

**No configuration met both targets.** The fallback has unlimited tree depth, one sample per leaf and all features available at splits. It uses body multiplier 1, no confidence cutoff and **relationship weight 0**. Three classifiers were fitted, but the selected inference path uses only the line-join and context classifiers (400 trees); its fitted relation model is unused. The output is still a learned classifier using engineered features, not a rule-free or language-understanding model.

Validation has 21 headings in four reports. The selected configuration gets 16 right, emits 19 predictions, and has 84.2% joint precision / 76.2% joint recall. This small reused validation sample is vulnerable to selection overfitting. The original league and previously inspected 38-heading test were evaluated only after selection; both are regression evidence, not fresh independent tests.

## Results

__RESULTS__

The selected model takes **16.42 seconds over all 523 pages**, including native-text extraction, features and inference, excluding model loading and writes. It ran on the local 48 GB M4 Pro. The training record gives Python 3.12.3, scikit-learn 1.9.1 and macOS 26.1 arm64. Full raw text and model weights remain outside Git; compact audit predictions and all validation scores are committed.

## What this establishes

Changing tree capacity and decision settings can recover titles that the confidence filter discarded. It has not solved generalization: the selected model reaches 94.7% joint recall on the inspected 38-heading set but 64.9% on the original league, with substantially more extras. Further threshold or tree-parameter searches on these same small sets risk selecting quirks rather than improving the method.

The next substantive experiment should expand independently reviewed, fully labeled sections across report styles, including hard negatives such as table labels and captions, and hold out whole template families. Document-level semantic context or a local language-model review stage is another candidate; its extra runtime must be measured. These are proposed next experiments, not completed improvements.

## Evidence and reproduction

[Protocol recorded before fitting](evidence/protocol.json) · [All 64 validation results and selected model hashes](evidence/selection.json) · [Validation and inspected-test results](evidence/regression.json) · [Original league results](evidence/historical.json) · [Page-restricted predictions](evidence/historical-audit.json).

Prepare the unchanged dataset using the [original instructions](../structure-v2/report.md), then:

```bash
export STRUCTURE_DATA=/path/outside/the/repository/structure-v2
export RECALL_RUN=/path/outside/the/repository/structure-recall/new-run
uv sync --locked --extra training
uv run python scripts/structure/retrain_recall.py --data "$STRUCTURE_DATA" --output "$RECALL_RUN"
uv run python scripts/structure/evaluate_recall.py --data "$STRUCTURE_DATA" --output "$RECALL_RUN"
uv run python scripts/runners/run_recall.py /path/to/new.pdf /path/to/new-output-directory --run "$RECALL_RUN"
```

Use new output paths. Evaluation checks the training configuration, relevant source hashes and saved model hashes. Raw model JSON hashes include recorded fit times, so they identify saved artifacts rather than promise identical hashes from fresh fitting. The selected model is a diagnostic fallback, not a candidate that met the stated validation targets.
