"""Readable heading lists preserve native levels and physical PDF page numbers."""

from pathlib import Path


def write_heading_list(path: Path, headings: list[dict], method: str) -> None:
    lines = [f"# {method}: predicted headings", "", "Native predictions, without corrections.", ""]
    for heading in headings:
        level, page = heading["level"], heading["page"]
        indent = "  " * (level - 1) if level is not None else ""
        label = f"H{level}" if level is not None else "Level not supplied"
        location = f"PDF page {page}" if page is not None else "Page not supplied"
        title = " ".join(heading["title"].splitlines())
        lines.append(f"{indent}- {label} · {location} · {title}")
    path.write_text("\n".join(lines) + "\n")
