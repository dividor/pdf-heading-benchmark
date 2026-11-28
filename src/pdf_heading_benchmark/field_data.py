"""Read the publisher's distinct leaderboard groups without mixing scorer versions."""

import hashlib
import re

from bs4 import BeautifulSoup
from markdown_it import MarkdownIt


def score(value: str) -> float:
    number = float(value)
    if not 0 <= number <= 100:
        raise ValueError(f"Score is outside 0-100: {value}")
    return number


def table_rows(table, layout: bool) -> list[dict]:
    records = []
    for tr in table.select("tbody tr"):
        cells = [cell.get_text().strip() for cell in tr.find_all("td")]
        expected = 7 if layout else 4
        if len(cells) != expected or cells[1] not in {"open", "closed"}:
            raise ValueError("Publisher table columns or weight categories changed")
        name = cells[0]
        records.append(
            {
                "name": name,
                "text": score(cells[3] if layout else cells[2]),
                "layout": score(cells[5]) if layout else None,
                "category": "hosted" if cells[1] == "closed" else "local",
                "retry": "†" in name,
                "annotation_contributor": "*" in name,
                "benchmark_vendor": "(Datalab)" in name,
            }
        )
    if not records:
        raise ValueError("Publisher table is empty")
    return records


def parse_source(source: str, revision: str, retrieved: str) -> dict:
    if re.fullmatch(r"[a-f0-9]{40}", revision) is None:
        raise ValueError("Use a full source commit, not a moving branch")
    soup = BeautifulSoup(MarkdownIt("commonmark").enable("table").render(source), "html.parser")
    groups = {}
    for heading, key, layout in (
        ("Leaderboard", "rows", True),
        ("Pending regrade", "pending", True),
        ("No layout output (no headline)", "text_only", False),
    ):
        node = soup.find(["h2", "h3"], string=heading)
        if node is None:
            raise ValueError(f"Publisher section is missing: {heading}")
        groups[key] = table_rows(node.find_next("table"), layout)
    version = re.search(r"Scorer:\*\* omni-parse-bench ([\d.]+)", source)
    pending = re.search(r"still graded by omni-parse-bench ([\d.]+)", source)
    if version is None or pending is None:
        raise ValueError("Publisher did not identify both scorer versions")
    return {
        "source": f"https://github.com/datalab-to/omni_parse_bench/blob/{revision}/README.md#leaderboard",
        "revision": revision,
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "retrieved": retrieved,
        "benchmark": "OmniParseBench " + version[1],
        "pending_benchmark": "OmniParseBench " + pending[1].rstrip("."),
        "selection": "All current text/layout and text-only rows; pending regrades excluded",
        **groups,
    }
