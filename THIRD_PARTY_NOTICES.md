# Third-party notices

The repository code is MIT licensed. Quality-check structure and the notebook checker were adapted from [dividor/tiered-taxonomy-tagging](https://github.com/dividor/tiered-taxonomy-tagging), Copyright (c) 2026 Dividor, MIT. That license is retained in LICENSE.

WFP owns or licenses the source reports. The repo links to their public downloads and retains short heading annotations/predictions for evaluation; it does not redistribute full PDFs or full-page OCR outputs.

Parser packages and model weights retain their own terms. Links in the report point to the corresponding official repositories/model cards. In particular, PyMuPDF-family packages, Marker, and Chandra have licensing terms that may matter for commercial use. Chandra's model card specifies a modified OpenRAIL-M license with commercial-use conditions. Local $0 API costs do not imply unrestricted free commercial use.

The Popo and Chandra helper repositories are fetched at fixed commits into the external data directory; they are not copied into this repository. Their prompts, image preparation and overlap algorithms are used under their upstream licenses. Check each upstream license before using or distributing its code/weights. This file is an attribution and scope note, not a substitute for those licenses.

## OpenBMB OCR field overview

`docs/images/ocr-field-overview.png` and its report copy reproduce OpenBMB's “Efficiency vs. Performance of Open-Source OCR Models” without alteration. Source: [MiniCPM-OCR](https://github.com/OpenBMB/MiniCPM-OCR/blob/c21a3ca524263ef8166cb6d350864b10c3056b61/docs/minicpm_ocr_1dot0_en.md#evaluation), [Apache-2.0 license](https://github.com/OpenBMB/MiniCPM-OCR/blob/c21a3ca524263ef8166cb6d350864b10c3056b61/LICENSE). Copyright and attribution remain with OpenBMB. This figure is external benchmark evidence, not a result of the WFP experiment.

The new field-trial configurations use MiniCPM-OCR 1.0, Xiaomi-OCR-0, PaddleOCR-VL-1.6 and PP-DocLayoutV3 weights. Their pinned Hugging Face repositories are listed in `configs/field-candidates.json`; consult each model card and upstream license. We distribute benchmark code and compact predictions, not model weights. The MiniCPM SDK is an external runtime dependency.

A copy of the OpenBMB figure’s upstream license is included at [docs/images/OpenBMB-LICENSE.txt](docs/images/OpenBMB-LICENSE.txt).
