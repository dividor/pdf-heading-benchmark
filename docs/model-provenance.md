# Provenance of OUR METHOD’s three classifiers

These classifiers were **trained from scratch for this benchmark**, using assistant annotations of WFP reports. They are three separate scikit-learn Extra Trees classifiers, not downloaded pretrained language models. The later confidence-filter experiment reuses their fitted trees without training them again.

## Where the fitting ran

The original experiment is **structure-v2**, local run **run-001**. The experiment report records an **Apple M4 Pro with 48 GB RAM**; the machine-readable training record records **macOS 26.1 arm64, Python 3.12.3 and scikit-learn 1.9.1**. Fitting used CPU with `n_jobs=4`. There was no remote training service or GPU fine-tuning.

The saved deployment files are `join.json`, `context.json` and `relation.json` in the external `structure-v2/run-001` directory. Model files remain outside Git; the repository publishes their hashes, sizes, training counts and selection results. The original training record does not contain a run timestamp or the precise model version of the annotating assistant; these details must not be inferred from the archive snapshot date or Git commit date.

## Exactly what was trained

| File | Task | Training examples | Input features | Target classes | Trees | Recorded fit time |
| --- | --- | --- | --- | --- | --- | --- |
| `join.json` | Join adjacent lines | 6,267 labeled adjacent-line pairs | 100 | separate / join | 200 | 0.816 s |
| `context.json` | Classify a text group | 6,736 groups: 887 headings + 5,849 body examples | 47 | body / H1–H5 | 200 | 0.700 s |
| `relation.json` | Compare successive headings | 867 consecutive annotated heading pairs | 142 | shallower / same / deeper | 200 | 0.575 s |

All three used `ExtraTreesClassifier(n_estimators=200, max_depth=16, min_samples_leaf=2, max_features=0.8, class_weight="balanced", random_state=42, n_jobs=4)`. Other options used scikit-learn 1.9.1 defaults. No search over these tree parameters was performed. The recorded fit timers cover estimator fitting and setup, excluding feature preparation, JSON export and validation; they are not end-to-end training times.

The training script fitted **five** classifiers for three pipeline variants: `line`, `join`, `group`, `context` and `relation`. The selected `context_relations` pipeline deploys **three** of them: `join`, `context` and `relation` (600 trees total). The `line` and `group` models belong to the comparison variants. Viterbi decoding combines group and relationship scores; it is an inference algorithm, not a fourth trained model.

## Data and labels

The 20 training reports supplied **887 annotated heading groups and 7,039 labeled text lines**. An assistant reviewed source text, layout/page snippets and table-of-contents context, then recorded explicit line membership and H levels. The 112 fully reviewed training pages supplied ordinary-text negatives; added positive-only annotations did not turn unreviewed lines into negatives. Labels have not been independently adjudicated by a human. There is only one H5 training line and no H6 example.

Reports were selected from the supplied *Evaluation list – Phase 1.xlsx* catalogue and its `20261121T043910Z` archive snapshot. The manifest records the PDF hash, archive member, official public URL, split and reviewed pages. The original four league-table PDFs supplied no training labels. Splits are by report, not by publisher/template family.

