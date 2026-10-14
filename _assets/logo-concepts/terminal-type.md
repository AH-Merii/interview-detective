# interview-detective: terminal-native logo concepts

Direction: typographic and terminal-native. Monogram marks, prompt glyphs, monospace wordmarks and cursor or bracket motifs. Each mark should also work as one line of text in a terminal.

All marks use paths and rects instead of `<text>`, so they look the same in every renderer. Only the wordmark text uses a font stack: `'JetBrains Mono', 'Iosevka', 'Berkeley Mono', ui-monospace, 'DejaVu Sans Mono', monospace`, bold. Every SVG passed `xml.dom.minidom.parse` and was rendered with `rsvg-convert` at 256px and 32px to check legibility.

| # | Mark | Mark + wordmark |
|---|------|-----------------|
| 1 | [terminal-type-1.svg](terminal-type-1.svg) | [terminal-type-1-wordmark.svg](terminal-type-1-wordmark.svg) |
| 2 | [terminal-type-2.svg](terminal-type-2.svg) | [terminal-type-2-wordmark.svg](terminal-type-2-wordmark.svg) |
| 3 | [terminal-type-3.svg](terminal-type-3.svg) | [terminal-type-3-wordmark.svg](terminal-type-3-wordmark.svg) |

---

## 1. Interrogation Prompt `❯?▍`

**Idea:** a shell prompt that waits on a question: the tool is a prompt you point at a company.

The mark is three glyphs on a dark tile: a green prompt chevron `❯`, a squared-off `?`, and a solid amber block cursor. It reads as "prompt, question, waiting for input", which matches the tool's input (a company) and output (likely questions). The shapes are thick strokes with square caps and miter joins, so they stay crisp at 32px. Colours: background `#0F1419`, chevron `#7FD962`, question mark `#E6E1CF`, cursor `#FFB454` (an Ayu Dark-style palette). Wordmark: bold monospace `interview-detective` in `#E6E1CF`, with the tagline `❯ clues in, questions out` in `#5C6773`.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" role="img" aria-label="interview-detective: prompt, question mark, cursor">
  <title>interview-detective: Interrogation Prompt</title>
  <rect width="256" height="256" rx="44" fill="#0F1419"/>
  <g transform="translate(6 0)">
    <!-- prompt chevron -->
    <polyline points="40,84 84,128 40,172" fill="none" stroke="#7FD962" stroke-width="22" stroke-linecap="square" stroke-linejoin="miter"/>
    <!-- question mark -->
    <path d="M108 104 A30 30 0 1 1 159.2 125.2 L138 142 V158" fill="none" stroke="#E6E1CF" stroke-width="22" stroke-linecap="butt" stroke-linejoin="miter"/>
    <rect x="127" y="174" width="22" height="22" fill="#E6E1CF"/>
    <!-- block cursor -->
    <rect x="184" y="60" width="32" height="136" fill="#FFB454"/>
  </g>
</svg>
```

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 200" width="640" height="200" role="img" aria-label="interview-detective">
  <title>interview-detective: Interrogation Prompt wordmark</title>
  <rect width="640" height="200" rx="28" fill="#0F1419"/>
  <g transform="translate(20 20) scale(0.625)">
    <g transform="translate(6 0)">
      <polyline points="40,84 84,128 40,172" fill="none" stroke="#7FD962" stroke-width="22" stroke-linecap="square" stroke-linejoin="miter"/>
      <path d="M108 104 A30 30 0 1 1 159.2 125.2 L138 142 V158" fill="none" stroke="#E6E1CF" stroke-width="22" stroke-linecap="butt" stroke-linejoin="miter"/>
      <rect x="127" y="174" width="22" height="22" fill="#E6E1CF"/>
      <rect x="184" y="60" width="32" height="136" fill="#FFB454"/>
    </g>
  </g>
  <text x="188" y="106" font-family="'JetBrains Mono', 'Iosevka', 'Berkeley Mono', ui-monospace, 'DejaVu Sans Mono', monospace" font-size="34" font-weight="700" fill="#E6E1CF">interview-detective</text>
  <text x="188" y="140" font-family="'JetBrains Mono', 'Iosevka', ui-monospace, 'DejaVu Sans Mono', monospace" font-size="17" fill="#5C6773"><tspan fill="#7FD962">❯</tspan> clues in, questions out</text>
</svg>
```

### Terminal version

