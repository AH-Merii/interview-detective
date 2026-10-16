#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["websocket-client"]
# ///
"""A visible Chromium the user logs into and agents read, over DevTools.

Modelled on niri-screen-lab's browser lab (AH-Merii/claude-plugins#48), except the window stays visible:
the user clears captchas and logs in there, and agents look and act through DevTools only (never the real
keyboard or mouse). The window never takes focus:
  - it opens with app-id dev.claude.lab, which the user's niri window rule (cfg/agents.kdl) opens with
    `open-focused false`; set ID_APP_ID to use another rule;
  - it starts without XDG_ACTIVATION_TOKEN or DESKTOP_STARTUP_ID, which would let it claim focus;
  - once open, it is moved, unfocused, to a new workspace named `interview-detective` on the output the
    user is working on; they switch there to log in. Every command pulls stray windows (login popups)
    back onto that workspace;
  - DevTools calls that raise a window or tab are refused, and agent tabs open in the background.

Run with: uv run tools/browser.py COMMAND ...

  start [URL...]           start the browser (or open URLs as new tabs if it is running)
  stop [--forget]          close it; --forget also deletes the profile and its logins
  login URL...             for a sign-in that refuses a browser that can be driven (Google says "Couldn't sign
                           you in"): close the browser, open the profile with no DevTools port, and return when
                           the user closes that window. The logins stay in the profile; then `start` again.
  tabs                     list tabs: index, title, url
  open URL                 open URL in a new tab
  text [-t TAB] [--max N]  the page's visible text
  js   [-t TAB] EXPR       evaluate JavaScript and print its JSON value
  goto [-t TAB] URL        navigate and wait for the load
  shot [-t TAB] FILE.png   screenshot the viewport (view it with the Read tool)
  click [-t TAB] X Y       click at CSS pixel X Y (find it with js + getBoundingClientRect())
  type [-t TAB] TEXT       type text into the focused element
  key  [-t TAB] NAME...    press keys: enter tab esc backspace up down pgup pgdn
  scroll [-t TAB] up|down [N]

TAB is a tab index from `tabs` or a substring of its url; default: the first tab.
"""

import argparse
import base64
import json
import os
import select
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

APP_ID = os.environ.get("ID_APP_ID", "dev.claude.lab")
HOME = Path(os.environ.get("ID_BROWSER_HOME", Path.home() / ".cache/interview-detective/browser"))
PROFILE, STATE, DOWNLOADS = HOME / "profile", HOME / "state.json", HOME / "downloads"
# Without the DevTools port: what a login window runs with.
LOGIN_FLAGS = [
    "--no-first-run",
    "--no-default-browser-check",
    "--password-store=basic",  # never the user's keyring
    "--deny-permission-prompts",
    "--disable-notifications",
    # keep background tabs and a covered window rendering, so agents can read and screenshot them
    "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding",
    "--disable-backgrounding-occluded-windows",
]
FLAGS = ["--remote-debugging-port=0", *LOGIN_FLAGS]  # a free port, written to DevToolsActivePort in the profile
WORKSPACE = os.environ.get("ID_WORKSPACE", "interview-detective")
# Methods that would raise the window or tab and take the user's focus.
DENIED = {"Page.bringToFront", "Target.activateTarget"}
KEYS = {
    "enter": ("Enter", 13, "\r"),
    "tab": ("Tab", 9, ""),
    "esc": ("Escape", 27, ""),
    "backspace": ("Backspace", 8, ""),
    "up": ("ArrowUp", 38, ""),
    "down": ("ArrowDown", 40, ""),
    "pgup": ("PageUp", 33, ""),
    "pgdn": ("PageDown", 34, ""),
}


def die(msg):
    raise SystemExit(f"browser: {msg}")


def port():
    try:
        return json.loads(STATE.read_text())["port"]
    except (OSError, ValueError, KeyError):
        die("not running; start it with: uv run tools/browser.py start URL")


