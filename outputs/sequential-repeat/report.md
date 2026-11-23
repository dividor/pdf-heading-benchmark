<span id="sequential-gpu-reruns"></span>

## Sequential GPU reruns

Seven selected MLX configurations were rerun one at a time on the same four PDFs, 32 audit pages and 77 reference headings. Every rerun reproduced the original heading titles, pages and levels exactly, with no parse errors, timeouts or token-limit truncations. The main table now uses these new timings, marked “Latest sequential run”; this comparison preserves the original measurements.

Chandra and the two LightOn runs took **14–31% less processing time**. Qwen results were mixed: visual-memory 27B improved **12.5%**, while single-image 27B took **4.7% longer**. Median system GPU utilization ranged from **92% to 100%**, with the Metal GPU independently verified inside each inference process. These observations confirm GPU execution; they do not establish optimal kernel efficiency or isolate the effect of background load.

<details>
<summary>How these reruns were measured: protocol, settings and hardware</summary>

**Execution and provenance:** each configuration ran in a fresh process and output directory, with only one benchmark model loaded at a time. The runner checked the default MLX device and Metal availability before model loading. It retained model/package versions, source and input hashes, raw page responses, process wall time, GPU activity and virtual-memory counters. The main timing column accepts only error-free, untruncated reruns with the same page scope and exactly matching heading predictions; the historical source evidence remains unchanged.

**Timing:** all rates below use seconds per page. Earlier and rerun processing rates use the original runners' measurement boundaries, excluding model loading and upstream candidate extraction. Whole-process rates include interpreter imports, model loading, image preparation, generation and output writes; they still exclude previously prepared candidate extraction and downloads. OCR batch time is divided by the number of pages, so it measures average throughput rather than single-page latency. Smaller values are faster. This is one repeat per configuration, not a statistical estimate of typical performance.

**Settings:** Qwen models retain their pinned MLX 4-bit weights, greedy decoding, seed 42, non-thinking prompts and 4,096-token limit. Single-image runs use a 1,280-pixel image; visual-memory runs use a 1,792-pixel current image plus up to six earlier 1,280-pixel images. Chandra retains batch four and a 12,384-token limit. LightOn 4B uses batch two throughout and a 12,384-token limit; its historical run mixed five single-page checkpoints (12,288-token limit) with batching, so that comparison includes a batching and token-limit change. LightOn 0.8B remains one image at a time with an 8,192-token limit. No headings or levels are repaired after generation.

