# 02_research — parallel detective lanes

One job: find public evidence of what this interview will hold, one lane per kind of source, then
merge it into `findings.md`.

## Inputs
- Working (this run): `<case>/01_intake/intake.md`
- Reference: `references/lanes/*.md` (one brief per lane), `references/lane-output.md`
- Reference: `../../_shared/agent-tiers.md`, `../../_shared/evidence.md`, `../../_shared/browser.md`,
  `../../_shared/pages.md`

Do NOT load: `03_glassdoor` outputs (that stage runs beside this one), other cases.

## Process
1. Start one background agent per lane, all in the same turn, at the tier its brief names. Prompt each
   with only: its brief's path, the intake path, `references/lane-output.md`, and its output path
   `<case>/02_research/lanes/<lane>.md`.

   | Lane | Brief | Tier |
   |---|---|---|
   | exercises | `references/lanes/exercises.md` | `sonnet` |
   | company-github | `references/lanes/company-github.md` | `sonnet` |
   | candidate-prep | `references/lanes/candidate-prep.md` | `sonnet` |
   | people | `references/lanes/people.md` | `opus` |
   | wildcard | `references/lanes/wildcard.md` | `opus` |

2. While they run, work on `03_glassdoor` with the user.
3. When the lanes are back, collect every `## Blocked` entry, whatever the site. Start the browser on
   them and check each tab: sites signed in to before the research usually load. Have the user clear
   the rest in one login window (`_shared/browser.md`), then send one `haiku` reader per site; each
   appends its findings to the lane file that listed the page.
4. Write `findings.md` from the lane files: merge duplicates, keep each finding's source and confidence,
   order by how directly it speaks to this round. End with what was looked for and not found.
5. Check the findings the user will act on first-hand before they read them: the round's format and
   task, the interviewer, and every premise behind an inference. Re-read each source yourself (open the
   page, run the `gh` command, read the intake lines); correct what a lane got wrong, and mark what you
   re-read `checked`.
6. Write a why page for each inference into `why/claims.json`, and link it from `findings.md`
   (`../../_shared/pages.md`). Run `tools/render.py` and `tools/check.py`, and fix what the check reports.

## Outputs
- `<case>/02_research/lanes/<lane>.md`, one per lane
- `<case>/02_research/findings.md`, `findings.html`, and `why/claims.json` with a page per inference

## Human check
The user reads `findings.html` and deletes or corrects wrong leads in `findings.md`; 04 and 05 read
what is left. Render and check again after their edits.
