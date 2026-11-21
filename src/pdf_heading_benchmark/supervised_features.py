"""Label-independent line features. No document-specific correction rules."""

import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pymupdf


def span_line(line: dict, page: pymupdf.Page, identifier: str) -> dict | None:
    spans = [s for s in line["spans"] if s["text"].strip()]
    if not spans:
        return None
    length = sum(len(s["text"]) for s in spans)
    weights = [len(s["text"]) / length for s in spans]
    return {
        "id": identifier,
        "page": page.number + 1,
        "text": " ".join(s["text"].strip() for s in spans),
        "bbox": list(line["bbox"]),
        "width": page.rect.width,
        "height": page.rect.height,
        "size": round(sum(s["size"] * w for s, w in zip(spans, weights, strict=True)), 2),
        "bold": round(sum(bool(s["flags"] & 16) * w for s, w in zip(spans, weights, strict=True)), 2),
        "italic": sum(bool(s["flags"] & 2) * w for s, w in zip(spans, weights, strict=True)),
        "color": spans[0]["color"],
        "font": spans[0]["font"],
    }


def extract_lines(path: Path) -> list[dict]:
    result = []
    with pymupdf.open(path) as document:
        for page in document:
            for block_index, block in enumerate(page.get_text("dict")["blocks"]):
                for line_index, line in enumerate(block.get("lines", [])):
                    identifier = f"p{page.number + 1:03d}b{block_index:03d}l{line_index:02d}"
                    value = span_line(line, page, identifier)
                    if value:
                        result.append(value)
    if not result:
        raise ValueError("No embedded text: this baseline requires an OCR/text layer")
    return result


def text_features(text: str) -> dict[str, float]:
    prefix = re.match(r"^(\d+(?:\.\d+)*)(?:\.|\s|$)", text)
    letters = [c for c in text if c.isalpha()]
    return {
        "log_chars": math.log1p(len(text)),
        "log_words": math.log1p(len(text.split())),
        "upper_fraction": sum(c.isupper() for c in letters) / max(1, len(letters)),
        "digit_fraction": sum(c.isdigit() for c in text) / max(1, len(text)),
        "prefix_depth": prefix[1].count(".") + 1 if prefix else 0,
        "number_only": float(bool(re.fullmatch(r"[\d.]+", text))),
        "dot_leader": float(bool(re.search(r"\.{3}|…|\u2026", text))),
        "ends_sentence": float(text.endswith((".", ";", ":"))),
        "caption_prefix": float(
            bool(re.match(r"^(figure|table|tabla|tableau|box|encadré)\s+\d", text, re.I))
        ),
    }


def line_features(line: dict, body: float, sizes: list[float], counts: Counter) -> dict[str, float]:
    x0, y0, x1, y1 = line["bbox"]
    return {
        **text_features(line["text"]),
        "relative_size": line["size"] / body,
        "size_rank": sum(s > round(line["size"], 1) for s in sizes) / max(1, len(sizes)),
        "bold": line["bold"],
        "italic": line["italic"],
        "red": (line["color"] >> 16 & 255) / 255,
        "green": (line["color"] >> 8 & 255) / 255,
        "blue": (line["color"] & 255) / 255,
        "x": x0 / line["width"],
        "y": y0 / line["height"],
        "width": (x1 - x0) / line["width"],
        "height": (y1 - y0) / line["height"],
        "repeat_count": math.log1p(counts[line["text"]]),
    }


def page_features(lines: list[dict], index: int, body: float) -> dict[str, float]:
    line = lines[index]
    previous = lines[max(0, index - 1)]
    following = lines[min(len(lines) - 1, index + 1)]
    return {
        "previous_size": previous["size"] / body,
        "next_size": following["size"] / body,
        "previous_bold": previous["bold"],
        "next_bold": following["bold"],
        "gap_before": (line["bbox"][1] - previous["bbox"][3]) / body,
        "gap_after": (following["bbox"][1] - line["bbox"][3]) / body,
        "previous_same_block": float(line["id"].split("l")[0] == previous["id"].split("l")[0]),
        "next_same_block": float(line["id"].split("l")[0] == following["id"].split("l")[0]),
        "next_number_only": text_features(following["text"])["number_only"],
        "previous_number_only": text_features(previous["text"])["number_only"],
    }


def feature_rows(lines: list[dict]) -> tuple[list[dict], list[str]]:
    pages: dict[int, list[dict]] = defaultdict(list)
    sizes: Counter = Counter()
    for line in lines:
        pages[line["page"]].append(line)
        sizes[round(line["size"], 1)] += len(line["text"])
    body = max(0.1, sizes.most_common(1)[0][0])
    counts = Counter(line["text"] for line in lines)
    rows = []
    for page in pages.values():
        dotted = np.mean([text_features(line["text"])["dot_leader"] for line in page])
        blocks = Counter(line["id"].split("l")[0] for line in page)
        for index, line in enumerate(page):
            features = line_features(line, body, list(sizes), counts)
            features.update(page_features(page, index, body))
            features["page_dot_fraction"] = float(dotted)
            features["block_lines"] = math.log1p(blocks[line["id"].split("l")[0]])
            rows.append({"id": line["id"], "page": line["page"], "features": features})
    return rows, sorted(rows[0]["features"])


def matrix(rows: list[dict], names: list[str]) -> np.ndarray:
    return np.asarray([[r["features"][name] for name in names] for r in rows], dtype=np.float64)
