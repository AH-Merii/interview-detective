<p align="center">
  <img src="_assets/logo-wordmark.svg" alt="interview detective: clues in, questions out" width="560">
</p>

Detective work before a job interview, run by Claude Code. You say what company, role and round; it
investigates in parallel and hands back a sourced report with the questions you are most likely to get.

- **Glassdoor**: scrapes the company's interview reviews for related roles into JSON you can query,
  grouped by how close each role is to yours. You log in once in a browser window it opens on its own
  workspace; it never takes your focus.
- **GitHub and the web**: the company's repos and stack, public work by people who work there, prep
  repos and take-home solutions past candidates uploaded, write-ups, talks, archived job posts.
- **Question check**: is each question a standard problem, a variant of one, or specific to this
  company, with a link to practise on.
- **Report**: summary, findings with sources and confidence, Glassdoor numbers, practice questions.

## Use it

In Claude Code, run `/interview-detective` or say you have an interview coming up. It asks what you
know, then walks the pipeline, stopping for you to check each stage's output.

```bash
tools/new_case.sh "Acme AI" "ML Engineer"   # start a case by hand
uv run tools/status.py                       # every case and its next stage
```

## How it works

The workspace is an [ICM](https://arxiv.org/abs/2603.16021) pipeline: folders carry the order, files
carry the state, and each stage's contract says exactly what it reads and writes.

- [CONTEXT.md](CONTEXT.md): the five stages on one screen.
- [CLAUDE.md](CLAUDE.md): where everything lives, and where to go next.
- [`_shared/agent-tiers.md`](_shared/agent-tiers.md): which model tier does which job.
- [`_shared/browser.md`](_shared/browser.md): the browser, and handing logins to you.

Each interview is a case folder under `interviews/`. Cases hold scraped reviews and notes on real
people's public work, so `.gitignore` keeps them out of the repo.

## Requirements

- [Claude Code](https://claude.com/claude-code), [uv](https://docs.astral.sh/uv/), Chromium, and the
  [`gh`](https://cli.github.com/) CLI, logged in.
- [niri](https://github.com/YaLTeR/niri), for the browser's own unfocused workspace. The window rule
  that keeps it unfocused matches app-id `dev.claude.lab`:

  ```kdl
  window-rule {
      match app-id=r#"^dev\.claude\.lab$"#
      open-focused false
  }
  ```

  Without niri the browser still works; it just opens wherever your compositor puts it.

## Install the skill

```bash
ln -s "$PWD/skill" ~/.claude/skills/interview-detective
```

Use your Claude config directory if it is not `~/.claude`.
