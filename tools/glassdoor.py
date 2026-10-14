#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["websocket-client"]
# ///
"""Glassdoor interviews: read them out of the logged-in browser (tools/browser.py), then shape them.

Run with: uv run tools/glassdoor.py COMMAND ...

  probe URL                       load page 1; print the interview count, pages and roles on it
  scrape OUT.json URL [URL...]    read every page of each URL (one per role filter, or the
                                  unfiltered page), merged by interview id
  normalize RAW.json SCOPE.json OUT.json
                                  flatten the records and tag each with its group from SCOPE.json
  roles OUT.json                  role -> count, with the group each landed in
  summary OUT.json DIR            DIR/stats.md (counts per group) and DIR/processes.md
                                  (every A/B process and question), for the next stages

Glassdoor builds each interviews page with its records embedded in the Next.js payload
("interviews":[...] beside "filteredInterviewCount"), so nothing is scraped from the rendered text.
"""

import json
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from browser import Tab

DEC = json.JSONDecoder()


def payload(tab):
    """(interviews on this page, filteredInterviewCount) from the page's embedded data, or (None, None)."""
    pushes = tab.js('[...document.scripts].map(s=>s.textContent).filter(t=>t.startsWith("self.__next_f.push"))')
    for p in pushes or []:
        m = re.match(r"self\.__next_f\.push\(\[1,(.*)\]\)\s*$", p, re.DOTALL)
        if not m:
            continue
        s = json.loads(m.group(1))
        i = s.find('"interviews":[')
        if i < 0:
            continue
        items = DEC.raw_decode(s, i + len('"interviews":'))[0]
        c = re.search(r'"filteredInterviewCount":(\d+)', s)
        return items, int(c.group(1)) if c else None
    return None, None


def load(tab, url):
    tab.goto(url)
    for _ in range(20):
        items, count = payload(tab)
        if items is not None:
            return items, count
        time.sleep(1)
    title = tab.js("document.title")
    sys.exit(
        f"no interview data at {url} (page title: {title!r}). "
        "If it is a Cloudflare check or a login wall, ask the user to clear it in the browser, then rerun."
    )


def next_url(tab, page):
    """The link to page `page` (Glassdoor's _P<n> form), from the page itself."""
    hrefs = tab.js('[...document.querySelectorAll("a[href]")].map(a=>a.href)') or []
    return next((h for h in hrefs if re.search(rf"_P{page}\.htm", h)), None)


