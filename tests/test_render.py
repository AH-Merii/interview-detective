"""tools/render.py: the HTML pages the user reads, made from a case's markdown and its why/claims.json files.

The markdown is the subset the stages write: headings, paragraphs, nested lists, tables, quotes, code
and links. Cases are built in a throwaway folder.
"""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from support import ROOT

# isort: split
import render


def run(*args):
    return subprocess.run(
        [sys.executable, ROOT / "tools/render.py", *args], capture_output=True, text=True, check=False
    )


def squash(html):
    """The html with the whitespace between tags removed, so structure can be matched in one regex."""
    return re.sub(r">\s+<", "><", html)


class MarkdownTest(unittest.TestCase):
    def test_a_nested_item_sits_inside_its_parent_item(self):
        html = squash(render.to_html("- parent\n  - child\n- sibling\n"))
        self.assertRegex(html, r"<ul><li>parent<ul><li>child</li></ul></li><li>sibling</li></ul>")

    def test_an_item_s_wrapped_lines_join_its_text(self):
        html = squash(render.to_html("- **A claim that\n  wraps** — confirmed\n- next\n"))
        self.assertIn("<li><strong>A claim that wraps</strong>", html)
        self.assertEqual(html.count("<li>"), 2)

    def test_numbered_items_make_an_ordered_list(self):
        html = squash(render.to_html("1. first\n2. second\n"))
        self.assertIn("<ol><li>first</li><li>second</li></ol>", html)

    def test_a_pipe_table_gets_header_and_body_cells(self):
        html = squash(render.to_html("| Group | Count |\n|---|---|\n| A | 2 |\n| B | 3 |\n"))
        self.assertRegex(html, r"<thead><tr><th>Group</th><th>Count</th></tr></thead>")
        self.assertRegex(html, r"<tr><td>A</td><td>2</td></tr><tr><td>B</td><td>3</td></tr>")

    def test_code_keeps_its_text_literal(self):
        html = render.to_html("```python\nif a < b and **kw:\n    pass\n```\n\nRun `**x**` here.\n")
        self.assertIn("if a &lt; b and **kw:\n    pass", html)
        self.assertIn("<code>**x**</code>", html)
        self.assertNotIn("<strong>", html)

    def test_markup_in_the_text_is_shown_not_run(self):
        html = render.to_html('A review said <script>alert("x")</script> & left.\n')
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_links_and_bare_urls_become_links(self):
        html = render.to_html("See [the docs](https://a.example/x) and https://b.example/y.\n")
        self.assertIn('<a href="https://a.example/x">the docs</a>', html)
        self.assertIn('<a href="https://b.example/y">https://b.example/y</a>.', html)

    def test_only_web_and_relative_links_are_followed(self):
        html = render.to_html("[a](javascript:alert(1)) [b](why/b.html) [c](data:text/html,x)\n")
        self.assertIn('href="why/b.html"', html)
        self.assertNotRegex(html, r'href="(javascript|data):')

    def test_a_quote_becomes_a_blockquote(self):
        html = squash(render.to_html("> started out simple\n> with extensions\n"))
        self.assertIn("<blockquote><p>started out simple with extensions</p></blockquote>", html)

    def test_why_links_and_confidence_labels_are_marked(self):
        html = render.to_html(
            "- A guess ([why](why/a.html)) — speculative\n- Most likely a guess — confirmed, checked\n"
        )
        self.assertIn('<a class="why" href="why/a.html">why</a>', html)
        self.assertIn('<span class="conf speculative">speculative</span>', html)
        self.assertIn('<span class="conf confirmed">confirmed</span>', html)
        self.assertIn("Most likely a guess", html, "a word in prose stays plain")

    def test_a_verdict_is_marked(self):
        html = render.to_html("- **Verdict:** company-specific\n")
        self.assertIn('<span class="conf company-specific">company-specific</span>', html)

    def test_each_h3_section_is_its_own_card(self):
        html = squash(render.to_html("## Bank\n### Q1. One\n- a\n### Q2. Two\n- b\n## After\ntext\n"))
        cards = re.findall(r'<section class="card">(.*?)</section>', html)
        self.assertEqual(len(cards), 2)
        self.assertIn("Q1. One", cards[0])
        self.assertIn("<li>a</li>", cards[0])
        self.assertIn("<li>b</li>", cards[1])
        self.assertNotIn("text", cards[1])

    def test_the_first_h2_section_is_highlighted(self):
        html = squash(render.to_html("# Title\n\n## Summary\n\nThe gist.\n\n## Findings\n\nMore.\n"))
        lead = re.search(r'<section class="lead">(.*?)</section>', html)
        assert lead, html
        self.assertIn("The gist.", lead[1])
        self.assertNotIn("More.", lead[1])


