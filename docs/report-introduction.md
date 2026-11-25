# Can local AI recover document headings?

Headings tell a search system what a passage is for: an executive summary may answer a user’s question; an acronyms list may not. We tested local tools on WFP evaluation reports to see whether they preserve both headings and their hierarchy.

## Results at a glance

**28 configurations · 4 WFP reports · 32 audited pages · 77 reference headings · Apple M4 Pro, 48 GB**

- **Highest score:** Qwen3.6-27B with visual memory gets **65/77** heading-level pairs right; **54 min 2 sec** for 32 pages. It receives extra PDF text, tags and document context.
- **Image-only alternative:** Chandra OCR 2 gets **53/77** right in **14 min 46 sec**. The three newer OCR trials did not beat its heading-level score.
- **OUR METHOD:** small trained CPU classifiers get **34/77** right with two extra headings. Fast, but the missing headings make this configuration unsuitable when coverage matters.

**Read the score as heading + page + level, all correct.** Joint F0.5 penalizes false headings and wrong levels, with more weight on precision. Check recall alongside it: a high score can still hide missed headings. These are exploratory results from one assistant’s annotations, without independent human review.

## Full configuration results

All runs are local. Select **i** for definitions, or **Method & predictions** for each configuration’s diagram, settings, code and heading-by-heading comparison. Times marked “Estimated” are scaled from longer runs; they are not measured 32-page runs.
