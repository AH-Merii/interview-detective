"""setup/wizard.sh: the checks it makes before asking the user to do anything. The stages wait on a person,
so the tests source the wizard, which stops before them, and call its helpers."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from support import ROOT

RULE = 'window-rule {\n    match app-id=r#"^dev\\.claude\\.lab$"#\n    open-focused false\n}\n'


class NiriRuleTest(unittest.TestCase):
    """The wizard finds the browser's window rule wherever the niri config keeps it, so it never asks the user
    to add a rule they already have."""

    def fresh(self):
        """A new, empty niri config folder, and a dotfiles folder its symlinks can point into."""
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.niri = self.tmp / "config/niri"
        self.dotfiles = self.tmp / "dotfiles"  # where a symlinked config really lives
        self.niri.mkdir(parents=True)
        self.dotfiles.mkdir()

    def has_rule(self):
        env = os.environ | {"XDG_CONFIG_HOME": str(self.tmp / "config"), "HOME": str(self.tmp)}
        r = subprocess.run(
            ["bash", "-c", 'source "$1" && has_rule', "bash", ROOT / "setup/wizard.sh"],
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        self.assertIn(r.returncode, (0, 1), r.stderr)
        return r.returncode == 0

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_finds_the_rule_however_the_config_is_laid_out(self):
        layouts = {
            "in config.kdl": lambda: self.write(self.niri / "config.kdl", RULE),
            "in an included file": lambda: self.write(self.niri / "cfg/agents.kdl", RULE),
            "in a symlinked config.kdl": lambda: (self.niri / "config.kdl").symlink_to(
                self.write(self.dotfiles / "config.kdl", RULE)
            ),
            "in a symlinked included file": lambda: (
                (self.niri / "cfg").mkdir(),
                (self.niri / "cfg/agents.kdl").symlink_to(self.write(self.dotfiles / "agents.kdl", RULE)),
            ),
            "in a symlinked folder of included files": lambda: (self.niri / "cfg").symlink_to(
                self.write(self.dotfiles / "cfg/agents.kdl", RULE).parent
            ),
        }
        for name, lay_out in layouts.items():
            with self.subTest(name):
                self.fresh()
                lay_out()
                self.write(self.niri / "other.kdl", "layout {}\n")
                self.assertTrue(self.has_rule())

    def test_a_config_without_the_rule_has_none(self):
        self.fresh()
        self.write(self.niri / "config.kdl", 'window-rule {\n    match app-id="firefox"\n}\n')
        (self.niri / "cfg").mkdir()
        (self.niri / "cfg/agents.kdl").symlink_to(self.write(self.dotfiles / "agents.kdl", "layout {}\n"))
        self.assertFalse(self.has_rule())


if __name__ == "__main__":
    unittest.main()
