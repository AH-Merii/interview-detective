# interview-detective — the pipeline

Ask what the user knows, investigate in parallel, check every question found, write the report.

`<case>` is `<cases>/<company>-<role>-<YYYY-MM>/`, in the user's cases folder. Contracts live in `stages/NN_*/CONTEXT.md`;
outputs land in `<case>/NN_*/`.

| Stage | Job | Input | Output | Human check |
|---|---|---|---|---|
| `01_intake` | ask the user what they know | the user | `intake.md` (`confirmed: true`) | user confirms it |
| `02_research` | parallel detective lanes | 01 | `lanes/*.md`, `findings.md` | user strikes wrong leads |
| `03_glassdoor` | scrape related reviews, group A/B/C | 01 | `scope.json`, `interviews.json`, `stats.md`, `processes.md` | user approves scope before a big scrape |
| `04_question-check` | is each question standard? | 01, 02, 03 | `question-bank.md` | user skims the bank |
| `05_report` | summary, findings, practice | 01–04 | `report.md` | user reads it |

02 and 03 depend only on 01, so they run at the same time: start the 02 lanes in the background, then
work through 03 with the user (it needs their logins). Pages that 02's lanes find blocked are opened as
extra tabs in the same browser, so the user clears everything in one visit.

Factory (every run): `stages/`, `_shared/`, `tools/`. Product (each run): `<cases>/<case>/`.
Status is whatever exists: `tools/status.py` (rules in its docstring).
