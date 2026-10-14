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

## Get started

You need [Claude Code](https://claude.com/claude-code), [uv](https://docs.astral.sh/uv/), Chromium,
and the [`gh`](https://cli.github.com/) CLI, logged in.

1. Clone the repo and link its skill into your Claude config:

   ```bash
   git clone git@github.com:AH-Merii/interview-detective.git
   cd interview-detective
   ln -s "$PWD/skill" "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/interview-detective"
   ```

2. On [niri](https://github.com/YaLTeR/niri), add this window rule so the browser opens without taking
   your focus. Without niri the browser still works; it opens wherever your compositor puts it.

   ```kdl
   window-rule {
       match app-id=r#"^dev\.claude\.lab$"#
       open-focused false
   }
   ```

3. In Claude Code, from any folder, run `/interview-detective` or say you have an interview coming up.

## What a run looks like

1. **Intake.** It asks for the company, role and round, and what you already have: emails, a job post,
   a take-home. It writes `interviews/<case>/01_intake/intake.md`; read it, fix anything wrong, and say
   it's right.
2. **Research and Glassdoor, at the same time.** Agents search GitHub and the web in the background.
   A Chromium window opens on a new workspace called `interview-detective` on your current screen;
   switch to it, log in to Glassdoor and clear any Cloudflare check, then tell Claude. If research hits
   pages behind a captcha or login, they open as more tabs there for you to clear.
3. **Question check.** Every reported question is matched to a standard problem, a variant, or marked
   as specific to the company. Star (★) the ones you want the report to favour.
4. **Report.** `interviews/<case>/05_report/report.md`: summary, findings with sources, Glassdoor
   numbers and practice questions.

It stops after each stage for you to read what it wrote, and the next stage reads your edits.
`uv run tools/status.py` lists every case and its next stage, and saying "resume" picks one up.

Your Glassdoor login stays in the browser's own profile, in `~/.cache/interview-detective/browser/`.
`uv run tools/browser.py stop --forget` deletes it.

## How it works

The workspace is an [ICM](https://arxiv.org/abs/2603.16021) pipeline: folders carry the order, files
carry the state, and each stage's contract says exactly what it reads and writes.

- [CONTEXT.md](CONTEXT.md): the five stages on one screen.
- [CLAUDE.md](CLAUDE.md): where everything lives, and where to go next.
- [`_shared/agent-tiers.md`](_shared/agent-tiers.md): which model tier does which job.
- [`_shared/browser.md`](_shared/browser.md): the browser, and handing logins to you.

Each interview is a case folder under `interviews/`. Cases hold scraped reviews and notes on real
people's public work, so `.gitignore` keeps them out of the repo.

## Develop

Checks are [mise](https://mise.jdx.dev/) tasks, and CI runs the same ones (`.github/workflows/ci.yml`):

```bash
mise run setup    # once after cloning: the pre-push secret scan
mise run check    # every check: lint, types, tests with coverage, complexity, secrets, workflows
```

The tests run offline, with Chromium and niri faked (`python3 -m unittest discover -s tests`).
`tests/test_live.py` checks the real Glassdoor; its docstring says how to run it.

## License

[MIT](LICENSE), copyright 2026 AH-Merii (AbdulHamid Merii).
