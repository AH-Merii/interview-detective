"""tools/glassdoor.py: reading every page of a review list out of the browser, and shaping the records.

The browser is faked as a site of pages; each page holds what Glassdoor embeds in it (the Next.js flight
pushes) and its pager links. tests/test_live.py checks the real site.
"""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import support  # noqa: F401  (first: it puts tools/ on sys.path)

# isort: split
import glassdoor

BASE = "https://www.glassdoor.co.uk/Interview/Acme-Interview-Questions-E1.htm"


def page_url(base, n):
    return base if n == 1 else base.replace(".htm", f"_P{n}.htm")


def record(id, role="Machine Learning Engineer", reviewed="2026-01-01T10:00:00", **fields):
    """A raw record with the fields Glassdoor sends, filled with made-up values."""
    r = {
        "id": id,
        "jobTitle": {"text": role},
        "reviewDateTime": reviewed,
        "interviewDateTime": None,
        "outcome": "NO_OFFER",
        "experience": "POSITIVE",
        "difficulty": "AVERAGE",
        "source": "APPLIED_ONLINE",
        "durationDays": 14,
        "processDescription": "Two rounds.",
        "userQuestions": [],
        "countHelpful": 0,
        "employerResponses": [],
        "location": {"name": "London, England", "type": "CITY"},
    }
    r.update(fields)
    return r


def scripts(items, count):
    """The page's flight pushes as Glassdoor sends them: the records sit inside a JSON-encoded string,
    among pushes that hold other things."""
    data = {"interviews": items, "other": 1}
    if count is not None:
        data["filteredInterviewCount"] = count
    flight = '5:["$","$L6",null,' + json.dumps(data, separators=(",", ":")) + "]\n"  # compact, as Next.js writes it
    return [
        "self.__next_f.push([0])",
        f"self.__next_f.push([1,{json.dumps('2:I[123,[],' + chr(34) + 'default' + chr(34) + ']' + chr(10))}])",
        f"self.__next_f.push([1,{json.dumps(flight)}])",
    ]


def paged(records, per=5, count="all", base=BASE):
    """A review list split into pages of `per`, each linking every page after the first. `count` is the total
    the page claims: by default every record, None for none."""
    chunks = [records[i : i + per] for i in range(0, len(records), per)] or [[]]
    last = len(chunks)
    count = len(records) if count == "all" else count
    links = [page_url(base, n) for n in range(2, last + 1)]
    return {page_url(base, n): {"scripts": scripts(chunk, count), "links": links} for n, chunk in enumerate(chunks, 1)}


class FakeSite:
    """The browser on a fixed set of pages: url -> {"scripts", "links", "title"}."""

    def __init__(self, *page_sets):
        self.pages = {k: v for p in page_sets for k, v in p.items()}
        self.visits = []

    def tab(self, _sel=None):
        site = self

        class Tab:
            url = None

            def goto(self, url):
                site.visits.append(url)
                self.url = url

            def js(self, expr):
                page = site.pages[self.url]
                if "document.scripts" in expr:
                    return page.get("scripts", [])
                if "a[href]" in expr:
                    return page.get("links", [])
                if "document.title" in expr:
                    return page.get("title", "")
                raise AssertionError(f"unexpected js: {expr}")

        return Tab()


class ScrapeTest(unittest.TestCase):
    def scrape(self, site, *urls):
        out = Path(self.enterContext(tempfile.TemporaryDirectory())) / "raw.json"
        self.sleeps = []
        with (
            mock.patch.object(glassdoor, "Tab", site.tab),
            mock.patch.object(glassdoor.time, "sleep", self.sleeps.append),
            contextlib.redirect_stdout(io.StringIO()) as log,
        ):
            glassdoor.scrape(out, urls)
        self.log = log.getvalue()
        return json.loads(out.read_text())

    def test_reads_every_page_of_a_list(self):
        site = FakeSite(paged([record(i) for i in range(1, 13)]))
        got = self.scrape(site, BASE)
        self.assertEqual(sorted(r["id"] for r in got), list(range(1, 13)))
        self.assertEqual(site.visits, [BASE, page_url(BASE, 2), page_url(BASE, 3)])

    def test_stops_once_it_has_the_count_even_if_the_pager_goes_on(self):
        site = FakeSite(paged([record(i) for i in range(1, 16)], count=10))
        got = self.scrape(site, BASE)
        self.assertEqual(len(got), 10)
        self.assertNotIn(page_url(BASE, 3), site.visits)

    def test_without_a_count_reads_until_there_is_no_next_page(self):
        got = self.scrape(FakeSite(paged([record(i) for i in range(1, 9)], count=None)), BASE)
        self.assertEqual(len(got), 8)

    def test_keeps_what_it_has_when_the_next_page_has_no_link(self):
        site = FakeSite({BASE: {"scripts": scripts([record(i) for i in range(1, 6)], 12), "links": []}})
        got = self.scrape(site, BASE)
        self.assertEqual(len(got), 5)
        self.assertIn("no link to page 2", self.log)

    def test_an_interview_under_two_role_filters_is_kept_once(self):
        ml, ds = BASE.replace(".htm", "_JT1.htm"), BASE.replace(".htm", "_JT2.htm")
        site = FakeSite(
            paged([record(1), record(2), record(3)], base=ml),
            paged([record(3, role="Data Scientist"), record(4, role="Data Scientist")], base=ds),
        )
        got = self.scrape(site, ml, ds)
        self.assertEqual(sorted(r["id"] for r in got), [1, 2, 3, 4])

    def test_waits_a_person_s_pace_between_pages(self):
        self.scrape(FakeSite(paged([record(i) for i in range(1, 13)])), BASE)
        self.assertEqual(len(self.sleeps), 2)
        for s in self.sleeps:
            self.assertGreaterEqual(s, 3)

    def test_text_that_looks_like_json_survives_intact(self):
        q = 'Given "a]b", return [x for x in y]}, ok? naïve, 日本'
        got = self.scrape(FakeSite(paged([record(1, userQuestions=[{"id": 9, "question": q}])])), BASE)
        self.assertEqual(got[0]["userQuestions"][0]["question"], q)

    def test_a_page_without_reviews_stops_and_says_why(self):
        site = FakeSite({BASE: {"scripts": [], "title": "Just a moment..."}})
        with self.assertRaises(SystemExit) as e:
            self.scrape(site, BASE)
        self.assertIn("Just a moment...", str(e.exception.code))
        self.assertIn("ask the user", str(e.exception.code))


