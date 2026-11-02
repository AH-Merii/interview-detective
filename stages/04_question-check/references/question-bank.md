# Question bank format

One entry per question. Search for it before classifying: quote its distinctive phrases, and look on
LeetCode, HackerRank, system design primers, Kaggle, case-interview collections and the web.

```markdown
### Q<n>. <the question, verbatim>
- **Priority:** 1 | 2 | 3 | 4 — <one line: why this tier>
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

## Priority
Set when the batches are merged (the contract's step 4); batch agents leave the line out. It ranks how
much an item matters for the next round, from three things:
- how likely it is to come up there: how directly, how recently and how often it is reported, or how
  firmly it follows from the invite;
- how much it weighs in what the round is said to assess (the invite, the recruiter's hints);
- how much it shows the seniority the user is aiming for (the intake).

| Priority | Meaning |
|---|---|
| 1, decides the round | near certain to come up, and central to what is assessed; a handful at most |
| 2, likely follow-ups | what probes or extends a priority-1 item, and what the panel is likely to dig into |
| 3, worth preparing | plausible if the round goes another way: other reported questions and their variants |
| 4, lower | unlikely in the next round, or for a later round |

The bank has a section per priority, `## Priority 1: decides the round` and so on, and numbers its items
in that order, so Q1 is the one to practise first.

LeetCode answers scripts with 403, so confirm a LeetCode problem's number, title and difficulty through
its GraphQL API:

```bash
curl -s https://leetcode.com/graphql -H 'Content-Type: application/json' \
  -d '{"query":"query{question(titleSlug:\"two-sum\"){questionFrontendId title difficulty}}"}'
```
