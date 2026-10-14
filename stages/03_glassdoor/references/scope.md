# Scope: what to scrape and how to group it

## How much to scrape
Glassdoor shows 5 interviews a page, and the scraper waits 3–6 s between pages, so each 100 interviews
take about 2 minutes. (Faculty.ai on 2026-10-14: 127 interviews, 26 pages.)

- **Up to 250 interviews:** scrape the unfiltered page; everything goes in, grouped A/B/C.
- **Over 250:** scrape only related roles. For each title in the intake's A and B lists, and close
  variants of them (Senior, Lead, ML/Machine Learning, Front End/Frontend), get a filtered URL:
  1. on the interviews tab, find the job-title filter box (`browser.py js` with
     `document.querySelectorAll('input')`), `click` it, `type` the title, `key enter`;
  2. read the result with `browser.py js 'location.href'`;
  3. `glassdoor.py probe <that url>`: its count must be lower than the unfiltered count, or the filter
     did not apply.

  The filtered URL form is not yet confirmed on a real run; record what worked here when it is.

## scope.json
```json
{
  "company": "Faculty.ai",
  "urls": ["https://www.glassdoor.co.uk/Interview/Faculty-ai-Interview-Questions-E1660422.htm"],
  "groups": {
    "A": {"priority": "highest", "roles": ["Machine Learning Engineer", "ML Engineer", "Software Engineer"]},
    "B": {"priority": "medium", "roles": ["Data Scientist", "Senior Data Scientist", "Cloud Engineer"]},
    "C": {"priority": "low", "default": true, "roles": []}
  }
}
```
- `urls`: every URL the scrape reads; filtered ones for a big company.
- `roles` match Glassdoor's titles exactly, ignoring case. Titles are free text, so one job appears
  under many spellings: list each one. Any title in no list lands in the group marked `default`.
- **A:** the same job as the target role, at any level (intern, senior, lead, fellow variants of it).
- **B:** adjacent jobs whose interviews share rounds with it (same discipline, neighbouring speciality,
  same platform or stack).
- **C:** everything else; kept for the stats, left out of `processes.md`.
- A generic title ("Associate", "Fellow") goes where the company uses it, if the intake or the
  reviews' text make that clear; say so in the stats review.
