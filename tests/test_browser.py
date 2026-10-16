"""tools/browser.py: the browser stays visible but never takes the user's focus, and keeps to its own
workspace and profile.

Chromium is faked by a script on PATH and niri by a socket (support.FakeNiri); the DevTools websocket is
faked in-process.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from support import ROOT, FakeNiri  # first: it puts tools/ on sys.path

# isort: split
import browser

FAKE_CHROMIUM = """#!/usr/bin/env python3
# Appends how it was started, and which earlier launches were still running, to FAKE_LOG (one JSON line per
# launch). With a DevTools port it says where DevTools listens and runs until killed; without one it is a window
# the user signs in to and closes after FAKE_WINDOW_OPEN_FOR seconds.
import json, os, signal, sys, time
profile = next(a.split("=", 1)[1] for a in sys.argv if a.startswith("--user-data-dir="))
def running(pid):
    try:
        return open(f"/proc/{pid}/stat").read().split()[2] != "Z"
    except OSError:
        return False
log = os.environ["FAKE_LOG"]
earlier = [json.loads(line)["pid"] for line in open(log)] if os.path.exists(log) else []
with open(log, "a") as f:
    record = {"argv": sys.argv[1:], "env": dict(os.environ), "pid": os.getpid()}
    f.write(json.dumps(record | {"running": [p for p in earlier if running(p)]}) + "\\n")
if any(a.startswith("--remote-debugging-port") for a in sys.argv):
    # like Chromium, it takes a moment to shut down after SIGTERM
    signal.signal(signal.SIGTERM, lambda *_: (time.sleep(0.5), sys.exit(0)))
    with open(os.path.join(profile, "DevToolsActivePort"), "w") as f:
        f.write("9222\\n/devtools/browser/fake\\n")
    time.sleep(60)
else:
    time.sleep(float(os.environ.get("FAKE_WINDOW_OPEN_FOR", "1")))
