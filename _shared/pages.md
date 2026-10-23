# The pages the user reads

The user reads each stage's output as HTML, and edits the markdown. Three stages have a reading page:
`02_research/findings.md`, `04_question-check/question-bank.md` and `05_report/report.md`. Each
inference in them links to a why page that lays out what it rests on.

## Why pages
Every inference gets one: each `likely` or `speculative` finding, and each recommendation drawn from
the evidence. The stage that makes it writes it into `<case>/<stage>/why/claims.json`, a list of:

```json
{
  "slug": "no-ml-in-round-1",
  "confidence": "likely",
  "claim": "Expect no ML questions in Round 1.",
  "premises": [
    {
      "shows": "What this premise shows, in one sentence.",
      "quote": "the source's words, verbatim; join fragments with ' · ' or '…'",
      "source": "Prep kit · intake.md:145-147",
      "link": "01_intake/intake.md:145-147",
      "checked": true
    }
  ],
  "reasoning": ["How the premises add up, citing them as [1], [2]."],
  "against": ["What cuts against it.", {"quote": "…", "source": "…", "link": "…", "checked": true}],
  "settle": ["What would settle it."],
  "related": ["another-slug", "02_research/a-slug-in-another-stage"],
  "table": {"head": ["", "Ours", "Theirs"], "rows": [["…", "…", "…"]]}
}
```

- `slug`, `confidence`, `claim`, `premises` and `reasoning` are required; the rest are optional.
- `link` is a web address, or a path in the case with the lines the quote sits on. `tools/check.py`
  holds a case path to its lines, so cite every line the quote spans.
- `checked` is true only when you re-read the source yourself this run, not when a lane quoted it.
- Link the page from the markdown right after the claim: `([why](why/<slug>.html))`, or from another
  stage, `([why](../02_research/why/<slug>.html))`.

## Make and check the pages
At the end of each of those stages, and after the user edits one:

```bash
uv run tools/render.py <case>   # writes the .html, and prints a command to open each reading page
uv run tools/check.py <case>    # quotes still at their lines, line references in range, links resolve
```

Fix what `check.py` reports, at the source: the claim, the citation or the markdown. Then give the
user the commands `render.py` printed. They hold full paths, so they work from any folder.

## Markdown the pages understand
Headings, paragraphs, lists (nested by indenting), pipe tables, `>` quotes, fenced code with a
language, links, bare URLs, `**bold**` and `*italics*`. Write a finding's confidence after `— `, in
brackets, or as `**Confidence:** likely`, and it shows as a coloured label. Each `###` section shows as
a card, and the first `##` section as a highlighted summary.
