#!/usr/bin/env python3
"""Make the HTML pages the user reads from a case's markdown, and print a command to open each.

Run with: uv run tools/render.py <case>

  <case>/02_research/findings.md          -> findings.html
  <case>/04_question-check/question-bank.md -> question-bank.html
  <case>/05_report/report.md              -> report.html
  <case>/<stage>/why/claims.json          -> why/<slug>.html, one page per inference

The markdown stays the edit surface; rerun after editing it. Only the markdown the stages write is
understood: headings, paragraphs, nested lists, pipe tables, quotes, fenced code, links, bold and italics.
The claims format is in _shared/evidence.md.
"""

import html
import json
import re
import shlex
import sys
from pathlib import Path

READING = {"02_research": "findings", "04_question-check": "question-bank", "05_report": "report"}
TITLES = {"findings": "findings", "question-bank": "question bank", "report": "report"}
LABELS = ("confirmed", "likely", "speculative", "standard", "variant", "company-specific", "unsure")
SAFE_LINK = re.compile(r"(https?://|mailto:|[^:]*$)", re.IGNORECASE)  # web links, or relative ones (no scheme)

# ---------------------------------------------------------------------------------------------- inline


def link(href, text, cls=""):
    if not SAFE_LINK.match(href):
        return text
    attr = f' class="{cls}"' if cls else ""
    return f'<a{attr} href="{html.escape(href)}">{text}</a>'


def inline(s):
    """Escape the text, then turn code spans, links, bare URLs, bold and italics into html."""
    saved = []

    def keep(fragment):
        saved.append(fragment)
        return f"\x00{len(saved) - 1}\x00"

    s = re.sub(r"(`+)(.+?)\1", lambda m: keep(f"<code>{html.escape(m[2].strip())}</code>"), s)
    s = html.escape(s, quote=False)
    s = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: keep(link(html.unescape(m[2]), m[1], "why" if m[1] == "why" else "")),
        s,
    )
    s = re.sub(r"https?://[^\s<>\"]+[^\s<>\".,;:)]", lambda m: keep(link(html.unescape(m[0]), m[0])), s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = mark_labels(s)
    while "\x00" in s:
        s = re.sub(r"\x00(\d+)\x00", lambda m: saved[int(m[1])], s)
    return s


def mark_labels(s):
    """A confidence or verdict label gets a chip where it is used as one: after `— `, `(`, `, `, `; ` or a
    bold `Verdict:` / `Confidence:`, and not followed by more of a word."""
    words = "|".join(LABELS)
    return re.sub(
        rf"(— |\(|, |; |<strong>(?:Verdict|Confidence):</strong> )({words})(?![\w-])",
        r'\1<span class="conf \2">\2</span>',
        s,
    )


# ---------------------------------------------------------------------------------------------- blocks

ITEM = re.compile(r"( *)([-*+]|\d+[.)]) +(.*)")
FENCE = re.compile(r" *(```+|~~~+) *([\w+-]*)")
HEADING = re.compile(r"(#{1,6}) +(.*?)(?: +#+)? *$")
RULE = re.compile(r" *([-*_])( *\1){2,} *$")


def indent(line):
    return len(line) - len(line.lstrip(" "))


def starts_block(line):
    s = line.lstrip()
    return bool(HEADING.match(s) or FENCE.match(line) or ITEM.match(line) or s.startswith((">", "|")))


def fence(lines, i):
    m = FENCE.match(lines[i])
    if not m:
        return None
    j = i + 1
    while j < len(lines) and not lines[j].strip().startswith(m[1]):
        j += 1
    lang = f' class="language-{m[2]}"' if m[2] else ""
    return f"<pre><code{lang}>{html.escape(chr(10).join(lines[i + 1 : j]))}</code></pre>", j + 1


def heading(lines, i):
    m = HEADING.match(lines[i])
    if not m:
        return None
    n = len(m[1])
    slug = re.sub(r"[^\w]+", "-", m[2].lower()).strip("-")
    return f'<h{n} id="{slug}">{inline(m[2])}</h{n}>', i + 1


def rule(lines, i):
    return ("<hr>", i + 1) if RULE.match(lines[i]) and not ITEM.match(lines[i]) else None


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def table(lines, i):
    if not (lines[i].lstrip().startswith("|") and i + 1 < len(lines) and re.match(r" *\|? *:?-+", lines[i + 1])):
        return None
    head = "".join(f"<th>{inline(c)}</th>" for c in cells(lines[i]))
    j, rows = i + 2, []
    while j < len(lines) and lines[j].lstrip().startswith("|"):
        rows.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells(lines[j])) + "</tr>")
        j += 1
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>", j


