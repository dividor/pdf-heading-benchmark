"""Author H1-H6 tags, using only the chosen page sample, without gold labels."""

import json
import re
import time

import pdfplumber
from pdfplumber.structure import PDFStructTree
from pdfplumber.utils import extract_text
from runtime import ROOT


def headings(pdf, pages):
    chars = {n: pdf.pages[n - 1].chars for n in pages}
    result = []
    for element in PDFStructTree(pdf).find_all(re.compile(r"^H[1-6]$")):
        selected, locations = [], []
        for page, mcid in element.all_mcids():
            if page in chars:
                selected.extend(c for c in chars[page] if c.get("mcid") == mcid)
                locations.append(page)
        if selected:
            result.append(
                dict(page=min(locations), level=int(element.type[1:]), title=extract_text(selected))
            )
    return result


def main():
    for key, pages in json.loads((ROOT / "reference/audit_pages.json").read_text()).items():
        start = time.perf_counter()
        with pdfplumber.open(ROOT / "corpus" / f"{key}.pdf") as pdf:
            result = headings(pdf, pages)
        out = ROOT / "results" / key
        (out / "pdf_tags_audit_only.headings.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2)
        )
        (out / "pdf_tags_audit_only.run.json").write_text(
            json.dumps(dict(pages=len(pages), seconds=time.perf_counter() - start))
        )


if __name__ == "__main__":
    main()
