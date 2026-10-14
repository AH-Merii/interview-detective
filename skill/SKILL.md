---
name: interview-detective
description: Prepare for a job interview by detective work. Asks what company, role and round, then researches in parallel (similar exercises on the web, the company's and employees' public GitHub, candidates' uploaded prep, creative leads), scrapes related Glassdoor interview reviews into priority-grouped JSON with the user logging in, checks whether each question is standard, and writes a sourced report with practice questions. Use when the user says they have an interview coming up, wants interview prep or intel on a company's interview, says "interview-detective", or wants to resume or check the status of a prep case.
---

# interview-detective

The work lives in an ICM workspace: the repository this skill's folder belongs to. The skill folder is a
symlink to the repo's `skill/`, so find the repo with `dirname "$(realpath <this skill's base directory>)"`.
Run every tool from there.

1. Read the repo's `CLAUDE.md` and follow its routing table.
2. For a new interview, start at stage 01: ask for the company and role before anything else.
3. To resume or report status, run `uv run tools/status.py`.

Every stage's contract is in `stages/NN_*/CONTEXT.md`; read only the one you are on.