def quote(lines, i):
    if not lines[i].lstrip().startswith(">"):
        return None
    j = i
    while j < len(lines) and lines[j].lstrip().startswith(">"):
        j += 1
    inner = [re.sub(r"^ *> ?", "", line) for line in lines[i:j]]
    return f"<blockquote>{''.join(blocks(inner))}</blockquote>", j


def paragraph(lines, i):
    j = i + 1
    while j < len(lines) and lines[j].strip() and not starts_block(lines[j]):
        j += 1
    return f"<p>{inline(' '.join(line.strip() for line in lines[i:j]))}</p>", j


def item_end(lines, i, depth):
    """The line after the item starting at i: its wrapped lines, nested blocks and the blank lines inside it."""
    j = i + 1
    while j < len(lines):
        line = lines[j]
        if not line.strip():
            k = next((k for k in range(j, len(lines)) if lines[k].strip()), len(lines))
            if k == len(lines) or indent(lines[k]) <= depth:
                return j
        elif indent(line) <= depth and starts_block(line):
            return j
        j += 1
    return j


def item(lines, depth):
    """One list item's html, from its lines (the marker already stripped from the first)."""
    body = [lines[0]] + [line[min(indent(line), depth + 2) :] if indent(line) > depth else line for line in lines[1:]]
    j = 1
    while j < len(body) and body[j].strip() and not starts_block(body[j]):
        j += 1
    text = inline(" ".join(line.strip() for line in body[:j]))
    return f"<li>{text}{''.join(blocks(body[j:]))}</li>"


def listing(lines, i):
    m = ITEM.match(lines[i])
    if not m:
        return None
    depth, ordered = indent(lines[i]), m[2][0].isdigit()
    items, j = [], i
    while j < len(lines):
        m = ITEM.match(lines[j])
        if not (m and indent(lines[j]) == depth and m[2][0].isdigit() == ordered):
            break
        end = item_end(lines, j, depth)
        items.append(item([m[3], *lines[j + 1 : end]], depth))
        j = end
        while j < len(lines) and not lines[j].strip() and j + 1 < len(lines) and ITEM.match(lines[j + 1]):
            j += 1
    tag = "ol" if ordered else "ul"
    return f"<{tag}>{''.join(items)}</{tag}>", j


KINDS = (fence, heading, rule, table, quote, listing, paragraph)


def blocks(lines):
    out, i = [], 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        for kind in KINDS:
            found = kind(lines, i)
            if found:
                out.append(found[0])
                i = found[1]
                break
    return out


def sections(parts):
    """Each h3 and what follows it, up to the next heading of level 1–3, goes in a card; the first h2 section
    goes in a highlighted box."""
    out, open_tag, lead_done = [], None, False
    for part in parts:
        level = re.match(r"<h([1-3])", part)
        if level and open_tag:
            out.append("</section>")
            open_tag = None
        if level and level[1] == "3":
            out.append('<section class="card">')
            open_tag = "card"
        elif level and level[1] == "2" and not lead_done:
            out.append('<section class="lead">')
            open_tag, lead_done = "lead", True
        out.append(part)
    return out + (["</section>"] if open_tag else [])


def to_html(md):
    return "\n".join(sections(blocks(md.splitlines())))


# ---------------------------------------------------------------------------------------------- pages

