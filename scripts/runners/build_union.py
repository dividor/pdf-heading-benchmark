"""Union two parsers' heading candidates; fuzzy matching only deduplicates text.

This is an exploratory recall experiment. It contains no heading/level rules
and never loads the reference annotations.
"""

import json
import re
import unicodedata
from difflib import SequenceMatcher

from runtime import ROOT


def norm(t):
    t = re.sub(r"<[^>]*>", "", t)
    return "".join(c for c in unicodedata.normalize("NFKC", t).casefold() if c.isalnum())


for item in json.loads((ROOT / "corpus/manifest.json").read_text()):
    out = ROOT / "results" / item["id"]
    a = json.loads((out / "docling_default.headings.json").read_text())
    b = json.loads((out / "pymupdf4llm.headings.json").read_text())
    result = []
    for page in sorted({h["page"] for h in a + b}):
        aa = [dict(h, candidate_sources=["docling"]) for h in a if h["page"] == page]
        bb = [dict(h, candidate_sources=["pymupdf4llm"]) for h in b if h["page"] == page]
        ids_a = list(range(len(aa)))
        ids_b = []
        lookup = dict(enumerate(aa))
        used = set()
        for j, h in enumerate(bb):
            options = [
                (SequenceMatcher(None, norm(h["title"]), norm(g["title"]), autojunk=False).ratio(), i)
                for i, g in enumerate(aa)
                if i not in used
            ]
            score, i = max(options, default=(0, -1))
            if score >= 0.90:
                ids_b.append(i)
                used.add(i)
                lookup[i]["candidate_sources"].append("pymupdf4llm")
            else:
                idx = len(aa) + j
                ids_b.append(idx)
                lookup[idx] = h
        combined = []
        for tag, i1, i2, j1, j2 in SequenceMatcher(None, ids_a, ids_b, autojunk=False).get_opcodes():
            if tag == "equal":
                combined.extend(ids_a[i1:i2])
            else:
                combined.extend(ids_a[i1:i2])
                combined.extend(ids_b[j1:j2])
        seen = set()
        for idx in combined:
            if idx not in seen:
                result.append(lookup[idx])
                seen.add(idx)
    (out / "union.headings.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(item["id"], len(a), len(b), "union", len(result))