def api(path, method="GET"):
    req = urllib.request.Request(f"http://127.0.0.1:{port()}/json{path}", method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=5))
    except OSError:
        die("not answering; the window may have been closed. Run start again")


def new_tab(url):
    """Open url in a background tab, so the tab the user is on stays in front."""
    import websocket

    ws = websocket.create_connection(api("/version")["webSocketDebuggerUrl"], suppress_origin=True, timeout=30)
    ws.send(json.dumps({"id": 1, "method": "Target.createTarget", "params": {"url": url, "background": True}}))
    while json.loads(ws.recv()).get("id") != 1:
        pass
    ws.close()


def tabs():
    return [t for t in api("") if t["type"] == "page"]


class Tab:
    def __init__(self, sel=None):
        import websocket

        ts = tabs()
        if not ts:
            die("no tabs open")
        if sel is None:
            t = ts[0]
        elif sel.isdigit():
            t = ts[int(sel)] if int(sel) < len(ts) else die(f"no tab {sel}; see `tabs`")
        else:
            t = next((t for t in ts if sel in t["url"]), None) or die(f"no tab whose url contains {sel!r}")
        self.ws = websocket.create_connection(t["webSocketDebuggerUrl"], suppress_origin=True, timeout=60)
        self.n = 0

    def call(self, method, **params):
        if method in DENIED:
            die(f"{method} is refused: it would take the user's focus")
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.n:
                if "error" in msg:
                    die(f"{method}: {msg['error'].get('message')}")
                return msg.get("result", {})

    def js(self, expr):
        r = self.call("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        if "exceptionDetails" in r:
            die(f"the page threw: {r['exceptionDetails'].get('exception', {}).get('description')}")
        return r.get("result", {}).get("value")

    def goto(self, url, timeout=45):
        r = self.call("Page.navigate", url=url)
        if r.get("errorText"):
            die(f"could not open {url}: {r['errorText']}")
        time.sleep(0.5)
        end = time.monotonic() + timeout
        while self.js("document.readyState") != "complete":
            if time.monotonic() > end:
                die(f"{url} did not finish loading in {timeout}s")
            time.sleep(0.3)

    def text(self):
        return self.js("document.title + '\\n' + location.href + '\\n\\n' + document.body.innerText")

    def mouse(self, kind, x, y, **kw):
        self.call("Input.dispatchMouseEvent", type=kind, x=x, y=y, **kw)

    def press(self, name):
        if name not in KEYS:
            die(f"unknown key {name}; known: {', '.join(KEYS)}")
        key, vk, text = KEYS[name]
        common = {"key": key, "code": key, "windowsVirtualKeyCode": vk}
        self.call("Input.dispatchKeyEvent", type="keyDown" if text else "rawKeyDown", text=text, **common)
        self.call("Input.dispatchKeyEvent", type="keyUp", **common)


# ---------- niri placement, after niri-screen-lab's place.py ----------
# Workspaces are referenced only by id or name: an index resolves against the focused output.


def niri(req):
    path = os.environ.get("NIRI_SOCKET")
    if not path:
        return None  # not under niri: leave placement to the compositor
    with socket.socket(socket.AF_UNIX) as s:
        s.connect(path)
        s.sendall((json.dumps(req) + "\n").encode())
        reply = json.loads(s.makefile().readline())
    if "Err" in reply:
        die(f"niri refused {json.dumps(req)}: {reply['Err']}")
    ok = reply["Ok"]
    return next(iter(ok.values())) if isinstance(ok, dict) and isinstance(req, str) else ok


def our_windows(pgid):
    """Every window of the browser's process group: its first window and any popups."""
    out = []
    for w in niri("Windows") or []:
        try:
            if w["app_id"] == APP_ID and w["pid"] and os.getpgid(w["pid"]) == pgid:
                out.append(w)
        except ProcessLookupError:
            pass
    return out


def workspace():
    """Our named workspace's id, creating it on the focused output's trailing (empty) workspace if needed."""
    wss = niri("Workspaces")
    named = next((w for w in wss if w["name"] == WORKSPACE), None)
    if named:
        return named["id"], False
    out = niri("FocusedOutput")["name"]
    return max((w for w in wss if w["output"] == out), key=lambda w: w["idx"])["id"], True


def gather(pgid):
    """Move any of our windows not on our workspace there, unfocused. Returns how many moved."""
    if niri("Windows") is None:
        return 0
    moved = 0
    for w in our_windows(pgid):
        ws_id, new = workspace()
        if w["workspace_id"] != ws_id:
            niri(
                {
                    "Action": {
                        "MoveWindowToWorkspace": {"window_id": w["id"], "reference": {"Id": ws_id}, "focus": False}
                    }
                }
            )
            moved += 1
        if new:  # name it after moving: a window landing on the last workspace makes niri append a new empty one
            niri({"Action": {"SetWorkspaceName": {"name": WORKSPACE, "workspace": {"Id": ws_id}}}})
    return moved


def place(pgid, timeout=10.0):
    end = time.monotonic() + timeout
    while not our_windows(pgid):
        if time.monotonic() > end:
            return print("browser: its window did not appear in niri; it was left where it opened")
        time.sleep(0.1)
    gather(pgid)
    wss = {w["id"]: w for w in niri("Workspaces")}
    for w in our_windows(pgid):
        ws = wss.get(w["workspace_id"], {})
        if w["is_focused"]:
            print("browser: WARNING its window has focus; tell the user")
        print(f"window on workspace '{ws.get('name')}' of {ws.get('output')} (switch there to log in)")


def launch(flags, urls):
    """Chromium on our profile and app-id, without the tokens that would let it claim focus."""
    (PROFILE / "Default").mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    prefs = PROFILE / "Default/Preferences"
    if not prefs.exists():  # downloads go here, never the user's folder, and never ask where
        prefs.write_text(json.dumps({"download": {"default_directory": str(DOWNLOADS), "prompt_for_download": False}}))
    env = {k: v for k, v in os.environ.items() if k not in ("XDG_ACTIVATION_TOKEN", "DESKTOP_STARTUP_ID")}
    with open(HOME / "chromium.log", "w") as log:  # Chromium keeps its own copy of the descriptor
        return subprocess.Popen(
            ["chromium", f"--class={APP_ID}", f"--user-data-dir={PROFILE}", *flags, *(urls or ["about:blank"])],
            stdout=log,
            stderr=log,
            env=env,
            start_new_session=True,
        )


def exited(pid, timeout):
    """Wait for a process that isn't our child to exit, without polling (a pidfd is readable once it has)."""
    try:
        fd = os.pidfd_open(pid)
    except ProcessLookupError:
        return True
    try:
        return bool(select.select([fd], [], [], timeout)[0])
    finally:
        os.close(fd)


def login(urls):
    if STATE.exists():
        stop(False)  # Chromium would hand this launch to the running browser, DevTools port and all
    proc = launch(LOGIN_FLAGS, urls)
    if niri("Windows") is not None:
        place(proc.pid)
    print("login window open: sign in there, then close the window")
    proc.wait()
    print(f"login window closed; the logins are kept in {PROFILE}")


def start(urls):
    if STATE.exists():
        try:
            for u in urls:
                new_tab(u)
            print(f"browser already running; opened {len(urls)} tab(s)")
            return
        except SystemExit:
            STATE.unlink()  # a stale state file from a closed window
    (PROFILE / "DevToolsActivePort").unlink(missing_ok=True)
    proc = launch(FLAGS, urls)
    for _ in range(100):
        try:
            p = int((PROFILE / "DevToolsActivePort").read_text().split()[0])
            STATE.write_text(json.dumps({"pid": proc.pid, "port": p}))
            print(f"browser up (pid {proc.pid}, DevTools :{p}, profile {PROFILE})")
            if niri("Windows") is not None:
                place(proc.pid)
            return
        except (OSError, ValueError, IndexError):
            time.sleep(0.1)
    die(f"Chromium wrote no DevToolsActivePort; see {HOME / 'chromium.log'}")


def stop(forget):
    if STATE.exists():
        pid = json.loads(STATE.read_text()).get("pid")
        try:
            os.killpg(pid, signal.SIGTERM)
            exited(pid, 10)
        except (ProcessLookupError, PermissionError, TypeError):
            pass
        STATE.unlink()
    if niri("Workspaces") and any(w["name"] == WORKSPACE for w in niri("Workspaces")):
        niri({"Action": {"UnsetWorkspaceName": {"reference": {"Name": WORKSPACE}}}})  # niri then drops it once empty
    if forget:
        shutil.rmtree(PROFILE, ignore_errors=True)
    print("stopped" + (" and forgot the profile" if forget else ""))


def parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("start").add_argument("urls", nargs="*")
    sub.add_parser("stop").add_argument("--forget", action="store_true")
    sub.add_parser("login").add_argument("urls", nargs="+")
    sub.add_parser("tabs")
    sub.add_parser("open").add_argument("url")

    def tabbed(name):
        s = sub.add_parser(name)
        s.add_argument("-t", "--tab")
        return s

    tabbed("text").add_argument("--max", type=int, default=200_000)
    tabbed("js").add_argument("expr")
    tabbed("goto").add_argument("url")
    tabbed("shot").add_argument("file")
    c = tabbed("click")
    c.add_argument("x", type=float)
    c.add_argument("y", type=float)
    tabbed("type").add_argument("text")
    tabbed("key").add_argument("names", nargs="+")
    s = tabbed("scroll")
    s.add_argument("direction", choices=["up", "down"])
    s.add_argument("n", type=int, nargs="?", default=1)
    return p


def shot(t, file):
    Path(file).write_bytes(base64.b64decode(t.call("Page.captureScreenshot", format="png")["data"]))
    print(file)


def click(t, x, y):
    t.mouse("mouseMoved", x, y)
    t.mouse("mousePressed", x, y, button="left", clickCount=1)
    t.mouse("mouseReleased", x, y, button="left", clickCount=1)


def scroll(t, direction, n):
    x, y = t.js("[innerWidth/2, innerHeight/2]")
    t.mouse("mouseWheel", x, y, deltaX=0, deltaY=(-400 if direction == "up" else 400) * n)


def goto(t, url):
    t.goto(url)
    print("loaded", url)


# The commands that act on one tab (-t).
TAB_COMMANDS = {
    "text": lambda t, a: print(t.text()[: a.max]),
    "js": lambda t, a: print(json.dumps(t.js(a.expr), ensure_ascii=False)),
    "goto": lambda t, a: goto(t, a.url),
    "shot": lambda t, a: shot(t, a.file),
    "click": lambda t, a: click(t, a.x, a.y),
    "type": lambda t, a: t.call("Input.insertText", text=a.text),
    "key": lambda t, a: [t.press(n) for n in a.names],
    "scroll": lambda t, a: scroll(t, a.direction, a.n),
}


def main():
    a = parser().parse_args()
    if a.cmd == "start":
        return start(a.urls)
    if a.cmd == "stop":
        return stop(a.forget)
    if a.cmd == "login":
        return login(a.urls)
    if STATE.exists():
        n = gather(json.loads(STATE.read_text())["pid"])  # a login popup opened since the last command
        if n:
            print(f"(moved {n} browser window(s) to the '{WORKSPACE}' workspace)", file=sys.stderr)
    if a.cmd == "tabs":
        for i, t in enumerate(tabs()):
            print(f"{i}\t{t['title'][:60]}\t{t['url']}")
        return
    if a.cmd == "open":
        new_tab(a.url)
        return print("opened in the background:", a.url)
    TAB_COMMANDS[a.cmd](Tab(a.tab), a)


if __name__ == "__main__":
    main()
