"""Full-document hosted comparisons; preserves raw responses and page provenance."""

import argparse
import base64
import json
import os
import re
import time
from pathlib import Path

import requests
from runtime import ROOT


def markdown_headings(text, page):
    result = []
    fenced = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*$", line)
        if m:
            result.append(dict(page=page, level=len(m[1]), title=m[2]))
    return result


def load_env(path):
    if not path:
        return
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.removeprefix("export ").partition("=")
        if sep:
            os.environ[key.strip()] = value.strip().strip("\"'")


def request_mistral(item, endpoint, key, rawpath):
    payload = dict(
        model="mistral-ocr-4-1",
        document={
            "type": "document_url",
            "document_url": "data:application/pdf;base64,"
            + base64.b64encode(Path(item["path"]).read_bytes()).decode(),
        },
        include_image_base64=False,
        extract_header=True,
        extract_footer=True,
        include_blocks=True,
    )
    response = requests.post(endpoint, headers={"Authorization": "Bearer " + key}, json=payload, timeout=600)
    if not response.ok:
        raise SystemExit(f"Mistral request failed: HTTP {response.status_code}; no automatic paid retry.")
    raw = response.json()
    rawpath.write_text(json.dumps(raw, ensure_ascii=False, indent=2))
    return raw


def request_azure(item, endpoint, key, rawpath, out, method):
    headers = {"Ocp-Apim-Subscription-Key": key, "Content-Type": "application/pdf"}
    jobfile = out / f"{method}.job.json"
    if jobfile.exists():
        job = json.loads(jobfile.read_text())["operation_url"]
    else:
        response = requests.post(
            endpoint + "/documentintelligence/documentModels/prebuilt-layout:analyze",
            params={
                "api-version": "2024-11-30",
                "outputContentFormat": "markdown",
                "stringIndexType": "unicodeCodePoint",
            },
            headers=headers,
            data=Path(item["path"]).read_bytes(),
            timeout=120,
        )
        if response.status_code != 202:
            raise SystemExit(f"Azure request failed: HTTP {response.status_code}; no automatic paid retry.")
        job = response.headers["Operation-Location"]
        jobfile.write_text(json.dumps({"operation_url": job}))
    for _attempt in range(240):
        response = requests.get(job, headers={"Ocp-Apim-Subscription-Key": key}, timeout=60)
        response.raise_for_status()
        raw = response.json()
        if raw.get("status") == "succeeded":
            break
        if raw.get("status") == "failed":
            raise SystemExit("Azure analysis failed; inspect provider job.")
        time.sleep(5)
    else:
        raise SystemExit("Azure job still pending; retained job reference for resume.")
    rawpath.write_text(json.dumps(raw, ensure_ascii=False, indent=2))
    return raw


def decode(raw, provider):
    headings = []
    if provider == "mistral":
        for page in raw["pages"]:
            headings.extend(markdown_headings(page["markdown"], page["index"] + 1))
        text = "\n\n".join(p["markdown"] for p in raw["pages"])
        n = len(raw["pages"])
    else:
        result = raw["analyzeResult"]
        text = result["content"]
        n = len(result["pages"])
        for para in result.get("paragraphs", []):
            if para.get("role") not in ("title", "sectionHeading"):
                continue
            regions = para.get("boundingRegions", [])
            if not regions:
                continue
            pn = regions[0]["pageNumber"]
            offset = para["spans"][0]["offset"]
            begin = text.rfind("\n", 0, offset) + 1
            end = text.find("\n", offset)
            line = text[begin : end if end >= 0 else len(text)]
            m = re.match(r"^\s*(#+)\s+", line)
            headings.append(dict(page=pn, title=para["content"], level=len(m[1]) if m else None))
    return headings, text, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("provider", choices=["mistral", "azure"])
    ap.add_argument("--env-file")
    args = ap.parse_args()
    load_env(args.env_file)
    if args.provider == "mistral":
        key = os.environ.get("MISTRAL_API_KEY")
        endpoint = "https://api.mistral.ai/v1/ocr"
        if not key:
            raise SystemExit("Missing MISTRAL_API_KEY; no requests made.")
        method = "mistral_ocr41"
    else:
        key = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        endpoint = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", "").rstrip("/")
        if not key or not endpoint:
            raise SystemExit("Missing Azure endpoint/key; no requests made.")
        if not endpoint.startswith("https://"):
            raise SystemExit("Azure endpoint must use HTTPS")
        method = "azure_layout"
    for item in json.loads((ROOT / "corpus/manifest.json").read_text()):
        out = ROOT / "results" / item["id"]
        rawpath = out / f"{method}.document.json"
        reused = rawpath.exists()
        start = time.perf_counter()
        if rawpath.exists():
            raw = json.loads(rawpath.read_text())
        elif args.provider == "mistral":
            raw = request_mistral(item, endpoint, key, rawpath)
        else:
            raw = request_azure(item, endpoint, key, rawpath, out, method)
        headings, text, n = decode(raw, args.provider)
        (out / f"{method}.md").write_text(text)
        (out / f"{method}.headings.json").write_text(json.dumps(headings, ensure_ascii=False, indent=2))
        runpath = out / f"{method}.run.json"
        elapsed = (
            json.loads(runpath.read_text())["seconds"]
            if reused and runpath.exists()
            else time.perf_counter() - start
        )
        runpath.write_text(
            json.dumps(
                dict(
                    pages=n,
                    seconds=elapsed,
                    source="full original PDF",
                    provider=args.provider,
                    usage=raw.get("usage_info"),
                    estimated_api_cost_usd=n * (0.004 if args.provider == "mistral" else 0.010),
                    cost_basis="published standard rate; Azure provisional regional estimate; not invoice",
                ),
                indent=2,
            )
        )
        print("DONE", method, item["id"], n, len(headings), flush=True)


if __name__ == "__main__":
    main()
