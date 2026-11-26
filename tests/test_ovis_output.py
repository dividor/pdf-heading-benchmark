from pdf_heading_benchmark.ovis_output import clean_repeated_tail, document_markdown


def test_ovis_preserves_heading_levels_and_filters_generated_crop_tags():
    assert (
        document_markdown('  ### Methods\n\n<img src="images/bbox_1_2_3_4.jpg" />\n\nBody  ')
        == "### Methods\n\nBody"
    )


def test_ovis_cleanup_uses_upstream_length_and_repetition_thresholds():
    assert clean_repeated_tail("abc" * 200) == "abc" * 200
    assert clean_repeated_tail("Start\n" + "abc" * 3000) == "Start\nabc"
    ordinary = "".join(str(n) + "\n" for n in range(3000))
    assert clean_repeated_tail(ordinary) == ordinary
