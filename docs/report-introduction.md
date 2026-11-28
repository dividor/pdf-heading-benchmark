# Can local AI recover document headings?

Headings tell a search system what a passage is for: an executive summary may answer a user’s question; an acronyms list may not. We tested local tools on WFP evaluation reports to see whether they preserve both headings and their hierarchy.

## Results at a glance

**33 configurations · 4 WFP reports · 32 audited pages · 77 reference headings · Apple M4 Pro, 48 GB**

- **Highest score:** Qwen3.6-27B with visual memory gets **65/77** heading-level pairs right; **54 min 2 sec** for 32 pages. It receives extra PDF text, tags and document context.
- **Image-only alternative:** Chandra OCR 2 gets **53/77** right in **14 min 46 sec**. OvisOCR3 gets **36/77** right in **6 min 58 sec**.
- **OUR METHOD:** small trained CPU classifiers get **34/77** right with two extra headings. Fast, but the missing headings make this configuration unsuitable when coverage matters.

**Score = correct title, page and level.** F0.5 favors precision; recall shows what is missing. References are assistant annotations without independent review.

## Full configuration results

Select a row’s **i** for its exact model, steps, settings and predictions. **Estimated** times scale longer runs to 32 pages.