**Hardware and limits:** this Mac has an Apple M4 Pro with a 20-core GPU and 48 GiB unified memory. GPU inference is active, but other applications still share memory and GPU resources. In the initial rerun, loading the sparse Qwen model increased total system swap usage from approximately 15 GB to 20 GB. The reruns therefore must not be described as measurements on an idle or memory-pressure-free machine. Swap-counter differences below show actual activity during each run, rather than treating existing swap allocation as proof of ongoing paging. PDF rendering, tokenization and JSON handling also use the CPU. [MLX's unified-memory and device documentation](https://ml-explore.github.io/mlx/build/html/usage/unified_memory.html) explains how CPU and GPU execution share memory; the recorded device selection and telemetry establish what happened in these runs.

[Sequential runner](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/runners/repeat_models.py) · [Importer and scorer](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/scripts/repeat_report.py) · [Rerun predictions versus reference](https://github.com/dividor/pdf-heading-benchmark/blob/codex/technique-explorer/outputs/sequential-repeat/report.md) · [Compact evidence](https://github.com/dividor/pdf-heading-benchmark/tree/codex/technique-explorer/outputs/sequential-repeat)

</details>


**Completed: 7/7 configurations.**

| Repeated configuration | Original time per page | Original time for 32 pages | Latest time per page | Latest time for 32 pages | Including startup, per page | Correct heading + level | Joint F0.5: earlier → rerun | Rerun extras | Errors | Timeouts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen3.6-35B-A3B 4-bit — single image | 9.8 sec | 5 min 13 sec | 10.7 sec | 5 min 42 sec | 11.6 sec | 53/77 → 53/77 | 68.8% → 68.8% | 0 | 0 | 0 |
| Qwen3.6-35B-A3B 4-bit — visual memory | 16.3 sec | 8 min 40 sec | 15.6 sec | 8 min 19 sec | 16.5 sec | 52/77 → 52/77 | 69.0% → 69.0% | 0 | 0 | 0 |
| Chandra OCR 2 / MLX | 32.3 sec | 17 min 12 sec | 27.7 sec | 14 min 46 sec | 28.2 sec | 53/77 → 53/77 | 72.6% → 72.6% | 2 | 0 | 0 |
| LightOnOCR-3-4B / MLX grounding | 44.1 sec | 23 min 33 sec | 33 sec | 17 min 36 sec | 33.5 sec | 46/77 → 46/77 | 57.9% → 57.9% | 8 | 0 | 0 |
| LightOnOCR-3-0.8B / MLX | 16.6 sec | 8 min 51 sec | 11.5 sec | 6 min 9 sec | 11.8 sec | 46/77 → 46/77 | 57.9% → 57.9% | 8 | 0 | 0 |
| Qwen3.6-27B 4-bit — single image | 1 min 4 sec | 33 min 58 sec | 1 min 7 sec | 35 min 33 sec | 1 min 7 sec | 60/77 → 60/77 | 77.1% → 77.1% | 1 | 0 | 0 |
| Qwen3.6-27B / MLX 4-bit / sampled visual memory | 1 min 56 sec | 1 hr 1 min 47 sec | 1 min 41 sec | 54 min 2 sec | 1 min 42 sec | 65/77 → 65/77 | 82.7% → 82.7% | 2 | 0 | 0 |

### GPU and memory observations

| Repeated configuration | Samples | Median GPU % | Maximum GPU % | Swap read GB | Swap written GB |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6-35B-A3B 4-bit — single image | 38 | 99.0 | 100 | 0.492 | 4.719 |
| Qwen3.6-35B-A3B 4-bit — visual memory | 53 | 99 | 100 | 0.098 | 0.029 |
| Chandra OCR 2 / MLX | 90 | 99.0 | 100 | 0.099 | 0.000 |
| LightOnOCR-3-4B / MLX grounding | 107 | 99 | 100 | 0.143 | 0.000 |
| LightOnOCR-3-0.8B / MLX | 38 | 92.0 | 100 | 0.201 | 0.000 |
| Qwen3.6-27B 4-bit — single image | 215 | 100 | 100 | 0.537 | 0.238 |
| Qwen3.6-27B / MLX 4-bit / sampled visual memory | 326 | 100.0 | 100 | 0.758 | 1.513 |

GPU and swap measurements are system-wide; they include other applications and model loading. A high GPU percentage confirms activity but does not prove optimal inference or identify a bottleneck.


### Qwen3.6-35B-A3B 4-bit — single image: rerun predictions versus reference

| Report | PDF page | Reference | Rerun prediction | Outcome |
| --- | --- | --- | --- | --- |
| targeting | 11 | H3 — Conclusion 2: WFP has a clear understanding of the strengths and weaknesses of various targeting and prioritization approaches and increasingly takes into account vulnerabilities in the way it targets and prioritizes. Selected approaches were found to be largely appropriate for their specific contexts but evidence related to the costs of various approaches is inconclusive. In addition, WFP’s targeting and prioritization practices were found to be insufficiently agile and cooperative. | H1 — Conclusion 2: WFP has a clear understanding of the strengths and weaknesses of various targeting and prioritization approaches and increasingly takes into account vulnerabilities in the way it targets and prioritizes. Selected approaches were found to be largely appropriate for their specific contexts but evidence related to the costs of various approaches is inconclusive. In addition, WFP’s targeting and prioritization practices were found to be insufficiently agile and cooperative. | Wrong or absent level |
| targeting | 11 | H4 — Appropriateness | H2 — Appropriateness | Wrong or absent level |
| targeting | 24 | H1 — 1 Introduction | H1 — 1 Introduction | Correct heading + level |
| targeting | 24 | H2 — 1.1 Evaluation features | H2 — 1.1 Evaluation features | Correct heading + level |
| targeting | 33 | H1 — 2 Evaluation findings | H1 — 2 Evaluation findings | Correct heading + level |
| targeting | 33 | H2 — 2.1 How relevant and appropriate are WFP’s approaches to targeting and prioritization? | H2 — 2.1 How relevant and appropriate are WFP’s approaches to targeting and prioritization? | Correct heading + level |
| targeting | 33 | H3 — 2.1.1 WFP’s normative framework and support structures for targeting and prioritization provide a broad and relevant operational foundation | H3 — 2.1.1 WFP’s normative framework and support structures for targeting and prioritization provide a broad and relevant operational foundation | Correct heading + level |
| targeting | 33 | H4 — 2.1.1.1 WFP’s normative framework on targeting and prioritization has clarified key aspects of the process | H4 — 2.1.1.1 WFP’s normative framework on targeting and prioritization has clarified key aspects of the process | Correct heading + level |
| targeting | 67 | H4 — 2.2.1.4 Good practices in reducing targeting errors are unevenly applied | H4 — 2.2.1.4 Good practices in reducing targeting errors are unevenly applied | Correct heading + level |
| targeting | 96 | H1 — 3 Conclusions and recommendations | H1 — 3 Conclusions and recommendations | Correct heading + level |
| targeting | 96 | H2 — 3.1 Conclusions | H2 — 3.1 Conclusions | Correct heading + level |
| targeting | 96 | H3 — Conclusion 1: WFP’s normative framework and support structures for targeting and prioritization have evolved considerably over the past years and largely serve their purpose well, although country offices are asking for clearer strategic guidance in an era of unprecedented budget cuts. | H3 — Conclusion 1: WFP’s normative framework and support structures for targeting and prioritization have evolved considerably over the past years and largely serve their purpose well, although country offices are asking for clearer strategic guidance in an era of unprecedented budget cuts. | Correct heading + level |
| targeting | 109 | H2 — Objectives and users of the evaluation | H1 — Objectives and users of the evaluation | Wrong or absent level |
| targeting | 109 | H2 — Evaluation questions | H1 — Evaluation questions | Wrong or absent level |
| targeting | 109 | H2 — Methodology and ethical considerations | H1 — Methodology and ethical considerations | Wrong or absent level |
| midterm | 8 | H1 — Executive summary | H1 — Executive summary | Correct heading + level |
| midterm | 8 | H2 — INTRODUCTION | H2 — INTRODUCTION | Correct heading + level |
| midterm | 8 | H3 — What was evaluated? | H3 — What was evaluated? | Correct heading + level |
| midterm | 8 | H3 — Why was the evaluation conducted and in which context? | H3 — Why was the evaluation conducted and in which context? | Correct heading + level |
| midterm | 10 | H2 — FINDINGS | H1 — FINDINGS | Wrong or absent level |
| midterm | 10 | H3 — Relevance and strategic focus of the design of the strategic plan | H2 — Relevance and strategic focus of the design of the strategic plan | Wrong or absent level |
| midterm | 26 | H1 — 1. Introduction | H1 — 1. Introduction | Correct heading + level |
| midterm | 26 | H2 — 1.1 EVALUATION FEATURES | H2 — 1.1 EVALUATION FEATURES | Correct heading + level |
| midterm | 27 | H2 — 1.2 CONTEXT | H2 — 1.2 CONTEXT | Correct heading + level |
| midterm | 27 | H3 — Global economic, climate, conflict and inequality trends | H3 — Global economic, climate, conflict and inequality trends | Correct heading + level |
| midterm | 36 | H1 — 2. Evaluation findings | H1 — 2. Evaluation findings | Correct heading + level |
| midterm | 36 | H2 — 2.1 STRENGTH AND RELEVANCE OF STRATEGIC PLAN DESIGN | H2 — 2.1 STRENGTH AND RELEVANCE OF STRATEGIC PLAN DESIGN | Correct heading + level |
| midterm | 36 | H3 — 2.1.1 Did the SP in its design clearly articulate its intended changes? | H3 — 2.1.1 Did the SP in its design clearly articulate its intended changes? | Correct heading + level |
| midterm | 61 | H3 — 2.2.3 How does the ambition of the SP compare to the evolving reality of funding? | H3 — 2.2.3 How does the ambition of the SP compare to the evolving reality of funding? | Correct heading + level |
| midterm | 87 | H1 — 3. Conclusions and recommendations | H1 — 3. Conclusions and recommendations | Correct heading + level |
| midterm | 87 | H2 — 2.3 3.1 CONCLUSIONS | H2 — 3.1 CONCLUSIONS | Correct heading + level |
| midterm | 98 | H1 — Annex III. Methodology | H1 — Annex III. Methodology | Correct heading + level |
| midterm | 98 | H2 — Overall approach | H2 — Overall approach | Correct heading + level |
| indonesia | 7 | H1 — Executive summary | H1 — Executive summary | Correct heading + level |
| indonesia | 7 | H2 — Introduction | H2 — Introduction | Correct heading + level |
| indonesia | 7 | H3 — Evaluation features | H2 — Evaluation features | Wrong or absent level |
| indonesia | 7 | H3 — Context | H2 — Context | Wrong or absent level |
| indonesia | 11 | H2 — Evaluation key insights and conclusions | H1 — Evaluation key insights and conclusions | Wrong or absent level |
| indonesia | 11 | H3 — Insight 1. CSP architecture | H2 — Insight 1. CSP architecture | Wrong or absent level |
| indonesia | 11 | H3 — Insight 2. Country capacity strengthening | H2 — Insight 2. Country capacity strengthening | Wrong or absent level |
| indonesia | 20 | H1 — Introduction | H2 — Introduction | Wrong or absent level |
| indonesia | 20 | H2 — 1.1. Evaluation features | H2 — 1.1. Evaluation features | Correct heading + level |
| indonesia | 20 | H2 — 1.2. Context | H2 — 1.2. Context | Correct heading + level |
| indonesia | 20 | H3 — Geography, Demography, and Government | H3 — Geography, Demography, and Government | Correct heading + level |
| indonesia | 20 | H3 — National policies and Sustainable Development Goals (SDG) | H3 — National policies and Sustainable Development Goals (SDG) | Correct heading + level |
| indonesia | 33 | H1 — Evaluation findings | H1 — Evaluation findings | Correct heading + level |
| indonesia | 33 | H2 — 2.1. EQ1: To what extent and in what ways is the CSP evidence-based and strategically focused to address the institutional capacity needs on food security, nutrition, and emergency preparedness of the Government of Indonesia? | H2 — 2.1. EQ1: To what extent and in what ways is the CSP evidence-based and strategically focused to address the institutional capacity needs on food security, nutrition, and emergency preparedness of the Government of Indonesia? | Correct heading + level |
| indonesia | 33 | H3 — EQ 1.1 To what extent was the design of the CSP informed by credible evidence (including by the evaluation of the previous CSP as relevant) and strategically and realistically targeted to address the food security, nutrition, and emergency preparedness institutional capacity needs of the Government? | H3 — EQ 1.1 To what extent was the design of the CSP informed by credible evidence (including by the evaluation of the previous CSP as relevant) and strategically and realistically targeted to address the food security, nutrition, and emergency preparedness institutional capacity needs of the Government? | Correct heading + level |
| indonesia | 33 | H3 — EQ 1.2 To what extent and in what ways was the CSP designed to support the UN cooperation framework and the SDGs? | H3 — EQ 1.2 To what extent and in what ways was the CSP designed to support the UN cooperation framework and the SDGs? | Correct heading + level |
| indonesia | 42 | H4 — EQ2.1a: CSP Output Achievements and Contributions to Outcomes | H2 — EQ2.1a: CSP Output Achievements and Contributions to Outcomes | Wrong or absent level |
| indonesia | 48 | H5 — SO1: Evidence and Data | H2 — SO1: Evidence and Data | Wrong or absent level |
| indonesia | 56 | H3 — EQ 2.3 To what extent are the enhanced food security, nutrition and emergency preparedness country capacities envisaged by the CSP likely to be sustainable, in particular from a financial, social, and institutional perspective? | H2 — EQ 2.3 To what extent are the enhanced food security, nutrition and emergency preparedness country capacities envisaged by the CSP likely to be sustainable, in particular from a financial, social, and institutional perspective? | Wrong or absent level |
| indonesia | 68 | H1 — Conclusions and recommendations | H1 — Conclusions and recommendations | Correct heading + level |
| indonesia | 68 | H2 — 3.1. Conclusions | H2 — 3.1. Conclusions | Correct heading + level |
| colombia | 7 | H1 — Resumen ejecutivo | H1 — Resumen ejecutivo | Correct heading + level |
| colombia | 7 | H2 — Introducción | H2 — Introducción | Correct heading + level |
| colombia | 7 | H3 — Características de la evaluación | H3 — Características de la evaluación | Correct heading + level |
| colombia | 7 | H3 — Contexto | H3 — Contexto | Correct heading + level |
| colombia | 13 | H2 — Hallazgos derivados de la evaluación | H1 — Hallazgos derivados de la evaluación | Wrong or absent level |
| colombia | 13 | H3 — ¿En qué medida el plan estratégico para el país se basa en datos empíricos y está orientado estratégicamente para atender las necesidades de los más vulnerables? | H2 — ¿En qué medida el plan estratégico para el país se basa en datos empíricos y está orientado estratégicamente para atender las necesidades de los más vulnerables? | Wrong or absent level |
| colombia | 13 | H4 — Pertinencia con respecto a las necesidades | H3 — Pertinencia con respecto a las necesidades | Wrong or absent level |
| colombia | 13 | H3 — ¿Cuáles son el alcance y la calidad de la contribución del PMA a los efectos estratégicos del plan estratégico para Colombia? | H2 — ¿Cuáles son el alcance y la calidad de la contribución del PMA a los efectos estratégicos del plan estratégico para Colombia? | Wrong or absent level |
| colombia | 28 | H1 — 1. Introducción | H1 — 1. Introducción | Correct heading + level |
| colombia | 28 | H2 — 1.1. CARACTERÍSTICAS DE LA EVALUACIÓN | H2 — 1.1. CARACTERÍSTICAS DE LA EVALUACIÓN | Correct heading + level |
| colombia | 28 | H2 — 1.2. CONTEXTO | H2 — 1.2. CONTEXTO | Correct heading + level |
| colombia | 28 | H3 — Contexto general | H3 — Contexto general | Correct heading + level |
| colombia | 42 | H1 — 2. Resultados de la evaluación | H1 — 2. Resultados de la evaluación | Correct heading + level |
| colombia | 42 | H2 — 2.1. PE 1: ¿EN QUÉ MEDIDA EL PEP ESTÁ BASADO EN EVIDENCIA Y ORIENTADO ESTRATÉGICAMENTE A SATISFACER LAS NECESIDADES DE LOS MÁS VULNERABLES? | H2 — 2.1. PE 1: ¿EN QUÉ MEDIDA EL PEP ESTÁ BASADO EN EVIDENCIA Y ORIENTADO ESTRATÉGICAMENTE A SATISFACER LAS NECESIDADES DE LOS MÁS VULNERABLES? | Correct heading + level |
| colombia | 42 | H3 — PE 1.1: ¿En qué medida el PEP se basó en los datos empíricos existentes sobre los desafíos relacionados con el hambre y los problemas de seguridad alimentaria y nutrición imperantes en el país, para asegurar así la pertinencia de su diseño a nivel territorial, tomando en cuenta la interculturalidad? | H3 — PE 1.1: ¿En qué medida el PEP se basó en los datos empíricos existentes sobre los desafíos relacionados con el hambre y los problemas de seguridad alimentaria y nutrición imperantes en el país, para asegurar así la pertinencia de su diseño a nivel territorial, tomando en cuenta la interculturalidad? | Correct heading + level |
| colombia | 56 | H4 — Dimensión 2: Entorno político | H3 — Dimensión 2: Entorno político | Wrong or absent level |
| colombia | 56 | H5 — Productos | H3 — Productos | Wrong or absent level |
| colombia | 56 | H5 — Resultados | H3 — Resultados92 | Wrong or absent level |
| colombia | 72 | H2 — 2.3. PE 3: ¿EN QUÉ MEDIDA EL PMA HA UTILIZADO SUS RECURSOS DE MANERA EFICIENTE PARA CONTRIBUIR A LOS PRODUCTOS Y EFECTOS ESTRATÉGICOS DEL PEP? | H2 — 2.3. PE 3: ¿EN QUÉ MEDIDA EL PMA HA UTILIZADO SUS RECURSOS DE MANERA EFICIENTE PARA CONTRIBUIR A LOS PRODUCTOS Y EFECTOS ESTRATÉGICOS DEL PEP? | Correct heading + level |
| colombia | 72 | H3 — PE 3.1 ¿En qué medida se entregaron los productos en el plazo previsto? | H3 — PE 3.1 ¿En qué medida se entregaron los productos en el plazo previsto? | Correct heading + level |
| colombia | 72 | H4 — Productos y logros | H3 — Productos y logros | Wrong or absent level |
| colombia | 93 | H1 — 3. Conclusiones y recomendaciones | H1 — 3. Conclusiones y recomendaciones | Correct heading + level |
| colombia | 93 | H2 — 3.1. CONCLUSIONES | H2 — 3.1. CONCLUSIONES | Correct heading + level |

### Qwen3.6-35B-A3B 4-bit — visual memory: rerun predictions versus reference

| Report | PDF page | Reference | Rerun prediction | Outcome |
| --- | --- | --- | --- | --- |
| targeting | 11 | H3 — Conclusion 2: WFP has a clear understanding of the strengths and weaknesses of various targeting and prioritization approaches and increasingly takes into account vulnerabilities in the way it targets and prioritizes. Selected approaches were found to be largely appropriate for their specific contexts but evidence related to the costs of various approaches is inconclusive. In addition, WFP’s targeting and prioritization practices were found to be insufficiently agile and cooperative. | H1 — Conclusion 2: WFP has a clear understanding of the strengths and weaknesses of various targeting and prioritization approaches and increasingly takes into account vulnerabilities in the way it targets and prioritizes. Selected approaches were found to be largely appropriate for their specific contexts but evidence related to the costs of various approaches is inconclusive. In addition, WFP’s targeting and prioritization practices were found to be insufficiently agile and cooperative. | Wrong or absent level |
| targeting | 11 | H4 — Appropriateness | H2 — Appropriateness | Wrong or absent level |
| targeting | 24 | H1 — 1 Introduction | H1 — 1 Introduction | Correct heading + level |
| targeting | 24 | H2 — 1.1 Evaluation features | H2 — 1.1 Evaluation features | Correct heading + level |
| targeting | 33 | H1 — 2 Evaluation findings | H1 — 2 Evaluation findings | Correct heading + level |
| targeting | 33 | H2 — 2.1 How relevant and appropriate are WFP’s approaches to targeting and prioritization? | H2 — 2.1 How relevant and appropriate are WFP’s approaches to targeting and prioritization? | Correct heading + level |
| targeting | 33 | H3 — 2.1.1 WFP’s normative framework and support structures for targeting and prioritization provide a broad and relevant operational foundation | H3 — 2.1.1 WFP’s normative framework and support structures for targeting and prioritization provide a broad and relevant operational foundation | Correct heading + level |
| targeting | 33 | H4 — 2.1.1.1 WFP’s normative framework on targeting and prioritization has clarified key aspects of the process | H4 — 2.1.1.1 WFP’s normative framework on targeting and prioritization has clarified key aspects of the process | Correct heading + level |
| targeting | 67 | H4 — 2.2.1.4 Good practices in reducing targeting errors are unevenly applied | H4 — 2.2.1.4 Good practices in reducing targeting errors are unevenly applied | Correct heading + level |
| targeting | 96 | H1 — 3 Conclusions and recommendations | H1 — 3 Conclusions and recommendations | Correct heading + level |
| targeting | 96 | H2 — 3.1 Conclusions | H2 — 3.1 Conclusions | Correct heading + level |
| targeting | 96 | H3 — Conclusion 1: WFP’s normative framework and support structures for targeting and prioritization have evolved considerably over the past years and largely serve their purpose well, although country offices are asking for clearer strategic guidance in an era of unprecedented budget cuts. | H3 — Conclusion 1: WFP’s normative framework and support structures for targeting and prioritization have evolved considerably over the past years and largely serve their purpose well, although country offices are asking for clearer strategic guidance in an era of unprecedented budget cuts. | Correct heading + level |
| targeting | 109 | H2 — Objectives and users of the evaluation | H2 — Objectives and users of the evaluation | Correct heading + level |
| targeting | 109 | H2 — Evaluation questions | H2 — Evaluation questions | Correct heading + level |
| targeting | 109 | H2 — Methodology and ethical considerations | H2 — Methodology and ethical considerations | Correct heading + level |
| midterm | 8 | H1 — Executive summary | H1 — Executive summary | Correct heading + level |
| midterm | 8 | H2 — INTRODUCTION | H2 — INTRODUCTION | Correct heading + level |
| midterm | 8 | H3 — What was evaluated? | H3 — What was evaluated? | Correct heading + level |
| midterm | 8 | H3 — Why was the evaluation conducted and in which context? | H3 — Why was the evaluation conducted and in which context? | Correct heading + level |
| midterm | 10 | H2 — FINDINGS | H1 — FINDINGS | Wrong or absent level |
| midterm | 10 | H3 — Relevance and strategic focus of the design of the strategic plan | H2 — Relevance and strategic focus of the design of the strategic plan | Wrong or absent level |
| midterm | 26 | H1 — 1. Introduction | H1 — 1. Introduction | Correct heading + level |
| midterm | 26 | H2 — 1.1 EVALUATION FEATURES | H2 — 1.1 EVALUATION FEATURES | Correct heading + level |
| midterm | 27 | H2 — 1.2 CONTEXT | H2 — 1.2 CONTEXT | Correct heading + level |
| midterm | 27 | H3 — Global economic, climate, conflict and inequality trends | H3 — Global economic, climate, conflict and inequality trends | Correct heading + level |
| midterm | 36 | H1 — 2. Evaluation findings | H1 — 2. Evaluation findings | Correct heading + level |
| midterm | 36 | H2 — 2.1 STRENGTH AND RELEVANCE OF STRATEGIC PLAN DESIGN | H2 — 2.1 STRENGTH AND RELEVANCE OF STRATEGIC PLAN DESIGN | Correct heading + level |
| midterm | 36 | H3 — 2.1.1 Did the SP in its design clearly articulate its intended changes? | H3 — 2.1.1 Did the SP in its design clearly articulate its intended changes? | Correct heading + level |
| midterm | 61 | H3 — 2.2.3 How does the ambition of the SP compare to the evolving reality of funding? | H3 — 2.2.3 How does the ambition of the SP compare to the evolving reality of funding? | Correct heading + level |
| midterm | 87 | H1 — 3. Conclusions and recommendations | H1 — 3. Conclusions and recommendations | Correct heading + level |
| midterm | 87 | H2 — 2.3 3.1 CONCLUSIONS | H2 — 3.1 CONCLUSIONS | Correct heading + level |
| midterm | 98 | H1 — Annex III. Methodology | H1 — Annex III. Methodology | Correct heading + level |
| midterm | 98 | H2 — Overall approach | H2 — Overall approach | Correct heading + level |
| indonesia | 7 | H1 — Executive summary | H1 — Executive summary | Correct heading + level |
| indonesia | 7 | H2 — Introduction | H2 — Introduction | Correct heading + level |
| indonesia | 7 | H3 — Evaluation features | H2 — Evaluation features | Wrong or absent level |
| indonesia | 7 | H3 — Context | H2 — Context | Wrong or absent level |
| indonesia | 11 | H2 — Evaluation key insights and conclusions | H1 — Evaluation key insights and conclusions | Wrong or absent level |
| indonesia | 11 | H3 — Insight 1. CSP architecture | H2 — Insight 1. CSP architecture | Wrong or absent level |
| indonesia | 11 | H3 — Insight 2. Country capacity strengthening | H2 — Insight 2. Country capacity strengthening | Wrong or absent level |
| indonesia | 20 | H1 — Introduction | H1 — Introduction | Correct heading + level |
| indonesia | 20 | H2 — 1.1. Evaluation features | H2 — 1.1. Evaluation features | Correct heading + level |
| indonesia | 20 | H2 — 1.2. Context | H2 — 1.2. Context | Correct heading + level |
| indonesia | 20 | H3 — Geography, Demography, and Government | H3 — Geography, Demography, and Government | Correct heading + level |
| indonesia | 20 | H3 — National policies and Sustainable Development Goals (SDG) | H3 — National policies and Sustainable Development Goals (SDG) | Correct heading + level |
| indonesia | 33 | H1 — Evaluation findings | H1 — Evaluation findings | Correct heading + level |
| indonesia | 33 | H2 — 2.1. EQ1: To what extent and in what ways is the CSP evidence-based and strategically focused to address the institutional capacity needs on food security, nutrition, and emergency preparedness of the Government of Indonesia? | H2 — 2.1. EQ1: To what extent and in what ways is the CSP evidence-based and strategically focused to address the institutional capacity needs on food security, nutrition, and emergency preparedness of the Government of Indonesia? | Correct heading + level |
| indonesia | 33 | H3 — EQ 1.1 To what extent was the design of the CSP informed by credible evidence (including by the evaluation of the previous CSP as relevant) and strategically and realistically targeted to address the food security, nutrition, and emergency preparedness institutional capacity needs of the Government? | — | Missed heading |
| indonesia | 33 | H3 — EQ 1.2 To what extent and in what ways was the CSP designed to support the UN cooperation framework and the SDGs? | — | Missed heading |
| indonesia | 42 | H4 — EQ2.1a: CSP Output Achievements and Contributions to Outcomes | H2 — EQ2.1a: CSP Output Achievements and Contributions to Outcomes | Wrong or absent level |
| indonesia | 48 | H5 — SO1: Evidence and Data | H2 — SO1: Evidence and Data | Wrong or absent level |
| indonesia | 56 | H3 — EQ 2.3 To what extent are the enhanced food security, nutrition and emergency preparedness country capacities envisaged by the CSP likely to be sustainable, in particular from a financial, social, and institutional perspective? | H2 — EQ 2.3 To what extent are the enhanced food security, nutrition and emergency preparedness country capacities envisaged by the CSP likely to be sustainable, in particular from a financial, social, and institutional perspective? | Wrong or absent level |
| indonesia | 68 | H1 — Conclusions and recommendations | H1 — Conclusions and recommendations | Correct heading + level |
| indonesia | 68 | H2 — 3.1. Conclusions | H2 — 3.1. Conclusions | Correct heading + level |
| colombia | 7 | H1 — Resumen ejecutivo | H1 — Resumen ejecutivo | Correct heading + level |
| colombia | 7 | H2 — Introducción | H1 — Introducción | Wrong or absent level |
| colombia | 7 | H3 — Características de la evaluación | H2 — Características de la evaluación | Wrong or absent level |
| colombia | 7 | H3 — Contexto | H2 — Contexto | Wrong or absent level |
| colombia | 13 | H2 — Hallazgos derivados de la evaluación | H1 — Hallazgos derivados de la evaluación | Wrong or absent level |
| colombia | 13 | H3 — ¿En qué medida el plan estratégico para el país se basa en datos empíricos y está orientado estratégicamente para atender las necesidades de los más vulnerables? | H2 — ¿En qué medida el plan estratégico para el país se basa en datos empíricos y está orientado estratégicamente para atender las necesidades de los más vulnerables? | Wrong or absent level |
| colombia | 13 | H4 — Pertinencia con respecto a las necesidades | H3 — Pertinencia con respecto a las necesidades | Wrong or absent level |
| colombia | 13 | H3 — ¿Cuáles son el alcance y la calidad de la contribución del PMA a los efectos estratégicos del plan estratégico para Colombia? | H2 — ¿Cuáles son el alcance y la calidad de la contribución del PMA a los efectos estratégicos del plan estratégico para Colombia? | Wrong or absent level |
| colombia | 28 | H1 — 1. Introducción | H1 — 1. Introducción | Correct heading + level |
| colombia | 28 | H2 — 1.1. CARACTERÍSTICAS DE LA EVALUACIÓN | H2 — 1.1. CARACTERÍSTICAS DE LA EVALUACIÓN | Correct heading + level |
| colombia | 28 | H2 — 1.2. CONTEXTO | H2 — 1.2. CONTEXTO | Correct heading + level |
| colombia | 28 | H3 — Contexto general | H3 — Contexto general | Correct heading + level |
| colombia | 42 | H1 — 2. Resultados de la evaluación | H1 — 2. Resultados de la evaluación | Correct heading + level |
| colombia | 42 | H2 — 2.1. PE 1: ¿EN QUÉ MEDIDA EL PEP ESTÁ BASADO EN EVIDENCIA Y ORIENTADO ESTRATÉGICAMENTE A SATISFACER LAS NECESIDADES DE LOS MÁS VULNERABLES? | H2 — 2.1. PE 1: ¿EN QUÉ MEDIDA EL PEP ESTÁ BASADO EN EVIDENCIA Y ORIENTADO ESTRATÉGICAMENTE A SATISFACER LAS NECESIDADES DE LOS MÁS VULNERABLES? | Correct heading + level |
| colombia | 42 | H3 — PE 1.1: ¿En qué medida el PEP se basó en los datos empíricos existentes sobre los desafíos relacionados con el hambre y los problemas de seguridad alimentaria y nutrición imperantes en el país, para asegurar así la pertinencia de su diseño a nivel territorial, tomando en cuenta la interculturalidad? | H3 — PE 1.1: ¿En qué medida el PEP se basó en los datos empíricos existentes sobre los desafíos relacionados con el hambre y los problemas de seguridad alimentaria y nutrición imperantes en el país, para asegurar así la pertinencia de su diseño a nivel territorial, tomando en cuenta la interculturalidad? | Correct heading + level |
| colombia | 56 | H4 — Dimensión 2: Entorno político | H3 — Dimensión 2: Entorno político | Wrong or absent level |
| colombia | 56 | H5 — Productos | H3 — Productos | Wrong or absent level |
| colombia | 56 | H5 — Resultados | H3 — Resultados | Wrong or absent level |
| colombia | 72 | H2 — 2.3. PE 3: ¿EN QUÉ MEDIDA EL PMA HA UTILIZADO SUS RECURSOS DE MANERA EFICIENTE PARA CONTRIBUIR A LOS PRODUCTOS Y EFECTOS ESTRATÉGICOS DEL PEP? | H2 — 2.3. PE 3: ¿EN QUÉ MEDIDA EL PMA HA UTILIZADO SUS RECURSOS DE MANERA EFICIENTE PARA CONTRIBUIR A LOS PRODUCTOS Y EFECTOS ESTRATÉGICOS DEL PEP? | Correct heading + level |
| colombia | 72 | H3 — PE 3.1 ¿En qué medida se entregaron los productos en el plazo previsto? | H3 — PE 3.1 ¿En qué medida se entregaron los productos en el plazo previsto? | Correct heading + level |
| colombia | 72 | H4 — Productos y logros | H3 — Productos y logros | Wrong or absent level |
| colombia | 93 | H1 — 3. Conclusiones y recomendaciones | H1 — 3. Conclusiones y recomendaciones | Correct heading + level |
| colombia | 93 | H2 — 3.1. CONCLUSIONES | H2 — 3.1. CONCLUSIONES | Correct heading + level |

### Chandra OCR 2 / MLX: rerun predictions versus reference

| Report | PDF page | Reference | Rerun prediction | Outcome |
| --- | --- | --- | --- | --- |
| targeting | 11 | H4 — Appropriateness | H3 — Appropriateness | Wrong or absent level |
| targeting | 11 | H3 — Conclusion 2: WFP has a clear understanding of the strengths and weaknesses of various targeting and prioritization approaches and increasingly takes into account vulnerabilities in the way it targets and prioritizes. Selected approaches were found to be largely appropriate for their specific contexts but evidence related to the costs of various approaches is inconclusive. In addition, WFP’s targeting and prioritization practices were found to be insufficiently agile and cooperative. | — | Missed heading |
| targeting | 24 | H1 — 1 Introduction | H1 — 1 Introduction | Correct heading + level |
| targeting | 24 | H2 — 1.1 Evaluation features | H2 — 1.1 Evaluation features | Correct heading + level |
| targeting | 33 | H1 — 2 Evaluation findings | H2 — 2 Evaluation findings | Wrong or absent level |
| targeting | 33 | H2 — 2.1 How relevant and appropriate are WFP’s approaches to targeting and prioritization? | H3 — 2.1 How relevant and appropriate are WFP's approaches to targeting and prioritization? | Wrong or absent level |
| targeting | 33 | H3 — 2.1.1 WFP’s normative framework and support structures for targeting and prioritization provide a broad and relevant operational foundation | H4 — 2.1.1 WFP's normative framework and support structures for targeting and prioritization provide a broad and relevant operational foundation | Wrong or absent level |
| targeting | 33 | H4 — 2.1.1.1 WFP’s normative framework on targeting and prioritization has clarified key aspects of the process | H5 — 2.1.1.1 WFP's normative framework on targeting and prioritization has clarified key aspects of the process | Wrong or absent level |
| targeting | 67 | H4 — 2.2.1.4 Good practices in reducing targeting errors are unevenly applied | H4 — 2.2.1.4 Good practices in reducing targeting errors are unevenly applied | Correct heading + level |
| targeting | 96 | H1 — 3 Conclusions and recommendations | H1 — 3 Conclusions and recommendations | Correct heading + level |
| targeting | 96 | H2 — 3.1 Conclusions | H2 — 3.1 Conclusions | Correct heading + level |
| targeting | 96 | H3 — Conclusion 1: WFP’s normative framework and support structures for targeting and prioritization have evolved considerably over the past years and largely serve their purpose well, although country offices are asking for clearer strategic guidance in an era of unprecedented budget cuts. | — | Missed heading |
| targeting | 109 | H2 — Objectives and users of the evaluation | H2 — Objectives and users of the evaluation | Correct heading + level |
| targeting | 109 | H2 — Evaluation questions | H2 — Evaluation questions | Correct heading + level |
| targeting | 109 | H2 — Methodology and ethical considerations | H2 — Methodology and ethical considerations | Correct heading + level |
| midterm | 8 | H1 — Executive summary | H1 — Executive summary | Correct heading + level |
| midterm | 8 | H2 — INTRODUCTION | H2 — INTRODUCTION | Correct heading + level |
| midterm | 8 | H3 — What was evaluated? | H3 — What was evaluated? | Correct heading + level |
| midterm | 8 | H3 — Why was the evaluation conducted and in which context? | H3 — Why was the evaluation conducted and in which context? | Correct heading + level |
| midterm | 10 | H2 — FINDINGS | H2 — FINDINGS | Correct heading + level |
| midterm | 10 | H3 — Relevance and strategic focus of the design of the strategic plan | H3 — Relevance and strategic focus of the design of the strategic plan | Correct heading + level |
| midterm | 26 | H1 — 1. Introduction | H1 — 1. Introduction | Correct heading + level |
| midterm | 26 | H2 — 1.1 EVALUATION FEATURES | H2 — 1.1 EVALUATION FEATURES | Correct heading + level |
| midterm | 27 | H2 — 1.2 CONTEXT | H2 — 1.2 CONTEXT | Correct heading + level |
| midterm | 27 | H3 — Global economic, climate, conflict and inequality trends | H3 — Global economic, climate, conflict and inequality trends | Correct heading + level |
| midterm | 36 | H1 — 2. Evaluation findings | H2 — 2. Evaluation findings | Wrong or absent level |
| midterm | 36 | H2 — 2.1 STRENGTH AND RELEVANCE OF STRATEGIC PLAN DESIGN | H3 — 2.1 STRENGTH AND RELEVANCE OF STRATEGIC PLAN DESIGN | Wrong or absent level |
| midterm | 36 | H3 — 2.1.1 Did the SP in its design clearly articulate its intended changes? | H4 — 2.1.1 Did the SP in its design clearly articulate its intended changes? | Wrong or absent level |
| midterm | 61 | H3 — 2.2.3 How does the ambition of the SP compare to the evolving reality of funding? | H3 — 2.2.3 How does the ambition of the SP compare to the evolving reality of funding? | Correct heading + level |
| midterm | 87 | H1 — 3. Conclusions and recommendations | H1 — 3. Conclusions and recommendations | Correct heading + level |
| midterm | 87 | H2 — 2.3 3.1 CONCLUSIONS | H2 — 2.3 3.1 CONCLUSIONS | Correct heading + level |
| midterm | 98 | H1 — Annex III. Methodology | H1 — Annex III. Methodology | Correct heading + level |
| midterm | 98 | H2 — Overall approach | H2 — Overall approach | Correct heading + level |
| indonesia | 7 | H1 — Executive summary | H1 — Executive summary | Correct heading + level |
| indonesia | 7 | H2 — Introduction | H2 — Introduction | Correct heading + level |
| indonesia | 7 | H3 — Evaluation features | H3 — Evaluation features | Correct heading + level |
| indonesia | 7 | H3 — Context | H3 — Context | Correct heading + level |
| indonesia | 11 | H2 — Evaluation key insights and conclusions | H2 — Evaluation key insights and conclusions | Correct heading + level |
| indonesia | 11 | H3 — Insight 1. CSP architecture | H3 — Insight 1. CSP architecture | Correct heading + level |
| indonesia | 11 | H3 — Insight 2. Country capacity strengthening | H3 — Insight 2. Country capacity strengthening | Correct heading + level |
| indonesia | 20 | H1 — Introduction | H1 — Introduction | Correct heading + level |
| indonesia | 20 | H2 — 1.1. Evaluation features | H2 — 1.1. Evaluation features | Correct heading + level |
| indonesia | 20 | H2 — 1.2. Context | H2 — 1.2. Context | Correct heading + level |
| indonesia | 20 | H3 — Geography, Demography, and Government | H3 — Geography, Demography, and Government | Correct heading + level |
| indonesia | 20 | H3 — National policies and Sustainable Development Goals (SDG) | H3 — National policies and Sustainable Development Goals (SDG) | Correct heading + level |
| indonesia | 33 | H1 — Evaluation findings | H1 — Evaluation findings | Correct heading + level |
| indonesia | 33 | H2 — 2.1. EQ1: To what extent and in what ways is the CSP evidence-based and strategically focused to address the institutional capacity needs on food security, nutrition, and emergency preparedness of the Government of Indonesia? | H2 — 2.1. EQ1: To what extent and in what ways is the CSP evidence-based and strategically focused to address the institutional capacity needs on food security, nutrition, and emergency preparedness of the Government of Indonesia? | Correct heading + level |
| indonesia | 33 | H3 — EQ 1.1 To what extent was the design of the CSP informed by credible evidence (including by the evaluation of the previous CSP as relevant) and strategically and realistically targeted to address the food security, nutrition, and emergency preparedness institutional capacity needs of the Government? | — | Missed heading |
| indonesia | 33 | H3 — EQ 1.2 To what extent and in what ways was the CSP designed to support the UN cooperation framework and the SDGs? | — | Missed heading |
| indonesia | 42 | H4 — EQ2.1a: CSP Output Achievements and Contributions to Outcomes | H3 — EQ2.1a: CSP Output Achievements and Contributions to Outcomes | Wrong or absent level |
| indonesia | 48 | H5 — SO1: Evidence and Data | H3 — SO1: Evidence and Data | Wrong or absent level |
| indonesia | 56 | H3 — EQ 2.3 To what extent are the enhanced food security, nutrition and emergency preparedness country capacities envisaged by the CSP likely to be sustainable, in particular from a financial, social, and institutional perspective? | Level not supplied — EQ 2.3 To what extent are the enhanced food security, nutrition and emergency preparedness country capacities envisaged by the CSP likely to be sustainable, in particular from a financial, social, and institutional perspective? | Wrong or absent level |
| indonesia | 68 | H1 — Conclusions and recommendations | H1 — Conclusions and recommendations | Correct heading + level |
| indonesia | 68 | H2 — 3.1. Conclusions | H2 — 3.1. Conclusions | Correct heading + level |
| colombia | 7 | H1 — Resumen ejecutivo | H1 — Resumen ejecutivo | Correct heading + level |
| colombia | 7 | H2 — Introducción | H2 — Introducción | Correct heading + level |
| colombia | 7 | H3 — Características de la evaluación | H3 — Características de la evaluación | Correct heading + level |
| colombia | 7 | H3 — Contexto | H3 — Contexto | Correct heading + level |
| colombia | 13 | H2 — Hallazgos derivados de la evaluación | H2 — Hallazgos derivados de la evaluación | Correct heading + level |
| colombia | 13 | H4 — Pertinencia con respecto a las necesidades | H3 — Pertinencia con respecto a las necesidades | Wrong or absent level |
| colombia | 13 | H3 — ¿En qué medida el plan estratégico para el país se basa en datos empíricos y está orientado estratégicamente para atender las necesidades de los más vulnerables? | — | Missed heading |
| colombia | 13 | H3 — ¿Cuáles son el alcance y la calidad de la contribución del PMA a los efectos estratégicos del plan estratégico para Colombia? | — | Missed heading |
| colombia | 28 | H1 — 1. Introducción | H1 — 1. Introducción | Correct heading + level |
| colombia | 28 | H2 — 1.1. CARACTERÍSTICAS DE LA EVALUACIÓN | H2 — 1.1. CARACTERÍSTICAS DE LA EVALUACIÓN | Correct heading + level |
| colombia | 28 | H2 — 1.2. CONTEXTO | H2 — 1.2. CONTEXTO | Correct heading + level |
| colombia | 28 | H3 — Contexto general | H3 — Contexto general | Correct heading + level |
| colombia | 42 | H1 — 2. Resultados de la evaluación | H2 — 2. Resultados de la evaluación | Wrong or absent level |
| colombia | 42 | H2 — 2.1. PE 1: ¿EN QUÉ MEDIDA EL PEP ESTÁ BASADO EN EVIDENCIA Y ORIENTADO ESTRATÉGICAMENTE A SATISFACER LAS NECESIDADES DE LOS MÁS VULNERABLES? | H3 — 2.1. PE 1: ¿EN QUÉ MEDIDA EL PEP ESTÁ BASADO EN EVIDENCIA Y ORIENTADO ESTRATÉGICAMENTE A SATISFACER LAS NECESIDADES DE LOS MÁS VULNERABLES? | Wrong or absent level |
| colombia | 42 | H3 — PE 1.1: ¿En qué medida el PEP se basó en los datos empíricos existentes sobre los desafíos relacionados con el hambre y los problemas de seguridad alimentaria y nutrición imperantes en el país, para asegurar así la pertinencia de su diseño a nivel territorial, tomando en cuenta la interculturalidad? | — | Missed heading |
| colombia | 42 | — | H4 — Resumen | Extra prediction |
| colombia | 56 | H4 — Dimensión 2: Entorno político | H2 — Dimensión 2: Entorno político | Wrong or absent level |
| colombia | 56 | H5 — Productos | H3 — Productos | Wrong or absent level |
| colombia | 56 | H5 — Resultados | H3 — Resultados 92 | Wrong or absent level |
| colombia | 72 | H2 — 2.3. PE 3: ¿EN QUÉ MEDIDA EL PMA HA UTILIZADO SUS RECURSOS DE MANERA EFICIENTE PARA CONTRIBUIR A LOS PRODUCTOS Y EFECTOS ESTRATÉGICOS DEL PEP? | H2 — 2.3. PE 3: ¿EN QUÉ MEDIDA EL PMA HA UTILIZADO SUS RECURSOS DE MANERA EFICIENTE PARA CONTRIBUIR A LOS PRODUCTOS Y EFECTOS ESTRATÉGICOS DEL PEP? | Correct heading + level |
| colombia | 72 | H3 — PE 3.1 ¿En qué medida se entregaron los productos en el plazo previsto? | H3 — PE 3.1 ¿En qué medida se entregaron los productos en el plazo previsto? | Correct heading + level |
| colombia | 72 | H4 — Productos y logros | H4 — Productos y logros | Correct heading + level |
| colombia | 72 | — | H4 — Resumen | Extra prediction |
| colombia | 93 | H1 — 3. Conclusiones y recomendaciones | H1 — 3. Conclusiones y recomendaciones | Correct heading + level |
| colombia | 93 | H2 — 3.1. CONCLUSIONES | H2 — 3.1. CONCLUSIONES | Correct heading + level |

### LightOnOCR-3-4B / MLX grounding: rerun predictions versus reference

| Report | PDF page | Reference | Rerun prediction | Outcome |
| --- | --- | --- | --- | --- |
| targeting | 7 | — | H1 — Figure 1: Global humanitarian requirements and resources (2019-2025) | Extra prediction |
| targeting | 11 | H4 — Appropriateness | Level not supplied — Appropriateness | Wrong or absent level |
| targeting | 11 | H3 — Conclusion 2: WFP has a clear understanding of the strengths and weaknesses of various targeting and prioritization approaches and increasingly takes into account vulnerabilities in the way it targets and prioritizes. Selected approaches were found to be largely appropriate for their specific contexts but evidence related to the costs of various approaches is inconclusive. In addition, WFP’s targeting and prioritization practices were found to be insufficiently agile and cooperative. | — | Missed heading |
| targeting | 24 | H1 — 1 Introduction | H1 — 1 Introduction | Correct heading + level |
| targeting | 24 | H2 — 1.1 Evaluation features | H2 — 1.1 Evaluation features | Correct heading + level |
| targeting | 27 | — | H1 — Figure 2. Resources required and allocated contributions, 2018–2025 | Extra prediction |
| targeting | 33 | H1 — 2 Evaluation findings | H1 — 2 Evaluation findings | Correct heading + level |
| targeting | 33 | H2 — 2.1 How relevant and appropriate are WFP’s approaches to targeting and prioritization? | H2 — EQ1 2.1 How relevant and appropriate are WFP’s approaches to targeting and prioritization? | Correct heading + level |
| targeting | 33 | H3 — 2.1.1 WFP’s normative framework and support structures for targeting and prioritization provide a broad and relevant operational foundation | H2 — EQ4.1 2.1.1 WFP’s normative framework and support structures for targeting and prioritization provide a broad and relevant operational foundation | Wrong or absent level |
| targeting | 33 | H4 — 2.1.1.1 WFP’s normative framework on targeting and prioritization has clarified key aspects of the process | H3 — 2.1.1.1 WFP’s normative framework on targeting and prioritization has clarified key aspects of the process | Wrong or absent level |
| targeting | 67 | H4 — 2.2.1.4 Good practices in reducing targeting errors are unevenly applied | Level not supplied — 2.2.1.4 Good practices in reducing targeting errors are unevenly applied | Wrong or absent level |
| targeting | 67 | — | Level not supplied — EQ2.1 EQ3.1 EQ4.3 | Extra prediction |
| targeting | 96 | H1 — 3 Conclusions and recommendations | H1 — 3 Conclusions and recommendations | Correct heading + level |
| targeting | 96 | H2 — 3.1 Conclusions | H2 — 3.1 Conclusions | Correct heading + level |
| targeting | 96 | H3 — Conclusion 1: WFP’s normative framework and support structures for targeting and prioritization have evolved considerably over the past years and largely serve their purpose well, although country offices are asking for clearer strategic guidance in an era of unprecedented budget cuts. | — | Missed heading |
| targeting | 109 | H2 — Objectives and users of the evaluation | H2 — Objectives and users of the evaluation | Correct heading + level |
| targeting | 109 | H2 — Evaluation questions | H2 — Evaluation questions | Correct heading + level |
| targeting | 109 | H2 — Methodology and ethical considerations | H2 — Methodology and ethical considerations | Correct heading + level |
| midterm | 8 | H1 — Executive summary | H1 — Executive summary | Correct heading + level |
| midterm | 8 | H2 — INTRODUCTION | H2 — INTRODUCTION | Correct heading + level |
| midterm | 8 | H3 — What was evaluated? | H3 — What was evaluated? | Correct heading + level |
| midterm | 8 | H3 — Why was the evaluation conducted and in which context? | H3 — Why was the evaluation conducted and in which context? | Correct heading + level |
| midterm | 10 | H2 — FINDINGS | H1 — FINDINGS | Wrong or absent level |
| midterm | 10 | H3 — Relevance and strategic focus of the design of the strategic plan | H2 — Relevance and strategic focus of the design of the strategic plan | Wrong or absent level |
| midterm | 26 | H1 — 1. Introduction | H1 — 1. Introduction | Correct heading + level |
| midterm | 26 | H2 — 1.1 EVALUATION FEATURES | H2 — 1.1 EVALUATION FEATURES | Correct heading + level |
| midterm | 27 | H2 — 1.2 CONTEXT | H1 — 1.2 CONTEXT | Wrong or absent level |
| midterm | 27 | H3 — Global economic, climate, conflict and inequality trends | H2 — Global economic, climate, conflict and inequality trends | Wrong or absent level |
| midterm | 36 | H1 — 2. Evaluation findings | H1 — 2. Evaluation findings | Correct heading + level |
| midterm | 36 | H2 — 2.1 STRENGTH AND RELEVANCE OF STRATEGIC PLAN DESIGN | H2 — 2.1 STRENGTH AND RELEVANCE OF STRATEGIC PLAN DESIGN | Correct heading + level |
| midterm | 36 | H3 — 2.1.1 Did the SP in its design clearly articulate its intended changes? | H3 — 2.1.1 Did the SP in its design clearly articulate its intended changes? | Correct heading + level |
| midterm | 61 | H3 — 2.2.3 How does the ambition of the SP compare to the evolving reality of funding? | H1 — 2.2.3 How does the ambition of the SP compare to the evolving reality of funding? | Wrong or absent level |
| midterm | 87 | H1 — 3. Conclusions and recommendations | H1 — 3. Conclusions and recommendations | Correct heading + level |
| midterm | 87 | H2 — 2.3 3.1 CONCLUSIONS | H2 — 2.3 3.1 CONCLUSIONS | Correct heading + level |
| midterm | 98 | H1 — Annex III. Methodology | H1 — Annex III. Methodology | Correct heading + level |
| midterm | 98 | H2 — Overall approach | H2 — Overall approach | Correct heading + level |
| indonesia | 7 | H1 — Executive summary | H1 — Executive summary | Correct heading + level |
| indonesia | 7 | H2 — Introduction | H2 — Introduction | Correct heading + level |
| indonesia | 7 | H3 — Evaluation features | H3 — Evaluation features | Correct heading + level |
| indonesia | 7 | H3 — Context | H3 — Context | Correct heading + level |
| indonesia | 11 | H2 — Evaluation key insights and conclusions | H1 — Evaluation key insights and conclusions | Wrong or absent level |
| indonesia | 11 | H3 — Insight 1. CSP architecture | H2 — Insight 1. CSP architecture | Wrong or absent level |
| indonesia | 11 | H3 — Insight 2. Country capacity strengthening | H2 — Insight 2. Country capacity strengthening | Wrong or absent level |
| indonesia | 20 | H1 — Introduction | H1 — Introduction | Correct heading + level |
| indonesia | 20 | H2 — 1.1. Evaluation features | H2 — 1.1. Evaluation features | Correct heading + level |
| indonesia | 20 | H2 — 1.2. Context | H2 — 1.2. Context | Correct heading + level |
| indonesia | 20 | H3 — Geography, Demography, and Government | H3 — Geography, Demography, and Government | Correct heading + level |
| indonesia | 20 | H3 — National policies and Sustainable Development Goals (SDG) | H3 — National policies and Sustainable Development Goals (SDG) | Correct heading + level |
| indonesia | 33 | H1 — Evaluation findings | H1 — Evaluation findings | Correct heading + level |
| indonesia | 33 | H2 — 2.1. EQ1: To what extent and in what ways is the CSP evidence-based and strategically focused to address the institutional capacity needs on food security, nutrition, and emergency preparedness of the Government of Indonesia? | H2 — 2.1. EQ1: To what extent and in what ways is the CSP evidence-based and strategically focused to address the institutional capacity needs on food security, nutrition, and emergency preparedness of the Government of Indonesia? | Correct heading + level |
| indonesia | 33 | H3 — EQ 1.1 To what extent was the design of the CSP informed by credible evidence (including by the evaluation of the previous CSP as relevant) and strategically and realistically targeted to address the food security, nutrition, and emergency preparedness institutional capacity needs of the Government? | — | Missed heading |
| indonesia | 33 | H3 — EQ 1.2 To what extent and in what ways was the CSP designed to support the UN cooperation framework and the SDGs? | — | Missed heading |
| indonesia | 42 | H4 — EQ2.1a: CSP Output Achievements and Contributions to Outcomes | H1 — EQ2.1a: CSP Output Achievements and Contributions to Outcomes | Wrong or absent level |
| indonesia | 42 | — | H2 — Table 15: Output Indicators Annual Achievements Against Targets | Extra prediction |
| indonesia | 48 | H5 — SO1: Evidence and Data | Level not supplied — **SO1: Evidence and Data** | Wrong or absent level |
| indonesia | 56 | H3 — EQ 2.3 To what extent are the enhanced food security, nutrition and emergency preparedness country capacities envisaged by the CSP likely to be sustainable, in particular from a financial, social, and institutional perspective? | Level not supplied — EQ 2.3 To what extent are the enhanced food security, nutrition and emergency preparedness country capacities envisaged by the CSP likely to be sustainable, in particular from a financial, social, and institutional perspective? | Wrong or absent level |
| indonesia | 68 | H1 — Conclusions and recommendations | H1 — Conclusions and recommendations | Correct heading + level |
| indonesia | 68 | H2 — 3.1. Conclusions | H2 — 3.1. Conclusions | Correct heading + level |
| colombia | 7 | H1 — Resumen ejecutivo | H1 — Resumen ejecutivo | Correct heading + level |
| colombia | 7 | H2 — Introducción | H2 — Introducción | Correct heading + level |
| colombia | 7 | H3 — Características de la evaluación | H3 — Características de la evaluación | Correct heading + level |
| colombia | 7 | H3 — Contexto | H2 — Contexto | Wrong or absent level |
| colombia | 13 | H2 — Hallazgos derivados de la evaluación | H1 — Hallazgos derivados de la evaluación | Wrong or absent level |
| colombia | 13 | H3 — ¿En qué medida el plan estratégico para el país se basa en datos empíricos y está orientado estratégicamente para atender las necesidades de los más vulnerables? | Level not supplied — ¿En qué medida el plan estratégico para el país se basa en datos empíricos y está orientado estratégicamente para atender las necesidades de los más vulnerables? | Wrong or absent level |
| colombia | 13 | H4 — Pertinencia con respecto a las necesidades | H2 — Pertinencia con respecto a las necesidades | Wrong or absent level |
| colombia | 13 | H3 — ¿Cuáles son el alcance y la calidad de la contribución del PMA a los efectos estratégicos del plan estratégico para Colombia? | H2 — ¿Cuáles son el alcance y la calidad de la contribución del PMA a los efectos estratégicos del plan estratégico para Colombia? | Wrong or absent level |
| colombia | 28 | H1 — 1. Introducción | H1 — 1. Introducción | Correct heading + level |
| colombia | 28 | H2 — 1.1. CARACTERÍSTICAS DE LA EVALUACIÓN | H2 — 1.1. CARACTERÍSTICAS DE LA EVALUACIÓN | Correct heading + level |
| colombia | 28 | H2 — 1.2. CONTEXTO | H2 — 1.2. CONTEXTO | Correct heading + level |
| colombia | 28 | H3 — Contexto general | H3 — Contexto general | Correct heading + level |
| colombia | 42 | H1 — 2. Resultados de la evaluación | H1 — 2. Resultados de la evaluación | Correct heading + level |
| colombia | 42 | H2 — 2.1. PE 1: ¿EN QUÉ MEDIDA EL PEP ESTÁ BASADO EN EVIDENCIA Y ORIENTADO ESTRATÉGICAMENTE A SATISFACER LAS NECESIDADES DE LOS MÁS VULNERABLES? | H2 — 2.1. PE 1: ¿EN QUÉ MEDIDA EL PEP ESTÁ BASADO EN EVIDENCIA Y ORIENTADO ESTRATÉGICAMENTE A SATISFACER LAS NECESIDADES DE LOS MÁS VULNERABLES? | Correct heading + level |
| colombia | 42 | H3 — PE 1.1: ¿En qué medida el PEP se basó en los datos empíricos existentes sobre los desafíos relacionados con el hambre y los problemas de seguridad alimentaria y nutrición imperantes en el país, para asegurar así la pertinencia de su diseño a nivel territorial, tomando en cuenta la interculturalidad? | — | Missed heading |
| colombia | 42 | — | H3 — Resumen | Extra prediction |
| colombia | 56 | H4 — Dimensión 2: Entorno político | H1 — Dimensión 2: Entorno político | Wrong or absent level |
| colombia | 56 | H5 — Productos | H2 — Productos | Wrong or absent level |
| colombia | 56 | H5 — Resultados | H2 — Resultados $^{92}$ | Wrong or absent level |
| colombia | 72 | H2 — 2.3. PE 3: ¿EN QUÉ MEDIDA EL PMA HA UTILIZADO SUS RECURSOS DE MANERA EFICIENTE PARA CONTRIBUIR A LOS PRODUCTOS Y EFECTOS ESTRATÉGICOS DEL PEP? | H1 — 2.3. PE 3: ¿EN QUÉ MEDIDA EL PMA HA UTILIZADO SUS RECURSOS DE MANERA EFICIENTE PARA CONTRIBUIR A LOS PRODUCTOS Y EFECTOS ESTRATÉGICOS DEL PEP? | Wrong or absent level |
| colombia | 72 | H3 — PE 3.1 ¿En qué medida se entregaron los productos en el plazo previsto? | H2 — PE 3.1 ¿En qué medida se entregaron los productos en el plazo previsto? | Wrong or absent level |
| colombia | 72 | H4 — Productos y logros | H3 — Productos y logros | Wrong or absent level |
| colombia | 72 | — | H3 — Resumen | Extra prediction |
| colombia | 73 | — | H1 — Figura 11: Total de dólares anuales en transferencias de efectivo ejecutadas | Extra prediction |
| colombia | 73 | — | H1 — Figura 12: Total de dólares anuales en transferencias de alimentos ejecutadas | Extra prediction |
| colombia | 93 | H1 — 3. Conclusiones y recomendaciones | H1 — 3. Conclusiones y recomendaciones | Correct heading + level |
| colombia | 93 | H2 — 3.1. CONCLUSIONES | H2 — 3.1. CONCLUSIONES | Correct heading + level |

### LightOnOCR-3-0.8B / MLX: rerun predictions versus reference

| Report | PDF page | Reference | Rerun prediction | Outcome |
| --- | --- | --- | --- | --- |
| targeting | 7 | — | H1 — Figure 1: Global humanitarian requirements and resources (2019-2025) | Extra prediction |
| targeting | 11 | H4 — Appropriateness | Level not supplied — **Appropriateness** | Wrong or absent level |
| targeting | 11 | H3 — Conclusion 2: WFP has a clear understanding of the strengths and weaknesses of various targeting and prioritization approaches and increasingly takes into account vulnerabilities in the way it targets and prioritizes. Selected approaches were found to be largely appropriate for their specific contexts but evidence related to the costs of various approaches is inconclusive. In addition, WFP’s targeting and prioritization practices were found to be insufficiently agile and cooperative. | — | Missed heading |
| targeting | 24 | H1 — 1 Introduction | H1 — 1 Introduction | Correct heading + level |
| targeting | 24 | H2 — 1.1 Evaluation features | H2 — 1.1 Evaluation features | Correct heading + level |
| targeting | 27 | — | H1 — Figure 2. Resources required and allocated contributions, 2018–2025 | Extra prediction |
| targeting | 33 | H1 — 2 Evaluation findings | H1 — 2 Evaluation findings | Correct heading + level |
| targeting | 33 | H2 — 2.1 How relevant and appropriate are WFP’s approaches to targeting and prioritization? | H2 — **EQ1** 2.1 How relevant and appropriate are WFP’s approaches to targeting and prioritization? | Correct heading + level |
| targeting | 33 | H3 — 2.1.1 WFP’s normative framework and support structures for targeting and prioritization provide a broad and relevant operational foundation | H3 — **EQ4.1** 2.1.1 WFP’s normative framework and support structures for targeting and prioritization provide a broad and relevant operational foundation | Correct heading + level |
| targeting | 33 | H4 — 2.1.1.1 WFP’s normative framework on targeting and prioritization has clarified key aspects of the process | H4 — 2.1.1.1 WFP’s normative framework on targeting and prioritization has clarified key aspects of the process | Correct heading + level |
| targeting | 67 | H4 — 2.2.1.4 Good practices in reducing targeting errors are unevenly applied | Level not supplied — 2.2.1.4 Good practices in reducing targeting errors are unevenly applied | Wrong or absent level |
| targeting | 96 | H1 — 3 Conclusions and recommendations | H1 — 3 Conclusions and recommendations | Correct heading + level |
| targeting | 96 | H2 — 3.1 Conclusions | H2 — 3.1 Conclusions | Correct heading + level |
| targeting | 96 | H3 — Conclusion 1: WFP’s normative framework and support structures for targeting and prioritization have evolved considerably over the past years and largely serve their purpose well, although country offices are asking for clearer strategic guidance in an era of unprecedented budget cuts. | — | Missed heading |
| targeting | 109 | H2 — Objectives and users of the evaluation | H1 — Objectives and users of the evaluation | Wrong or absent level |
| targeting | 109 | H2 — Evaluation questions | H1 — Evaluation questions | Wrong or absent level |
| targeting | 109 | H2 — Methodology and ethical considerations | H1 — Methodology and ethical considerations | Wrong or absent level |
| midterm | 8 | H1 — Executive summary | H1 — Executive summary | Correct heading + level |
| midterm | 8 | H2 — INTRODUCTION | H2 — INTRODUCTION | Correct heading + level |
| midterm | 8 | H3 — What was evaluated? | H3 — What was evaluated? | Correct heading + level |
| midterm | 8 | H3 — Why was the evaluation conducted and in which context? | H3 — Why was the evaluation conducted and in which context? | Correct heading + level |
| midterm | 10 | H2 — FINDINGS | H1 — FINDINGS | Wrong or absent level |
| midterm | 10 | H3 — Relevance and strategic focus of the design of the strategic plan | H2 — Relevance and strategic focus of the design of the strategic plan | Wrong or absent level |
| midterm | 26 | H1 — 1. Introduction | H1 — 1. Introduction | Correct heading + level |
| midterm | 26 | H2 — 1.1 EVALUATION FEATURES | H2 — 1.1 EVALUATION FEATURES | Correct heading + level |
| midterm | 27 | H2 — 1.2 CONTEXT | H1 — 1.2 CONTEXT | Wrong or absent level |
| midterm | 27 | H3 — Global economic, climate, conflict and inequality trends | H2 — Global economic, climate, conflict and inequality trends | Wrong or absent level |
| midterm | 36 | H1 — 2. Evaluation findings | H1 — 2. Evaluation findings | Correct heading + level |
| midterm | 36 | H2 — 2.1 STRENGTH AND RELEVANCE OF STRATEGIC PLAN DESIGN | H2 — 2.1 STRENGTH AND RELEVANCE OF STRATEGIC PLAN DESIGN | Correct heading + level |
| midterm | 36 | H3 — 2.1.1 Did the SP in its design clearly articulate its intended changes? | H3 — 2.1.1 Did the SP in its design clearly articulate its intended changes? | Correct heading + level |
| midterm | 61 | H3 — 2.2.3 How does the ambition of the SP compare to the evolving reality of funding? | H1 — 2.2.3 How does the ambition of the SP compare to the evolving reality of funding? | Wrong or absent level |
| midterm | 87 | H1 — 3. Conclusions and recommendations | H1 — 3. Conclusions and recommendations | Correct heading + level |
| midterm | 87 | H2 — 2.3 3.1 CONCLUSIONS | H2 — 2.3 3.1 CONCLUSIONS | Correct heading + level |
| midterm | 98 | H1 — Annex III. Methodology | H1 — Annex III. Methodology | Correct heading + level |
| midterm | 98 | H2 — Overall approach | H2 — Overall approach | Correct heading + level |
| indonesia | 7 | H1 — Executive summary | H1 — Executive summary | Correct heading + level |
| indonesia | 7 | H2 — Introduction | H2 — Introduction | Correct heading + level |
| indonesia | 7 | H3 — Evaluation features | H3 — Evaluation features | Correct heading + level |
| indonesia | 7 | H3 — Context | H3 — Context | Correct heading + level |
| indonesia | 11 | H2 — Evaluation key insights and conclusions | H1 — Evaluation key insights and conclusions | Wrong or absent level |
| indonesia | 11 | H3 — Insight 1. CSP architecture | H2 — Insight 1. CSP architecture | Wrong or absent level |
| indonesia | 11 | H3 — Insight 2. Country capacity strengthening | H2 — Insight 2. Country capacity strengthening | Wrong or absent level |
| indonesia | 20 | H1 — Introduction | H1 — Introduction | Correct heading + level |
| indonesia | 20 | H2 — 1.1. Evaluation features | H2 — 1.1. Evaluation features | Correct heading + level |
| indonesia | 20 | H2 — 1.2. Context | H2 — 1.2. Context | Correct heading + level |
| indonesia | 20 | H3 — Geography, Demography, and Government | H3 — Geography, Demography, and Government | Correct heading + level |
| indonesia | 20 | H3 — National policies and Sustainable Development Goals (SDG) | H3 — National policies and Sustainable Development Goals (SDG) | Correct heading + level |
| indonesia | 33 | H1 — Evaluation findings | H1 — Evaluation findings | Correct heading + level |
| indonesia | 33 | H2 — 2.1. EQ1: To what extent and in what ways is the CSP evidence-based and strategically focused to address the institutional capacity needs on food security, nutrition, and emergency preparedness of the Government of Indonesia? | H2 — 2.1. EQ1: To what extent and in what ways is the CSP evidence-based and strategically focused to address the institutional capacity needs on food security, nutrition, and emergency preparedness of the Government of Indonesia? | Correct heading + level |
| indonesia | 33 | H3 — EQ 1.1 To what extent was the design of the CSP informed by credible evidence (including by the evaluation of the previous CSP as relevant) and strategically and realistically targeted to address the food security, nutrition, and emergency preparedness institutional capacity needs of the Government? | — | Missed heading |
| indonesia | 33 | H3 — EQ 1.2 To what extent and in what ways was the CSP designed to support the UN cooperation framework and the SDGs? | — | Missed heading |
| indonesia | 33 | — | H3 — Table 9: Strategic Review Gaps and CSP Interventions | Extra prediction |
| indonesia | 42 | H4 — EQ2.1a: CSP Output Achievements and Contributions to Outcomes | H1 — EQ2.1a: CSP Output Achievements and Contributions to Outcomes | Wrong or absent level |
| indonesia | 42 | — | H2 — Table 15: Output Indicators Annual Achievements Against Targets | Extra prediction |
| indonesia | 48 | H5 — SO1: Evidence and Data | Level not supplied — **SO1: Evidence and Data** | Wrong or absent level |
| indonesia | 56 | H3 — EQ 2.3 To what extent are the enhanced food security, nutrition and emergency preparedness country capacities envisaged by the CSP likely to be sustainable, in particular from a financial, social, and institutional perspective? | Level not supplied — EQ 2.3 To what extent are the enhanced food security, nutrition and emergency preparedness country capacities envisaged by the CSP likely to be sustainable, in particular from a financial, social, and institutional perspective? | Wrong or absent level |
| indonesia | 68 | H1 — Conclusions and recommendations | H1 — Conclusions and recommendations | Correct heading + level |
| indonesia | 68 | H2 — 3.1. Conclusions | H2 — 3.1. Conclusions | Correct heading + level |
| colombia | 7 | H1 — Resumen ejecutivo | H1 — Resumen ejecutivo | Correct heading + level |
| colombia | 7 | H2 — Introducción | H2 — Introducción | Correct heading + level |
| colombia | 7 | H3 — Características de la evaluación | H3 — Características de la evaluación | Correct heading + level |
| colombia | 7 | H3 — Contexto | H3 — Contexto | Correct heading + level |
| colombia | 13 | H2 — Hallazgos derivados de la evaluación | H1 — Hallazgos derivados de la evaluación | Wrong or absent level |
| colombia | 13 | H3 — ¿En qué medida el plan estratégico para el país se basa en datos empíricos y está orientado estratégicamente para atender las necesidades de los más vulnerables? | Level not supplied — ¿En qué medida el plan estratégico para el país se basa en datos empíricos y está orientado estratégicamente para atender las necesidades de los más vulnerables? | Wrong or absent level |
| colombia | 13 | H4 — Pertinencia con respecto a las necesidades | H2 — Pertinencia con respecto a las necesidades | Wrong or absent level |
| colombia | 13 | H3 — ¿Cuáles son el alcance y la calidad de la contribución del PMA a los efectos estratégicos del plan estratégico para Colombia? | H2 — ¿Cuáles son el alcance y la calidad de la contribución del PMA a los efectos estratégicos del plan estratégico para Colombia? | Wrong or absent level |
| colombia | 28 | H1 — 1. Introducción | H1 — 1. Introducción | Correct heading + level |
| colombia | 28 | H2 — 1.1. CARACTERÍSTICAS DE LA EVALUACIÓN | H2 — 1.1. CARACTERÍSTICAS DE LA EVALUACIÓN | Correct heading + level |
| colombia | 28 | H2 — 1.2. CONTEXTO | H2 — 1.2. CONTEXTO | Correct heading + level |
| colombia | 28 | H3 — Contexto general | H3 — Contexto general | Correct heading + level |
| colombia | 42 | H1 — 2. Resultados de la evaluación | H1 — 2. Resultados de la evaluación | Correct heading + level |
| colombia | 42 | H2 — 2.1. PE 1: ¿EN QUÉ MEDIDA EL PEP ESTÁ BASADO EN EVIDENCIA Y ORIENTADO ESTRATÉGICAMENTE A SATISFACER LAS NECESIDADES DE LOS MÁS VULNERABLES? | H2 — 2.1. PE 1: ¿EN QUÉ MEDIDA EL PEP ESTÁ BASADO EN EVIDENCIA Y ORIENTADO ESTRATÉGICAMENTE A SATISFACER LAS NECESIDADES DE LOS MÁS VULNERABLES? | Correct heading + level |
| colombia | 42 | H3 — PE 1.1: ¿En qué medida el PEP se basó en los datos empíricos existentes sobre los desafíos relacionados con el hambre y los problemas de seguridad alimentaria y nutrición imperantes en el país, para asegurar así la pertinencia de su diseño a nivel territorial, tomando en cuenta la interculturalidad? | — | Missed heading |
| colombia | 42 | — | H3 — Resumen | Extra prediction |
| colombia | 56 | H4 — Dimensión 2: Entorno político | H1 — Dimensión 2: Entorno político | Wrong or absent level |
| colombia | 56 | H5 — Productos | H2 — Productos | Wrong or absent level |
| colombia | 56 | H5 — Resultados | H2 — Resultados⁹² | Wrong or absent level |
| colombia | 72 | H2 — 2.3. PE 3: ¿EN QUÉ MEDIDA EL PMA HA UTILIZADO SUS RECURSOS DE MANERA EFICIENTE PARA CONTRIBUIR A LOS PRODUCTOS Y EFECTOS ESTRATÉGICOS DEL PEP? | H1 — 2.3. PE 3: ¿EN QUÉ MEDIDA EL PMA HA UTILIZADO SUS RECURSOS DE MANERA EFICIENTE PARA CONTRIBUIR A LOS PRODUCTOS Y EFECTOS ESTRATÉGICOS DEL PEP? | Wrong or absent level |
| colombia | 72 | H3 — PE 3.1 ¿En qué medida se entregaron los productos en el plazo previsto? | H2 — PE 3.1 ¿En qué medida se entregaron los productos en el plazo previsto? | Wrong or absent level |
| colombia | 72 | H4 — Productos y logros | H3 — Productos y logros | Wrong or absent level |
| colombia | 72 | — | H3 — Resumen | Extra prediction |
| colombia | 73 | — | H1 — Figura 11: Total de dólares anuales en transferencias de efectivo ejecutadas | Extra prediction |
| colombia | 73 | — | H1 — Figura 12: Total de dólares anuales en transferencias de alimentos ejecutadas | Extra prediction |
| colombia | 93 | H1 — 3. Conclusiones y recomendaciones | H1 — 3. Conclusiones y recomendaciones | Correct heading + level |
| colombia | 93 | H2 — 3.1. CONCLUSIONES | H2 — 3.1. CONCLUSIONES | Correct heading + level |

### Qwen3.6-27B 4-bit — single image: rerun predictions versus reference

| Report | PDF page | Reference | Rerun prediction | Outcome |
| --- | --- | --- | --- | --- |
| targeting | 11 | H3 — Conclusion 2: WFP has a clear understanding of the strengths and weaknesses of various targeting and prioritization approaches and increasingly takes into account vulnerabilities in the way it targets and prioritizes. Selected approaches were found to be largely appropriate for their specific contexts but evidence related to the costs of various approaches is inconclusive. In addition, WFP’s targeting and prioritization practices were found to be insufficiently agile and cooperative. | H2 — Conclusion 2: WFP has a clear understanding of the strengths and weaknesses of various targeting and prioritization approaches and increasingly takes into account vulnerabilities in the way it targets and prioritizes. Selected approaches were found to be largely appropriate for their specific contexts but evidence related to the costs of various approaches is inconclusive. In addition, WFP’s targeting and prioritization practices were found to be insufficiently agile and cooperative. | Wrong or absent level |
| targeting | 11 | H4 — Appropriateness | H3 — Appropriateness | Wrong or absent level |
| targeting | 24 | H1 — 1 Introduction | H1 — 1 Introduction | Correct heading + level |
| targeting | 24 | H2 — 1.1 Evaluation features | H2 — 1.1 Evaluation features | Correct heading + level |
| targeting | 33 | H1 — 2 Evaluation findings | H1 — 2 Evaluation findings | Correct heading + level |
| targeting | 33 | H2 — 2.1 How relevant and appropriate are WFP’s approaches to targeting and prioritization? | H2 — 2.1 How relevant and appropriate are WFP’s approaches to targeting and prioritization? | Correct heading + level |
| targeting | 33 | H3 — 2.1.1 WFP’s normative framework and support structures for targeting and prioritization provide a broad and relevant operational foundation | H3 — 2.1.1 WFP’s normative framework and support structures for targeting and prioritization provide a broad and relevant operational foundation | Correct heading + level |
| targeting | 33 | H4 — 2.1.1.1 WFP’s normative framework on targeting and prioritization has clarified key aspects of the process | H4 — 2.1.1.1 WFP’s normative framework on targeting and prioritization has clarified key aspects of the process | Correct heading + level |
| targeting | 67 | H4 — 2.2.1.4 Good practices in reducing targeting errors are unevenly applied | H4 — 2.2.1.4 Good practices in reducing targeting errors are unevenly applied | Correct heading + level |
| targeting | 96 | H1 — 3 Conclusions and recommendations | H1 — 3 Conclusions and recommendations | Correct heading + level |
| targeting | 96 | H2 — 3.1 Conclusions | H2 — 3.1 Conclusions | Correct heading + level |
| targeting | 96 | H3 — Conclusion 1: WFP’s normative framework and support structures for targeting and prioritization have evolved considerably over the past years and largely serve their purpose well, although country offices are asking for clearer strategic guidance in an era of unprecedented budget cuts. | H3 — Conclusion 1: WFP’s normative framework and support structures for targeting and prioritization have evolved considerably over the past years and largely serve their purpose well, although country offices are asking for clearer strategic guidance in an era of unprecedented budget cuts. | Correct heading + level |
| targeting | 109 | H2 — Objectives and users of the evaluation | H2 — Objectives and users of the evaluation | Correct heading + level |
| targeting | 109 | H2 — Evaluation questions | H2 — Evaluation questions | Correct heading + level |
| targeting | 109 | H2 — Methodology and ethical considerations | H2 — Methodology and ethical considerations | Correct heading + level |
| midterm | 8 | H1 — Executive summary | H1 — Executive summary | Correct heading + level |
| midterm | 8 | H2 — INTRODUCTION | H2 — INTRODUCTION | Correct heading + level |
| midterm | 8 | H3 — What was evaluated? | H3 — What was evaluated? | Correct heading + level |
| midterm | 8 | H3 — Why was the evaluation conducted and in which context? | H3 — Why was the evaluation conducted and in which context? | Correct heading + level |
| midterm | 10 | H2 — FINDINGS | H1 — FINDINGS | Wrong or absent level |
| midterm | 10 | H3 — Relevance and strategic focus of the design of the strategic plan | H2 — Relevance and strategic focus of the design of the strategic plan | Wrong or absent level |
| midterm | 26 | H1 — 1. Introduction | H1 — 1. Introduction | Correct heading + level |
| midterm | 26 | H2 — 1.1 EVALUATION FEATURES | H2 — 1.1 EVALUATION FEATURES | Correct heading + level |
| midterm | 27 | H2 — 1.2 CONTEXT | H2 — 1.2 CONTEXT | Correct heading + level |
| midterm | 27 | H3 — Global economic, climate, conflict and inequality trends | H3 — Global economic, climate, conflict and inequality trends | Correct heading + level |
| midterm | 36 | H1 — 2. Evaluation findings | H1 — 2. Evaluation findings | Correct heading + level |
| midterm | 36 | H2 — 2.1 STRENGTH AND RELEVANCE OF STRATEGIC PLAN DESIGN | H2 — 2.1 STRENGTH AND RELEVANCE OF STRATEGIC PLAN DESIGN | Correct heading + level |
| midterm | 36 | H3 — 2.1.1 Did the SP in its design clearly articulate its intended changes? | H3 — 2.1.1 Did the SP in its design clearly articulate its intended changes? | Correct heading + level |
| midterm | 61 | H3 — 2.2.3 How does the ambition of the SP compare to the evolving reality of funding? | H3 — 2.2.3 How does the ambition of the SP compare to the evolving reality of funding? | Correct heading + level |
| midterm | 87 | H1 — 3. Conclusions and recommendations | H1 — 3. Conclusions and recommendations | Correct heading + level |
| midterm | 87 | H2 — 2.3 3.1 CONCLUSIONS | H2 — 3.1 CONCLUSIONS | Correct heading + level |
| midterm | 98 | H1 — Annex III. Methodology | H1 — Annex III. Methodology | Correct heading + level |
| midterm | 98 | H2 — Overall approach | H2 — Overall approach | Correct heading + level |
| indonesia | 7 | H1 — Executive summary | H1 — Executive summary | Correct heading + level |
| indonesia | 7 | H2 — Introduction | H2 — Introduction | Correct heading + level |
| indonesia | 7 | H3 — Evaluation features | H3 — Evaluation features | Correct heading + level |
| indonesia | 7 | H3 — Context | H3 — Context | Correct heading + level |
| indonesia | 11 | H2 — Evaluation key insights and conclusions | H1 — Evaluation key insights and conclusions | Wrong or absent level |
| indonesia | 11 | H3 — Insight 1. CSP architecture | H2 — Insight 1. CSP architecture | Wrong or absent level |
| indonesia | 11 | H3 — Insight 2. Country capacity strengthening | H2 — Insight 2. Country capacity strengthening | Wrong or absent level |
| indonesia | 20 | H1 — Introduction | H1 — Introduction | Correct heading + level |
| indonesia | 20 | H2 — 1.1. Evaluation features | H2 — 1.1. Evaluation features | Correct heading + level |
| indonesia | 20 | H2 — 1.2. Context | H2 — 1.2. Context | Correct heading + level |
| indonesia | 20 | H3 — Geography, Demography, and Government | H3 — Geography, Demography, and Government | Correct heading + level |
| indonesia | 20 | H3 — National policies and Sustainable Development Goals (SDG) | H3 — National policies and Sustainable Development Goals (SDG) | Correct heading + level |
| indonesia | 33 | H1 — Evaluation findings | H1 — Evaluation findings | Correct heading + level |
| indonesia | 33 | H2 — 2.1. EQ1: To what extent and in what ways is the CSP evidence-based and strategically focused to address the institutional capacity needs on food security, nutrition, and emergency preparedness of the Government of Indonesia? | H2 — 2.1. EQ1: To what extent and in what ways is the CSP evidence-based and strategically focused to address the institutional capacity needs on food security, nutrition, and emergency preparedness of the Government of Indonesia? | Correct heading + level |
| indonesia | 33 | H3 — EQ 1.1 To what extent was the design of the CSP informed by credible evidence (including by the evaluation of the previous CSP as relevant) and strategically and realistically targeted to address the food security, nutrition, and emergency preparedness institutional capacity needs of the Government? | H3 — EQ 1.1 To what extent was the design of the CSP informed by credible evidence (including by the evaluation of the previous CSP as relevant) and strategically and realistically targeted to address the food security, nutrition, and emergency preparedness institutional capacity needs of the Government? | Correct heading + level |
| indonesia | 33 | H3 — EQ 1.2 To what extent and in what ways was the CSP designed to support the UN cooperation framework and the SDGs? | H3 — EQ 1.2 To what extent and in what ways was the CSP designed to support the UN cooperation framework and the SDGs? | Correct heading + level |
| indonesia | 42 | H4 — EQ2.1a: CSP Output Achievements and Contributions to Outcomes | H3 — EQ2.1a: CSP Output Achievements and Contributions to Outcomes | Wrong or absent level |
| indonesia | 48 | H5 — SO1: Evidence and Data | H3 — SO1: Evidence and Data | Wrong or absent level |
| indonesia | 56 | H3 — EQ 2.3 To what extent are the enhanced food security, nutrition and emergency preparedness country capacities envisaged by the CSP likely to be sustainable, in particular from a financial, social, and institutional perspective? | H3 — EQ 2.3 To what extent are the enhanced food security, nutrition and emergency preparedness country capacities envisaged by the CSP likely to be sustainable, in particular from a financial, social, and institutional perspective? | Correct heading + level |
| indonesia | 68 | H1 — Conclusions and recommendations | H1 — Conclusions and recommendations | Correct heading + level |
| indonesia | 68 | H2 — 3.1. Conclusions | H2 — 3.1. Conclusions | Correct heading + level |
| colombia | 7 | H1 — Resumen ejecutivo | H1 — Resumen ejecutivo | Correct heading + level |
| colombia | 7 | H2 — Introducción | H2 — Introducción | Correct heading + level |
| colombia | 7 | H3 — Características de la evaluación | H3 — Características de la evaluación | Correct heading + level |
| colombia | 7 | H3 — Contexto | H3 — Contexto | Correct heading + level |
| colombia | 13 | H2 — Hallazgos derivados de la evaluación | H1 — Hallazgos derivados de la evaluación | Wrong or absent level |
| colombia | 13 | H3 — ¿En qué medida el plan estratégico para el país se basa en datos empíricos y está orientado estratégicamente para atender las necesidades de los más vulnerables? | H2 — ¿En qué medida el plan estratégico para el país se basa en datos empíricos y está orientado estratégicamente para atender las necesidades de los más vulnerables? | Wrong or absent level |
| colombia | 13 | H4 — Pertinencia con respecto a las necesidades | H3 — Pertinencia con respecto a las necesidades | Wrong or absent level |
| colombia | 13 | H3 — ¿Cuáles son el alcance y la calidad de la contribución del PMA a los efectos estratégicos del plan estratégico para Colombia? | H2 — ¿Cuáles son el alcance y la calidad de la contribución del PMA a los efectos estratégicos del plan estratégico para Colombia? | Wrong or absent level |
| colombia | 28 | H1 — 1. Introducción | H1 — 1. Introducción | Correct heading + level |
| colombia | 28 | H2 — 1.1. CARACTERÍSTICAS DE LA EVALUACIÓN | H2 — 1.1. CARACTERÍSTICAS DE LA EVALUACIÓN | Correct heading + level |
| colombia | 28 | H2 — 1.2. CONTEXTO | H2 — 1.2. CONTEXTO | Correct heading + level |
| colombia | 28 | H3 — Contexto general | H3 — Contexto general | Correct heading + level |
| colombia | 42 | H1 — 2. Resultados de la evaluación | H1 — 2. Resultados de la evaluación | Correct heading + level |
| colombia | 42 | H2 — 2.1. PE 1: ¿EN QUÉ MEDIDA EL PEP ESTÁ BASADO EN EVIDENCIA Y ORIENTADO ESTRATÉGICAMENTE A SATISFACER LAS NECESIDADES DE LOS MÁS VULNERABLES? | H2 — 2.1. PE 1: ¿EN QUÉ MEDIDA EL PEP ESTÁ BASADO EN EVIDENCIA Y ORIENTADO ESTRATÉGICAMENTE A SATISFACER LAS NECESIDADES DE LOS MÁS VULNERABLES? | Correct heading + level |
| colombia | 42 | H3 — PE 1.1: ¿En qué medida el PEP se basó en los datos empíricos existentes sobre los desafíos relacionados con el hambre y los problemas de seguridad alimentaria y nutrición imperantes en el país, para asegurar así la pertinencia de su diseño a nivel territorial, tomando en cuenta la interculturalidad? | H3 — PE 1.1: ¿En qué medida el PEP se basó en los datos empíricos existentes sobre los desafíos relacionados con el hambre y los problemas de seguridad alimentaria y nutrición imperantes en el país, para asegurar así la pertinencia de su diseño a nivel territorial, tomando en cuenta la interculturalidad? | Correct heading + level |
| colombia | 42 | — | H4 — Resumen | Extra prediction |
| colombia | 56 | H4 — Dimensión 2: Entorno político | H3 — Dimensión 2: Entorno político | Wrong or absent level |
| colombia | 56 | H5 — Productos | H4 — Productos | Wrong or absent level |
| colombia | 56 | H5 — Resultados | H4 — Resultados | Wrong or absent level |
| colombia | 72 | H2 — 2.3. PE 3: ¿EN QUÉ MEDIDA EL PMA HA UTILIZADO SUS RECURSOS DE MANERA EFICIENTE PARA CONTRIBUIR A LOS PRODUCTOS Y EFECTOS ESTRATÉGICOS DEL PEP? | H2 — 2.3. PE 3: ¿EN QUÉ MEDIDA EL PMA HA UTILIZADO SUS RECURSOS DE MANERA EFICIENTE PARA CONTRIBUIR A LOS PRODUCTOS Y EFECTOS ESTRATÉGICOS DEL PEP? | Correct heading + level |
| colombia | 72 | H3 — PE 3.1 ¿En qué medida se entregaron los productos en el plazo previsto? | H3 — PE 3.1 ¿En qué medida se entregaron los productos en el plazo previsto? | Correct heading + level |
| colombia | 72 | H4 — Productos y logros | H3 — Productos y logros | Wrong or absent level |
| colombia | 93 | H1 — 3. Conclusiones y recomendaciones | H1 — 3. Conclusiones y recomendaciones | Correct heading + level |
| colombia | 93 | H2 — 3.1. CONCLUSIONES | H2 — 3.1. CONCLUSIONES | Correct heading + level |

### Qwen3.6-27B / MLX 4-bit / sampled visual memory: rerun predictions versus reference

| Report | PDF page | Reference | Rerun prediction | Outcome |
| --- | --- | --- | --- | --- |
| targeting | 11 | H3 — Conclusion 2: WFP has a clear understanding of the strengths and weaknesses of various targeting and prioritization approaches and increasingly takes into account vulnerabilities in the way it targets and prioritizes. Selected approaches were found to be largely appropriate for their specific contexts but evidence related to the costs of various approaches is inconclusive. In addition, WFP’s targeting and prioritization practices were found to be insufficiently agile and cooperative. | H2 — Conclusion 2: WFP has a clear understanding of the strengths and weaknesses of various targeting and prioritization approaches and increasingly takes into account vulnerabilities in the way it targets and prioritizes. Selected approaches were found to be largely appropriate for their specific contexts but evidence related to the costs of various approaches is inconclusive. In addition, WFP’s targeting and prioritization practices were found to be insufficiently agile and cooperative. | Wrong or absent level |
| targeting | 11 | H4 — Appropriateness | H3 — Appropriateness | Wrong or absent level |
| targeting | 24 | H1 — 1 Introduction | H1 — 1 Introduction | Correct heading + level |
| targeting | 24 | H2 — 1.1 Evaluation features | H2 — 1.1 Evaluation features | Correct heading + level |
| targeting | 33 | H1 — 2 Evaluation findings | H1 — 2 Evaluation findings | Correct heading + level |
| targeting | 33 | H2 — 2.1 How relevant and appropriate are WFP’s approaches to targeting and prioritization? | H2 — 2.1 How relevant and appropriate are WFP’s approaches to targeting and prioritization? | Correct heading + level |
| targeting | 33 | H3 — 2.1.1 WFP’s normative framework and support structures for targeting and prioritization provide a broad and relevant operational foundation | H3 — 2.1.1 WFP’s normative framework and support structures for targeting and prioritization provide a broad and relevant operational foundation | Correct heading + level |
| targeting | 33 | H4 — 2.1.1.1 WFP’s normative framework on targeting and prioritization has clarified key aspects of the process | H4 — 2.1.1.1 WFP’s normative framework on targeting and prioritization has clarified key aspects of the process | Correct heading + level |
| targeting | 67 | H4 — 2.2.1.4 Good practices in reducing targeting errors are unevenly applied | H4 — 2.2.1.4 Good practices in reducing targeting errors are unevenly applied | Correct heading + level |
| targeting | 96 | H1 — 3 Conclusions and recommendations | H1 — 3 Conclusions and recommendations | Correct heading + level |
| targeting | 96 | H2 — 3.1 Conclusions | H2 — 3.1 Conclusions | Correct heading + level |
| targeting | 96 | H3 — Conclusion 1: WFP’s normative framework and support structures for targeting and prioritization have evolved considerably over the past years and largely serve their purpose well, although country offices are asking for clearer strategic guidance in an era of unprecedented budget cuts. | H2 — Conclusion 1: WFP’s normative framework and support structures for targeting and prioritization have evolved considerably over the past years and largely serve their purpose well, although country offices are asking for clearer strategic guidance in an era of unprecedented budget cuts. | Wrong or absent level |
| targeting | 109 | H2 — Objectives and users of the evaluation | H2 — Objectives and users of the evaluation | Correct heading + level |
| targeting | 109 | H2 — Evaluation questions | H2 — Evaluation questions | Correct heading + level |
| targeting | 109 | H2 — Methodology and ethical considerations | H2 — Methodology and ethical considerations | Correct heading + level |
| midterm | 8 | H1 — Executive summary | H1 — Executive summary | Correct heading + level |
| midterm | 8 | H2 — INTRODUCTION | H2 — INTRODUCTION | Correct heading + level |
| midterm | 8 | H3 — What was evaluated? | H3 — What was evaluated? | Correct heading + level |
| midterm | 8 | H3 — Why was the evaluation conducted and in which context? | H3 — Why was the evaluation conducted and in which context? | Correct heading + level |
| midterm | 10 | H2 — FINDINGS | H2 — FINDINGS | Correct heading + level |
| midterm | 10 | H3 — Relevance and strategic focus of the design of the strategic plan | H3 — Relevance and strategic focus of the design of the strategic plan | Correct heading + level |
| midterm | 26 | H1 — 1. Introduction | H1 — 1. Introduction | Correct heading + level |
| midterm | 26 | H2 — 1.1 EVALUATION FEATURES | H2 — 1.1 EVALUATION FEATURES | Correct heading + level |
| midterm | 27 | H2 — 1.2 CONTEXT | H2 — 1.2 CONTEXT | Correct heading + level |
| midterm | 27 | H3 — Global economic, climate, conflict and inequality trends | H3 — Global economic, climate, conflict and inequality trends | Correct heading + level |
| midterm | 36 | H1 — 2. Evaluation findings | H1 — 2. Evaluation findings | Correct heading + level |
| midterm | 36 | H2 — 2.1 STRENGTH AND RELEVANCE OF STRATEGIC PLAN DESIGN | H2 — 2.1 STRENGTH AND RELEVANCE OF STRATEGIC PLAN DESIGN | Correct heading + level |
| midterm | 36 | H3 — 2.1.1 Did the SP in its design clearly articulate its intended changes? | H3 — 2.1.1 Did the SP in its design clearly articulate its intended changes? | Correct heading + level |
| midterm | 61 | H3 — 2.2.3 How does the ambition of the SP compare to the evolving reality of funding? | H3 — 2.2.3 How does the ambition of the SP compare to the evolving reality of funding? | Correct heading + level |
| midterm | 87 | H1 — 3. Conclusions and recommendations | H1 — 3. Conclusions and recommendations | Correct heading + level |
| midterm | 87 | H2 — 2.3 3.1 CONCLUSIONS | H2 — 3.1 CONCLUSIONS | Correct heading + level |
| midterm | 98 | H1 — Annex III. Methodology | H1 — Annex III. Methodology | Correct heading + level |
| midterm | 98 | H2 — Overall approach | H2 — Overall approach | Correct heading + level |
| indonesia | 7 | H1 — Executive summary | H1 — Executive summary | Correct heading + level |
| indonesia | 7 | H2 — Introduction | H2 — Introduction | Correct heading + level |
| indonesia | 7 | H3 — Evaluation features | H3 — Evaluation features | Correct heading + level |
| indonesia | 7 | H3 — Context | H3 — Context | Correct heading + level |
| indonesia | 11 | H2 — Evaluation key insights and conclusions | H2 — Evaluation key insights and conclusions | Correct heading + level |
| indonesia | 11 | H3 — Insight 1. CSP architecture | H3 — Insight 1. CSP architecture | Correct heading + level |
| indonesia | 11 | H3 — Insight 2. Country capacity strengthening | H3 — Insight 2. Country capacity strengthening | Correct heading + level |
| indonesia | 20 | H1 — Introduction | H1 — Introduction | Correct heading + level |
| indonesia | 20 | H2 — 1.1. Evaluation features | H2 — 1.1. Evaluation features | Correct heading + level |
| indonesia | 20 | H2 — 1.2. Context | H2 — 1.2. Context | Correct heading + level |
| indonesia | 20 | H3 — Geography, Demography, and Government | H3 — Geography, Demography, and Government | Correct heading + level |
| indonesia | 20 | H3 — National policies and Sustainable Development Goals (SDG) | H3 — National policies and Sustainable Development Goals (SDG) | Correct heading + level |
| indonesia | 33 | H1 — Evaluation findings | H1 — Evaluation findings | Correct heading + level |
| indonesia | 33 | H2 — 2.1. EQ1: To what extent and in what ways is the CSP evidence-based and strategically focused to address the institutional capacity needs on food security, nutrition, and emergency preparedness of the Government of Indonesia? | H2 — 2.1. EQ1: To what extent and in what ways is the CSP evidence-based and strategically focused to address the institutional capacity needs on food security, nutrition, and emergency preparedness of the Government of Indonesia? | Correct heading + level |
| indonesia | 33 | H3 — EQ 1.1 To what extent was the design of the CSP informed by credible evidence (including by the evaluation of the previous CSP as relevant) and strategically and realistically targeted to address the food security, nutrition, and emergency preparedness institutional capacity needs of the Government? | H3 — EQ 1.1 To what extent was the design of the CSP informed by credible evidence (including by the evaluation of the previous CSP as relevant) and strategically and realistically targeted to address the food security, nutrition, and emergency preparedness institutional capacity needs of the Government? | Correct heading + level |
| indonesia | 33 | H3 — EQ 1.2 To what extent and in what ways was the CSP designed to support the UN cooperation framework and the SDGs? | H3 — EQ 1.2 To what extent and in what ways was the CSP designed to support the UN cooperation framework and the SDGs? | Correct heading + level |
| indonesia | 42 | H4 — EQ2.1a: CSP Output Achievements and Contributions to Outcomes | H3 — EQ2.1a: CSP Output Achievements and Contributions to Outcomes | Wrong or absent level |
| indonesia | 48 | H5 — SO1: Evidence and Data | H3 — SO1: Evidence and Data | Wrong or absent level |
| indonesia | 56 | H3 — EQ 2.3 To what extent are the enhanced food security, nutrition and emergency preparedness country capacities envisaged by the CSP likely to be sustainable, in particular from a financial, social, and institutional perspective? | H3 — EQ 2.3 To what extent are the enhanced food security, nutrition and emergency preparedness country capacities envisaged by the CSP likely to be sustainable, in particular from a financial, social, and institutional perspective? | Correct heading + level |
| indonesia | 68 | H1 — Conclusions and recommendations | H1 — Conclusions and recommendations | Correct heading + level |
| indonesia | 68 | H2 — 3.1. Conclusions | H2 — 3.1. Conclusions | Correct heading + level |
| colombia | 7 | H1 — Resumen ejecutivo | H1 — Resumen ejecutivo | Correct heading + level |
| colombia | 7 | H2 — Introducción | H2 — Introducción | Correct heading + level |
| colombia | 7 | H3 — Características de la evaluación | H3 — Características de la evaluación | Correct heading + level |
| colombia | 7 | H3 — Contexto | H3 — Contexto | Correct heading + level |
| colombia | 13 | H2 — Hallazgos derivados de la evaluación | H1 — Hallazgos derivados de la evaluación | Wrong or absent level |
| colombia | 13 | H3 — ¿En qué medida el plan estratégico para el país se basa en datos empíricos y está orientado estratégicamente para atender las necesidades de los más vulnerables? | H2 — ¿En qué medida el plan estratégico para el país se basa en datos empíricos y está orientado estratégicamente para atender las necesidades de los más vulnerables? | Wrong or absent level |
| colombia | 13 | H4 — Pertinencia con respecto a las necesidades | H3 — Pertinencia con respecto a las necesidades | Wrong or absent level |
| colombia | 13 | H3 — ¿Cuáles son el alcance y la calidad de la contribución del PMA a los efectos estratégicos del plan estratégico para Colombia? | H2 — ¿Cuáles son el alcance y la calidad de la contribución del PMA a los efectos estratégicos del plan estratégico para Colombia? | Wrong or absent level |
| colombia | 28 | H1 — 1. Introducción | H1 — 1. Introducción | Correct heading + level |
| colombia | 28 | H2 — 1.1. CARACTERÍSTICAS DE LA EVALUACIÓN | H2 — 1.1. CARACTERÍSTICAS DE LA EVALUACIÓN | Correct heading + level |
| colombia | 28 | H2 — 1.2. CONTEXTO | H2 — 1.2. CONTEXTO | Correct heading + level |
| colombia | 28 | H3 — Contexto general | H3 — Contexto general | Correct heading + level |
| colombia | 42 | H1 — 2. Resultados de la evaluación | H1 — 2. Resultados de la evaluación | Correct heading + level |
| colombia | 42 | H2 — 2.1. PE 1: ¿EN QUÉ MEDIDA EL PEP ESTÁ BASADO EN EVIDENCIA Y ORIENTADO ESTRATÉGICAMENTE A SATISFACER LAS NECESIDADES DE LOS MÁS VULNERABLES? | H2 — 2.1. PE 1: ¿EN QUÉ MEDIDA EL PEP ESTÁ BASADO EN EVIDENCIA Y ORIENTADO ESTRATÉGICAMENTE A SATISFACER LAS NECESIDADES DE LOS MÁS VULNERABLES? | Correct heading + level |
| colombia | 42 | H3 — PE 1.1: ¿En qué medida el PEP se basó en los datos empíricos existentes sobre los desafíos relacionados con el hambre y los problemas de seguridad alimentaria y nutrición imperantes en el país, para asegurar así la pertinencia de su diseño a nivel territorial, tomando en cuenta la interculturalidad? | H3 — PE 1.1: ¿En qué medida el PEP se basó en los datos empíricos existentes sobre los desafíos relacionados con el hambre y los problemas de seguridad alimentaria y nutrición imperantes en el país, para asegurar así la pertinencia de su diseño a nivel territorial, tomando en cuenta la interculturalidad? | Correct heading + level |
| colombia | 42 | — | H4 — Resumen | Extra prediction |
| colombia | 56 | H4 — Dimensión 2: Entorno político | H3 — Dimensión 2: Entorno político | Wrong or absent level |
| colombia | 56 | H5 — Productos | H4 — Productos | Wrong or absent level |
| colombia | 56 | H5 — Resultados | H4 — Resultados | Wrong or absent level |
| colombia | 72 | H2 — 2.3. PE 3: ¿EN QUÉ MEDIDA EL PMA HA UTILIZADO SUS RECURSOS DE MANERA EFICIENTE PARA CONTRIBUIR A LOS PRODUCTOS Y EFECTOS ESTRATÉGICOS DEL PEP? | H2 — 2.3. PE 3: ¿EN QUÉ MEDIDA EL PMA HA UTILIZADO SUS RECURSOS DE MANERA EFICIENTE PARA CONTRIBUIR A LOS PRODUCTOS Y EFECTOS ESTRATÉGICOS DEL PEP? | Correct heading + level |
| colombia | 72 | H3 — PE 3.1 ¿En qué medida se entregaron los productos en el plazo previsto? | H3 — PE 3.1 ¿En qué medida se entregaron los productos en el plazo previsto? | Correct heading + level |
| colombia | 72 | H4 — Productos y logros | H4 — Productos y logros | Correct heading + level |
| colombia | 72 | — | H4 — Resumen | Extra prediction |
| colombia | 93 | H1 — 3. Conclusiones y recomendaciones | H1 — 3. Conclusiones y recomendaciones | Correct heading + level |
| colombia | 93 | H2 — 3.1. CONCLUSIONES | H2 — 3.1. CONCLUSIONES | Correct heading + level |
