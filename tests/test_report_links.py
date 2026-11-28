"""Published method links must open the code readers are instructed to clone."""

import re
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup

from pdf_heading_benchmark.io import REPO


def test_report_repository_links_use_the_documented_checkout_and_existing_paths():
    prefix = "https://github.com/dividor/pdf-heading-benchmark/"
    branch = "codex/full-method-verification/"
    soup = BeautifulSoup((REPO / "outputs/report/index.html").read_text(), "html.parser")
    urls = {a["href"] for a in soup.select("a[href]") if a["href"].startswith(prefix)}
    assert len(urls) > 30
    for url in urls:
        suffix = url.removeprefix(prefix)
        if suffix.startswith(("blob/", "tree/")):
            reference = suffix.split("/", 1)[1]
            if reference.startswith(branch):
                relative = reference.removeprefix(branch)
            else:
                revision, relative = reference.split("/", 1)
                assert re.fullmatch(r"[0-9a-f]{7,40}", revision), url
            path = unquote(urlsplit(relative).path)
            assert (REPO / path).exists(), url
    for link in soup.select("table.league-table tbody tr td:nth-child(6) a"):
        assert link["href"].startswith(prefix + "blob/" + branch)
    assert f"git clone --branch {branch.rstrip('/')} " in (REPO / "README.md").read_text()
