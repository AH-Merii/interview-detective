"""Shared by the tests: puts tools/ on sys.path, and fakes the outside world the tools talk to.

Run the suite with: python3 -m unittest discover -s tests   (or: mise run check:test)
"""

import json
import os
import socket
import sys
import tempfile
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def scratch_cases(test):
    """A throwaway cases folder, and an environment that points the case tools at it (ID_CASES_DIR) and keeps
    them off the user's own config and home (XDG_CONFIG_HOME, HOME). Both are removed after the test."""
    tmp = Path(test.enterContext(tempfile.TemporaryDirectory()))
    env = {k: v for k, v in os.environ.items() if k != "ID_CASES_DIR"}
    return tmp / "cases", env | {
        "ID_CASES_DIR": str(tmp / "cases"),
        "XDG_CONFIG_HOME": str(tmp / "config"),
        "HOME": str(tmp / "home"),
    }


class FakeNiri:
    """A niri IPC socket that answers Windows, Workspaces and FocusedOutput from its own state, and records and
    applies the window moves and workspace names it is asked for. Only what tools/browser.py sends."""

    def __init__(self, folder, windows, workspaces, output="DP-1"):
        self.path = str(Path(folder) / "niri.sock")
        self.windows, self.workspaces, self.output, self.actions = windows, workspaces, output, []
        self.sock = socket.socket(socket.AF_UNIX)
        self.sock.bind(self.path)
        self.sock.listen()
        threading.Thread(target=self.serve, daemon=True).start()

    def close(self):
        self.sock.close()

    def serve(self):
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            with conn:
                req = json.loads(conn.makefile().readline())
                conn.sendall((json.dumps(self.answer(req)) + "\n").encode())

    def answer(self, req):
        if req == "Windows":
            return {"Ok": {"Windows": self.windows}}
        if req == "Workspaces":
            return {"Ok": {"Workspaces": self.workspaces}}
        if req == "FocusedOutput":
            return {"Ok": {"FocusedOutput": {"name": self.output}}}
        ((name, args),) = req["Action"].items()
        self.actions.append((name, args))
        if name == "MoveWindowToWorkspace":
            next(w for w in self.windows if w["id"] == args["window_id"])["workspace_id"] = args["reference"]["Id"]
        elif name == "SetWorkspaceName":
            next(w for w in self.workspaces if w["id"] == args["workspace"]["Id"])["name"] = args["name"]
        elif name == "UnsetWorkspaceName":
            for w in self.workspaces:
                if w["name"] == args["reference"]["Name"]:
                    w["name"] = None
        return {"Ok": "Handled"}
