# Evidence rules

Every file a stage writes follows these. A finding without a source is left out or marked `unverified`.

## A finding
- **Claim**: one sentence.
- **Source**: a URL, a `path:line`, or a command and the part of its output that shows it.
- **Confidence**: `confirmed` (the source says it directly), `likely` (several sources agree, or one
  strong indirect one), `speculative` (an inference; say what it rests on).
- **Date**: when the source was written, if known. Interview processes change; old evidence is weaker.

## People
- Public sources only: public repos, gists, blog posts, talks, public profiles. No guessing at private
  accounts, no contacting anyone, nothing behind someone else's login.
- Write down what a person's public work says about the interview or the stack, with the link, not a
  profile of the person: a GitHub handle and the repo or post is enough.

## Logins and captchas
- Agents never log in, enter credentials or solve captchas. A page that needs it goes in the lane's
  `## Blocked` list; the orchestrator asks the user to clear it (see [browser.md](browser.md)).

## Pace
- Load pages at a person's pace: a few seconds apart, never in parallel against one site.