CSS = """:root{--bg:#f7f7f5;--card:#fff;--ink:#1d1d1f;--muted:#6b6b70;--line:#e4e4e0;--accent:#2563eb;--lead:#eef4ff;
--confirmed:#1f8a4c;--likely:#b7791f;--speculative:#7a5af8;--standard:#1f8a4c;--variant:#b7791f;--company-specific:#d0443e;
--unsure:#6b6b70}
@media (prefers-color-scheme:dark){:root{--bg:#141416;--card:#1d1d21;--ink:#ececf0;--muted:#9a9aa3;--line:#2e2e34;
--accent:#60a5fa;--lead:#18233a;--confirmed:#4ade80;--likely:#fbbf24;--speculative:#a78bfa;--standard:#4ade80;
--variant:#fbbf24;--company-specific:#f87171;--unsure:#9a9aa3}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,sans-serif}
main{max-width:880px;margin:0 auto;padding:36px 20px 80px;overflow-wrap:anywhere}a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}nav{font-size:.88rem;color:var(--muted);margin-bottom:18px}
h1{font-size:1.7rem;line-height:1.25;margin:0 0 8px}h2{font-size:1.25rem;margin:40px 0 12px;padding-bottom:6px;
border-bottom:1px solid var(--line)}h3{font-size:1.02rem;margin:4px 0 8px}
code{font:.86em ui-monospace,Menlo,monospace;background:var(--line);padding:1px 5px;border-radius:4px}
pre{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px;overflow-x:auto}
pre code{background:none;padding:0}blockquote{margin:8px 0;padding:4px 14px;border-left:3px solid var(--line);color:var(--muted)}
table{border-collapse:collapse;width:100%;font-size:.92rem;margin:12px 0;background:var(--card)}
th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}th{background:var(--line)}
li{margin:4px 0}.lead{background:var(--lead);border:1px solid var(--line);border-radius:12px;padding:2px 20px 8px;margin:20px 0}
.lead h2{margin-top:14px}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 18px;
margin:12px 0}.conf{font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.03em;padding:0 7px;
border:1px solid currentColor;border-radius:999px;white-space:nowrap}
.confirmed{color:var(--confirmed)}.likely{color:var(--likely)}.speculative{color:var(--speculative)}
.standard{color:var(--standard)}.variant{color:var(--variant)}.company-specific{color:var(--company-specific)}
.unsure{color:var(--unsure)}a.why{font-size:.75rem;font-weight:700;border:1px solid currentColor;border-radius:999px;
padding:0 7px;white-space:nowrap}a.why::after{content:" →"}
.chip{font-size:.68rem;font-weight:700;text-transform:uppercase;padding:0 6px;border-radius:999px;border:1px dashed}
.chip.checked{color:var(--confirmed)}.chip.lane{color:var(--muted)}ol.premises>li{background:var(--card);
border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:10px 0}.shows{font-weight:600}
.src{font-size:.85rem;color:var(--muted)}footer{margin-top:44px;font-size:.82rem;color:var(--muted)}"""


def shell(title, body, nav=""):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style></head>
<body><main>
{nav}
{body}
</main></body></html>
"""


def reading_page(case, stage, name):
    """The html for <stage>/<name>.md, with a bar linking the case's other reading pages."""
    md = (case / stage / f"{name}.md").read_text()
    others = [
        f'<a href="../{s}/{n}.html">{TITLES[n]}</a>'
        for s, n in READING.items()
        if s != stage and (case / s / f"{n}.md").is_file()
    ]
    nav = f"<nav>{' · '.join(others)}</nav>" if others else ""
    title = next((line.lstrip("# ") for line in md.splitlines() if line.startswith("# ")), name)
    footer = f"<footer>Made from <code>{stage}/{name}.md</code>, which stays the file to edit.</footer>"
    return shell(title, to_html(md) + footer, nav)


# ---------------------------------------------------------------------------------------------- why pages

REQUIRED = ("slug", "confidence", "claim", "premises", "reasoning")


def href(target):
    """A premise's link: a web address as it is, or a case path (`01_intake/intake.md:3-5`) made relative
    to <case>/<stage>/why/, with its lines kept as a fragment."""
    if re.match(r"https?://", target):
        return target
    path, _, lines = target.partition(":")
    return f"../../{path}" + (f"#L{lines}" if lines else "")


