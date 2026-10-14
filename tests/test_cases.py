"""tools/new_case.sh and tools/status.py: starting a case from the template, and reading each case's stage
from the files it holds. Both run against a throwaway copy of the repo."""

import re
import subprocess
import sys
import unittest

from support import scratch_repo

# Each stage's output, from the pipeline table in CONTEXT.md. 01 is done by confirming intake.md instead.
OUTPUTS = {
    "02": "02_research/findings.md",
    "03": "03_glassdoor/interviews.json",
    "04": "04_question-check/question-bank.md",
    "05": "05_report/report.md",
}


class NewCaseTest(unittest.TestCase):
    def setUp(self):
        self.repo = scratch_repo(self)

    def new_case(self, *args):
        return subprocess.run(
            ["bash", self.repo / "tools/new_case.sh", *args], capture_output=True, text=True, check=False
        )

    def intake(self, slug):
        return (self.repo / "interviews" / slug / "01_intake/intake.md").read_text()

    def test_copies_the_template_under_a_kebab_case_slug(self):
        r = self.new_case("Acme AI, Inc.", "Senior ML Engineer", "2026-11")
        self.assertEqual(r.returncode, 0, r.stderr)
        slug = "acme-ai-inc-senior-ml-engineer-2026-11"
        self.assertEqual(r.stdout.strip(), f"interviews/{slug}")
        case = self.repo / "interviews" / slug
        for folder in ("01_intake", "02_research/lanes", "03_glassdoor", "04_question-check/batches", "05_report"):
            self.assertTrue((case / folder).is_dir(), folder)
        intake = self.intake(slug)
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
                intake = self.intake(r.stdout.strip().removeprefix("interviews/"))
                self.assertIn(f"\ncompany: {company}\n", intake)
                self.assertIn(f"\nrole: {role}\n", intake)

    def test_refuses_to_overwrite_a_case(self):
        slug = self.new_case("Acme", "ML Engineer", "2026-11").stdout.strip().removeprefix("interviews/")
        path = self.repo / "interviews" / slug / "01_intake/intake.md"
        path.write_text("the user's notes")
        r = self.new_case("Acme", "ML Engineer", "2026-11")
        self.assertEqual(r.returncode, 1)
        self.assertIn("already exists", r.stderr)
        self.assertEqual(path.read_text(), "the user's notes")

    def test_needs_a_company_and_a_role(self):
        r = self.new_case("Acme")
        self.assertEqual(r.returncode, 2)
        self.assertIn("usage", r.stderr)
        self.assertEqual(list((self.repo / "interviews").iterdir()), [])


class StatusTest(unittest.TestCase):
    def setUp(self):
        self.repo = scratch_repo(self)
        out = subprocess.run(
            ["bash", self.repo / "tools/new_case.sh", "Acme", "ML Engineer", "2026-11"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.case = self.repo / out
        (self.repo / "interviews/CONTEXT.md").write_text("not a case")

    def set_field(self, key, value):
        intake = self.case / "01_intake/intake.md"
        intake.write_text(re.sub(rf"(?m)^{key}:.*$", f"{key}: {value}", intake.read_text()))

    def make(self, *stages):
        for s in stages:
            path = self.case / OUTPUTS[s]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("output")

    def status(self):
        """The case's row of _index/log.md, by column name."""
        subprocess.run([sys.executable, self.repo / "tools/status.py"], capture_output=True, check=True)
        lines = (self.repo / "_index/log.md").read_text().splitlines()
        table = [[c.strip() for c in line.strip("|").split("|")] for line in lines if line.startswith("|")]
        head, rows = table[0], table[2:]
        self.assertEqual(len(rows), 1, "one row per case folder")
        return dict(zip(head, rows[0]))

    def test_a_new_case_waits_on_intake(self):
        row = self.status()
        self.assertEqual((row["Done"], row["Next"]), ("-", "01"))
        self.assertEqual((row["Company"], row["Role"]), ("Acme", "ML Engineer"))
        self.assertIn("(../interviews/acme-ml-engineer-2026-11/)", row["Case"])

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


if __name__ == "__main__":
    unittest.main()
