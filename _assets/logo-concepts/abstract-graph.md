# interview-detective: logo concepts (abstract / geometric)

Three marks in a modern dev-tool style, with no detective costume or props. Each mark is a 256x256 rounded tile,
and each has a 640x200 version with the wordmark. All SVGs are also saved as their own files in this folder:

| Concept | Mark | Mark + wordmark |
| --- | --- | --- |
| 1. Pinboard | `abstract-graph-1.svg` | `abstract-graph-1-wordmark.svg` |
| 2. Node Lens | `abstract-graph-2.svg` | `abstract-graph-2-wordmark.svg` |
| 3. Stage Keyhole | `abstract-graph-3.svg` | `abstract-graph-3-wordmark.svg` |

Notes:

- The wordmarks use `<text>` with font stacks (JetBrains Mono / Inter, then system fonts). Convert them to paths
  before shipping if the exact typeface matters.
- Every mark sits on its own dark tile, so it reads on both GitHub light and dark themes.

---

## 1. Pinboard

**Idea:** an evidence board drawn as a graph. Red string runs from every clue to the one node that matters.

Four pale "pins" (`#E2E8F0`) are the sources: Glassdoor, the company's repos, employee repos and prep repos. Slate
edges (`#475569`) join some of them as loose context, and red string edges (`#F43F5E`) run from every pin to a
central red ring (`#F43F5E`, with its centre cut out in the `#0B1220` tile colour). That ring is the conclusion,
the likely questions. The wordmark is JetBrains Mono Bold in `#E2E8F0`, with only the hyphen in red so it echoes
the string. The tagline "clues in, questions out" is in `#64748B`.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" role="img" aria-label="interview-detective: Pinboard">
  <rect width="256" height="256" rx="48" fill="#0B1220"/>
  <g stroke="#475569" stroke-width="10" stroke-linecap="round">
    <line x1="60" y1="76" x2="176" y2="52"/>
    <line x1="60" y1="76" x2="84" y2="200"/>
    <line x1="204" y1="172" x2="84" y2="200"/>
  </g>
  <g stroke="#F43F5E" stroke-width="10" stroke-linecap="round">
    <line x1="60" y1="76" x2="132" y2="128"/>
    <line x1="176" y1="52" x2="132" y2="128"/>
    <line x1="204" y1="172" x2="132" y2="128"/>
    <line x1="84" y1="200" x2="132" y2="128"/>
  </g>
  <g fill="#E2E8F0">
    <circle cx="60" cy="76" r="18"/>
    <circle cx="176" cy="52" r="18"/>
    <circle cx="204" cy="172" r="18"/>
    <circle cx="84" cy="200" r="18"/>
  </g>
  <circle cx="132" cy="128" r="28" fill="#F43F5E"/>
  <circle cx="132" cy="128" r="11" fill="#0B1220"/>
</svg>
```

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 200" width="640" height="200" role="img" aria-label="interview-detective">
  <rect width="640" height="200" rx="32" fill="#0B1220"/>
  <g transform="translate(20 20) scale(0.625)">
    <g stroke="#475569" stroke-width="10" stroke-linecap="round">
      <line x1="60" y1="76" x2="176" y2="52"/>
      <line x1="60" y1="76" x2="84" y2="200"/>
      <line x1="204" y1="172" x2="84" y2="200"/>
    </g>
    <g stroke="#F43F5E" stroke-width="10" stroke-linecap="round">
      <line x1="60" y1="76" x2="132" y2="128"/>
      <line x1="176" y1="52" x2="132" y2="128"/>
      <line x1="204" y1="172" x2="132" y2="128"/>
      <line x1="84" y1="200" x2="132" y2="128"/>
    </g>
    <g fill="#E2E8F0">
      <circle cx="60" cy="76" r="18"/>
      <circle cx="176" cy="52" r="18"/>
      <circle cx="204" cy="172" r="18"/>
      <circle cx="84" cy="200" r="18"/>
    </g>
    <circle cx="132" cy="128" r="28" fill="#F43F5E"/>
    <circle cx="132" cy="128" r="11" fill="#0B1220"/>
  </g>
  <text x="196" y="112" font-family="JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="36" font-weight="700" fill="#E2E8F0">interview<tspan fill="#F43F5E">-</tspan>detective</text>
  <text x="198" y="146" font-family="JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="16" fill="#64748B">clues in, questions out</text>
</svg>
```

---

## 2. Node Lens

**Idea:** a magnifying lens whose rim is a graph, which zooms in on a single highlighted node.

