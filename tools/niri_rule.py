#!/usr/bin/env python3
"""The niri window rule that keeps the browser (app-id dev.claude.lab) from taking focus: find it where niri
loads it, choose where it goes, and add it there with the include that loads it.

Run with: python3 tools/niri_rule.py COMMAND

  find          print the file niri loads the rule from; exit 1 if niri loads none
  target        print the file the rule goes in: an agents.kdl the config already includes, else
                cfg/agents.kdl beside config.kdl (rules made for agents are kept in their own file)
  add [FILE]    add the rule to FILE (default: target) and include FILE from config.kdl, each only if missing;
                a relative FILE is relative to config.kdl's folder. If `niri validate` then fails, both files
                are put back as they were. Does nothing if niri already loads the rule.
  rule          print the rule

The config is $NIRI_CONFIG, else $XDG_CONFIG_HOME/niri/config.kdl, as niri reads it. Includes are followed the
way niri follows them: relative to the including file's path as written, so through symlinks without resolving
them.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RULE = 'window-rule {\n    match app-id=r#"^dev\\.claude\\.lab$"#\n    open-focused false\n}\n'
HEADER = "// niri rules made for Claude and agent workflows, kept apart from the general config.\n"
COMMENT = "// Claude's lab windows and the interview-detective browser: open without taking focus.\n"
HAS_RULE = re.compile(r'app-id=r?#*"[^"\n]*dev\\?\.claude\\?\.lab')
INCLUDE = re.compile(r'^[ \t]*include[ \t]+"([^"]*)"', re.MULTILINE)


def config_path():
    xdg = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(os.environ.get("NIRI_CONFIG") or Path(xdg) / "niri/config.kdl")


def uncommented(text):
    """The KDL text without its comments: /* blocks */, // line comments, and /- nodes (with their { children })."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", "", text)
    while (start := text.find("/-")) != -1:
        end = text.find("\n", start)
        brace = text.find("{", start, end if end != -1 else None)
        if brace == -1:
            end = len(text) if end == -1 else end
        else:
            depth, end = 0, brace
            while end < len(text):
                depth += {"{": 1, "}": -1}.get(text[end], 0)
                end += 1
                if depth == 0:
                    break
        text = text[:start] + text[end:]
    return text


def resolve(path, base):
    """An include's path as niri reads it: ~ expanded, relative to the including file's folder as written."""
    return Path(os.path.normpath(Path(base).parent / Path(path).expanduser()))


def loaded(config):
    """Every file niri loads, in order, as (path as written, its text without comments)."""
    seen, out = set(), []

    def visit(path):
        if not path.is_file() or path.resolve() in seen:
            return
        seen.add(path.resolve())
        text = uncommented(path.read_text())
        out.append((path, text))
        for include in INCLUDE.findall(text):
            visit(resolve(include, path))

    visit(config)
    return out


def find(config):
    return next((path for path, text in loaded(config) if HAS_RULE.search(text)), None)


def target(config):
    agents = (path for path, _ in loaded(config)[1:] if path.name == "agents.kdl")
    return next(agents, Path(os.path.normpath(config.parent / "cfg/agents.kdl")))


def include_line(path, config):
    rel = os.path.relpath(path, config.parent)
    return f'include "{path if rel.startswith("..") else "./" + rel}"\n'


def appended(text, addition):
    return text + ("" if not text or text.endswith("\n") else "\n") + addition


class Edits:
    """The files an add changes, so they can all be put back as they were."""

    def __init__(self):
        self.saved, self.made = {}, []

    def write(self, path, text):
        if path not in self.saved:
            self.saved[path] = path.read_text() if path.exists() else None
        for parent in reversed(path.parents):
            if not parent.exists():
                parent.mkdir()
                self.made.append(parent)
        path.write_text(text)

    def undo(self):
        for path, text in self.saved.items():
            if text is None:
                path.unlink()
            else:
                path.write_text(text)
        for folder in reversed(self.made):
            folder.rmdir()


def add(config, chosen):
    if not config.is_file():
        sys.exit(f"no niri config at {config}: niri writes its default one on first start; then run this again")
    if where := find(config):
        print(f"niri already loads the rule, from {where}")
        return
    path = resolve(chosen, config.parent / "config.kdl") if chosen else target(config)
    edits = Edits()
    text = path.read_text() if path.exists() else HEADER + "\n"
    if not HAS_RULE.search(uncommented(text)):
        edits.write(path, appended(text, ("\n" if path.exists() else "") + COMMENT + RULE))
    if path.resolve() not in {p.resolve() for p, _ in loaded(config)}:
        edits.write(config, appended(config.read_text(), include_line(path, config)))
    validate(config, edits)
    print(f"added the rule to {path}" + (f", included from {config}" if config in edits.saved else ""))


def validate(config, edits):
    if not shutil.which("niri"):
        print("niri isn't on PATH, so the config wasn't validated")
        return
    r = subprocess.run(["niri", "validate", "-c", str(config)], capture_output=True, text=True, check=False)
    if r.returncode != 0:
        edits.undo()
        sys.exit(f"niri validate failed, so the config was put back as it was:\n{r.stdout}{r.stderr}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("find", "target", "rule"):
        sub.add_parser(name)
    sub.add_parser("add").add_argument("file", nargs="?")
    args = p.parse_args()
    config = config_path()
    if args.cmd == "find":
        where = find(config)
        print(where or "", end="\n" if where else "")
        sys.exit(0 if where else 1)
    if args.cmd == "target":
        print(target(config))
    elif args.cmd == "rule":
        print(RULE, end="")
    else:
        add(config, args.file)


if __name__ == "__main__":
    main()
