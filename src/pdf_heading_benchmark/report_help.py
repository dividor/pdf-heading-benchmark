"""Column explanations and accessible information controls for the league table."""

from html import escape

COLUMN_DESCRIPTIONS = {
    "Configuration": [
        (
            "The exact parser, model and settings used for this measured run. Variants of the same "
            "model are separate configurations."
        ),
        (
            "Use the information button beside a configuration to see its diagram, parameters, "
            "training or tuning, limitations, and links to code and original sources."
        ),
    ],
    "Primary score: joint F0.5": [
        (
            "The primary ranking score rewards a heading only when its title matches on the correct "
            "PDF page and its H level is exactly right. Higher is better."
        ),
        (
            "Let C be correct title-and-level pairs, P all predicted headings and G reference "
            "headings. Joint F0.5 = 1.25C / (P + 0.25G). It emphasizes precision more than recall. "
            "Extra headings and wrong levels reduce the score; missing headings also count against "
            "it. Empty output scores zero."
        ),
        "The table is sorted by this score. There is no separate PASS/FAIL qualification gate.",
    ],
    "Joint precision": [
        "The fraction of all emitted headings with the correct title, PDF page and exact H level: "
        "C / P. A wrong level, an absent level or an extra heading counts against precision.",
        "For MinerU basic, 31 of 68 predictions have the correct heading and level: 45.6%. "
        "Matching 66 genuine titles is insufficient because 35 have the wrong level.",
        "The count beside the percentage is correct heading-level pairs / all predictions. "
        "No predictions gives zero precision by this benchmark's convention.",
    ],
    "Method / code": [
        (
            "A summary of the actual execution path: inputs, model or parser, settings and processing "
            "scope. Select the method link to open its detailed diagram and code/source links."
        ),
        (
            "The same model can produce different results with different inputs or settings. These "
            "results describe the recorded configurations, not every possible use of the underlying "
            "package."
        ),
    ],
    "Status": [
        "Whether the benchmark run completed. This table includes completed local configurations only.",
        ("Completed does not mean that the configuration is accurate or supplies every required output."),
    ],
    "Joint recall": [
        (
            "The count and percentage of all 77 reference headings recovered on the correct page with "
            "the exact H level: C / G. This is joint recall, not the primary score."
        ),
        (
            "Missing headings and wrong levels reduce this percentage. Extra predictions do not "
            "reduce it directly, which is why joint F0.5 is used for ranking. An absent level earns "
            "no joint credit."
        ),
    ],
    "Headings recovered": [
        (
            "The count and percentage of all 77 reference titles matched on the correct PDF page, "
            "regardless of level: M / G."
        ),
        (
            "Matching normalizes title text, uses one-to-one assignment and requires at least 90% "
            "title similarity on the same page. It tolerates small text differences; it is not a "
            "character-perfect transcription test."
        ),
    ],
    "False headings": [
        (
            "Predictions on audited pages that do not match a reference heading title on that page: P "
            "minus M. Lower is better."
        ),
        (
            "A genuine heading with the wrong level is not included in this extra-heading count, but "
            "it does count as an error in joint F0.5. Counts cover the 32 audit pages, not every page "
            "parsed."
        ),
    ],
    "Native prose retention": [
        (
            "The fraction of five-word sequences from longer native PDF text blocks retained in "
            "extracted text on the audit pages. Higher means more of this reference prose survived "
            "extraction."
        ),
        (
            "This is a limited proxy, not a measure of reading order, table accuracy, semantic "
            "accuracy or downstream search quality. A dash means unavailable or not evaluated, not "
            "zero."
        ),
    ],
    "Measured time": [
        (
            "Observed processing time and the scope of that run. Some methods processed all 523 "
            "pages; others processed the 32 audit pages or only a hierarchy stage."
        ),
        (
            "Timings were recorded on a shared 48 GB Apple M4 Pro and are not a controlled speed "
            "benchmark. Qwen and Popo hierarchy times exclude upstream extraction. Exact inclusions "
            "and exclusions are described in each method's details."
        ),
        (
            "These are local runs. Hardware, electricity, setup, review and licensing costs were not "
            "measured in dollars."
        ),
    ],
}


def info_button(soup, target: str, label: str):
    button = soup.new_tag(
        "button",
        attrs={
            "type": "button",
            "class": "info-button",
            "data-technique": target,
            "aria-haspopup": "dialog",
            "aria-controls": target,
            "aria-label": "About " + label,
            "title": "About " + label,
        },
    )
    icon = soup.new_tag("span", attrs={"aria-hidden": "true"})
    icon.string = "i"
    button.append(icon)
    return button


def column_help(soup, results) -> str:
    panels = []
    for index, header in enumerate(results.find_all("th")):
        label = header.get_text()
        target = f"column-help-{index}"
        header.append(" ")
        header.append(info_button(soup, target, label))
        paragraphs = "".join(f"<p>{escape(p)}</p>" for p in COLUMN_DESCRIPTIONS[label])
        panels.append(
            f'<dialog id="{target}" aria-labelledby="title-{target}" '
            'class="technique-dialog column-dialog"><div class="technique-shell">'
            '<header class="technique-header">'
            f'<h2 id="title-{target}" tabindex="-1">{escape(label)}</h2>'
            '<button type="button" class="technique-close" aria-label="Close column description">'
            'Close <span aria-hidden="true">&times;</span></button></header>'
            f"{paragraphs}</div></dialog>"
        )
    return "".join(panels)
