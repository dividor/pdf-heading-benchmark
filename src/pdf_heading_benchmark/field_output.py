"""Read native Markdown heading levels without inferring or repairing hierarchy."""

from markdown_it import MarkdownIt


def markdown_headings(text: str, page: int) -> list[dict]:
    tokens = MarkdownIt("commonmark", {"html": True}).parse(text)
    return [
        dict(page=page, title=tokens[i + 1].content.strip(), level=int(token.tag[1:]))
        for i, token in enumerate(tokens)
        if token.type == "heading_open"
    ]
