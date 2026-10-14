# interviews.json

Written by `tools/glassdoor.py normalize`; the field mapping lives there, in `normalize()`.

```json
{
  "company": "Faculty.ai",
  "source": ["<urls scraped>"],
  "scraped": "2026-10-14",
  "count": 127,
  "interviews": [
    {
      "id": 105266860,
      "role": "Software Engineer",
      "group": "A",
      "priority": "highest",
      "location": "Norway",
      "review_date": "2026-08-20",
      "interview_date": "2026-08",
      "outcome": "no_offer",
      "experience": "positive",
      "difficulty": "difficult",
      "how_obtained": "applied_online",
      "duration_days": 30,
      "process": "full text of the candidate's account",
      "questions": ["each question the candidate listed"],
      "helpful": 0,
      "employer_responses": []
    }
  ]
}
```

Values seen so far (Faculty.ai, 127 interviews):
- `outcome`: `accept_offer`, `no_offer`, `decline_offer`
- `experience`: `positive`, `neutral`, `negative`
- `difficulty`: `very_easy`, `easy`, `average`, `difficult`, or null
- `how_obtained`: `applied_online`, `recruiter`, `employee_referral`, `staffing_agency`, `college`,
  `other`, or null
- `interview_date` is month precision; null when the candidate left it blank.

Query examples:
```bash
jq '.interviews[] | select(.group=="A") | {role, review_date, questions}' interviews.json
jq '[.interviews[] | select(.group!="C") | .questions[]] | length' interviews.json
```
