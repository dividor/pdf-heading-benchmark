# New local OCR trials on the WFP sample

Same four public PDFs, 32 audit pages and 77 references. [Protocol, model revisions and reproduction](../../docs/field-candidates.md). Each model ran separately; recognition uses Metal and regional layout uses CPU. These are portable configurations, not replications of the external NVIDIA leaderboard. No PDF tags, text inputs, previous-page memory or gold-tuned level corrections.

| Configuration / evidence | Joint F0.5 | Correct title + level | Titles found | Extra headings | Prose retention | Time per page | Measured time / 32 pages | Loading (separate) | Errors | Pages with timeout | Pages hitting token cap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Xiaomi-OCR-0 — MLX whole page](xiaomi_ocr0.json) | 39.7% | 29/77 | 69/77 | 3 | 98.8% | 11.6 sec | 6 min 12 sec | 3.3 sec | 0 | 0 | 0 |
| [MiniCPM-OCR 1.0 — MLX + CPU layout](minicpm_ocr10.json) | 22.2% | 16/77 | 68/77 | 3 | 98.1% | 14.7 sec | 7 min 50 sec | 4.7 sec | 0 | 0 | 0 |
| [PaddleOCR-VL-1.6 — MLX + CPU layout](paddleocr_vl16.json) | 22.2% | 16/77 | 68/77 | 3 | 98.4% | 8.7 sec | 4 min 39 sec | 1.5 sec | 0 | 0 | 0 |

Joint F0.5 = 1.25C / (P + 0.25G). The main report includes joint precision, recall and every predicted-versus-reference heading. Prose retention is five-word-sequence recall from native paragraphs of at least 50 words; it is not table or reading-order accuracy.
