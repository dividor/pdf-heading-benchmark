"""Measure full-document local inference; accuracy remains limited to reviewed pages."""

import argparse
import resource
from pathlib import Path

from pdf_heading_benchmark.supervised_data import read_json, write_json
from pdf_heading_benchmark.supervised_inference import markdown_text, parse_document


def benchmark(config: Path, data: Path, run: Path) -> None:
    output = run / "inference"
    if output.exists():
        raise ValueError("Inference results already exist")
    selection = read_json(run / "selection.json")
    model = read_json(run / f"{selection['selected']}.json")
    timings = []
    for record in read_json(config / "corpus.json"):
        result = parse_document(data / "pdfs" / f"wfp-{record['id']}.pdf", model)
        write_json(output / f"{record['id']}.json", result)
        (output / f"{record['id']}.md").write_text(markdown_text(result))
        timing = {k: result[k] for k in ("extract_and_feature_seconds", "predict_seconds", "total_seconds")}
        timings.append(
            {
                "report_id": record["id"],
                "pages": record["pages"],
                "lines": len(result["lines"]),
                "predicted_groups": len(result["headings"]),
                **timing,
            }
        )
        print(f"{record['id']}: {result['total_seconds']:.2f}s", flush=True)
    write_json(
        run / "runtime.json",
        {
            "documents": timings,
            "peak_rss_platform_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "peak_rss_note": "Bytes on macOS, KiB on Linux; whole-process high water mark",
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/supervised"))
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    benchmark(args.config, args.data, args.run)
