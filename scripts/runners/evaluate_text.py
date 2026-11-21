"""Native-text retention proxy on audit pages; this is not OCR ground-truth CER.

Reports five-word sequence recall from the native PDF text, all content and a
long-paragraph subset. It does not validate semantic correctness/table structure.
"""

import json
import re
import unicodedata
from collections import defaultdict

import pymupdf
from bs4 import BeautifulSoup
from runtime import ROOT

samples = json.loads((ROOT / "reference/audit_pages.json").read_text())


def words(text):
    text = BeautifulSoup(text, "html.parser").get_text(" ")
    text = re.sub(r"!\[[\w+]+\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"(\w)[\-\u2010]\s*\n\s*(\w)", r"\1\2", text)
    return re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", text).casefold())


def grams(text):
    w = words(text)
    return {tuple(w[i : i + 5]) for i in range(len(w) - 4)}


def html_walk(b):
    return b.get("html", "") + "\n" + "\n".join(html_walk(c) for c in b.get("children") or [])


rows = []
for key, pages in samples.items():
    d = pymupdf.open(ROOT / "corpus" / f"{key}.pdf")
    out = ROOT / "results" / key
    methods = {}
    j = json.loads((out / "docling_default.document.json").read_text())
    by = defaultdict(list)
    for t in j["texts"]:
        for p in t["prov"]:
            by[p["page_no"]].append(t["text"])
    for t in j["tables"]:
        for p in t["prov"]:
            by[p["page_no"]].extend(c.get("text", "") for c in t["data"].get("table_cells", []))
    methods["docling_no_tables"] = {p: "\n".join(v) for p, v in by.items()}
    j = json.loads((out / "marker.document.json").read_text())
    methods["marker"] = {i: html_walk(p) for i, p in enumerate(j["children"], 1)}
    j = json.loads((out / "pymupdf4llm.chunks.json").read_text())
    methods["pymupdf4llm"] = {p["metadata"]["page_number"]: p["text"] for p in j}
    if (out / "lighton_mlx").is_dir():
        methods["lighton_mlx"] = {
            int(p.stem): json.loads(p.read_text())["text"] for p in (out / "lighton_mlx").glob("*.json")
        }
    for method in ["lighton4b_mlx", "chandra2_mlx", "mineru_pro_mlx"]:
        if (out / f"{method}.headings.json").exists():
            methods[method] = {
                int(p.stem): json.loads(p.read_text()).get("text", "") for p in (out / method).glob("*.json")
            }
    if (out / "mistral_ocr41.document.json").exists():
        j = json.loads((out / "mistral_ocr41.document.json").read_text())
        methods["mistral_ocr41"] = {p["index"] + 1: p["markdown"] for p in j["pages"]}
    if (out / "azure_layout.document.json").exists():
        j = json.loads((out / "azure_layout.document.json").read_text())["analyzeResult"]
        methods["azure_layout"] = {
            p["pageNumber"]: "\n".join(
                j["content"][s["offset"] : s["offset"] + s["length"]] for s in p["spans"]
            )
            for p in j["pages"]
        }
    if (out / "mineru_basic.document.json").exists():
        j = json.loads((out / "mineru_basic.document.json").read_text())

        def extract(b):
            if isinstance(b, str):
                return b
            if isinstance(b, list):
                return " ".join(extract(x) for x in b)
            if isinstance(b, dict):
                return " ".join(extract(b[k]) for k in ["text", "content", "blocks", "children"] if k in b)
            return ""

        methods["mineru_basic"] = {i: extract(p) for i, p in enumerate(j["pages"], 1)}
    if (out / "docling_tables.pages.json").exists():
        methods["docling_tables"] = {
            int(p): t for p, t in json.loads((out / "docling_tables.pages.json").read_text()).items()
        }
    for method, page_texts in methods.items():
        for pn in pages:
            if pn not in page_texts:
                continue
            native = d[pn - 1].get_text(sort=True)
            paragraphs = [b[4] for b in d[pn - 1].get_text("blocks") if b[6] == 0 and len(words(b[4])) >= 50]
            body = set().union(*(grams(p) for p in paragraphs)) if paragraphs else set()
            ref = grams(native)
            prediction = grams(page_texts[pn])
            rows.append(
                dict(
                    document=key,
                    page=pn,
                    method=method,
                    native_ngrams=len(ref),
                    retained=len(ref & prediction),
                    paragraph_ngrams=len(body),
                    paragraph_retained=len(body & prediction),
                )
            )
(ROOT / "results/text_retention.json").write_text(json.dumps(rows, indent=2))
for method in sorted({r["method"] for r in rows}):
    rs = [r for r in rows if r["method"] == method]
    a = sum(r["native_ngrams"] for r in rs)
    b = sum(r["paragraph_ngrams"] for r in rs)
    print(
        method,
        len(rs),
        "pages",
        "all",
        round(sum(r["retained"] for r in rs) / a, 4),
        "long blocks",
        round(sum(r["paragraph_retained"] for r in rs) / b, 4),
    )