def probe(url):
    tab = Tab("glassdoor")
    items, count = load(tab, url)
    per = len(items) or 1
    print(
        json.dumps(
            {
                "url": url,
                "interviews": count,
                "per_page": per,
                "pages": count and -(-count // per),
                "roles_on_page_1": Counter((i.get("jobTitle") or {}).get("text") for i in items),
            },
            indent=1,
        )
    )


def scrape(out, urls):
    tab = Tab("glassdoor")
    found = {}
    for url in urls:
        items, count = load(tab, url)
        print(f"{url}\n  {count} interviews")
        page, got = 1, 0
        while True:
            for it in items:
                it["_source_url"] = url
                found[it["id"]] = it
            got += len(items)
            print(f"  page {page}: {len(items)}")
            if not items or (count is not None and got >= count):  # no count: read until no next page
                break
            page += 1
            nxt = next_url(tab, page)
            if not nxt:
                print(f"  no link to page {page}; stopping at {got}/{count}")
                break
            time.sleep(random.uniform(3, 6))  # a person's pace, not a crawler's
            items, _ = load(tab, nxt)
    Path(out).write_text(json.dumps(list(found.values()), indent=1, ensure_ascii=False))
    print(f"{len(found)} unique interviews -> {out}")


def grouper(scope):
    groups = json.loads(Path(scope).read_text())["groups"]
    table = {r.casefold().strip(): g for g, spec in groups.items() for r in spec.get("roles", [])}
    priority = {g: spec["priority"] for g, spec in groups.items()}
    default = next(g for g, spec in groups.items() if spec.get("default"))
    return lambda role: (g := table.get((role or "").casefold().strip(), default), priority[g])


def normalize(raw, scope, out):
    group = grouper(scope)
    lc = lambda s: s.lower() if s else None
    rows = []
    for r in sorted(json.loads(Path(raw).read_text()), key=lambda r: r["reviewDateTime"], reverse=True):
        role = (r.get("jobTitle") or {}).get("text")
        g, prio = group(role)
        rows.append(
            {
                "id": r["id"],
                "role": role,
                "group": g,
                "priority": prio,
                "location": (r.get("location") or {}).get("name"),
                "review_date": r["reviewDateTime"][:10],
                "interview_date": r["interviewDateTime"][:7] if r.get("interviewDateTime") else None,
                "outcome": lc(r.get("outcome")),
                "experience": lc(r.get("experience")),
                "difficulty": lc(r.get("difficulty")),
                "how_obtained": lc(r.get("source")),
                "duration_days": r.get("durationDays"),
                "process": r.get("processDescription"),
                "questions": [q["question"] for q in r.get("userQuestions") or []],
                "helpful": r.get("countHelpful"),
                "employer_responses": [e.get("response") or e for e in r.get("employerResponses") or []],
            }
        )
    meta = json.loads(Path(scope).read_text())
    Path(out).write_text(
        json.dumps(
            {
                "company": meta.get("company"),
                "source": meta.get("urls"),
                "scraped": time.strftime("%Y-%m-%d"),
                "count": len(rows),
                "interviews": rows,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    print(
        f"{len(rows)} interviews -> {out}: "
        + ", ".join(f"{g} {n}" for g, n in sorted(Counter(r["group"] for r in rows).items()))
    )


def roles(path):
    data = json.loads(Path(path).read_text())["interviews"]
    for (role, g), n in sorted(Counter((r["role"], r["group"]) for r in data).items(), key=lambda x: (x[0][1], -x[1])):
        print(f"{g}\t{n}\t{role}")


def tally(rows, key):
    return ", ".join(f"{v} {n}" for v, n in Counter(r[key] for r in rows).most_common())


def summary(path, outdir):
    d = json.loads(Path(path).read_text())
    rows, out = d["interviews"], Path(outdir)
    head = f"Generated by `tools/glassdoor.py summary` from `interviews.json` ({d['count']} interviews, scraped {d['scraped']}). Do not edit; edit scope.json and rerun."
    stats = [f"# Glassdoor stats: {d['company']}", "", head, ""]
    procs = [
        f"# Glassdoor processes and questions: {d['company']}, groups A and B",
        "",
        head,
        "Group C stays in interviews.json; query it with jq.",
        "",
    ]
    for g in sorted({r["group"] for r in rows}):
        sel = [r for r in rows if r["group"] == g]
        stats += [
            f"## Group {g} ({sel[0]['priority']} priority): {len(sel)} interviews",
            "",
            f"- Roles: {', '.join(f'{v} ({n})' for v, n in Counter(r['role'] for r in sel).most_common())}",
            f"- Outcome: {tally(sel, 'outcome')}",
            f"- Experience: {tally(sel, 'experience')}",
            f"- Difficulty: {tally(sel, 'difficulty')}",
            f"- How obtained: {tally(sel, 'how_obtained')}",
            f"- Reviews dated {min(r['review_date'] for r in sel)} to {max(r['review_date'] for r in sel)}",
            f"- Questions reported: {sum(len(r['questions']) for r in sel)}",
            "",
        ]
        if g == "C":
            continue
        procs += [f"## Group {g}", ""]
        for r in sel:
            procs.append(f"- **{r['role']}**, {r['review_date']}, {r['outcome']}, {r['difficulty']} (id {r['id']})")
            if r["process"]:
                procs.append(f"  - Process: {' '.join(r['process'].split())}")
            for q in r["questions"]:
                procs.append(f"  - Q: {' '.join(q.split())}")
        procs.append("")
    (out / "stats.md").write_text("\n".join(stats))
    (out / "processes.md").write_text("\n".join(procs))
    print(f"-> {out / 'stats.md'}, {out / 'processes.md'}")


def main():
    cmd, *args = sys.argv[1:] or ["-h"]
    fns = {
        "probe": (probe, 1),
        "scrape": (lambda o, *u: scrape(o, u), 2),
        "normalize": (normalize, 3),
        "roles": (roles, 1),
        "summary": (summary, 2),
    }
    if cmd not in fns or len(args) < fns[cmd][1]:
        sys.exit(__doc__)
    fns[cmd][0](*args)


if __name__ == "__main__":
    main()