def source(p):
    mark = '<span class="chip checked">checked</span>' if p.get("checked") else '<span class="chip lane">lane</span>'
    quote = f"<blockquote>{inline(p['quote'])}</blockquote>" if p.get("quote") else ""
    return f'{quote}<div class="src">{link(href(p["link"]), inline(p["source"]))} {mark}</div>'


def related_link(ref, titles):
    stage, _, slug = ref.rpartition("/")
    page = f"../../{stage}/why/{slug}.html" if stage else f"{slug}.html"
    return f'<li><a href="{html.escape(page)}">{inline(titles.get(ref, slug))}</a></li>'


def why_page(c, stage, titles):
    premises = "".join(f'<li><div class="shows">{inline(p["shows"])}</div>{source(p)}</li>' for p in c["premises"])
    against = "".join(f"<li>{inline(a) if isinstance(a, str) else source(a)}</li>" for a in c.get("against", []))
    parts = [
        f'<ol class="premises">{premises}</ol>',
        table_html(c.get("table")),
        "<h2>How it adds up</h2><ol>" + "".join(f"<li>{inline(r)}</li>" for r in c["reasoning"]) + "</ol>",
        f"<h2>What cuts against it</h2><ul>{against}</ul>" if against else "",
        "<h2>What would settle it</h2><ul>" + "".join(f"<li>{inline(s)}</li>" for s in c["settle"]) + "</ul>"
        if c.get("settle")
        else "",
        "<h2>Related</h2><ul>" + "".join(related_link(r, titles) for r in c["related"]) + "</ul>"
        if c.get("related")
        else "",
    ]
    back = (
        f'<nav><a href="../{READING[stage]}.html">← Back to the {TITLES[READING[stage]]}</a></nav>'
        if stage in READING
        else ""
    )
    conf = c["confidence"]
    body = (
        f'<div class="src">Why we think this <span class="conf {conf}">{conf}</span></div>'
        f"<h1>{inline(c['claim'])}</h1><h2>Based on</h2>{''.join(parts)}"
        '<footer><span class="chip checked">checked</span> re-read first-hand this run · '
        '<span class="chip lane">lane</span> quoted by a research agent, not re-read. '
        "Numbers in [brackets] point to the premises above.</footer>"
    )
    return shell(f"Why: {c['claim']}", body, back)


def table_html(t):
    if not t:
        return ""
    head = "".join(f"<th>{inline(h)}</th>" for h in t["head"])
    rows = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>" for row in t["rows"])
    return f"<table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>"


def load_claims(path):
    claims = json.loads(path.read_text())
    for c in claims:
        missing = [k for k in REQUIRED if not c.get(k)]
        if missing:
            raise ValueError(f"{path}: claim {c.get('slug', '?')!r} has no {', '.join(missing)}")
    return claims


def why_pages(case):
    """Every why page in the case, as (path, html). Related claims may sit in another stage: `02_research/slug`."""
    found = {p.parent.parent.name: load_claims(p) for p in sorted(case.glob("*/why/claims.json"))}
    titles = {f"{stage}/{c['slug']}": c["claim"] for stage, cs in found.items() for c in cs}
    for stage, claims in found.items():
        local = titles | {c["slug"]: c["claim"] for c in claims}
        for c in claims:
            yield case / stage / "why" / f"{c['slug']}.html", why_page(c, stage, local)


# ---------------------------------------------------------------------------------------------- main


def main(argv):
    if len(argv) != 2:
        sys.exit("usage: render.py <case>")
    case = Path(argv[1])
    if not case.is_dir():
        sys.exit(f"render.py: no case folder at {case}")
    try:
        pages = list(why_pages(case))
    except (ValueError, json.JSONDecodeError) as e:
        sys.exit(f"render.py: {e}")
    for path, page in pages:
        path.write_text(page)
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    for stage, name in READING.items():
        if (case / stage / f"{name}.md").is_file():
            out = case / stage / f"{name}.html"
            out.write_text(reading_page(case, stage, name))
            print(f"{opener} {shlex.quote(str(out.resolve()))}")


if __name__ == "__main__":
    main(sys.argv)