CLAIMS = [
    {
        "slug": "no-ml",
        "confidence": "likely",
        "claim": "Expect no ML questions in Round 1.",
        "premises": [
            {
                "shows": "The round is the same for every engineer.",
                "quote": "API Integration Interview - 1 hour",
                "source": "Senior SWE post",
                "link": "https://jobs.example/senior-swe",
                "checked": True,
            },
            {
                "shows": "The kit describes the task.",
                "quote": "process a matrix of data",
                "source": "Prep kit · intake.md:3",
                "link": "01_intake/intake.md:3",
            },
        ],
        "reasoning": ["The round is shared [1], and its task has no ML in it [2]."],
        "against": [
            "The ML post has no process section.",
            {"quote": "not Relay specific", "source": "Prep kit · intake.md:4", "link": "01_intake/intake.md:4"},
        ],
        "settle": ["Ask the recruiter."],
        "related": ["other"],
    },
    {
        "slug": "other",
        "confidence": "speculative",
        "claim": "Another guess.",
        "premises": [{"shows": "A hint.", "source": "A page", "link": "https://example.com/hint"}],
        "reasoning": ["It follows [1]."],
    },
]


class RenderCaseTest(unittest.TestCase):
    def setUp(self):
        self.case = Path(self.enterContext(tempfile.TemporaryDirectory())) / "acme-ml-engineer-2026-11"
        for folder in ("01_intake", "02_research/why", "04_question-check", "05_report"):
            (self.case / folder).mkdir(parents=True)
        (self.case / "01_intake/intake.md").write_text("# Intake\n\nprocess a matrix of data\nnot Relay specific\n")
        (self.case / "02_research/findings.md").write_text("# Findings\n\n- A finding ([why](why/no-ml.html))\n")
        (self.case / "04_question-check/question-bank.md").write_text(
            "# Bank\n\n### Q1. Two Sum\n- **Verdict:** standard\n"
        )

    def write_claims(self, claims):
        (self.case / "02_research/why/claims.json").write_text(json.dumps(claims))

    def test_renders_each_reading_page_the_case_has_and_says_how_to_open_it(self):
        r = run(str(self.case))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.case / "02_research/findings.html").is_file())
        self.assertTrue((self.case / "04_question-check/question-bank.html").is_file())
        self.assertFalse((self.case / "05_report/report.html").exists(), "no report.md, so no page")
        lines = r.stdout.strip().splitlines()
        self.assertEqual(len(lines), 2, r.stdout)
        self.assertIn(str((self.case / "02_research/findings.html").resolve()), lines[0])
        self.assertIn(str((self.case / "04_question-check/question-bank.html").resolve()), lines[1])

    def test_a_page_links_to_the_case_s_other_reading_pages(self):
        run(str(self.case))
        html = (self.case / "02_research/findings.html").read_text()
        self.assertIn('href="../04_question-check/question-bank.html"', html)
        self.assertNotIn("report.html", html)

    def test_a_claim_becomes_a_page_that_shows_what_it_rests_on(self):
        self.write_claims(CLAIMS)
        r = run(str(self.case))
        self.assertEqual(r.returncode, 0, r.stderr)
        page = self.case / "02_research/why/no-ml.html"
        html = page.read_text()
        for text in (
            "Expect no ML questions in Round 1.",
            "API Integration Interview - 1 hour",
            "process a matrix of data",
            "The round is shared [1]",
            "The ML post has no process section.",
            "not Relay specific",
            "Ask the recruiter.",
        ):
            self.assertIn(text, html)
        self.assertIn('href="https://jobs.example/senior-swe"', html)
        self.assertIn('href="../findings.html"', html)
        self.assertIn('href="other.html"', html)
        self.assertIn("Another guess.", html, "a related claim is named by its claim")
        intake = re.search(r'href="([^"]*intake\.md[^"]*)"', html)
        assert intake, html
        self.assertTrue((page.parent / intake[1].split("#")[0]).resolve().samefile(self.case / "01_intake/intake.md"))
        premises = re.search(r'<ol class="premises">(.*?)</ol>', html, re.DOTALL)
        assert premises, html
        self.assertEqual(
            re.findall(r'class="chip (checked|lane)"', premises[1]),
            ["checked", "lane"],
            "the first premise was re-read first-hand, the second only by a lane",
        )
        self.assertTrue((self.case / "02_research/why/other.html").is_file())

    def test_a_claim_missing_a_required_field_is_named(self):
        broken = [dict(CLAIMS[1], slug="half")]
        del broken[0]["reasoning"]
        self.write_claims(broken)
        r = run(str(self.case))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("half", r.stderr)
        self.assertIn("reasoning", r.stderr)

    def test_refuses_a_folder_that_is_not_a_case(self):
        r = run(str(self.case / "missing"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("missing", r.stderr)


if __name__ == "__main__":
    unittest.main()
