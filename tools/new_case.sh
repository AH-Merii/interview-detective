#!/usr/bin/env bash
# Start a case by copying the template: tools/new_case.sh <company> <role> [YYYY-MM]
# Slug: <company>-<role>-<YYYY-MM>, kebab-case, e.g. faculty-ml-engineer-2026-10.
set -euo pipefail
cd "$(dirname "$0")/.."
[ $# -ge 2 ] || { echo "usage: $0 <company> <role> [YYYY-MM]" >&2; exit 2; }
kebab() { echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-|-$//g'; }
slug="$(kebab "$1")-$(kebab "$2")-${3:-$(date +%Y-%m)}"
[ -e "interviews/$slug" ] && { echo "interviews/$slug already exists" >&2; exit 1; }
cp -r _templates/interview "interviews/$slug"
# git keeps no empty folders, so a clone's template lacks the empty stage folders
mkdir -p "interviews/$slug"/{01_intake,02_research/lanes,03_glassdoor,04_question-check/batches,05_report}
sed -i "s/^company:.*/company: $1/; s/^role:.*/role: $2/; s/^opened:.*/opened: $(date +%F)/" "interviews/$slug/01_intake/intake.md"
echo "interviews/$slug"
