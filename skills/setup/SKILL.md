---
name: setup
description: Set up or reconfigure interview-detective with its terminal wizard (requirements, cases folder, the niri window rule, a browser check and optional Glassdoor and LinkedIn logins). Use when the user asks to set up, configure or reconfigure interview-detective, or to change where its cases are kept.
---

# Set up interview-detective

The setup is an interactive wizard, so the user runs it in a terminal of their own; it can't run through
Claude Code's `!` or the Bash tool. Give them this command and what it does, then stop:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/setup/wizard.sh
```

It checks for uv, Chromium and a logged-in `gh`; asks where cases live and saves it to
`~/.config/interview-detective/config.env`; on niri, checks that niri loads the window rule that keeps the browser
from taking focus, and with the user's approval adds it to `cfg/agents.kdl` (or a file they name) and
includes that file from `config.kdl`; opens the browser once to check it; and offers Glassdoor and LinkedIn logins. Running it again keeps
what was saved unless they change it.
