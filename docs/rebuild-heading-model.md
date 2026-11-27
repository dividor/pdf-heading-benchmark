# Rebuild and use our combined heading method

This guide covers **OUR METHOD — confidence-filtered v2**, also called the combined method in the discussion. Its three deployed Extra Trees classifiers join text lines, classify headings and predict relationships between heading levels. A validation-selected confidence filter rejects uncertain headings. This is a CPU model for PDFs with selectable text, not an OCR model.

The workflow downloads the exact 28 public World Food Programme (WFP) PDFs in the training manifest, checks every SHA-256 checksum, prepares the committed annotations, fits the trees, selects settings on validation reports and predicts headings. It also downloads the four historical benchmark reports for regression. No private catalogue, archive, original weights, API key or GPU is required.

**Verified November 27, 2026:** the headless notebook completed from a fresh clone with these changes, a new Python environment and an empty data folder. It reproduced the historical heading predictions exactly and wrote Markdown and JSON for the example PDF. The [acceptance record](../outputs/rebuild-check/summary.json) includes settings, counts and source/model hashes. This verifies this combined method only.

## Install from a fresh checkout

Install Git and [uv](https://docs.astral.sh/uv/getting-started/installation/). Use Python 3.12, selected by the repository's `.python-version`. If using an ExFAT drive on macOS, first set `UV_PROJECT_ENVIRONMENT` as shown below. Then run:

```bash
git clone --branch codex/rebuild-training-notebook https://github.com/dividor/pdf-heading-benchmark.git
cd pdf-heading-benchmark
uv sync --locked --extra training --extra notebook
export PDF_BENCHMARK_DATA="$(pwd)/../pdf-heading-benchmark-data"
```

Keep `PDF_BENCHMARK_DATA` outside the checkout and allow space for PDFs, extracted text, logs and models. A new notebook run gets its own timestamped directory. Verified source PDFs can be reused; existing predictions and training runs are not overwritten.

**External drives on macOS:** if the checkout is on an ExFAT drive, put the Python environment on the Mac's native filesystem before running `uv sync`. For example:

```bash
export UV_PROJECT_ENVIRONMENT="$HOME/Library/Caches/pdf-heading-benchmark-venv"
uv sync --locked --extra training --extra notebook
```

The PDFs, model files and prediction outputs still go to `PDF_BENCHMARK_DATA` on the external drive. macOS can create `._` metadata files there; they are not model weights or experiment records.

## Run the notebook

```bash
uv run --extra training --extra notebook jupyter lab notebooks/rebuild_heading_model.ipynb
```

Choose the project Python kernel and **Run All**. The notebook prints the selected settings, regression counts and a heading preview. Its final cell uses a downloaded benchmark PDF by default. To try your own document, change `PDF` to `Path("/path/to/your.pdf")` and choose a fresh `OUTPUT` folder.

To execute the same notebook without opening Jupyter, first create the external data folder:

```bash
mkdir -p "$PDF_BENCHMARK_DATA"
uv run --extra training --extra notebook jupyter nbconvert \
  --to notebook --execute notebooks/rebuild_heading_model.ipynb \
  --ExecutePreprocessor.timeout=1800 \
  --output rebuilt-notebook.ipynb --output-dir "$PDF_BENCHMARK_DATA"
```

Execution stops on an error. Inspect the log for that stage in the new `rebuilds/<timestamp>/` directory. A changed public PDF or annotation mismatch must be investigated; do not change the frozen hashes or labels to get a run through.

## Equivalent terminal steps

These call the same programs as the notebook. The `MODEL_RUN` and `SELECTION_RUN` directories must not already exist. Pick new names for a second training run.

```bash
export STRUCTURE_DATA="$PDF_BENCHMARK_DATA/structure-v2"
export MODEL_RUN="$PDF_BENCHMARK_DATA/rebuilds/manual/models"
export SELECTION_RUN="$PDF_BENCHMARK_DATA/rebuilds/manual/precision"

uv run --extra training python scripts/structure/prepare.py \
  --download --data "$STRUCTURE_DATA"
uv run --extra training python scripts/structure/train.py \
  --data "$STRUCTURE_DATA" --output "$MODEL_RUN"
uv run --extra training python scripts/structure/optimize_precision.py select \
  --data "$STRUCTURE_DATA" --run "$MODEL_RUN" --output "$SELECTION_RUN"

uv run pdf-headings download
uv run --extra training python scripts/structure/optimize_precision.py regression \
  --data "$STRUCTURE_DATA" --run "$MODEL_RUN" --output "$SELECTION_RUN"

uv run python scripts/runners/run_precision.py \
  /path/to/your.pdf "$PDF_BENCHMARK_DATA/my-prediction" \
  --run "$MODEL_RUN" --selection "$SELECTION_RUN"
```

After a notebook run, use the `models` and `precision` directories under its printed run directory instead of the manual paths. The predictor does not require scikit-learn or Jupyter: it reads exported JSON trees with the core dependencies. Model and selection hashes must agree.

## Outputs and checks

| File | What it contains |
| --- | --- |
| `models/selection.json` | Training counts, chosen variant, package versions and model hashes |
| `precision/protocol.json` | Source and model hashes, validation grid and matching rules |
| `precision/selection.json` | Every validation setting and the selected setting |
| `precision/historical-audit.json` | Fresh predictions on the 32 historical audit pages |
| `precision/historical.json` | Historical scores and measured full-document processing times |
| `prediction/structure_precision.md` | Native PDF text with predicted heading markers |
| `prediction/structure_precision.headings.json` | Heading titles, physical PDF page numbers and levels |
| `prediction/structure_precision.document.json` | Native lines, heading groups, boxes and inferred parents |
| `prediction/structure_precision.run.json` | Parser duration and selected settings |

The original validation procedure compares three pipeline variants, then searches 36 decision settings. Only the 20 training reports fit trees; only the four validation reports select settings. The four later reports and four original benchmark reports are previously inspected regression sets. They do not select the model and are not independent evidence of generalization.

The historical result to compare is 41 predictions: 39 matched titles, 34 with the correct level, two extra headings and 70.5% joint F0.5. Do not overwrite the published report merely because a fresh run differs. Model-file hashes may differ because exported JSON includes measured fitting time; compare predictions as well as the recorded settings and versions.

The historical regression parses all 523 PDF pages to retain document-wide context and scores 32 audit pages. Its duration is a **measured 523-page duration**, not a measured 32-page duration. Parser timings exclude model loading and output writes. This rebuild does not replace or validate timings for other models.

## What belongs in Git

Commit code, frozen labels, manifests, compact audit evidence and concise notebook results. Keep downloaded PDFs, raw extraction, model weights and logs outside Git. `.gitignore` protects common data directories, archives, model formats and this model's JSON weight filenames. The existing pre-commit large-file check remains enabled; `.gitignore` does not prevent an intentional `git add -f`.

Before committing changes, run:

```bash
uv run --extra training --extra notebook pytest -q
uv run --extra training --extra notebook pre-commit run --all-files
```