Six nodes (`#E6EDF3`) joined in a teal hexagon (`#2DD4BF`) form the lens rim. A thick teal handle comes off the
lower-right node, so the shape reads as a lens without drawing a literal magnifying glass. Faint spokes (teal at 45%
opacity) pull three rim nodes in towards an amber centre node (`#FBBF24`), which is the insight. The tile is
GitHub-dark `#0D1117`. The wordmark is Inter SemiBold set as one word, "interview" in `#E6EDF3` and "detective" in
teal, with a monospace CLI line underneath in `#7D8590` so it also works as a terminal banner.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" role="img" aria-label="interview-detective: Node Lens">
  <rect width="256" height="256" rx="48" fill="#0D1117"/>
  <line x1="153" y1="153" x2="210" y2="210" stroke="#2DD4BF" stroke-width="18" stroke-linecap="round"/>
  <polygon points="153,153 91,170 46,125 63,63 125,46 170,91" fill="none" stroke="#2DD4BF" stroke-width="10" stroke-linejoin="round"/>
  <g stroke="#2DD4BF" stroke-opacity="0.45" stroke-width="6" stroke-linecap="round">
    <line x1="108" y1="108" x2="91" y2="170"/>
    <line x1="108" y1="108" x2="63" y2="63"/>
    <line x1="108" y1="108" x2="170" y2="91"/>
  </g>
  <g fill="#E6EDF3">
    <circle cx="153" cy="153" r="15"/>
    <circle cx="91" cy="170" r="15"/>
    <circle cx="46" cy="125" r="15"/>
    <circle cx="63" cy="63" r="15"/>
    <circle cx="125" cy="46" r="15"/>
    <circle cx="170" cy="91" r="15"/>
  </g>
  <circle cx="108" cy="108" r="20" fill="#FBBF24"/>
</svg>
```

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 200" width="640" height="200" role="img" aria-label="interview-detective">
  <rect width="640" height="200" rx="32" fill="#0D1117"/>
  <g transform="translate(20 20) scale(0.625)">
    <line x1="153" y1="153" x2="210" y2="210" stroke="#2DD4BF" stroke-width="18" stroke-linecap="round"/>
    <polygon points="153,153 91,170 46,125 63,63 125,46 170,91" fill="none" stroke="#2DD4BF" stroke-width="10" stroke-linejoin="round"/>
    <g stroke="#2DD4BF" stroke-opacity="0.45" stroke-width="6" stroke-linecap="round">
      <line x1="108" y1="108" x2="91" y2="170"/>
      <line x1="108" y1="108" x2="63" y2="63"/>
      <line x1="108" y1="108" x2="170" y2="91"/>
    </g>
    <g fill="#E6EDF3">
      <circle cx="153" cy="153" r="15"/>
      <circle cx="91" cy="170" r="15"/>
      <circle cx="46" cy="125" r="15"/>
      <circle cx="63" cy="63" r="15"/>
      <circle cx="125" cy="46" r="15"/>
      <circle cx="170" cy="91" r="15"/>
    </g>
    <circle cx="108" cy="108" r="20" fill="#FBBF24"/>
  </g>
  <text x="196" y="112" font-family="Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif" font-size="40" font-weight="600" letter-spacing="-0.5" fill="#E6EDF3">interview<tspan fill="#2DD4BF">detective</tspan></text>
  <text x="198" y="146" font-family="JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="16" fill="#7D8590">$ interview-detective --company acme</text>
</svg>
```

---

## 3. Stage Keyhole

**Idea:** the five pipeline stages, 01 to 05, stack up into a keyhole, so working through them unlocks the interview.

A keyhole silhouette is cut out of five horizontal bands, one band per stage folder. The bands run in a cool-to-warm
ramp from `#38BDF8` (01) through `#60A5FA`, `#818CF8` and `#A78BFA` to `#C084FC` (05), on a `#111827` tile.
At 32px the gaps between bands blur, but the keyhole shape still reads. The wordmark is JetBrains Mono Bold in
`#F3F4F6`, with the stage numbers `01 02 03 04 05` underneath, each in its band's colour.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" role="img" aria-label="interview-detective: Stage Keyhole">
  <defs>
    <clipPath id="keyhole">
      <circle cx="128" cy="96" r="56"/>
      <polygon points="106,124 150,124 174,212 82,212"/>
    </clipPath>
  </defs>
  <rect width="256" height="256" rx="48" fill="#111827"/>
  <g clip-path="url(#keyhole)">
    <rect x="0" y="40" width="256" height="28" fill="#38BDF8"/>
    <rect x="0" y="76" width="256" height="28" fill="#60A5FA"/>
    <rect x="0" y="112" width="256" height="28" fill="#818CF8"/>
    <rect x="0" y="148" width="256" height="28" fill="#A78BFA"/>
    <rect x="0" y="184" width="256" height="28" fill="#C084FC"/>
  </g>
</svg>
```

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 200" width="640" height="200" role="img" aria-label="interview-detective">
  <defs>
    <clipPath id="keyhole">
      <circle cx="128" cy="96" r="56"/>
      <polygon points="106,124 150,124 174,212 82,212"/>
    </clipPath>
  </defs>
  <rect width="640" height="200" rx="32" fill="#111827"/>
  <g transform="translate(20 20) scale(0.625)">
    <g clip-path="url(#keyhole)">
      <rect x="0" y="40" width="256" height="28" fill="#38BDF8"/>
      <rect x="0" y="76" width="256" height="28" fill="#60A5FA"/>
      <rect x="0" y="112" width="256" height="28" fill="#818CF8"/>
      <rect x="0" y="148" width="256" height="28" fill="#A78BFA"/>
      <rect x="0" y="184" width="256" height="28" fill="#C084FC"/>
    </g>
  </g>
  <text x="196" y="112" font-family="JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="36" font-weight="700" fill="#F3F4F6">interview-detective</text>
  <g font-family="JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="16" font-weight="700">
    <text x="198" y="146" fill="#38BDF8">01</text>
    <text x="236" y="146" fill="#60A5FA">02</text>
    <text x="274" y="146" fill="#818CF8">03</text>
    <text x="312" y="146" fill="#A78BFA">04</text>
    <text x="350" y="146" fill="#C084FC">05</text>
  </g>
</svg>
```
