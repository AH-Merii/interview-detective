# Question bank format

One entry per question. Search for it before classifying: quote its distinctive phrases, and look on
LeetCode, HackerRank, system design primers, Kaggle, case-interview collections and the web.

```markdown
### Q<n>. <the question, verbatim>
- **Origin:** glassdoor A (id 105266860, 2026-08-20) · findings (<link>)
- **Round:** <the round it bears on: the next round, or a later one, such as `onsite`>
- **Kind:** coding | ml-concepts | system-design | data/case study | take-home | behavioural | other
- **Verdict:** standard | variant | company-specific | unsure
- **Closest public version:** <name and link>, or "none found"
- **Topics:** <2–5 tags, e.g. sliding window, model deployment, A/B testing>
- **Notes:** <one or two lines: what the variant changes, or what makes it company-specific>
```

- **standard**: the same problem exists publicly under a known name; link it.
- **variant**: a known problem with a twist; link the base problem and say what the twist is.
- **company-specific**: no close public version; say what was searched.
- **unsure**: the evidence does not settle it; say why (a `sonnet` agent then retries it).

LeetCode answers scripts with 403, so confirm a LeetCode problem's number, title and difficulty through
its GraphQL API:

```bash
curl -s https://leetcode.com/graphql -H 'Content-Type: application/json' \
  -d '{"query":"query{question(titleSlug:\"two-sum\"){questionFrontendId title difficulty}}"}'
```
