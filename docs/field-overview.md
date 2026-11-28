# Reproduce the OCR field chart

The report has one field chart. It shows the 39 OmniParseBench 1.8.0 systems with layout scores strictly above 70. Eleven systems without layout scores, four scoring 70 or less, and two awaiting rescoring from version 1.5 remain in the source snapshot but are not plotted.

These are Datalab's published results, not our WFP test or the separate OmniDocBench benchmark. Teal identifies eight models or tools also tested in our WFP study; their configurations differ. Purple squares show hosted services and gray circles show other open models and tools.

Every point and visible model name opens a dialog with its pipeline, settings and source code. On a phone, use the model selector or scroll the chart horizontally. Labels are placed without overlapping other labels or markers, giving priority to study models and hosted services. Hovering or focusing a name highlights its connecting line and brings its marker to the front. Hosted squares draw above open-model circles so crowded service markers remain visible. Scores and coordinates do not move. The PNG uses the same labels and coordinates.

## Download the pinned source and rebuild

From the repository’s installed core environment:

```bash
uv run python scripts/update_field_overview.py
uv run python scripts/field_overview.py
uv run pdf-headings report
```

The downloader uses the exact upstream Git commit and README checksum in `configs/field-overview-source.json`. It fails if the downloaded source differs. It makes no parsing API calls. `--source /path/to/saved-README.md` verifies and imports an already downloaded copy. Ordinary report generation uses the committed JSON and works offline.

`configs/field-overview.json` preserves publisher names, scores, access categories and the retry, vendor and test-authoring markers. The SVG and PNG are written to `docs/images/ocr-text-layout.*`; the HTML embeds its own interactive chart, and the Markdown report links the PNG. No layout score is imputed and no table-extraction score is plotted.

To update the benchmark later, inspect the publisher’s scoring changes, set a new commit, checksum and retrieval date, then rerun these commands and the tests. Do not combine old and new scoring groups. Exact API versions and configuration details belong to the publisher’s run notes; a leaderboard name alone does not identify the configuration we will test on WFP reports.

[Source and run notes](https://github.com/datalab-to/omni_parse_bench/blob/65cc5b63f7f7f7e126416558b03bd107a417ac64/README.md#leaderboard).

`configs/field-model-details.json` records each displayed system’s adapter, settings, model link and exact study-method mapping. Details come from the pinned upstream adapter code and run notes. Adapter defaults are not claimed to be a complete raw run manifest. The study highlight matches a model or tool, not identical weights, hardware or options.
