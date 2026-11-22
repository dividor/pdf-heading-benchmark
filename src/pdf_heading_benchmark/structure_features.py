"""Generic line-pair, heading-group and document-context features without gold labels."""

import math
import re
from collections import defaultdict

import numpy as np

from pdf_heading_benchmark.supervised_features import text_features


def pair_features(a: dict, b: dict) -> dict:
    af, bf = a["features"], b["features"]
    result = {f"a_{k}": v for k, v in af.items()}
    result.update({f"b_{k}": v for k, v in bf.items()})
    result.update({f"delta_{k}": bf[k] - af[k] for k in af})
    result["page_delta"] = b["page"] - a["page"]
    return {"features": result}


def style_key(line: dict) -> tuple:
    return (round(line["size"], 1), round(line["bold"]), round(line["italic"]), line["color"])


def title_key(text: str) -> str:
    text = re.split(r"\.{3,}|…", text)[0]
    text = re.sub(r"^\d+(?:\.\d+)*\.?\s*", "", text)
    return " ".join(re.findall(r"\w+", text.casefold()))


def context_index(lines: list[dict]) -> tuple[dict, set]:
    styles: dict[tuple, list] = defaultdict(list)
    toc = set()
    for line in lines:
        features = text_features(line["text"])
        if features["dot_leader"]:
            toc.add(title_key(line["text"]))
        elif features["prefix_depth"]:
            styles[style_key(line)].append(features["prefix_depth"])
    return dict(styles), toc


def group_features(indices: list[int], lines: list[dict], rows: list[dict], context: tuple) -> dict:
    first, last = indices[0], indices[-1]
    text = " ".join(lines[i]["text"] for i in indices)
    features = dict(rows[first]["features"])
    features.update(text_features(text))
    features["group_lines"] = math.log1p(len(indices))
    features["group_pages"] = lines[last]["page"] - lines[first]["page"]
    features["gap_after"] = rows[last]["features"]["gap_after"]
    for name in ("relative_size", "bold", "italic", "width"):
        values = [rows[i]["features"][name] for i in indices]
        features[f"mean_{name}"] = float(np.mean(values))
        features[f"max_{name}"] = max(values)
    styles, toc = context
    depths = styles.get(style_key(lines[first]), [])
    contextual = {
        "style_numbered_count": math.log1p(len(depths)),
        "style_mean_depth": float(np.mean(depths)) if depths else 0,
        "style_max_depth": max(depths, default=0),
        "toc_exact_title": float(bool(title_key(text)) and title_key(text) in toc),
    }
    return {
        "id": lines[first]["id"],
        "page": lines[first]["page"],
        "features": features,
        "context": contextual,
        "indices": indices,
    }


def with_context(row: dict) -> dict:
    return {**row, "features": row["features"] | row["context"]}


def training_groups(document: dict) -> list[dict]:
    lines, rows, labels = document["lines"], document["rows"], document["labels"]
    lookup = {line["id"]: i for i, line in enumerate(lines)}
    groups = [(a["level"], [lookup[k] for k in a["line_ids"]]) for a in document["groups"]]
    groups.extend((0, [i]) for i, line in enumerate(lines) if labels.get(line["id"]) == 0)
    context = context_index(lines)
    return [
        dict(group_features(indices, lines, rows, context), label=level)
        for level, indices in sorted(groups, key=lambda g: g[1][0])
    ]


def training_pairs(document: dict) -> list[dict]:
    membership = {key: i for i, a in enumerate(document["groups"]) for key in a["line_ids"]}
    result = []
    labels = document["labels"]
    for a, b in zip(document["rows"], document["rows"][1:], strict=False):
        if a["id"] not in labels or b["id"] not in labels:
            continue
        same = a["id"] in membership and membership.get(b["id"]) == membership[a["id"]]
        result.append(dict(pair_features(a, b), label=int(same)))
    return result
