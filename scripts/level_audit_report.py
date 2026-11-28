"""Recompute heading-level disagreements from the published predictions."""

from pdf_heading_benchmark.io import REPO, read_json, write_json
from pdf_heading_benchmark.level_audit import level_audit
from pdf_heading_benchmark.prediction_comparison import comparisons
from pdf_heading_benchmark.report import table

METHODS = {
    "xiaomi_ocr0": "Xiaomi: earlier whole-page adaptation",
    "minicpm_ocr10": "MiniCPM: earlier MLX adaptation",
    "paddleocr_vl16": "Paddle: earlier MiniCPM assembly adaptation",
    "chandra2_mlx": "Chandra OCR 2: existing MLX run",
    "paddleocr_vl16_official": "Paddle: official Apple Silicon pipeline",
    "ovisocr3_official_metal": "OvisOCR3: upstream prompt, vLLM Metal",
    "minicpm_ocr10_official_ollama": "MiniCPM: official package, Ollama Q8 + DSpark",
    "xiaomi_ocr0_official_metal": "Xiaomi: upstream two-stage pipeline, Metal",
}


def audit_markdown(evidence):
    rows = [[METHODS[key], *audit["counts"].values()] for key, audit in evidence.items()]
    content = "## Heading-level audit\n\n"
    content += "A recognized title can still have the wrong depth. The first three counts below add to "
    content += "the 77 references; extra predictions are counted separately. Open a method's details "
    content += "in Results to inspect every prediction beside its reference.\n\n"
    content += table(
        [
            "Configuration",
            "Correct title + level",
            "Title found, wrong level",
            "Missed title",
            "Extra prediction",
        ],
        rows,
    )
    content += "\n\n**What we verified:** on the mid-term report's PDF page 26, “1. Introduction” is "
    content += "visually the main section and “1.1 Evaluation features” its subsection. "
    content += "The earlier MiniCPM assembler emits both as H3. It also promotes the ordinary "
    content += "paragraph “3. The MTE's key features are:” to a heading. Paddle's full pipeline "
    content += "reproduces these three outputs on that page.\n\n"
    content += "In the earlier Xiaomi whole-page run, 65 of its 69 matched titles were H2. "
    content += (
        "Those titles span reference levels H1-H5, so changing every level by one cannot fix the result. "
    )
    content += "We have applied no offsets or rules fitted to these reports.\n\n"
    if "xiaomi_ocr0_official_metal" in evidence:
        content += "**Xiaomi's upstream default formatter assigns H2 to paragraph titles.** "
        content += "Executing that formatter on H1, H3 and numbered example titles returned H2 each time. "
        content += "On mid-term page 26, both Introduction and its Evaluation features subsection are H2. "
        content += (
            "The upstream two-stage run still has 37 wrong-level matches; no WFP correction was applied.\n\n"
        )
    if "ovisocr3_official_metal" in evidence:
        content += "**OvisOCR3 sometimes transcribes a title without marking it as a heading.** "
        content += "On Indonesia page 7, Executive summary, Introduction and Evaluation features "
        content += "appear as ordinary text. On targeting page 33, 2 Evaluation findings has no heading "
        content += "marker, although its subsections have H2-H4 markers. These are classification "
        content += "misses, not necessarily unreadable or absent text.\n\n"
    remote = "https://github.com/dividor/pdf-heading-benchmark/blob/codex/full-method-verification/"
    content += f"[All level disagreements and counts]({remote}outputs/level-audit.json) · "
    content += f"[Raw region-to-heading assembly examples]({remote}outputs/assembly-trace.json) · "
    content += f"[Xiaomi formatter measurements]({remote}outputs/xiaomi-assembly-trace.json) · "
    content += f"[Rerun protocol and runtime differences]({remote}docs/official-pipelines.md).\n"
    return content


def main():
    predictions = read_json(REPO / "outputs/audit_predictions.json")
    methods = [key for key in METHODS if key in predictions]
    evidence = {method: level_audit(items) for method, items in comparisons(methods).items()}
    write_json(REPO / "outputs/level-audit.json", evidence)
    (REPO / "docs/level-audit.md").write_text(audit_markdown(evidence))
    for method, audit in evidence.items():
        print(method, audit["counts"], audit["level_pairs"])


if __name__ == "__main__":
    main()
