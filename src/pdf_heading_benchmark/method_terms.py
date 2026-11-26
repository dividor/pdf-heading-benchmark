"""Explain method vocabulary and link model names where readers encounter them."""

import re
from html import escape


def linked_text(text: str, technique: dict) -> str:
    terms = {
        alias: term for term in technique.get("terms", []) for alias in term.get("aliases", [term["name"]])
    }
    if not terms:
        return escape(text)
    pattern = r"(?<!\w)(" + "|".join(re.escape(a) for a in sorted(terms, key=len, reverse=True)) + r")(?!\w)"
    pieces = re.split(pattern, text)
    return "".join(
        (
            f'<a href="{escape(terms[piece]["url"], quote=True)}" target="_blank" '
            f'rel="noopener noreferrer" title="{escape(terms[piece]["description"], quote=True)}">'
            f"{escape(piece)}</a>"
            if index % 2
            else escape(piece)
        )
        for index, piece in enumerate(pieces)
    )


def explained_terms(technique: dict) -> str:
    items = "".join(
        f'<dt><a href="{escape(term["url"], quote=True)}" target="_blank" rel="noopener noreferrer">'
        f"{escape(term['name'])}</a></dt><dd>{escape(term['description'])}</dd>"
        for term in technique.get("terms", [])
    )
    return f'<section class="method-terms"><h3>Models and terms explained</h3><dl>{items}</dl></section>'
