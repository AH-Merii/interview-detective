# 05_report — summary, findings, practice

One job: write `report.md`, the one file the user preps from.

## Inputs
- Working (this run): `<case>/01_intake/intake.md`
- Working (this run): `<case>/02_research/findings.md`
- Working (this run): `<case>/03_glassdoor/stats.md` (not `processes.md`: 04 already pulled its questions)
- Working (this run): `<case>/04_question-check/question-bank.md`
- Reference: `references/report-template.md`, `../../_shared/evidence.md`

Do NOT load: lane files, batches, `interviews.json`, `raw.json`, other cases.

## Process
1. Start one `opus` agent with the input paths, the template and the output path; it writes the report.
2. Read it against the inputs: every claim carries a source from them; no new facts appear.
3. Tell the user where it is, with the summary's first lines.

## Outputs
- `<case>/05_report/report.md`

## Human check
The user reads the report. If something is wrong, fix it at its source (findings, question bank,
scope) and rerun this stage, so the report stays derived from its inputs.
