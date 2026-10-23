"""tools/check.py: a case's sources still say what its pages claim, and its pages' links resolve.

Each test builds a small case in a throwaway folder, then edits it the way a stage or the user would.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from support import ROOT

INTAKE = """# Intake

- Round 1: API integration, 60 min.
  You'll read through the documentation of a particular public API, make API
  calls against it, and then process a matrix of data.
- Both are industry standard design interviews and not Relay specific.
"""


def premise(quote, link):
    return {"shows": "What it shows.", "quote": quote, "source": "Prep kit", "link": link}


def claim(slug, *premises, related=()):
    return {
        "slug": slug,
        "confidence": "speculative",
        "claim": f"A claim called {slug}.",
        "premises": list(premises),
        "reasoning": ["It follows [1]."],
        "related": list(related),
    }


class CheckTest(unittest.TestCase):
    def setUp(self):
        self.case = Path(self.enterContext(tempfile.TemporaryDirectory())) / "acme-ml-engineer-2026-11"
        for folder in ("01_intake", "02_research/why"):
            (self.case / folder).mkdir(parents=True)
        self.intake = self.case / "01_intake/intake.md"
        self.intake.write_text(INTAKE)
        self.claims(
            [
                claim(
                    "task",
                    premise(
                        "read through the documentation of a particular public API, make API calls"
                        " against it · process a matrix of data",
                        "01_intake/intake.md:4-5",
                    ),
                )
            ]
        )

    def claims(self, claims):
        (self.case / "02_research/why/claims.json").write_text(json.dumps(claims))

    def check(self):
        return subprocess.run(
            [sys.executable, ROOT / "tools/check.py", str(self.case)], capture_output=True, text=True, check=False
        )

    def test_passes_when_each_quote_sits_at_the_lines_it_cites(self):
        r = self.check()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ok", r.stdout)

    def test_a_quote_that_moved_names_the_line_it_is_on_now(self):
        self.intake.write_text("# Intake\n\nA note added later.\n\n" + INTAKE.split("\n", 2)[2])
        r = self.check()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("task", r.stdout)
        self.assertIn("01_intake/intake.md:4-5", r.stdout)
        self.assertIn("lines 6-7", r.stdout)

    def test_a_quote_the_source_no_longer_has_fails(self):
        self.intake.write_text(INTAKE.replace("process a matrix", "transform a table"))
        r = self.check()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("process a matrix of data", r.stdout)
        self.assertIn("not found", r.stdout)

    def test_a_quote_whose_lines_are_too_narrow_fails(self):
        self.claims([claim("task", premise("process a matrix of data", "01_intake/intake.md:4"))])
        r = self.check()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("line 5", r.stdout)

    def test_a_quote_without_lines_may_sit_anywhere_in_its_file(self):
        self.claims([claim("task", premise("not Relay specific", "01_intake/intake.md"))])
        self.assertEqual(self.check().returncode, 0)
        self.claims([claim("task", premise("Relay specific and generic", "01_intake/intake.md"))])
        self.assertEqual(self.check().returncode, 1)

    def test_a_quote_from_a_file_that_is_missing_fails(self):
        self.claims([claim("task", premise("anything", "01_intake/gone.md:1"))])
        r = self.check()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("01_intake/gone.md", r.stdout)

    def test_a_related_claim_that_does_not_exist_fails(self):
        self.claims([claim("task", premise("process a matrix of data", "01_intake/intake.md:5"), related=["nope"])])
        r = self.check()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("nope", r.stdout)

    def test_a_line_reference_in_a_reading_page_must_exist(self):
        findings = self.case / "02_research/findings.md"
        findings.write_text("- The task — `01_intake/intake.md:4-5` — confirmed\n")
        self.assertEqual(self.check().returncode, 0, self.check().stdout)
        for ref in ("01_intake/intake.md:4-40", "01_intake/missing.md:1"):
            findings.write_text(f"- The task — `{ref}` — confirmed\n")
            r = self.check()
            self.assertEqual(r.returncode, 1, ref)
            self.assertIn(ref, r.stdout)

    def test_a_local_link_to_a_missing_file_fails_and_web_links_are_left_alone(self):
        (self.case / "02_research/findings.html").write_text(
            '<a href="why/gone.html">why</a> <a href="https://example.com/x">x</a> <a href="#top">top</a>'
            ' <a href="../01_intake/intake.md#L4">intake</a>'
        )
        r = self.check()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("why/gone.html", r.stdout)
        self.assertNotIn("example.com", r.stdout)
        self.assertNotIn("intake.md", r.stdout)


if __name__ == "__main__":
    unittest.main()