"""


class FakeSocket:
    """A DevTools websocket that answers every request with an empty result."""

    def __init__(self):
        self.sent = []

    def send(self, data):
        self.sent.append(json.loads(data))

    def recv(self):
        return json.dumps({"id": self.sent[-1]["id"], "result": {}})

    def close(self):
        pass


class DevToolsTest(unittest.TestCase):
    def setUp(self):
        self.ws = FakeSocket()
        fake = mock.Mock(create_connection=mock.Mock(return_value=self.ws))
        self.enterContext(mock.patch.dict(sys.modules, websocket=fake))

    def test_refuses_calls_that_raise_a_window_or_tab(self):
        self.assertLessEqual({"Page.bringToFront", "Target.activateTarget"}, browser.DENIED)
        page = {"type": "page", "url": "https://example.com", "webSocketDebuggerUrl": "ws://fake"}
        with mock.patch.object(browser, "tabs", return_value=[page]):
            tab = browser.Tab()
        for method in sorted(browser.DENIED):
            with self.subTest(method=method):
                with self.assertRaises(SystemExit) as e:
                    tab.call(method)
                self.assertIn("focus", str(e.exception))
                self.assertEqual(self.ws.sent, [])

    def test_new_tabs_open_in_the_background(self):
        ws = self.ws
        with mock.patch.object(browser, "api", return_value={"webSocketDebuggerUrl": "ws://fake"}):
            browser.new_tab("https://example.com")
        self.assertEqual(
            ws.sent,
            [{"id": 1, "method": "Target.createTarget", "params": {"url": "https://example.com", "background": True}}],
        )


class CommandsTest(unittest.TestCase):
    def test_every_command_has_a_handler(self):
        sub = next(a for a in browser.parser()._actions if isinstance(a, argparse._SubParsersAction))
        self.assertIn("click", sub.choices)
        self.assertEqual(set(sub.choices) - set(browser.TAB_COMMANDS), {"start", "stop", "tabs", "open", "login"})


class LaunchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (self.tmp / "bin").mkdir()
        (self.tmp / "bin/chromium").write_text(FAKE_CHROMIUM)
        (self.tmp / "bin/chromium").chmod(0o755)
        env = {k: v for k, v in os.environ.items() if k != "NIRI_SOCKET"}
        self.env = env | {
            "PATH": f"{self.tmp / 'bin'}:{env['PATH']}",
            "ID_BROWSER_HOME": str(self.tmp / "home"),
            "FAKE_LOG": str(self.tmp / "launches.jsonl"),
            "XDG_ACTIVATION_TOKEN": "token",
            "DESKTOP_STARTUP_ID": "startup",
        }
        self.addCleanup(self.browser, "stop")

    def browser(self, *args):
        return subprocess.run(
            [sys.executable, ROOT / "tools/browser.py", *args],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    def launches(self):
        return [json.loads(line) for line in (self.tmp / "launches.jsonl").read_text().splitlines()]

    @staticmethod
    def running(pid):
        try:
            return Path(f"/proc/{pid}/stat").read_text().split()[2] != "Z"
        except OSError:
            return False

    def test_starts_unable_to_claim_focus_on_its_own_profile(self):
        r = self.browser("start", "https://example.com")
        self.assertEqual(r.returncode, 0, r.stderr)
        (launch,) = self.launches()
        self.assertNotIn("XDG_ACTIVATION_TOKEN", launch["env"])
        self.assertNotIn("DESKTOP_STARTUP_ID", launch["env"])
        self.assertIn("--class=dev.claude.lab", launch["argv"])
        self.assertIn(f"--user-data-dir={self.tmp / 'home/profile'}", launch["argv"])

    def test_stop_forget_deletes_the_profile_and_its_logins(self):
        self.assertEqual(self.browser("start").returncode, 0)
        pid = json.loads((self.tmp / "home/state.json").read_text())["pid"]
        r = self.browser("stop", "--forget")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse((self.tmp / "home/profile").exists())
        for _ in range(50):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            if Path(f"/proc/{pid}/stat").read_text().split()[2] == "Z":
                break  # exited; the test's reaper just hasn't collected it
            time.sleep(0.1)
        else:
            self.fail("the browser process outlived stop")

    def test_login_opens_the_profile_with_nothing_attached_and_returns_once_the_window_closes(self):
        """Google refuses to sign in a browser that can be driven ("Couldn't sign you in"), so a login window
        has no DevTools port. It is still our profile, our app-id and unable to claim focus."""
        r = self.browser("login", "https://accounts.google.com/")
        self.assertEqual(r.returncode, 0, r.stderr)
        (launch,) = self.launches()
        self.assertEqual([a for a in launch["argv"] if "remote-debugging" in a], [])
        self.assertIn("https://accounts.google.com/", launch["argv"])
        self.assertIn("--class=dev.claude.lab", launch["argv"])
        self.assertIn(f"--user-data-dir={self.tmp / 'home/profile'}", launch["argv"])
        self.assertNotIn("XDG_ACTIVATION_TOKEN", launch["env"])
        self.assertNotIn("DESKTOP_STARTUP_ID", launch["env"])
        self.assertFalse(self.running(launch["pid"]), "returned before the user closed the window")

    def test_login_closes_a_running_browser_on_the_profile_first(self):
        """Chromium hands a second launch on the same profile to the one running, which has a DevTools port."""
        self.assertEqual(self.browser("start").returncode, 0)
        r = self.browser("login", "https://accounts.google.com/")
        self.assertEqual(r.returncode, 0, r.stderr)
        _, login = self.launches()
        self.assertEqual(login["running"], [], "the browser with a DevTools port was still running")
        self.assertFalse((self.tmp / "home/state.json").exists())


class GatherTest(unittest.TestCase):
    """Every window of our browser ends up on the `interview-detective` workspace, without focus; nothing
    else is touched."""

    def setUp(self):
        self.tmp = self.enterContext(tempfile.TemporaryDirectory())
        self.pgid = os.getpgid(0)
        other = subprocess.Popen(["sleep", "30"], start_new_session=True)  # another browser lab's process group
        self.addCleanup(other.wait)
        self.addCleanup(other.kill)
        self.other_pid = other.pid

    def niri(self, windows, workspaces):
        fake = FakeNiri(self.tmp, windows, workspaces)
        self.addCleanup(fake.close)
        self.enterContext(mock.patch.dict(os.environ, NIRI_SOCKET=fake.path))
        return fake

    def window(self, id, ws, app="dev.claude.lab", pid=None):
        return {"id": id, "app_id": app, "pid": pid or os.getpid(), "workspace_id": ws, "is_focused": False}

    @staticmethod
    def ws(id, idx, output="DP-1", name=None):
        return {"id": id, "idx": idx, "output": output, "name": name}

    def moves(self, fake):
        return {a["window_id"]: a for name, a in fake.actions if name == "MoveWindowToWorkspace"}

    def test_moves_our_windows_to_a_new_workspace_on_the_focused_output(self):
        fake = self.niri(
            [
                self.window(1, 10),
                self.window(2, 20),
                self.window(3, 10, app="firefox"),
                self.window(4, 10, pid=self.other_pid),
            ],
            [
                self.ws(10, 1),
                self.ws(20, 2),
                self.ws(30, 3),
                self.ws(40, 1, output="HDMI-A-1"),
                self.ws(41, 2, output="HDMI-A-1"),
            ],
        )
        self.assertEqual(browser.gather(self.pgid), 2)
        moves = self.moves(fake)
        self.assertEqual(set(moves), {1, 2})
        for m in moves.values():
            self.assertEqual(m["reference"], {"Id": 30})
            self.assertIs(m["focus"], False)
        names = [i for i, (name, _) in enumerate(fake.actions) if name == "SetWorkspaceName"]
        self.assertEqual(fake.actions[names[0]][1], {"name": "interview-detective", "workspace": {"Id": 30}})
        self.assertGreater(names[0], 0, "named after a window moves there, or niri appends another empty one")

    def test_pulls_a_popup_back_to_the_named_workspace(self):
        fake = self.niri(
            [self.window(1, 30), self.window(2, 10)],
            [self.ws(10, 1), self.ws(30, 2, name="interview-detective"), self.ws(31, 3)],
        )
        self.assertEqual(browser.gather(self.pgid), 1)
        self.assertEqual(self.moves(fake)[2]["reference"], {"Id": 30})
        self.assertNotIn("SetWorkspaceName", [name for name, _ in fake.actions])


if __name__ == "__main__":
    unittest.main()
