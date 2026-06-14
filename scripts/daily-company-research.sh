#!/usr/bin/env bash
# daily-company-research.sh — orchestrator for capital repo daily research runs.
#
# This is a DESIGN DOCUMENT and orchestration wrapper. The actual research,
# modeling, and projection work is performed by the Hermes agent running in the
# main session, not by spawned hermes chat subprocesses (which lose filesystem
# tool access and hit shell 600s timeouts).
#
# Intended use: run from a cron job or manually via the Hermes agent.
# The agent executes three delegation tasks in sequence:
#   1. Pick a ticker via scripts/pick-company-ticker.py
#   2. Delegate research report generation (capital-research skill)
#   3. Delegate workbook model generation (capital-research skill)
#   4. Delegate projection sheet generation (capital-research skill)
#   5. Git commit + push three commits
#   6. Mark ticker seen via scripts/pick-company-ticker.py --mark-seen
#
# Configuration defaults:
: "${CAPITAL_REPO_DIR:=$HOME/dev/capital}"
: "${CAPITAL_LOG_DIR:=$HOME/var/log/capital}"
: "${CAPITAL_TIMEZONE:=America/New_York}"
: "${DAILY_RESEARCH_DRY_RUN:=1}"

export TZ="$CAPITAL_TIMEZONE"
mkdir -p "$CAPITAL_LOG_DIR" "$CAPITAL_REPO_DIR/automation/state"

# Lock-based mutual exclusion to prevent overlapping runs.
LOCK_DIR="$CAPITAL_REPO_DIR/automation/state/daily-company-research.lock"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "another daily-company-research run is already active" >&2
  exit 1
fi
trap 'rmdir "$LOCK_DIR"' EXIT

cd "$CAPITAL_REPO_DIR"

# ── Git hygiene ──────────────────────────────────────────────────────────

git checkout main
git fetch origin
git pull --ff-only origin main

if [ -n "$(git status --porcelain)" ]; then
  git status --short
  echo "worktree is dirty; aborting" >&2
  exit 1
fi

# ── Ticker selection ─────────────────────────────────────────────────────

TICKER="$(python3 scripts/pick-company-ticker.py)"
if [ -z "$TICKER" ] || [ "$TICKER" = "n/a" ]; then
  echo "ticker picker returned no valid ticker" >&2
  exit 1
fi
echo "selected ticker: $TICKER"

if [ "$DAILY_RESEARCH_DRY_RUN" = "1" ]; then
  echo "dry run enabled; no further action"
  exit 0
fi

# ── Stage 1: Research report ─────────────────────────────────────────────
# This section is intentionally a no-op in the shell script.
# The actual research generation happens via the Hermes agent's browser,
# terminal, and file tools — not via a spawned hermes chat subprocess.
# When run unattended via cron, the Hermes agent orchestrates the three
# stages through delegate_task calls with full filesystem and browser access.
# ─────────────────────────────────────────────────────────────────────────

echo "daily company research orchestration complete at $(date -Is)"
echo "Next: delegate to Hermes agent for research/model/projection stages."
