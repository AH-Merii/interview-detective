#!/usr/bin/env bash
# Start a case by copying the template: tools/new_case.sh <company> <role> [YYYY-MM]
# Slug: <company>-<role>-<YYYY-MM>, kebab-case, e.g. faculty-ml-engineer-2026-10.
# The case goes in the cases folder: $ID_CASES_DIR, else the one setup/wizard.sh saved. Prints its path.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
[ $# -ge 2 ] || { echo "usage: $0 <company> <role> [YYYY-MM]" >&2; exit 2; }
config="${XDG_CONFIG_HOME:-$HOME/.config}/interview-detective/config.env"
cases="${ID_CASES_DIR:-}"
if [ -z "$cases" ] && [ -f "$config" ]; then cases="$(sed -n 's/^ID_CASES_DIR=//p' "$config" | tail -n1)"; fi
[ -n "$cases" ] || { echo "interview-detective isn't set up yet: run bash $root/setup/wizard.sh in a terminal" >&2; exit 3; }
cases="${cases/#\~/$HOME}"
kebab() { echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-|-$//g'; }
case="$cases/$(kebab "$1")-$(kebab "$2")-${3:-$(date +%Y-%m)}"
[ -e "$case" ] && { echo "$case already exists" >&2; exit 1; }
mkdir -p "$cases"
cp -r "$root/_templates/interview" "$case"
# git keeps no empty folders, so the template lacks the empty stage folders
mkdir -p "$case"/{01_intake,02_research/lanes,03_glassdoor,04_question-check/batches,05_report}
# names like "AT&T" or "R/GA" go in literally: escape what sed reads in a replacement
lit() { printf '%s' "$1" | sed 's/[\\/&]/\\&/g'; }
sed -i "s/^company:.*/company: $(lit "$1")/; s/^role:.*/role: $(lit "$2")/; s/^opened:.*/opened: $(date +%F)/" "$case/01_intake/intake.md"
echo "$case"