Block-character banner (7 rows, for `--help` or a startup splash):

```text
██▄          ▄▄▄▄▄     ████
 ▀██▄      ██▀   ▀██   ████
   ▀██▄          ▄██   ████
   ▄██▀       ▄██▀     ████
 ▄██▀         ██       ████
██▀                    ████
              ██       ████
```

One-line coloured version for fish (truecolour; `set_color` takes hex RGB):

```fish
printf '%s❯ %s?%s▍%s interview-detective\n' (set_color 7fd962) (set_color e6e1cf) (set_color ffb454) (set_color normal)
```

Plain-ASCII fallback: `> ?_ interview-detective`

---

## 2. Case Brackets `[id]`

**Idea:** the project's initials as a case-file label, with a magnifying lens as the dot on the `i`.

A lowercase geometric `id` monogram sits between two heavy square brackets. The brackets work as the case-file tag and as an array or index, which suits a tool that collects evidence into a list. The only accent is the dot of the `i`, drawn as a hollow coral ring: a lens or "clue marker". It still shows as a ring at 32px. Colours: background `#16181D`, brackets `#6B7280`, letters `#E8E6E3`, lens `#FF6B57`. Wordmark: bold monospace `interview-detective` with a grey hyphen. The tagline `◦ glassdoor · github · prep repos` names the three evidence sources.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" role="img" aria-label="interview-detective: [id] monogram with a lens for the i's dot">
  <title>interview-detective: Case Brackets</title>
  <rect width="256" height="256" rx="44" fill="#16181D"/>
  <!-- brackets -->
  <path d="M46 48 H28 V208 H46" fill="none" stroke="#6B7280" stroke-width="18" stroke-linecap="square" stroke-linejoin="miter"/>
  <path d="M210 48 H228 V208 H210" fill="none" stroke="#6B7280" stroke-width="18" stroke-linecap="square" stroke-linejoin="miter"/>
  <!-- i: stem + lens tittle -->
  <line x1="88" y1="124" x2="88" y2="200" stroke="#E8E6E3" stroke-width="18"/>
  <circle cx="88" cy="86" r="16" fill="none" stroke="#FF6B57" stroke-width="10"/>
  <!-- d: bowl + ascender -->
  <circle cx="152" cy="161" r="30" fill="none" stroke="#E8E6E3" stroke-width="18"/>
  <line x1="182" y1="66" x2="182" y2="200" stroke="#E8E6E3" stroke-width="18"/>
</svg>
```

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 200" width="640" height="200" role="img" aria-label="interview-detective">
  <title>interview-detective: Case Brackets wordmark</title>
  <rect width="640" height="200" rx="28" fill="#16181D"/>
  <g transform="translate(20 20) scale(0.625)">
    <path d="M46 48 H28 V208 H46" fill="none" stroke="#6B7280" stroke-width="18" stroke-linecap="square"/>
    <path d="M210 48 H228 V208 H210" fill="none" stroke="#6B7280" stroke-width="18" stroke-linecap="square"/>
    <line x1="88" y1="124" x2="88" y2="200" stroke="#E8E6E3" stroke-width="18"/>
    <circle cx="88" cy="86" r="16" fill="none" stroke="#FF6B57" stroke-width="10"/>
    <circle cx="152" cy="161" r="30" fill="none" stroke="#E8E6E3" stroke-width="18"/>
    <line x1="182" y1="66" x2="182" y2="200" stroke="#E8E6E3" stroke-width="18"/>
  </g>
  <text x="188" y="106" font-family="'JetBrains Mono', 'Iosevka', 'Berkeley Mono', ui-monospace, 'DejaVu Sans Mono', monospace" font-size="34" font-weight="700" fill="#E8E6E3">interview<tspan fill="#6B7280">-</tspan>detective</text>
  <text x="188" y="140" font-family="'JetBrains Mono', 'Iosevka', ui-monospace, 'DejaVu Sans Mono', monospace" font-size="17" fill="#6B7280"><tspan fill="#FF6B57">◦</tspan> glassdoor · github · prep repos</text>
</svg>
```

### Terminal version

Box-drawing version (5 rows); `◦` is the lens:

```text
┏       ┓
┃ ◦   ╻ ┃
┃ ╻ ┏━┫ ┃
┃ ┃ ┗━┛ ┃
┗       ┛
```

Inline: `[id]`, with grey brackets and a coral `◦` in front when colour is available.

---

