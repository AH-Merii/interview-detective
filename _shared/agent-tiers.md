# Which agent tier for which task

Pick the tier by how open the task is, not by how important it is. The more freedom and creativity a
task needs, the more capable the model; the more scoped and checkable, the lighter the model.

Name tiers by family alias only (`haiku`, `sonnet`, `opus`), never a version: the alias always resolves
to the newest model in that family. Never use `fable`.

| Tier | Use for | Examples in this workspace |
|---|---|---|
| `haiku` | Scoped, mechanical, checkable: a fixed input, a fixed output shape | reading a page the user unlocked; classifying a batch of questions against known problem sets; mapping role titles to groups |
| `sonnet` | Searching a defined area with judgement about relevance | similar exercises on the web; the company's GitHub organisation; candidates' prep repos |
| `opus` | Open-ended detective work and synthesis; no fixed path to the answer | the people lane; the wildcard lane; writing the report |

Escalate, don't guess: when a `haiku` agent marks an item `unsure`, rerun that item with `sonnet`.

## Dispatching
- Each agent gets a short prompt that names its brief file, its input files and its output file;
  the brief holds the instructions, so they live in one place.
- Agents with no dependency between them start in the same turn, in the background.
- Every agent's prompt names [evidence.md](evidence.md): each claim carries a link, a `path:line`, or a
  command and its output.
