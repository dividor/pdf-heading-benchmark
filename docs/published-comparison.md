## Published comparison

**Can newer models beat Chandra 2?** MiniCPM-OCR 1.0, Xiaomi-OCR-0 and PaddleOCR-VL-1.6 score higher on three parsing benchmarks in OpenBMB's published comparison. Chandra leads these candidates on olmOCR. This is evidence for a shortlist, not a universal winner.

[Open the original comparison table](https://raw.githubusercontent.com/OpenBMB/MiniCPM-OCR/c21a3ca524263ef8166cb6d350864b10c3056b61/assets/minicpm-ocr/ocr-benchmarks.png) · [Author's evaluation and methodology](https://github.com/OpenBMB/MiniCPM-OCR/blob/c21a3ca524263ef8166cb6d350864b10c3056b61/docs/minicpm_ocr_1dot0_en.md#evaluation).

[![Four comparisons: MiniCPM, Xiaomi and Paddle exceed Chandra on OmniDocBench, Real5 and Wild; Chandra leads these candidates on olmOCR. These are external parsing scores, not WFP heading-and-level results.](../../docs/images/published-comparison.png)](https://raw.githubusercontent.com/OpenBMB/MiniCPM-OCR/c21a3ca524263ef8166cb6d350864b10c3056b61/assets/minicpm-ocr/ocr-benchmarks.png)

*Original diagram of reported values. Click the diagram for the source table. Higher is better within each column; scores from different benchmarks must not be compared directly.*

| Model | OmniDocBench 1.6 | Real5 | Wild | olmOCR |
| --- | ---: | ---: | ---: | ---: |
| [Chandra 2](https://huggingface.co/datalab-to/chandra-ocr-2) | 92.27 | 88.74 | 89.08 | **85.8** |
| [MiniCPM-OCR 1.0](https://huggingface.co/openbmb/MiniCPM-OCR-1.0) | 96.51 | **93.68** | **92.39** | 82.7 |
| [Xiaomi-OCR-0](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0) | **96.83** | 92.73 | 92.06 | 82.1 |
| [PaddleOCR-VL-1.6](https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6) | 96.34 | 93.19 | 91.49 | 80.2 |
| [Unlimited-OCR-2](https://huggingface.co/baidu/Unlimited-OCR-2) | 94.02 | 87.93 | 87.79 | 79.5 |

**Source and scope:** OpenBMB's MiniCPM-OCR 1.0 comparison, checked November 23, 2026; links pin the source revision. Bold marks the highest score among these five candidates. These are results reported by a competing model's authors, not independent measurements by this project. Values preserve that comparison's configurations; later model-card updates can differ. Datalab's own Chandra 2 release announcement reports 85.9 on olmOCR, whereas this comparison reports 85.8. [Chandra release report](https://www.datalab.to/blog/chandra-2).

These benchmarks evaluate broader document parsing. They do not establish performance on our WFP titles, pages and exact heading levels. None of these external scores enters our ranking or changes our joint F0.5 results. The next comparison would run candidate pipelines on the same WFP pages and record both joint heading-and-level quality and processing time on the Mac.
