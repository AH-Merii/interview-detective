# Lane output format

Every lane writes one markdown file in this shape. Follow `_shared/evidence.md`.

```markdown
# <lane>: <company>, <role>

## Findings
- **<claim>** — <source URL or path:line> — <confirmed|likely|speculative> — <date if known>
  <one or two lines: what it tells us about the interview, and how directly>

## Exercises and questions found
- <the exercise or question, verbatim where possible> — <source> — <how it was used: take-home, live, prep>

## Blocked
- <URL> — <needs: login | captcha | paywall> — <what we expect to find there>

## Searched, nothing useful
- <query or place> — <one line why it came up empty>
```

Keep it under about 1,500 words. Leave a section out when it would be empty, except
"Searched, nothing useful", which shows the ground covered.
