"""Decode the model's documented grounding format, including inline markers."""

import json
import re

from runtime import ROOT


def decode(text, page):
    records = []
    previous_type = None
    pattern = r"!\[([\w+]+)\]\(([^)]+)\)\s*(.*?)(?=!\[[\w+]+\]\(|\Z)"
    for m in re.finditer(pattern, text, re.S):
        prior = previous_type
        previous_type = m[1]
        if m[1].rstrip("+") != "title":
            continue
        content = m[3].strip()
        h = re.match(r"^(#{1,6})\s+(.+)", content, re.S)
        title = h[2].strip() if h else content
        level = len(h[1]) if h else None
        box = [float(x) / 1000 for x in m[2].split(",")]
        # The model card defines '+' as continuation of the preceding block.
        if m[1] == "title+" and prior in ("title", "title+") and records:
            prev = records[-1]
            prev["title"] += " " + title
            if prev["level"] is None:
                prev["level"] = level
            b = prev["bbox"]
            prev["bbox"] = [min(b[0], box[0]), min(b[1], box[1]), max(b[2], box[2]), max(b[3], box[3])]
            prev["continuation_blocks"] = prev.get("continuation_blocks", 0) + 1
        else:
            records.append(dict(title=title, level=level, page=page, bbox=box, type=m[1]))
    return records


if __name__ == "__main__":
    for d in (ROOT / "results").iterdir():
        source = d / "lighton_mlx"
        if not source.is_dir():
            continue
        headings = []
        for p in sorted(source.glob("*.json"), key=lambda p: int(p.stem)):
            j = json.loads(p.read_text())
            headings.extend(decode(j["text"], j["page"]))
        (d / "lighton_mlx.headings.json").write_text(json.dumps(headings, ensure_ascii=False, indent=2))
