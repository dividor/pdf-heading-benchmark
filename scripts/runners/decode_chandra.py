"""Decode the upstream Chandra layout HTML without repairing heading levels."""

import re

from bs4 import BeautifulSoup


def chandra_headings(raw, page):
    soup = BeautifulSoup(raw, "html.parser")
    headings = []
    for element in soup.find_all(re.compile(r"^h[1-6]$")):
        headings.append(dict(page=page, level=int(element.name[1:]), title=element.get_text(" ", strip=True)))
    for element in soup.find_all(attrs={"data-label": "Section-Header"}):
        if not element.find(re.compile(r"^h[1-6]$")):
            headings.append(dict(page=page, level=None, title=element.get_text(" ", strip=True)))
    return headings
