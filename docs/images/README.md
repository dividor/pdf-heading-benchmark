# Heading classification illustrations

These original explanatory diagrams use invented text. They are not WFP report quotations, model outputs or additional benchmark results.

- `heading-classification.svg` / `.png`: correct section, subsection and body-text labels compared with an incorrect hierarchy.
- `heading-relevance.svg` / `.png`: why a summary passage and an acronyms entry can have different relevance to a user's question.

The SVGs are editable source artwork. The PNGs are 1920 × 1040 exports for the README and article. Both are covered by this repository's MIT license. Text alternatives and captions accompany the embedded images.

Regenerate the PNGs from the SVGs using the project's existing PyMuPDF dependency, from the repository root:

```bash
uv run python - <<'PY'
from pathlib import Path
import pymupdf

for source in Path('docs/images').glob('*.svg'):
    with pymupdf.open(source) as vector:
        pdf_bytes = vector.convert_to_pdf()
    with pymupdf.open(stream=pdf_bytes, filetype='pdf') as document:
        document[0].get_pixmap(matrix=pymupdf.Matrix(1.6, 1.6)).save(source.with_suffix('.png'))
PY
```
