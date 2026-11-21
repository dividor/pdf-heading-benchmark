# Repository instructions

Work only in this repository for this project. Do not commit benchmark code to another checkout.

Follow CONTRIBUTING.md. Keep core code in src/pdf_heading_benchmark, backend-specific optional imports in scripts/runners, and all downloaded PDFs/models/raw outputs outside Git. Published labels and audit predictions are intentionally committed for offline verification.

Do not silently repair heading values, invent missing scores, use per-document correction rules, or describe sampled-page results as full-document accuracy. Do not call paid APIs during tests or routine report generation. Changing a prompt/model/configuration requires a fresh run directory and explicit provenance.

Run all pre-commit hooks and pytest. Regenerate both report formats after data/method edits. No suppression comments or ignored checks to get a change through. Blog drafts stay in ignored blog/ and are never published without the user's request.
