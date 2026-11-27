"""Keep notebook console output readable without discarding useful results."""


def long_streams(notebook: dict) -> list[int]:
    found = []
    for index, cell in enumerate(notebook.get("cells", [])):
        for output in cell.get("outputs", []):
            if output.get("output_type") != "stream":
                continue
            value = output.get("text", "")
            text = "".join(value) if isinstance(value, list) else value
            if len(text.splitlines()) > 40 or len(text) > 4000:
                found.append(index)
                break
    return found
