"""tools/new_case.sh and tools/status.py: starting a case from the template, reading each case's stage from
the files it holds, and finding the user's cases folder. Both run against a throwaway cases folder."""

import re
import subprocess
import sys
import unittest
from pathlib import Path

from support import ROOT, scratch_cases

# Each stage's output, from the pipeline table in CONTEXT.md. 01 is done by confirming intake.md instead.
OUTPUTS = {
    "02": "02_research/findings.md",
    "03": "03_glassdoor/interviews.json",
    "04": "04_question-check/question-bank.md",
    "05": "05_report/report.md",
}


def run(env, tool, *args):
    cmd = ["bash", ROOT / "tools/new_case.sh"] if tool == "new_case" else [sys.executable, ROOT / "tools/status.py"]
    return subprocess.run([*cmd, *args], env=env, capture_output=True, text=True, check=False)


class NewCaseTest(unittest.TestCase):
    def setUp(self):
        self.cases, self.env = scratch_cases(self)

    def new_case(self, *args):
        return run(self.env, "new_case", *args)

    def test_copies_the_template_under_a_kebab_case_slug(self):
        r = self.new_case("Acme AI, Inc.", "Senior ML Engineer", "2026-11")
        self.assertEqual(r.returncode, 0, r.stderr)
        case = self.cases / "acme-ai-inc-senior-ml-engineer-2026-11"
        self.assertEqual(r.stdout.strip(), str(case))
        for folder in ("01_intake", "02_research/lanes", "03_glassdoor", "04_question-check/batches", "05_report"):
            self.assertTrue((case / folder).is_dir(), folder)
        intake = (case / "01_intake/intake.md").read_text()
        self.assertRegex(intake, r"(?m)^opened: \d{4}-\d\d-\d\d$")
        self.assertRegex(intake, r"(?m)^confirmed: false$")

    def test_writes_company_and_role_into_intake_exactly_as_given(self):
        for company, role in [
            ("Acme", "ML Engineer"),
            ("AT&T", "R&D Engineer"),
            ("R/GA", "ML/AI Engineer"),
            ("Back\\slash", "C++ | Rust"),
        ]:
            with self.subTest(company=company, role=role):
                r = self.new_case(company, role, "2026-11")
                self.assertEqual(r.returncode, 0, r.stderr)
                intake = (Path(r.stdout.strip()) / "01_intake/intake.md").read_text()
                self.assertIn(f"\ncompany: {company}\n", intake)
                self.assertIn(f"\nrole: {role}\n", intake)

    def test_refuses_to_overwrite_a_case(self):
        path = Path(self.new_case("Acme", "ML Engineer", "2026-11").stdout.strip()) / "01_intake/intake.md"
        path.write_text("the user's notes")
        r = self.new_case("Acme", "ML Engineer", "2026-11")
        self.assertEqual(r.returncode, 1)
        self.assertIn("already exists", r.stderr)
        self.assertEqual(path.read_text(), "the user's notes")

    def test_needs_a_company_and_a_role(self):
        r = self.new_case("Acme")
        self.assertEqual(r.returncode, 2)
        self.assertIn("usage", r.stderr)
        self.assertFalse(self.cases.exists() and any(self.cases.iterdir()))


