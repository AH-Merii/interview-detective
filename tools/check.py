#!/usr/bin/env python3
"""Check that a case's sources still say what its pages claim, and that its pages' links resolve.

Run with: uv run tools/check.py <case>     (after tools/render.py, so the html is current)

  - every quote in a <stage>/why/claims.json sits at the lines its case path cites
    (`01_intake/intake.md:145-147`), or anywhere in the file when no lines are given. A quote may join
    fragments with " · " or "…"; each must be there. A quote that moved names the line it is on now.
  - every related claim exists;
  - every case path with lines in findings.md, question-bank.md and report.md points inside its file;
  - every local link in the case's html points to a file that exists.

Prints one line per problem and exits 1, or prints what it checked and exits 0.
"""

import bisect
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

READING = ("02_research/findings.md", "04_question-check/question-bank.md", "05_report/report.md")
CASE_REF = re.compile(r"(\d\d_[\w-]+/[\w./-]+\.\w+):(\d+)(?:-(\d+))?")


class Source:
    """A file's text with its whitespace collapsed, mapped back to line numbers."""

    def __init__(self, path):
        lines = path.read_text().splitlines()
        self.count = len(lines)
        self.starts, parts, pos = [], [], 0
        for line in lines:
            self.starts.append(pos)
            text = " ".join(line.split())
            parts.append(text)
            pos += len(text) + 1
        self.text = " ".join(parts)

    def find(self, fragment, first=1, last=None):
        """The lines a fragment spans, as "N" or "N-M", searching lines first..last; "" when it isn't there."""
        lo = self.starts[first - 1] if first <= self.count else len(self.text)
        hi = self.starts[last] if last and last < self.count else len(self.text)
        fragment = " ".join(fragment.split())
        at = self.text.find(fragment, lo, hi)
        if at < 0:
            return ""
        start, end = (bisect.bisect_right(self.starts, i) for i in (at, at + len(fragment) - 1))
        return f"{start}-{end}" if end > start else f"{start}"


def fragments(quote):
    return [f.strip(" .") for f in re.split(r" · |…|\.\.\.", quote) if f.strip(" .")]


def check_quote(case, where, p, sources):
    path, _, lines = p["link"].partition(":")
    file = case / path
    if not file.is_file():
        return [f"{where}: {path} does not exist"]
    src = sources.setdefault(file, Source(file))
    first, _, last = lines.partition("-")
    first, last = int(first or 1), int(last or first or src.count)
    problems = []
    for frag in fragments(p["quote"]):
        if src.find(frag, first, last):
            continue
        now = src.find(frag)
        cited = p["link"] if lines else path
        lines_now = "lines" if "-" in now else "line"
        problems.append(
            f"{where}: {frag!r} is not at {cited}; " + (f"it is at {lines_now} {now}" if now else "not found")
        )
    return problems


def quoted(claim):
    """Each premise, and each objection given as a source, that quotes a case file."""
    items = claim.get("premises", []) + [a for a in claim.get("against", []) if isinstance(a, dict)]
    return [p for p in items if p.get("quote") and not re.match(r"https?://", p.get("link", ""))]


def check_claims(case):
    problems, count, sources = [], 0, {}
    files = sorted(case.glob("*/why/claims.json"))
    slugs = {f"{f.parent.parent.name}/{c['slug']}" for f in files for c in json.loads(f.read_text())}
    for f in files:
        stage = f.parent.parent.name
        for c in json.loads(f.read_text()):
            where = f"{f.relative_to(case)}: {c['slug']}"
            for p in quoted(c):
                count += 1
                problems += check_quote(case, where, p, sources)
            for r in c.get("related", []):
                if (r if "/" in r else f"{stage}/{r}") not in slugs:
                    problems.append(f"{where}: related claim {r!r} does not exist")
    return problems, count


def check_refs(case):
    problems, count = [], 0
    for name in READING:
        page = case / name
        if not page.is_file():
            continue
        for m in CASE_REF.finditer(page.read_text()):
            count += 1
            file, last = case / m[1], int(m[3] or m[2])
            if not file.is_file():
                problems.append(f"{name}: {m[0]}: {m[1]} does not exist")
            elif last > len(file.read_text().splitlines()):
                problems.append(f"{name}: {m[0]}: past the end of {m[1]}")
    return problems, count


def check_links(case):
    problems, count = [], 0
    for page in sorted(case.rglob("*.html")):
        for target in re.findall(r'href="([^"]+)"', page.read_text()):
            if re.match(r"[a-z][\w+.-]*:|#", target, re.IGNORECASE):
                continue
            count += 1
            path = unquote(target.split("#")[0].split("?")[0])
            if not (page.parent / path).exists():
                problems.append(f"{page.relative_to(case)}: link to {target} goes nowhere")
    return problems, count


def main(argv):
    if len(argv) != 2:
        sys.exit("usage: check.py <case>")
    case = Path(argv[1])
    if not case.is_dir():
        sys.exit(f"check.py: no case folder at {case}")
    results = [check_claims(case), check_refs(case), check_links(case)]
    problems = [p for found, _ in results for p in found]
    for p in problems:
        print(p)
    if problems:
        sys.exit(1)
    quotes, refs, links = (n for _, n in results)
    print(f"ok: {quotes} quotes, {refs} line references, {links} local links")


if __name__ == "__main__":
    main(sys.argv)
