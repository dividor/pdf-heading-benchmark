"""Strict structural decoding, with no semantic title or level repair."""

import json
import re


def parse(raw, pn):
    raw = raw.split("</think>")[-1].strip()
    fenced = re.findall(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if len(fenced) == 1:
        raw = fenced[0].strip()
    obj = json.loads(raw)
    heads = obj if isinstance(obj, list) else obj["headings"]
    if not isinstance(heads, list):
        raise ValueError("headings is not a list")
    for h in heads:
        if not isinstance(h, dict):
            raise ValueError("Heading must be an object")
        if type(h.get("level")) is not int or not 1 <= h["level"] <= 6 or not isinstance(h.get("title"), str):
            raise ValueError("Invalid heading schema")
    return [dict(page=pn, title=h["title"], level=h["level"]) for h in heads]
