# PDF heading benchmark

Code and evidence for a blog experiment: how well do local PDF parsers recover heading text **and its correct level**?

The benchmark uses four public **World Food Programme (WFP)** evaluation reports: 523 pages, with 77 annotated headings on 32 selected pages. The report compares 34 local configurations. Its primary score, **joint F0.5**, rewards correct heading–level pairs and penalizes extra headings and wrong levels. These are assistant-reviewed labels on a small, deliberately selected sample, not a general accuracy benchmark.

[Results and methods](outputs/report/league_table.md) · [Interactive HTML](outputs/report/index.html) · [Validation status](docs/validation.md) · [Source PDFs and checksums](configs/corpus.json)

**Main finding:** larger models recovered more correct heading levels, but their processing times can limit practical use. Our small trained CPU method is fast, yet its best precision-focused configuration recovered only 34 of 77 headings at the correct level. Read the complete results before choosing a parser.

## Choose a starting point

| You want to… | Start here |
| --- | --- |
| Recalculate the published scores without downloading models | Run the commands below |
| Train and use our combined heading method | [Step-by-step guide](docs/rebuild-heading-model.md) · [Notebook](notebooks/rebuild_heading_model.ipynb) |
| Run a parser on the benchmark or your own PDF | [Parser commands](docs/run-parsers.md) |
| Check which fresh runs reproduced the table | [Validation record](docs/validation.md) |
| Inspect settings, predictions and method diagrams | Open `outputs/report/index.html` after cloning |

## Recalculate the published scores

Requires Git and [uv](https://docs.astral.sh/uv/). The repository selects Python 3.12.

```bash
git clone --branch codex/full-method-verification https://github.com/dividor/pdf-heading-benchmark.git
cd pdf-heading-benchmark
uv sync --locked
uv run pdf-headings score --historical
uv run pdf-headings report
```

The validation work is currently on this feature branch, in [PR #12](https://github.com/dividor/pdf-heading-benchmark/pull/12). These commands score committed predictions and regenerate the report offline; they do not rerun model inference. GitHub shows the HTML source, so download or clone it to open the interactive report.

## Train our method from scratch

Follow the [rebuild guide](docs/rebuild-heading-model.md). It downloads and verifies 28 public training/validation/regression reports, fits the classifiers, selects settings on validation reports, then predicts headings on the four separate benchmark reports. No original weights, private archive, GPU or API key is needed.

The fresh notebook run reproduced all historical heading predictions for the combined method. It produced **41 predictions, 34 correct heading–level pairs, two extra headings and 70.5% joint F0.5**. It still misses many headings: correct-level recall is **44.2%**. [Acceptance evidence](outputs/rebuild-check/summary.json).

## What is verified?

Fresh runs have reproduced the audit predictions of **12 configurations exactly**, including all seven small trained variants, PyMuPDF4LLM, three Docling variants and Marker. Qwen received configuration and adapter checks without another generation run, as requested. MinerU basic stopped when host memory pressure rose. Other fresh model runs remain incomplete.

The [validation record](docs/validation.md) distinguishes these checks from the original measured runs. Published scores remain unchanged. A runnable adapter is not, by itself, proof that its fresh installation reproduces the original result.

## Keep downloads outside Git

```bash
export PDF_BENCHMARK_DATA="$PWD/../pdf-heading-data"
export HF_HOME="$PDF_BENCHMARK_DATA/cache/huggingface"
export UV_CACHE_DIR="$PDF_BENCHMARK_DATA/cache/uv"
```

PDFs, weights and raw responses belong there. Git contains code, labels, source manifests and compact result evidence. `.gitignore` and the pre-commit large-file check protect common data and model formats. See the rebuild guide for Python environments on ExFAT drives.

## Methods and limitations

- [Scoring and matching rules](docs/joint-metric.md), [sampling and timing limits](docs/reproducibility.md).
- [Training provenance](docs/model-provenance.md), [annotation viewer](docs/annotation-review/README.md).
- [OCR field comparison](docs/published-comparison.md), [official parsing pipelines](docs/official-pipelines.md), [EvidenceLab and forced OCR](docs/evidencelab-and-ocr.md).
- [Earlier experiments and illustrations](docs/experiment-notes.md), including why section headings matter for finding relevant text.

![Correct heading levels versus incorrect classification](docs/images/heading-classification.png)

*Illustration, not model output. Heading levels help distinguish a summary’s findings from an acronyms section or ordinary body text.*

## Repository and quality checks

`src/` contains scoring, the CLI and reporting; `scripts/` contains model adapters and training; `configs/` holds sources, labels and version pins; `outputs/` holds compact published evidence; `tests/` checks application code. Notebooks call the same scripts as the terminal instructions.

```bash
uv sync --locked --all-extras
uv run pre-commit install
uv run pre-commit run --all-files
uv run pytest -q
```

CI checks formatting, types, security, complexity, tests and deterministic reports. Read [CONTRIBUTING.md](CONTRIBUTING.md). Code is MIT licensed; models and documents retain their own [licenses](THIRD_PARTY_NOTICES.md).
