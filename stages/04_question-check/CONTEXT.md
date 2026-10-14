# 04_question-check — is each question standard?

One job: for every question gathered so far, say whether it is a standard problem, a variant of one,
or specific to this company, and link the closest public version to practise on.

## Inputs
- Working (this run): `<case>/01_intake/intake.md` (questions the user already received)
- Working (this run): `<case>/02_research/findings.md` (exercises and questions found)
- Working (this run): `<case>/03_glassdoor/processes.md` (group A and B questions)
- Reference: `references/question-bank.md` (the output format), `../../_shared/agent-tiers.md`,
  `../../_shared/evidence.md`

Do NOT load: `interviews.json` whole, `02_research/lanes/*` (findings.md already merges them), group C.

## Process
1. Collect the questions from the three inputs into `questions.md`: one per line, numbered, with its
   origin (`intake`, `findings`, `glassdoor A`, `glassdoor B`) and the Glassdoor id or source link.
   Merge duplicates and near-duplicates, keeping every origin.
2. Split them into batches of about 10 and start one `haiku` agent per batch in the same turn, in the
   background. Each gets `references/question-bank.md`, `_shared/evidence.md`, the batch, and writes
   `<case>/04_question-check/batches/NN.md`.
3. Rerun every item a batch marked `unsure` with a `sonnet` agent, replacing it in the batch file.
4. Merge the batches into `question-bank.md`, ordered: group A and intake first, then findings, then B;
   within each, the most recent and most often reported first.

## Outputs
- `<case>/04_question-check/questions.md`, `batches/NN.md`, `question-bank.md`

## Human check
The user skims `question-bank.md`, deletes what is irrelevant and stars (`★`) what they most want to
practise; 05 favours starred items.
