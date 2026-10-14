# Lane: company-github (tier: sonnet)

Find the company's public GitHub presence and what it says about the interview and the work.

- Find the organisation (or several: product orgs, research orgs, acquired companies). Use
  `gh search repos`, `gh api orgs/<org>/repos`, and links from the company's site.
- Look for: interview or hiring repos, take-home templates, coding-challenge starters, onboarding docs,
  engineering handbooks, style guides, CONTRIBUTING files, and job-related READMEs.
- Read the stack: languages, frameworks, infra (Dockerfiles, CI, Terraform), ML tooling, test
  conventions. What the team uses is what a practical exercise will likely use.
- Note activity: which repos are live, who the frequent committers are (handles only; the people lane
  takes it from there).

Use `gh` and the web; cite repo URLs and `path:line` links to files. Write to the output path you were
given, in the lane output format.
