# 03_glassdoor — scrape related reviews, group them

One job: get this company's Glassdoor interview reviews for related roles into `interviews.json`,
grouped A (same job, highest), B (adjacent, medium), C (the rest, low).

## Inputs
- Working (this run): `<case>/01_intake/intake.md` (company, role, `glassdoor_url`, related roles)
- Reference: `references/scope.md` (scope.json, when to filter), `references/schema.md` (output fields)
- Reference: `../../_shared/browser.md`, `../../_shared/agent-tiers.md`

Do NOT load: `02_research` outputs, other cases, `interviews.json` whole (query it with jq).

## Process
1. Find the company's interviews page (intake's `glassdoor_url`, or search
   "<company> glassdoor interview questions"); use the user's country domain.
2. `uv run tools/browser.py start <url>`. The sign-in before the research covered Glassdoor; if the
   page still shows a login or a Cloudflare check, send it to the user (`_shared/browser.md`).
3. `uv run tools/glassdoor.py probe <url>`: the count decides the scope (`references/scope.md`).
4. Write `scope.json`. Over the threshold, show the user the role filters and the A/B lists and wait
   for approval before scraping; under it, show them and go on.
5. `uv run tools/glassdoor.py scrape <case>/03_glassdoor/raw.json <url> [<url>...]` with the scope's urls.
6. `uv run tools/glassdoor.py normalize <raw> <scope> <case>/03_glassdoor/interviews.json`, then
   `roles <interviews.json>`. Add real titles that belong in A or B to `scope.json` (`haiku` agent when
   there are more than about 30 titles), and normalize again.
7. `uv run tools/glassdoor.py summary <case>/03_glassdoor/interviews.json <case>/03_glassdoor`.

If the company has no Glassdoor page, write `skipped.md` saying what was searched.

## Outputs
- `<case>/03_glassdoor/`: `scope.json`, `raw.json`, `interviews.json`, `stats.md`, `processes.md`
  (the last two are generated; never edit them, edit `scope.json` and rerun steps 6–7)

## Human check
Before a filtered scrape: the user approves `scope.json`. After: the user reads `stats.md` and moves any
misgrouped role between lists in `scope.json`.