class StatusTest(unittest.TestCase):
    def setUp(self):
        self.cases, self.env = scratch_cases(self)
        self.case = Path(run(self.env, "new_case", "Acme", "ML Engineer", "2026-11").stdout.strip())
        (self.cases / "notes").mkdir()  # the user's own folder, not a case

    def set_field(self, key, value):
        intake = self.case / "01_intake/intake.md"
        intake.write_text(re.sub(rf"(?m)^{key}:.*$", f"{key}: {value}", intake.read_text()))

    def make(self, *stages):
        for s in stages:
            path = self.case / OUTPUTS[s]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("output")

    def status(self):
        """The case's row of <cases>/log.md, by column name."""
        r = run(self.env, "status")
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = (self.cases / "log.md").read_text().splitlines()
        table = [[c.strip() for c in line.strip("|").split("|")] for line in lines if line.startswith("|")]
        head, rows = table[0], table[2:]
        self.assertEqual(len(rows), 1, "one row per case folder")
        return dict(zip(head, rows[0]))

    def test_a_new_case_waits_on_intake(self):
        row = self.status()
        self.assertEqual((row["Done"], row["Next"]), ("-", "01"))
        self.assertEqual((row["Company"], row["Role"]), ("Acme", "ML Engineer"))
        self.assertIn("(acme-ml-engineer-2026-11/)", row["Case"], "links resolve from log.md, beside the cases")

    def test_each_stage_is_done_only_by_its_own_output(self):
        self.set_field("confirmed", "true")
        self.assertEqual((self.status()["Done"], self.status()["Next"]), ("01", "02"))
        done = ["01"]
        for stage in OUTPUTS:
            with self.subTest(stage=stage):
                self.make(stage)
                done.append(stage)
                row = self.status()
                self.assertEqual(row["Done"], " ".join(done))
                self.assertEqual(row["Next"], {"02": "03", "03": "04", "04": "05", "05": "finished"}[stage])

    def test_next_is_the_first_stage_not_done(self):
        self.set_field("confirmed", "true")
        self.make("03", "04")
        row = self.status()
        self.assertEqual((row["Done"], row["Next"]), ("01 03 04", "02"))

    def test_glassdoor_is_done_when_the_company_has_no_page(self):
        (self.case / "03_glassdoor/skipped.md").write_text("no Glassdoor page")
        self.assertEqual(self.status()["Done"], "03")

    def test_an_empty_field_reads_as_empty(self):
        self.assertEqual(self.status()["Interview date"], "")
        self.set_field("interview_date", "2026-11-20")
        self.assertEqual(self.status()["Interview date"], "2026-11-20")

    def test_prints_where_the_cases_are(self):
        self.assertIn(str(self.cases), run(self.env, "status").stdout)


class CasesFolderTest(unittest.TestCase):
    """Both tools find the cases folder the same way: ID_CASES_DIR, else the one the setup wizard saved in
    $XDG_CONFIG_HOME/interview-detective/config.env; with neither, they refuse and name the wizard."""

    TOOLS = (("new_case", ("Acme", "ML Engineer", "2026-11")), ("status", ()))

    def setUp(self):
        self.cases, env = scratch_cases(self)
        self.config = Path(env["XDG_CONFIG_HOME"]) / "interview-detective/config.env"
        self.unset = {k: v for k, v in env.items() if k != "ID_CASES_DIR"}

    def save(self, *lines):
        self.config.parent.mkdir(parents=True, exist_ok=True)
        self.config.write_text("".join(f"{line}\n" for line in lines))

    def wrote_a_case_in(self, folder):
        return (folder / "acme-ml-engineer-2026-11").is_dir() or (folder / "log.md").exists()

    def test_uses_the_folder_the_wizard_saved(self):
        old, saved = self.cases.parent / "old", self.cases.parent / "saved"
        self.save("OTHER=1", f"ID_CASES_DIR={old}", f"ID_CASES_DIR={saved}")  # the wizard appends on a re-run
        for tool, args in self.TOOLS:
            with self.subTest(tool=tool):
                r = run(self.unset, tool, *args)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertTrue(self.wrote_a_case_in(saved))
                self.assertFalse(old.exists())

    def test_id_cases_dir_wins_over_the_saved_folder(self):
        saved = self.cases.parent / "saved"
        self.save(f"ID_CASES_DIR={saved}")
        for tool, args in self.TOOLS:
            with self.subTest(tool=tool):
                r = run(self.unset | {"ID_CASES_DIR": str(self.cases)}, tool, *args)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertTrue(self.wrote_a_case_in(self.cases))
                self.assertFalse(saved.exists())

    def test_without_setup_refuses_and_names_the_wizard(self):
        for config in (None, "OTHER=1"):
            if config:
                self.save(config)
            for tool, args in self.TOOLS:
                with self.subTest(tool=tool, config=config):
                    r = run(self.unset, tool, *args)
                    self.assertNotEqual(r.returncode, 0)
                    self.assertIn(f"bash {ROOT}/setup/wizard.sh", r.stderr)
                    self.assertFalse(self.cases.exists())


if __name__ == "__main__":
    unittest.main()
