# The browser, and handing logins to the user

`tools/browser.py` runs one visible Chromium shared by every stage (`uv run tools/browser.py -h`).
It opens on its own niri workspace, `interview-detective`, on the user's current output, without
taking focus. Agents read and act through DevTools only. Logins persist in its profile
(`~/.cache/interview-detective/browser/profile`) until `stop --forget`.

The user signs in and clears captchas in a login window instead: the same profile with no DevTools port.
Sites can tell when a browser can be driven, and some refuse to sign it in: Google says "Couldn't sign
you in", which also blocks every "Sign in with Google" button.

## Sign in before the research
Once the intake is confirmed, before 02's lanes and 03 start, get the user signed in to every site the
case reads behind a login:
- Glassdoor: 03 scrapes its interview reviews (Sign in with Google works there);
- LinkedIn: the people lane looks up the interviewer, the panel and people in the role, and profiles
  and posts need a login;
- any other site the intake names that needs an account.

`uv run tools/browser.py start` on a page of each site, and check each tab as in step 4 below. Every
site that shows a sign-in, a captcha or a check goes into one login window (steps 1–3). If every site
is already signed in, say so and go on.

## When a page needs the user
Any page an agent needs that shows a login, a captcha or a check goes to the user, whatever the site.
Only pages that are gone (404, 410) are dropped, and the stage's output says which.

1. Open every page that needs them in one login window, in the background (it blocks until the window
   closes, and you're told when it does): `uv run tools/browser.py login URL [URL...]`. It closes the
   agents' browser first, so finish reading before you call it.
2. Tell the user, in one message: the workspace name, the tabs, what each needs (sign in, captcha), and
   to close the window when they're done.
3. When `login` returns, start the agents' browser on the same pages: `uv run tools/browser.py start
   URL [URL...]`. Never type credentials or solve a captcha yourself.
4. Check each tab: `uv run tools/browser.py text -t <url-part> --max 2000`. If it still shows a login
   or a check, say which, and run `login` again for it.

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
