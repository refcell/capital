#!/usr/bin/env bash
# daily-company-research.sh — the deterministic half of a daily research run.
#
# It syncs main, picks today's task (a due earnings update or a new name), captures
# prices and SEC data once into data/, commits them, and scaffolds
# data/<TICKER>/<today>/. The research itself (report, call.json, workbook, projection)
# is done by an agent following .agents/skills/researching-companies/SKILL.md, which
# finishes with `python3 -m capital.validate` and a commit to main.
#
# Environment:
#   CAPITAL_REPO_DIR        repo checkout (default: this script's repo)
#   CAPITAL_SEC_CONTACT     contact email for the SEC User-Agent (personal or project, never a work address)
#   DAILY_RESEARCH_DRY_RUN  1 = choose the task and stop (default)
set -euo pipefail

: "${CAPITAL_REPO_DIR:=$(cd "$(dirname "$0")/.." && pwd)}"
: "${CAPITAL_TIMEZONE:=America/New_York}"
: "${DAILY_RESEARCH_DRY_RUN:=1}"
export TZ="$CAPITAL_TIMEZONE"
cd "$CAPITAL_REPO_DIR"
mkdir -p automation/state

LOCK_DIR="automation/state/daily-company-research.lock"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "another daily-company-research run is already active" >&2
  exit 1
fi
trap 'rmdir "$LOCK_DIR"' EXIT

git checkout main
git pull --ff-only origin main
if [ -n "$(git status --porcelain)" ]; then
  git status --short
  echo "worktree is dirty; aborting" >&2
  exit 1
fi

python3 -m capital.build
TASK="$(python3 -m capital.next)"
echo "task: $TASK"
KIND="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["task"])' "$TASK")"
if [ "$KIND" = "update" ]; then
  TICKER="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["ticker"])' "$TASK")"
else
  TICKER="$(python3 scripts/pick-company-ticker.py --record)"
fi
if [ -z "$TICKER" ] || [ "$TICKER" = "n/a" ]; then
  echo "no ticker to research" >&2
  exit 1
fi
echo "ticker: $TICKER ($KIND)"

if [ "$DAILY_RESEARCH_DRY_RUN" = "1" ]; then
  echo "dry run enabled; stopping before capture"
  exit 0
fi

python3 -m capital.prices "$TICKER" SPY
python3 -m capital.sec "$TICKER"
python3 -m capital.build
git add data library
if ! git diff --cached --quiet; then
  git commit -m "data: capture $TICKER prices and SEC facts"
  git push origin main
fi
python3 -m capital.new "$TICKER"

echo "scaffolded data/$TICKER/$(date +%F)/; continue with .agents/skills/researching-companies/SKILL.md"
