---
name: interview-detective
description: Prepare for a job interview by detective work. Asks what company, role and round, then researches in parallel (similar exercises on the web, the company's and employees' public GitHub, candidates' uploaded prep, creative leads), scrapes related Glassdoor interview reviews into priority-grouped JSON with the user logging in, checks whether each question is standard, and writes a sourced report with practice questions. Use when the user says they have an interview coming up, wants interview prep or intel on a company's interview, says "interview-detective", or wants to resume or check the status of a prep case.
---

# interview-detective

Detective work before a job interview: from what the user knows, find what the interview will likely
hold (Glassdoor reviews, public GitHub, candidates' prep, the open web) and leave a sourced report with
practice questions.

Built on ICM: folders carry sequencing, hierarchy carries context, files carry state. If something needs
explaining, it goes in that folder's CONTEXT.md.

## Where things live

The factory is this plugin, in `${CLAUDE_PLUGIN_ROOT}`. Paths below, and in every contract, are relative
to it unless they start with `<cases>`. Run tools by their full path, as in
`uv run ${CLAUDE_PLUGIN_ROOT}/tools/status.py`.

| Path | What it holds |
|---|---|
| `CONTEXT.md` | the pipeline on one screen |
| `stages/` | the stage contracts, in order |
| `_shared/` | rules every stage follows: agent tiers, evidence, the browser |
| `_templates/interview/` | the stamp a new case is copied from |
| `tools/` | browser, Glassdoor scraper, new case, status |
| `<cases>/<case>/` | one case per interview (product): `01_intake/` … `05_report/` outputs |
| `<cases>/log.md` | generated case list and status; rebuilt by `tools/status.py` |

`<cases>` is the user's cases folder, set by the setup wizard; `tools/status.py` prints where it is.

## First, every time

Run `uv run ${CLAUDE_PLUGIN_ROOT}/tools/status.py`. If it says setup hasn't run, stop and give the user
this command to run in a terminal (it asks questions, so not through Claude Code's `!`):

```bash
bash ${CLAUDE_PLUGIN_ROOT}/setup/wizard.sh
```

## Route by what just happened

| If | Go to | Then stop at |
|---|---|---|
| a new interview to prepare | `tools/new_case.sh <company> <role>`, then `stages/01_intake/CONTEXT.md` | user confirms `intake.md` |
| intake confirmed | `stages/02_research/` and `stages/03_glassdoor/`, at the same time | user reads `findings.md` and `stats.md` |
| research and Glassdoor read | `stages/04_question-check/CONTEXT.md` | user skims `question-bank.md` |
| question bank read | `stages/05_report/CONTEXT.md` | user reads `report.md` |
| asked for status | `tools/status.py` | report the table |
| resuming a case | `tools/status.py`; the Next column names the stage | that stage's human check |

For a new interview, ask for the company and role before anything else. Read only the contract of the
stage you are on.

## The one rule

Nothing moves to the next stage until the user has read the output of the last one. A case's stage
folders are edit surfaces: the next stage reads whatever the user left there.
