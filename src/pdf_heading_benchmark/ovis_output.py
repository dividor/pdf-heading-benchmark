"""OvisOCR3's documented Markdown cleanup, without heading repair.

Adapted from ATH-MaaS/OvisOCR3 README, revision 5b252386ba615bd464a5a26597560eaba87dae5c,
Apache-2.0. The upstream algorithm removes repetitive tails on every response.
"""


def clean_repeated_tail(text: str) -> str:
    n = len(text)
    if n < 8000:
        return text
    for unit_len in range(1, min(200, n - 1) + 1):
        if text[n - 1] != text[n - 1 - unit_len]:
            continue
        match_len, index = 1, n - 2
        while index >= unit_len and text[index] == text[index - unit_len]:
            match_len += 1
            index -= 1
        total_len = match_len + unit_len
        if total_len // unit_len >= 5 and total_len >= 100:
            return text[: n - total_len + unit_len] + text[n - total_len % unit_len :]
    return text


def document_markdown(raw: str) -> str:
    text = "\n\n".join(
        block for block in raw.strip().split("\n\n") if not block.strip().startswith('<img src="images/bbox_')
    )
    return clean_repeated_tail(text)
