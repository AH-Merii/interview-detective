# 05_report — summary, findings, practice

One job: write `report.md`, the one file the user preps from.

## Inputs
- Working (this run): `<case>/01_intake/intake.md`
- Working (this run): `<case>/02_research/findings.md`
- Working (this run): `<case>/03_glassdoor/stats.md` (not `processes.md`: 04 already pulled its questions)
- Working (this run): `<case>/04_question-check/question-bank.md`
- Reference: `references/report-template.md`, `../../_shared/evidence.md`, `../../_shared/pages.md`

Do NOT load: lane files, batches, `interviews.json`, `raw.json`, other cases.

## Process
1. Start one `opus` agent with the input paths, the template, the list of why pages in `02_research/why/`
   and `04_question-check/why/` (each page's slug, confidence and claim, from its `claims.json`) and the
   output path. Have it return the report as text, and save it to `report.md` yourself: Claude Code
   refuses report files written by subagents.
2. Read it against the inputs: every claim carries a source from them; no new facts appear. A `sonnet`
   agent can check each `path:line` against the lines it cites; give it the report and the inputs.
3. Run `tools/render.py` and `tools/check.py` (`../../_shared/pages.md`), and fix what the check reports.
4. Tell the user where it is, with the summary's first lines and the commands `render.py` printed.

## Outputs
- `<case>/05_report/report.md`, `report.html`

## Human check
The user reads `report.html`. If something is wrong, fix it at its source (findings, question bank,
scope) and rerun this stage, so the report stays derived from its inputs.