## 3. Backward Search `?id`

**Idea:** Vim's `?` searches backwards, and the tool searches backwards through what a company has already asked. `id` is the highlighted match.

A blue `?`, the Vim/Neovim backward-search command, is followed by a butter-yellow search-match highlight with a dark `id` cut into it. Anyone who uses Neovim reads it as "search backwards for id, found it". For everyone else it is still a question mark beside the initials. The solid highlight block makes the strongest silhouette of the three at 32px. Colours (Catppuccin Mocha-style): background `#1E1E2E`, `?` `#89B4FA`, highlight `#F9E2AF`, letters knocked out in `#1E1E2E`, wordmark `#CDD6F4`. The tagline `?what did they ask last time?` is in `#6C7086`.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" role="img" aria-label="interview-detective: Vim backward search ?id with the match highlighted">
  <title>interview-detective: Backward Search</title>
  <rect width="256" height="256" rx="44" fill="#1E1E2E"/>
  <g transform="translate(0 10)">
    <!-- ? (Vim backward-search prompt) -->
    <path d="M44 98 A22 22 0 1 1 81.6 113.6 L66 126 V142" fill="none" stroke="#89B4FA" stroke-width="18" stroke-linecap="butt" stroke-linejoin="miter"/>
    <rect x="57" y="152" width="18" height="18" fill="#89B4FA"/>
    <!-- search-match highlight -->
    <rect x="98" y="62" width="136" height="124" fill="#F9E2AF"/>
    <!-- i -->
    <rect x="116" y="84" width="17" height="17" fill="#1E1E2E"/>
    <line x1="124.5" y1="112" x2="124.5" y2="170" stroke="#1E1E2E" stroke-width="17"/>
    <!-- d -->
    <circle cx="178" cy="138.5" r="23" fill="none" stroke="#1E1E2E" stroke-width="17"/>
    <line x1="203" y1="80" x2="203" y2="170" stroke="#1E1E2E" stroke-width="17"/>
  </g>
</svg>
```

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 200" width="640" height="200" role="img" aria-label="interview-detective">
  <title>interview-detective: Backward Search wordmark</title>
  <rect width="640" height="200" rx="28" fill="#1E1E2E"/>
  <g transform="translate(20 20) scale(0.625)">
    <g transform="translate(0 10)">
      <path d="M44 98 A22 22 0 1 1 81.6 113.6 L66 126 V142" fill="none" stroke="#89B4FA" stroke-width="18" stroke-linecap="butt"/>
      <rect x="57" y="152" width="18" height="18" fill="#89B4FA"/>
      <rect x="98" y="62" width="136" height="124" fill="#F9E2AF"/>
      <rect x="116" y="84" width="17" height="17" fill="#1E1E2E"/>
      <line x1="124.5" y1="112" x2="124.5" y2="170" stroke="#1E1E2E" stroke-width="17"/>
      <circle cx="178" cy="138.5" r="23" fill="none" stroke="#1E1E2E" stroke-width="17"/>
      <line x1="203" y1="80" x2="203" y2="170" stroke="#1E1E2E" stroke-width="17"/>
    </g>
  </g>
  <text x="188" y="106" font-family="'JetBrains Mono', 'Iosevka', 'Berkeley Mono', ui-monospace, 'DejaVu Sans Mono', monospace" font-size="34" font-weight="700" fill="#CDD6F4">interview-detective</text>
  <text x="188" y="140" font-family="'JetBrains Mono', 'Iosevka', ui-monospace, 'DejaVu Sans Mono', monospace" font-size="17" fill="#6C7086"><tspan fill="#89B4FA">?</tspan>what did they ask last time?</text>
</svg>
```

### Terminal version

The mark is just text plus a background colour, so it renders exactly in any truecolour terminal:

```fish
printf '%s?%s%sid%s interview-detective\n' (set_color 89b4fa) (set_color normal) (set_color -b f9e2af 1e1e2e) (set_color normal)
```

Without colour, as a Neovim cmdline: `?id` followed by `interview-detective`.

---

## Notes

- **Smallest-size legibility (from the 32px renders):** concept 3 holds up best because of the solid highlight block. Concept 1 is next; the cursor bar carries it. In concept 2 the lens ring is about 4px across at 32px, so it still reads as a ring but only just.
- **Light backgrounds:** all three tiles carry their own dark background, so they work on GitHub's light and dark themes without a `<picture>` swap.
