<p align="center">
  <img src="_assets/logo-wordmark.svg" alt="interview detective: clues in, questions out" width="560">
</p>

Detective work before a job interview, run by Claude Code. You say what company, role and round; it
investigates in parallel and hands back a sourced report with the questions you are most likely to get.

- **Glassdoor**: scrapes the company's interview reviews for related roles into JSON you can query,
  grouped by how close each role is to yours. You log in once in a browser window it opens on its own
  workspace; it never takes your focus.
- **People**: your interviewer and panel, and people already in your role or next to it, found on the
  company's LinkedIn People page. For each, their public GitHub, including repos made around when they
  joined, where hires often leave their own interview exercise.
- **GitHub and the web**: the company's repos and stack, prep repos and take-home solutions past
  candidates uploaded, write-ups, talks, archived job posts.
- **Question check**: is each question a standard problem, a variant of one, or specific to this
  company, with a link to practise on.
- **Report**: summary, a day-by-day practice plan sized to the time you have, findings with sources and
  confidence, Glassdoor numbers, practice questions.
- **Pages to read**: each stage you read opens as an HTML page, and every guess links to a page that
  shows what it rests on: the sources, how they add up, and what cuts against it.

## Get started

You need [Claude Code](https://claude.com/claude-code), [uv](https://docs.astral.sh/uv/), Chromium,
and the [`gh`](https://cli.github.com/) CLI, logged in. The setup wizard checks for each.

1. Install the plugin from the [ah-merii marketplace](https://github.com/AH-Merii/claude-plugins), in
   Claude Code:

   ```text
   /plugin marketplace add AH-Merii/claude-plugins
   /plugin install interview-detective@ah-merii
   ```

2. Run the setup wizard in a terminal. `/interview-detective:setup` prints the command with the
   plugin's path filled in; it looks like this:

   ```bash
   bash ~/.claude/plugins/cache/ah-merii/interview-detective/<version>/setup/wizard.sh
   ```

   It checks the requirements and asks where your cases should live (`~/interview-detective` by
   default). On [niri](https://github.com/YaLTeR/niri) it checks for the window rule that keeps the
   browser from taking your focus. If niri doesn't load that rule yet, the wizard shows it and offers to
   add it, once you approve, to `~/.config/niri/cfg/agents.kdl`, the file for rules made for agents.
   It uses an `agents.kdl` your config already includes, if there is one, and you can name another file.
   It also adds the `include` line to `config.kdl` if it's missing. If `niri validate` rejects the
   result, both files go back to how they were. Then it opens the browser once to check it, and offers
   Glassdoor and LinkedIn logins. Run it again any time: anything already in place is left alone.

3. In Claude Code, from any folder, run `/interview-detective:interview-detective` or say you have an
   interview coming up.

## What a run looks like

1. **Intake.** It asks for the company, role and round, what you already have (emails, a job post, a
   take-home), and how much time you have to prepare. It writes `<case>/01_intake/intake.md` in your
   cases folder; read it, fix anything wrong, and say it's right.
2. **Sign in, then research and Glassdoor at the same time.** A Chromium window opens on a new
   workspace called `interview-detective` on your current screen, with a tab for each site the case
   reads behind a login: Glassdoor (Sign in with Google works) and LinkedIn, plus any your intake names.
   Switch to it, sign in, clear any Cloudflare check, then close the window. Sites you're already
   signed in to are skipped. Agents then search GitHub and the web in the background. If research hits
   other pages behind a captcha or login, they open in one more window for you.
   Nothing can drive that window while you use it, so sites that refuse automated browsers still let
   you sign in. Claude reopens the browser for its agents once you close it.
3. **Question check.** Every reported question is matched to a standard problem, a variant, or marked
   as specific to the company, with the next round's questions first. Star (★) the ones you want the
   report to favour.
4. **Report.** `<case>/05_report/report.md`: summary, practice plan, findings with sources, Glassdoor
   numbers and practice questions.

It stops after each stage for you to read what it wrote, as an HTML page it gives you a command to
open, and the next stage reads your edits to the markdown beside it.
Asking for status lists every case and its next stage, and saying "resume" picks one up.

Your logins stay in the browser's own profile, in `~/.cache/interview-detective/browser/`.
Deleting that folder deletes them.

## How it works

The workspace is an [ICM](https://arxiv.org/abs/2603.16021) pipeline: folders carry the order, files
carry the state, and each stage's contract says exactly what it reads and writes.

- [CONTEXT.md](CONTEXT.md): the five stages on one screen.
- [The skill](skills/interview-detective/SKILL.md): where everything lives, and where to go next.
- [`_shared/agent-tiers.md`](_shared/agent-tiers.md): which model tier does which job.
- [`_shared/browser.md`](_shared/browser.md): the browser, and handing logins to you.
- [`_shared/pages.md`](_shared/pages.md): the pages you read, and the why page behind each guess.
- [`setup/wizard.sh`](setup/wizard.sh): the first-run setup.

The plugin is the factory: contracts, rules, templates and tools, replaced whole on each update. The
cases are the product, so they live outside it, in the folder the wizard saved to
`~/.config/interview-detective/config.env`. They hold scraped reviews and notes on real people's public
work, and never leave your machine.

## Develop

Checks are [mise](https://mise.jdx.dev/) tasks, and CI runs the same ones (`.github/workflows/ci.yml`):

```bash
mise run setup    # once after cloning: the pre-push secret scan
mise run check    # every check: plugin validation, lint, types, tests with coverage, complexity, secrets, workflows
```

`claude --plugin-dir .` loads the plugin from this folder, to try changes without installing them.

The tests run offline, with Chromium and niri faked (`python3 -m unittest discover -s tests`).
`tests/test_live.py` checks the real Glassdoor; its docstring says how to run it.

Releases are automatic. PR titles follow [Conventional Commits](https://www.conventionalcommits.org/), and
release-please keeps a release PR open that bumps `version.txt`, the plugin's version in
`.claude-plugin/plugin.json` (Claude Code updates a plugin only when that changes) and `CHANGELOG.md`. The
interview-detective-bot App merges it once CI passes, which tags `vX.Y.Z` and publishes the release
(`.github/workflows/release.yml`).

## License

[MIT](LICENSE), copyright 2026 AH-Merii (AbdulHamid Merii).
