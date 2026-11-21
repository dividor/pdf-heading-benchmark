"""Read author-provided H1-H6 tags across complete PDFs, without reference labels."""

import json
import re

import pdfplumber
from pdfplumber.structure import PDFStructTree
from pdfplumber.utils import extract_text
from runtime import ROOT

for item in json.loads((ROOT / "corpus/manifest.json").read_text()):
    out = ROOT / "results" / item["id"] / "pdf_tags_full_context.json"
    if out.exists():
        continue
    with pdfplumber.open(item["path"]) as pdf:
        tree = PDFStructTree(pdf)
        heads = []
        for el in tree.find_all(re.compile(r"^H[1-6]$")):
            selected = []
            page_numbers = []
            for n, mcid in el.all_mcids():
                if n is None:
                    continue
                selected.extend(c for c in pdf.pages[n - 1].chars if c.get("mcid") == mcid)
                page_numbers.append(n)
            if selected:
                heads.append(
                    {"page": min(page_numbers), "level": int(el.type[1:]), "title": extract_text(selected)}
                )
        out.write_text(json.dumps(heads, ensure_ascii=False, indent=2))
        print(item["id"], len(heads), flush=True)
