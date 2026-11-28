# Compare Chandra OCR 2 and EvidenceLab on another PDF

Use a fresh external run directory. Both commands process the entire PDF. Run them sequentially so they do not compete for memory. They do not add a new accuracy score to the benchmark.

## Run Chandra OCR 2 on Apple Silicon

After the environment setup in the [README](../README.md):

```bash
export RUN=/path/to/new-run
uv run pdf-headings extract chandra2_mlx /path/to/report.pdf --output "$RUN"
uv run --no-project --python 3.12 --with . --with-requirements configs/environments/mlx.txt \
  python scripts/runners/export_chandra_markdown.py --data "$RUN"
```

The model uses the pinned Chandra OCR 2 weights, upstream layout prompt and image preparation. The exporter uses the pinned author's HTML-to-Markdown converter. It retains headers and footers and omits image placeholders. It does not infer or repair heading levels.

Outputs under `results/document/`:

- `chandra2.markdown.md` contains actual Markdown with physical PDF page markers.
- `chandra2.predicted-headings.json` contains native titles, H levels and physical PDF pages.
- `chandra2.predicted-headings.md` shows the same predictions as an indented list.
- `chandra2_mlx/` retains every raw page response and timing. The older runner's `chandra2_mlx.md` contains raw layout HTML, despite its suffix; use the converted file above for Markdown.

An error, exhausted output-token limit or empty conversion stops the export. A page without a heading is retained in the full text.

## Run EvidenceLab on the same PDF

After Chandra exits:

```bash
uv run python scripts/runners/benchmark_evidencelab.py \
  --data "$RUN" --manifest "$RUN/corpus/manifest.json" \
  --output "$RUN/evidencelab/run-001"
```

This uses the [pinned EvidenceLab image and parser settings](../configs/evidencelab.json) in an isolated container. It runs Docling and EvidenceLab's post-processor with four CPU cores and a 12 GB memory limit. It does not use a running service's database. If your external drive cannot store symbolic links, put the EvidenceLab output and cache on an APFS volume.

Look in `evidencelab/run-001/parsed/other/document/` for `document.md` and `toc.txt`. The final TOC is EvidenceLab's native heading output, including its level normalization and title truncation. Keep that distinct from the headings embedded in Markdown. `protocol.json`, `model-files.json` and `timing.json` record the inputs, versions and measured processing time.

Export a readable heading list without changing native predictions:

```bash
uv run python scripts/runners/export_evidencelab.py \
  --run "$RUN/evidencelab/run-001" --document document --output "$RUN/exports"
```

The copied Markdown is unchanged, including any image paths inside it. The exported heading list comes from the final TOC rather than Markdown heading marks.

## The November 28 demonstration

We selected *Operation Evaluations Series: Regional Synthesis 2013–2017, Southern Africa Region* (WFP, November 2017; archive ID 351; 36 pages) before inference. Its SHA-256 is `e8665cbc2d0ff7cb50365710e8a2a9d018593241a2a2f26182052816a40c6c3a`.

Neither its archive ID nor its file hash occurs in `configs/corpus.json`, `configs/supervised/corpus.json`, `configs/structure-v2/corpus.json` or `configs/supervised/excluded.json`. This checks separation from our training, validation and benchmark documents. It does not establish whether the document appeared in a model provider's pretraining data.

The external run stores `selection.json` with the source location and the hashes of those four manifests. Raw PDFs, model weights and page responses remain outside Git.

### Recorded status

EvidenceLab completed all 36 pages in 159.7 seconds and returned 48 final TOC entries (8 H1, 33 H2, 7 H3). Its Markdown contains 51 headings at H2–H4; neither output was adjusted to agree with the other.

Chandra weights are ready, but new-document inference was blocked before startup by the memory guard: 15.0 GiB available versus 18 GiB required, including the reserve. No Chandra predictions or accuracy claims are recorded for this document. The official Markdown converter was separately exercised on two saved benchmark page responses.

[Selection and run record](../outputs/unseen/southern-africa-2017.json).
