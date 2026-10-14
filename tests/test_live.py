"""The one check against the real Glassdoor, off by default: it needs the browser running, logged in.

  uv run tools/browser.py start URL   # log in and clear any check in the window
  ID_LIVE_GLASSDOOR=URL python3 -m unittest tests.test_live   (from the repo root, with websocket-client)

It reads page 1 of URL, an interviews page, the way `glassdoor.py scrape` does, and checks the records
still carry the fields normalize reads. Run it when a scrape comes back empty or odd.
"""

import os
import unittest

import support  # noqa: F401  (puts tools/ on sys.path)

URL = os.environ.get("ID_LIVE_GLASSDOOR")


@unittest.skipUnless(URL, "set ID_LIVE_GLASSDOOR to an interviews page URL to run")
class LiveGlassdoorTest(unittest.TestCase):
    def test_page_one_carries_records_and_a_count(self):
        import glassdoor

        items, count = glassdoor.load(glassdoor.Tab("glassdoor"), URL)
        self.assertGreater(count or 0, 0, "no filteredInterviewCount on the page")
        self.assertTrue(items)
        for field in ("id", "jobTitle", "reviewDateTime", "outcome", "difficulty", "userQuestions"):
            self.assertIn(field, items[0])
        self.assertTrue(
            glassdoor.next_url(glassdoor.Tab("glassdoor"), 2) or count <= len(items),
            "more reviews than one page, but no link to page 2",
        )


if __name__ == "__main__":
    unittest.main()
