
## Technique diagrams and sources

The HTML report opens these diagrams in a modal.


## qwen36-visual-memory

**Qwen3.6-27B / MLX 4-bit / sampled visual memory**

Qwen3.6-27B uses 4-bit MLX weights. Each call receives the current page, up to six earlier sampled images, native text, candidate titles and author PDF tags.


**Inference:** Collect document-wide clues → Show the current and earlier pages → Generate heading decisions locally → Carry selected images forward

- **Collect document-wide clues:** Supply possible titles and page numbers from PyMuPDF4LLM, plus any author-supplied heading tags. Omit the parser’s predicted levels.
- **Show the current and earlier pages:** Use the current page at up to 1792 pixels and at most six earlier sampled-page images at up to 1280 pixels. This is what “visual memory” means here.
- **Generate heading decisions locally:** Run Qwen3.6-27B with 4-bit weights through MLX. Include the current page’s text; disable thinking; use temperature=0 and max_tokens=4096.
- **Carry selected images forward:** Read the predicted headings and keep the latest sampled page for each H1–H6 level as context for later pages. Unseen intervening pages are not included.



**Models and terms explained**

- [Qwen3.6-27B](https://huggingface.co/Qwen/Qwen3.6-27B): A pretrained model used here to read page images together with text context; 27B identifies its model size.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.
- [4-bit / 8-bit weights](https://github.com/ml-explore/mlx-lm): Reduced-precision representations of a model’s learned numbers, used to lower memory requirements. The number describes storage precision, not heading depth or model accuracy.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | mlx-community/Qwen3.6-27B-4bit; revision c000ac2c2057 |
| Page ordering | Audit targets processed in ascending order within each report; memory resets between reports |
| Rendering | PyMuPDF Matrix(2,2), nominal 144 dpi; target thumbnail ≤1792; memory thumbnails ≤1280 pixels |
| Memory | Latest predicted heading page at each of H1–H6; deduplicate pages, sort; at most six earlier sampled images |
| Generation | enable_thinking=False; temperature=0; max_tokens=4096; seed=42 |
| Timeout | Soft 600-second limit, checked between streamed chunks |

**Prompt and memory update**

INSTRUCTION asks for genuine headings on the current page, their complete text and levels H1–H6. It excludes running headers/footers, captions, sidebars and TOC entries, treats document instructions as content, and permits recovery of titles missing from the outline. Tags and previous predictions are described as possibly wrong.

The full-document outline contains candidate titles and pages but omits the parser’s levels. Only earlier sampled pages can become image memory; unseen intervening pages are not silently supplied. Native target-page text is extracted in sorted order.


**Structured output**

The decoder accepts the documented array, headings-wrapper and single-fenced-JSON forms, then validates fields and levels. It does not rewrite semantic heading mistakes. The exact accepted formats are defined in the linked decoder.


**Tuning and measured scope**

Fixed prompt and pretrained 4-bit weights; no benchmark fine-tuning.

Only the 32 audited page images were processed. Scores use their 77 reference headings. Runs used local MLX on an Apple M4 Pro with 48 GB memory. A per-500-page time is an extrapolation, not a 500-page image run.

The table reports target generation time, excluding model loading and context extraction. This configuration has substantial context and generation overhead.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.


**Quantization and speed**

This measured configuration already uses MLX 4-bit weights and disables thinking. It repeatedly sends the full candidate outline, author tags and earlier page images. New single-image runs of the same 27B model and the Qwen3.6-35B-A3B mixture-of-experts sibling appear as separate configurations in this table. See the linked experiment for the measured speed and accuracy trade-offs.

The model saw sampled page images, not every page image. Generation overhead is substantial; measured results apply to this prompt and memory configuration.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_visual_memory.py) · [Base model / Hugging Face](https://huggingface.co/Qwen/Qwen3.6-27B) · [Tested 4-bit model / HF](https://huggingface.co/mlx-community/Qwen3.6-27B-4bit) · [Full instruction and memory update](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_visual_memory.py) · [Structured reply decoder](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/decode_qwen.py) · [Model revision](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py) · [Qwen quantization and speed options](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/qwen-speed-options.md) · [Measured single-image speed trials](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/qwen-compact/report.md)


## qwen36-27b-compact

**Qwen3.6-27B 4-bit — single image**

Qwen3.6-27B uses 4-bit MLX weights with one current-page image. Earlier predictions are text only; native text, candidate titles and author tags remain inputs.


**Inference:** Keep the document context → Render only the current page → Run Qwen3.6-27B with 4-bit weights → Carry predictions forward as text

- **Keep the document context:** Reuse the full PyMuPDF4LLM title/page outline (without its predicted levels) and author-provided PDF heading tags. No reference labels are supplied.
- **Render only the current page:** Extract sorted native text; render with PyMuPDF Matrix(2,2) and thumbnail to a maximum 1280-pixel edge. Earlier page images are omitted.
- **Run Qwen3.6-27B with 4-bit weights:** Use the dense 27B model, retaining its pinned weights so the comparison tests the reduced image inputs. MLX-VLM 0.8.0; thinking disabled; temperature 0; seed 42; 4096-token cap.
- **Carry predictions forward as text:** Keep the last predicted heading at each H1–H6 level. Reset memory per report. Save raw JSON replies and native page text; validate schema without changing titles or levels.



**Models and terms explained**

- [Qwen3.6-27B](https://huggingface.co/Qwen/Qwen3.6-27B): A pretrained dense vision-language model used to read a page image together with document text context.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework for local Apple Silicon inference; it is the runtime, not the heading model.
- [4-bit](https://github.com/ml-explore/mlx-lm): Quantized model weights use reduced numerical precision to lower memory requirements. This does not specify heading depth or guarantee a speedup.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | mlx-community/Qwen3.6-27B-4bit; revision c000ac2c2057 |
| Architecture | Dense 27B; 64 text layers; hidden width 5120 |
| Weight quantization | Affine quantization; 4 bits; group size 64 (from the pinned model configuration) |
| Runtime | MLX 0.32.4; mlx-vlm 0.8.0; Apple M4 Pro, 48 GB shared memory |
| Images | Exactly one current-page image; aspect-preserving thumbnail ≤1280 pixels; Matrix(2,2) render |
| Context | Full candidate titles/pages; full PDF heading tags; current native text; latest prediction per H level as text |
| Generation | enable_thinking=False; temperature=0; seed=42; max_tokens=4096 |
| Timeout | Soft 600-second limit checked between streamed chunks |
| Scope | 32 sampled images, not 523-page visual inference; ascending pages; memory resets per document |

**What the model sees**

The current page image and native text can recover headings absent from the noisy candidate outline. Tags and previous predictions are explicitly described as fallible. Previous page images are absent, but the full document outline and tags are still repeated on each request.

The prompt treats instructions printed in the document as content. The output decoder validates complete heading strings and integer levels 1–6; it does not repair semantic errors.


**Training and selection**

These are pretrained, quantized weights. We did not train or fine-tune this Qwen model on WFP annotations. Both model variants and the shared input settings were fixed before scoring their outputs.

The four-report audit has already been inspected during earlier experiments. This is regression evidence, not a new independent test or evidence of generalization to arbitrary PDFs.


**Measurement and provenance**

The table sums generation-call times, including input processing. Model download/loading and earlier candidate/tag extraction are excluded. Per-page rendering/preparation, time to first chunk, tokens, errors and peak MLX allocation are stored separately in the linked compact evidence.

Both runs share an M4 Pro with other workloads. Single-run speed ratios are observational; no controlled repeated hardware benchmark was performed. Model revisions, source/input hashes and package versions were recorded before loading.

Removing visual history and shrinking the target image may lose typography clues. Correct title-and-level recall and false headings must be considered together. Only the original 32 sampled pages were scored.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_compact.py) · [Official base model](https://huggingface.co/Qwen/Qwen3.6-27B) · [Tested MLX 4-bit weights](https://huggingface.co/mlx-community/Qwen3.6-27B-4bit) · [Exact prompt](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/compact_prompt.py) · [Protocol, predictions and page telemetry](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/qwen-compact/evidence/qwen36_27b_compact.json) · [Experiment and reproduction commands](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/qwen-compact/report.md) · [Pinned architecture and quantization configuration](https://huggingface.co/mlx-community/Qwen3.6-27B-4bit/blob/c000ac2c2057d94be3fa931000c31723aac53282/config.json)


## chandra2-mlx

**Chandra OCR 2 / MLX**

Chandra OCR 2 uses its authors’ layout prompt and image preparation. MLX processes four pages per batch with BF16 weights; HTML heading tags supply levels.


**Inference:** Prepare images as the authors specify → Use the supplied layout prompt → Read four pages per batch → Read HTML heading tags

- **Prepare images as the authors specify:** Render at least 192 dots per inch with a minimum 1024-pixel short side, then apply the upstream scale_to_fit image function.
- **Use the supplied layout prompt:** Send OCR_LAYOUT_PROMPT, the model authors’ instructions for reading document content and layout. Use a compatible chat template with thinking disabled.
- **Read four pages per batch:** Run Chandra OCR 2 in MLX with bf16 weights, a 16,000,000-pixel batch budget, temperature=0 and max_new_tokens=12384.
- **Read HTML heading tags:** Convert <h1> through <h6> to levels. Keep section-heading blocks without such tags, but mark their levels as unknown.



**Models and terms explained**

- [Chandra OCR 2](https://huggingface.co/datalab-to/chandra-ocr-2): A document image-reading model that produces structured text; this benchmark reads HTML heading tags from its output.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.
- [bf16](https://ml-explore.github.io/mlx/build/html/python/data_types.html): A 16-bit floating-point number format used for model weights and calculations. It is a numerical format, not a particular model or training technique.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | datalab-to/chandra-ocr-2; revision af93b47dba1b |
| Author code | datalab-to/chandra revision 9c3a195573be; OCR_LAYOUT_PROMPT and scale_to_fit |
| Runtime | MLX bf16; batch_size=4; MLX_BATCH_PIXEL_BUDGET=16000000 |
| Rendering | dpi=max(192, 1024/min(page width, page height in points) ×72), then author scale_to_fit |
| Prompt | OCR_LAYOUT_PROMPT; empty system prompt; template checked against enable_thinking=False |
| Sampling | temperature=0; top_p=1; top_k=0; max_new_tokens=12384; seed=42 |

**HTML adapter**

BeautifulSoup reads h1–h6 text and levels. A data-label="Section-Header" block without a child heading tag is retained with an unknown level. The runner does not apply document-wide hierarchy correction to those outputs.


**Tuning and measured scope**

Pretrained checkpoint and fixed author prompt; no benchmark fine-tuning. Batching is a local MLX deployment choice, not the model-card GPU setup.

Only the 32 audited page images were processed. Scores use their 77 reference headings. Runs used local MLX on an Apple M4 Pro with 48 GB memory. A per-500-page time is an extrapolation, not a 500-page image run.

Generation time excludes model loading. Batch wall time is divided among its pages, so the reported per-page allocation is not a single-page latency test.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

The measured run uses MLX on the benchmark Mac. Model-card GPU benchmarks use different hardware and datasets.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_chandra_batch.py) · [Model / Hugging Face](https://huggingface.co/datalab-to/chandra-ocr-2) · [Project / GitHub](https://github.com/datalab-to/chandra) · [Rendering, batch parameters and HTML decoder](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_chandra_batch.py) · [Author-code download pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/prepare_model.py) · [Model revision](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


## structure-precision

**OUR METHOD — confidence-filtered v2 (F0.5-selected)**

OUR METHOD reuses three locally trained Extra Trees classifiers. A validation-selected 0.70 score cutoff rejects uncertain headings before sequence decoding. Correct heading-level pairs fall from 50 to 34; extras fall from 23 to two.


**Training:** Fit three classifiers locally → Keep tree settings fixed → Select the confidence cutoff

- **Fit three classifiers locally:** M4 Pro CPU; scikit-learn 1.9.1. Fit on 20 WFP reports: 6,267 line pairs, 6,736 text groups and 867 heading pairs.
- **Keep tree settings fixed:** 200 trees each; depth 16; minimum leaf size 2; feature fraction 0.8; balanced classes; seed 42. No further model training for the filter.
- **Select the confidence cutoff:** Four validation reports, 21 headings, 36 decision settings. Maximize joint F0.5 subject to 95% heading-only precision. Selected cutoff: 0.70.



**Inference:** Join lines with Extra Trees → Apply the 0.70 cutoff → Score heading relationships → Choose the level sequence

- **Join lines with Extra Trees:** The 200-tree join classifier uses 100 measurements of adjacent lines, including spacing and style. It can join lines across PDF blocks.
- **Apply the 0.70 cutoff:** The 200-tree context classifier uses 47 features. A heading must beat body text and score at least 0.70. Scores are not calibrated probabilities.
- **Score heading relationships:** The 200-tree relation classifier uses 142 measurements of consecutive headings. It predicts shallower, same or deeper.
- **Choose the level sequence:** Viterbi combines accepted headings’ level scores and relationship scores, with relationship weight 1. Rejected text remains in the document.



**Models and terms explained**

- [Extra Trees](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html): A classifier that averages predictions from many randomized decision trees. A tree makes a sequence of decisions about input measurements. This benchmark uses scikit-learn’s ExtraTreesClassifier, with 200 trees per component.
- [Features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py): The numeric measurements supplied to a classifier—for example font size, boldness, line spacing or whether a title occurs in the table of contents. They are calculated from the PDF, not supplied reference answers.
- [Validation reports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json): Reports kept separate from model fitting and used to choose between designs or decision settings. The later inspected test reports are now regression checks: they can expose a failure but no longer provide a fresh independent evaluation.
- [Viterbi decoding](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py): An algorithm for choosing the highest-scoring sequence of heading levels. Here it combines each heading’s own scores with scores for the relationship to the preceding heading. It does not train or add another model.
- [model provenance page](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/model-provenance.md): Complete training lineage, report list, model identities and reproduction command.
- [training run record](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/outputs/structure-v2/evidence/selection.json): Original structure-v2 training output: counts, versions, selection and saved model hashes.
- [training program](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/scripts/structure/train.py): Code that constructs training examples and fits the five comparison classifiers.
- [training data manifest](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/configs/structure-v2/corpus.json): Exact source reports, PDF hashes, report splits and annotation coverage.
- [Materialized training annotations](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/configs/structure-v2/annotations.json): Explicit heading line groups and levels reviewed by the assistant.
- [later filter protocol](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/outputs/structure-precision/evidence/protocol.json): Records the same model hashes before the subsequent confidence-filter search.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Estimator | sklearn.ensemble.ExtraTreesClassifier; scikit-learn 1.9.1; Python 3.12.3 |
| Trees per classifier | n_estimators=200 |
| Tree limits | max_depth=16; min_samples_leaf=2 |
| Feature sampling / weighting | max_features=0.8; class_weight="balanced" |
| Reproducibility / parallelism | random_state=42; n_jobs=4 |
| Other estimator options | Library defaults; no tree hyperparameter search was run |
| Join classifier | ExtraTreesClassifier: 100 features; 6,267 pairs; 200 trees; separate/join |
| Context classifier | ExtraTreesClassifier: 47 features; 6,736 groups; 200 trees; body/H1–H5 |
| Relation classifier | ExtraTreesClassifier: 142 features; 867 heading pairs; 200 trees; shallower/same/deeper |
| Total deployed trees | 3 ×200 =600; join + context + relation |
| Decision filter | body_weight=1.0; min_heading_score=0.70; relation_weight=1.0 |
| Selection objective | Maximum validation joint F0.5 among candidates with heading precision ≥0.95; empty output fails |
| Grid | 36 settings: learned_groups/context_relations × body {1,2,4} × score {0,.5,.7,.85}; contextual relation {1,0} |
| Matching | Same physical page; normalized title similarity ≥0.90; exact H level; pooled counts before scoring |

**Where these three classifiers were trained**

These are our own classifiers, trained from scratch in the structure-v2/run-001 experiment on the local Apple M4 Pro with 48 GB RAM, using CPU. The training run record identifies Python 3.12.3, scikit-learn 1.9.1 and macOS 26.1 arm64. The training program fitted the models from assistant-labeled WFP examples; they were not obtained from a pretrained-model repository.

The deployed files are join.json (200 trees; 6,267 line pairs; 100 features), context.json (200 trees; 6,736 heading/body groups; 47 features), and relation.json (200 trees; 867 heading pairs; 142 features). All use max_depth=16, min_samples_leaf=2, max_features=0.8, class_weight=balanced, random_state=42 and n_jobs=4. Five classifiers were fitted for the comparison variants, but this pipeline uses only these three.

The training data manifest identifies the 20 fitting reports, their official PDF URLs, SHA-256 hashes and reviewed pages. Materialized training annotations contain explicit line groups and levels. Four separate validation reports selected the context-and-relationships pipeline; four further reports were evaluated after selection. No training labels came from the four original league-table PDFs.

The model provenance page lists all reports, the exact reproduction command and the three full model hashes. The hashes agree between the original training run record, the later filter protocol and the local saved files. Model files are stored outside Git. The source records do not capture a precise training timestamp or the annotating assistant model version.


**Training data and annotation source**

A single assistant reviewed source text, layout/page snippets and table-of-contents context and supplied explicit line groups and H levels. The annotation provenance does not record a precise model version used by the annotating assistant, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate reference labels. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The training split contains 20 WFP reports, 887 heading groups and 7,039 labeled lines. Line classes: body=5,849; H1=238; H2=391; H3=432; H4=128; H5=1; H6=0. Negative examples come from 112 fully reviewed training pages. Unmarked lines on positive-only annotation pages are not automatically negatives. The H5/H6 coverage is a material limitation.

Validation uses reports 103, 538, 176 and 128: 21 reference groups on 20 reviewed pages. The test from the second training experiment uses reports 321, 844, 560 and 394: 38 groups on 32 reviewed pages. Splits are by report, not random lines; report-template families are not held out. Those test pages have now been inspected and are results on previously inspected test documents for subsequent changes.


**What each model learns**

The 33 measurements of selectable PDF text lines cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.

The context classifier uses 47 features: the 43 group features plus style_numbered_count, style_mean_depth, style_max_depth and toc_exact_title. Style statistics group lines by rounded font size, bold/italic and color, then summarize numeric-prefix depth. table-of-contents matching normalizes title text, strips its numeric prefix and dot leaders, and checks exact membership among dot-leader lines. This is a learned input feature, not a hard TOC level override.

The relationship classifier uses 142 features: two 47-feature groups, their differences and page delta. Its 867 training pairs are consecutive annotated headings. Target −1 means the next H number is smaller (shallower), 0 means equal and +1 means larger (deeper). It learns direction, not the number of levels skipped.


**Filter and validation selection**

The largest heading-class score must be at least 0.70 and a heading must beat the weighted body score. Scores are not calibrated probabilities. Filtering precedes relationship inference and Viterbi, so rejected groups cannot return.

The fixed 36-setting grid was evaluated only on the four validation reports (21 headings). Twenty-three settings met the 95% detection-precision gate. The selected configuration emitted 14 headings, all correctly leveled, and missed seven: joint F0.5 90.9%. Exact ties retain fixed grid order. No eligible candidate would mean no selection.


**Measured result and lost recall**

On the historical 77-heading benchmark, joint F0.5 rises from 58.8% to 70.5%, extras fall from 23 to 2, and heading precision rises to 95.1%. Correct heading-level pairs fall from 50 to 34. Of 41 predictions, 39 are real headings and five of those have incorrect levels; 38 reference titles are missed.

On the previously inspected 38-heading regression set, the candidate emits 28 headings, all correctly leveled, misses ten and scores 93.3% joint F0.5. These are regression results, not independent new test evidence. The 95.1% historical precision is a narrow sample pass.


**Runtime and reproducibility**

Measured full-PDF runtime is 11.66 seconds across all 523 pages on the shared 48 GB Apple M4 Pro. It includes extraction, features and inference; model loading and writes are excluded. The 600 previously trained decision trees and data-only JSON deployment are unchanged.

Selection saves model scores for reuse for speed and reads no test documents. The protocol records the search settings before selection and source/model/configuration hashes. Regression checks those hashes. Full text and raw outputs remain external; compact audit predictions and all grid scores are committed.

Only 34/77 heading-level pairs are correct. The low extra-heading count does not make this a complete outline.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/optimize_precision.py) · [Model provenance page](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/model-provenance.md) · [Training run record](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/outputs/structure-v2/evidence/selection.json) · [Training program](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/scripts/structure/train.py) · [Training data manifest](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/configs/structure-v2/corpus.json) · [Materialized training annotations](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/configs/structure-v2/annotations.json) · [Later filter protocol](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/outputs/structure-precision/evidence/protocol.json) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Exact estimator constructor and JSON export](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Native line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [Group/context/pair features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py) · [Training components and variant selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/train.py) · [PDF sources and report splits](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json) · [Reviewable heading annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/annotations.json) · [Inference, grouping and Viterbi](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py) · [Precision filter and sequence inference](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/precision_inference.py) · [Joint metric implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/joint_metrics.py) · [All validation results](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-precision/evidence/selection.json) · [Experiment, trade-offs and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-precision/report.md) · [Run on a new PDF](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_precision.py)


## qwen36-35b-visual-memory

**Qwen3.6-35B-A3B 4-bit — visual memory**

Qwen3.6-35B-A3B uses the original multi-image prompt with 4-bit weights. It restores up to six earlier sampled images alongside text, candidates and author tags.


**Inference:** Keep the original document clues → Restore current and earlier page images → Run the sparse Qwen3.6-35B-A3B model → Update visual memory from predictions

- **Keep the original document clues:** Supply the full-document PyMuPDF4LLM candidate titles/pages, author PDF heading tags and current native text. Reference labels are not supplied.
- **Restore current and earlier page images:** Use a current-page thumbnail up to 1792 pixels and up to six earlier sampled images at 1280 pixels. Memory pages contain the latest predicted heading at each H1–H6 level.
- **Run the sparse Qwen3.6-35B-A3B model:** Use the same pinned 4-bit weights as the single-image sparse trial. Keep the original instruction from run_qwen_visual_memory.py; temperature 0, seed 42, thinking disabled, 4096-token cap.
- **Update visual memory from predictions:** Call the unchanged original generate_page function. Retain the latest prediction at each level, deduplicate and sort earlier pages, and reset memory between reports. Save every raw reply without semantic repair.



**Models and terms explained**

- [Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B): A pretrained sparse vision-language model; only a subset of its expert parameters is active per token, although all weights are stored.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework for local Apple Silicon inference; it is the runtime, not the heading model.
- [4-bit](https://github.com/ml-explore/mlx-lm): Quantized model weights use reduced numerical precision to lower memory requirements. This does not specify heading depth or guarantee a speedup.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | mlx-community/Qwen3.6-35B-A3B-4bit; revision 38740b847e4c |
| Architecture | MoE 35B total / approximately 3B active; 40 text layers; width 2048; 256 routed experts, 8 selected per token |
| Weight quantization | Affine quantization; 4 bits; group size 64 (from the pinned model configuration) |
| Runtime | MLX 0.32.4; mlx-vlm 0.8.0; Apple M4 Pro, 48 GB shared memory |
| Images | Current thumbnail ≤1792 pixels plus up to six prior sampled-page thumbnails ≤1280 pixels; Matrix(2,2) render |
| Context | Full candidate titles/pages, PDF tags, native target text and earlier sampled images with predicted headings |
| Generation | enable_thinking=False; temperature=0; seed=42; max_tokens=4096 |
| Timeout | Soft 600-second limit checked between streamed chunks |
| Scope | 32 sampled images, not 523-page visual inference; ascending pages; memory resets per document |
| Experiment sequence | Follow-up chosen after the two single-image scores; no claim of independent test-set selection |

**Why this follow-up was run**

The sparse single-image model recovered all 77 titles without extra headings, but only 53 levels were correct. This trial tests whether restoring earlier typography examples helps hierarchy decisions. It changes image size, visual memory and the associated instruction back to the original configuration; it does not identify their separate effects.


**Exact implementation and training**

The wrapper calls the original generate_page function in run_qwen_visual_memory.py, including its instruction, image construction, strict decoder and soft 600-second limit. The only model substitution relative to the original vision-memory experiment is the pinned Qwen3.6-35B-A3B 4-bit model. No weights were trained or fine-tuned.

Earlier images come only from previously processed audit pages. Intervening pages are not silently read. Previous predictions can be wrong, so memory may propagate errors.


**Timing, provenance and limitations**

Generation time uses the original runner’s boundary. Model loading and work outside generation are recorded separately. The reused function does not record time to first token, so that measurement is explicitly unavailable for this variant.

The protocol records source and input checksums before loading. This is an exploratory follow-up on the already inspected historical corpus, selected after observing the two single-image trials; it is not an independent generalization test.

This follow-up was motivated by errors on the historical audit set. Visual memory may propagate earlier level mistakes. A new report/template holdout is needed to establish generalization.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_sparse_memory.py) · [Official base model](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) · [Tested MLX 4-bit weights](https://huggingface.co/mlx-community/Qwen3.6-35B-A3B-4bit) · [Experiment and reproduction commands](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/qwen-compact/report.md) · [Pinned architecture and quantization configuration](https://huggingface.co/mlx-community/Qwen3.6-35B-A3B-4bit/blob/38740b847e4cb78f352aba30aa41c76e08e6eb46/config.json) · [Unchanged original instruction and generation function](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_visual_memory.py) · [Protocol, predictions and page telemetry](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/qwen-compact/evidence/qwen36_35b_visual_memory.json)


## qwen36-35b-compact

**Qwen3.6-35B-A3B 4-bit — single image**

Qwen3.6-35B-A3B uses 4-bit MLX weights with one current-page image and text history. Approximately 3B of its 35B parameters are active per token.


**Inference:** Keep the document context → Render only the current page → Run Qwen3.6-35B-A3B with 4-bit weights → Carry predictions forward as text

- **Keep the document context:** Reuse the full PyMuPDF4LLM title/page outline (without its predicted levels) and author-provided PDF heading tags. No reference labels are supplied.
- **Render only the current page:** Extract sorted native text; render with PyMuPDF Matrix(2,2) and thumbnail to a maximum 1280-pixel edge. Earlier page images are omitted.
- **Run Qwen3.6-35B-A3B with 4-bit weights:** Use the sparse mixture-of-experts model: 35B total / approximately 3B active parameters per token; all weights still occupy memory. MLX-VLM 0.8.0; thinking disabled; temperature 0; seed 42; 4096-token cap.
- **Carry predictions forward as text:** Keep the last predicted heading at each H1–H6 level. Reset memory per report. Save raw JSON replies and native page text; validate schema without changing titles or levels.



**Models and terms explained**

- [Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B): A pretrained sparse vision-language model; only a subset of its expert parameters is active per token, although all weights are stored.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework for local Apple Silicon inference; it is the runtime, not the heading model.
- [4-bit](https://github.com/ml-explore/mlx-lm): Quantized model weights use reduced numerical precision to lower memory requirements. This does not specify heading depth or guarantee a speedup.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | mlx-community/Qwen3.6-35B-A3B-4bit; revision 38740b847e4c |
| Architecture | MoE 35B total / approximately 3B active; 40 text layers; width 2048; 256 routed experts, 8 selected per token |
| Weight quantization | Affine quantization; 4 bits; group size 64 (from the pinned model configuration) |
| Runtime | MLX 0.32.4; mlx-vlm 0.8.0; Apple M4 Pro, 48 GB shared memory |
| Images | Exactly one current-page image; aspect-preserving thumbnail ≤1280 pixels; Matrix(2,2) render |
| Context | Full candidate titles/pages; full PDF heading tags; current native text; latest prediction per H level as text |
| Generation | enable_thinking=False; temperature=0; seed=42; max_tokens=4096 |
| Timeout | Soft 600-second limit checked between streamed chunks |
| Scope | 32 sampled images, not 523-page visual inference; ascending pages; memory resets per document |

**What the model sees**

The current page image and native text can recover headings absent from the noisy candidate outline. Tags and previous predictions are explicitly described as fallible. Previous page images are absent, but the full document outline and tags are still repeated on each request.

The prompt treats instructions printed in the document as content. The output decoder validates complete heading strings and integer levels 1–6; it does not repair semantic errors.


**Training and selection**

These are pretrained, quantized weights. We did not train or fine-tune this Qwen model on WFP annotations. Both model variants and the shared input settings were fixed before scoring their outputs.

The four-report audit has already been inspected during earlier experiments. This is regression evidence, not a new independent test or evidence of generalization to arbitrary PDFs.


**Measurement and provenance**

The table sums generation-call times, including input processing. Model download/loading and earlier candidate/tag extraction are excluded. Per-page rendering/preparation, time to first chunk, tokens, errors and peak MLX allocation are stored separately in the linked compact evidence.

Both runs share an M4 Pro with other workloads. Single-run speed ratios are observational; no controlled repeated hardware benchmark was performed. Model revisions, source/input hashes and package versions were recorded before loading.

Removing visual history and shrinking the target image may lose typography clues. Correct title-and-level recall and false headings must be considered together. Only the original 32 sampled pages were scored.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_compact.py) · [Official base model](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) · [Tested MLX 4-bit weights](https://huggingface.co/mlx-community/Qwen3.6-35B-A3B-4bit) · [Exact prompt](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/compact_prompt.py) · [Protocol, predictions and page telemetry](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/qwen-compact/evidence/qwen36_35b_compact.json) · [Experiment and reproduction commands](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/qwen-compact/report.md) · [Pinned architecture and quantization configuration](https://huggingface.co/mlx-community/Qwen3.6-35B-A3B-4bit/blob/38740b847e4cb78f352aba30aa41c76e08e6eb46/config.json)


## ovisocr3-official-metal

**OvisOCR3 — upstream prompt and vLLM Metal**

OvisOCR3 uses original 0.8B BF16 weights through vLLM Metal. The official document_markdown prompt and cleanup produce the scored Markdown.


**Inference:** Render a page without extracting its text → Apply the official document-parsing prompt → Generate with OvisOCR3 on Metal → Apply only the documented cleanup

- **Render a page without extracting its text:** Render each of the 32 audit pages at 200 DPI in RGB. Supply one image at a time, without native PDF text, tags, reference headings or adjacent-page context.
- **Apply the official document-parsing prompt:** Read document_markdown.txt from the pinned ATH-MaaS/OvisOCR3 checkpoint. The prompt requests natural reading order, Markdown text, LaTeX formulas, HTML tables and image crop tags. Apply the checkpoint’s chat template with thinking disabled.
- **Generate with OvisOCR3 on Metal:** The original BF16 0.8B Qwen3.5-based model runs through vLLM 0.34.0 and vllm-metal 0.34.0. Temperature 0, seed 42, maximum 16,384 output tokens, one sequence. Image bounds remain 448² to 2880² pixels.
- **Apply only the documented cleanup:** Preserve raw output, then remove image-tag blocks and apply the model card’s repeated-tail cleanup. Parse the resulting native Markdown headings. Bold text is not promoted to a heading, and H levels are never shifted.



**Models and terms explained**

- [OvisOCR3](https://huggingface.co/ATH-MaaS/OvisOCR3): A compact visual language model from ATH-MaaS for document parsing and other OCR tasks. This row uses its Markdown task.
- [vLLM Metal](https://github.com/vllm-project/vllm-metal): A community-maintained vLLM hardware plugin that runs supported models on Apple GPUs through MLX. It uses different kernels from NVIDIA Triton.
- [BF16](https://huggingface.co/ATH-MaaS/OvisOCR3): A 16-bit floating-point weight format. These are the original published weights, not a smaller quantized conversion.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Checkpoint | ATH-MaaS/OvisOCR3 @5b252386ba615bd464a5a26597560eaba87dae5c |
| Weights | 0.8B parameters; original BF16 weights; no quantization or WFP fine-tuning |
| Runtime | vllm==0.34.0+cpu with vllm-metal==0.34.0; MLX backend on Apple M4 Pro GPU |
| Official-example difference | Model card uses vLLM 0.22.1 with gdn_prefill_backend=triton. Metal selects its own kernels; this is not a CUDA benchmark replication. |
| Prompt | Pinned prompts/document_markdown.txt; official chat template; enable_thinking=False |
| Sampling | temperature=0; max_tokens=16384; seed=42; max_num_seqs=1; tensor_parallel_size=1 |
| Images | One RGB image per call; minimum 448×448 and maximum 2880×2880 pixel area; current processor size API |
| Memory | gpu_memory_utilization=0.8; native Metal attention kernels; upstream default context limit 262144 |
| Cleanup | Filter image-tag blocks; upstream repeated-tail thresholds: minimum text 8000 characters, period 1–200, repeat span ≥100 characters and ≥5 repetitions |
| Timing | 418.19 seconds for 32 pages (13.07 seconds/page); 20.64 seconds model initialization separately |
| Completion | 32/32 pages; zero errors; zero length-limit stops; raw responses, tokens and finish reasons retained |

**Training and provenance**

OvisOCR3 is the authors’ published Qwen3.5-0.8B-based model. Its model card describes continued pretraining, mid-training, on-policy distillation and reinforcement learning. We did not train it on WFP reports or select its prompt using our reference labels.


**How to interpret this result**

The model emitted 50 headings and 36 had both the correct title and level. Its one extra heading should not hide the 28 missing reference headings. The 65.0% score is lower than the recorded Chandra configuration’s 72.6%, while measured processing time is shorter. Backend and pipeline differences prevent attributing that difference solely to the weights.


**Some missed headings were transcribed as ordinary text**

On Indonesia PDF page 7, the raw response begins with Executive summary, Introduction and Evaluation features as plain text, without Markdown heading markers. On targeting page 33, it transcribes 2 Evaluation findings as plain text while marking its subsections H2, H3 and H4. These are heading-classification misses even though the title text was recognized. We do not promote these lines using our reference labels.

Original weights and official task recipe, with a newer vLLM runtime and Metal hardware plugin. Published CUDA accuracy and speed have not been reproduced. References are not independently human-validated.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_ovis_official.py) · [Pinned model card and inference recipe](https://huggingface.co/ATH-MaaS/OvisOCR3/blob/5b252386ba615bd464a5a26597560eaba87dae5c/README.md) · [OvisOCR3 paper](https://arxiv.org/abs/2610.33066) · [Cleanup implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/ovis_output.py) · [Runtime pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/ovis-metal.txt) · [Measured run and predictions](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/official-pipelines/ovisocr3_official_metal.json) · [Raw examples of missing heading markers](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/ovis-heading-examples.json) · [Configuration source / evidence](https://huggingface.co/ATH-MaaS/OvisOCR3)


## structure-calibrated

**OUR METHOD v2 + calibrated decoding (CPU)**

The same three trained Extra Trees classifiers are reused. Multiplying the body-text score by two makes heading selection stricter; relationship weight stays 1.


**Training:** Train our three classifiers locally → Try nine decision settings → Keep the validation choice

- **Train our three classifiers locally:** The structure-v2/run-001 training program fits Extra Trees on assistant annotations from 20 WFP reports, on the local M4 Pro CPU. See the model provenance page and training run record. Later decision-setting experiments reuse these fitted models. No further model training occurs in those experiments.
- **Try nine decision settings:** On four validation reports, combine body-score multipliers 1, 1.5 and 2 with relationship weights 1, 0.5 and 0.
- **Keep the validation choice:** Body multiplier 2 and relationship weight 1 scored 81.1% exact group-and-level F1. The original benchmark was evaluated afterwards; it did not choose these settings.



**Inference:** Join lines with Extra Trees → Favor ordinary body text → Score heading relationships → Choose the level sequence

- **Join lines with Extra Trees:** The 200-tree join classifier uses 100 measurements of adjacent lines, including spacing and style. It can join lines across PDF blocks.
- **Favor ordinary body text:** Use the same 200-tree heading classifier with 47 measurements. Double its body-text score, then choose the highest-scoring class; this can reject real headings too.
- **Score heading relationships:** The 200-tree relation classifier uses 142 measurements of consecutive headings. It predicts shallower, same or deeper.
- **Choose the level sequence:** Viterbi combines accepted headings’ level scores and relationship scores, with relationship weight 1. Rejected text remains in the document.



**Models and terms explained**

- [Extra Trees](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html): A classifier that averages predictions from many randomized decision trees. A tree makes a sequence of decisions about input measurements. This benchmark uses scikit-learn’s ExtraTreesClassifier, with 200 trees per component.
- [Features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py): The numeric measurements supplied to a classifier—for example font size, boldness, line spacing or whether a title occurs in the table of contents. They are calculated from the PDF, not supplied reference answers.
- [Validation reports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json): Reports kept separate from model fitting and used to choose between designs or decision settings. The later inspected test reports are now regression checks: they can expose a failure but no longer provide a fresh independent evaluation.
- [Viterbi decoding](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py): An algorithm for choosing the highest-scoring sequence of heading levels. Here it combines each heading’s own scores with scores for the relationship to the preceding heading. It does not train or add another model.
- [model provenance page](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/model-provenance.md): Complete training lineage, report list, model identities and reproduction command.
- [training run record](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/outputs/structure-v2/evidence/selection.json): Original structure-v2 training output: counts, versions, selection and saved model hashes.
- [training program](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/scripts/structure/train.py): Code that constructs training examples and fits the five comparison classifiers.
- [training data manifest](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/configs/structure-v2/corpus.json): Exact source reports, PDF hashes, report splits and annotation coverage.
- [Materialized training annotations](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/configs/structure-v2/annotations.json): Explicit heading line groups and levels reviewed by the assistant.
- [later filter protocol](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/outputs/structure-precision/evidence/protocol.json): Records the same model hashes before the subsequent confidence-filter search.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Estimator | sklearn.ensemble.ExtraTreesClassifier; scikit-learn 1.9.1; Python 3.12.3 |
| Trees per classifier | n_estimators=200 |
| Tree limits | max_depth=16; min_samples_leaf=2 |
| Feature sampling / weighting | max_features=0.8; class_weight="balanced" |
| Reproducibility / parallelism | random_state=42; n_jobs=4 |
| Other estimator options | Library defaults; no tree hyperparameter search was run |
| Join classifier | ExtraTreesClassifier: 100 features; 6,267 pairs; 200 trees; separate/join |
| Context classifier | ExtraTreesClassifier: 47 features; 6,736 groups; 200 trees; body/H1–H5 |
| Relation classifier | ExtraTreesClassifier: 142 features; 867 heading pairs; 200 trees; shallower/same/deeper |
| Total deployed trees | 3 ×200 =600; join + context + relation |
| Grid actually searched | body_weight ∈ {1.0, 1.5, 2.0}; relation_weight ∈ {1.0, 0.5, 0.0}; 9 combinations |
| Selected decoding | body_weight=2.0; relation_weight=1.0 |
| Selection metric / ties | Validation exact group-and-level F1; first grid entry wins ties, with baseline settings ordered first |
| Model integrity | Same JSON model hashes as v2; no refitting or label changes |

**Where these three classifiers were trained**

These are our own classifiers, trained from scratch in the structure-v2/run-001 experiment on the local Apple M4 Pro with 48 GB RAM, using CPU. The training run record identifies Python 3.12.3, scikit-learn 1.9.1 and macOS 26.1 arm64. The training program fitted the models from assistant-labeled WFP examples; they were not obtained from a pretrained-model repository.

The deployed files are join.json (200 trees; 6,267 line pairs; 100 features), context.json (200 trees; 6,736 heading/body groups; 47 features), and relation.json (200 trees; 867 heading pairs; 142 features). All use max_depth=16, min_samples_leaf=2, max_features=0.8, class_weight=balanced, random_state=42 and n_jobs=4. Five classifiers were fitted for the comparison variants, but this pipeline uses only these three.

The training data manifest identifies the 20 fitting reports, their official PDF URLs, SHA-256 hashes and reviewed pages. Materialized training annotations contain explicit line groups and levels. Four separate validation reports selected the context-and-relationships pipeline; four further reports were evaluated after selection. No training labels came from the four original league-table PDFs.

The model provenance page lists all reports, the exact reproduction command and the three full model hashes. The hashes agree between the original training run record, the later filter protocol and the local saved files. Model files are stored outside Git. The source records do not capture a precise training timestamp or the annotating assistant model version.


**Previously trained models and their examples**

A single assistant reviewed source text, layout/page snippets and table-of-contents context and supplied explicit line groups and H levels. The annotation provenance does not record a precise model version used by the annotating assistant, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate reference labels. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The training split contains 20 WFP reports, 887 heading groups and 7,039 labeled lines. Line classes: body=5,849; H1=238; H2=391; H3=432; H4=128; H5=1; H6=0. Negative examples come from 112 fully reviewed training pages. Unmarked lines on positive-only annotation pages are not automatically negatives. The H5/H6 coverage is a material limitation.

Validation uses reports 103, 538, 176 and 128: 21 reference groups on 20 reviewed pages. The test from the second training experiment uses reports 321, 844, 560 and 394: 38 groups on 32 reviewed pages. Splits are by report, not random lines; report-template families are not held out. Those test pages have now been inspected and are results on previously inspected test documents for subsequent changes.


**Features and sequence decoding**

The 33 measurements of selectable PDF text lines cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.

The context classifier uses 47 features: the 43 group features plus style_numbered_count, style_mean_depth, style_max_depth and toc_exact_title. Style statistics group lines by rounded font size, bold/italic and color, then summarize numeric-prefix depth. table-of-contents matching normalizes title text, strips its numeric prefix and dot leaders, and checks exact membership among dot-leader lines. This is a learned input feature, not a hard TOC level override.

The relationship classifier uses 142 features: two 47-feature groups, their differences and page delta. Its 867 training pairs are consecutive annotated headings. Target −1 means the next H number is smaller (shallower), 0 means equal and +1 means larger (deeper). It learns direction, not the number of levels skipped.

First, choosing the highest body-or-heading score decides which predicted groups survive. Viterbi then maximizes the sum of log heading-class probabilities and weighted log relationship probabilities for transitions between retained groups. Transition class is sign(next H − previous H); probabilities are clipped below at 1e-12. Default relation weight is 1.0. This decoder is an algorithm, not a fourth trained model, and cannot recover a group already rejected as body.


**What calibration changes**

Only the body column of a copy of the group-probability array is multiplied by body_weight before choosing the highest-scoring class. Surviving headings still use the original probabilities in Viterbi. This is decision weighting, not statistical probability calibration.

On the four validation reports, body weights 1.0, 1.5 and 2.0 yield group-and-level F1 of 69.8%, 76.9% and 81.1%. All three relationship weights tie at each body weight, so the ordered grid retains relation_weight=1.0. There is no evidence from this grid that a relationship-weight change helped.


**Regression outcome and why this is not promoted**

On the previously inspected 38-heading set, F1 rises from 85.7% to 94.7%: 36 groups remain correctly leveled, false groups fall from 8 to 1, and one genuine group is now missed. This is results on previously inspected test documents, not a new independent test.

On the historical main-table 77 headings, correct title-plus-level matches fall from 50 to 47; matched titles fall from 64 to 59 and false headings from 23 to 21. The candidate therefore remains a separate historical candidate; the current highlighted method is selected using joint F0.5 and the precision gate.


**Deployment and measured scope**

Models are exported as data-only JSON arrays. Exported predict_proba is checked against scikit-learn with atol=1e-7. Runtime inference uses NumPy and float32 tree traversal; it needs no LLM or scikit-learn model server. Full selectable PDF text is retained. Parent IDs are derived from the predicted level stack, not separately learned or evaluated.

The main comparison parses all four historical PDFs (523 pages) on an Apple M4 Pro with 48 GB memory, but scores only 77 headings on 32 audited pages. Its fuzzy title matching plus exact level is different from the supervised exact group-and-level F1. Main-table scores are historical diagnostics, not the fresh supervised split. Timing covers extraction, feature construction and prediction; model-file loading occurs before the parser timer.

The runner accepts a separate calibration file and verifies the recorded model and configuration checksums. No score or inference output is changed by this documentation update.

The models and labels are unchanged. Validation selects a stricter heading decision. Regression on previously inspected pages improves F1 but misses one genuine heading. It is not new independent test evidence.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/calibrate.py) · [Model provenance page](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/model-provenance.md) · [Training run record](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/outputs/structure-v2/evidence/selection.json) · [Training program](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/scripts/structure/train.py) · [Training data manifest](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/configs/structure-v2/corpus.json) · [Materialized training annotations](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/configs/structure-v2/annotations.json) · [Later filter protocol](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/outputs/structure-precision/evidence/protocol.json) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Calibration protocol and regression evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-calibration/report.md) · [Exact estimator constructor and JSON export](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Native line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [Group/context/pair features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py) · [Training components and variant selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/train.py) · [Recorded validation scores and training settings](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-v2/evidence/selection.json) · [PDF sources and report splits](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json) · [Reviewable heading annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/annotations.json) · [Inference, grouping and Viterbi](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py) · [Recorded search results and selected decision settings](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-calibration/evidence/selection.json) · [Calibration runner and artifact input](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_structure.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


## structure-context-relations

**v2: context + relationships (selected)**

Three 200-tree Extra Trees classifiers learn line joining, heading levels and relationships. Viterbi selects a level sequence using document context and relationship weight 1.


**Training:** Train our three classifiers locally → Train Extra Trees classifiers → Compare designs on validation reports

- **Train our three classifiers locally:** The structure-v2/run-001 training program fits Extra Trees on assistant annotations from 20 WFP reports, on the local M4 Pro CPU. See the model provenance page and training run record. Later decision-setting experiments reuse these fitted models. No further model training occurs in those experiments.
- **Train Extra Trees classifiers:** An Extra Trees classifier combines many randomized decision trees. Each tree uses measurements such as font size and spacing to vote for a class. Each component here has 200 trees, maximum depth 16, minimum leaf size 2, balanced classes and seed 42.
- **Compare designs on validation reports:** Use 21 headings in four separate reports to compare the line-only, joined-text and document-context designs. Their original exact group-and-level F1 scores were 55.3%, 63.6% and 69.8%; that earlier selection predates the new F0.5 objective.



**Inference:** Join lines with Extra Trees → Recognize headings and propose levels → Score heading relationships → Choose the level sequence

- **Join lines with Extra Trees:** The 200-tree join classifier uses 100 measurements of adjacent lines, including spacing and style. It can join lines across PDF blocks.
- **Recognize headings and propose levels:** A second 200-tree Extra Trees classifier uses 47 measurements of each text group and the document’s numbering, styles and table of contents. It scores body text and levels H1–H5.
- **Score heading relationships:** The 200-tree relation classifier uses 142 measurements of consecutive headings. It predicts shallower, same or deeper.
- **Choose the level sequence:** Viterbi combines accepted headings’ level scores and relationship scores, with relationship weight 1. Rejected text remains in the document.



**Models and terms explained**

- [Extra Trees](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html): A classifier that averages predictions from many randomized decision trees. A tree makes a sequence of decisions about input measurements. This benchmark uses scikit-learn’s ExtraTreesClassifier, with 200 trees per component.
- [Features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py): The numeric measurements supplied to a classifier—for example font size, boldness, line spacing or whether a title occurs in the table of contents. They are calculated from the PDF, not supplied reference answers.
- [Validation reports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json): Reports kept separate from model fitting and used to choose between designs or decision settings. The later inspected test reports are now regression checks: they can expose a failure but no longer provide a fresh independent evaluation.
- [Viterbi decoding](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py): An algorithm for choosing the highest-scoring sequence of heading levels. Here it combines each heading’s own scores with scores for the relationship to the preceding heading. It does not train or add another model.
- [model provenance page](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/model-provenance.md): Complete training lineage, report list, model identities and reproduction command.
- [training run record](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/outputs/structure-v2/evidence/selection.json): Original structure-v2 training output: counts, versions, selection and saved model hashes.
- [training program](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/scripts/structure/train.py): Code that constructs training examples and fits the five comparison classifiers.
- [training data manifest](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/configs/structure-v2/corpus.json): Exact source reports, PDF hashes, report splits and annotation coverage.
- [Materialized training annotations](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/configs/structure-v2/annotations.json): Explicit heading line groups and levels reviewed by the assistant.
- [later filter protocol](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/outputs/structure-precision/evidence/protocol.json): Records the same model hashes before the subsequent confidence-filter search.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Estimator | sklearn.ensemble.ExtraTreesClassifier; scikit-learn 1.9.1; Python 3.12.3 |
| Trees per classifier | n_estimators=200 |
| Tree limits | max_depth=16; min_samples_leaf=2 |
| Feature sampling / weighting | max_features=0.8; class_weight="balanced" |
| Reproducibility / parallelism | random_state=42; n_jobs=4 |
| Other estimator options | Library defaults; no tree hyperparameter search was run |
| Join classifier | ExtraTreesClassifier: 100 features; 6,267 pairs; 200 trees; separate/join |
| Context classifier | ExtraTreesClassifier: 47 features; 6,736 groups; 200 trees; body/H1–H5 |
| Relation classifier | ExtraTreesClassifier: 142 features; 867 heading pairs; 200 trees; shallower/same/deeper |
| Total deployed trees | 3 ×200 =600; join + context + relation |
| Decoding | body_weight=1.0; relation_weight=1.0; Viterbi over retained H1–H5 candidates |
| Artifacts / fitting | 23.2 MiB combined JSON; ≈2.09 s summed classifier fitting, excluding extraction/export/validation |

**Where these three classifiers were trained**

These are our own classifiers, trained from scratch in the structure-v2/run-001 experiment on the local Apple M4 Pro with 48 GB RAM, using CPU. The training run record identifies Python 3.12.3, scikit-learn 1.9.1 and macOS 26.1 arm64. The training program fitted the models from assistant-labeled WFP examples; they were not obtained from a pretrained-model repository.

The deployed files are join.json (200 trees; 6,267 line pairs; 100 features), context.json (200 trees; 6,736 heading/body groups; 47 features), and relation.json (200 trees; 867 heading pairs; 142 features). All use max_depth=16, min_samples_leaf=2, max_features=0.8, class_weight=balanced, random_state=42 and n_jobs=4. Five classifiers were fitted for the comparison variants, but this pipeline uses only these three.

The training data manifest identifies the 20 fitting reports, their official PDF URLs, SHA-256 hashes and reviewed pages. Materialized training annotations contain explicit line groups and levels. Four separate validation reports selected the context-and-relationships pipeline; four further reports were evaluated after selection. No training labels came from the four original league-table PDFs.

The model provenance page lists all reports, the exact reproduction command and the three full model hashes. The hashes agree between the original training run record, the later filter protocol and the local saved files. Model files are stored outside Git. The source records do not capture a precise training timestamp or the annotating assistant model version.


**Training data and annotation source**

A single assistant reviewed source text, layout/page snippets and table-of-contents context and supplied explicit line groups and H levels. The annotation provenance does not record a precise model version used by the annotating assistant, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate reference labels. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The training split contains 20 WFP reports, 887 heading groups and 7,039 labeled lines. Line classes: body=5,849; H1=238; H2=391; H3=432; H4=128; H5=1; H6=0. Negative examples come from 112 fully reviewed training pages. Unmarked lines on positive-only annotation pages are not automatically negatives. The H5/H6 coverage is a material limitation.

Validation uses reports 103, 538, 176 and 128: 21 reference groups on 20 reviewed pages. The test from the second training experiment uses reports 321, 844, 560 and 394: 38 groups on 32 reviewed pages. Splits are by report, not random lines; report-template families are not held out. Those test pages have now been inspected and are results on previously inspected test documents for subsequent changes.


**What each model learns**

The 33 measurements of selectable PDF text lines cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.

The context classifier uses 47 features: the 43 group features plus style_numbered_count, style_mean_depth, style_max_depth and toc_exact_title. Style statistics group lines by rounded font size, bold/italic and color, then summarize numeric-prefix depth. table-of-contents matching normalizes title text, strips its numeric prefix and dot leaders, and checks exact membership among dot-leader lines. This is a learned input feature, not a hard TOC level override.

The relationship classifier uses 142 features: two 47-feature groups, their differences and page delta. Its 867 training pairs are consecutive annotated headings. Target −1 means the next H number is smaller (shallower), 0 means equal and +1 means larger (deeper). It learns direction, not the number of levels skipped.


**Sequence decoding**

First, choosing the highest body-or-heading score decides which predicted groups survive. Viterbi then maximizes the sum of log heading-class probabilities and weighted log relationship probabilities for transitions between retained groups. Transition class is sign(next H − previous H); probabilities are clipped below at 1e-12. Default relation weight is 1.0. This decoder is an algorithm, not a fourth trained model, and cannot recover a group already rejected as body.


**Selection, not a tree-parameter search**

We compared three pipeline variants, with identical fixed tree settings. Validation exact group-and-level F1 was 55.3% for expanded_line, 63.6% for learned_groups and 69.8% for context_relations. The highest validation F1 selected context_relations before the test from the second training experiment. Selection did not use the historical main-table results. F1 = 2 × exact group-and-level matches / (gold groups + predicted groups); group matching requires identical source-line membership.

The original separate 38-heading v2 test achieved 85.7% exact group-and-level F1: 38 matched groups, 36 correctly leveled and 8 additional false groups. That small test is distinct from the historical 77-heading table.


**Deployment and timing**

Models are exported as data-only JSON arrays. Exported predict_proba is checked against scikit-learn with atol=1e-7. Runtime inference uses NumPy and float32 tree traversal; it needs no LLM or scikit-learn model server. Full selectable PDF text is retained. Parent IDs are derived from the predicted level stack, not separately learned or evaluated.

The main comparison parses all four historical PDFs (523 pages) on an Apple M4 Pro with 48 GB memory, but scores only 77 headings on 32 audited pages. Its fuzzy title matching plus exact level is different from the supervised exact group-and-level F1. Main-table scores are historical diagnostics, not the fresh supervised split. Timing covers extraction, feature construction and prediction; model-file loading occurs before the parser timer.

No LLM is needed at inference. Labels are assistant-assisted, not independently human-verified. Parent links are inferred, not evaluated. v2 main-table scores are historical diagnostics; the separate 38-heading pilot has a different metric.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) · [Model provenance page](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/model-provenance.md) · [Training run record](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/outputs/structure-v2/evidence/selection.json) · [Training program](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/scripts/structure/train.py) · [Training data manifest](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/configs/structure-v2/corpus.json) · [Materialized training annotations](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/configs/structure-v2/annotations.json) · [Later filter protocol](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/outputs/structure-precision/evidence/protocol.json) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Exact estimator constructor and JSON export](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Native line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [Group/context/pair features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py) · [Training components and variant selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/train.py) · [Recorded validation scores and training settings](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-v2/evidence/selection.json) · [PDF sources and report splits](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json) · [Reviewable heading annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/annotations.json) · [Inference, grouping and Viterbi](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py) · [Configuration source / evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md)


## structure-recall

**OUR METHOD — retrained trees (coverage trial; target not met)**

Extra Trees are retrained with eight tree settings and eight decision settings. No candidate meets both 80% joint precision and recall; this row is the recorded diagnostic selection.


**Training:** Reuse reviewed training examples → Fit eight Extra Trees bundles → Select using coverage and precision

- **Reuse reviewed training examples:** Use the unchanged 20-report fitting split: 6,267 adjacent-line pairs, 6,736 text groups and 867 heading pairs. Validation and regression reports do not contribute labels to fitting.
- **Fit eight Extra Trees bundles:** Cross max_depth 16/unlimited, min_samples_leaf 1/2 and max_features 0.8/1.0. Fit join, context and relation models with 200 trees each, balanced class weights and seed 42.
- **Select using coverage and precision:** Evaluate 64 configurations on four validation reports. None meets both 80% joint precision and recall. The predeclared fallback maximizes the smaller metric, then joint F0.5; it reaches 84.2% precision and 76.2% recall.



**Inference:** Join wrapped heading lines → Assign body or heading level → Use the selected direct decision → Retain text and score recorded predictions

- **Join wrapped heading lines:** The newly fitted 200-tree join classifier groups adjacent lines, using 100 features. PDF text is extracted locally.
- **Assign body or heading level:** The newly fitted context classifier uses 47 features. Its unlimited-depth trees allow one training sample per leaf and consider all features at each split.
- **Use the selected direct decision:** Choose the largest class score with body multiplier 1 and no confidence cutoff. Relationship weight is 0, so the fitted relation model and Viterbi are not used.
- **Retain text and score recorded predictions:** Keep all native text. On the original 77-heading regression sample: 87 predictions, 66 genuine titles, 50 correct heading-level pairs. This is the same matching contract as every other row.



**Models and terms explained**

- [Extra Trees](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html): A classifier that averages predictions from many randomized decision trees. A tree makes a sequence of decisions about input measurements. This benchmark uses scikit-learn’s ExtraTreesClassifier, with 200 trees per component.
- [Features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py): The numeric measurements supplied to a classifier—for example font size, boldness, line spacing or whether a title occurs in the table of contents. They are calculated from the PDF, not supplied reference answers.
- [Validation reports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json): Reports kept separate from model fitting and used to choose between designs or decision settings. The later inspected test reports are now regression checks: they can expose a failure but no longer provide a fresh independent evaluation.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Estimator | scikit-learn 1.9.1 ExtraTreesClassifier; Python 3.12.3 |
| Trees | 200 per classifier; three fitted, two used by selected inference |
| Selected tree settings | max_depth=None; min_samples_leaf=1; max_features=1.0 |
| Fixed settings | class_weight=balanced; random_state=42; n_jobs=4 |
| Selected decision settings | body_weight=1.0; min_heading_score=0.0; relation_weight=0.0 |
| Validation search | 8 tree bundles × 8 decision configurations = 64 |
| Selection result | No eligible candidate; predeclared diagnostic fallback |
| Measured time | 16.42 seconds / 523 pages; excludes model loading and writes |

**Training provenance**

Trained locally on the M4 Pro CPU in structure-recall/run-002. The same 887 assistant-annotated heading groups and fully reviewed body examples were used as in structure-v2. No new labels were added. The source/configuration hashes were recorded before fitting; the selected model hashes and all validation results are committed. Model files and full extracted text remain outside Git.


**Why the result is not an improvement in usable quality**

Title recovery rises from 39/77 to 66/77 relative to the confidence filter, but extras rise from two to 21. Correct heading-level pairs are 50/77, exactly the older unfiltered context model’s count. On the inspected 38-heading set, joint recall is 94.7% and joint precision 81.8%. The large difference between sets limits any generalization claim.

Original league: 66/77 titles recovered, 50/77 correct heading-level pairs, 21 extra headings and 16 wrong levels. Same correct-pair count as the older unfiltered model. Small reused validation and inspected regression sets; no independent new test or new annotations.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/retrain_recall.py) · [Full trial and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-recall/report.md) · [Predeclared protocol](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-recall/evidence/protocol.json) · [All validation scores and model hashes](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-recall/evidence/selection.json) · [Fitting code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/recall_training.py) · [Original training labels and source reports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/model-provenance.md) · [Run on a new PDF](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_recall.py)


## lighton-mlx

**LightOnOCR-3-0.8B / MLX**

LightOnOCR-3-0.8B reads one page image through MLX. Its grounding output supplies title regions; Markdown markers supply levels.


**Inference:** Make images of the 32 audit pages → Request text with locations → Read the reported title blocks → Join wrapped titles and read levels

- **Make images of the 32 audit pages:** Render at 400 dots per inch, then shrink each image so its longest side is at most 2048 pixels.
- **Request text with locations:** Run LightOnOCR-3-0.8B through MLX using the “grounding” prompt, which asks the model to associate content with page regions. Disable thinking; use temperature=0 and at most 8192 output tokens.
- **Read the reported title blocks:** The model marks titles and supplies bounding boxes—the rectangles locating them on the page.
- **Join wrapped titles and read levels:** A title+ block continues the previous title. Count any leading # characters to obtain its level; retain an unknown level when none is supplied.



**Models and terms explained**

- [LightOnOCR-3-0.8B](https://huggingface.co/lightonai/LightOnOCR-3-0.8B): A document image-reading model with approximately 0.8 billion parameters. Its output includes text and page regions.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.
- [Grounding](https://huggingface.co/lightonai/LightOnOCR-3-0.8B): Returning text together with the page regions it refers to. In these OCR runs, the response locates title blocks; a location alone does not establish a heading’s level.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | lightonai/LightOnOCR-3-0.8B; revision 36d863692532 (pin in runner) |
| Runtime | MLX native checkpoint; no quantization conversion in the runner; one page per call |
| Image | 400 dpi → longest side ≤2048 pixels |
| Prompt | Literal “grounding”; num_images=1; enable_thinking=False |
| Generation | temperature=0; max_tokens=8192; MLX seed=42 |
| Timeout | Soft 300-second limit, checked between streamed chunks; not a hard interrupt |

**Grounding decoder**

Grounded title blocks include bounding boxes on a 0–1000 coordinate scale, normalized by the adapter. A title+ block is appended only when the preceding block is title/title+. Markdown # through ###### supplies level; an unmarked title retains level=null. Raw text, token counts and limit/timeout status are saved.


**Tuning and measured scope**

Pretrained weights and a fixed grounding prompt; no benchmark fine-tuning. The linked 2026 LightOnOCR paper is earlier research, not a claim that this benchmark replicates a LightOnOCR-3 paper.

Only the 32 audited page images were processed. Scores use their 77 reference headings. Runs used local MLX on an Apple M4 Pro with 48 GB memory. A per-500-page time is an extrapolation, not a 500-page image run.

The reported time sums page generation; model loading is excluded. Cached completed pages support resumption.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

Page-local recognition has less document-wide hierarchy context. These are local MLX measurements, not vendor throughput claims.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_lighton_mlx.py) · [Model / Hugging Face](https://huggingface.co/lightonai/LightOnOCR-3-0.8B) · [Project / GitHub](https://github.com/lightonai/LightOnOCR) · [Earlier LightOnOCR research paper](https://arxiv.org/abs/2601.14251) · [Grounding prompt, image sizing and decoder](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_lighton_mlx.py) · [MLX package pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/mlx.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


## lighton4b-mlx

**LightOnOCR-3-4B / MLX grounding**

LightOnOCR-3-4B reads two independent page images per MLX batch using BF16 weights. Title blocks and Markdown markers supply the outline.


**Inference:** Render each audit page → Process two pages together → Include five earlier outputs → Extract titles and their levels

- **Render each audit page:** Render at 400 dots per inch and shrink to a maximum 2048-pixel side. Each page is a separate input; batching does not share context.
- **Process two pages together:** Run LightOnOCR-3-4B through MLX with bf16 weights, the “grounding” prompt, temperature=0 and a 12,384-token output limit.
- **Include five earlier outputs:** The published run retained five already completed single-page results. Those used a 12,288-token limit; it was not a clean rerun of all pages with one batch setting.
- **Extract titles and their levels:** Join title+ continuation blocks, read Markdown # levels where supplied, and retain page numbers and bounding boxes.



**Models and terms explained**

- [LightOnOCR-3-4B](https://huggingface.co/lightonai/LightOnOCR-3-4B): The four-billion-parameter document image-reading model used in this run.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.
- [bf16](https://ml-explore.github.io/mlx/build/html/python/data_types.html): A 16-bit floating-point number format used for model weights and calculations. It is a numerical format, not a particular model or training technique.
- [Grounding](https://huggingface.co/lightonai/LightOnOCR-3-0.8B): Returning text together with the page regions it refers to. In these OCR runs, the response locates title blocks; a location alone does not establish a heading’s level.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | lightonai/LightOnOCR-3-4B; revision b71010f095dc |
| Runtime | MLX bf16; MlxVlmClient; batch_size=2; no quantization conversion |
| Image | 400 dpi → longest side ≤2048 pixels |
| Prompt | Literal “grounding”; empty system prompt; wrapper checked against template with enable_thinking=False |
| Sampling | temperature=0; top_p=1; top_k=0; max_new_tokens=12384; seed=42 |
| Historical exception | Five cached single-page outputs use max_tokens=12288; fresh packaged runs batch all 32 pages |

**Output and provenance**

The grounded title/title+ decoder is shared with the 0.8B path. It retains unknown levels rather than inferring them. The table’s measured result combines the five earlier checkpoints with the subsequent batch outputs; it is not a claim that all 32 historical pages used an identical batching configuration.


**Tuning and measured scope**

No benchmark fine-tuning or parameter search. Batch size and token limits are fixed runtime choices.

Only the 32 audited page images were processed. Scores use their 77 reference headings. Runs used local MLX on an Apple M4 Pro with 48 GB memory. A per-500-page time is an extrapolation, not a 500-page image run.

Timing sums recorded generation, excludes model loading, and allocates a batch’s wall time equally across its pages. Allocated per-page times are not individual-page latency measurements.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

Page-local recognition has less document-wide hierarchy context. These are local MLX measurements, not vendor throughput claims.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_chandra_batch.py) · [Model / Hugging Face](https://huggingface.co/lightonai/LightOnOCR-3-4B) · [Project / GitHub](https://github.com/lightonai/LightOnOCR) · [Earlier LightOnOCR research paper](https://arxiv.org/abs/2601.14251) · [Batch settings and prompt verification](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_chandra_batch.py) · [Grounded title decoder](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_lighton_mlx.py) · [Checkpoint revisions](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


## structure-learned-groups

**v2: learned grouping**

Two 200-tree Extra Trees classifiers learn line joining and heading levels. This variant uses 100 join features and 43 group features, without document context.


**Training:** Annotate examples in other WFP reports → Train Extra Trees classifiers → Compare designs on validation reports

- **Annotate examples in other WFP reports:** An assistant labels heading text, levels and ordinary body text. The expanded training set contains 887 heading groups in 20 reports; validation and test reports are separate.
- **Train Extra Trees classifiers:** An Extra Trees classifier combines many randomized decision trees. Each tree uses measurements such as font size and spacing to vote for a class. Each component here has 200 trees, maximum depth 16, minimum leaf size 2, balanced classes and seed 42.
- **Compare designs on validation reports:** Use 21 headings in four separate reports to compare the line-only, joined-text and document-context designs. Their original exact group-and-level F1 scores were 55.3%, 63.6% and 69.8%; that earlier selection predates the new F0.5 objective.



**Inference:** Decide whether neighboring lines belong together → Build complete title groups → Classify the joined text → Choose each group’s level independently

- **Decide whether neighboring lines belong together:** A 200-tree Extra Trees classifier uses 100 measurements of the two lines, their differences and their page separation to predict join or separate.
- **Build complete title groups:** Join predicted continuations even across PDF block boundaries. Keep the IDs of the original lines so every group can be traced to the PDF.
- **Classify the joined text:** A second 200-tree Extra Trees classifier uses 43 text-and-style measurements to choose body text or H1–H5.
- **Choose each group’s level independently:** Take the highest-scoring class. This variant does not use table-of-contents clues or the predicted relationships between headings.



**Models and terms explained**

- [Extra Trees](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html): A classifier that averages predictions from many randomized decision trees. A tree makes a sequence of decisions about input measurements. This benchmark uses scikit-learn’s ExtraTreesClassifier, with 200 trees per component.
- [Features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py): The numeric measurements supplied to a classifier—for example font size, boldness, line spacing or whether a title occurs in the table of contents. They are calculated from the PDF, not supplied reference answers.
- [Validation reports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json): Reports kept separate from model fitting and used to choose between designs or decision settings. The later inspected test reports are now regression checks: they can expose a failure but no longer provide a fresh independent evaluation.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Estimator | sklearn.ensemble.ExtraTreesClassifier; scikit-learn 1.9.1; Python 3.12.3 |
| Trees per classifier | n_estimators=200 |
| Tree limits | max_depth=16; min_samples_leaf=2 |
| Feature sampling / weighting | max_features=0.8; class_weight="balanced" |
| Reproducibility / parallelism | random_state=42; n_jobs=4 |
| Other estimator options | Library defaults; no tree hyperparameter search was run |
| Join classifier | 100 features; 6,267 labeled adjacent-line pairs; classes 0=separate, 1=join |
| Group classifier | 43 features; 6,736 examples; classes body/H1–H5 |
| Total deployed trees | 2 ×200 =400 |
| Artifact sizes / fit | join.json 1,958,200 bytes / ≈0.816 s; group.json 17,519,049 bytes / ≈0.995 s |

**Training set and annotation source**

A single assistant reviewed source text, layout/page snippets and table-of-contents context and supplied explicit line groups and H levels. The annotation provenance does not record a precise model version used by the annotating assistant, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate reference labels. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The training split contains 20 WFP reports, 887 heading groups and 7,039 labeled lines. Line classes: body=5,849; H1=238; H2=391; H3=432; H4=128; H5=1; H6=0. Negative examples come from 112 fully reviewed training pages. Unmarked lines on positive-only annotation pages are not automatically negatives. The H5/H6 coverage is a material limitation.

Validation uses reports 103, 538, 176 and 128: 21 reference groups on 20 reviewed pages. The test from the second training experiment uses reports 321, 844, 560 and 394: 38 groups on 32 reviewed pages. Splits are by report, not random lines; report-template families are not held out. Those test pages have now been inspected and are results on previously inspected test documents for subsequent changes.


**Join and group targets**

The 33 measurements of selectable PDF text lines cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.

An adjacent pair is positive only if both lines belong to the same explicit annotated heading. Only pairs with known labels on both lines are trained. Pair features concatenate A, B, B−A and page difference: 3×33+1=100.

The group classifier trains on 887 annotated heading groups plus 5,849 reviewed singleton body lines. Its 43 features start from the 33 line features, recompute text indicators on the joined title, use the last line’s following gap, and add group length/page span plus mean/max size, bold, italic and width. Inference uses predicted groups, so join errors can propagate into classification.


**Selection and deployment**

We compared three pipeline variants, with identical fixed tree settings. Validation exact group-and-level F1 was 55.3% for expanded_line, 63.6% for learned_groups and 69.8% for context_relations. The highest validation F1 selected context_relations before the test from the second training experiment. Selection did not use the historical main-table results. F1 = 2 × exact group-and-level matches / (gold groups + predicted groups); group matching requires identical source-line membership.

Models are exported as data-only JSON arrays. Exported predict_proba is checked against scikit-learn with atol=1e-7. Runtime inference uses NumPy and float32 tree traversal; it needs no LLM or scikit-learn model server. Full selectable PDF text is retained. Parent IDs are derived from the predicted level stack, not separately learned or evaluated.

The main comparison parses all four historical PDFs (523 pages) on an Apple M4 Pro with 48 GB memory, but scores only 77 headings on 32 audited pages. Its fuzzy title matching plus exact level is different from the supervised exact group-and-level F1. Main-table scores are historical diagnostics, not the fresh supervised split. Timing covers extraction, feature construction and prediction; model-file loading occurs before the parser timer.

No LLM is needed at inference. Labels are assistant-assisted, not independently human-verified. Parent links are inferred, not evaluated. v2 main-table scores are historical diagnostics; the separate 38-heading pilot has a different metric.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Exact estimator constructor and JSON export](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Native line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [Group/context/pair features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py) · [Training components and variant selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/train.py) · [Recorded validation scores and training settings](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-v2/evidence/selection.json) · [PDF sources and report splits](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json) · [Reviewable heading annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/annotations.json) · [Inference, grouping and Viterbi](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py) · [Configuration source / evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md)


## evidencelab

**EvidenceLab — Docling + hierarchical post-processing**

EvidenceLab combines Docling 2.58.0 with a hierarchical post-processor, font and numbering rules, and final contents-list normalization. We score that final list exactly as returned.


**Inference:** Parse the full PDF with Docling → Run EvidenceLab’s hierarchy processing → Keep the final contents list

- **Parse the full PDF with Docling:** Docling 2.58.0 uses Heron layout detection and TableFormer fast. OCR is disabled. The isolated Linux ARM64 container has four CPU cores and a 12 GB memory limit.
- **Run EvidenceLab’s hierarchy processing:** docling-hierarchical-pdf 0.1.2 assigns levels from PDF hierarchy metadata when available, otherwise from heading geometry and font style. EvidenceLab applies its built-in safeguards afterward.
- **Keep the final contents list:** EvidenceLab creates and normalizes toc.txt, including front matter and numbered sections. We preserve its H levels and 80-character title limit.



**Models and terms explained**

- [Docling](https://github.com/docling-project/docling): PDF conversion software used here to detect text, layout and headings.
- [EvidenceLab](https://github.com/dividor/evidencelab): An evaluation-document application whose parsing pipeline adds hierarchy and contents-list processing to Docling.
- [docling-hierarchical-pdf](https://github.com/krrome/docling-hierarchical-pdf): The post-processor used by EvidenceLab to infer hierarchy from PDF metadata or heading layout and font measurements.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Source | dividor/evidencelab @ 40c4ae48296d68814af8d308a4aa5388c71cdd9e |
| Image | sha256:cab774211d7bd5a2287f5f8948d7698411c4169a4b56e346d2b52c75fa292bee |
| Packages | Docling 2.58.0; docling-hierarchical-pdf 0.1.2; runtime versions and image digest recorded |
| Runtime | Linux ARM64; 4 CPU cores; 12 GB memory limit; OMP_NUM_THREADS=4 |
| Parser | no_ocr=True; table_mode=fast; enable_chunking=False; use_subprocess=False; enable_superscripts=True; ocr_fallback=False |
| Hierarchy | hierarchical.postprocessor.ResultPostprocessor; upstream safeguards, hybrid font/numbering rules and TOC normalization remain unchanged |
| Models | Heron revision 8f39ad3c0b4c58e9c2d2c84a38465abf757272d8; docling-models revision fc0f2d45e2218ea24bce5045f58a389aed16dc23 |
| Scored output | Final toc.txt; native H levels and title truncation retained |
| Time | 9 min 50 sec for 523 pages; first-document time includes lazy model loading/download; constructor setup is recorded separately |
| Post-processor | docling-hierarchical-pdf 0.1.2; ResultPostprocessor(result, source=PDF, raise_on_error=False) |

**Training and selection**

No WFP-specific training or setting search was performed. This configuration reproduces the parser and post-processing in the running EvidenceLab image. It uses an older Docling release than our Docling-only rows, so the difference cannot be attributed to post-processing alone.


**Reproducibility**

The runner calls ParseProcessor.process_document without a database. The image digest, source revision, model revisions, file hashes, native headings, full-PDF timings and archived runner hash are recorded. Repeated runs download the recorded model revisions before switching Hugging Face to offline mode.

37/77 heading-level pairs are correct. There are 26 matched headings at the wrong level, 14 missing headings and 7 extra headings. This is not a complete, accurate outline.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/benchmark_evidencelab.py) · [Reproduction commands](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/evidencelab-and-ocr.md) · [Importer and output checks](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/pipeline_evidence.py) · [Pinned EvidenceLab parser](https://github.com/dividor/evidencelab/blob/40c4ae48296d68814af8d308a4aa5388c71cdd9e/pipeline/processors/parsing/parser.py) · [Pinned heading post-processing](https://github.com/dividor/evidencelab/blob/40c4ae48296d68814af8d308a4aa5388c71cdd9e/pipeline/processors/parsing/parser_headings.py) · [Saved evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/pipeline-runs/evidencelab.json) · [Hierarchy post-processor source](https://github.com/krrome/docling-hierarchical-pdf) · [Configuration source / evidence](https://github.com/dividor/evidencelab)


## structure-expanded-line

**v2: more annotations**

The line-only Extra Trees classifier is retrained on 20 reports and 887 heading groups. It uses 33 features and joins titles within PDF blocks.


**Training:** Annotate examples in other WFP reports → Train Extra Trees classifiers → Compare designs on validation reports

- **Annotate examples in other WFP reports:** An assistant labels heading text, levels and ordinary body text. The expanded training set contains 887 heading groups in 20 reports; validation and test reports are separate.
- **Train Extra Trees classifiers:** An Extra Trees classifier combines many randomized decision trees. Each tree uses measurements such as font size and spacing to vote for a class. Each component here has 200 trees, maximum depth 16, minimum leaf size 2, balanced classes and seed 42.
- **Compare designs on validation reports:** Use 21 headings in four separate reports to compare the line-only, joined-text and document-context designs. Their original exact group-and-level F1 scores were 55.3%, 63.6% and 69.8%; that earlier selection predates the new F0.5 objective.



**Inference:** Train on the expanded examples → Classify each new line → Join lines using PDF blocks → Keep the simpler design

- **Train on the expanded examples:** Fit a 200-tree Extra Trees classifier on 7,039 labeled lines, using 33 measurements per line.
- **Classify each new line:** Predict scores for ordinary body text and H1–H5. Choose the class with the highest score.
- **Join lines using PDF blocks:** Merge adjacent same-level heading lines only inside the same source PDF block. No model learns how to join lines in this variant.
- **Keep the simpler design:** Do not add table-of-contents context or a model for relationships between headings. Validation group-and-level F1 was 55.3%.



**Models and terms explained**

- [Extra Trees](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html): A classifier that averages predictions from many randomized decision trees. A tree makes a sequence of decisions about input measurements. This benchmark uses scikit-learn’s ExtraTreesClassifier, with 200 trees per component.
- [Features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py): The numeric measurements supplied to a classifier—for example font size, boldness, line spacing or whether a title occurs in the table of contents. They are calculated from the PDF, not supplied reference answers.
- [Validation reports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json): Reports kept separate from model fitting and used to choose between designs or decision settings. The later inspected test reports are now regression checks: they can expose a failure but no longer provide a fresh independent evaluation.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Estimator | sklearn.ensemble.ExtraTreesClassifier; scikit-learn 1.9.1; Python 3.12.3 |
| Trees per classifier | n_estimators=200 |
| Tree limits | max_depth=16; min_samples_leaf=2 |
| Feature sampling / weighting | max_features=0.8; class_weight="balanced" |
| Reproducibility / parallelism | random_state=42; n_jobs=4 |
| Other estimator options | Library defaults; no tree hyperparameter search was run |
| Deployed components | line: 33 features, 7,039 examples, 200 trees |
| Observed target classes | 0=body, 1–5=heading level; no H6 training examples |
| Artifact / fit | line.json: 22,737,104 bytes; fit ≈1.007 s; excludes extraction/export/validation |

**Training set and annotation source**

A single assistant reviewed source text, layout/page snippets and table-of-contents context and supplied explicit line groups and H levels. The annotation provenance does not record a precise model version used by the annotating assistant, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate reference labels. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The training split contains 20 WFP reports, 887 heading groups and 7,039 labeled lines. Line classes: body=5,849; H1=238; H2=391; H3=432; H4=128; H5=1; H6=0. Negative examples come from 112 fully reviewed training pages. Unmarked lines on positive-only annotation pages are not automatically negatives. The H5/H6 coverage is a material limitation.

Validation uses reports 103, 538, 176 and 128: 21 reference groups on 20 reviewed pages. The test from the second training experiment uses reports 321, 844, 560 and 394: 38 groups on 32 reviewed pages. Splits are by report, not random lines; report-template families are not held out. Those test pages have now been inspected and are results on previously inspected test documents for subsequent changes.


**Features and grouping**

The 33 measurements of selectable PDF text lines cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.

Line classification uses the largest class probability. The original grouping combines adjacent heading lines only when their PDF block and predicted level agree. There is no learned line-joining model, group classifier or Viterbi stage in this comparison.


**Selection and deployment**

We compared three pipeline variants, with identical fixed tree settings. Validation exact group-and-level F1 was 55.3% for expanded_line, 63.6% for learned_groups and 69.8% for context_relations. The highest validation F1 selected context_relations before the test from the second training experiment. Selection did not use the historical main-table results. F1 = 2 × exact group-and-level matches / (gold groups + predicted groups); group matching requires identical source-line membership.

Models are exported as data-only JSON arrays. Exported predict_proba is checked against scikit-learn with atol=1e-7. Runtime inference uses NumPy and float32 tree traversal; it needs no LLM or scikit-learn model server. Full selectable PDF text is retained. Parent IDs are derived from the predicted level stack, not separately learned or evaluated.

The main comparison parses all four historical PDFs (523 pages) on an Apple M4 Pro with 48 GB memory, but scores only 77 headings on 32 audited pages. Its fuzzy title matching plus exact level is different from the supervised exact group-and-level F1. Main-table scores are historical diagnostics, not the fresh supervised split. Timing covers extraction, feature construction and prediction; model-file loading occurs before the parser timer.

No LLM is needed at inference. Labels are assistant-assisted, not independently human-verified. Parent links are inferred, not evaluated. v2 main-table scores are historical diagnostics; the separate 38-heading pilot has a different metric.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/scripts/structure/train.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Exact estimator constructor and JSON export](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Native line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [Group/context/pair features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py) · [Training components and variant selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/structure/train.py) · [Recorded validation scores and training settings](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/structure-v2/evidence/selection.json) · [PDF sources and report splits](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json) · [Reviewable heading annotations](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/annotations.json) · [Inference, grouping and Viterbi](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_inference.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py) · [Configuration source / evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/supervised-structure-v2/outputs/structure-v2/report.md)


## supervised-extra-trees

**Supervised Extra Trees / CPU / assistant labels**

OUR METHOD v1 uses one 200-tree Extra Trees classifier trained on 16 WFP reports. It labels PDF text lines, then joins adjacent same-level lines within each block.


**Training:** Label training examples → Compare two classifiers → Choose the validation winner

- **Label training examples:** An assistant annotated 154 heading groups from 16 training reports. Separate reports were reserved for validation and testing.
- **Compare two classifiers:** Fit scaled LogisticRegression(C=1), a linear classifier, and a 200-tree Extra Trees classifier using fixed settings.
- **Choose the validation winner:** Extra Trees scored 69.1% exact-level line F1 versus 47.6% for logistic regression. Save the winning trained classifier without fitting it on the benchmark PDFs.



**Inference:** Measure each text line → Classify the line → Join wrapped heading lines → Export text and the outline

- **Measure each text line:** PyMuPDF reads the selectable text and 33 measurements, including font size, position, spacing and text patterns.
- **Classify the line:** A scikit-learn ExtraTreesClassifier with 200 trees predicts body text or a heading level. Each tree is limited to depth 16 and at least two training examples per leaf.
- **Join wrapped heading lines:** Merge adjacent heading lines with the same predicted level only when they are in the same PDF text block.
- **Export text and the outline:** Keep source lines and page numbers. Record each heading’s level and infer its parent from the preceding heading levels.



**Models and terms explained**

- [Extra Trees](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html): A classifier that averages predictions from many randomized decision trees. A tree makes a sequence of decisions about input measurements. This benchmark uses scikit-learn’s ExtraTreesClassifier, with 200 trees per component.
- [Features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/structure_features.py): The numeric measurements supplied to a classifier—for example font size, boldness, line spacing or whether a title occurs in the table of contents. They are calculated from the PDF, not supplied reference answers.
- [Validation reports](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/structure-v2/corpus.json): Reports kept separate from model fitting and used to choose between designs or decision settings. The later inspected test reports are now regression checks: they can expose a failure but no longer provide a fresh independent evaluation.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Estimator | sklearn.ensemble.ExtraTreesClassifier; scikit-learn 1.9.1; Python 3.12.3 |
| Trees per classifier | n_estimators=200 |
| Tree limits | max_depth=16; min_samples_leaf=2 |
| Feature sampling / weighting | max_features=0.8; class_weight="balanced" |
| Reproducibility / parallelism | random_state=42; n_jobs=4 |
| Other estimator options | Library defaults; no tree hyperparameter search was run |
| Training set | 154 heading groups / 16 WFP reports |
| Alternative estimator | StandardScaler + LogisticRegression(C=1, class_weight="balanced", max_iter=3000, random_state=42) |
| Selected artifact | 200-tree JSON model, 9.97 MiB; recorded fit time ≈0.455 s, excluding preparation |

**Labels and features**

A single assistant reviewed source text, layout/page snippets and table-of-contents context and supplied explicit line groups and H levels. The annotation provenance does not record a precise model version used by the annotating assistant, and there was no independent human adjudication. These labels are reviewable training targets, not demonstrated 100%-accurate reference labels. This trains classical classifiers from labels; it does not fine-tune an LLM or transfer neural weights.

The 33 measurements of selectable PDF text lines cover font size relative to document body text, font-size rank, bold/italic proportions, RGB color, normalized position/width/height, gaps, adjacent-line style/block indicators, repeated-text count, log character/word counts, uppercase/digit fractions, numeric-prefix depth, number-only lines, dot leaders, sentence endings and a generic multilingual caption-prefix indicator. Body font size is the size accounting for the most characters. These are engineered features, including text-pattern indicators; this is not a rule-free model.


**What was actually tuned**

Two estimator families were compared using validation exact-level LINE F1: logistic regression 47.6%, Extra Trees 69.1%. Tree parameters and logistic C were fixed, not searched. Validation contains 21 heading groups across four reports; the separate v1 test contains 27 groups across four reports.

The v1 test scored 82.0% exact-level line F1 and 22/27 complete heading groups at the right level. This differs from the v2 group-F1 metric. The v1 training set was expanded with additional reviewed training pages before the reported selection/test; it is smaller than the later 887-group v2 set.


**Export and measured scope**

Models are exported as data-only JSON arrays. Exported predict_proba is checked against scikit-learn with atol=1e-7. Runtime inference uses NumPy and float32 tree traversal; it needs no LLM or scikit-learn model server. Full selectable PDF text is retained. Parent IDs are derived from the predicted level stack, not separately learned or evaluated.

The main comparison parses all four historical PDFs (523 pages) on an Apple M4 Pro with 48 GB memory, but scores only 77 headings on 32 audited pages. Its fuzzy title matching plus exact level is different from the supervised exact group-and-level F1. Main-table scores are historical diagnostics, not the fresh supervised split. Timing covers extraction, feature construction and prediction; model-file loading occurs before the parser timer.

Assistant-produced labels lack independent adjudication. V1 selection uses line F1, not v2 group F1. Same-block grouping can split multi-block headings; parent edges are inferred and unscored.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/supervised/compare.py) · [Extra Trees implementation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html) · [Extra Trees algorithm paper (2006)](https://doi.org/10.1007/s10994-006-6226-1) · [Estimator definitions](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_models.py) · [Line features](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_features.py) · [V1 training and selection](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/supervised/train.py) · [V1 validation evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/supervised/evidence/selection.json) · [V1 corpus and source URLs](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/supervised/corpus.json) · [Grouping and parent inference](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/supervised_inference.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py) · [Configuration source / evidence](https://github.com/dividor/pdf-heading-benchmark/blob/main/src/pdf_heading_benchmark/supervised_models.py)


## mineru-basic

**MinerU 4.2.3 basic CPU**

MinerU 4.2.3 uses its basic ONNX CPU parser. We retain its document-title and paragraph-title blocks and supplied levels.


**Inference:** Run the basic CPU parser → Process every PDF page → Collect detected titles → Keep the supplied hierarchy

- **Run the basic CPU parser:** Set small_backend="onnx" and onnx_device="cpu". ONNX Runtime executes the parser’s model on the CPU.
- **Process every PDF page:** Use MinerUParser with parse_mode="auto", page_range="all" and image_analysis=False.
- **Collect detected titles:** Read the parser’s document-title and paragraph-title blocks: DocTitleBlock and ParagraphTitleBlock.
- **Keep the supplied hierarchy:** Export the block’s text, level and bounding box. No extra level classifier or document-specific repair is applied.



**Models and terms explained**

- [MinerU](https://github.com/opendatalab/MinerU): Document parsing software; this row uses its basic CPU parser, not the separate Pro image model.
- [ONNX Runtime](https://onnxruntime.ai/docs/): Software that executes a model saved in the ONNX format. The basic MinerU run uses it on the CPU.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Package | mineru==4.2.3 |
| Backend | small_backend="onnx"; onnx_device="cpu" |
| Parser | tier="basic"; parse_mode="auto"; image_analysis=False; page_range="all" |
| External assistance | Empty VLM server URL; runner rejects enabled LLM title leveling or cross-page table-cell merging |
| Tuning | No benchmark training; individual parser model revisions are not explicitly pinned by this runner |

**Native extraction**

Heading text, level, box and page are taken from the parser’s title objects. The runner does not add a title hierarchy prompt or rewrite missing levels.


**Measured scope and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

The parse call is timed; parser construction happens before that timer.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

This CPU tier is different from the MinerU Pro vision model below.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_mineru.py) · [Project / GitHub](https://github.com/opendatalab/MinerU) · [ONNX configuration and block extraction](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_mineru.py) · [Pinned environment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/mineru.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


## xiaomi-ocr0-official-metal

**Xiaomi-OCR-0 — upstream two-stage pipeline, Metal**

Xiaomi’s upstream two-stage pipeline uses native PaddleX layout on CPU and BF16 recognition through vLLM Metal. Its default formatter assigns paragraph titles H2.


**Inference:** Render each audited PDF page → Locate text, titles, tables and formulas → Recognize each crop with Xiaomi-OCR-0 → Apply the upstream retry and assembly code

- **Render each audited PDF page:** Render the same 32 physical pages at 200 DPI in RGB. No native PDF text, document tags or reference headings enter inference.
- **Locate text, titles, tables and formulas:** Run native PP-DocLayoutV3 through PaddleX on CPU with the published benchmark threshold 0.25. Xiaomi’s upstream serializer preserves the detected regions and reading order.
- **Recognize each crop with Xiaomi-OCR-0:** The unchanged upstream CLI sends one region at a time to vLLM Metal. Original BF16 weights receive the official text, formula or table prompt; tables use Xiaomi’s structured table tokens.
- **Apply the upstream retry and assembly code:** Use the official repetition retry policy, then convert formulas and tables and assemble the page. The default title_profile="v2" makes document titles H1 and paragraph titles H2. No retry was triggered across these 32 pages.



**Models and terms explained**

- [PP-DocLayoutV3](https://huggingface.co/PaddlePaddle/PP-DocLayoutV3): Paddle’s model for locating and classifying page regions, such as a title, paragraph, table or formula.
- [BF16](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0): A 16-bit floating-point format for model weights. This run uses the original weights rather than a quantized conversion.
- [vLLM Metal](https://github.com/vllm-project/vllm-metal): A plugin that runs supported vLLM models on Apple’s Metal GPU backend. It differs from the CUDA runtime used in the published benchmark.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Weights | xiaomi-research/Xiaomi-OCR-0, original BF16; revision bbd8cf8d21f256b3644b44cb860f3a7cecb93c30 |
| Upstream code | SeerRay-Lab/Xiaomi-OCR-0, revision 4abc240285b69a2965cf64762101ddb4ab35f32d |
| Layout | PaddleX 3.7.2 / PaddlePaddle 3.3.1; native PP-DocLayoutV3; CPU; threshold=0.25 |
| Recognition runtime | vLLM 0.34.0 with vllm-metal 0.34.0; original BF16; one concurrent sequence; seed=42; GPU memory fraction=0.8 |
| Decoding | temperature=0; top_p=0.8; presence_penalty=0; repetition_penalty=1; max_tokens=16384; timeout=600 seconds |
| Repetition retry | Enabled; retry presence penalty=1.5; same-character run=128; minimum repeats=8; minimum repeated characters=512; ratio=0.5; maximum unit=256 characters |
| Assembly | Default MergeOptions(title_profile="v2"); no number-based title profile or hierarchy repair |
| Concurrency | One OCR model at a time; one page and one upstream worker at a time |

**What changed from the earlier Xiaomi row**

The earlier trial sent each complete page directly to Xiaomi through MLX. This run uses the upstream layout, crop recognition, table conversion and page assembly pipeline. Correct title-level pairs increase from 29 to 31 out of 77; joint F0.5 increases from 39.7% to 42.9%.

The pipeline remains adapted to this Mac: layout uses CPU, and recognition uses vLLM Metal instead of the documented CUDA servers. The model weights and upstream recognition/assembly code are pinned.


**Why the heading levels are limited**

We executed the upstream paragraph-title formatter on “# Introduction”, “### Methods” and “1.1 Features”. It returned H2 for all three. In the actual mid-term report, page 26, both “1. Introduction” and “1.1 EVALUATION FEATURES” are H2. The ordinary paragraph beginning “3. The MTE’s key features are” is also emitted as H2.

The saved region field named merged has already passed through assembly. It is not an untouched model response. We therefore do not claim the recognition model itself chose every reported level.


**What the timing includes**

Measured total: 7 min 52 sec for 32 pages, averaging 14.8 seconds per page. Includes rendering, CPU layout, launching the upstream command separately for each page, recognition, assembly and saving. CPU layout initialization took a separate 2.0 seconds; recognition weights were already loaded after the cover smoke test.

All 32 pages completed without reported recognition failures. The upstream retry reports show zero repetition retries. Complete per-request finish reasons are unavailable, so token-limit hits are not reported as zero. Only this OCR model was running; unrelated host workloads were not controlled.

The default assembler limits detected title regions to H1/H2. This is a measurement of the complete local pipeline, not an isolated test of the recognition weights or a reproduction of CUDA benchmark throughput.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_official_xiaomi.py) · [Model / Hugging Face](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0) · [Official evaluation instructions](https://github.com/SeerRay-Lab/Xiaomi-OCR-0/blob/4abc240285b69a2965cf64762101ddb4ab35f32d/evaluation_pipeline/README.md) · [Official heading formatter](https://github.com/SeerRay-Lab/Xiaomi-OCR-0/blob/4abc240285b69a2965cf64762101ddb4ab35f32d/postprocess/markdown_merge.py#L301) · [Measured evidence and predictions](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/official-pipelines/xiaomi_ocr0_official_metal.json) · [Reproduction and runtime differences](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/official-pipelines.md) · [Metal runtime](https://github.com/vllm-project/vllm-metal/tree/v0.34.0)


## qwen-ids-union

**Qwen3.5-4B / union candidates**

Qwen3.5-4B, quantized to 4 bits, assigns levels to the combined Docling and PyMuPDF4LLM candidate list. It receives text and page numbers only.


**Inference:** Collect possible headings → Give each title a reference ID → Ask Qwen to assign levels → Validate the reply

- **Collect possible headings:** Combine headings proposed by both parsers. Merge same-page titles with normalized similarity of at least 0.90.
- **Give each title a reference ID:** Send one list per document containing IDs such as h0000, title text and page number. An ID lets the reply refer unambiguously to an input title.
- **Ask Qwen to assign levels:** Use Qwen3.5-4B with temperature=0, max_tokens=4096, seed=42 and thinking disabled. These are fixed generation settings, not training.
- **Validate the reply:** Require a JSON mapping from every supplied ID to a level 1–20 or null. Null means rejected as a heading. Invalid replies are rejected rather than silently repaired.



**Models and terms explained**

- [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B): A pretrained language model with approximately four billion parameters. Here it reads lists of possible headings and assigns levels.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.
- [4-bit / 8-bit weights](https://github.com/ml-explore/mlx-lm): Reduced-precision representations of a model’s learned numbers, used to lower memory requirements. The number describes storage precision, not heading depth or model accuracy.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | mlx-community/Qwen3.5-4B-MLX-4bit; revision 32f3e8ecf654 (full pin in configs/models.json) |
| Input | One full-document text candidate list; num_images=0; enable_thinking=False |
| Generation | temperature=0; max_tokens=4096; prefill_step_size=256; MLX seed=42 |
| Candidate source | Docling + PyMuPDF4LLM |
| Output contract | Exact input-ID key set; integer level 1–20 or null; invalid response produces null levels for that document |
| Tuning | Fixed prompt and pretrained quantized weights; no fine-tuning or recorded prompt search |

**Candidate construction**

The union uses same-page greedy one-to-one matching at normalized title similarity ≥0.90. It strips HTML, normalizes Unicode and alphanumeric text, and uses SequenceMatcher with autojunk=False. Matched source candidates are deduplicated; unmatched candidates are merged while preserving relative order. This operates on parser outputs, not gold labels.


**Prompt and decoding**

The same PROMPT is used for each report. It asks for logical hierarchy, treats executive summaries/main sections/annexes as top level, rejects captions, table cells, running headers, emphasis and TOC entries, and requires consistent parallel sections. Cover text must not shift body levels; absolute page number must not determine level. The complete prompt is linked in the runner.

The decoder strips a code-fence wrapper, then validates every ID and value. Accepted IDs are joined back to their original titles and pages; null rejects a candidate. A missing source title cannot be created by this method. Invalid responses are recorded as errors and yield no accepted headings for that document.


**Measured scope and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

Reported time covers the hierarchy-generation stage only. Candidate extraction and model loading/download are excluded; end-to-end deployment must also pay for the source parser.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

A missing candidate cannot be recovered by this refinement. JSON is validated; invalid replies are not silently repaired.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) · [Base model / Hugging Face](https://huggingface.co/Qwen/Qwen3.5-4B) · [Tested 4-bit model / HF](https://huggingface.co/mlx-community/Qwen3.5-4B-MLX-4bit) · [Exact PROMPT, sampling and validation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_ids.py) · [Model revision pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Candidate union and order preservation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/build_union.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


## xiaomi-ocr0

**Xiaomi-OCR-0 — MLX whole page**

Xiaomi-OCR-0 reads whole-page images through MLX using e2e_img2md. Its generated Markdown supplies the heading levels.


**Inference:** Render the fixed WFP sample → Read the entire page with Xiaomi-OCR-0 → Keep the model’s own hierarchy

- **Render the fixed WFP sample:** Render all 32 audit pages at 200 DPI for Xiaomi-OCR-0. Supply pixels only: no native PDF text, tags, reference headings or earlier-page memory.
- **Read the entire page with Xiaomi-OCR-0:** Use the documented e2e_img2md instruction: extract the main body in reading order as Markdown, with OTSL tables and LaTeX formulas; ignore headers and footers. The Qwen3.5-based 0.8B model runs through MLX on Metal.
- **Keep the model’s own hierarchy:** Greedy decoding, temperature 0, seed 42, thinking disabled, maximum 16,384 output tokens per page. Read Markdown heading tokens as H1–H6, including setext headings. Do not infer headings from bold text or adjust levels.



**Models and terms explained**

- [Xiaomi-OCR-0](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0): The upstream 0.8B-parameter visual recognition model, loaded from its pinned Hugging Face revision.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework; recognition uses Metal GPU kernels. Layout detection, where present, runs separately on CPU.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | xiaomi-research/Xiaomi-OCR-0; revision bbd8cf8d21f256b3644b44cb860f3a7cecb93c30 |
| Model size / weights | 0.8B parameters; original BF16 weights, no weight quantization or fine-tuning |
| Runtime | MLX 0.32.4; mlx-vlm 0.8.0; Transformers 5.23.0; Apple M4 Pro, 48 GB unified memory |
| Input | 32 fixed physical PDF pages; PyMuPDF render at 200 DPI; pixels only |
| Decoding | temperature=0; seed=42; enable_thinking=False |
| Concurrency | One model and one page at a time; region recognition sequential; Metal kernels internally parallel |
| Limits | Soft 600-second timeout per recognition request, checked between streamed chunks |
| Timing | Includes rendering, CPU layout when used, recognition and assembly; model loading recorded separately |
| Output budget | 16,384 tokens per whole page |
| Prompt | Exact upstream evaluation_pipeline/e2e_img2md.py whole-page Markdown instruction; recorded in runner |

**What was trained, and by whom**

We use the published Xiaomi-OCR-0 weights at the pinned revision. We do not train, fine-tune or select checkpoints on these four WFP reports. The model card documents the upstream training; our contribution here is the Apple Silicon evaluation adapter.


**What this row establishes**

This is the documented whole-page variant, not Xiaomi’s two-stage layout-plus-recognition configuration behind its strongest published scores.

Broad OCR benchmark quality does not establish correct heading depth. This row scores the headings the pipeline actually emits, without document-specific corrections. Native prose retention measures overlapping five-word sequences from PDF paragraphs of at least 50 words; it does not measure table accuracy or reading order.

This is the documented whole-page variant, not Xiaomi’s two-stage layout-plus-recognition configuration behind its strongest published scores.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_field_candidate.py) · [Official model and model card](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0) · [Upstream implementation and documentation](https://github.com/xiaomi-research/Xiaomi-OCR-0) · [Download pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/field-candidates.json) · [Protocol and reproduction commands](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/field-candidates.md) · [Measured predictions and page telemetry](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/field-candidates/xiaomi_ocr0.json)


## qwen-ids-pymupdf4llm

**Qwen3.5-4B / PyMuPDF candidates**

Qwen3.5-4B, quantized to 4 bits, assigns levels to PyMuPDF4LLM candidates. It receives text and page numbers only.


**Inference:** Collect possible headings → Give each title a reference ID → Ask Qwen to assign levels → Validate the reply

- **Collect possible headings:** Use the headings marked in PyMuPDF4LLM’s Markdown for the full PDF.
- **Give each title a reference ID:** Send one list per document containing IDs such as h0000, title text and page number. An ID lets the reply refer unambiguously to an input title.
- **Ask Qwen to assign levels:** Use Qwen3.5-4B with temperature=0, max_tokens=4096, seed=42 and thinking disabled. These are fixed generation settings, not training.
- **Validate the reply:** Require a JSON mapping from every supplied ID to a level 1–20 or null. Null means rejected as a heading. Invalid replies are rejected rather than silently repaired.



**Models and terms explained**

- [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B): A pretrained language model with approximately four billion parameters. Here it reads lists of possible headings and assigns levels.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.
- [4-bit / 8-bit weights](https://github.com/ml-explore/mlx-lm): Reduced-precision representations of a model’s learned numbers, used to lower memory requirements. The number describes storage precision, not heading depth or model accuracy.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | mlx-community/Qwen3.5-4B-MLX-4bit; revision 32f3e8ecf654 (full pin in configs/models.json) |
| Input | One full-document text candidate list; num_images=0; enable_thinking=False |
| Generation | temperature=0; max_tokens=4096; prefill_step_size=256; MLX seed=42 |
| Candidate source | PyMuPDF4LLM |
| Output contract | Exact input-ID key set; integer level 1–20 or null; invalid response produces null levels for that document |
| Tuning | Fixed prompt and pretrained quantized weights; no fine-tuning or recorded prompt search |

**Candidate construction**

Only PyMuPDF4LLM supplies candidates. This variant changes the candidate source, while keeping the Qwen model, prompt and generation settings the same as the other ID-refinement rows.


**Prompt and decoding**

The same PROMPT is used for each report. It asks for logical hierarchy, treats executive summaries/main sections/annexes as top level, rejects captions, table cells, running headers, emphasis and TOC entries, and requires consistent parallel sections. Cover text must not shift body levels; absolute page number must not determine level. The complete prompt is linked in the runner.

The decoder strips a code-fence wrapper, then validates every ID and value. Accepted IDs are joined back to their original titles and pages; null rejects a candidate. A missing source title cannot be created by this method. Invalid responses are recorded as errors and yield no accepted headings for that document.


**Measured scope and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

Reported time covers the hierarchy-generation stage only. Candidate extraction and model loading/download are excluded; end-to-end deployment must also pay for the source parser.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

A missing candidate cannot be recovered by this refinement. JSON is validated; invalid replies are not silently repaired.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) · [Base model / Hugging Face](https://huggingface.co/Qwen/Qwen3.5-4B) · [Tested 4-bit model / HF](https://huggingface.co/mlx-community/Qwen3.5-4B-MLX-4bit) · [Exact PROMPT, sampling and validation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_ids.py) · [Model revision pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Candidate parser](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_pymupdf4llm.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


## pymupdf4llm

**PyMuPDF4LLM 2.1**

PyMuPDF4LLM 2.1 converts selectable text to Markdown. Its heading markers supply the levels; OCR is disabled.


**Inference:** Read the complete PDF → Convert one page at a time → Read Markdown headings → Keep text and page numbers

- **Read the complete PDF:** Use the PDF’s selectable text, fonts and layout rather than recognizing text from images.
- **Convert one page at a time:** Run to_markdown with page_chunks=True and use_ocr=False. Each output keeps its original PDF page number.
- **Read Markdown headings:** A line starting with # is H1; ## is H2, and so on through H6. We do not add a custom font-size threshold.
- **Keep text and page numbers:** Export heading titles and levels together with the Markdown text and the original page numbers.



**Models and terms explained**

- [PyMuPDF4LLM](https://github.com/pymupdf/pymupdf4llm): A library that converts PDF text and layout into Markdown, including heading markers.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Package | pymupdf4llm==2.1 |
| Call | to_markdown(pdf, page_chunks=True, use_ocr=False) |
| Heading parser | Start-of-line #{1,6}, followed by whitespace and nonempty text |
| Tuning / prompt | No benchmark fitting, prompt or manual font-threshold override; other options use package defaults |

**Extraction and decoding**

Markdown determines both heading membership and H level. The adapter does not repair typography-driven mistakes or infer hierarchy from section numbers. Full text is retained in page chunks and Markdown.


**Measured scope and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

Timing covers the conversion call; JSON/Markdown heading decoding is a separate adapter step.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

Typography-driven Markdown can confuse display text with section headings.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_pymupdf4llm.py) · [Project / GitHub](https://github.com/pymupdf/pymupdf4llm) · [Documentation](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/) · [Markdown conversion and heading regex](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_pymupdf4llm.py) · [Pinned environment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/pymupdf.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


## qwen-ids-mineru-basic

**Qwen3.5-4B / MinerU candidates**

Qwen3.5-4B, quantized to 4 bits, assigns levels to MinerU basic candidates. It receives text and page numbers only.


**Inference:** Collect possible headings → Give each title a reference ID → Ask Qwen to assign levels → Validate the reply

- **Collect possible headings:** Use the document-title and paragraph-title blocks proposed by MinerU across the full PDF.
- **Give each title a reference ID:** Send one list per document containing IDs such as h0000, title text and page number. An ID lets the reply refer unambiguously to an input title.
- **Ask Qwen to assign levels:** Use Qwen3.5-4B with temperature=0, max_tokens=4096, seed=42 and thinking disabled. These are fixed generation settings, not training.
- **Validate the reply:** Require a JSON mapping from every supplied ID to a level 1–20 or null. Null means rejected as a heading. Invalid replies are rejected rather than silently repaired.



**Models and terms explained**

- [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B): A pretrained language model with approximately four billion parameters. Here it reads lists of possible headings and assigns levels.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.
- [4-bit / 8-bit weights](https://github.com/ml-explore/mlx-lm): Reduced-precision representations of a model’s learned numbers, used to lower memory requirements. The number describes storage precision, not heading depth or model accuracy.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | mlx-community/Qwen3.5-4B-MLX-4bit; revision 32f3e8ecf654 (full pin in configs/models.json) |
| Input | One full-document text candidate list; num_images=0; enable_thinking=False |
| Generation | temperature=0; max_tokens=4096; prefill_step_size=256; MLX seed=42 |
| Candidate source | MinerU basic |
| Output contract | Exact input-ID key set; integer level 1–20 or null; invalid response produces null levels for that document |
| Tuning | Fixed prompt and pretrained quantized weights; no fine-tuning or recorded prompt search |

**Candidate construction**

Only MinerU basic supplies candidates. This variant changes the candidate source, while keeping the Qwen model, prompt and generation settings the same as the other ID-refinement rows.


**Prompt and decoding**

The same PROMPT is used for each report. It asks for logical hierarchy, treats executive summaries/main sections/annexes as top level, rejects captions, table cells, running headers, emphasis and TOC entries, and requires consistent parallel sections. Cover text must not shift body levels; absolute page number must not determine level. The complete prompt is linked in the runner.

The decoder strips a code-fence wrapper, then validates every ID and value. Accepted IDs are joined back to their original titles and pages; null rejects a candidate. A missing source title cannot be created by this method. Invalid responses are recorded as errors and yield no accepted headings for that document.


**Measured scope and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

Reported time covers the hierarchy-generation stage only. Candidate extraction and model loading/download are excluded; end-to-end deployment must also pay for the source parser.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

A missing candidate cannot be recovered by this refinement. JSON is validated; invalid replies are not silently repaired.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_qwen_ids.py) · [Base model / Hugging Face](https://huggingface.co/Qwen/Qwen3.5-4B) · [Tested 4-bit model / HF](https://huggingface.co/mlx-community/Qwen3.5-4B-MLX-4bit) · [Exact PROMPT, sampling and validation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_qwen_ids.py) · [Model revision pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Candidate parser](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_mineru.py) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


## docling-tuned

**Docling fixed tolerance 0.15**

Docling 2.151.1 runs HeadingHierarchyModel with style_size_tolerance=0.15. Detection is shared with the default run.


**Inference:** Read the text and page layout → Keep each item’s location → Change the style tolerance → Export headings and levels

- **Read the text and page layout:** Process the full PDF on the CPU with eight threads. Optical character recognition (OCR) and table reconstruction are disabled because these PDFs already contain selectable text.
- **Keep each item’s location:** Save parsed page information, including text positions, so the hierarchy step can inspect layout. The code option is generate_parsed_pages=True.
- **Change the style tolerance:** Set style_size_tolerance=0.15 in HeadingHierarchyModel. Start from the original conversion so this is not a second refinement of the default hierarchy result.
- **Export headings and levels:** Save each heading’s text, supplied H level, PDF page and bounding box—the rectangle around its text.



**Models and terms explained**

- [Docling](https://github.com/docling-project/docling): PDF conversion software used here to identify section headings and read or infer their levels.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Package | docling==2.151.1 |
| Device / parallelism | CPU; num_threads=8 |
| Conversion | do_ocr=False; do_table_structure=False; generate_parsed_pages=True |
| Hierarchy | enabled=True; style_size_tolerance=0.15; other settings use library defaults |
| Model provenance | Package-managed layout models; the runner does not explicitly pin individual layout-model revisions. |

**What changed and how it was selected**

Use Docling 2.151.1 with a fixed font-style tolerance of 0.15 in its hierarchy step. This setting was applied to every report; it was an exploratory choice, not a demonstrated best setting.

These are fixed configurations, not a learned WFP-specific correction or a recorded hyperparameter search. The tolerance variant is exploratory; “tuned” in its historical row name should not be read as a validated optimum.


**Output and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

The variants share one base conversion. Its recorded time includes first model load/download. The ordinary hierarchy pass has a separate timer; the tolerance pass was not separately timed. Their table times therefore do not represent three independent end-to-end conversions.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

These variants share detected blocks. A hierarchy stage cannot recover a heading absent from its inputs. The tolerance variant is exploratory.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) · [Project / GitHub](https://github.com/docling-project/docling) · [Docling technical report (2024)](https://arxiv.org/abs/2408.09869) · [Conversion and both hierarchy passes](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_docling.py) · [Pinned environment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/docling.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


## marker

**Marker 2.2 no OCR/LLM**

Marker 2.2 runs local CPU models with OCR and LLM assistance disabled. SectionHeader HTML tags supply heading levels.


**Inference:** Load Marker’s local models → Read the PDF’s existing text → Find section-heading blocks → Preserve unknown levels

- **Load Marker’s local models:** Use create_model_dict(device="cpu", no_server=True). Model inference runs on this machine.
- **Read the PDF’s existing text:** Convert the full document with JSONRenderer, no_ocr mode and use_llm=False.
- **Find section-heading blocks:** Inspect each SectionHeader block. HTML tags such as <h1> and <h2> specify its heading level.
- **Preserve unknown levels:** If Marker identifies a title but supplies no heading tag, keep its text with an unknown level. Do not guess a replacement.



**Models and terms explained**

- [Marker](https://github.com/datalab-to/marker): Document conversion software. This run uses its local models on the CPU and reads heading tags from the output.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Package | marker-pdf==2.2 |
| Models | create_model_dict(device="cpu", no_server=True); internal checkpoints not explicitly pinned by this runner |
| Renderer | marker.renderers.json.JSONRenderer |
| Configuration | mode="no_ocr"; disable_ocr=True; use_llm=False; disable_image_extraction=True; disable_tqdm=True |
| Tuning | No benchmark fine-tuning or prompt; remaining options use package defaults |

**Output adapter**

The adapter enumerates output pages from 1, visits nested SectionHeader blocks and uses BeautifulSoup to identify h1–h6 tags. A title without such a tag remains a heading candidate with an unknown level.


**Measured scope and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

The timer starts before create_model_dict, so model loading/download and shutdown are included. This timing boundary differs from the vision-model generation-only measurements.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

This benchmark is the local no-OCR/no-LLM configuration, not Marker with generative assistance.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_marker.py) · [Project / GitHub](https://github.com/datalab-to/marker) · [Model construction and JSON decoding](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_marker.py) · [Pinned environment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/marker.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


## paddleocr-vl16-official

**PaddleOCR-VL-1.6 — official Apple Silicon pipeline**

PaddleOCR 3.7.0 runs the complete v1.6 pipeline: native PaddleX layout on CPU, PaddleOCR-VL-1.6 on Metal, then Paddle’s Markdown assembler.


**Inference:** Render each audit page → Run Paddle’s native layout detector → Recognize regions on the Mac GPU → Use Paddle’s own Markdown output

- **Render each audit page:** PyMuPDF renders the same 32 physical PDF pages at 200 DPI. Only RGB pixels enter the pipeline. No PDF text, tags, reference labels or previous-page context is supplied.
- **Run Paddle’s native layout detector:** PaddleOCRVL(pipeline_version="v1.6", device="cpu") uses PP-DocLayoutV3 in PaddlePaddle 3.3.1. PaddleX 3.7.2 applies its own threshold 0.3, suppression, box merging and reading-order processing.
- **Recognize regions on the Mac GPU:** The pipeline sends its crops and task prompts to the official mlx-vlm-server backend. The original BF16 PaddleOCR-VL-1.6 weights run in MLX 0.32.4 / mlx-vlm 0.8.0. Temperature is 0; requests are sequential.
- **Use Paddle’s own Markdown output:** Read result.markdown["markdown_texts"] from the unmodified Paddle pipeline. Preserve every heading marker. The native pipeline still emits "1. Introduction" as H3 on the mid-term report, page 26; this is measured output, not a level correction.



**Models and terms explained**

- [PaddleOCR-VL-1.6](https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6): The upstream 0.9B-parameter visual recognition model, loaded from its pinned Hugging Face revision.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework; recognition uses Metal GPU kernels. Layout detection, where present, runs separately on CPU.
- [PP-DocLayoutV3](https://huggingface.co/PaddlePaddle/PP-DocLayoutV3_safetensors): A document-layout detector that labels regions such as titles, text, tables and figures. Its block labels and the Markdown assembler help determine the emitted hierarchy.
- [PaddleX](https://github.com/PaddlePaddle/PaddleX): Paddle’s pipeline framework. This run uses its native layout detector and Markdown assembly, not MiniCPM’s replacements.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Pipeline | paddleocr==3.7.0; paddlex==3.7.2; paddlepaddle==3.3.1; pipeline_version=v1.6 |
| Weights | PaddlePaddle/PaddleOCR-VL-1.6 @132c45f52c0a26ed5a6b2f6bd8e3985794cc27dd; original BF16 |
| Hardware | Apple M4 Pro; 48 GB unified memory; Paddle layout on CPU, MLX recognition on Metal |
| Concurrency | One model, one page and one recognition request at a time; use_queues=False; vl_rec_max_concurrency=1 |
| Layout | PP-DocLayoutV3 native Paddle weights; threshold=0.3; native v1.6 merging defaults |
| Recognition | temperature=0; upstream per-region output budget and task prompts |
| Other pipeline options | v1.6 defaults: chart recognition=False, seal recognition=False, document preprocessing=False; merge_layout_blocks=True |
| Image bounds limitation | Paddle’s mlx-vlm client warns that min_pixels and max_pixels are not supported by this backend. The model processor uses its own bounds. |
| Timing | 291.97 seconds for 32 pages (9.12 seconds/page). Includes rendering, layout, recognition, assembly and JSON saving. CPU pipeline initialization: 1.52 seconds separately. Recognition model was preloaded. |
| Request telemetry | No page errors. Per-request finish reasons and token-limit counts are not exposed by this pipeline, so they are not reported as zero. |

**What changed from the earlier Paddle row**

The earlier adaptation used a Transformers layout detector and MiniCPM’s Markdown assembler. This run calls PaddleOCRVL directly and uses Paddle’s native pipeline throughout. Model weights and the 32-page sample are unchanged.

Correct title-and-level matches rose from 16 to 18. There are still 50 matched titles with wrong levels, 9 missing reference headings and 3 extra predictions. This run does not establish general document-hierarchy accuracy.

This is the documented Apple Silicon pipeline, not the NVIDIA deployment used in published OCR charts. Frozen references are assistant annotations, not independently human-validated. No hierarchy repairs were applied.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_official_paddle.py) · [Official Apple Silicon pipeline guide](https://www.paddleocr.ai/latest/en/version3.x/pipeline_usage/PaddleOCR-VL-Apple-Silicon.html) · [Model weights and model card](https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6) · [Dependency pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/paddle-official.txt) · [Measured run evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/official-pipelines/paddleocr_vl16_official.json)


## docling-default

**Docling 2.151.1 default**

Docling 2.151.1 reads native PDF text on CPU. This row uses its original heading levels, without a second hierarchy pass.


**Inference:** Read the text and page layout → Keep each item’s location → Keep Docling’s original levels → Export headings and levels

- **Read the text and page layout:** Process the full PDF on the CPU with eight threads. Optical character recognition (OCR) and table reconstruction are disabled because these PDFs already contain selectable text.
- **Keep each item’s location:** Save parsed page information, including text positions, so the hierarchy step can inspect layout. The code option is generate_parsed_pages=True.
- **Keep Docling’s original levels:** Read the level attached to each detected section heading directly from Docling’s conversion output.
- **Export headings and levels:** Save each heading’s text, supplied H level, PDF page and bounding box—the rectangle around its text.



**Models and terms explained**

- [Docling](https://github.com/docling-project/docling): PDF conversion software used here to identify section headings and read or infer their levels.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Package | docling==2.151.1 |
| Device / parallelism | CPU; num_threads=8 |
| Conversion | do_ocr=False; do_table_structure=False; generate_parsed_pages=True |
| Hierarchy | No explicit HeadingHierarchyModel pass |
| Model provenance | Package-managed layout models; the runner does not explicitly pin individual layout-model revisions. |

**What changed and how it was selected**

Use the heading levels returned by Docling 2.151.1 when it first reads the PDF. No additional step changes the hierarchy.

These are fixed configurations, not a learned WFP-specific correction or a recorded hyperparameter search. The tolerance variant is exploratory; “tuned” in its historical row name should not be read as a validated optimum.


**Output and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

The variants share one base conversion. Its recorded time includes first model load/download. The ordinary hierarchy pass has a separate timer; the tolerance pass was not separately timed. Their table times therefore do not represent three independent end-to-end conversions.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

These variants share detected blocks. A hierarchy stage cannot recover a heading absent from its inputs. The tolerance variant is exploratory.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) · [Project / GitHub](https://github.com/docling-project/docling) · [Docling technical report (2024)](https://arxiv.org/abs/2408.09869) · [Conversion and both hierarchy passes](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_docling.py) · [Pinned environment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/docling.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


## docling-hierarchy

**Docling built-in hierarchy**

Docling 2.151.1 detects headings, then HeadingHierarchyModel assigns levels using its default settings.


**Inference:** Read the text and page layout → Keep each item’s location → Assign levels in a second pass → Export headings and levels

- **Read the text and page layout:** Process the full PDF on the CPU with eight threads. Optical character recognition (OCR) and table reconstruction are disabled because these PDFs already contain selectable text.
- **Keep each item’s location:** Save parsed page information, including text positions, so the hierarchy step can inspect layout. The code option is generate_parsed_pages=True.
- **Assign levels in a second pass:** Run Docling’s HeadingHierarchyModel on the detected headings, using its default enabled options.
- **Export headings and levels:** Save each heading’s text, supplied H level, PDF page and bounding box—the rectangle around its text.



**Models and terms explained**

- [Docling](https://github.com/docling-project/docling): PDF conversion software used here to identify section headings and read or infer their levels.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Package | docling==2.151.1 |
| Device / parallelism | CPU; num_threads=8 |
| Conversion | do_ocr=False; do_table_structure=False; generate_parsed_pages=True |
| Hierarchy | HeadingHierarchyOptions(enabled=True); other hierarchy settings use library defaults |
| Model provenance | Package-managed layout models; the runner does not explicitly pin individual layout-model revisions. |

**What changed and how it was selected**

Use Docling 2.151.1 to find headings, then run its built-in HeadingHierarchyModel to assign their levels. This tests whether Docling’s extra hierarchy step improves the same detected headings.

These are fixed configurations, not a learned WFP-specific correction or a recorded hyperparameter search. The tolerance variant is exploratory; “tuned” in its historical row name should not be read as a validated optimum.


**Output and timing**

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

The variants share one base conversion. Its recorded time includes first model load/download. The ordinary hierarchy pass has a separate timer; the tolerance pass was not separately timed. Their table times therefore do not represent three independent end-to-end conversions.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

These variants share detected blocks. A hierarchy stage cannot recover a heading absent from its inputs. The tolerance variant is exploratory.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_docling.py) · [Project / GitHub](https://github.com/docling-project/docling) · [Docling technical report (2024)](https://arxiv.org/abs/2408.09869) · [Conversion and both hierarchy passes](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_docling.py) · [Pinned environment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/docling.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


## minicpm-ocr10

**MiniCPM-OCR 1.0 — MLX + CPU layout**

PP-DocLayoutV3 finds crops on CPU. MiniCPM-OCR 1.0 reads them through MLX; MiniCPM SDK 1.0.5 assembles Markdown.


**Inference:** Render the fixed WFP sample → Locate and crop document regions → Recognize each crop with MiniCPM-OCR 1.0 → Assemble the native Markdown outline

- **Render the fixed WFP sample:** Render all 32 audit pages at 200 DPI for MiniCPM-OCR 1.0. Supply pixels only: no native PDF text, tags, reference headings or earlier-page memory.
- **Locate and crop document regions:** Run PP-DocLayoutV3 on CPU with four Torch threads, detection threshold 0.3 and non-maximum suppression. MiniCPM SDK 1.0.5 provides the layout detector, ordered crops and block labels.
- **Recognize each crop with MiniCPM-OCR 1.0:** Load original BF16 weights in MLX on Metal. Use class-specific instructions: Text Recognition:, Table Recognition:, Formula Recognition:, Chart to Table:, Seal Recognition: Decode one region at a time, temperature 0; retain the raw response and region metadata.
- **Assemble the native Markdown outline:** MiniCPM SDK 1.0.5 assigns document titles H1. Its default numbered paragraph-title formatter makes “2” H2, “2.1” H3 and unnumbered section titles H2. Headers, footers and footnotes are excluded by the upstream assembly defaults. We retain this hierarchy even when it disagrees with the reference.



**Models and terms explained**

- [MiniCPM-OCR 1.0](https://huggingface.co/openbmb/MiniCPM-OCR-1.0): The upstream 1.3B-parameter visual recognition model, loaded from its pinned Hugging Face revision.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework; recognition uses Metal GPU kernels. Layout detection, where present, runs separately on CPU.
- [PP-DocLayoutV3](https://huggingface.co/PaddlePaddle/PP-DocLayoutV3_safetensors): A document-layout detector that labels regions such as titles, text, tables and figures. Its block labels and the Markdown assembler help determine the emitted hierarchy.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | openbmb/MiniCPM-OCR-1.0; revision 883ca368d17335b9ce5aa6fef4d000ef0684fcaa |
| Model size / weights | 1.3B parameters; original BF16 weights, no weight quantization or fine-tuning |
| Runtime | MLX 0.32.4; mlx-vlm 0.8.0; Transformers 5.23.0; Apple M4 Pro, 48 GB unified memory |
| Input | 32 fixed physical PDF pages; PyMuPDF render at 200 DPI; pixels only |
| Decoding | temperature=0; seed=42; enable_thinking=False |
| Concurrency | One model and one page at a time; region recognition sequential; Metal kernels internally parallel |
| Limits | Soft 600-second timeout per recognition request, checked between streamed chunks |
| Timing | Includes rendering, CPU layout when used, recognition and assembly; model loading recorded separately |
| Layout model | PaddlePaddle/PP-DocLayoutV3_safetensors; revision e4f489dc536556fc1be02b973ba06756e0d4a2ac |
| Layout settings | CPU; torch.set_num_threads(4); threshold=0.3; nms=True; chart and seal recognition enabled; image-block OCR disabled |
| SDK | minicpm-ocr==1.0.5; direct detector/crop/assemble_markdown components |
| Output budgets | Upstream class recipes: titles 512; body text 4096; tables 8192; display formulas 2048; charts 4096; seals 256 tokens |
| Hierarchy | SDK title_style=numbered; no offset correction or WFP-specific rules |

**What was trained, and by whom**

We use the published MiniCPM-OCR 1.0 weights at the pinned revision. We do not train, fine-tune or select checkpoints on these four WFP reports. The model card documents the upstream training; our contribution here is the Apple Silicon evaluation adapter.


**What this row establishes**

This is a portable MLX recognition and CPU layout adaptation. It is not the vendor’s CUDA deployment, and its speed cannot be compared directly with the NVIDIA field chart.

Broad OCR benchmark quality does not establish correct heading depth. This row scores the headings the pipeline actually emits, without document-specific corrections. Native prose retention measures overlapping five-word sequences from PDF paragraphs of at least 50 words; it does not measure table accuracy or reading order.

This is a portable MLX recognition and CPU layout adaptation. It is not the vendor’s CUDA deployment, and its speed cannot be compared directly with the NVIDIA field chart.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_field_candidate.py) · [Official model and model card](https://huggingface.co/openbmb/MiniCPM-OCR-1.0) · [Upstream implementation and documentation](https://github.com/OpenBMB/MiniCPM-OCR) · [Download pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/field-candidates.json) · [Protocol and reproduction commands](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/field-candidates.md) · [Measured predictions and page telemetry](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/field-candidates/minicpm_ocr10.json)


## paddleocr-vl16

**PaddleOCR-VL-1.6 — MLX + CPU layout**

PP-DocLayoutV3 finds crops on CPU. PaddleOCR-VL-1.6 reads them through MLX, but MiniCPM SDK assembles the Markdown in this adaptation.


**Inference:** Render the fixed WFP sample → Locate and crop document regions → Recognize each crop with PaddleOCR-VL-1.6 → Assemble the native Markdown outline

- **Render the fixed WFP sample:** Render all 32 audit pages at 200 DPI for PaddleOCR-VL-1.6. Supply pixels only: no native PDF text, tags, reference headings or earlier-page memory.
- **Locate and crop document regions:** Run PP-DocLayoutV3 on CPU with four Torch threads, detection threshold 0.3 and non-maximum suppression. MiniCPM SDK 1.0.5 provides the layout detector, ordered crops and block labels.
- **Recognize each crop with PaddleOCR-VL-1.6:** Load original BF16 weights in MLX on Metal. Use class-specific instructions: OCR:, Table Recognition:, Formula Recognition:, Chart Recognition:, Seal Recognition: Decode one region at a time, temperature 0; retain the raw response and region metadata.
- **Assemble the native Markdown outline:** MiniCPM SDK 1.0.5 assigns document titles H1. Its default numbered paragraph-title formatter makes “2” H2, “2.1” H3 and unnumbered section titles H2. Headers, footers and footnotes are excluded by the upstream assembly defaults. We retain this hierarchy even when it disagrees with the reference.



**Models and terms explained**

- [PaddleOCR-VL-1.6](https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6): The upstream 0.9B-parameter visual recognition model, loaded from its pinned Hugging Face revision.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework; recognition uses Metal GPU kernels. Layout detection, where present, runs separately on CPU.
- [PP-DocLayoutV3](https://huggingface.co/PaddlePaddle/PP-DocLayoutV3_safetensors): A document-layout detector that labels regions such as titles, text, tables and figures. Its block labels and the Markdown assembler help determine the emitted hierarchy.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | PaddlePaddle/PaddleOCR-VL-1.6; revision 132c45f52c0a26ed5a6b2f6bd8e3985794cc27dd |
| Model size / weights | 0.9B parameters; original BF16 weights, no weight quantization or fine-tuning |
| Runtime | MLX 0.32.4; mlx-vlm 0.8.0; Transformers 5.23.0; Apple M4 Pro, 48 GB unified memory |
| Input | 32 fixed physical PDF pages; PyMuPDF render at 200 DPI; pixels only |
| Decoding | temperature=0; seed=42; enable_thinking=False |
| Concurrency | One model and one page at a time; region recognition sequential; Metal kernels internally parallel |
| Limits | Soft 600-second timeout per recognition request, checked between streamed chunks |
| Timing | Includes rendering, CPU layout when used, recognition and assembly; model loading recorded separately |
| Layout model | PaddlePaddle/PP-DocLayoutV3_safetensors; revision e4f489dc536556fc1be02b973ba06756e0d4a2ac |
| Layout settings | CPU; torch.set_num_threads(4); threshold=0.3; nms=True; chart and seal recognition enabled; image-block OCR disabled |
| SDK | minicpm-ocr==1.0.5; direct detector/crop/assemble_markdown components |
| Output budgets | Upstream class recipes: titles 512; body text 4096; tables 8192; display formulas 2048; charts 4096; seals 256 tokens |
| Hierarchy | SDK title_style=numbered; no offset correction or WFP-specific rules |

**What was trained, and by whom**

We use the published PaddleOCR-VL-1.6 weights at the pinned revision. We do not train, fine-tune or select checkpoints on these four WFP reports. The model card documents the upstream training; our contribution here is the Apple Silicon evaluation adapter.


**What this row establishes**

This is a portable MLX recognition and CPU layout adaptation. It is not the vendor’s CUDA deployment, and its speed cannot be compared directly with the NVIDIA field chart.

Broad OCR benchmark quality does not establish correct heading depth. This row scores the headings the pipeline actually emits, without document-specific corrections. Native prose retention measures overlapping five-word sequences from PDF paragraphs of at least 50 words; it does not measure table accuracy or reading order.

This is a portable MLX recognition and CPU layout adaptation. It is not the vendor’s CUDA deployment, and its speed cannot be compared directly with the NVIDIA field chart.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_field_candidate.py) · [Official model and model card](https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6) · [Upstream implementation and documentation](https://github.com/PaddlePaddle/PaddleOCR) · [Download pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/field-candidates.json) · [Protocol and reproduction commands](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/field-candidates.md) · [Measured predictions and page telemetry](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/field-candidates/paddleocr_vl16.json) · [PaddleOCR-VL-1.6 paper](https://arxiv.org/abs/2606.03264)


## minicpm-ocr10-official-ollama

**MiniCPM-OCR 1.0 — official package, Ollama Q8 + DSpark**

MiniCPM-OCR 1.0.5 handles orientation, native PaddleX layout and Markdown assembly. Ollama runs the official Q8 model with DSpark speculative decoding on Metal.


**Inference:** Render the same 32 pages → Run the package’s page and layout processing → Recognize crops through official Ollama deployment → Keep the package’s heading formatter

- **Render the same 32 pages:** Render fixed physical pages at 200 DPI. Treat each PNG as a separate document with --split-images. The package receives pixels only; no reference labels, native PDF text or adjacent-page context.
- **Run the package’s page and layout processing:** minicpm-ocr 1.0.5 uses its orientation models and native PaddleX PP-DocLayoutV3 on CPU, threshold 0.3. It chooses the crops, their order and labels, and the per-class prompts. Chart and seal recognition stay enabled.
- **Recognize crops through official Ollama deployment:** Ollama 0.40.17 loads the official Q8_0 MiniCPM main model, F16 4× vision projector and matching Q8_0 DSpark draft. DSpark proposes token blocks and the main model verifies them. Logs show 25/25 main-model layers and 6/6 draft layers offloaded to the GPU, and accepted draft tokens.
- **Keep the package’s heading formatter:** Use the default numbered-title Markdown assembly without changes. Document-title blocks become H1. Paragraph titles are assigned markers using their number prefix; unnumbered paragraph titles become H2. We do not repair the resulting depths.



**Models and terms explained**

- [MiniCPM-OCR](https://github.com/OpenBMB/MiniCPM-OCR): OpenBMB’s document-recognition model and official parsing package. The package also performs layout detection and Markdown assembly.
- [DSpark](https://huggingface.co/openbmb/MiniCPM-OCR-1.0-DSpark): A smaller draft model proposes several tokens at once; the main model checks them. Accepted draft tokens can reduce the number of main-model decoding steps.
- [Ollama](https://github.com/ollama/ollama): The local model server used by this official deployment. This run executes its model layers on Metal.
- [Q8_0](https://huggingface.co/openbmb/MiniCPM-OCR-1.0-gguf): An 8-bit GGUF weight format. It is a quantized model file, so this row is distinct from the earlier BF16 configuration.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Package | minicpm-ocr==1.0.5; paddlepaddle==3.3.1; paddleocr==3.7.0; paddlex==3.7.2 |
| Main and vision files | MiniCPM-OCR-1_0-Q8_0.gguf and mmproj-model-f16-4x.gguf; openbmb/MiniCPM-OCR-1.0-gguf @0133ad8db635210441a55dcf421e25bfb9915142 |
| Draft file | dspark-MiniCPM-OCR-1_0-Q8_0.gguf; openbmb/MiniCPM-OCR-1.0-DSpark-gguf @cab493a5a26516a1c4c6e07c73b4470ff854a898 |
| Weight verification | The runner verifies that Ollama’s registered main, projector and draft blob hashes match the pinned official files. |
| Runtime | Ollama 0.40.17; llama.cpp engine on Apple M4 Pro Metal; 48 GB unified memory |
| Sampling | temperature=0; top_p=0.001; top_k=1; repeat_penalty=1; Ollama num_ctx=8192; draft_num_predict=15 |
| Concurrency | One model configuration and one recognition request at a time. SDK queue_mode=concurrent can group regions across pages; max_workers=1 and page_workers=1; layout/recognition overlap=False. |
| Layout and orientation | Native PP-DocLayoutV3, threshold=0.3, nms=True; SDK orientation models downloaded and warmed before the scored run |
| Output budgets | SDK class defaults: paragraph/doc titles 512; body text 4096; table 8192; display formula 2048; chart 4096; seal 256 |
| Timing | 465.87 seconds measured for 32 pages (14.56 seconds/page). Includes rendering and the complete CPU pipeline initialization. Ollama weights were loaded by the cover smoke test. |
| Result | Joint F0.5 22.2%; 16/77 correct title-level pairs; 3 extra predictions; heading metrics unchanged from the earlier BF16 MLX adaptation. |

**Which components were trained**

The main model, vision projector and DSpark draft are upstream published models. We did not train or fine-tune them. Q8_0 stores the main and draft weights in an 8-bit quantized format; the projector stays in F16. This differs from the earlier original-BF16 run.


**What this rerun establishes**

Running the full official package on its documented Mac deployment did not improve the heading-level counts. Its native formatter still disagrees with our reference hierarchy. This result describes the complete configuration and does not isolate the recognition weights from layout and assembly.

The package queues crops across the sample. Our measured time is for all 32 pages; the table’s per-page time is that total divided by 32, not a claim that each individual page completed in 14.56 seconds.

Official Ollama route with Q8 main/draft weights, not the BF16 NVIDIA deployment from the published field chart. The reference labels are not independently human-validated.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_official_minicpm.py) · [Official Ollama deployment instructions](https://github.com/OpenBMB/MiniCPM-OCR/blob/main/docs/ollama_deploy.md) · [Official main model and projector](https://huggingface.co/openbmb/MiniCPM-OCR-1.0-gguf) · [Official DSpark draft](https://huggingface.co/openbmb/MiniCPM-OCR-1.0-DSpark-gguf) · [Pinned files and hashes](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/official-pipelines.json) · [Measured evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/official-pipelines/minicpm_ocr10_official_ollama.json) · [Configuration source / evidence](https://huggingface.co/openbmb/MiniCPM-OCR-1.0)


## docling-ocr

**Docling — full-page RapidOCR + heading hierarchy**

Docling 2.151.1 reads every page image with RapidOCR, using PP-OCRv5 mobile detection and Latin-script recognition. Heron detects layout, then HeadingHierarchyModel assigns heading levels.


**Inference:** Recognize text across every page → Detect layout with Heron → Assign heading levels

- **Recognize text across every page:** RapidOCR 3.10.0 runs PP-OCRv5 mobile detection and Latin-script recognition at 216 dpi with ONNX Runtime on CPU. Full-page mode forces image-based reading even when PDF text exists.
- **Detect layout with Heron:** Docling groups the recognized text into document blocks. Table reconstruction is disabled; parsed page information is retained for hierarchy processing.
- **Assign heading levels:** Docling’s HeadingHierarchyModel runs with its default settings. We save each native section_header text, H level and PDF page without correcting them.



**Models and terms explained**

- [RapidOCR](https://github.com/RapidAI/RapidOCR): An OCR package that detects text in images and recognizes the characters.
- [Heron](https://huggingface.co/docling-project/docling-layout-heron): Docling’s layout model, which identifies regions such as text, headings and tables.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Packages | docling==2.151.1; docling-core==2.108.0; rapidocr==3.10.0; onnxruntime==1.32.0; torch==2.15.0; pymupdf==2.1 |
| OCR | mode=FULL_PAGE; lang=[latin]; backend=onnxruntime; scale=3.0 (216 dpi); model_size=small; text_score=0.5; detect_orientation=False |
| Recognition models | ch_PP-OCRv5_det_mobile.onnx; latin_PP-OCRv5_rec_mobile.onnx; ch_ppocr_mobile_v2.0_cls_mobile.onnx |
| Device | CPU; num_threads=8 |
| Conversion | do_ocr=True; do_table_structure=False; generate_parsed_pages=True |
| Hierarchy | HeadingHierarchyOptions(enabled=True); remaining settings use defaults |
| Scored output | Native SectionHeaderItem text, level and first provenance page |
| Timing | Full-PDF conversion plus hierarchy; initialization recorded separately |
| Observed time | 9 min 23 sec for 523 pages; 4.12 sec initialization excluded; 1.08 sec/page average |
| Model pins | Heron revision 8f39ad3c0b4c58e9c2d2c84a38465abf757272d8; OCR weight hashes in configs/docling-ocr-models.json |

**Training and selection**

No models were trained or tuned on WFP reports for this configuration. Latin-script recognition was selected to cover the English and Spanish documents. The earlier Docling configurations explicitly disabled OCR.


**Interpretation**

This tests forced full-page OCR on PDFs with selectable text. It does not measure performance on a scanned-document corpus, and it is not an exhaustive comparison of Docling’s OCR engines.


**Observed outputs**

The 69 audit predictions comprise 5 H1, 13 H2, 9 H3, 9 H4, 23 H5 and 10 H6 headings. Of 67 matched titles, 52 have the wrong level. Native prose retention is 86.6% on the audit pages. This is a text-retention measure, not a character-accuracy score.

15/77 heading-level pairs are correct, versus 16/77 for Docling without OCR. There are 52 incorrect levels, 10 missing headings and 2 extras. Forced OCR did not improve this selectable-text corpus.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_docling_ocr.py) · [Reproduction commands](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/docs/evidencelab-and-ocr.md) · [Importer and output checks](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/pipeline_evidence.py) · [Docling model catalog](https://docling-project.github.io/docling/usage/model_catalog/) · [RapidOCR](https://github.com/RapidAI/RapidOCR) · [Docling technical report](https://arxiv.org/abs/2408.09869) · [Environment pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/docling-ocr.txt) · [Saved evidence](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/pipeline-runs/docling_ocr.json) · [Configuration source / evidence](https://github.com/docling-project/docling)


## popo-docling

**Popo + Docling / experimental MLX 8-bit**

MinerU-Popo assigns levels to Docling candidates using overlapping eight-page image groups. This row is an experimental 8-bit MLX port.


**Inference:** Find possible titles with Docling → Arrange eight pages for the model → Ask MinerU-Popo for heading levels → Reconcile the repeated page

- **Find possible titles with Docling:** Collect section-header text and its page rectangle. Skip content inside picture and table blocks.
- **Arrange eight pages for the model:** Use the author’s adaptive_chunk routine and bordered image mosaics—several page images arranged together—with one page repeated between consecutive groups.
- **Ask MinerU-Popo for heading levels:** Run the “Title Level Analysis” prompt with title IDs, pages, boxes and text. Use 8-bit weights through MLX and max_tokens=8192.
- **Reconcile the repeated page:** Apply the author’s output-reading and overlap-alignment code to make levels agree across page groups. Map answers back to source title IDs; reject negative level labels.



**Models and terms explained**

- [MinerU-Popo](https://github.com/opendatalab/MinerU-Popo): A model and supporting code for assigning levels to document titles. This benchmark uses an experimental MLX adaptation.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.
- [4-bit / 8-bit weights](https://github.com/ml-explore/mlx-lm): Reduced-precision representations of a model’s learned numbers, used to lower memory requirements. The number describes storage precision, not heading depth or model accuracy.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | DreamEternal/MinerU-Popo; revision af75342abdc5 |
| Author code | opendatalab/MinerU-Popo revision 8b9a8bd57ef3 |
| Quantization | mlx_vlm.convert; affine 8-bit; group_size=64 |
| Chunking | adaptive_chunk(..., chunk_size=8); recorded one-page overlap; author concatenate_pdf_pages_with_border |
| Prompt | &lt;image&gt; then “Title Level Analysis: ” and candidate ID/page/box/content fields |
| Generation | temperature=0; max_tokens=8192; prefill_step_size=256; seed=42; thinking not explicitly overridden |

**Candidate and overlap processing**

The adapter reads Docling’s default body hierarchy, excludes picture/table subtrees, and converts boxes to normalized page coordinates with the proper origin. Author preprocessing functions prepare title candidates and visual chunks.

extract_label2 decodes the response. Overlap disagreements involving a negative label reject both copies; otherwise the rounded mean level difference supplies an offset for new positive labels. Repeated IDs retain existing assignments. Nonnegative output labels are accepted as emitted, including 0; negative or missing labels are demoted to text. No hidden +1 shift is applied.


**Tuning and measured scope**

No fine-tuning or parameter search; fixed conversion and inference settings. Only the title-level task was run, not summary generation or other Popo tasks.

All four complete PDFs (523 pages) were parsed. Scores use only the shared 32 audited pages / 77 reference headings; they are not full-document accuracy. Runs used an Apple M4 Pro with 48 GB memory.

The reported hierarchy-stage time excludes base Docling extraction and model loading. This MLX adapter is experimental and is not an end-to-end replication of the authors’ benchmark.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

This is our experimental Docling + MLX adapter, not the authors’ standard end-to-end deployment. No summary task was run.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_popo_mlx.py) · [Project / GitHub](https://github.com/opendatalab/MinerU-Popo) · [Model / Hugging Face](https://huggingface.co/DreamEternal/MinerU-Popo) · [MinerU-Popo paper](https://arxiv.org/abs/2605.24973) · [Mosaic prompt and overlap alignment](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_popo_mlx.py) · [Quantization and author-code preparation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/prepare_model.py) · [Model revision](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)


## mineru-pro-mlx

**MinerU2.5-Pro-2605-1.2B / direct MLX interface**

MinerU2.5-Pro-2605-1.2B uses two_step_extract through MLX. This interface returned title blocks without heading levels.


**Inference:** Render the 32 audit pages → Process one image at a time → Read layout, then content → Record the missing hierarchy

- **Render the 32 audit pages:** Render at 400 dots per inch and shrink to at most 2048 pixels on the longest side.
- **Process one image at a time:** Call MinerUClient.two_step_extract with mlx-engine, batch_size=1 and max_concurrency=1.
- **Read layout, then content:** The two steps locate page blocks and read their content. Convert the returned blocks with json2md and retain recognized title types.
- **Record the missing hierarchy:** Save detected title text and bounding boxes. With no supplied # heading levels, leave the level unknown; do not add another classifier.



**Models and terms explained**

- [MinerU2.5-Pro-2605-1.2B](https://huggingface.co/opendatalab/MinerU2.5-Pro-2605-1.2B): The 1.2-billion-parameter document image model tested through its direct two-step interface. It supplied title blocks but no levels in this run.
- [MLX](https://github.com/ml-explore/mlx): Apple’s machine-learning framework used here to run models locally on Apple Silicon. It is the execution software, not the heading model.

**Parameters used in this run**

| Parameter | Recorded value |
| --- | --- |
| Model | opendatalab/MinerU2.5-Pro-2605-1.2B; revision 08aaea840498 |
| Runtime | MLX bf16; mineru-vl-utils==2.0.9; backend="mlx-engine" |
| Parallelism | batch_size=1; max_concurrency=1; use_tqdm=False |
| Image / seed | 400 dpi → longest side ≤2048 pixels; MLX seed=42; image_analysis=False |
| Prompt / sampling | Internal two_step_extract library defaults; prompt, temperature and token ceiling are not explicitly overridden or individually recorded by this runner |

**What the score means**

The adapter checks the Markdown rendering of each title block for # through ######. When those markers are absent, level remains null. The historical result recovered 69 of 77 reference titles but no complete title-plus-level matches. Zero complete matches is not zero title detection.


**Tuning and measured scope**

No benchmark training and no additional title-leveling stage. This configuration should not be generalized to every MinerU deployment.

Only the 32 audited page images were processed. Scores use their 77 reference headings. Runs used local MLX on an Apple M4 Pro with 48 GB memory. A per-500-page time is an extrapolation, not a 500-page image run.

Timing surrounds two_step_extract and excludes model/client loading.

The main table matches titles on the same physical PDF page at normalized similarity ≥0.90, with one-to-one assignment, then checks exact H level. False headings are reported separately. This is different from the supervised group-and-level F1 used for model selection.

This direct interface did not supply heading levels. Title detection alone is not a complete heading-and-level output.

[Benchmark code](https://github.com/dividor/pdf-heading-benchmark/blob/main/scripts/runners/run_mineru_pro.py) · [Model / Hugging Face](https://huggingface.co/opendatalab/MinerU2.5-Pro-2605-1.2B) · [Project / GitHub](https://github.com/opendatalab/MinerU) · [Research paper linked by model card](https://arxiv.org/abs/2604.04771) · [Two-step interface and null-level handling](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/run_mineru_pro.py) · [Model revision](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/models.json) · [Library pins](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/configs/environments/mlx.txt) · [Main-table scoring implementation](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/src/pdf_heading_benchmark/evaluation.py)
