# Lane: people (tier: opus)

Find hints in the public work of the people who will interview the user, and of the people who already
hold this job or one next to it. Hires in the same role often published their own interview exercise,
in a repo that never names the company. This lane is open-ended: follow the trail where it goes.

## 1. The interviewer and the panel
The intake names them. For each:
- LinkedIn (signed in before the research): title, team, when they joined, earlier jobs that hint at
  what they value. Read their posts.
- Their GitHub (a link on the profile, or a match on name and location; say how sure the match is):
  what they build, the code they review (their comments on others' pull requests show what they ask
  for), and anything they built or reviewed for hiring.
- Talks, posts and papers, and what they say about how they hire or what good code looks like.

## 2. People in this role and next to it
- Open the company's LinkedIn People page and search it by the titles in the intake's related roles
  (group A, then B), plus the title of the job itself. Order the matches by group, then by how
  recently they joined. Open at most 30 profiles, and note each one's title, start date and any GitHub
  or site link.
- Add people the company's GitHub points to: public members of its orgs
  (`gh api orgs/<org>/public_members`), frequent committers to its repos, and profiles naming the
  company.
- For each person, find their GitHub, and look at the repos and gists they created in the six months
  before they joined, and any with an exercise's name (interview, challenge, take-home, assessment,
  test, kata, or the domain's words). The task statement in a README is the prize; note its date.
- Also look for talks or posts about the team's stack, its problems, or how it hires.

Weigh relevance: someone in this role, joined recently, beats a former employee from years ago.

Follow `_shared/evidence.md` on people: public work only, nobody contacted, and record what the work
says about the interview or the stack, with a handle and a link, not a profile of the person. Use
LinkedIn through the browser as `_shared/browser.md` says: one tab, a few seconds between pages, read
only. Write to the output path you were given, in the lane output format; add a table of the people you
looked at (name, title, group, start, profile, GitHub) under `## People`.
