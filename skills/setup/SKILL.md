---
name: setup
description: Set up or reconfigure interview-detective with its terminal wizard (requirements, cases folder, the niri window rule, a browser check and an optional Glassdoor login). Use when the user asks to set up, configure or reconfigure interview-detective, or to change where its cases are kept.
---

# Set up interview-detective

The setup is an interactive wizard, so the user runs it in a terminal of their own; it can't run through
Claude Code's `!` or the Bash tool. Give them this command and what it does, then stop:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/setup/wizard.sh
```

It checks for uv, Chromium and a logged-in `gh`; asks where cases live and saves it to
`~/.config/interview-detective/config.env`; on niri, checks the window rule that keeps the browser from
taking focus; opens the browser once to check it; and offers a Glassdoor login. Running it again keeps
what was saved unless they change it.
