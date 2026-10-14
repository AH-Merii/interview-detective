# The browser, and handing logins to the user

`tools/browser.py` runs one visible Chromium shared by every stage (`uv run tools/browser.py -h`).
It opens on its own niri workspace, `interview-detective`, on the user's current output, without
taking focus. The user switches there to log in or clear a captcha; agents read and act through
DevTools only. Logins persist in its profile (`~/.cache/interview-detective/browser/profile`) until
`stop --forget`.

## When a page needs the user
1. Open each page as a tab: `uv run tools/browser.py start URL [URL...]` (opens tabs if it is already
   running). Several sites at once are fine; one tab each.
2. Tell the user, in one message: the workspace name, the tabs, and what each needs (log in, captcha).
3. Wait for them to say they are done. Never type credentials or solve a captcha yourself.
4. Check each tab: `uv run tools/browser.py text -t <url-part> --max 2000`. If it still shows a login
   or a check, say which, and ask again.

## Reading an unlocked page (a `haiku` reader agent)
Prompt: the tab's url part, what to extract, the output file. The reader uses `text`, `js`, `goto`,
`scroll` and `shot` (view the PNG with Read) on that tab only, stays on that site, and writes findings
in the [evidence.md](evidence.md) format. It never logs in, never opens other sites, and keeps a few
seconds between page loads.

## Rules
- Only DevTools input (`click`, `type`, `key`, `scroll`): never wtype, ydotool or any real input.
- Agent tabs open in the background; never bring a tab or the window to the front.
- One site, one tab, one reader at a time.
- Stop the browser at the end of a run unless the user wants it kept: `uv run tools/browser.py stop`.
