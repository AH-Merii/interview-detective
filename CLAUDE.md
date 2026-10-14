# interview-detective

Detective work before a job interview: from what the user knows, find what the interview will likely
hold (Glassdoor reviews, public GitHub, candidates' prep, the open web) and leave a sourced report with
practice questions.

Built on ICM: folders carry sequencing, hierarchy carries context, files carry state. If something needs
explaining, it goes in that folder's CONTEXT.md.

## Where things live

| Folder | What it holds |
|---|---|
| `stages/` | the pipeline contracts (factory), in order; [CONTEXT.md](CONTEXT.md) shows it on one screen |
| `interviews/<case>/` | one case per interview (product): `01_intake/` … `05_report/` outputs |
| `_shared/` | rules every stage follows: agent tiers, evidence, the browser |
| `_templates/interview/` | the stamp a new case is copied from |
| `_index/log.md` | generated case list and status; rebuild with `uv run tools/status.py` |
| `tools/` | browser, Glassdoor scraper, new case, status |
| `skill/` | the `/interview-detective` skill, which routes here |
| `_assets/` | logo and logo concepts |

## Route by what just happened

| If | Go to | Then stop at |
|---|---|---|
| a new interview to prepare | `tools/new_case.sh <company> <role>`, then `stages/01_intake/CONTEXT.md` | user confirms `intake.md` |
| intake confirmed | `stages/02_research/` and `stages/03_glassdoor/`, at the same time | user reads `findings.md` and `stats.md` |
| research and Glassdoor read | `stages/04_question-check/CONTEXT.md` | user skims `question-bank.md` |
| question bank read | `stages/05_report/CONTEXT.md` | user reads `report.md` |
| asked for status | `uv run tools/status.py` | report the table |
| resuming a case | `uv run tools/status.py`; the Next column names the stage | that stage's human check |

## The one rule

Nothing moves to the next stage until the user has read the output of the last one. A case's stage
folders are edit surfaces: the next stage reads whatever the user left there.