| Split | Catalogue ID | Report / official PDF |
| --- | --- | --- |
| train | 347 | [Annual Synthesis of Operation Evaluations (2016-2017)](https://docs.wfp.org/api/documents/WFP-0000023485/download/) |
| train | 534 | [Synthesis of evidence and lessons from WFP's policy evaluations (2011 - 2019)](https://docs.wfp.org/api/documents/WFP-0000115570/download) |
| train | 584 | [Synthesis of evidence and lessons on country capacity strengthening from decentralized evaluations](https://docs.wfp.org/api/documents/WFP-0000127565/download/) |
| train | 425 | [Four Evaluations of the Impact of WFP Programmes on Nutrition in Humanitarian Contexts in the Sahel: A Synthesis](https://docs.wfp.org/api/documents/WFP-0000063326/download/) |
| train | 443 | [Evaluation Series on Emergency School Feeding in Lebanon 2015-2019](https://docs.wfp.org/api/documents/WFP-0000127163/download/) |
| train | 44 | [Evaluation of the Satellite Index Insurance for Pastoralists in Ethiopia (SIIPE) Programme: Impact Evaluation of the SIIPE Pilot (2017 – 2019)](https://docs.wfp.org/api/documents/WFP-0000107946/download/) |
| train | 104 | [Final Evaluation of USDA McGovern-Dole-funded International Food for Education and Child Nutrition Program’s Support in Liberia (2013-2016)](https://docs.wfp.org/api/documents/WFP-0000023073/download/) |
| train | 79 | [Evaluation of WFP’s General Food Assistance to Syrian Refugees in Jordan from 2015 to mid-2018](https://docs.wfp.org/api/documents/WFP-0000101797/download/) |
| train | 177 | [Emergency Social Safety Nets (ESSN) Mid-term Evaluation in Turkey](https://docs.wfp.org/api/documents/WFP-0000100401/download/) |
| train | 35 | [Evaluation of the Nutrition Components of the Algeria PRRO 200301](https://docs.wfp.org/api/documents/WFP-0000099834/download/) |
| train | 448 | [Evaluation of WFP’s support to smallholder farmers and expanded portfolio across the agriculture value chain in Bhutan, 2019-2021](https://docs.wfp.org/api/documents/WFP-0000139663/download/) |
| train | 857 | [Mid-term Evaluation of WFP’s Private Sector Partnerships and Fundraising Strategy 2020-2025](https://docs.wfp.org/api/documents/WFP-0000160228/download/) |
| train | 37 | [Evaluación final de la relevancia del rol y la respuesta del PMA para avanzar en un enfoque de asistencia alimentaria vinculado a los sistemas de protección social en Ecuador](https://docs.wfp.org/api/documents/WFP-0000073498/download/) |
| train | 494 | [Contribution des cantines scolaires aux résultats de l’éducation dans le sud de Madagascar (2015 à 2019) : Une analyse de la contribution](https://docs.wfp.org/api/documents/WFP-0000118909/download/) |
| train | 340 | [Djibouti IPSR 200824 : Une évaluation d’opération à mi-parcours du PAM](https://docs.wfp.org/api/documents/72403381cf214e11925fb73b5b1968b9/download/) |
| train | 324 | [The Impact of Humanitarian Aid on Food Insecure Populations During Conflict in Mali: An impact evaluation](https://www.3ieimpact.org/sites/default/files/GFR-TW6.1039-food-insecure-population-mali.pdf) |
| validation | 103 | [Evaluation of WFP Livelihoods and Resilience Activities in Lebanon from 2016 to 2019](https://docs.wfp.org/api/documents/WFP-0000128024/download/) |
| validation | 538 | [Evaluation of School Feeding Modalities Applied in Armenia](https://docs.wfp.org/api/documents/WFP-0000164067/download/) |
| validation | 176 | [Evaluation of WFP’s capacity strengthening activities  to develop the  School Meals Programme from 2016 to 2018 in Tunisia](https://docs.wfp.org/api/documents/WFP-0000108206/download/) |
| validation | 128 | [Evaluación Intermedia del Proyecto BOOST en las zonas de Nueva Segovia, Madriz, Estelí, Matagalpa,  Jinotega y la RACCN en Nicaragua, 2018-2021](https://docs.wfp.org/api/documents/WFP-0000138855/download/) |
| test | 321 | [WFP Malnutrition Interventions in Niger](https://www.3ieimpact.org/sites/default/files/2019-01/IE80-WFP-malnutrition-Niger.pdf) |
| test | 844 | [Impact evaluation of Anticipatory Action in Nepal](https://docs.wfp.org/api/documents/WFP-0000165767/download/?_ga=2.213186772.1572714128.1747122969-1660177980.1674680269) |
| test | 560 | [Evaluation of Chad WFP Country Strategic Plan 2019-2023](https://docs.wfp.org/api/documents/WFP-0000146206/download/) |
| test | 394 | [Ecuador: an Evaluation of WFP's Strategic Plan (2017-2021)](https://docs.wfp.org/api/documents/WFP-0000143384/download/) |
| train | 323 | [Targeting Moderate Acute Malnutrition in Humanitarian Situations in Chad](https://www.3ieimpact.org/sites/default/files/2019-01/IE78-MAM-Chad_1.pdf) |
| train | 33 | [Cote d'Ivoire PRRO 200464: a decentralized evaluation](https://docs.wfp.org/api/documents/WFP-0000063843/download/) |
| train | 15 | [Evaluación Final del Programa de País del Programa Mundial de Alimentos de las Naciones Unidas en el Estado Plurinacional de Bolivia – PP 200381 2013 - 2017](https://docs.wfp.org/api/documents/WFP-0000103099/download/) |
| train | 334 | [Evaluation of the WFP Corporate Partnership Strategy (2014-2017)](https://docs.wfp.org/api/documents/WFP-0000015489/download/) |

Validation reports **103, 538, 176 and 128** supplied 21 reference groups on 20 reviewed pages. The original three pipeline variants were compared using exact group-and-level F1: 55.3% for `expanded_line`, 63.6% for `learned_groups`, and 69.8% for `context_relations`. This selected the three-classifier design before evaluation on test reports **321, 844, 560 and 394** (38 groups on 32 pages). Those test documents have since been inspected and now provide regression evidence.

The later **structure-precision/run-002** experiment did not refit the trees. It searched 36 decision settings on the validation reports and selected a 0.70 heading-score cutoff, body multiplier 1 and relationship weight 1. Its historical selection constraint was at least 95% heading-only precision; that constraint is preserved in its protocol but no longer serves as a league-table quality gate.

## Checkable chain of evidence

- [Training program — constructs examples, fits models and selects the pipeline](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/scripts/structure/train.py)
- [Estimator implementation — exact tree parameters and JSON export verification](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/src/pdf_heading_benchmark/supervised_models.py)
- [Feature and training-pair construction](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/src/pdf_heading_benchmark/structure_features.py)
- [Original training run record — counts, versions, timings and model hashes](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/outputs/structure-v2/evidence/selection.json)
- [PDF manifest — all source reports, splits and PDF hashes](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/configs/structure-v2/corpus.json)
- [Materialized annotations — line membership and H levels](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/configs/structure-v2/annotations.json)
- [Annotation compilation and review decisions](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/scripts/structure/compile_annotations.py)
- [Original experiment report — hardware, coverage and reproduction](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/outputs/structure-v2/report.md)
- [Publication provenance — package versions and training source hashes](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/outputs/structure-v2/evidence/publication-provenance.json)
- [Later filter protocol — same model hashes, separate decision-setting search](https://github.com/dividor/pdf-heading-benchmark/blob/87e044a/outputs/structure-precision/evidence/protocol.json)

Evidence links above are pinned to commit `87e044a`. The following SHA-256 values agree between the original training record, the later filter protocol and the local saved files checked for this documentation update.

| Model file | SHA-256 | Bytes |
| --- | --- | --- |
| `join.json` | `dfaa15f128243fa17aea3c26b9c451279d71bce2f05f95f966fcba6da07a18ea` | 1,958,200 |
| `context.json` | `1666290d9e5b2e74a2c7be79efa998297dc784f4b17ec2a11ab4945f0d3c1c47` | 16,777,687 |
| `relation.json` | `82b359ffc0c64093f57b85b4c8fb28d0055ef331c37bbf281acf852e4a1b0196` | 5,589,536 |

## Reproduce fitting

From the repository checkout, using the source archive and a new output directory:

```bash
uv sync --locked --extra training
export STRUCTURE_DATA=/path/outside/the/repository/structure-v2
uv run python scripts/structure/prepare.py --data "$STRUCTURE_DATA" --archive /path/to/wfp-20261121T043910Z.tar
uv run python scripts/structure/train.py --data "$STRUCTURE_DATA" --output "$STRUCTURE_DATA/reproduction-001"
```

The training program rejects an existing output directory and reads only training and validation splits. JSON exports are checked against scikit-learn predictions. A rerun should record its own provenance: whole-file hashes include measured fitting time, so they are artifact identities, not a promise of byte-identical files from a new execution. Reproduction requires the source PDFs/archive, which are not bundled with the code.