SCOPE = {
    "company": "Acme",
    "urls": [BASE],
    "groups": {
        "A": {"priority": "high", "roles": ["Machine Learning Engineer"]},
        "B": {"priority": "medium", "roles": ["Data Scientist"]},
        "C": {"priority": "low", "default": True},
    },
}


class NormalizeTest(unittest.TestCase):
    def normalize(self, raw):
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (tmp / "raw.json").write_text(json.dumps(raw))
        (tmp / "scope.json").write_text(json.dumps(SCOPE))
        with contextlib.redirect_stdout(io.StringIO()):
            glassdoor.normalize(tmp / "raw.json", tmp / "scope.json", tmp / "out.json")
        return json.loads((tmp / "out.json").read_text())

    def test_groups_roles_by_the_scope_ignoring_case_and_spaces(self):
        cases = {
            "Machine Learning Engineer": ("A", "high"),
            "  machine LEARNING engineer ": ("A", "high"),
            "Data Scientist": ("B", "medium"),
            "Product Manager": ("C", "low"),
            None: ("C", "low"),
        }
        raw = [record(i, jobTitle={"text": role} if role else None) for i, role in enumerate(cases)]
        got = {r["id"]: (r["group"], r["priority"]) for r in self.normalize(raw)["interviews"]}
        for i, (role, want) in enumerate(cases.items()):
            with self.subTest(role=role):
                self.assertEqual(got[i], want)

    def test_newest_review_first(self):
        raw = [
            record(1, reviewed="2025-03-01T00:00:00"),
            record(2, reviewed="2026-07-01T00:00:00"),
            record(3, reviewed="2025-11-01T00:00:00"),
        ]
        self.assertEqual([r["id"] for r in self.normalize(raw)["interviews"]], [2, 3, 1])

    def test_record_shape(self):
        raw = [
            record(
                7,
                reviewed="2026-02-03T04:05:06.7",
                interviewDateTime="2026-01-01T00:00:00",
                outcome="ACCEPT_OFFER",
                experience="NEUTRAL",
                difficulty=None,
                userQuestions=[{"id": 1, "question": "Reverse a list", "answerCount": 0}],
                employerResponses=[{"response": "Thanks", "responseDateTime": "2026-02-04"}],
            )
        ]
        out = self.normalize(raw)
        self.assertEqual((out["company"], out["count"]), ("Acme", 1))
        self.assertEqual(
            out["interviews"][0],
            {
                "id": 7,
                "role": "Machine Learning Engineer",
                "group": "A",
                "priority": "high",
                "location": "London, England",
                "review_date": "2026-02-03",
                "interview_date": "2026-01",
                "outcome": "accept_offer",
                "experience": "neutral",
                "difficulty": None,
                "how_obtained": "applied_online",
                "duration_days": 14,
                "process": "Two rounds.",
                "questions": ["Reverse a list"],
                "helpful": 0,
                "employer_responses": ["Thanks"],
            },
        )


class SummaryTest(unittest.TestCase):
    def test_processes_cover_groups_a_and_b_only_and_stats_count_every_group(self):
        rows = [
            {
                "id": i,
                "role": role,
                "group": g,
                "priority": p,
                "review_date": "2026-01-0" + str(i),
                "outcome": "no_offer",
                "experience": "positive",
                "difficulty": "easy",
                "how_obtained": "applied_online",
                "process": f"process {g}{i}",
                "questions": [f"question {g}{i}"],
            }
            for i, (role, g, p) in enumerate(
                [("MLE", "A", "high"), ("MLE", "A", "high"), ("DS", "B", "medium"), ("PM", "C", "low")], 1
            )
        ]
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (tmp / "interviews.json").write_text(
            json.dumps({"company": "Acme", "scraped": "2026-10-14", "count": 4, "interviews": rows})
        )
        with contextlib.redirect_stdout(io.StringIO()):
            glassdoor.summary(tmp / "interviews.json", tmp)
        procs, stats = (tmp / "processes.md").read_text(), (tmp / "stats.md").read_text()
        for kept in ("question A1", "question A2", "question B3", "process B3"):
            self.assertIn(kept, procs)
        self.assertNotIn("C4", procs)
        for line in (
            "Group A (high priority): 2 interviews",
            "Group B (medium priority): 1 interviews",
            "Group C (low priority): 1 interviews",
        ):
            self.assertIn(line, stats)


if __name__ == "__main__":
    unittest.main()
