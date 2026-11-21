"""Boundary cases that previously made visually plausible outputs misleading."""

import pytest
from decode_chandra import chandra_headings
from decode_qwen import parse
from parse_lighton import decode
from run_hosted_ocr import decode as decode_hosted
from run_hosted_ocr import markdown_headings


@pytest.mark.parametrize(
    "raw",
    [
        '[{"title":"A","level":2}]',
        '{"headings":[{"title":"A","level":2}]}',
        'Here is the JSON:\n```json\n[{"title":"A","level":2}]\n```',
    ],
)
def test_qwen_structural_wrappers(raw):
    assert parse(raw, 7) == [dict(title="A", level=2, page=7)]


@pytest.mark.parametrize(
    "raw",
    [
        '[{"title":"A","level":true}]',
        '[{"title":"A","level":"2"}]',
        '[{"title":"A","level":7}]',
        "[42]",
        '{"headings":{}}',
        "nonsense",
    ],
)
def test_qwen_does_not_repair_bad_values(raw):
    with pytest.raises((ValueError, TypeError)):
        parse(raw, 1)


def test_lighton_continuation_and_nonheading_gap():
    result = decode(
        "![title](0,0,100,50) ## First\n![title+](0,50,100,100) part\n"
        "![text](0,100,100,120) prose\n![title+](0,120,100,150) Second",
        3,
    )
    assert [(h["title"], h["level"]) for h in result] == [("First part", 2), ("Second", None)]
    assert result[0]["bbox"] == [0, 0, 0.1, 0.1]


def test_chandra_no_duplicate_nested_heading():
    result = chandra_headings(
        '<div data-label="Section-Header"><h2>A</h2></div><div data-label="Section-Header">B</div>', 4
    )
    assert result == [dict(page=4, level=2, title="A"), dict(page=4, level=None, title="B")]


def test_markdown_fences_and_page_index():
    assert markdown_headings("```\n# Not a heading\n```\n## Real", 4) == [dict(page=4, level=2, title="Real")]
    result, _, count = decode_hosted({"pages": [{"index": 0, "markdown": "# A"}]}, "mistral")
    assert result[0]["page"] == count == 1


def test_azure_unicode_offsets_and_h7():
    text = "é\n####### Annex\n"
    raw = {
        "analyzeResult": {
            "content": text,
            "pages": [{}],
            "paragraphs": [
                {
                    "role": "sectionHeading",
                    "content": "Annex",
                    "spans": [{"offset": 10}],
                    "boundingRegions": [{"pageNumber": 5}],
                }
            ],
        }
    }
    heads, _, _ = decode_hosted(raw, "azure")
    assert heads == [dict(page=5, title="Annex", level=7)]
