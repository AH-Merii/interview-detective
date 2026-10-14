# 01_intake — ask what the user knows

One job: turn what the user knows about the interview into `intake.md`.

## Inputs
- Working (this run): `<case>/01_intake/intake.md`, the blank stamp from `tools/new_case.sh`
- Reference: the user, in conversation

Do NOT load: other cases, `stages/02+`, `_shared/` (nothing here searches or scrapes).

## Process
1. If there is no case yet, ask for the company and the role first, then run
   `tools/new_case.sh "<company>" "<role>"` and work in the folder it prints.
2. Ask the rest of the stamp's questions a few at a time, in its order: the round and its format, the
   panel, what the recruiter said, the team and stack, the job post, anything already received
   (exercises, emails), other leads, which roles count as the same job (A) or adjacent (B), and what
   the user wants most. Skip what the user says they don't know; never invent an answer.
3. Write the answers into `intake.md`, keeping the user's wording. Paste received exercises in full.
4. Show the file's path and a five-line summary; ask the user to read and correct it.

## Outputs
- `<case>/01_intake/intake.md`

## Human check
The user reads `intake.md` and fixes anything wrong; then set `confirmed: true` in its frontmatter.
