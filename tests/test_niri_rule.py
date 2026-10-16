"""tools/niri_rule.py: finding the browser's niri window rule where niri loads it, choosing where it goes, and
adding it with the include that loads it, once, keeping the config valid.

Runs against real files and symlinks in a throwaway folder; niri itself is faked on PATH (its `validate` passes or
fails as a test says).
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from support import ROOT

FAKE_NIRI = """#!/usr/bin/env python3
# Records each call; `validate` fails when FAKE_NIRI_INVALID is set, the way niri reports a bad config.
import json, os, sys
with open(os.environ["FAKE_NIRI_LOG"], "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\\n")
if os.environ.get("FAKE_NIRI_INVALID"):
    print("error loading config: node `include` is broken", file=sys.stderr)
    sys.exit(1)
"""

RULE = 'window-rule {\n    match app-id=r#"^dev\\.claude\\.lab$"#\n    open-focused false\n}\n'


class NiriRuleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.niri = self.tmp / "config/niri"
        self.dotfiles = self.tmp / "dotfiles"  # where symlinked config files really live
        self.niri.mkdir(parents=True)
        self.dotfiles.mkdir()
        (self.tmp / "bin").mkdir()
        (self.tmp / "bin/niri").write_text(FAKE_NIRI)
        (self.tmp / "bin/niri").chmod(0o755)
        env = {k: v for k, v in os.environ.items() if k not in ("NIRI_CONFIG", "FAKE_NIRI_INVALID")}
        self.env = env | {
            "XDG_CONFIG_HOME": str(self.tmp / "config"),
            "HOME": str(self.tmp / "home"),
            "PATH": f"{self.tmp / 'bin'}:{env['PATH']}",
            "FAKE_NIRI_LOG": str(self.tmp / "niri.log"),
        }

    def run_tool(self, *args, **env):
        return subprocess.run(
            [sys.executable, ROOT / "tools/niri_rule.py", *args],
            env=self.env | env,
            capture_output=True,
            text=True,
            check=False,
            cwd=self.tmp,
        )

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def config(self, text):
        return self.write(self.niri / "config.kdl", text)

    def found(self):
        r = self.run_tool("find")
        self.assertIn(r.returncode, (0, 1), r.stderr)
        return r.stdout.strip() if r.returncode == 0 else None

    def snapshot(self):
        """Every file under the niri folder and the dotfiles, with its content: what a run changed."""
        return {
            str(p): (p.read_text(), p.is_symlink())
            for root in (self.niri, self.dotfiles)
            for p in sorted(root.rglob("*"))
            if p.is_file()
        }


class FindTest(NiriRuleTest):
    """The rule counts only where niri would load it: config.kdl and the files it includes, followed the way niri
    follows them (relative to the including file's path as written, so through symlinks)."""

    def test_finds_the_rule_wherever_niri_loads_it(self):
        def symlinked_config():
            self.write(self.dotfiles / "config.kdl", 'include "./cfg/agents.kdl"\n')
            (self.niri / "config.kdl").symlink_to(self.dotfiles / "config.kdl")
            return self.write(self.niri / "cfg/agents.kdl", RULE)  # beside the link, where niri looks

        def symlinked_include():
            self.config('include "./cfg/agents.kdl"\n')
            (self.niri / "cfg").mkdir()
            (self.niri / "cfg/agents.kdl").symlink_to(self.write(self.dotfiles / "agents.kdl", RULE))
            return self.niri / "cfg/agents.kdl"

        layouts = {
            "in config.kdl": lambda: self.config("layout {}\n" + RULE),
            "in an included file": lambda: (
                self.config('include "./cfg/rules.kdl"\n'),
                self.write(self.niri / "cfg/rules.kdl", RULE),
            )[1],
            "in a file an included file includes": lambda: (
                self.config('include "cfg/a.kdl"\n'),
                self.write(self.niri / "cfg/a.kdl", 'include "b.kdl"\n'),
                self.write(self.niri / "cfg/b.kdl", RULE),
            )[2],
            "through a symlinked config.kdl": symlinked_config,
            "through a symlinked included file": symlinked_include,
        }
        for name, lay_out in layouts.items():
            with self.subTest(name):
                self.setUp()
                where = lay_out()
                self.assertEqual(self.found(), str(where))

    def test_a_rule_niri_would_not_load_is_not_found(self):
        layouts = {
            "in a file nothing includes": lambda: (
                self.config("layout {}\n"),
                self.write(self.niri / "cfg/agents.kdl", RULE),
            ),
            "behind a commented-out include": lambda: (
                self.config('//include "./cfg/agents.kdl"\n/-include "./cfg/agents.kdl"\n'),
                self.write(self.niri / "cfg/agents.kdl", RULE),
            ),
            "commented out itself, as a block": lambda: self.config("/*\n" + RULE + "*/\n"),
            "commented out itself, line by line": lambda: self.config(
                "".join(f"// {line}\n" for line in RULE.splitlines())
            ),
            "commented out itself, as a node": lambda: self.config("/-" + RULE),
            "only beside a symlinked config's target": lambda: (
                self.write(self.dotfiles / "config.kdl", 'include "./cfg/agents.kdl"\n'),
                (self.niri / "config.kdl").symlink_to(self.dotfiles / "config.kdl"),
                self.write(self.dotfiles / "cfg/agents.kdl", RULE),
            ),
            "with no config at all": lambda: None,
        }
        for name, lay_out in layouts.items():
            with self.subTest(name):
                self.setUp()
                lay_out()
                self.assertIsNone(self.found())

    def test_an_include_loop_ends(self):
        self.config('include "./a.kdl"\n')
        self.write(self.niri / "a.kdl", 'include "./config.kdl"\n')
        self.assertIsNone(self.found())

    def test_niri_config_names_the_config_file(self):
        other = self.write(self.tmp / "elsewhere/main.kdl", RULE)
        self.config("layout {}\n")
        r = self.run_tool("find", NIRI_CONFIG=str(other))
        self.assertEqual((r.returncode, r.stdout.strip()), (0, str(other)), r.stderr)


class TargetTest(NiriRuleTest):
    def target(self):
        r = self.run_tool("target")
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def test_an_included_agents_kdl_is_where_the_rule_goes(self):
        self.config('include "./cfg/rules.kdl"\ninclude "./agent-rules/agents.kdl"\n')
        self.write(self.niri / "cfg/rules.kdl", "layout {}\n")
        self.write(self.niri / "agent-rules/agents.kdl", "layout {}\n")
        self.assertEqual(self.target(), str(self.niri / "agent-rules/agents.kdl"))

    def test_otherwise_cfg_agents_kdl_beside_the_config(self):
        for name, text in {
            "no includes": "layout {}\n",
            "an agents.kdl that is commented out": '//include "./elsewhere/agents.kdl"\n',
        }.items():
            with self.subTest(name):
                self.config(text)
                self.assertEqual(self.target(), str(self.niri / "cfg/agents.kdl"))


class AddTest(NiriRuleTest):
    def add(self, *args, **env):
        r = self.run_tool("add", *args, **env)
        self.log = r.stdout + r.stderr
        return r

    def includes(self):
        return [line for line in (self.niri / "config.kdl").read_text().splitlines() if line.startswith("include")]

    def test_adds_the_rule_to_the_target_and_includes_it(self):
        self.config('include "./cfg/rules.kdl"\n')
        self.write(self.niri / "cfg/rules.kdl", "layout {}\n")
        r = self.add()
        self.assertEqual(r.returncode, 0, self.log)
        agents = self.niri / "cfg/agents.kdl"
        self.assertIn(RULE, agents.read_text())
        self.assertEqual(self.includes(), ['include "./cfg/rules.kdl"', 'include "./cfg/agents.kdl"'])
        self.assertEqual(self.found(), str(agents))
        self.assertIn(f'["validate", "-c", "{self.niri / "config.kdl"}"]', (self.tmp / "niri.log").read_text())

    def test_running_it_again_changes_nothing(self):
        self.config("layout {}\n")
        self.assertEqual(self.add().returncode, 0, self.log)
        before = self.snapshot()
        r = self.add()
        self.assertEqual(r.returncode, 0, self.log)
        self.assertEqual(self.snapshot(), before)

    def test_adds_only_what_is_missing(self):
        cases = {
            "the file is included but lacks the rule": (
                'include "./cfg/agents.kdl"\n',
                "// my agent rules\nlayout {}\n",
            ),
            "the file has the rule but nothing includes it": ("layout {}\n", RULE),
            "the file holds other rules": ("layout {}\n", 'window-rule {\n    match app-id="firefox"\n}\n'),
        }
        for name, (config, existing) in cases.items():
            with self.subTest(name):
                self.setUp()
                self.config(config)
                self.write(self.niri / "cfg/agents.kdl", existing)
                self.assertEqual(self.add().returncode, 0, self.log)
                agents = (self.niri / "cfg/agents.kdl").read_text()
                self.assertTrue(agents.startswith(existing), "keeps what the file held")
                self.assertEqual(agents.count("dev\\.claude\\.lab"), 1)
                self.assertEqual(self.includes().count('include "./cfg/agents.kdl"'), 1)

    def test_a_chosen_file_is_used_and_included(self):
        cases = {
            "relative to the config's folder": ("rules/mine.kdl", "rules/mine.kdl", 'include "./rules/mine.kdl"'),
            "inside the config's folder, given in full": (
                "{niri}/rules/mine.kdl",
                "rules/mine.kdl",
                'include "./rules/mine.kdl"',
            ),
            "outside the config's folder": ("{tmp}/elsewhere/mine.kdl", None, 'include "{tmp}/elsewhere/mine.kdl"'),
            "under ~": ("~/niri-rules/mine.kdl", None, 'include "{tmp}/home/niri-rules/mine.kdl"'),
        }
        for name, (given, under_niri, include) in cases.items():
            with self.subTest(name):
                self.setUp()
                self.config("layout {}\n")
                r = self.add(given.format(niri=self.niri, tmp=self.tmp))
                self.assertEqual(r.returncode, 0, self.log)
                where = self.niri / under_niri if under_niri else Path(include.split('"')[1].format(tmp=self.tmp))
                self.assertIn(RULE, where.read_text())
                self.assertEqual(self.includes(), [include.format(tmp=self.tmp)])
                self.assertEqual(self.found(), str(where))

    def test_writes_through_a_symlinked_config(self):
        self.write(self.dotfiles / "config.kdl", "layout {}\n")
        (self.niri / "config.kdl").symlink_to(self.dotfiles / "config.kdl")
        self.assertEqual(self.add().returncode, 0, self.log)
        self.assertTrue((self.niri / "config.kdl").is_symlink(), "the link stays a link")
        self.assertIn('include "./cfg/agents.kdl"', (self.dotfiles / "config.kdl").read_text())
        self.assertEqual(self.found(), str(self.niri / "cfg/agents.kdl"))

    def test_an_invalid_result_is_undone(self):
        cases = {
            "a new file": (None,),
            "an existing file": ("// my agent rules\n",),
        }
        for name, (existing,) in cases.items():
            with self.subTest(name):
                self.setUp()
                self.config('include "./cfg/rules.kdl"\n')
                self.write(self.niri / "cfg/rules.kdl", "layout {}\n")
                if existing:
                    self.write(self.niri / "cfg/agents.kdl", existing)
                before = self.snapshot()
                r = self.add(FAKE_NIRI_INVALID="1")
                self.assertNotEqual(r.returncode, 0)
                self.assertIn("node `include` is broken", self.log)
                self.assertEqual(self.snapshot(), before)

    def test_does_nothing_when_niri_already_loads_the_rule(self):
        self.config('include "./cfg/rules.kdl"\n')
        self.write(self.niri / "cfg/rules.kdl", RULE)
        before = self.snapshot()
        r = self.add()
        self.assertEqual(r.returncode, 0, self.log)
        self.assertIn(str(self.niri / "cfg/rules.kdl"), self.log)
        self.assertEqual(self.snapshot(), before)

    def test_refuses_without_a_config(self):
        """A config.kdl holding only an include would replace niri's whole default config."""
        r = self.add()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(str(self.niri / "config.kdl"), self.log)
        self.assertEqual(self.snapshot(), {})


class RuleTest(NiriRuleTest):
    def test_prints_the_rule_it_adds(self):
        r = self.run_tool("rule")
        self.assertEqual((r.returncode, r.stdout), (0, RULE))


if __name__ == "__main__":
    unittest.main()
